#!/usr/bin/env python3
"""
Symptom Feature Analysis for LLM UTI Phenotyping
=================================================
Runs on definitive ground truth cases only (UTI = Yes or No, no NaN).

Produces three analyses:
1. Missingness Uncertainty    — P(UTI=Yes | symptom="No") per symptom
2. Diagnostic Power vs        — scatter plot: documentation freq vs diagnostic power
   Documentation Frequency
3. Feature Importance         — which symptom disagreements predict LLM UTI error

Usage:
    python3 symptom_feature_analysis.py
    python3 symptom_feature_analysis.py --llm-file data/output/llm_phenotyping_gpt-5_summary.csv
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for background runs
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from config.settings import DEFAULT_INPUT_CSV, OUTPUT_DIR

ADJ_CSV = DEFAULT_INPUT_CSV                 # default; override with --input
OUT_DIR = OUTPUT_DIR / "analysis"

# ---------------------------------------------------------------------------
# Symptom column mapping
# adjudication ground truth col  →  LLM result col
# ---------------------------------------------------------------------------
SYMPTOM_MAP = {
    "Ability to Perceive Symptoms": {
        "gt":  "Ability to Perceive Symptoms_ground_truth",
        "llm": "Ability to Perceive Symptoms_LLM",
    },
    "Dysuria": {
        "gt":  "Dysuria_ground_truth",
        "llm": "Dysuria_LLM",
    },
    "Subjective Fever": {
        "gt":  "Subjective Fever_ground_truth",
        "llm": "Subjective Fever_LLM",
    },
    "Urinary Urgency": {
        "gt":  "Urinary Urgency_ground_truth",
        "llm": "Urinary Urgency_LLM",
    },
    "Urinary Frequency": {
        "gt":  "Urinary Frequency_ground_truth",
        "llm": "Urinary Frequency_LLM",
    },
    "Suprapubic Pain": {
        "gt":  "Suprapubic Pain/Tenderness_ground_truth",
        "llm": "Suprapubic Pain/Tenderness_LLM",
    },
    "Flank/CVA Pain": {
        "gt":  "Flank (CVA) Pain/Tenderness_ground_truth",
        "llm": "Flank (CVA) Pain/Tenderness_LLM",
    },
    "Perineal Pain": {
        "gt":  "Perineal Pain/Painful Prostate Exam_ground_truth",
        "llm": "Perineal Pain/Painful Prostate Exam_LLM",
    },
    "Urinary Incontinence": {
        "gt":  "Urinary Incontinence_ground_truth",
        "llm": "Urinary Incontinence_LLM",
    },
    "Macroscopic Hematuria": {
        "gt":  "Macroscopic Hematuria_ground_truth",
        "llm": "Macroscopic Hematuria_LLM",
    },
}


# ---------------------------------------------------------------------------
# Data loading & joining
# ---------------------------------------------------------------------------

def load_data(llm_csv: Path, adj_csv: Path = ADJ_CSV) -> pd.DataFrame:
    df_adj = pd.read_csv(adj_csv, encoding="utf-8-sig")
    df_llm = pd.read_csv(llm_csv)

    if "UTI?_ground_truth" not in df_adj.columns:
        raise SystemExit(
            f"ERROR: no 'UTI?_ground_truth' column in {adj_csv}.\n"
            "symptom_feature_analysis.py requires ground-truth labels to run."
        )

    # Join keys
    df_adj["mrn_str"]  = df_adj["patient_MRN"].astype(str).str.strip()
    df_llm["mrn_str"]  = df_llm["patient_MRN"].astype(str).str.strip()

    df_adj["note_dt"] = pd.to_datetime(
        df_adj["Note Date/Time (Collins)"].fillna(df_adj["Note Date/Time (Lee)"]),
        errors="coerce",
    ).dt.floor("min")
    df_llm["note_dt"] = pd.to_datetime(df_llm["note_dt"], errors="coerce").dt.floor("min")

    # Merge — bring ground truth symptom cols from adjudication into LLM results
    gt_symptom_cols = [m["gt"] for m in SYMPTOM_MAP.values()]
    df = df_llm.merge(
        df_adj[["mrn_str", "note_dt", "UTI?_ground_truth"] + gt_symptom_cols],
        on=["mrn_str", "note_dt"],
        how="inner",
        suffixes=("_llm_file", "_adj"),
    )

    # Resolve UTI ground truth — prefer adjudication column
    df["uti_gt"] = df["UTI?_ground_truth"].fillna(df.get("ground_truth_uti", np.nan))

    # Keep only definitive UTI cases
    df = df[df["uti_gt"].isin(["Yes", "No"])].copy()
    df["uti_gt_binary"] = (df["uti_gt"] == "Yes").astype(int)

    print(f"Definitive cases: {len(df)}  (Yes={df['uti_gt_binary'].sum()}, No={(df['uti_gt_binary']==0).sum()})")
    return df


# ---------------------------------------------------------------------------
# Analysis 1 — Missingness Uncertainty
# P(UTI=Yes | symptom="No")  with 95% Wilson CI
# ---------------------------------------------------------------------------

def wilson_ci(k, n, z=1.96):
    """Wilson score confidence interval for a proportion."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0, centre - margin), min(1, centre + margin)


