
from typing import List, Optional, Set, Literal
import re
from pydantic import BaseModel, Field, model_validator, confloat


class ErrorHighlight(BaseModel):
    excerpt: str = Field(..., description="Verbatim span from the LLM response; never truncated.")
    explanation: str = Field(..., description="Clinical reasoning for why this span evidences an error.")

    class Config:
        extra = "forbid"


class ErrorCheckOutput(BaseModel):
    error_present: Literal[True, False] = Field(
        ...,
        description="True if the specific error is found in the LLM response, otherwise False."
    )
    rationale: str = Field(
        ...,
        description="Brief explanation for the classification decision."
    )
    verbatim_excerpt: str = Field(
        ...,
        description="Exact quote from the llm_response that demonstrates the error. Use 'Not Applicable' when error_present is False."
    )

    @model_validator(mode="after")
    def _enforce_excerpt_rules(self):
        if self.error_present:
            if not self.verbatim_excerpt or self.verbatim_excerpt.strip() in {"Not Applicable", ""}:
                raise ValueError("error_present=True requires a non-empty verbatim_excerpt.")
        else:
            # Normalize to the canonical placeholder when no error is present
            if self.verbatim_excerpt.strip() == "":
                self.verbatim_excerpt = "Not Applicable"
        return self

    class Config:
        extra = "forbid"


class ErrorIdentifierOutput(BaseModel):
    index: int
    patient_message: str = Field(..., description='May end with " [truncated]" in output.')
    llm_response: str = Field(..., description='May end with " [truncated]" in output.')
    error_present: bool
    error_highlights: List[ErrorHighlight] = Field(
        default_factory=list,
        description="Zero or more highlights; required to be non-empty if error_present is True."
    )
    error_summary: str = Field(..., description="A few sentences concise summary of the core error(s). If no error: 'no error found—no applicable'")

    @model_validator(mode='after')
    def _consistency_checks(self):
        err = self.error_present
        highlights = self.error_highlights or []
        summary = (self.error_summary or "").strip()

        if err and not highlights:
            raise ValueError("error_present=True requires at least one item in error_highlights.")

        if not err:
            # Soft guardrails for the 'no error' case
            if not highlights:
                self.error_highlights = [ErrorHighlight(
                    excerpt="no error found—no applicable highlight",
                    explanation="no error found—no applicable explanation"
                )]
            if summary == "":
                self.error_summary = "no error found—no applicable"
        return self

    class Config:
        extra = "forbid"


# Matches citations like [H1], [H2], ...
# HID_PATTERN = re.compile(r"\[H(\d+)\]")
# Accept [H1] or [H1,H2, H10] (used only for presence checks if you like)
HID_GROUP = re.compile(r"\[(?:H\d+(?:,\s*H\d+)*)\]")

# Extract tokens H1, H2, H10 even without brackets; avoid word-embedded matches
# e.g., matches "... H10 ..." but not "... XH10Y ..."
HID_TOKEN = re.compile(r"(?<![A-Za-z0-9_])H(\d+)(?![A-Za-z0-9_])")


class ErrorHighlightOut(BaseModel):
    id: str = Field(..., description='Highlight ID like "H1".')
    excerpt: str = Field(..., description="Verbatim span from the LLM response; never truncated.")
    explanation: str = Field(..., description="Why this span evidences an error.")

    class Config:
        extra = "forbid"
class ErrorCodeLabel(BaseModel):
    error_code: str
    yes: bool
    rationale: Optional[str] = Field(
        None,description='If yes=true, cite one or more highlight IDs, e.g., [H1], [H1,H2] or H1 H2.'
    )
    confidence: confloat(ge=0.0, le=1.0)

    class Config:
        extra = "forbid"

class SubdomainLabel(BaseModel):
    subdomain: str
    yes: bool
    rationale: Optional[str] = Field(
        None, description='If yes=true, cite one or more highlight IDs, e.g., [H1], [H1,H2] or H1 H2.'
    )
    confidence: confloat(ge=0.0, le=1.0)
    error_codes: List[ErrorCodeLabel]

    class Config:
        extra = "forbid"

class ErrorLabelerOutput(BaseModel):
    index: int
    domain: str
    error_summary: str = Field(..., description="Echoed summary from identifier step.")
    error_highlights: List[ErrorHighlightOut] = Field(
        ..., description="Numbered highlights (H1, H2, ...) echoed in the output."
    )
    subdomains: List[SubdomainLabel]

    class Config:
        extra = "forbid"

    @model_validator(mode='after')
    def _enforce_evidence_citations(self):
        # Build valid ID set from error_highlights
        highlights: List[ErrorHighlightOut] = self.error_highlights or []
        valid_ids: Set[str] = {h.id for h in highlights}
        
        def cited_ids(text: Optional[str]) -> Set[str]:
            if not text:
                return set()
            # Pull all H-numbers anywhere in the text (bracketed or not)
            return {f"H{n}" for n in HID_TOKEN.findall(text)}


        # Subdomain-level checks
        for sd in self.subdomains or []:
            if sd.yes:
                ids = cited_ids(sd.rationale)
                if not ids:
                    raise ValueError(
                        f'Subdomain "{sd.subdomain}" has yes=true but rationale does not cite any [H#].'
                    )
                unknown = ids - valid_ids
                if unknown:
                    raise ValueError(
                        f'Subdomain "{sd.subdomain}" cites unknown highlights: {sorted(unknown)}.'
                    )
            # Error-code-level checks
            for ec in sd.error_codes:
                if ec.yes:
                    ids = cited_ids(ec.rationale)
                    if not ids:
                        raise ValueError(
                            f'Error code "{ec.error_code}" under subdomain "{sd.subdomain}" has yes=true but no [H#] citation.'
                        )
                    unknown = ids - valid_ids
                    if unknown:
                        raise ValueError(
                            f'Error code "{ec.error_code}" under subdomain "{sd.subdomain}" cites unknown highlights: {sorted(unknown)}.'
                        )
        return self
