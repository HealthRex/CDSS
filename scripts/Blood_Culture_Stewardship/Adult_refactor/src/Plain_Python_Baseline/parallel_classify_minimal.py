#!/usr/bin/env python3
"""
Minimal async batch classifier.

Differences from parallel_classify.py:
- Keeps original data intact and writes all outputs to a new folder.
- Stores only llm_prediction_result during processing.
- Final CSV is limited to:
  anon_id, pat_enc_csn_id_coded, order_proc_id_coded,
  blood_culture_order_datetime_utc, final_label, llm_prediction_result.
"""

import asyncio
import json
import os
import pickle
import re
import time
from datetime import datetime
from typing import Optional, Tuple

import aiohttp
import pandas as pd
from dotenv import load_dotenv
from tqdm.asyncio import tqdm

# Ensure environment variables are available
load_dotenv()

# Local import for PROMPT text
from prompt import PROMPT


class MinimalAsyncClassifier:
    def __init__(
        self,
        data_dir: Optional[str] = None,
        max_concurrent: int = 6,
        delay_between_requests: float = 1.0,
        batch_size: int = 10,
        checkpoint_interval: int = 10,
        EHR_IncludeInprompt: bool = False,
    ):
        # Base data (original source file lives here)
        self.base_data_dir = "/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data"
        self.original_file = os.path.join(self.base_data_dir, "Test_set_df_note_ORIGINAL_new.csv")

        # Working/output directory (separate from the original run)
        if data_dir is None:
            self.data_dir = os.path.join(
                self.base_data_dir, f"EHR_IncludeInprompt_{EHR_IncludeInprompt}_minimal"
            )
        else:
            self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        # Runtime knobs
        self.max_concurrent = max_concurrent
        self.delay_between_requests = delay_between_requests
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval
        self.EHR_IncludeInprompt = EHR_IncludeInprompt

        # File paths (names are distinct from the original pipeline)
        self.checkpoint_file = os.path.join(self.data_dir, "classification_checkpoint_minimal.pkl")
        self.df_backup_file = os.path.join(self.data_dir, "Test_set_df_note_backup_minimal.csv")

        # Columns we keep in the final output
        self.target_output_cols = [
            "anon_id",
            "pat_enc_csn_id_coded",
            "order_proc_id_coded",
            "blood_culture_order_datetime_utc",
            "final_label",
            "llm_prediction_result",
        ]

        # API settings
        self.api_url = os.getenv("API_URL")
        self.api_headers = {
            os.getenv("API_HEADER_KEY"): os.getenv("API_KEY"),
            "Content-Type": "application/json",
        }

        # Async helpers
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.lock = asyncio.Lock()
        self.processed_count = 0
        self.error_count = 0

        print(f"✅ Minimal classifier initialized.")
        print(f"   Data dir: {self.data_dir}")
        print(f"   Max concurrent: {self.max_concurrent}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Delay between batches: {self.delay_between_requests}s")
        print(f"   Checkpoint interval: {self.checkpoint_interval}")
        print(f"   Include EHR in prompt: {self.EHR_IncludeInprompt}")

    # --------------------
    # Data loading helpers
    # --------------------
    def load_data(self) -> pd.DataFrame:
        """Load the source dataset required for classification."""
        if not os.path.exists(self.original_file):
            raise FileNotFoundError(f"Source file not found: {self.original_file}")

        df = pd.read_csv(self.original_file)
        print(f"✅ Loaded source data: {df.shape}")

        required_cols = {
            "anon_id",
            "deid_note_text",
            "pat_enc_csn_id_coded",
            "order_proc_id_coded",
            "blood_culture_order_datetime_utc",
        }
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns in source data: {missing}")

        # Ensure a working label column is available for final output
        if "final_label" not in df.columns:
            if "Label" in df.columns:
                df["final_label"] = df["Label"]
            elif "Final_Label" in df.columns:
                df["final_label"] = df["Final_Label"]
            else:
                df["final_label"] = None  # graceful placeholder
                print("⚠️ No label column found; final_label set to None")

        return df

    def load_checkpoint(self) -> set:
        """Return the set of processed row indices if a checkpoint exists."""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "rb") as f:
                processed_indices = pickle.load(f)
            print(f"✅ Loaded checkpoint with {len(processed_indices)} processed rows")
            return processed_indices
        print("ℹ️ No checkpoint found; starting fresh")
        return set()

    def load_working_data(self, df_original: pd.DataFrame, processed_indices: set) -> pd.DataFrame:
        """Create a working copy and restore any saved predictions."""
        df_working = df_original.copy()
        result_col = "llm_prediction_result"

        if result_col not in df_working.columns:
            df_working[result_col] = None
            print(f"✅ Initialized column: {result_col}")

        if os.path.exists(self.df_backup_file) and processed_indices:
            try:
                df_backup = pd.read_csv(self.df_backup_file)
                restored = 0
                for idx in processed_indices:
                    if idx < len(df_backup) and idx < len(df_working):
                        if pd.notna(df_backup.at[idx, result_col]):
                            df_working.at[idx, result_col] = df_backup.at[idx, result_col]
                            restored += 1
                print(f"✅ Restored {restored} predictions from backup")
            except Exception as exc:
                print(f"⚠️ Could not load backup results: {exc}")

        return df_working

    # --------------------
    # Request / parsing
    # --------------------
    async def classify_single_row(self, session, row_data: Tuple[int, str, str, Optional[str]]):
        """Classify one row with simple retry + concurrency control."""
        idx, anon_id, note_text, ehr = row_data
        if not self.EHR_IncludeInprompt:
            ehr = None

        max_retries = 3
        base_delay = 0.5

        for attempt in range(max_retries):
            async with self.semaphore:
                try:
                    raw_result = await self.make_api_request(session, anon_id, note_text, ehr)
                    cleaned = self._extract_classification(raw_result)
                    return idx, cleaned, None
                except aiohttp.ClientResponseError as exc:
                    if exc.status == 429 and attempt < max_retries - 1:
                        retry_delay = base_delay * (2 ** attempt)
                        print(f"Rate limit hit for row {idx}; retrying in {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                        continue
                    return idx, "ERROR", str(exc)
                except Exception as exc:  # noqa: BLE001
                    if attempt < max_retries - 1:
                        retry_delay = base_delay * (2 ** attempt)
                        print(f"Error on row {idx}; retrying in {retry_delay}s: {exc}")
                        await asyncio.sleep(retry_delay)
                        continue
                    return idx, "ERROR", str(exc)

        return idx, "ERROR", "Max retries exceeded"

    async def make_api_request(self, session, anon_id: str, note_text: str, EHR: Optional[str]):
        """Send the prompt to the LLM and return its raw string result."""
        normalized_note = re.sub(r"\s+", " ", note_text.replace("\n", " ")).strip()

        question = f"{PROMPT}\n\nanon_id: {anon_id}\n\nNOTE:\n{normalized_note}"
        if EHR:
            question += f"\nStructured EHR data is provided below:\n\nEHR:\n{EHR}"
        else:
            question += "\nStructured EHR data is not provided."

        payload = {"model": "gpt-5", "messages": [{"role": "user", "content": question}]}

        async with session.post(
            self.api_url,
            headers=self.api_headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data["choices"][0]["message"]["content"]

    def _extract_classification(self, raw_result: str) -> str:
        """
        Normalize the LLM output down to the allowed labels.
        Returns the first valid match; otherwise the stripped raw result.
        """
        if not isinstance(raw_result, str):
            return "Undetermined"

        match = re.search(r"\b(high|intermediate|low|undetermined)\b", raw_result, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Fallback to stripped text; keeps visibility if LLM deviates
        return raw_result.strip()

    # --------------------
    # Persistence
    # --------------------
    async def save_checkpoint(self, processed_indices: set, df_working: pd.DataFrame):
        """Persist progress and the working dataframe."""
        async with self.lock:
            if processed_indices:
                with open(self.checkpoint_file, "wb") as f:
                    pickle.dump(processed_indices, f)
                df_working.to_csv(self.df_backup_file, index=False)
                print(f"💾 Checkpoint saved ({len(processed_indices)} rows)")

    def save_final_results(self, df_working: pd.DataFrame) -> str:
        """Write the final CSV with only the requested columns."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = os.path.join(
            self.data_dir, f"blood_culture_llm_predictions_minimal_{timestamp}.csv"
        )

        # Build minimal view
        subset = df_working.copy()
        if "final_label" not in subset.columns and "Label" in subset.columns:
            subset["final_label"] = subset["Label"]
        elif "final_label" not in subset.columns and "Final_Label" in subset.columns:
            subset["final_label"] = subset["Final_Label"]

        missing_final = set(self.target_output_cols) - set(subset.columns)
        if missing_final:
            raise ValueError(f"Missing required columns for output: {missing_final}")

        subset = subset[self.target_output_cols]
        subset.to_csv(final_path, index=False)
        print(f"✅ Final minimal results saved: {final_path}")
        return final_path

    # --------------------
    # Processing loop
    # --------------------
    def batchify(self, lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i : i + batch_size]

    async def process_async(self, df_working: pd.DataFrame, processed_indices: set):
        """Process all unprocessed rows in batches."""
        rows_to_process = []
        for idx, row in df_working.iterrows():
            if idx not in processed_indices:
                rows_to_process.append(
                    (idx, row["anon_id"], row["deid_note_text"], row.get("EHR"))
                )

        if not rows_to_process:
            print("✅ Nothing to process; all rows already completed.")
            return df_working, processed_indices

        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=300)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            total_batches = len(list(self.batchify(rows_to_process, self.batch_size)))
            for batch_index, batch in enumerate(self.batchify(rows_to_process, self.batch_size), start=1):
                print(f"Processing batch {batch_index}/{total_batches} ({len(batch)} rows)")
                tasks = [self.classify_single_row(session, row_data) for row_data in batch]

                with tqdm(total=len(tasks), desc=f"Batch {batch_index}") as pbar:
                    for coro in asyncio.as_completed(tasks):
                        idx, result, error = await coro

                        if result != "ERROR":
                            df_working.at[idx, "llm_prediction_result"] = result
                            processed_indices.add(idx)
                            async with self.lock:
                                self.processed_count += 1
                        else:
                            async with self.lock:
                                self.error_count += 1
                            if error:
                                print(f"❌ Row {idx} failed: {error}")

                        pbar.update(1)

                await self.save_checkpoint(processed_indices, df_working)

                if batch_index < total_batches:
                    print(f"Waiting {self.delay_between_requests}s before next batch...")
                    await asyncio.sleep(self.delay_between_requests)

        return df_working, processed_indices

    async def run(self):
        """End-to-end minimal processing flow."""
        start = time.time()
        df_original = self.load_data()
        processed_indices = self.load_checkpoint()
        df_working = self.load_working_data(df_original, processed_indices)

        df_working, processed_indices = await self.process_async(df_working, processed_indices)
        await self.save_checkpoint(processed_indices, df_working)

        final_path = self.save_final_results(df_working)

        duration = time.time() - start
        print("\n🎉 Minimal classification complete")
        print(f"   Rows processed (success): {self.processed_count}")
        print(f"   Errors: {self.error_count}")
        if self.processed_count:
            print(f"   Avg time per row: {duration / self.processed_count:.2f}s")
        print(f"   Total time: {duration:.1f}s")
        print(f"   Final file: {final_path}")
        return final_path


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Minimal Async LLM Classification Pipeline")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Optional output directory; defaults to EHR_IncludeInprompt_<flag>_minimal under base data dir",
    )
    parser.add_argument("--concurrent", type=int, default=6, help="Max concurrent requests")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between batches (seconds)")
    parser.add_argument("--batch-size", type=int, default=10, help="Rows per batch")
    parser.add_argument("--checkpoint-interval", type=int, default=10, help="Rows between checkpoints")
    parser.add_argument(
        "--EHR_IncludeInprompt",
        action="store_true",
        help="Include EHR column in prompt (if present in data)",
    )

    args = parser.parse_args()

    classifier = MinimalAsyncClassifier(
        data_dir=args.data_dir,
        max_concurrent=args.concurrent,
        delay_between_requests=args.delay,
        batch_size=args.batch_size,
        checkpoint_interval=args.checkpoint_interval,
        EHR_IncludeInprompt=args.EHR_IncludeInprompt,
    )
    await classifier.run()


if __name__ == "__main__":
    asyncio.run(main())

