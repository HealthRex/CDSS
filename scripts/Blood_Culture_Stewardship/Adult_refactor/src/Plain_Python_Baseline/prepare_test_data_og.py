# #!/usr/bin/env python3
# """
# Data Preparation Script
# Complete pipeline to prepare Test_set_df_note from BigQuery data
# """

# import pandas as pd
# import os
# from datetime import datetime
# import sys
# from google.cloud import bigquery
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# def load_bigquery_data(EHR_IncludeInprompt=False):
#     """
#     Load data from BigQuery and prepare Test_set_df_note
    
#     Returns:
#         pd.DataFrame: Prepared Test_set_df_note with Label column
#     """
#     print("🔄 Initializing BigQuery client...")
#     client = bigquery.Client()
    
#     # Query 1: Load cohort data
#     print("📊 Loading cohort data...")
#     # cohort_query = "select * from `som-nero-phi-jonc101.blood_culture_stewardship.cohort` where order_year>=2023"
#     cohort_query = "select * from `som-nero-phi-jonc101.blood_culture_stewardship_sandy_2024.final_base_features_imputed_test`"
#     Test_set_df = client.query(cohort_query).to_dataframe()
#     print(f"✅ Loaded cohort data: {Test_set_df.shape}")
    
#     # Query 2: Load notes data
#     print("📝 Loading notes data...")
#     # notes_query = "select * from `som-nero-phi-jonc101.blood_culture_stewardship.EDProviderNotes`"
#     # notes_query = "SELECT distinct * FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` where note_type_desc = 'ED Provider Notes' limit 100"
#     notes_query = """
#     WITH cohort AS (
#             SELECT * FROM `som-nero-phi-jonc101.blood_culture_stewardship_sandy_2024.final_base_features_imputed_test`
#         ),
#         note as(SELECT note.*, FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` note INNER JOIN `som-nero-phi-jonc101.shc_core_2024.prov_map` m  ON m.shc_prov_id = CAST(SUBSTR(note.author_prov_map_id, 2) AS STRING) WHERE note.note_type_desc like 'ED Provider Notes' AND m.prov_type in ('PHYSICIAN') )
#         select cohort.anon_id,
#         cohort.pat_enc_csn_id_coded,
#         cohort.order_proc_id_coded,
#         note.jittered_note_date_utc as notedatetime,
#         note.deid_note_text,
#         note.note_type,
#         note.note_type_desc,
#         from cohort 
#         inner join note using(anon_id)
#         WHERE TIMESTAMP_DIFF(
#         note.jittered_note_date_utc,
#         TIMESTAMP(cohort.blood_culture_order_datetime_utc),
#         HOUR
#         ) BETWEEN -24 AND 24
#         """
#     Notes_df = client.query(notes_query).to_dataframe()
#     print(f"✅ Loaded notes data: {Notes_df.shape}")
    
#     # Merge data
#     print("🔗 Merging cohort and notes data...")
#     Test_set_df_note = pd.merge(
#         Test_set_df, 
#         Notes_df, 
#         how='inner', 
#         on=['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded']
#     )
#     print(f"✅ Merged data: {Test_set_df_note.shape}")
    
#     # Filter out null notes
#     print("🧹 Filtering out null notes...")
#     Test_set_df_note = Test_set_df_note[Test_set_df_note.deid_note_text.notnull()]
#     print(f"✅ After filtering nulls: {Test_set_df_note.shape}")
    
#     # Remove duplicates
#     print("🔍 Removing duplicates...")
#     Test_set_df_note.drop_duplicates(
#         subset=[
#             'anon_id', 
#             'pat_enc_csn_id_coded', 
#             'order_proc_id_coded',
#             'blood_culture_order_datetime_utc',
#             'notedatetime',
#             'deid_note_text'
#         ], 
#         inplace=True
#     )
#     print(f"✅ After removing duplicates: {Test_set_df_note.shape}")
    
