
import os
import json
import asyncio
import logging
import pandas as pd
import traceback
from util.pydantic_modules import ErrorIdentifierOutput, ErrorLabelerOutput
from util.DSPy_modules import ErrorIdentifierModule, ErrorLabelerModule
from llm.llm_client import generate_response
from util.DSPy_results_helpers import (
    save_jsonl_line,
    load_processed_indices,
    load_processed_labeler_keys,
)

def extract_reference_pairs(row, num_pairs=5):
    pairs = []
    for i in range(2, 2 + num_pairs):
        pm_col = f"Patient Message_{i}"
        resp_col = f"Actual Response Sent to Patient_{i}"
        if pd.notnull(row.get(pm_col, None)) and pd.notnull(row.get(resp_col, None)):
            pairs.append({
                "patient_message": row[pm_col],
                "response": row[resp_col]
            })
    return pairs

async def identify_error_task(row, identifier, with_reference, identifier_path_output):
    if with_reference:
        pairs = extract_reference_pairs(row)
        retrieved_pairs = json.dumps(pairs, ensure_ascii=False) if pairs else ""
    else:
        retrieved_pairs = ""
    prompt = identifier.build_prompt(
        index=row["index"],
        patient_message=row["Patient Message"],
        llm_response=row["Suggested Response from LLM"],
        patient_info=row["Data"],
        clinical_notes=row["Last Note"],
        previous_messages=row["Previous Messages"],
        retrieved_pairs=retrieved_pairs
    )
    input_json = {
        "index": row["index"],
        "patient_message": row["Patient Message"],
        "llm_response": row["Suggested Response from LLM"],
        "patient_info": row["Data"],
        "clinical_notes": row["Last Note"],
        "previous_messages": row["Previous Messages"],
        "retrieved_pairs": retrieved_pairs
    }
    save_jsonl_line(identifier_path_output.replace(".jsonl", "_input.jsonl"), input_json)
    llm_id_output = await generate_response(prompt=prompt)
    await asyncio.sleep(0.5)  # Add 0.5 second delay to prevent 500 errors
    try:
        id_result = ErrorIdentifierOutput.model_validate_json(llm_id_output)
        save_jsonl_line(identifier_path_output, id_result.model_dump())
        logging.info(f"[{row['index']}] [Validated Error Identifier Output]:\n{id_result.model_dump_json(indent=2)}")
        return row["index"], llm_id_output
    except Exception as e:
        logging.error(f"Validation error for row index {row['index']}:\n{e}\nResponse was: {llm_id_output}\nTraceback:\n{traceback.format_exc()}")
        return None  # or return row["index"], None to indicate skipped


