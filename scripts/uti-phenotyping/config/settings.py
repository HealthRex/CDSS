"""
BigQuery configuration settings for UTI Phenotyping data mapping.
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
QUERIES_DIR = PROJECT_ROOT / "queries"

# Default file locations (every script accepts --input to override these)
DEFAULT_INPUT_CSV = INPUT_DIR / "adjudication.csv"
DEFAULT_CURATED_CSV = OUTPUT_DIR / "curated_dataset.csv"

# BigQuery settings
BQ_PROJECT = "som-nero-phi-jonc101"
BQ_PROJECT_SECURE = "som-nero-phi-jonc101-secure"
BQ_DATASET_CORE = "shc_core_2024"
BQ_DATASET_UTI = "uti_prediction"

# Table references
TABLES = {
    # MRN to anon_id mapping (secure project)
    "mrn_map": f"{BQ_PROJECT_SECURE}.starr_map.shc_map_2025-07-17",
    
    # UTI prediction tables
    "uti_cohort": f"{BQ_PROJECT}.{BQ_DATASET_UTI}.cohort",
    "uti_notes": f"{BQ_PROJECT}.{BQ_DATASET_UTI}.notes",
    
    # Core clinical tables
    "lab_result": f"{BQ_PROJECT}.{BQ_DATASET_CORE}.lab_result",
    "demographic": f"{BQ_PROJECT}.{BQ_DATASET_CORE}.demographic",
    "order_proc": f"{BQ_PROJECT}.{BQ_DATASET_CORE}.order_proc",
}

# CSV column names (from your input file)
CSV_COLUMNS = {
    "mrn": "patient_MRN",
    "order_time": "Urine Culture_Order Date & Time(taken time)",
    "note_time": "Note Date/Time (Collins)",  # or "Note Date/Time (Lee)"
}

# Time tolerance for matching (in seconds) - for datetime comparison
TIME_MATCH_TOLERANCE_SECONDS = 60
