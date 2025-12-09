"""
Async batch runner for the Modular 59-code Binary Classifier Pipeline.

Uses asyncio + ThreadPoolExecutor to run classifiers in parallel across:
1. Multiple cases (rows) concurrently
2. Multiple classifiers per case concurrently

Output: One JSONL row per index with all detected errors.
"""
import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Tuple

# Load .env file for API keys
from dotenv import load_dotenv
load_dotenv()

import dspy
import pandas as pd
from tqdm import tqdm

from data.loader_dspy import load_codebook
from util.modular_error_pipeline import (
    AggregatorModule,
    ModularErrorClassifier,
    build_error_code_map,
)
from util.DSPy_results_helpers import save_jsonl_line, load_processed_indices
from llm.dspy_adapter import HealthRexDSPyLM

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------- Configuration ----------
ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_DIR = ROOT / "optimized_classifiers_gpt-5"
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-5")


def init_lm():
    """Initialize the DSPy language model using HealthRex's secure adapter."""
    lm = HealthRexDSPyLM(model_name=MODEL_NAME)
    dspy.configure(lm=lm)
    logging.info("Configured DSPy with HealthRexDSPyLM: %s", MODEL_NAME)
    return lm


def load_classifiers(
    checkpoint_dir: Path = CHECKPOINT_DIR,
) -> Tuple[Dict[str, ModularErrorClassifier], Dict[str, str]]:
    """
    Load all 59 classifiers.
    - Optimized checkpoints are loaded where available.
    - Fresh (untuned) classifiers are used for codes without checkpoints.
    
    Returns:
        classifiers: dict of code_key -> ModularErrorClassifier
        error_code_map: dict of code_key -> definition string
    """
    codebook = load_codebook()
    error_code_map = build_error_code_map(codebook, include_examples=False)
    logging.info("Loaded %d error codes from codebook", len(error_code_map))

    classifiers: Dict[str, ModularErrorClassifier] = {}
    loaded_count = 0
    
    for code_key, definition in error_code_map.items():
        classifier = ModularErrorClassifier(error_code_str=definition)
        ckpt_path = checkpoint_dir / f"optimized_classifier_{code_key}.json"
        if ckpt_path.exists():
            classifier.load(str(ckpt_path))
            loaded_count += 1
        classifiers[code_key] = classifier

    logging.info(
        "Loaded %d/%d optimized checkpoints from %s",
        loaded_count, len(error_code_map), checkpoint_dir
    )
    return classifiers, error_code_map


def extract_reference_pairs(row, num_pairs: int = 5) -> str:
    """Extract retrieved Q&A pairs from row columns."""
    pairs = []
    for i in range(2, 2 + num_pairs):
        pm_col = f"Patient Message_{i}"
        resp_col = f"Actual Response Sent to Patient_{i}"
        if pd.notnull(row.get(pm_col, None)) and pd.notnull(row.get(resp_col, None)):
            pairs.append({
                "patient_message": row[pm_col],
                "response": row[resp_col]
            })
    return json.dumps(pairs, ensure_ascii=False) if pairs else ""


def run_single_classifier(
    code_key: str,
    classifier: ModularErrorClassifier,
    patient_message: str,
    llm_response: str,
    patient_info: str,
    clinical_notes: str,
    previous_messages: str,
    retrieved_pairs: str,
) -> Tuple[str, dict]:
    """Run a single classifier and return (code_key, assessment_dict)."""
    try:
        result = classifier(
            patient_message=patient_message,
            llm_response=llm_response,
            patient_info=patient_info,
            clinical_notes=clinical_notes,
            previous_messages=previous_messages,
            retrieved_pairs=retrieved_pairs,
        )
        return (code_key, result.model_dump())
    except Exception as e:
        logging.error("Error running classifier %s: %s", code_key, e)
        return (code_key, {"error_present": False, "rationale": f"Error: {e}", "verbatim_excerpt": "Not Applicable"})


