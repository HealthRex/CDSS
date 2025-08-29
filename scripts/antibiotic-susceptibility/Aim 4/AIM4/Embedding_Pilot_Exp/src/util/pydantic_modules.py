
from typing import List, Optional, Set
import re
from pydantic import BaseModel, Field, model_validator, confloat


class ErrorHighlight(BaseModel):
    excerpt: str = Field(..., description="Verbatim span from the LLM response; never truncated.")
    explanation: str = Field(..., description="Clinical reasoning for why this span evidences an error.")

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
HID_PATTERN = re.compile(r"\[H(\d+)\]")
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
        None, description="If yes=true, must cite one or more highlight IDs like [H1]."
    )
    confidence: confloat(ge=0.0, le=1.0)

    class Config:
        extra = "forbid"

class SubdomainLabel(BaseModel):
    subdomain: str
    yes: bool
    rationale: Optional[str] = Field(
        None, description="If yes=true, must cite one or more highlight IDs like [H1]."
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
            return {f"H{m.group(1)}" for m in HID_PATTERN.finditer(text)}

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
