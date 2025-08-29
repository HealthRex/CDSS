import os
import logging
import asyncio
from data.loader import load_data, load_codebook
from util.DSPy_modules import ErrorIdentifierModule
from batch_runner_DSPy_ import batch_pipeline_runner  # <--- import your runner
import time

async def main_single_run(BASE_PATH, with_reference=False, size=20, sleep_per_task = 1.5):
    start = time.time()
    os.makedirs(BASE_PATH, exist_ok=True)

    identifier_path_output = os.path.join(BASE_PATH, "identifier_results.jsonl")
    labeler_path_output = os.path.join(BASE_PATH, "labeler_results.jsonl")
    log_path = os.path.join(BASE_PATH, "llm_judge_debug.log")

    # Logging setup
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)
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
    
    logging.info(f"Running with reference: {with_reference}")
    logging.info(f"Running with size: {size}")

    logging.info("Loading codebook...")
    codebook = load_codebook()
    logging.info(f"Codebook loaded with {len(codebook)} entries.")

    logging.info("Loading sample data...")
    sample_data = load_data(size=size, random_state=42,cache= True, force_resample= False)
    logging.info(f"Sample data loaded with {len(sample_data)} rows.")

    identifier = ErrorIdentifierModule()
    logging.info("Starting batch async process...")

    await batch_pipeline_runner(
        sample_data, codebook, identifier, with_reference,
        identifier_path_output, labeler_path_output,
        batch_size=10, delay_between_batches=4, sleep_per_task=sleep_per_task
    )

    elapsed = time.time() - start
    logging.info(f"Batch run completed in {elapsed:.1f} seconds.")

async def main():
    size = 500
    await main_single_run(BASE_PATH=f"src/DSPy_results_batch_{size}_dedup_with_prev_msg", with_reference=False, size=size, sleep_per_task=1.2)
    await main_single_run(BASE_PATH=f"src/DSPy_results_batch_{size}_dedup_with_prev_msg_w_ref", with_reference=True, size=size, sleep_per_task=1.6)


if __name__ == "__main__":
    asyncio.run(main())
