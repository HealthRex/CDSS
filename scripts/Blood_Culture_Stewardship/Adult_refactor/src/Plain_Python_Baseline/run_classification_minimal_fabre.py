#!/usr/bin/env python3
"""
Runner for the Fabre minimal batch classifier.

Defaults:
- Source CSV: /Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data/Fabre_labeled_ED_notes_with_EHR.csv
- Output dir: .../src/data/EHR_IncludeInprompt_<flag>_fabre_minimal/
- Output columns: anon_id, pat_enc_csn_id_coded, order_proc_id_coded,
                  blood_culture_order_datetime_utc, final_label, llm_prediction_result
"""

import argparse
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parallel_classify_minimal_fabre import MinimalAsyncClassifierFabre


async def main():
    parser = argparse.ArgumentParser(description="Run minimal Fabre LLM classification")
    parser.add_argument(
        "--source-csv",
        default=None,
        help="Optional override for source CSV (defaults to Fabre_labeled_ED_notes_with_EHR.csv)",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Optional output directory. Defaults to EHR_IncludeInprompt_<flag>_fabre_minimal under the data folder.",
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
    default_source = os.path.join(base_data_dir, "Fabre_labeled_ED_notes_with_EHR.csv")
    if args.source_csv is None:
        args.source_csv = default_source

    if args.data_dir is None:
        args.data_dir = os.path.join(
            base_data_dir, f"EHR_IncludeInprompt_{args.EHR_IncludeInprompt}_fabre_minimal"
        )

    print("🚀 Fabre minimal classification runner")
    print(f"Source CSV: {args.source_csv}")
    print(f"Output dir: {args.data_dir}")

    classifier = MinimalAsyncClassifierFabre(
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