async def label_domain_task(index, error_summary, error_highlights,domain, codebook, labeler_path_output, sleep_per_task):
    domain_codebook = codebook[codebook["Dedup Domain"] == domain].reset_index(drop=True)
    labeler = ErrorLabelerModule(domain=domain, codebook=domain_codebook)
    prompt_label = labeler.build_prompt(
        index=index,
        error_summary=error_summary,
        error_highlights=error_highlights
    )
    try:
        llm_label_output = await generate_response(prompt=prompt_label)
        await asyncio.sleep(sleep_per_task)  # Add 1 second delay to prevent 500 errors
        
        label_result = ErrorLabelerOutput.model_validate_json(llm_label_output)
        save_jsonl_line(labeler_path_output, label_result.model_dump())
        logging.info(f"[{index}] [Validated Error Labeler Output for {domain}]:\n{label_result.model_dump_json(indent=2)}")
        return (domain, llm_label_output)
    except Exception as e:
        logging.error(
            f"Validation error for labeler at index {index}, domain {domain}:\n{e}\n"
            f"Response was: {locals().get('llm_label_output', None)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        return None  # or (domain, None) if you want to track skips


def batchify(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


async def pipeline_task(
    row, identifier, with_reference, identifier_path_output,
    codebook, labeler_path_output, unique_domains, processed_labeler_keys, sleep_per_task
):
    # IDENTIFIER STAGE
    id_result = await identify_error_task(row, identifier, with_reference, identifier_path_output)
    if id_result is None:
        return None, []
    idx, llm_id_output = id_result
    # Parse id_result for error_present and summary
    try:
        id_output_dict = json.loads(llm_id_output)
        error_present = id_output_dict.get("error_present", False)
        error_summary = id_output_dict.get("error_summary", "")
        error_highlights = id_output_dict.get("error_highlights", []) or []
    except Exception as e:
        logging.error(f"Failed to parse identifier output for index {idx}: {e}")
        return id_result, []
    
    # LABELER STAGE (immediately after identifier if error present)
    labeler_results = []
    if error_present:
        labeler_tasks = []
        for domain in unique_domains:
            if (idx, domain) in processed_labeler_keys:
                logging.info(f"[{idx}] [{domain}] Already labeled—skipping.")
                continue
            labeler_tasks.append(
                label_domain_task(idx, error_summary, error_highlights, domain, codebook, labeler_path_output, sleep_per_task)
            )
        # Run labeler tasks for this case concurrently
        labeler_results = await asyncio.gather(*labeler_tasks)
    return id_result, labeler_results

async def batch_pipeline_runner(
    sample_data, codebook, identifier, with_reference,
    identifier_path_output, labeler_path_output,
    batch_size=10, delay_between_batches=5, sleep_per_task=1.5
):
    from tqdm import tqdm

    unique_domains = sorted(codebook["Dedup Domain"].unique())
    processed_id_indices = set(load_processed_indices(identifier_path_output))
    processed_labeler_keys = set(load_processed_labeler_keys(labeler_path_output))
    logging.info(f"Loaded {len(processed_labeler_keys)} processed labeler keys from {labeler_path_output}")

    # Helper: Load all identifier results for resuming partial labelers
    def load_all_identifier_results(identifier_path_output):
        results = {}
        if os.path.exists(identifier_path_output):
            with open(identifier_path_output, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        results[obj["index"]] = obj
                    except Exception:
                        continue
        return results
    identifier_results_dict = load_all_identifier_results(identifier_path_output)

    tasks = []
    for _, row in sample_data.iterrows():
        idx = row["index"]

        if idx not in processed_id_indices:
            # Case 1: Identifier not done, do full pipeline
            tasks.append(
                pipeline_task(
                    row, identifier, with_reference, identifier_path_output,
                    codebook, labeler_path_output, unique_domains, processed_labeler_keys, sleep_per_task
                )
            )
        else:
            # Case 2: Identifier done
            id_output = identifier_results_dict.get(idx, None)
            if id_output is None:
                continue  # Shouldn't happen

            error_present = id_output.get("error_present", False)
            error_summary = id_output.get("error_summary", "")
            missing_domains = [
                domain for domain in unique_domains
                if (idx, domain) not in processed_labeler_keys
            ]
            if error_present and missing_domains:
                # Only need to run labelers for missing domains.
                async def resume_labeler_task(idx=idx, error_summary=error_summary, missing_domains=missing_domains):
                    labeler_tasks = [
                        label_domain_task(idx, error_summary, id_output.get("error_highlights", []), domain, codebook, labeler_path_output, sleep_per_task)
                        for domain in missing_domains
                    ]
                    labeler_results = await asyncio.gather(*labeler_tasks)
                    # Return format to match pipeline_task output
                    return (idx, None), labeler_results
                tasks.append(resume_labeler_task())
            # else: all labelers are done, skip

    all_id_results = []
    all_labeler_results = []

    for i, batch in enumerate(batchify(tasks, batch_size)):
        logging.info(f"Running pipeline batch {i+1}")
        batch_id_results = []
        batch_labeler_results = []
        for res in tqdm(asyncio.as_completed(batch), total=len(batch), desc=f"Pipeline Batch {i+1}"):
            id_result, labeler_results = await res
            if id_result is not None:
                batch_id_results.append(id_result)
            if labeler_results:
                batch_labeler_results.extend([r for r in labeler_results if r is not None])
        all_id_results.extend(batch_id_results)
        all_labeler_results.extend(batch_labeler_results)
        if i < (len(tasks) // batch_size):
            logging.info(f"Sleeping for {delay_between_batches}s between pipeline batches...")
            await asyncio.sleep(delay_between_batches)

    return all_id_results, all_labeler_results