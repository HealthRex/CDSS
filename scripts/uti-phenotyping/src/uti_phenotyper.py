"""
LLM-based UTI Phenotyper following the clinician reviewer instructions.

For each clinical note the model:
1. Labels 10 UTI-related symptoms (Yes / Negation / No)
2. Provides a verbatim supporting quote for each Yes/Negation label
3. Answers 4 final assessment questions (Yes / No / Unclear)
4. Provides brief clinical reasoning for each assessment

Output is a structured dict that mirrors the adjudication CSV schema.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from .phi_safe_llm import PHISafeLLM


# ---------------------------------------------------------------------------
# Symptom definitions (mirrors clinician instruction PDF)
# ---------------------------------------------------------------------------

SYMPTOM_DEFINITIONS = {
    "ability_to_perceive_symptoms": (
        "Capable of perceiving and expressing symptoms? "
        "Patients who are comatose, encephalopathic, or unable to speak may not be able to do so."
    ),
    "dysuria": "Pain or discomfort during urination.",
    "subjective_fever": (
        "Subjective fever that the patient experienced or is experiencing, "
        "but not necessarily febrile during the encounter."
    ),
    "urinary_urgency": "Sudden, intense urge to urinate.",
    "urinary_frequency": "More frequent urination.",
    "suprapubic_pain_tenderness": "Discomfort in the bladder / lower abdomen.",
    "flank_cva_pain_tenderness": "Pain in the back or side near the kidneys.",
    "perineal_pain_painful_prostate_exam": "Pain in the perineum or during prostate examination.",
    "urinary_incontinence": "Loss of bladder control.",
    "macroscopic_hematuria": "Visible blood in the urine.",
}

FINAL_ASSESSMENT_DEFINITIONS = {
    "uti": "Did the patient actually have a urinary tract infection?",
    "any_infection_present": (
        "Including urinary tract infection, is there evidence of any infection "
        "(e.g., pneumonia, cellulitis, etc.)?"
    ),
    "presumed_infection_plausible": (
        "Did the observed symptoms (and urinalysis, if applicable) at the time of urine culture "
        "(but NOT knowing the final urine culture result) suggest that the patient had an infection "
        "that needed empiric antibiotics?"
    ),
    "prophylactic_antibiotics_appropriate": (
        "Did the patient require prophylactic antibiotics due to one or more of: "
        "asymptomatic bacteriuria in pregnancy, impending urologic procedure, or "
        "immunocompromising conditioning (e.g., febrile neutropenia) with atypical labs/symptoms?"
    ),
}

SYMPTOM_LABEL_OPTIONS = ["Yes", "Negation", "No"]
ASSESSMENT_LABEL_OPTIONS = ["Yes", "No", "Unclear"]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert clinical reviewer assisting with UTI (urinary tract infection) phenotyping.
Your task is to analyze clinical notes and extract structured information following the exact \
protocol used by physician reviewers. You must be precise, evidence-based, and output \
well-formed JSON.

Symptom labeling rules:
- "Yes"      — the symptom is explicitly ENDORSED in the note
- "Negation" — the symptom is explicitly DENIED in the note
- "No"       — the symptom is NOT mentioned anywhere in the note

For "Yes" or "Negation", you MUST copy the EXACT verbatim sentence(s) from the note that \
contain the symptom. Do not paraphrase. Copy the full sentence even if it contains other symptoms.
For "No", set support to null.

Final assessment labels: "Yes", "No", or "Unclear".
For the UTI decision specifically, provide a detailed step-by-step rationale that covers:
  1. Which symptoms were present or absent
  2. Any relevant lab/UA findings mentioned in the note
  3. Clinical context (e.g., patient's ability to report symptoms, comorbidities)
  4. Your final reasoning for the Yes/No/Unclear label
For the other three assessments, provide a brief one-sentence reasoning.

Always return ONLY valid JSON — no markdown fences, no preamble, no trailing text.\
"""

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(note_text: str) -> str:
    symptom_items = list(SYMPTOM_DEFINITIONS.items())
    symptom_block = ",\n".join(
        f'    "{key}": {{\n      "label": <"Yes"|"Negation"|"No">,\n      "support": <verbatim quote or null>\n    }}'
        for key, _ in symptom_items
    )

    assessment_items = list(FINAL_ASSESSMENT_DEFINITIONS.items())
    assessment_parts = []
    for key, q in assessment_items:
        if key == "uti":
            reasoning_hint = "<step-by-step rationale covering symptoms, labs, clinical context, and conclusion>"
        else:
            reasoning_hint = "<one-sentence reasoning>"
        assessment_parts.append(
            f'    "{key}": {{\n      "label": <"Yes"|"No"|"Unclear">,\n      "reasoning": {reasoning_hint}\n    }}'
        )
    assessment_block = ",\n".join(assessment_parts)

    return f"""\
Review the following clinical note and return a JSON object with exactly this structure:

{{
  "symptoms": {{
{symptom_block}
  }},
  "final_assessment": {{
{assessment_block}
  }}
}}

Symptom definitions for reference:
{chr(10).join(f'  - {key}: {defn}' for key, defn in SYMPTOM_DEFINITIONS.items())}

CLINICAL NOTE:
{note_text}
"""


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SymptomResult:
    label: str       # "Yes", "Negation", or "No"
    support: Optional[str] = None  # verbatim quote, or None


