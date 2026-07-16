#!/usr/bin/env python3
"""
Stage 2 — LLM UTI phenotyping (inference).

Reads an adjudication sheet + the curated notes (from Stage 1) and runs a PHI-safe
LLM over each note's `deid_note_text`, writing one structured record per note.

Ground truth is optional: if the sheet has no `*_ground_truth` columns, this still
runs the LLM and writes predictions (with a warning) but skips the accuracy line.

Usage:
    ./run_phenotyping.py --model gemini-2.5-pro
    ./run_phenotyping.py --model claude-sonnet-4-6 --limit 50
    ./run_phenotyping.py --input data/input/other_sheet.csv --model gemini-2.5-flash

Results are written incrementally to the output dir so progress is never lost.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

load_dotenv(SCRIPT_DIR / ".env")

from config.settings import DEFAULT_INPUT_CSV, DEFAULT_CURATED_CSV, OUTPUT_DIR  # noqa: E402
from src.uti_phenotyper import (  # noqa: E402
    SYMPTOM_DEFINITIONS,
    FINAL_ASSESSMENT_DEFINITIONS,
    _snake_to_csv_name,
)

# All ground-truth column names as they appear in the adjudication sheet.
GT_COLUMNS = [f"{_snake_to_csv_name(k)}_ground_truth"
              for k in list(SYMPTOM_DEFINITIONS) + list(FINAL_ASSESSMENT_DEFINITIONS)]
UTI_GT_COL = "UTI?_ground_truth"


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------

def load_and_merge(adj_csv: Path, notes_csv: Path) -> pd.DataFrame:
    df_adj = pd.read_csv(adj_csv, encoding="utf-8-sig")
    df_notes = pd.read_csv(notes_csv)

    df_adj["mrn_str"] = df_adj["patient_MRN"].astype(str).str.strip()
    df_notes["mrn_str"] = df_notes["mrn"].astype(str).str.strip()

    df_adj["note_dt"] = pd.to_datetime(
        df_adj["Note Date/Time (Collins)"].fillna(df_adj["Note Date/Time (Lee)"]),
        errors="coerce",
    ).dt.floor("min")

    df_notes["note_dt"] = pd.to_datetime(
        df_notes["input_note_time"], errors="coerce"
    ).dt.floor("min")

    df_merged = df_adj.merge(
        df_notes[["mrn_str", "note_dt", "deid_note_text", "note_type"]],
        on=["mrn_str", "note_dt"],
        how="inner",
    )

    print(f"Matched {len(df_merged)} / {len(df_adj)} adjudication rows")
    return df_merged


# ---------------------------------------------------------------------------
# Incremental runner
# ---------------------------------------------------------------------------

def run(model: str, input_csv: Path, curated_csv: Path, output_dir: Path,
        limit, output_prefix: str, resume: bool) -> None:
    from src.uti_phenotyper import UTIPhenotyper, UTIPhenotypeResult

    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / f"{output_prefix}_results.jsonl"
    summary_path = output_dir / f"{output_prefix}_summary.csv"

    df = load_and_merge(input_csv, curated_csv)

    # Ground truth is optional — warn and continue if absent.
    has_gt = UTI_GT_COL in df.columns and df[UTI_GT_COL].notna().any()
    if not has_gt:
        print("WARNING: no UTI ground-truth column found in the input sheet — "
              "running inference only; accuracy will not be computed.")
    present_gt_cols = [c for c in GT_COLUMNS if c in df.columns]

    if limit:
        df = df.head(limit)
        print(f"Limited to {limit} rows")

    done_indices = set()
    if resume and results_path.exists():
        with open(results_path) as f:
            for line in f:
                done_indices.add(json.loads(line)["row_index"])
        print(f"Resuming — {len(done_indices)} rows already done")

    phenotyper = UTIPhenotyper(model_name=model)
    total = len(df)
    start_time = time.time()

    with open(results_path, "a") as out_f:
        for i, (_, row) in enumerate(df.iterrows()):
            if i in done_indices:
                continue

            elapsed = time.time() - start_time
            done_so_far = i - len(done_indices) + 1
            eta_str = ""
            if done_so_far > 1:
                rate = elapsed / done_so_far
                eta_str = f" | ETA {((total - i - 1) * rate)/60:.1f} min"
            print(f"[{model}] {i+1}/{total}{eta_str} ...", end=" ", flush=True)

            try:
                result = phenotyper.phenotype(row["deid_note_text"])
                status = "PARSE_ERR" if result.parse_error else result.uti.label
                print(f"UTI={status}")
            except Exception as e:
                result = UTIPhenotypeResult(model_name=model, parse_error=str(e))
                print(f"ERROR: {e}")

            record = {
                "row_index": i,
                "patient_MRN": str(row.get("patient_MRN", "")),
                "note_dt": str(row.get("note_dt", "")),
                "note_type": str(row.get("note_type", "")),
                "model": model,
                **result.to_flat_dict(),
            }
            # Carry every available ground-truth column so the summary is
            # self-contained for evaluate.py (empty when the sheet is unlabeled).
            for col in present_gt_cols:
                record[col] = row.get(col)
            out_f.write(json.dumps(record) + "\n")
            out_f.flush()

    # JSONL -> summary CSV
    records = [json.loads(line) for line in open(results_path)]
    df_res = pd.DataFrame(records)
    df_res.to_csv(summary_path, index=False)

    print(f"\nDone in {(time.time() - start_time)/60:.1f} min.")
    print(f"  results: {results_path}")
    print(f"  summary: {summary_path}")

    # Quick UTI accuracy — only when ground truth is present.
    if has_gt and UTI_GT_COL in df_res.columns and "UTI?_LLM" in df_res.columns:
        valid = df_res[df_res[UTI_GT_COL].notna() & df_res["UTI?_LLM"].notna()]
        if len(valid):
            acc = (valid[UTI_GT_COL].astype(str).str.strip()
                   == valid["UTI?_LLM"].astype(str).str.strip()).mean()
            print(f"UTI accuracy vs ground truth: {acc:.3f} (n={len(valid)})")
    else:
        print("(no ground truth — skipped accuracy; run evaluate.py once labels exist)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run LLM UTI phenotyping (Stage 2 inference)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", default="gemini-2.5-pro",
                        help="Vertex model name (default: gemini-2.5-pro). "
                             "Others: gemini-2.5-flash, claude-opus-4-7, claude-sonnet-4-6, "
                             "claude-haiku-4-5, llama-4-maverick, llama-4-scout")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_CSV,
                        help=f"Adjudication sheet (default: {DEFAULT_INPUT_CSV})")
    parser.add_argument("--curated", type=Path, default=DEFAULT_CURATED_CSV,
                        help=f"Curated notes from Stage 1 (default: {DEFAULT_CURATED_CSV})")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR,
                        help=f"Output directory (default: {OUTPUT_DIR})")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only process first N rows (quick test)")
    parser.add_argument("--output-prefix", default=None,
                        help="Prefix for output files (default: llm_phenotyping_<model>)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Start fresh even if partial results exist")
    args = parser.parse_args()

    for label, path in [("input sheet", args.input), ("curated notes", args.curated)]:
        if not path.exists():
            sys.exit(
                f"ERROR: {label} not found: {path}\n"
                f"  - input sheet: place your adjudication CSV at the path above "
                f"(or pass --input <path>). PHI inputs are shared separately (see README).\n"
                f"  - curated notes: run ./build_curated_dataset.py first to create it."
            )

    prefix = args.output_prefix or f"llm_phenotyping_{args.model.replace('.', '_')}"
    run(
        model=args.model,
        input_csv=args.input,
        curated_csv=args.curated,
        output_dir=args.output_dir,
        limit=args.limit,
        output_prefix=prefix,
        resume=not args.no_resume,
    )


if __name__ == "__main__":
    main()
