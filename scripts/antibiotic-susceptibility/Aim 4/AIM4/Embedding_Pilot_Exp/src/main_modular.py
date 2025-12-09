"""
Entry point for running the modular 59-binary-classifier pipeline in inference mode.
Loads optimized classifiers (if present) and runs all checks per case.
"""

import logging
import os
from pathlib import Path

import dspy

from data.loader_dspy import load_codebook, load_data
from llm.dspy_adapter import HealthRexDSPyLM
from util.DSPy_results_helpers import save_jsonl_line
from util.modular_error_pipeline import AggregatorModule, build_error_code_map


def _extract_reference_pairs(row, num_pairs: int = 5):
    pairs = []
    for i in range(2, 2 + num_pairs):
        pm_col = f"Patient Message_{i}"
        resp_col = f"Actual Response Sent to Patient_{i}"
        if row.get(pm_col) and row.get(resp_col):
            pairs.append({"patient_message": row[pm_col], "response": row[resp_col]})
    return pairs


def main(
    base_path: str = "modular_results",
    model: str = "gpt-5",
    with_reference: bool = True,
    size: int = 20,
):
    os.makedirs(base_path, exist_ok=True)
    output_path = Path(base_path) / "modular_errors.jsonl"

    logging.basicConfig(level=logging.INFO)
    logging.info("Loading codebook and data...")
    codebook = load_codebook()
    error_code_map = build_error_code_map(codebook)

    sample_data = load_data(size=size, random_state=42, cache=True, force_resample=False)

    lm = HealthRexDSPyLM(model_name=model)
    dspy.settings.configure(lm=lm, assert_transform=True)

    aggregator = AggregatorModule(
        error_code_map, optimized_dir=Path("optimized_classifiers"), max_workers=12, parallel=True
    )

    for _, row in sample_data.iterrows():
        retrieved_pairs = ""
        if with_reference:
            pairs = _extract_reference_pairs(row)
            if pairs:
                retrieved_pairs = pairs

        detected = aggregator(
            patient_message=row.get("Patient Message", ""),
            llm_response=row.get("Suggested Response from LLM", ""),
            patient_info=row.get("Data", ""),
            clinical_notes=row.get("Last Note", ""),
            previous_messages=row.get("Previous Messages", ""),
            retrieved_pairs=retrieved_pairs,
        )

        save_jsonl_line(
            str(output_path),
            {
                "index": row.get("index"),
                "detected_errors": detected,
                "patient_message": row.get("Patient Message", ""),
                "llm_response": row.get("Suggested Response from LLM", ""),
            },
        )
        logging.info("Processed index %s; detected %d errors", row.get("index"), len(detected))

    logging.info("Finished inference. Results written to %s", output_path)


if __name__ == "__main__":
    main()

