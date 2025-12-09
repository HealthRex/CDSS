#!/usr/bin/env python3
"""
Inference script for the Modular Clinical Error Identification Pipeline.

Usage:
    python src/run_inference.py

This script:
1. Loads all 59 error code definitions from the codebook.
2. Loads optimized checkpoints where available (falls back to untuned for missing codes).
3. Runs the AggregatorModule on input data.
4. Outputs detected errors.
"""
import json
import logging
import os
from pathlib import Path

import dspy
import pandas as pd

from data.loader_dspy import load_codebook
from util.modular_error_pipeline import AggregatorModule, build_error_code_map

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------- Configuration ----------
ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_DIR = ROOT / "optimized_classifiers_gpt-5"
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-5")

# ---------- Initialize LLM ----------
def init_lm():
    """Initialize the DSPy language model."""
    lm = dspy.LM(MODEL_NAME)
    dspy.configure(lm=lm)
    logging.info("Configured DSPy with LM: %s", MODEL_NAME)
    return lm


# ---------- Load Pipeline ----------
def load_pipeline(checkpoint_dir: Path = CHECKPOINT_DIR, max_workers: int = 8) -> AggregatorModule:
    """
    Load the full inference pipeline with all 59 classifiers.
    - Optimized checkpoints are loaded where available.
    - Fresh (untuned) classifiers are used for codes without checkpoints.
    """
    codebook = load_codebook()
    error_code_map = build_error_code_map(codebook, include_examples=False)
    logging.info("Loaded %d error codes from codebook", len(error_code_map))

    # Count how many checkpoints exist
    existing = sum(1 for k in error_code_map if (checkpoint_dir / f"optimized_classifier_{k}.json").exists())
    logging.info("Found %d/%d optimized checkpoints in %s", existing, len(error_code_map), checkpoint_dir)

    aggregator = AggregatorModule(
        error_code_map=error_code_map,
        optimized_dir=checkpoint_dir,
        max_workers=max_workers,
        parallel=True,
    )
    return aggregator


# ---------- Run Inference ----------
def run_inference(
    aggregator: AggregatorModule,
    patient_message: str,
    llm_response: str,
    patient_info: str = "",
    clinical_notes: str = "",
    previous_messages: str = "",
    retrieved_pairs: str = "",
) -> list[dict]:
    """
    Run inference on a single case.
    Returns a list of detected errors (empty if none found).
    """
    detected = aggregator(
        patient_message=patient_message,
        llm_response=llm_response,
        patient_info=patient_info,
        clinical_notes=clinical_notes,
        previous_messages=previous_messages,
        retrieved_pairs=retrieved_pairs,
    )
    return detected


def run_inference_batch(
    aggregator: AggregatorModule,
    df: pd.DataFrame,
    output_path: Path | str | None = None,
) -> pd.DataFrame:
    """
    Run inference on a DataFrame of cases.
    
    Expected columns:
        - patient_message (or Patient Message)
        - llm_response (or LLM Response)
        - patient_info (optional)
        - clinical_notes (optional)
        - previous_messages (optional)
        - retrieved_pairs (optional)
    
    Returns DataFrame with added 'detected_errors' column.
    """
    def _get(row, *keys):
        for k in keys:
            if k in row and pd.notna(row[k]):
                return str(row[k])
        return ""

    results = []
    for idx, row in df.iterrows():
        logging.info("Processing row %s...", idx)
        detected = run_inference(
            aggregator,
            patient_message=_get(row, "patient_message", "Patient Message"),
            llm_response=_get(row, "llm_response", "LLM Response"),
            patient_info=_get(row, "patient_info", "Patient Info"),
            clinical_notes=_get(row, "clinical_notes", "Clinical Notes"),
            previous_messages=_get(row, "previous_messages", "Previous Messages"),
            retrieved_pairs=_get(row, "retrieved_pairs", "Retrieved Pairs"),
        )
        results.append({
            "index": idx,
            "detected_errors": detected,
            "error_codes": [e["error_code"] for e in detected],
            "num_errors": len(detected),
        })
        logging.info("  -> Found %d errors", len(detected))

    result_df = pd.DataFrame(results)
    if output_path:
        result_df.to_json(output_path, orient="records", lines=True)
        logging.info("Saved results to %s", output_path)
    
    return result_df


# ---------- Example Usage ----------
def main():
    init_lm()
    aggregator = load_pipeline()

    # Example single inference
    example_result = run_inference(
        aggregator,
        patient_message="I have been having chest pain for 2 days.",
        llm_response="Based on your symptoms, you likely have indigestion. Take some antacids and you should be fine. No need to see a doctor.",
        patient_info="45-year-old male with history of hypertension and diabetes.",
        clinical_notes="Recent labs show elevated cholesterol.",
        previous_messages="",
        retrieved_pairs="",
    )

    print("\n=== Detected Errors ===")
    if example_result:
        for err in example_result:
            print(f"\nError Code: {err['error_code']}")
            print(f"  Rationale: {err['assessment']['rationale']}")
            print(f"  Excerpt: {err['assessment']['verbatim_excerpt']}")
    else:
        print("No errors detected.")


if __name__ == "__main__":
    main()

