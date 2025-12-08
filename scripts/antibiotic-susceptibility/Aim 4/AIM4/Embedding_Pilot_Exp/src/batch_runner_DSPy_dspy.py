
import os
import json
import asyncio
import logging
import pandas as pd
import traceback
from util.pydantic_modules import ErrorIdentifierOutput, ErrorLabelerOutput
from util.DSPy_modules_dspy import ErrorIdentifierModule, ErrorLabelerModule
# from llm.llm_client import generate_response # No longer needed directly
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

async def identify_error_task(row, identifier, with_reference, identifier_path_output, model):
    # Note: 'model' param is unused here because DSPy LM is configured globally or passed to module if needed. 
    # But strictly speaking, identifier uses dspy.settings.lm. 
    # If we want to support per-call model switching, we'd need to use dspy.context(lm=...)
    
    if with_reference:
        pairs = extract_reference_pairs(row)
        retrieved_pairs = json.dumps(pairs, ensure_ascii=False) if pairs else ""
    else:
        retrieved_pairs = ""
    
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

    loop = asyncio.get_running_loop()
    
    try:
        # Run DSPy module in a separate thread to avoid blocking the async loop
        # identifier is an instance of ErrorIdentifierModule (dspy.Module)
        id_result = await loop.run_in_executor(
            None,
            lambda: identifier(
                index=row["index"],
                patient_message=row["Patient Message"],
                llm_response=row["Suggested Response from LLM"],
                patient_info=row["Data"],
                clinical_notes=row["Last Note"],
                previous_messages=row["Previous Messages"],
                retrieved_pairs=retrieved_pairs
            )
        )
        
        # id_result is already an ErrorIdentifierOutput object (Pydantic)
        result_dict = id_result.model_dump()
        
        # Ensure we save the result
        save_jsonl_line(identifier_path_output, result_dict)
        
        # DSPy might not return the raw string of the LLM response easily unless we access history.
        # For compatibility, we return the object and empty string or reconstructed string.
        llm_id_output = id_result.model_dump_json() 
        
        return row["index"], llm_id_output, id_result
    except Exception as e:
        logging.error(f"Validation error for row index {row['index']}:\n{e}\nTraceback:\n{traceback.format_exc()}")
        return None


async def label_domain_task(index, error_summary, error_highlights, domain, patient_message, llm_response, codebook, labeler_path_output, sleep_per_task):
    domain_codebook = codebook[codebook["Dedup Domain"] == domain].reset_index(drop=True)
    labeler = ErrorLabelerModule(domain=domain, codebook=domain_codebook)
    
    loop = asyncio.get_running_loop()
    
    try:
        # Run labeler in thread
        label_result = await loop.run_in_executor(
            None,
            lambda: labeler(
                index=index,
                error_summary=error_summary,
                error_highlights=error_highlights,
                patient_message=patient_message,
                llm_response=llm_response
            )
        )
        
        save_jsonl_line(labeler_path_output, label_result.model_dump())
        return (domain, label_result)
    except Exception as e:
        logging.error(
            f"Validation error for labeler at index {index}, domain {domain}:\n{e}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        return None


def batchify(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


async def pipeline_task(
    row, identifier, with_reference, identifier_path_output,
    codebook, labeler_path_output, unique_domains, processed_labeler_keys, sleep_per_task, model
):
    # IDENTIFIER STAGE
    # We pass 'model' but ideally we should use dspy.context to set it if it differs from global
    # For now, we assume global configuration in main covers it.
    id_res = await identify_error_task(row, identifier, with_reference, identifier_path_output, model)
    if id_res is None:
        return None, []
    
    idx, llm_id_output_json, id_result_obj = id_res
    
    # id_result_obj is ErrorIdentifierOutput
    error_present = id_result_obj.error_present
    error_summary = id_result_obj.error_summary
    # error_highlights is a list of objects, we need to pass them as they are to labeler (which expects list or dicts)
    # DSPy module expects what? ErrorLabelerModule expects list of objects or dicts.
    # Our updated ErrorLabelerModule handles objects (getattr).
    error_highlights = id_result_obj.error_highlights
    
    patient_message = id_result_obj.patient_message
    llm_response = id_result_obj.llm_response

    
    # LABELER STAGE
    labeler_results = []
    if error_present:
        labeler_tasks = []
        for domain in unique_domains:
            if (idx, domain) in processed_labeler_keys:
                logging.info(f"[{idx}] [{domain}] Already labeled—skipping.")
                continue
            labeler_tasks.append(
                label_domain_task(idx, error_summary, error_highlights, domain, patient_message, llm_response, codebook, labeler_path_output, sleep_per_task)
            )
        labeler_results = await asyncio.gather(*labeler_tasks)
        
    return (idx, llm_id_output_json), labeler_results

async def batch_pipeline_runner(
    sample_data, codebook, identifier, with_reference,
    identifier_path_output, labeler_path_output,
    batch_size=10, delay_between_batches=5, sleep_per_task=1.5, model="gpt-5"
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
            # Case 1: Identifier not done
            tasks.append(
                pipeline_task(
                    row, identifier, with_reference, identifier_path_output,
                    codebook, labeler_path_output, unique_domains, processed_labeler_keys, sleep_per_task, model
                )
            )
        else:
            # Case 2: Identifier done
            id_output = identifier_results_dict.get(idx, None)
            
            error_present = id_output.get("error_present", False)
            error_summary = id_output.get("error_summary", "")
            error_highlights = id_output.get("error_highlights", [])
            patient_message = id_output.get("patient_message", "")
            llm_response = id_output.get("llm_response", "")
            
            missing_domains = [
                domain for domain in unique_domains
                if (idx, domain) not in processed_labeler_keys
            ]
            
            if error_present and missing_domains:
                async def resume_labeler_task(idx=idx, error_summary=error_summary, error_highlights=error_highlights, missing_domains=missing_domains, pm=patient_message, resp=llm_response):
                    labeler_tasks = [
                        label_domain_task(idx, error_summary, error_highlights, domain, pm, resp, codebook, labeler_path_output, sleep_per_task)
                        for domain in missing_domains
                    ]
                    labeler_results = await asyncio.gather(*labeler_tasks)
                    return (idx, None), labeler_results
                tasks.append(resume_labeler_task())

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

