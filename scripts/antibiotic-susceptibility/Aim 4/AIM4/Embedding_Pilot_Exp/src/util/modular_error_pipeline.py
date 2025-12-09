import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, Tuple

import dspy
import pandas as pd

from .pydantic_modules import ErrorCheckOutput


# ---------- Error code helpers ----------

def _slug(text: str) -> str:
    """
    File/identifier safe key for an error code.
    - Preserves underscores inside each hierarchy segment.
    - Uses "__" only to join Domain / Subdomain / Error Code boundaries.
    """
    # Split on hyphens (the way we concatenate domain-subdomain-code), keep non-empty parts.
    segments = [seg.strip().lower() for seg in re.split(r"-+", text) if seg.strip()]
    slugged_segments = []
    for seg in segments:
        # Replace non-word chars (excluding underscore) inside the segment with "_"
        cleaned = re.sub(r"[^\w]+", "_", seg)
        cleaned = re.sub(r"_+", "_", cleaned).strip("_")
        if cleaned:
            slugged_segments.append(cleaned)
    return "__".join(slugged_segments)


def _dspy_assert(condition, message: str):
    """Version-tolerant assert; no-op if Assert is unavailable."""
    fn = getattr(dspy, "Assert", None) or getattr(dspy, "assert_", None) or getattr(dspy, "assert_that", None)
    if fn:
        return fn(condition, message)
    return None


def _dspy_suggest(condition, message: str):
    """Version-tolerant suggest; no-op if Suggest is unavailable."""
    fn = getattr(dspy, "Suggest", None) or getattr(dspy, "suggest", None)
    if fn:
        return fn(condition, message)
    return None


def build_error_definition_row(row: pd.Series, include_examples: bool = False) -> str:
    """
    Construct the textual definition passed into each binary classifier.
    This keeps the definition compact but explicit about domain context.
    """
    domain = row.get("Dedup Domain", "").strip()
    subdomain = row.get("Dedup Subdomain", "").strip()
    code = row.get("Dedup Error Code", "").strip()
    definition = row.get("Dedup Definition", "").strip()

    parts = [
        f"Domain: {domain}",
        f"Subdomain: {subdomain}",
        f"Error Code: {code}",
        f"Definition: {definition}",
    ]

    if include_examples:
        rep_examples_str = row.get("Representative Examples", "")
        if rep_examples_str and rep_examples_str.strip() != "[]":
            try:
                examples = json.loads(rep_examples_str)
                parts.append(f"Examples: {json.dumps(examples, ensure_ascii=False)}")
            except Exception:
                logging.warning("Failed to parse Representative Examples for %s", code)
    return "\n".join(parts)


def build_error_code_map(
    codebook: pd.DataFrame, include_examples: bool = False
) -> Dict[str, str]:
    """
    Build a {code_key -> definition_str} map from the deduped codebook.
    code_key is a slug of Domain/Subdomain/Error Code to use in filenames.
    """
    required_cols = {"Dedup Domain", "Dedup Subdomain", "Dedup Error Code", "Dedup Definition"}
    missing = required_cols - set(codebook.columns)
    if missing:
        raise ValueError(f"Codebook missing required columns: {sorted(missing)}")

    code_map: Dict[str, str] = {}
    seen_keys: set[str] = set()
    for _, row in codebook.iterrows():
        domain = row["Dedup Domain"]
        subdomain = row["Dedup Subdomain"]
        code = row["Dedup Error Code"]
        key = _slug(f"{domain}-{subdomain}-{code}")

        # Avoid accidental duplicates (keep the first)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        code_map[key] = build_error_definition_row(row, include_examples=include_examples)
    return code_map


def load_error_code_map(codebook_path: Path, include_examples: bool = False) -> Dict[str, str]:
    df = pd.read_csv(codebook_path)
    return build_error_code_map(df, include_examples=include_examples)


# ---------- DSPy Signature and Modules ----------

class BinaryErrorClassifierSignature(dspy.Signature):
    """
    You are a highly specialized clinical informatics reviewer. Your sole task is to
    determine if the AI-generated response contains the specific error described below.
    Your output MUST adhere to the provided JSON schema.
    """

    patient_message = dspy.InputField()
    llm_response = dspy.InputField()
    patient_info = dspy.InputField()
    clinical_notes = dspy.InputField()
    previous_messages = dspy.InputField()
    retrieved_pairs = dspy.InputField(desc="Reference examples of similar Q&A pairs")
    error_definition = dspy.InputField(
        desc="The hierarchical error code (Domain, Subdomain, Code) and its definition. This is the ONLY error you are checking for."
    )

    assessment: ErrorCheckOutput = dspy.OutputField(
        desc="JSON object containing the binary classification, rationale, and verbatim excerpt."
    )


