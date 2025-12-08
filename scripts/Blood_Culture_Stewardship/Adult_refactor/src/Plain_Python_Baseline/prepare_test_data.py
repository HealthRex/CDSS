#!/usr/bin/env python3
"""
Data Preparation Script for Fabre-Labeled ED Notes

Pipeline:
1) Load human Fabre labels from CSV
2) Aggregate to encounter level (MRN + NoteDateTime)
3) Build MRN list
4) Query BigQuery to:
   - map MRNs to anon_id via starr_map
   - pull ED Provider Notes (physician only)
   - join with adult enriched cohort within ±24h of blood culture
   - compute unjittered timestamps in BigQuery
5) Bring into Pandas and merge with human Fabre labels on (MRN, NoteDateTime)
6) Construct EHR dictionary column from EHR summary features
7) Save final dataset to disk
"""

import os
import argparse

import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables (GOOGLE_APPLICATION_CREDENTIALS, etc.)
load_dotenv()


def load_human_labels(labels_csv_path: str) -> pd.DataFrame:
    """
    Load human Fabre labels from CSV and aggregate to encounter level.

    Returns:
        human_Fabre_labels_encounter_level (pd.DataFrame)
        with columns: MRN, NoteDateTime, Final_Label, Final_Result, BloodCultureOrderDateTime
    """
    print(f"📄 Loading human Fabre labels from: {labels_csv_path}")
    human_Fabre_labels = pd.read_csv(labels_csv_path)
    human_Fabre_labels["Final_Label"] = human_Fabre_labels["Risk"].apply(lambda x: 1 if x in ("High Risk", "Intermediate Risk") else 0)
    human_Fabre_labels["Final_Result"] = human_Fabre_labels["Result"].apply(lambda x: 1 if x in ("Positive") else 0)
    print(f"✅ Loaded human labels: {human_Fabre_labels.shape}")

    # Ensure NoteDateTime is parsed to datetime
    if "NoteDateTime" in human_Fabre_labels.columns:
        human_Fabre_labels["NoteDateTime"] = pd.to_datetime(
            human_Fabre_labels["NoteDateTime"]
        )
    else:
        raise ValueError("Column 'NoteDateTime' not found in human_Fabre_labels CSV")

    # Aggregate to encounter-level labels
    print("📊 Aggregating human labels to encounter level...")
    human_Fabre_labels_encounter_level = (
        human_Fabre_labels
        .groupby(["MRN", "NoteDateTime"])[["Final_Label", "Final_Result", "BloodCultureOrderDateTime"]]
        .max()
        .reset_index()
    )
    print(f"✅ Aggregated human labels: {human_Fabre_labels_encounter_level.shape}")

    return human_Fabre_labels_encounter_level


def load_bigquery_data(human_Fabre_labels_encounter_level: pd.DataFrame) -> pd.DataFrame:
    """
    Run BigQuery pipeline using MRNs from human_Fabre_labels_encounter_level:
    - Filter starr_map by MRN
    - Join to notes + cohort
    - Unjitter timestamps in BigQuery

    Returns:
        valid_notes (pd.DataFrame) with unjittered timestamps and all cohort features.
    """
    print("🔄 Initializing BigQuery client...")
    client = bigquery.Client()

    # Build MRN list from human_Fabre_labels_encounter_level
    print("🧮 Preparing MRN list for BigQuery query...")
    mrn_series = human_Fabre_labels_encounter_level["MRN"].dropna()
    mrn_series = mrn_series.astype(int)
    mrn_list = sorted(mrn_series.unique())
    print(f"✅ Unique MRNs: {len(mrn_list)}")

    if len(mrn_list) == 0:
        raise ValueError("MRN list is empty. Check your human_Fabre_labels_encounter_level input.")

    mrn_list_str = ",".join(str(x) for x in mrn_list)

    # BigQuery query using demo → note → merged CTEs
    print("📡 Running BigQuery query for cohort + notes + jitter handling...")
    query = f"""
    WITH demo AS (
      SELECT *
      FROM `som-nero-phi-jonc101-secure.starr_map.shc_map_2024-11-17` AS c
      WHERE CAST(c.mrn AS INT64) IN ({mrn_list_str})
    ),
    note AS (
      SELECT
        note.*,
        demo.mrn,
        demo.jitter
      FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` AS note
      JOIN `som-nero-phi-jonc101.shc_core_2024.prov_map` AS m
        ON m.shc_prov_id = CAST(SUBSTR(note.author_prov_map_id, 2) AS STRING)
      JOIN demo
        ON demo.anon_id = note.anon_id
      WHERE note.note_type_desc = 'ED Provider Notes'
        AND m.prov_type = 'PHYSICIAN'
    ),
    merged AS (
      SELECT
        c.*,
        n.jittered_note_date AS notedatetime_not_utc,
        n.jittered_note_date_utc AS notedatetime,
        n.mrn,
        n.jitter,
        n.deid_note_text
      FROM `som-nero-phi-jonc101.blood_culture_stewardship_sandy_2024.enriched_label_filtered_adult_only_analysis_cohort_all_features` AS c
      JOIN note AS n
        ON c.anon_id = n.anon_id
      WHERE TIMESTAMP_DIFF(
              n.jittered_note_date_utc,
              TIMESTAMP(c.blood_culture_order_datetime_utc),
              HOUR
            ) BETWEEN -24 AND 24
    )
    SELECT
      m.*,
      TIMESTAMP_SUB(
        TIMESTAMP_SUB(m.blood_culture_order_datetime_utc, INTERVAL m.jitter DAY),
        INTERVAL 8 HOUR
      ) AS unjittered_blood_culture_order_datetime_utc,
      TIMESTAMP_SUB(m.notedatetime_not_utc, INTERVAL m.jitter DAY) AS unjittered_notedatetime
    FROM merged AS m
    """

    valid_notes = client.query(query).to_dataframe()
    print(f"✅ BigQuery result (valid_notes): {valid_notes.shape}")

    # Basic type cleaning before merge
    print("🧹 Cleaning dtypes for MRN and datetime columns...")
    valid_notes["mrn"] = valid_notes["mrn"].astype(int)

    valid_notes["unjittered_notedatetime"] = pd.to_datetime(
        valid_notes["unjittered_notedatetime"]
    )
    valid_notes["unjittered_blood_culture_order_datetime_utc"] = pd.to_datetime(
        valid_notes["unjittered_blood_culture_order_datetime_utc"]
    )

    return valid_notes


