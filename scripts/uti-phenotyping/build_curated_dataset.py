#!/usr/bin/env python3
"""
Stage 1 — build the curated dataset from an adjudication sheet.

For each labeled case (MRN + urine-culture order time + note time) this maps the MRN
to its de-identified `anon_id`, de-jitters the BigQuery timestamps, and pulls the
matching note text, writing:
    <output-dir>/curated_dataset.csv    (one row per case, incl. deid_note_text)
    <output-dir>/mapping_summary.csv    (per-case mapping diagnostics)

Requires BigQuery access to som-nero-phi-jonc101 (+ -secure):
    gcloud auth application-default login

Usage:
    ./build_curated_dataset.py
    ./build_curated_dataset.py --input data/input/other_sheet.csv --output-dir data/output
"""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config.settings import DEFAULT_INPUT_CSV, OUTPUT_DIR  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Build curated_dataset.csv from an adjudication sheet (Stage 1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_CSV,
                        help=f"Adjudication sheet (default: {DEFAULT_INPUT_CSV})")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR,
                        help=f"Output directory (default: {OUTPUT_DIR})")
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit(
            f"ERROR: input sheet not found: {args.input}\n"
            f"Place your adjudication CSV at that path (or pass --input <path>).\n"
            f"PHI input files are shared separately (see README, 'Data setup')."
        )

    # Imported here so --help / the not-found check work without BigQuery creds.
    from src.data_mapper import UTIDataMapper

    args.output_dir.mkdir(parents=True, exist_ok=True)

    mapper = UTIDataMapper()
    mapper.load_labeled_cases(str(args.input))
    results = mapper.process_all_cases(output_dir=str(args.output_dir))

    n_ok = sum(1 for r in results if not r.get("error"))
    print(f"\nDone. {n_ok}/{len(results)} cases mapped.")
    print(f"  {args.output_dir / 'curated_dataset.csv'}")
    print(f"  {args.output_dir / 'mapping_summary.csv'}")
    if n_ok < len(results):
        print("  (see mapping_summary.csv for cases that did not match)")


if __name__ == "__main__":
    main()
