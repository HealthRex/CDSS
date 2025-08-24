import os
import logging
import asyncio

from data.loader import load_data, load_codebook
from batch_runner import process_batch_async

BATCH_SIZE = 200
DELAY_BETWEEN_BATCHES = 5  # seconds, adjust as needed

def main():
    BASE_PATH = "prospective_test"
    os.makedirs(BASE_PATH, exist_ok=True)    

    output_path = os.path.join(BASE_PATH, "llm_results.jsonl")
    failed_dir = os.path.join(BASE_PATH, "failed_llm_outputs")
    log_path = os.path.join(BASE_PATH, "llm_judge_debug.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    logging.info("Starting main process.")

    # load codebook
    logging.info("Loading codebook...")
    codebook = load_codebook()
    logging.info(f"Codebook loaded with {len(codebook)} entries.")

    # load sample data
    logging.info("Loading sample data...")
    with_reference = True
    sample_data = load_data(size=1000, random_state=42, pre_defined=True, with_reference= with_reference, prospective = True)
    logging.info(f"Sample data loaded with {len(sample_data)} rows.")

    # get batch_df data
    logging.info("Selecting required columns for batch processing...")
    default_cols = ["index", "Patient Message", "Actual Response Sent to Patient", "Suggested Response from LLM"]
    if with_reference: 
        for i in range(2, 7):  # Reference pairs 2 through 6
            patient_col = f"Patient Message_{i}"
            response_col = f"Actual Response Sent to Patient_{i}"
            default_cols.append(patient_col)
            default_cols.append(response_col)
        batch_df = sample_data[default_cols]
    else:
        batch_df = sample_data[default_cols]
    logging.info(f"Prepared batch_df with {len(batch_df)} entries.")

    # execute batch_runner task async with batch size and delay
    logging.info("Starting async batch processing...")
    asyncio.run(
        process_batch_async(
            batch_df,
            codebook,
            output_path,
            failed_dir,
            log_path,
            batch_size=BATCH_SIZE,
            delay_between_batches=DELAY_BETWEEN_BATCHES,
            with_reference= with_reference
        )
    )
    logging.info("Async batch processing completed.")

if __name__ == "__main__":
    main()