async def run_all_classifiers_for_case(
    classifiers: Dict[str, ModularErrorClassifier],
    patient_message: str,
    llm_response: str,
    patient_info: str,
    clinical_notes: str,
    previous_messages: str,
    retrieved_pairs: str,
    executor: ThreadPoolExecutor,
    max_concurrent_classifiers: int = 10,
    case_index: int = 0,
) -> Dict[str, dict]:
    """
    Run all 59 classifiers for a single case using thread pool.
    Uses semaphore to limit concurrent classifier calls.
    
    Returns: dict of code_key -> assessment_dict
    """
    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(max_concurrent_classifiers)
    total_classifiers = len(classifiers)
    completed = [0]  # Use list to allow mutation in nested function
    
    async def run_with_semaphore(code_key: str, clf: ModularErrorClassifier):
        async with semaphore:
            result = await loop.run_in_executor(
                executor,
                run_single_classifier,
                code_key,
                clf,
                patient_message,
                llm_response,
                patient_info,
                clinical_notes,
                previous_messages,
                retrieved_pairs,
            )
            completed[0] += 1
            print(f"\r  [Index {case_index}] Classifiers: {completed[0]}/{total_classifiers}", end="", flush=True)
            return result
    
    tasks = [
        run_with_semaphore(code_key, clf)
        for code_key, clf in classifiers.items()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print()  # Newline after progress
    
    assessments = {}
    for res in results:
        if isinstance(res, Exception):
            logging.error("Classifier task failed: %s", res)
            continue
        code_key, assessment = res
        assessments[code_key] = assessment
    
    return assessments


async def process_single_row(
    row: pd.Series,
    classifiers: Dict[str, ModularErrorClassifier],
    executor: ThreadPoolExecutor,
    output_path: str,
    with_reference: bool = True,
    max_concurrent_classifiers: int = 10,
) -> dict:
    """
    Process a single row: run all 59 classifiers and save result.
    
    Output format:
    {
        "index": <int>,
        "detected_errors": [{"code_key": ..., "assessment": {...}}, ...],
        "all_assessments": {"code_key": {...}, ...},  # optional, for debugging
        "num_errors": <int>
    }
    """
    idx = row["index"]
    
    # Extract inputs
    patient_message = str(row.get("Patient Message", ""))
    llm_response = str(row.get("Suggested Response from LLM", ""))
    patient_info = str(row.get("Data", ""))
    clinical_notes = str(row.get("Last Note", ""))
    previous_messages = str(row.get("Previous Messages", ""))
    retrieved_pairs = extract_reference_pairs(row) if with_reference else ""
    
    # Run all classifiers
    all_assessments = await run_all_classifiers_for_case(
        classifiers=classifiers,
        patient_message=patient_message,
        llm_response=llm_response,
        patient_info=patient_info,
        clinical_notes=clinical_notes,
        previous_messages=previous_messages,
        retrieved_pairs=retrieved_pairs,
        executor=executor,
        max_concurrent_classifiers=max_concurrent_classifiers,
        case_index=idx,
    )
    
    # Extract detected errors (only positives)
    detected_errors = []
    for code_key, assessment in all_assessments.items():
        if assessment.get("error_present", False):
            detected_errors.append({
                "code_key": code_key,
                "rationale": assessment.get("rationale", ""),
                "verbatim_excerpt": assessment.get("verbatim_excerpt", ""),
            })
    
    result = {
        "index": idx,
        "detected_errors": detected_errors,
        "error_codes": [e["code_key"] for e in detected_errors],
        "num_errors": len(detected_errors),
        # Optionally include all assessments for debugging (comment out to reduce size)
        # "all_assessments": all_assessments,
    }
    
    # Save immediately for resume capability
    save_jsonl_line(output_path, result)
    
    return result


def batchify(lst, batch_size):
    """Yield successive batches from lst."""
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


async def batch_pipeline_runner(
    sample_data: pd.DataFrame,
    classifiers: Dict[str, ModularErrorClassifier],
    output_path: str,
    with_reference: bool = True,
    batch_size: int = 5,
    delay_between_batches: float = 2.0,
    max_concurrent_classifiers: int = 10,
    max_workers: int = 20,
):
    """
    Run the modular classifier pipeline on all rows.
    
    Args:
        sample_data: DataFrame with input columns
        classifiers: dict of code_key -> ModularErrorClassifier
        output_path: path to output JSONL
        with_reference: whether to include retrieved pairs
        batch_size: number of rows to process concurrently
        delay_between_batches: seconds to wait between batches (rate limiting)
        max_concurrent_classifiers: max classifiers to run concurrently per case
        max_workers: thread pool size
    """
    # Load already processed indices for resume
    processed_indices = set(load_processed_indices(output_path))
    logging.info("Loaded %d already processed indices from %s", len(processed_indices), output_path)
    
    # Filter to unprocessed rows
    rows_to_process = [
        row for _, row in sample_data.iterrows()
        if row["index"] not in processed_indices
    ]
    logging.info("Processing %d rows (skipping %d already done)", len(rows_to_process), len(processed_indices))
    
    if not rows_to_process:
        logging.info("All rows already processed!")
        return []
    
    all_results = []
    executor = ThreadPoolExecutor(max_workers=max_workers)
    
    try:
        for batch_num, batch in enumerate(batchify(rows_to_process, batch_size)):
            logging.info("Processing batch %d (%d rows)...", batch_num + 1, len(batch))
            
            tasks = [
                process_single_row(
                    row=row,
                    classifiers=classifiers,
                    executor=executor,
                    output_path=output_path,
                    with_reference=with_reference,
                    max_concurrent_classifiers=max_concurrent_classifiers,
                )
                for row in batch
            ]
            
            # Run batch with progress bar
            batch_results = []
            for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Batch {batch_num + 1}"):
                result = await coro
                batch_results.append(result)
                logging.info("  Index %s: %d errors detected", result["index"], result["num_errors"])
            
            all_results.extend(batch_results)
            
            # Rate limiting between batches
            if batch_num < (len(rows_to_process) - 1) // batch_size:
                logging.info("Sleeping %.1fs between batches...", delay_between_batches)
                await asyncio.sleep(delay_between_batches)
    
    finally:
        executor.shutdown(wait=False)
    
    logging.info("Completed processing %d rows", len(all_results))
    return all_results


async def main_async(
    input_path: str,
    output_path: str,
    with_reference: bool = True,
    batch_size: int = 5,
    delay_between_batches: float = 2.0,
    max_concurrent_classifiers: int = 10,
):
    """Main async entry point."""
    # Initialize LM
    init_lm()
    
    # Load classifiers
    classifiers, _ = load_classifiers()
    
    # Load input data
    logging.info("Loading input data from %s", input_path)
    if input_path.endswith(".csv"):
        sample_data = pd.read_csv(input_path)
    else:
        sample_data = pd.read_json(input_path, lines=True)
    logging.info("Loaded %d rows", len(sample_data))
    
    # Run pipeline
    results = await batch_pipeline_runner(
        sample_data=sample_data,
        classifiers=classifiers,
        output_path=output_path,
        with_reference=with_reference,
        batch_size=batch_size,
        delay_between_batches=delay_between_batches,
        max_concurrent_classifiers=max_concurrent_classifiers,
    )
    
    # Summary
    total_errors = sum(r["num_errors"] for r in results)
    logging.info("=== Summary ===")
    logging.info("Processed %d cases", len(results))
    logging.info("Total errors detected: %d", total_errors)
    logging.info("Results saved to %s", output_path)
    
    return results


def main():
    """Synchronous main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run modular 59-code classifier pipeline")
    parser.add_argument("--input", "-i", required=True, help="Input CSV or JSONL path")
    parser.add_argument("--output", "-o", required=True, help="Output JSONL path")
    parser.add_argument("--no-reference", action="store_true", help="Disable retrieved pairs")
    parser.add_argument("--batch-size", type=int, default=5, help="Rows per batch")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between batches (seconds)")
    parser.add_argument("--max-classifiers", type=int, default=10, help="Max concurrent classifiers per case")
    
    args = parser.parse_args()
    
    asyncio.run(main_async(
        input_path=args.input,
        output_path=args.output,
        with_reference=not args.no_reference,
        batch_size=args.batch_size,
        delay_between_batches=args.delay,
        max_concurrent_classifiers=args.max_classifiers,
    ))


if __name__ == "__main__":
    main()

