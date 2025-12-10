"""
Optimization script for the modular 59-classifier pipeline.

For each deduplicated error code we:
1) Build a code-specific binary trainset.
2) Optimize the ModularErrorClassifier with BootstrapFewShotWithRandomSearch.
3) Save the optimized program to disk (optimized_classifier_<code_key>.json).

Expect the training dataframe to include one boolean column per error code:
label_<code_key>, where code_key is slugified Domain-Subdomain-ErrorCode.
Optional columns: rationale_<code_key>, excerpt_<code_key>.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List

import dspy
import pandas as pd
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

from data.loader_dspy import load_codebook
from llm.dspy_adapter import HealthRexDSPyLM
from util.modular_error_pipeline import (
    ModularErrorClassifier,
    build_error_code_map,
)
from util.pydantic_modules import ErrorCheckOutput

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5")  # Change to target LM (e.g., "gemini-2.5-pro")
# Resolve repo root (one level up from this file's directory)
ROOT = Path(__file__).resolve().parent.parent
TRAIN_PATH = ROOT / "src/data/input_data/labeled_modular_training_20pos_20neg.csv"


def _safe_dir(name: str) -> str:
    """Sanitize model name to a filesystem-friendly suffix."""
    return re.sub(r"[^\w.-]+", "_", name)


# Separate output per model so you can keep multiple runs; allow override via env
OUTPUT_DIR = Path(
    os.getenv("OUTPUT_DIR", str(ROOT / f"optimized_classifiers_{_safe_dir(MODEL_NAME)}"))
)


def _extract_assessment(obj):
    """Handle both wrapped (obj.assessment) and direct ErrorCheckOutput."""
    return getattr(obj, "assessment", obj)


def validate_binary_classification(example, pred, trace=None):
    """Metric: strict match on error_present."""
    gt = _extract_assessment(example)
    pr = _extract_assessment(pred)
    return getattr(gt, "error_present", None) == getattr(pr, "error_present", None)


def _stringify(val) -> str:
    if val is None:
        return ""
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def _first_present(row, keys):
    for k in keys:
        if k in row and pd.notna(row[k]):
            return row[k]
    return ""


def build_trainset_for_code(code_key: str, df: pd.DataFrame) -> List[dspy.Example]:
    """
    Build a DSPy trainset for a specific code.
    Expects a boolean column `label_<code_key>` in df.
    """
    label_col = f"label_{code_key}"
    rationale_col = f"rationale_{code_key}"
    excerpt_col = f"excerpt_{code_key}"

    if label_col not in df.columns:
        logging.warning("Skipping %s: missing label column %s", code_key, label_col)
        return []

    trainset: List[dspy.Example] = []
    for _, row in df.iterrows():
        label_val = bool(row[label_col])
        rationale = row.get(rationale_col, "Human label provided; rationale not captured.")
        if label_val:
            excerpt = row.get(
                excerpt_col,
                "Human label provided as positive; excerpt not captured in dataset.",
            )
        else:
            excerpt = "Not Applicable"

        expected = ErrorCheckOutput(
            error_present=label_val,
            rationale=_stringify(rationale),
            verbatim_excerpt=_stringify(excerpt),
        )

        ex = (
            dspy.Example(
                patient_message=_stringify(_first_present(row, ["patient_message", "Patient Message"])),
                llm_response=_stringify(_first_present(row, ["llm_response", "Suggested Response from LLM"])),
                patient_info=_stringify(_first_present(row, ["patient_info", "Data"])),
                clinical_notes=_stringify(_first_present(row, ["clinical_notes", "Last Note"])),
                previous_messages=_stringify(_first_present(row, ["previous_messages", "Previous Messages"])),
                retrieved_pairs=_stringify(_first_present(row, ["retrieved_pairs"])),
                assessment=expected,
            ).with_inputs(
                "patient_message",
                "llm_response",
                "patient_info",
                "clinical_notes",
                "previous_messages",
                "retrieved_pairs",
            )
        )
        trainset.append(ex)
    return trainset


def optimize_all(error_code_map: Dict[str, str], train_df: pd.DataFrame):
    """Compile an optimized classifier per error code."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lm = HealthRexDSPyLM(model_name=MODEL_NAME)
    dspy.settings.configure(lm=lm, assert_transform=True)

    # Optional: filter codes via env CODE_FILTER (comma-separated). Empty set => run all.
    code_filter_env = os.getenv("CODE_FILTER", "").strip()
    code_filter = {c.strip() for c in code_filter_env.split(",") if c.strip()} if code_filter_env else set()
    
    # For the quick run, only use the first 2 codes ToDo: remove this later
    for code_key, definition in list(error_code_map.items())[:2]:
        if code_filter and code_key not in code_filter:
            continue
        ckpt_path = OUTPUT_DIR / f"optimized_classifier_{code_key}.json"
        if ckpt_path.exists():
            logging.info("Checkpoint exists for %s, skipping: %s", code_key, ckpt_path)
            continue

        logging.info("Optimizing classifier for %s", code_key)
        trainset = build_trainset_for_code(code_key, train_df)
        if not trainset:
            logging.warning("No training data for %s. Skipping optimization.", code_key)
            continue

        student = ModularErrorClassifier(error_code_str=definition)
        optimizer = BootstrapFewShotWithRandomSearch(
            metric=validate_binary_classification,
            max_bootstrapped_demos=1,
            max_labeled_demos=2,
            num_candidate_programs=2,  # reduce search to shorten runtime
            num_threads=1,  # LM adapter is synchronous
        )

        try:
            optimized_program = optimizer.compile(student, trainset=trainset)
            optimized_program.save(str(ckpt_path))
            logging.info("Saved optimized classifier to %s", ckpt_path)
        except Exception as e:
            logging.exception("Failed to optimize/save for %s: %s", code_key, e)
            raise

        # For the quick run, stop after the first code
        return


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Loading codebook and training data...")
    codebook = load_codebook()
    error_code_map = build_error_code_map(codebook, include_examples=False)

    if not TRAIN_PATH.exists():
        raise FileNotFoundError(f"Training CSV not found at {TRAIN_PATH}")
    # For the quick run, only use the first 5 rows of the training data ToDo: remove this later
    train_df = pd.read_csv(TRAIN_PATH)[:5]
    logging.info("Loaded training data with shape %s from %s", train_df.shape, TRAIN_PATH)

    optimize_all(error_code_map, train_df)


if __name__ == "__main__":
    main()