@dataclass
class AssessmentResult:
    label: str       # "Yes", "No", or "Unclear"
    reasoning: Optional[str] = None


@dataclass
class UTIPhenotypeResult:
    # Symptoms
    ability_to_perceive_symptoms: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    dysuria: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    subjective_fever: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    urinary_urgency: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    urinary_frequency: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    suprapubic_pain_tenderness: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    flank_cva_pain_tenderness: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    perineal_pain_painful_prostate_exam: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    urinary_incontinence: SymptomResult = field(default_factory=lambda: SymptomResult("No"))
    macroscopic_hematuria: SymptomResult = field(default_factory=lambda: SymptomResult("No"))

    # Final assessment
    uti: AssessmentResult = field(default_factory=lambda: AssessmentResult("Unclear"))
    any_infection_present: AssessmentResult = field(default_factory=lambda: AssessmentResult("Unclear"))
    presumed_infection_plausible: AssessmentResult = field(default_factory=lambda: AssessmentResult("Unclear"))
    prophylactic_antibiotics_appropriate: AssessmentResult = field(default_factory=lambda: AssessmentResult("Unclear"))

    # Metadata
    model_name: str = ""
    raw_response: str = ""
    parse_error: Optional[str] = None

    def to_flat_dict(self) -> dict:
        """Returns a flat dict matching the adjudication CSV column naming convention."""
        flat = {}
        symptom_fields = list(SYMPTOM_DEFINITIONS.keys())
        for key in symptom_fields:
            result: SymptomResult = getattr(self, key)
            col_label = _snake_to_csv_name(key)
            flat[f"{col_label}_LLM"] = result.label
            flat[f"{col_label}_Support_LLM"] = result.support
        for key in FINAL_ASSESSMENT_DEFINITIONS.keys():
            result: AssessmentResult = getattr(self, key)
            col_label = _snake_to_csv_name(key)
            flat[f"{col_label}_LLM"] = result.label
            flat[f"{col_label}_Reasoning_LLM"] = result.reasoning
        flat["model_name"] = self.model_name
        flat["parse_error"] = self.parse_error
        return flat