#     print("⏰ Processing datetime columns...")
#     Test_set_df_note['blood_culture_order_datetime_utc'] = pd.to_datetime(
#         Test_set_df_note['blood_culture_order_datetime_utc'], utc=True
#     )
#     Test_set_df_note['notedatetime'] = pd.to_datetime(
#         Test_set_df_note['notedatetime'], utc=True
#     )
#     print(f"✅ Converted datetime columns (timezone-aligned to UTC)")

    
#     # Calculate time difference in hours
#     print("📏 Calculating time differences...")
#     Test_set_df_note['time-diff'] = (
#         Test_set_df_note['blood_culture_order_datetime_utc'] - Test_set_df_note['notedatetime']
#     ).dt.total_seconds() / 3600
#     Test_set_df_note['time-diff'] = Test_set_df_note['time-diff'].astype(int)
#     print(f"✅ Calculated time differences")
    
#     # Filter to keep only notes within 24 hours before blood culture order
#     print("🔍 Filtering notes within 24 hours before blood culture order...")
#     before_filter = Test_set_df_note.shape[0]
#     Test_set_df_note = Test_set_df_note[Test_set_df_note['time-diff'] >= -24]
#     after_filter = Test_set_df_note.shape[0]
#     print(f"✅ Filtered from {before_filter} to {after_filter} records ({before_filter - after_filter} removed)")
    
#     # Sort by time difference and keep only the closest note per patient/encounter/order
#     print("📋 Keeping only the closest note per patient/encounter/order...")
#     before_dedup = Test_set_df_note.shape[0]
#     Test_set_df_note = Test_set_df_note.sort_values('time-diff').drop_duplicates(
#         subset=['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'blood_culture_order_datetime_utc'], 
#         keep='first'
#     )
#     after_dedup = Test_set_df_note.shape[0]
#     print(f"✅ Deduplicated from {before_dedup} to {after_dedup} records ({before_dedup - after_dedup} removed)")
    
#     # Create Label column
#     print("🏷️ Creating Label column...")
#     Test_set_df_note['Label'] = (
#         Test_set_df_note['positive_blood_culture']
#     )
    
#     # Summary
#     label_counts = Test_set_df_note['Label'].value_counts()
#     print(f"✅ Label distribution:")
#     print(f"   False (Negative): {label_counts.get(0,0)}")
#     print(f"   True (Positive): {label_counts.get(1,0)}")
    
#     print(f"✅ Final dataset ready: {Test_set_df_note.shape}")
#     print(f"✅ Columns: {list(Test_set_df_note.columns)}")

#     print(f"✅ Extracting EHR columns")
#     EHR_columns = [col for col in Test_set_df_note.columns.values if 'min' in col and "missing_flag" not in col]
#     EHR_columns.extend([col for col in Test_set_df_note.columns.values if 'max' in col and "missing_flag" not in col])
#     EHR_columns.extend([col for col in Test_set_df_note.columns.values if 'avg' in col and "missing_flag" not in col])
#     EHR_columns.extend([col for col in Test_set_df_note.columns.values if 'median' in col and "missing_flag" not in col])
    
#     # Create EHR dictionary with only non-NaN values for each row
#     def create_ehr_dict(row):
#         return {col: row[col] for col in EHR_columns if pd.notna(row[col])}
    
#     Test_set_df_note['EHR'] = Test_set_df_note.apply(create_ehr_dict, axis=1)
#     print("🧽 Removing columns with 'missing_flag' in their names...")
#     Test_set_df_note = Test_set_df_note.loc[:, ~Test_set_df_note.columns.str.contains("missing_flag")]
#     print(f"✅ After dropping 'missing_flag' columns: {Test_set_df_note.shape}")


    
#     return Test_set_df_note

# def save_prepared_data(test_set_df_note, data_dir):
#     """
#     Save the prepared Test_set_df_note to the data directory
    
#     Args:
#         test_set_df_note: The prepared DataFrame
#         data_dir: Directory to save the backup
    
