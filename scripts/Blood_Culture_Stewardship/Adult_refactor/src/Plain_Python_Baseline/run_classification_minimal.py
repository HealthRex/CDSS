#!/usr/bin/env python3
"""
Runner for the minimal batch classifier.

Outputs a CSV with exactly:
anon_id, pat_enc_csn_id_coded, order_proc_id_coded,
blood_culture_order_datetime_utc, final_label, llm_prediction_result.
"""

import argparse
import asyncio
import os
import sys

# Allow local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parallel_classify_minimal import MinimalAsyncClassifier


async def main():
    parser = argparse.ArgumentParser(description="Minimal async LLM classification runner")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Optional output directory. Defaults to EHR_IncludeInprompt_<flag>_minimal under base data.",
    )
    parser.add_argument("--concurrent", type=int, default=6, help="Max concurrent requests (default: 6)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between batches in seconds (default: 1.0)")
    parser.add_argument("--batch-size", type=int, default=10, help="Rows per batch (default: 10)")
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=10,
        help="Save checkpoint every N rows (default: 10)",
    )
    parser.add_argument(
        "--EHR_IncludeInprompt",
        action="store_true",
        help="Include EHR column in prompt if present",
    )

    args = parser.parse_args()

    base_data_dir = "/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data"
    source_file = os.path.join(base_data_dir, "Test_set_df_note_ORIGINAL_new.csv")

    if args.data_dir is None:
        args.data_dir = os.path.join(
            base_data_dir, f"EHR_IncludeInprompt_{args.EHR_IncludeInprompt}_minimal"
        )

    print("🚀 Minimal classification runner")
    print(f"Source data: {source_file}")
    print(f"Output dir: {args.data_dir}")

    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        print("Please generate the source data (e.g., via prepare_test_data.py) before running.")
        return

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

