"""
Evaluation module for LLM UTI Phenotyping.

Loads the adjudication CSV (schema only, no PHI logging), runs the phenotyper on
note texts supplied by the user, then computes agreement metrics between LLM
labels and physician ground truth.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

import pandas as pd
from sklearn.metrics import cohen_kappa_score, classification_report, confusion_matrix


# ---------------------------------------------------------------------------
# Column name mappings (CSV column names → internal snake_case keys)
# ---------------------------------------------------------------------------

SYMPTOM_GT_COLUMNS = {
    "ability_to_perceive_symptoms": "Ability to Perceive Symptoms_ground_truth",
    "dysuria": "Dysuria_ground_truth",
    "subjective_fever": "Subjective Fever_ground_truth",
    "urinary_urgency": "Urinary Urgency_ground_truth",
    "urinary_frequency": "Urinary Frequency_ground_truth",
    "suprapubic_pain_tenderness": "Suprapubic Pain/Tenderness_ground_truth",
    "flank_cva_pain_tenderness": "Flank (CVA) Pain/Tenderness_ground_truth",
    "perineal_pain_painful_prostate_exam": "Perineal Pain/Painful Prostate Exam_ground_truth",
    "urinary_incontinence": "Urinary Incontinence_ground_truth",
    "macroscopic_hematuria": "Macroscopic Hematuria_ground_truth",
}

ASSESSMENT_GT_COLUMNS = {
    "uti": "UTI?_ground_truth",
    "any_infection_present": "Is any infection present?_ground_truth",
    "presumed_infection_plausible": "Presumed Infection Plausible?_ground_truth",
    "prophylactic_antibiotics_appropriate": "Prophylactic Antibiotics Appropriate?_ground_truth",
}

ALL_GT_COLUMNS = {**SYMPTOM_GT_COLUMNS, **ASSESSMENT_GT_COLUMNS}


# ---------------------------------------------------------------------------
# CSV schema reader
# ---------------------------------------------------------------------------

def load_adjudication_schema(csv_path: str | Path) -> list[str]:
    """Returns only the column names from the adjudication CSV (no row data)."""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        return next(reader)


def load_adjudication_csv(csv_path: str | Path) -> pd.DataFrame:
    """Load the full adjudication CSV into a DataFrame."""
    return pd.read_csv(csv_path, encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# Results builder
# ---------------------------------------------------------------------------

def build_results_dataframe(
    df_adjudication: pd.DataFrame,
    llm_results: list,          # list of UTIPhenotypeResult
    note_col: str = "note_text",  # column in df_adjudication that holds the note text
) -> pd.DataFrame:
    """
    Merge ground truth labels with LLM predictions.

    Args:
        df_adjudication: DataFrame loaded from the adjudication CSV. Must contain
                         a 'note_text' column (or whatever note_col is set to) with
                         the clinical note text passed to the phenotyper.
        llm_results:     List of UTIPhenotypeResult objects, one per row.
        note_col:        Column name for the note text.

    Returns:
        DataFrame with ground truth columns + LLM prediction columns side by side.
    """
    assert len(df_adjudication) == len(llm_results), (
        f"Mismatch: {len(df_adjudication)} rows in adjudication CSV "
        f"but {len(llm_results)} LLM results."
    )

    rows = []
    for i, (_, adj_row) in enumerate(df_adjudication.iterrows()):
        llm = llm_results[i]
        row = {}

        # Ground truth labels
        for key, col in ALL_GT_COLUMNS.items():
            row[f"{key}_ground_truth"] = adj_row.get(col, None)

        # LLM predictions
        for key in SYMPTOM_GT_COLUMNS:
            sym = getattr(llm, key, None)
            row[f"{key}_llm"] = sym.label if sym else None
            row[f"{key}_llm_support"] = sym.support if sym else None

        for key in ASSESSMENT_GT_COLUMNS:
            asmt = getattr(llm, key, None)
            row[f"{key}_llm"] = asmt.label if asmt else None
            row[f"{key}_llm_reasoning"] = asmt.reasoning if asmt else None

        row["model_name"] = llm.model_name
        row["parse_error"] = llm.parse_error
        rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(results_df: pd.DataFrame) -> dict:
    """
    Compute per-field agreement metrics between LLM and ground truth.

    Returns a dict keyed by field name with:
        - accuracy
        - cohen_kappa
        - classification_report (str)
        - n_valid  (rows where both ground truth and LLM label are non-null)
    """
    metrics = {}

    for key in ALL_GT_COLUMNS:
        gt_col = f"{key}_ground_truth"
        llm_col = f"{key}_llm"

        if gt_col not in results_df.columns or llm_col not in results_df.columns:
            continue

        sub = results_df[[gt_col, llm_col]].dropna()
        if len(sub) == 0:
            metrics[key] = {"error": "No valid rows"}
            continue

        y_true = sub[gt_col].astype(str).str.strip()
        y_pred = sub[llm_col].astype(str).str.strip()

        try:
            kappa = cohen_kappa_score(y_true, y_pred)
        except Exception:
            kappa = None

        n_correct = (y_true == y_pred).sum()
        accuracy = n_correct / len(y_true)

        metrics[key] = {
            "n_valid": len(y_true),
            "accuracy": round(accuracy, 4),
            "cohen_kappa": round(kappa, 4) if kappa is not None else None,
            "classification_report": classification_report(y_true, y_pred, zero_division=0),
        }

    return metrics


def print_metrics_summary(metrics: dict) -> None:
    """Pretty-print a summary of evaluation metrics."""
    print(f"{'Field':<45} {'N':>5} {'Accuracy':>9} {'Kappa':>8}")
    print("-" * 72)
    for field_name, m in metrics.items():
        if "error" in m:
            print(f"{field_name:<45} {'—':>5} {'error':>9}")
            continue
        kappa_str = f"{m['cohen_kappa']:.3f}" if m["cohen_kappa"] is not None else "N/A"
        print(f"{field_name:<45} {m['n_valid']:>5} {m['accuracy']:>9.3f} {kappa_str:>8}")


def save_results(
    results_df: pd.DataFrame,
    metrics: dict,
    output_dir: str | Path = "data/output",
    prefix: str = "llm_phenotyping",
) -> None:
    """Save results DataFrame and metrics JSON to disk."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / f"{prefix}_results.csv"
    metrics_path = output_dir / f"{prefix}_metrics.json"

    results_df.to_csv(results_path, index=False)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Results saved to: {results_path}")
    print(f"Metrics saved to: {metrics_path}")