#     Returns:
#         str: standard_backup filename
#     """
#     # Create the directory if it doesn't exist
#     os.makedirs(data_dir, exist_ok=True)
#     print(f"✅ Data directory ready: {data_dir}")
    
#     # Save as standard backup name for easy reference
#     standard_backup = os.path.join(data_dir, 'Test_set_df_note_ORIGINAL_new.csv')
#     test_set_df_note.to_csv(standard_backup, index=False)
#     print(f"✅ Saved as: {standard_backup}")
    
#     print(f"📊 Final data shape: {test_set_df_note.shape}")
#     print(f"📋 Final columns: {list(test_set_df_note.columns)}")
#     print("\n🎉 Your prepared data is now saved in the data folder!")
    
#     return standard_backup

# def prepare_data_complete(data_dir):
#     """
#     Complete data preparation pipeline: load from BigQuery and save
    
#     Args:
#         data_dir: Directory to save the prepared data
        
#     Returns:
#         str: standard_backup filename
#     """
#     print("🚀 Starting complete data preparation pipeline...")
    
#     # Load and prepare data from BigQuery
#     test_set_df_note = load_bigquery_data()
    
#     # Save prepared data
#     standard_backup = save_prepared_data(test_set_df_note, data_dir)
    
#     print("✅ Data preparation complete!")
#     return standard_backup

# def prepare_data(test_set_df_note, data_dir):
#     """
#     Legacy function: Save already prepared Test_set_df_note
    
#     Args:
#         test_set_df_note: The prepared DataFrame
#         data_dir: Directory to save the backup
#     """
#     return save_prepared_data(test_set_df_note, data_dir)

# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser(description='Prepare data for LLM classification')

#     parser.add_argument('--data-dir', 
#                        default=f'/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data',
#                        help='Data directory path')
    
#     args = parser.parse_args()
    
#     try:
#         prepare_data_complete(args.data_dir)
#     except Exception as e:
#         print(f"❌ Error during data preparation: {e}")
#         raise
#!/usr/bin/env python3
"""
Data Preparation Script (Clean Version)
Complete pipeline to prepare Test_set_df_note from BigQuery data
- Single cohort query
- Notes filtered within ±24 h inside BigQuery
- One merge in Pandas
- No redundant missing_flag filtering
"""

import pandas as pd
import os
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables (e.g., GOOGLE_APPLICATION_CREDENTIALS)
load_dotenv()

