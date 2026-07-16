#!/usr/bin/env python3
"""
Stage 3 — evaluate LLM predictions against physician ground truth.

Reads one or more `<prefix>_summary.csv` files (produced by run_phenotyping.py, which
already carries the `*_ground_truth` columns) and computes per-field accuracy, Cohen's
kappa, and a classification report. Optionally prints physician inter-rater agreement
(P1 vs P2) from the adjudication sheet as an upper bound.

Ground truth is REQUIRED here: if a summary has no `*_ground_truth` columns (i.e. it was
produced from an unlabeled sheet), this raises an error — there is nothing to score.

Usage:
    ./evaluate.py --model gemini-2.5-pro
    ./evaluate.py --models gemini-2.5-pro claude-sonnet-4-6 llama-4-maverick
    ./evaluate.py --summary data/output/llm_phenotyping_gemini-2_5-pro_summary.csv --input data/input/adjudication.csv
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config.settings import OUTPUT_DIR, DEFAULT_INPUT_CSV  # noqa: E402
from src.evaluation import ALL_GT_COLUMNS, compute_metrics, print_metrics_summary  # noqa: E402
from src.uti_phenotyper import _snake_to_csv_name  # noqa: E402


def _summary_to_scored_df(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Reshape a summary CSV into the {key}_ground_truth / {key}_llm columns compute_metrics expects."""
    out = {}
    found_gt = False
    for key in ALL_GT_COLUMNS:
        display = _snake_to_csv_name(key)
        gt_col, llm_col = f"{display}_ground_truth", f"{display}_LLM"
        if gt_col in summary_df.columns:
            out[f"{key}_ground_truth"] = summary_df[gt_col]
            if summary_df[gt_col].notna().any():
                found_gt = True
        if llm_col in summary_df.columns:
            out[f"{key}_llm"] = summary_df[llm_col]
    if not found_gt:
        raise SystemExit(
            "ERROR: no ground-truth columns in this summary — nothing to score.\n"
            "Cause: either the sheet was unlabeled, or the summary was produced by an older\n"
            "run_phenotyping.py that didn't carry *_ground_truth columns.\n"
            "Fix: re-run ./run_phenotyping.py (on a labeled sheet) to regenerate the summary."
        )
    return pd.DataFrame(out)


def evaluate_one(summary_path: Path, output_dir: Path) -> dict:
    if not summary_path.exists():
        sys.exit(f"ERROR: summary not found: {summary_path}\n"
                 f"Run ./run_phenotyping.py for this model first.")
    summary_df = pd.read_csv(summary_path)
    scored = _summary_to_scored_df(summary_df)   # raises if no ground truth
    metrics = compute_metrics(scored)

    print(f"\n{'='*72}\n{summary_path.name}\n{'='*72}")
    print_metrics_summary(metrics)
    if "uti" in metrics and "classification_report" in metrics["uti"]:
        print("\nUTI classification report:")
        print(metrics["uti"]["classification_report"])

    metrics_path = output_dir / summary_path.name.replace("_summary.csv", "_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"Metrics saved: {metrics_path}")
    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate LLM predictions vs ground truth (Stage 3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--model", default=None, help="Single model name (default: gemini-2.5-pro)")
    g.add_argument("--models", nargs="+", help="Several model names to compare")
    g.add_argument("--summary", type=Path, help="Explicit path to a *_summary.csv")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_CSV,
                        help="Adjudication sheet for physician inter-rater agreement (optional)")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR,
                        help=f"Output directory (default: {OUTPUT_DIR})")
    args = parser.parse_args()

    def summary_for(model: str) -> Path:
        return args.output_dir / f"llm_phenotyping_{model.replace('.', '_')}_summary.csv"

    if args.summary:
        summaries = [args.summary]
    elif args.models:
        summaries = [summary_for(m) for m in args.models]
    else:
        summaries = [summary_for(args.model or "gemini-2.5-pro")]

    all_metrics = {s.stem: evaluate_one(s, args.output_dir) for s in summaries}

    # Multi-model kappa comparison for key fields.
    if len(all_metrics) > 1:
        key_fields = ["uti", "any_infection_present", "dysuria", "urinary_frequency",
                      "flank_cva_pain_tenderness", "ability_to_perceive_symptoms"]
        print(f"\n{'='*72}\nKappa comparison (key fields)\n{'='*72}")
        header = f"{'field':<38}" + "".join(f"{name[:16]:>18}" for name in all_metrics)
        print(header + "\n" + "-" * len(header))
        for field in key_fields:
            row = f"{field:<38}"
            for m in all_metrics.values():
                k = m.get(field, {}).get("cohen_kappa")
                row += f"{(f'{k:.3f}' if k is not None else 'N/A'):>18}"
            print(row)

    # Physician inter-rater agreement (optional upper bound).
    if args.input and args.input.exists():
        from src.evaluation import physician_agreement
        ira = physician_agreement(pd.read_csv(args.input, encoding="utf-8-sig"))
        if ira:
            print(f"\n{'='*72}\nPhysician inter-rater agreement (P1 vs P2)\n{'='*72}")
            print(f"{'field':<45}{'N':>5}{'accuracy':>10}{'kappa':>8}")
            print("-" * 68)
            for field, m in ira.items():
                k = f"{m['cohen_kappa']:.3f}" if m["cohen_kappa"] is not None else "N/A"
                print(f"{field:<45}{m['n_valid']:>5}{m['accuracy']:>10.3f}{k:>8}")


if __name__ == "__main__":
    main()
