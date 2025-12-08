#!/usr/bin/env python3
"""
Minimal async batch classifier (Fabre-prepared data) – JSON-aware.

Changes vs prior minimal Fabre version:
- Expects the LLM to return JSON with keys: Classification, Rationale.
- Writes two output columns: classification, rationale (plus final_label).
- Final CSV columns (exactly):
  anon_id, pat_enc_csn_id_coded, order_proc_id_coded,
  blood_culture_order_datetime_utc, final_label, classification, rationale
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

from prompt import PROMPT

load_dotenv()


class MinimalAsyncClassifierFabreV2:
    def __init__(
        self,
        source_csv: Optional[str] = None,
        data_dir: Optional[str] = None,
        max_concurrent: int = 6,
        delay_between_requests: float = 1.0,
        batch_size: int = 10,
        checkpoint_interval: int = 10,
        EHR_IncludeInprompt: bool = False,
    ):
        # Source data
        self.default_source_csv = "/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data/Fabre_labeled_ED_notes_with_EHR.csv"
        self.source_csv = source_csv or self.default_source_csv

        # Output / working dir
        base_data_dir = os.path.dirname(self.default_source_csv)
        if data_dir is None:
            self.data_dir = os.path.join(
                base_data_dir, f"EHR_IncludeInprompt_{EHR_IncludeInprompt}_fabre_minimal_v2"
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

        # Persisted state paths
        self.checkpoint_file = os.path.join(self.data_dir, "classification_checkpoint_fabre_minimal_v2.pkl")
        self.df_backup_file = os.path.join(self.data_dir, "Fabre_df_note_backup_minimal_v2.csv")

        # Required output columns
        self.target_output_cols = [
            "anon_id",
            "pat_enc_csn_id_coded",
            "order_proc_id_coded",
            "blood_culture_order_datetime_utc",
            "final_label",
            "classification",
            "rationale",
        ]

        # API
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

        print("✅ Minimal Fabre classifier v2 initialized")
        print(f"   Source CSV: {self.source_csv}")
        print(f"   Output dir: {self.data_dir}")
        print(f"   Max concurrent: {self.max_concurrent}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Delay between batches: {self.delay_between_requests}s")
        print(f"   Checkpoint interval: {self.checkpoint_interval}")
        print(f"   Include EHR in prompt: {self.EHR_IncludeInprompt}")

    # --------------------
    # Data loading helpers
    # --------------------
    def load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.source_csv):
            raise FileNotFoundError(f"Source CSV not found: {self.source_csv}")

        df = pd.read_csv(self.source_csv)
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

        # Ensure final_label exists
        if "final_label" not in df.columns:
            if "Label" in df.columns:
                df["final_label"] = df["Label"]
            elif "Final_Label" in df.columns:
                df["final_label"] = df["Final_Label"]
            else:
                df["final_label"] = None
                print("⚠️ No final_label column found; set to None")

        # Initialize prediction columns
        for col in ("classification", "rationale"):
            if col not in df.columns:
                df[col] = None

        return df

    def load_checkpoint(self) -> set:
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "rb") as f:
                processed_indices = pickle.load(f)
            print(f"✅ Loaded checkpoint with {len(processed_indices)} rows")
            return processed_indices
        print("ℹ️ No checkpoint found; starting fresh")
        return set()

    def load_working_data(self, df_original: pd.DataFrame, processed_indices: set) -> pd.DataFrame:
        df_working = df_original.copy()

        if os.path.exists(self.df_backup_file) and processed_indices:
            try:
                df_backup = pd.read_csv(self.df_backup_file)
                restored = 0
                for idx in processed_indices:
                    if idx < len(df_backup) and idx < len(df_working):
                        if pd.notna(df_backup.at[idx, "classification"]):
                            df_working.at[idx, "classification"] = df_backup.at[idx, "classification"]
                        if pd.notna(df_backup.at[idx, "rationale"]):
                            df_working.at[idx, "rationale"] = df_backup.at[idx, "rationale"]
                        restored += 1
                print(f"✅ Restored {restored} rows from backup")
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️ Could not load backup; continuing fresh ({exc})")

        return df_working

    # --------------------
    # Request / parsing
    # --------------------
    async def classify_single_row(self, session, row_data: Tuple[int, str, str, Optional[str]]):
        idx, anon_id, note_text, ehr = row_data
        if not self.EHR_IncludeInprompt:
            ehr = None

        max_retries = 3
        base_delay = 0.5

        for attempt in range(max_retries):
            async with self.semaphore:
                try:
                    raw_result = await self.make_api_request(session, anon_id, note_text, ehr)
                    classification, rationale = self._parse_json_result(raw_result)
                    return idx, classification, rationale, None
                except aiohttp.ClientResponseError as exc:
                    if exc.status == 429 and attempt < max_retries - 1:
                        retry_delay = base_delay * (2**attempt)
                        print(f"429 for row {idx}; retrying in {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                        continue
                    return idx, "ERROR", None, str(exc)
                except Exception as exc:  # noqa: BLE001
                    if attempt < max_retries - 1:
                        retry_delay = base_delay * (2**attempt)
                        print(f"Error row {idx}; retrying in {retry_delay}s: {exc}")
                        await asyncio.sleep(retry_delay)
                        continue
                    return idx, "ERROR", None, str(exc)
        return idx, "ERROR", None, "Max retries exceeded"

    async def make_api_request(self, session, anon_id: str, note_text: str, ehr: Optional[str]):
        normalized_note = re.sub(r"\s+", " ", note_text.replace("\n", " ")).strip()

        question = f"{PROMPT}\n\nanon_id: {anon_id}\n\nNOTE:\n{normalized_note}"
        if ehr:
            question += f"\nStructured EHR data is provided below:\n\nEHR:\n{ehr}"
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

    def _parse_json_result(self, raw_result: str) -> Tuple[str, str]:
        """
        Parse the JSON result from the LLM.
        Falls back to simple extraction if JSON parsing fails.
        """
        if isinstance(raw_result, str):
            try:
                parsed = json.loads(raw_result)
                classification = parsed.get("Classification", "Undetermined")
                rationale = parsed.get("Rationale", "")
                # Normalize classification text
                classification = str(classification).strip().upper()
                if classification not in {"HIGH", "INTERMEDIATE", "LOW", "UNDETERMINED"}:
                    # Attempt regex if unexpected value
                    classification = self._extract_classification(classification)
                return classification, str(rationale).strip()
            except Exception:
                # Not valid JSON, fallback
                pass

        # Fallback: attempt to extract classification from raw text; rationale empty
        classification = self._extract_classification(raw_result if isinstance(raw_result, str) else "")
        return classification, ""

    def _extract_classification(self, raw_result: str) -> str:
        if not isinstance(raw_result, str):
            return "UNDETERMINED"
        match = re.search(r"\b(high|intermediate|low|undetermined)\b", raw_result, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return "UNDETERMINED"

    # --------------------
    # Persistence
    # --------------------
    async def save_checkpoint(self, processed_indices: set, df_working: pd.DataFrame):
        async with self.lock:
            if processed_indices:
                with open(self.checkpoint_file, "wb") as f:
                    pickle.dump(processed_indices, f)
                df_working.to_csv(self.df_backup_file, index=False)
                print(f"💾 Checkpoint saved ({len(processed_indices)} rows)")

    def save_final_results(self, df_working: pd.DataFrame) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_path = os.path.join(
            self.data_dir, f"blood_culture_llm_predictions_fabre_minimal_v2_{timestamp}.csv"
        )

        missing_final = set(self.target_output_cols) - set(df_working.columns)
        if missing_final:
            raise ValueError(f"Missing required columns for output: {missing_final}")

        df_working[self.target_output_cols].to_csv(final_path, index=False)
        print(f"✅ Final minimal results saved: {final_path}")
        return final_path

    # --------------------
    # Processing
    # --------------------
    def batchify(self, lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i : i + batch_size]

    async def process_async(self, df_working: pd.DataFrame, processed_indices: set):
        rows_to_process = []
        for idx, row in df_working.iterrows():
            if idx not in processed_indices:
                rows_to_process.append(
                    (idx, row["anon_id"], row["deid_note_text"], row.get("EHR"))
                )

        if not rows_to_process:
            print("✅ Nothing to process; all rows completed.")
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
                        idx, classification, rationale, error = await coro

                        if classification != "ERROR":
                            df_working.at[idx, "classification"] = classification
                            df_working.at[idx, "rationale"] = rationale
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
        start = time.time()
        df_original = self.load_data()
        processed_indices = self.load_checkpoint()
        df_working = self.load_working_data(df_original, processed_indices)

        df_working, processed_indices = await self.process_async(df_working, processed_indices)
        await self.save_checkpoint(processed_indices, df_working)

        final_path = self.save_final_results(df_working)

        duration = time.time() - start
        print("\n🎉 Minimal Fabre classification v2 complete")
        print(f"   Rows processed (success): {self.processed_count}")
        print(f"   Errors: {self.error_count}")
        if self.processed_count:
            print(f"   Avg time per row: {duration / self.processed_count:.2f}s")
        print(f"   Total time: {duration:.1f}s")
        print(f"   Final file: {final_path}")
        return final_path


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Minimal async LLM classification (Fabre data, JSON-aware)")
    parser.add_argument(
        "--source-csv",
        default=None,
        help="Optional override for source CSV; defaults to Fabre_labeled_ED_notes_with_EHR.csv",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Optional output directory. Defaults to EHR_IncludeInprompt_<flag>_fabre_minimal_v2 under the data folder.",
    )
    parser.add_argument("--concurrent", type=int, default=6, help="Max concurrent requests")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between batches (seconds)")
    parser.add_argument("--batch-size", type=int, default=10, help="Rows per batch")
    parser.add_argument("--checkpoint-interval", type=int, default=10, help="Rows between checkpoints")
    parser.add_argument(
        "--EHR_IncludeInprompt",
        action="store_true",
        help="Include EHR column in prompt if present",
    )

    args = parser.parse_args()

    classifier = MinimalAsyncClassifierFabreV2(
        source_csv=args.source_csv,
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