def load_bigquery_data():
    """
    Load and prepare the Test_set_df_note DataFrame.
    Returns:
        pd.DataFrame: prepared Test_set_df_note with Label and EHR columns
    """
    print("🔄 Initializing BigQuery client...")
    client = bigquery.Client()

    # -----------------------------
    # 1️⃣ Load cohort table
    # -----------------------------
    print("📊 Loading cohort data...")
    cohort_query = """
        SELECT *
        FROM `som-nero-phi-jonc101.blood_culture_stewardship_sandy_2024.final_base_features_imputed_test`
    """
    cohort_df = client.query(cohort_query).to_dataframe()
    print(f"✅ Loaded cohort: {cohort_df.shape}")

    # -----------------------------
    # 2️⃣ Load notes filtered within ±24 h in BigQuery
    # -----------------------------
    print("📝 Loading and filtering notes (±24 h) directly from BigQuery...")
    notes_query = """
        WITH note AS (
            SELECT note.*
            FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` AS note
            JOIN `som-nero-phi-jonc101.shc_core_2024.prov_map` AS m
              ON m.shc_prov_id = CAST(SUBSTR(note.author_prov_map_id, 2) AS STRING)
            WHERE note.note_type_desc = 'ED Provider Notes'
              AND m.prov_type = 'PHYSICIAN'
        )
        SELECT
            c.anon_id,
            c.pat_enc_csn_id_coded,
            c.order_proc_id_coded,
            n.jittered_note_date_utc AS notedatetime,
            n.deid_note_text,
            n.note_type,
            n.note_type_desc
        FROM `som-nero-phi-jonc101.blood_culture_stewardship_sandy_2024.final_base_features_imputed_test` AS c
        JOIN note AS n
          ON c.anon_id = n.anon_id
        WHERE TIMESTAMP_DIFF(n.jittered_note_date_utc,
                             TIMESTAMP(c.blood_culture_order_datetime_utc),
                             HOUR)
              BETWEEN -24 AND 24
    """
    notes_df = client.query(notes_query).to_dataframe()
    print(f"✅ Loaded filtered notes: {notes_df.shape}")

    # -----------------------------
    # 3️⃣ Merge cohort + notes once
    # -----------------------------
    print("🔗 Merging cohort and notes...")
    merged = pd.merge(
        cohort_df,
        notes_df,
        how="inner",
        on=["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]
    )
    print(f"✅ Merged: {merged.shape}")

    # -----------------------------
    # 4️⃣ Clean and process
    # -----------------------------
    print("🧹 Filtering null notes and duplicates...")
    merged = merged[merged["deid_note_text"].notnull()]
    merged = merged.drop_duplicates(
        subset=[
            "anon_id",
            "pat_enc_csn_id_coded",
            "order_proc_id_coded",
            "blood_culture_order_datetime_utc",
            "notedatetime",
            "deid_note_text",
        ]
    )

    # Datetime alignment
    print("⏰ Converting datetime columns to UTC...")
    merged["blood_culture_order_datetime_utc"] = pd.to_datetime(
        merged["blood_culture_order_datetime_utc"], utc=True
    )
    merged["notedatetime"] = pd.to_datetime(merged["notedatetime"], utc=True)

    # Compute time difference (hours)
    merged["time-diff"] = (
        merged["blood_culture_order_datetime_utc"] - merged["notedatetime"]
    ).dt.total_seconds() / 3600
    merged["time-diff"] = merged["time-diff"].astype(int)

    # Keep the closest note (smallest absolute time difference)
    print("📋 Keeping the closest note per order...")
    merged = (
        merged.sort_values("time-diff")
        .drop_duplicates(
            subset=[
                "anon_id",
                "pat_enc_csn_id_coded",
                "order_proc_id_coded",
                "blood_culture_order_datetime_utc",
            ],
            keep="first",
        )
    )
    print(f"✅ After deduplication: {merged.shape}")

    # -----------------------------
    # 5️⃣ Label & EHR columns
    # -----------------------------
    print("🏷️ Creating Label column...")
    merged["Label"] = merged["positive_blood_culture"]

    print("✅ Extracting EHR columns...")
    ehr_cols = [
        col
        for col in merged.columns
        if (
            ("min" in col or "max" in col or "avg" in col or "median" in col)
            and "missing_flag" not in col
        )
    ]

    # Construct per-row EHR dictionary (non-NaN values only)
    def create_ehr_dict(row):
        return {col: row[col] for col in ehr_cols if pd.notna(row[col])}

    merged["EHR"] = merged.apply(create_ehr_dict, axis=1)

    # Drop any remaining "missing_flag" columns globally
    print("🧽 Removing columns with 'missing_flag' in their names...")
    merged = merged.loc[:, ~merged.columns.str.contains("missing_flag")]
    print(f"✅ Final shape: {merged.shape}")

    return merged


def save_prepared_data(df, data_dir):
    """Save prepared data to CSV."""
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "Test_set_df_note_ORIGINAL_new.csv")
    df.to_csv(out_path, index=False)
    print(f"✅ Saved to: {out_path}")
    print(f"📊 Shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    print("\n🎉 Data preparation complete!")
    return out_path


def prepare_data_complete(data_dir):
    """Run full preparation pipeline."""
    print("🚀 Starting data preparation pipeline...")
    df = load_bigquery_data()
    save_prepared_data(df, data_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare data for LLM classification")
    parser.add_argument(
        "--data-dir",
        default="/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data",
        help="Directory to save prepared data",
    )
    args = parser.parse_args()

    try:
        prepare_data_complete(args.data_dir)
    except Exception as e:
        print(f"❌ Error during data preparation: {e}")
        raise