def missingness_uncertainty(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symptom, cols in SYMPTOM_MAP.items():
        gt_col = cols["gt"]
        if gt_col not in df.columns:
            continue
        missing_mask = df[gt_col].fillna("No") == "No"
        sub = df[missing_mask]
        n = len(sub)
        k = sub["uti_gt_binary"].sum()
        lo, hi = wilson_ci(k, n)
        rows.append({
            "symptom": symptom,
            "n_missing": n,
            "n_uti_yes_when_missing": k,
            "p_uti_given_missing": round(k / n, 3) if n > 0 else np.nan,
            "ci_low": round(lo, 3),
            "ci_high": round(hi, 3),
        })
    return pd.DataFrame(rows).sort_values("p_uti_given_missing", ascending=False)


# ---------------------------------------------------------------------------
# Analysis 2 — Diagnostic Power vs Documentation Frequency
# Uses ground truth symptom labels as the reference
# ---------------------------------------------------------------------------

def diagnostic_power_vs_frequency(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symptom, cols in SYMPTOM_MAP.items():
        gt_col = cols["gt"]
        if gt_col not in df.columns:
            continue
        vals = df[gt_col].fillna("No")

        # Documentation frequency: % of cases where symptom is explicitly Yes or Negation
        documented = vals.isin(["Yes", "Negation"])
        doc_freq = documented.mean()

        # Diagnostic power: P(UTI=Yes | symptom="Yes") — sensitivity proxy
        present = vals == "Yes"
        n_present = present.sum()
        p_uti_given_present = (
            df.loc[present, "uti_gt_binary"].mean() if n_present > 0 else np.nan
        )

        # Also compute presence rate among UTI=Yes cases (feature prevalence)
        uti_yes = df["uti_gt_binary"] == 1
        p_present_given_uti = (
            (df.loc[uti_yes, gt_col].fillna("No") == "Yes").mean()
            if uti_yes.sum() > 0 else np.nan
        )

        rows.append({
            "symptom": symptom,
            "doc_frequency": round(doc_freq, 3),
            "n_documented": int(documented.sum()),
            "n_present": int(n_present),
            "p_uti_given_present": round(p_uti_given_present, 3) if not np.isnan(p_uti_given_present) else np.nan,
            "p_present_given_uti": round(p_present_given_uti, 3) if not np.isnan(p_present_given_uti) else np.nan,
        })
    return pd.DataFrame(rows).sort_values("p_uti_given_present", ascending=False)


# ---------------------------------------------------------------------------
# Analysis 3 — Feature Importance: which symptom mismatches predict LLM error
# ---------------------------------------------------------------------------

def symptom_mismatch_importance(df: pd.DataFrame) -> pd.DataFrame:
    # LLM UTI error flag
    df = df.copy()
    df["llm_uti"] = df["UTI?_LLM"].fillna("Unclear")
    df["llm_uti_binary"] = (df["llm_uti"] == "Yes").astype(int)
    df["uti_error"] = (df["llm_uti_binary"] != df["uti_gt_binary"]).astype(int)

    print(f"\nLLM UTI accuracy: {1 - df['uti_error'].mean():.3f}  "
          f"({df['uti_error'].sum()} errors / {len(df)} cases)")

    # Per-symptom mismatch flag (LLM label ≠ ground truth label)
    feature_cols = []
    for symptom, cols in SYMPTOM_MAP.items():
        gt_col  = cols["gt"]
        llm_col = cols["llm"]
        if gt_col not in df.columns or llm_col not in df.columns:
            continue
        mismatch_col = f"mismatch_{symptom}"
        df[mismatch_col] = (
            df[gt_col].fillna("No").str.strip() != df[llm_col].fillna("No").str.strip()
        ).astype(int)
        feature_cols.append((symptom, mismatch_col))

    # Summary table: mismatch rate + association with UTI error
    rows = []
    for symptom, col in feature_cols:
        mismatch_rate = df[col].mean()
        # Point-biserial correlation with UTI error
        if df[col].std() > 0:
            corr, pval = stats.pointbiserialr(df[col], df["uti_error"])
        else:
            corr, pval = 0.0, 1.0
        # P(UTI error | symptom mismatch)
        sub_mismatch = df[df[col] == 1]
        p_error_given_mismatch = sub_mismatch["uti_error"].mean() if len(sub_mismatch) > 0 else np.nan
        rows.append({
            "symptom": symptom,
            "mismatch_rate": round(mismatch_rate, 3),
            "n_mismatches": int(df[col].sum()),
            "p_uti_error_given_mismatch": round(p_error_given_mismatch, 3) if not np.isnan(p_error_given_mismatch) else np.nan,
            "correlation_with_uti_error": round(corr, 3),
            "p_value": round(pval, 3),
        })

    return pd.DataFrame(rows).sort_values("correlation_with_uti_error", ascending=False), df


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_missingness_uncertainty(df_miss: pd.DataFrame, out_dir: Path, model: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    y = range(len(df_miss))
    ax.barh(y, df_miss["p_uti_given_missing"], color="steelblue", alpha=0.7)
    ax.errorbar(
        df_miss["p_uti_given_missing"], y,
        xerr=[
            df_miss["p_uti_given_missing"] - df_miss["ci_low"],
            df_miss["ci_high"] - df_miss["p_uti_given_missing"],
        ],
        fmt="none", color="black", capsize=4,
    )
    ax.axvline(0.5, color="red", linestyle="--", alpha=0.5, label="50% baseline")
    ax.set_yticks(list(y))
    ax.set_yticklabels(df_miss["symptom"])
    ax.set_xlabel("P(UTI = Yes | symptom not documented)")
    ax.set_title(f"Uncertainty of Missingness — {model}\n"
                 "How often is UTI = Yes even when this symptom is absent from the note?")
    ax.legend()
    plt.tight_layout()
    path = out_dir / f"missingness_uncertainty_{model}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


def plot_diagnostic_vs_frequency(df_diag: pd.DataFrame, out_dir: Path, model: str):
    fig, ax = plt.subplots(figsize=(10, 8))

    x = df_diag["doc_frequency"]
    y = df_diag["p_uti_given_present"].fillna(0)
    labels = df_diag["symptom"]

    # Quadrant lines at medians
    x_mid = x.median()
    y_mid = y.median()
    ax.axvline(x_mid, color="gray", linestyle="--", alpha=0.4)
    ax.axhline(y_mid, color="gray", linestyle="--", alpha=0.4)

    ax.scatter(x, y, s=100, color="steelblue", zorder=5)
    for xi, yi, label in zip(x, y, labels):
        ax.annotate(label, (xi, yi), textcoords="offset points",
                    xytext=(6, 4), fontsize=8)

    # Quadrant labels
    ax.text(0.02, 0.97, "Rare but\ndiagnostic", transform=ax.transAxes,
            va="top", fontsize=8, color="darkgreen", alpha=0.7)
    ax.text(0.75, 0.97, "Common &\ndiagnostic", transform=ax.transAxes,
            va="top", fontsize=8, color="navy", alpha=0.7)
    ax.text(0.02, 0.05, "Rare &\nweak signal", transform=ax.transAxes,
            va="bottom", fontsize=8, color="gray", alpha=0.7)
    ax.text(0.75, 0.05, "Common but\nweak signal", transform=ax.transAxes,
            va="bottom", fontsize=8, color="darkorange", alpha=0.7)

    ax.set_xlabel("Documentation Frequency (% of cases explicitly mentioned)")
    ax.set_ylabel("Diagnostic Power — P(UTI=Yes | symptom present)")
    ax.set_title(f"Diagnostic Power vs Documentation Frequency — {model}")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    plt.tight_layout()
    path = out_dir / f"diagnostic_vs_frequency_{model}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


def plot_mismatch_importance(df_imp: pd.DataFrame, out_dir: Path, model: str):
    df_plot = df_imp.sort_values("correlation_with_uti_error")
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["salmon" if c > 0 else "steelblue" for c in df_plot["correlation_with_uti_error"]]
    ax.barh(range(len(df_plot)), df_plot["correlation_with_uti_error"], color=colors, alpha=0.8)
    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot["symptom"])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Correlation with UTI label error (point-biserial r)")
    ax.set_title(f"Symptom Mismatch → UTI Error Importance — {model}\n"
                 "Positive = symptom disagreement associated with LLM getting UTI wrong")
    # Mark significant (p < 0.1) with *
    for i, (_, row) in enumerate(df_plot.iterrows()):
        if row["p_value"] < 0.1:
            ax.text(row["correlation_with_uti_error"] + 0.01, i, "*", va="center", fontsize=12)
    plt.tight_layout()
    path = out_dir / f"mismatch_importance_{model}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(llm_csv: Path, adj_csv: Path = ADJ_CSV):
    model = llm_csv.stem.replace("llm_phenotyping_", "").replace("_summary", "")
    out_dir = OUT_DIR / model
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Model: {model}")
    print(f"{'='*60}")

    df = load_data(llm_csv, adj_csv)

    # Analysis 1
    print("\n--- Missingness Uncertainty ---")
    df_miss = missingness_uncertainty(df)
    print(df_miss.to_string(index=False))
    df_miss.to_csv(out_dir / "missingness_uncertainty.csv", index=False)
    plot_missingness_uncertainty(df_miss, out_dir, model)

    # Analysis 2
    print("\n--- Diagnostic Power vs Documentation Frequency ---")
    df_diag = diagnostic_power_vs_frequency(df)
    print(df_diag.to_string(index=False))
    df_diag.to_csv(out_dir / "diagnostic_vs_frequency.csv", index=False)
    plot_diagnostic_vs_frequency(df_diag, out_dir, model)

    # Analysis 3
    print("\n--- Symptom Mismatch Feature Importance ---")
    df_imp, df_with_errors = symptom_mismatch_importance(df)
    print(df_imp.to_string(index=False))
    df_imp.to_csv(out_dir / "mismatch_importance.csv", index=False)
    plot_mismatch_importance(df_imp, out_dir, model)

    print(f"\nAll outputs saved to: {out_dir}")
    return df_miss, df_diag, df_imp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Symptom feature analysis (requires ground-truth labels)")
    parser.add_argument("--model", default=None,
                        help="Model name; resolves to data/output/llm_phenotyping_<model>_summary.csv")
    parser.add_argument("--llm-file", default=None,
                        help="Explicit path to an LLM summary CSV (overrides --model)")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_CSV,
                        help=f"Adjudication sheet (default: {DEFAULT_INPUT_CSV})")
    args = parser.parse_args()

    if args.llm_file:
        llm_file = Path(args.llm_file)
    else:
        model = args.model or "gemini-2.5-pro"
        llm_file = OUTPUT_DIR / f"llm_phenotyping_{model.replace('.', '_')}_summary.csv"

    if not llm_file.exists():
        raise SystemExit(f"ERROR: summary not found: {llm_file}\nRun ./run_phenotyping.py first.")
    if not args.input.exists():
        raise SystemExit(f"ERROR: adjudication sheet not found: {args.input}\n"
                         "Pass --input <path> (needed for ground-truth labels).")
    run(llm_file, args.input)
