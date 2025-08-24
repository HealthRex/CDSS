import os
import json
import asyncio
import time

from datetime import datetime
from llm.llm_client import generate_response
from util.prompt_helper import make_prompt
from util.results_helper import load_results


async def process_case(row, codebook_json, output_path, failed_dir, logger, with_reference = False):
    case_index = int(row['index']) if 'index' in row else -1
    prompt = make_prompt(row, codebook_json,with_reference)
    if logger:
        # logger.write(f"\n=== Case {case_index} ===\n[PROMPT]\n{prompt}\n")
        logger.write(f"\n=== Case {case_index} ===")
        logger.flush()

    content = await generate_response(prompt=prompt, logger=logger)

    if logger:
        logger.write(f"[RAW OUTPUT]\n{content}\n")
        logger.flush()

    try:
        result = json.loads(content)
    except Exception:
        try:
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            result = json.loads(content[json_start:json_end])
        except Exception as e:
            failed_file = os.path.join(failed_dir, f"case_{case_index}_failed_{int(time.time())}.txt")
            with open(failed_file, "w") as f:
                f.write("PROMPT:\n" + prompt + "\n\n")
                f.write("LLM_OUTPUT:\n" + content + "\n\n")
                f.write(f"ERROR: {str(e)}")
            logger.write(f"[ERROR] Parsing failed for case {case_index}: {e}\n")
            result = {"index": case_index, "error": str(e)}

    # Add index
    if isinstance(result, list):
        for d in result:
            d["index"] = case_index
    elif isinstance(result, dict):
        result["index"] = case_index

    with open(output_path, 'a') as f:
        f.write(json.dumps(result) + "\n")

    logger.write(f"[SUCCESS] Saved result for case {case_index}\n")
    logger.flush()
    return result


async def process_batch_async(batch_df, codebook, output_path, failed_dir, log_path, batch_size=100, delay_between_batches=10, with_reference = False):
    if not os.path.exists(failed_dir):
        os.makedirs(failed_dir)

    _, already_processed = load_results(output_path)
    logger = open(log_path, "a")
    codebook_json = codebook.to_dict('records')

    # Prepare tasks for unprocessed cases
    tasks = []
    for idx, row in batch_df.iterrows():
        case_index = int(row['index']) if 'index' in row else idx
        if case_index in already_processed:
            continue
        tasks.append(process_case(row, codebook_json, output_path, failed_dir, logger, with_reference))

    # Batch tasks and run with sleep in between
    total_tasks = len(tasks)
    num_batches = (total_tasks + batch_size - 1) // batch_size
    final_results = []

    for batch_num in range(num_batches):
        start = batch_num * batch_size
        end = min(start + batch_size, total_tasks)
        batch_tasks = tasks[start:end]
        print(f"Running batch {batch_num + 1}/{num_batches} ({end}/{total_tasks})")
        batch_results = await asyncio.gather(*batch_tasks)
        final_results.extend(batch_results)
        logger.flush()
        # Sleep except after last batch
        if batch_num < num_batches - 1:
            await asyncio.sleep(delay_between_batches)

    logger.close()
    print(f"Completed processing {len(final_results)} cases.")
    return final_results