# ---------------------------------------------------------------------------
# Inter-rater agreement helper (physician vs physician, for reference)
# ---------------------------------------------------------------------------

def physician_agreement(df: pd.DataFrame) -> dict:
    """
    Compute P1 vs P2 inter-rater agreement for all symptoms and assessments.
    Useful as an upper-bound reference for LLM performance.
    """
    from .uti_phenotyper import SYMPTOM_DEFINITIONS, FINAL_ASSESSMENT_DEFINITIONS

    p1_p2_pairs = {
        "ability_to_perceive_symptoms": (
            "Ability to Perceive Symptoms_P1 (Collins)",
            "Ability to Perceive Symptoms_P2 (Lee)",
        ),
        "dysuria": ("Dysuria_P1 (Collins)", "Dysuria_P2 (Lee)"),
        "subjective_fever": ("Subjective Fever_P1 (Collins)", "Subjective Fever_P2 (Lee)"),
        "urinary_urgency": ("Urinary Urgency_P1 (Collins)", "Urinary Urgency_P2 (Lee)"),
        "urinary_frequency": ("Urinary Frequency_P1 (Collins)", "Urinary Frequency_P2 (Lee)"),
        "suprapubic_pain_tenderness": (
            "Suprapubic Pain/Tenderness_P1 (Collins)",
            "Suprapubic Pain/Tenderness_P2 (Lee)",
        ),
        "flank_cva_pain_tenderness": (
            "Flank (CVA) Pain/Tenderness_P1 (Collins)",
            "Flank (CVA) Pain/Tenderness_P2 (Lee)",
        ),
        "perineal_pain_painful_prostate_exam": (
            "Perineal Pain/Painful Prostate Exam_P1 (Collins)",
            "Perineal Pain/Painful Prostate Exam_P2 (Lee)",
        ),
        "urinary_incontinence": ("Urinary Incontinence_P1 (Collins)", "Urinary Incontinence_P2 (Lee)"),
        "macroscopic_hematuria": ("Macroscopic Hematuria_P1 (Collins)", "Macroscopic Hematuria_P2 (Lee)"),
        "uti": ("UTI?_P1 (Collins)", "UTI?_P2 (Lee)"),
        "any_infection_present": (
            "Is any infection present?_P1 (Collins)",
            "Is any infection present?_P2 (Lee)",
        ),
        "presumed_infection_plausible": (
            "Presumed Infection Plausible?_P1 (Collins)",
            "Presumed Infection Plausible?_P2 (Lee)",
        ),
        "prophylactic_antibiotics_appropriate": (
            "Prophylactic Antibiotics Appropriate?_P1 (Collins)",
            "Prophylactic Antibiotics Appropriate?_P2 (Lee)",
        ),
    }

    metrics = {}
    for key, (col1, col2) in p1_p2_pairs.items():
        if col1 not in df.columns or col2 not in df.columns:
            continue
        sub = df[[col1, col2]].dropna()
        if len(sub) == 0:
            continue
        y1 = sub[col1].astype(str).str.strip()
        y2 = sub[col2].astype(str).str.strip()
        try:
            kappa = cohen_kappa_score(y1, y2)
        except Exception:
            kappa = None
        accuracy = (y1 == y2).sum() / len(y1)
        metrics[key] = {
            "n_valid": len(y1),
            "accuracy": round(accuracy, 4),
            "cohen_kappa": round(kappa, 4) if kappa is not None else None,
        }
    return metrics