class ModularErrorClassifier(dspy.Module):
    """
    Core module that runs the binary prediction and enforces logical constraints
    with DSPy assertions/suggestions. Assertions require assert_transform=True or
    program.activate_assertions().
    """

    def __init__(self, error_code_str: str):
        super().__init__()
        self.error_code_str = error_code_str
        self.predictor = dspy.Predict(BinaryErrorClassifierSignature)

    def forward(
        self,
        patient_message,
        llm_response,
        patient_info,
        clinical_notes,
        previous_messages,
        retrieved_pairs,
    ):
        pred = self.predictor(
            patient_message=patient_message,
            llm_response=llm_response,
            patient_info=patient_info,
            clinical_notes=clinical_notes,
            previous_messages=previous_messages,
            retrieved_pairs=retrieved_pairs,
            error_definition=self.error_code_str,
        )

        # --- DSPy ASSERTIONS FOR LOGICAL CONSISTENCY (version tolerant) ---
        _dspy_assert(
            (pred.assessment.error_present is False)
            or (pred.assessment.verbatim_excerpt != "Not Applicable"),
            "Error found, but excerpt is 'Not Applicable'. Find the quote in the LLM response that shows the error.",
        )

        _dspy_suggest(
            (pred.assessment.error_present is True)
            or (pred.assessment.verbatim_excerpt == "Not Applicable"),
            "No error found, but excerpt is not 'Not Applicable'. Default to 'Not Applicable' when error_present is False.",
        )

        # Optional: Ensure excerpt is drawn from the llm_response.
        _dspy_suggest(
            pred.assessment.verbatim_excerpt in llm_response,
            "The verbatim excerpt must be an exact quote from the LLM response."
        )

        return pred.assessment


class AggregatorModule(dspy.Module):
    """
    Aggregates all optimized binary classifiers and returns only detected errors.
    Runs classifiers in parallel threads by default (safe because DSPy calls are blocking).
    """

    def __init__(
        self,
        error_code_map: Dict[str, str],
        optimized_dir: Path | str | None = None,
        max_workers: int = 8,
        parallel: bool = True,
    ):
        super().__init__()
        self.max_workers = max_workers
        self.parallel = parallel
        self.optimized_dir = Path(optimized_dir) if optimized_dir else None

        self.classifiers: Dict[str, ModularErrorClassifier] = {}
        for code_key, definition in error_code_map.items():
            classifier = ModularErrorClassifier(error_code_str=definition)
            if self.optimized_dir:
                ckpt_path = self.optimized_dir / f"optimized_classifier_{code_key}.json"
                if ckpt_path.exists():
                    classifier.load(str(ckpt_path))
                else:
                    logging.warning("No optimized checkpoint found for %s at %s", code_key, ckpt_path)
            self.classifiers[code_key] = classifier

    def forward(
        self,
        patient_message,
        llm_response,
        patient_info,
        clinical_notes,
        previous_messages,
        retrieved_pairs,
    ):
        def _run_one(key: str, clf: ModularErrorClassifier) -> Tuple[str, ErrorCheckOutput]:
            return (
                key,
                clf(
                    patient_message=patient_message,
                    llm_response=llm_response,
                    patient_info=patient_info,
                    clinical_notes=clinical_notes,
                    previous_messages=previous_messages,
                    retrieved_pairs=retrieved_pairs,
                ),
            )

        results: list[Tuple[str, ErrorCheckOutput]] = []
        if self.parallel and len(self.classifiers) > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                futures = {
                    pool.submit(_run_one, key, clf): key for key, clf in self.classifiers.items()
                }
                for fut in as_completed(futures):
                    results.append(fut.result())
        else:
            for key, clf in self.classifiers.items():
                results.append(_run_one(key, clf))

        detected_errors = []
        for code_key, assessment in results:
            if assessment.error_present:
                detected_errors.append(
                    {"error_code": code_key, "assessment": assessment.model_dump()}
                )

        return detected_errors