def merge_with_human_labels(
    valid_notes: pd.DataFrame,
    human_Fabre_labels_encounter_level: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge BigQuery results with human Fabre labels on (MRN, NoteDateTime),
    and construct the EHR dictionary column.

    Returns:
        merged_df: final dataframe ready for downstream tasks.
    """
    print("⏱ Ensuring NoteDateTime in labels is datetime...")
    human_Fabre_labels_encounter_level["NoteDateTime"] = pd.to_datetime(
        human_Fabre_labels_encounter_level["NoteDateTime"]
    )

    print("🔗 Merging valid_notes with human Fabre labels on (MRN, NoteDateTime)...")
    merged_df = valid_notes.merge(
        human_Fabre_labels_encounter_level,
        left_on=["mrn", "unjittered_notedatetime"],
        right_on=["MRN", "NoteDateTime"],
        how="inner",   # keep only notes with human labels
    )
    print(f"✅ After merge: {merged_df.shape}")

    # Canonical label column (customize as needed)
    if "Final_Label" in merged_df.columns:
        merged_df["Label"] = merged_df["Final_Label"]

    # -----------------------------
    # EHR dictionary construction
    # -----------------------------
    print("🧬 Identifying EHR feature columns...")
    ehr_cols = [
        col
        for col in merged_df.columns
        if (
            ("min" in col or "max" in col or "avg" in col or "median" in col)
            and "missing_flag" not in col
        )
    ]
    print(f"✅ Found {len(ehr_cols)} EHR columns")

    def create_ehr_dict(row):
        return {col: row[col] for col in ehr_cols if pd.notna(row[col])}

    print("📦 Constructing EHR dictionary column...")
    merged_df["EHR"] = merged_df[ehr_cols].apply(create_ehr_dict, axis=1)

    # Drop any *missing_flag columns globally
    print("🧽 Dropping 'missing_flag' columns...")
    merged_df = merged_df.loc[:, ~merged_df.columns.str.contains("missing_flag")]
    print(f"✅ Final merged_df shape after EHR + cleanup: {merged_df.shape}")

    return merged_df


def save_prepared_data(df: pd.DataFrame, data_dir: str, filename: str = "Fabre_labeled_ED_notes_with_EHR.csv") -> str:
    """
    Save prepared dataframe to CSV.

    Args:
        df: final dataframe
        data_dir: directory to save
        filename: output file name

    Returns:
        full_path: path to saved CSV
    """
    os.makedirs(data_dir, exist_ok=True)
    full_path = os.path.join(data_dir, filename)
    df.to_csv(full_path, index=False)
    print(f"💾 Saved final dataset to: {full_path}")
    print(f"📊 Shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    return full_path


def prepare_data_complete(labels_csv_path: str, data_dir: str) -> str:
    """
    Full pipeline:
      1) Load + aggregate human labels
      2) Run BigQuery query with MRN filter and unjittering
      3) Merge on (MRN, NoteDateTime)
      4) Build EHR dict column
      5) Save CSV

    Returns:
        path to saved CSV
    """
    print("🚀 Starting complete data preparation pipeline (Fabre-labeled ED notes + EHR)...")

    human_Fabre_labels_encounter_level = load_human_labels(labels_csv_path)
    valid_notes = load_bigquery_data(human_Fabre_labels_encounter_level)
    final_df = merge_with_human_labels(valid_notes, human_Fabre_labels_encounter_level)

    out_path = save_prepared_data(final_df, data_dir)
    print("🎉 Data preparation complete.")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Fabre-labeled ED note dataset for downstream pipeline")

    parser.add_argument(
        "--labels-csv",
        default="/Users/sandychen/Downloads/Combined_Final.csv",
        help="Path to human Fabre labels CSV (Combined_Final.csv)",
    )
    parser.add_argument(
        "--data-dir",
        default="/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data",
        help="Directory to save prepared dataset",
    )

    args = parser.parse_args()

    try:
        prepare_data_complete(args.labels_csv, args.data_dir)
    except Exception as e:
        print(f"❌ Error during data preparation: {e}")
        raise