def _snake_to_csv_name(key: str) -> str:
    """Convert snake_case key to the CSV column display name."""
    mapping = {
        "ability_to_perceive_symptoms": "Ability to Perceive Symptoms",
        "dysuria": "Dysuria",
        "subjective_fever": "Subjective Fever",
        "urinary_urgency": "Urinary Urgency",
        "urinary_frequency": "Urinary Frequency",
        "suprapubic_pain_tenderness": "Suprapubic Pain/Tenderness",
        "flank_cva_pain_tenderness": "Flank (CVA) Pain/Tenderness",
        "perineal_pain_painful_prostate_exam": "Perineal Pain/Painful Prostate Exam",
        "urinary_incontinence": "Urinary Incontinence",
        "macroscopic_hematuria": "Macroscopic Hematuria",
        "uti": "UTI?",
        "any_infection_present": "Is any infection present?",
        "presumed_infection_plausible": "Presumed Infection Plausible?",
        "prophylactic_antibiotics_appropriate": "Prophylactic Antibiotics Appropriate?",
    }
    return mapping.get(key, key.replace("_", " ").title())


# ---------------------------------------------------------------------------
# JSON parser
# ---------------------------------------------------------------------------

def _parse_response(raw: str, model_name: str) -> UTIPhenotypeResult:
    # Strip markdown code fences if present
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return UTIPhenotypeResult(model_name=model_name, raw_response=raw, parse_error=str(e))

    result = UTIPhenotypeResult(model_name=model_name, raw_response=raw)

    symptoms = data.get("symptoms", {})
    for key in SYMPTOM_DEFINITIONS:
        sym = symptoms.get(key, {})
        label = sym.get("label", "No")
        if label not in SYMPTOM_LABEL_OPTIONS:
            label = "No"
        support = sym.get("support") or None
        setattr(result, key, SymptomResult(label=label, support=support))

    assessments = data.get("final_assessment", {})
    for key in FINAL_ASSESSMENT_DEFINITIONS:
        asmt = assessments.get(key, {})
        label = asmt.get("label", "Unclear")
        if label not in ASSESSMENT_LABEL_OPTIONS:
            label = "Unclear"
        reasoning = asmt.get("reasoning") or None
        setattr(result, key, AssessmentResult(label=label, reasoning=reasoning))

    return result


# ---------------------------------------------------------------------------
# Main phenotyper class
# ---------------------------------------------------------------------------

class UTIPhenotyper:
    """
    Runs UTI phenotyping on clinical notes using a PHI-safe LLM.

    Example:
        phenotyper = UTIPhenotyper(model_name="gemini-2.5-pro")
        result = phenotyper.phenotype(note_text)
        print(result.uti.label)           # "Yes" / "No" / "Unclear"
        print(result.dysuria.label)       # "Yes" / "Negation" / "No"
        print(result.dysuria.support)     # verbatim quote from note
    """

    def __init__(self, model_name: str = "gemini-2.5-pro", project: Optional[str] = None):
        self.model_name = model_name
        self.llm = PHISafeLLM(model_name=model_name, project=project)

    def phenotype(self, note_text: str) -> UTIPhenotypeResult:
        """
        Phenotype a single clinical note.

        Args:
            note_text: Raw clinical note text.

        Returns:
            UTIPhenotypeResult with symptom labels and final assessment.
        """
        prompt = _build_prompt(note_text)
        raw = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)
        return _parse_response(raw, model_name=self.model_name)

    def phenotype_batch(self, notes: list[str], verbose: bool = True) -> list[UTIPhenotypeResult]:
        """
        Phenotype a list of clinical notes.

        Args:
            notes: List of note text strings.
            verbose: Print progress.

        Returns:
            List of UTIPhenotypeResult.
        """
        results = []
        for i, note in enumerate(notes):
            if verbose:
                print(f"  [{self.model_name}] Phenotyping note {i+1}/{len(notes)}...", end=" ", flush=True)
            try:
                r = self.phenotype(note)
                results.append(r)
                if verbose:
                    status = "PARSE_ERR" if r.parse_error else r.uti.label
                    print(f"UTI={status}")
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(UTIPhenotypeResult(model_name=self.model_name, parse_error=str(e)))
        return results
