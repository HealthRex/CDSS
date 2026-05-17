"""
ARMD Pipeline Configuration

Central configuration for the ARMD (Antibiotic Resistance Microbiology Dataset) pipeline.

The pipeline now supports multiple yearly data refreshes. Each run produces a
self-contained dataset named ARMD_<year> (e.g. ARMD_2024, ARMD_2025) built from
the matching STARR source dataset shc_core_<year>.

How parameterization works
--------------------------
The SQL files in sql/ keep two "default" literal strings so each file remains
independently runnable in the BigQuery console:

    som-nero-phi-jonc101.shc_core_2023            ← source dataset
    som-nero-phi-jonc101.antimicrobial_stewardship ← destination dataset

At pipeline runtime, run_pipeline.py substitutes those literals with the
year-specific values resolved here.

Update REFERENCE_STATS after each refresh so the test suite stays meaningful.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Project and dataset defaults
# ---------------------------------------------------------------------------

BQ_PROJECT = "som-nero-phi-jonc101"

# Default year used when --year is not passed. Bump this when shc_core_<year>
# becomes the most recent refresh.
DEFAULT_YEAR = 2025

# Year-agnostic literal strings that appear in every sql/*.sql file.
# run_pipeline.py replaces these at runtime with the year-specific values.
SOURCE_PLACEHOLDER_DATASET = "shc_core_2023"
DEST_PLACEHOLDER_DATASET = "antimicrobial_stewardship"

# Reference data that does NOT change with the source year. Left untouched
# during substitution.
REFERENCE_DATASETS = ("mapdata",)


def source_dataset(year: int) -> str:
    """Resolve the STARR source dataset for a given year (shc_core_<year>)."""
    return f"shc_core_{year}"


def dest_dataset(year: int) -> str:
    """Resolve the destination dataset for a given year (ARMD_<year>)."""
    return f"ARMD_{year}"


def fully_qualified_source(year: int) -> str:
    return f"{BQ_PROJECT}.{source_dataset(year)}"


def fully_qualified_dest(year: int) -> str:
    return f"{BQ_PROJECT}.{dest_dataset(year)}"


# ---------------------------------------------------------------------------
# Backwards-compatible aliases (used by old scripts / tests still importing
# DEST_DATASET, SOURCE_DATASET as module-level strings). They resolve to the
# DEFAULT_YEAR. Prefer the helper functions above in new code.
# ---------------------------------------------------------------------------

BQ_DATASET = dest_dataset(DEFAULT_YEAR)
BQ_SOURCE_DATASET = source_dataset(DEFAULT_YEAR)
DEST_DATASET = fully_qualified_dest(DEFAULT_YEAR)
SOURCE_DATASET = fully_qualified_source(DEFAULT_YEAR)


# ---------------------------------------------------------------------------
# Output tables (relative to the destination dataset for the chosen year)
# ---------------------------------------------------------------------------

def tables_for_year(year: int) -> dict[str, str]:
    """Return a dict mapping logical table key -> fully qualified table id."""
    dest = fully_qualified_dest(year)
    return {
        "cohort": f"{dest}.microbiology_cultures_cohort",
        "demographics": f"{dest}.microbiology_cultures_demographics",
        "ward_info": f"{dest}.microbiology_cultures_ward_info",
        "labs": f"{dest}.microbiology_Labs",
        "vitals": f"{dest}.microbiology_Vitals",
        "abx_lookup": f"{dest}.class_subtype_lookup",
        "prior_medications": f"{dest}.microbiology_cultures_medication_exposure",
        "abx_class_exposure": f"{dest}.microbiology_cultures_antibiotic_class_exposure",
        "abx_subtype_exposure": f"{dest}.microbiology_cultures_antibiotic_subtype_exposure",
        "microbial_resistance": f"{dest}.microbiology_microbial_resistance_augmented",
        "prior_infecting_organism": f"{dest}.microbiology_culture_prior_infecting_organism_augmented",
        "comorbidities": f"{dest}.microbiology_comorbidity_augmented",
        "prior_procedures": f"{dest}.microbiology_cultures_priorprocedures_augmented",
        "adi_scores": f"{dest}.microbiology_cultures_adi_scores",
        "adi_scores_imputed": f"{dest}.microbiology_cultures_adi_scores_imputed",
        "nursing_home_visits": f"{dest}.microbiology_cultures_nursing_home_visits_augmented",
        "implied_susceptibility": f"{dest}.microbiology_implied_susceptibility",
        # Reference tables loaded from CSV at the start of each run
        "temp_antibiotics": f"{dest}.temp_antibiotics",
        "prior_antibiotics_list": f"{dest}.prior_antibiotics_list",
        "cpt_icd10pcs_mapping": f"{dest}.CPT_ICD10PCS_mapping",
    }


# Backwards-compatible mapping for code that imports TABLES directly.
TABLES = tables_for_year(DEFAULT_YEAR)


# ---------------------------------------------------------------------------
# Reference CSVs uploaded as the first pipeline step
# ---------------------------------------------------------------------------

# Mapping: BigQuery table name (in destination dataset) -> CSV file name.
# Files are expected at the project root one level above ARMD_pipeline/
# (i.e. HealthRex CDSS master scripts-antibiotic-susceptibility_Aim 1a/).
REFERENCE_CSVS = {
    "temp_antibiotics": "temp_antibiotics.csv",
    "prior_antibiotics_list": "prior_antibiotics_list.csv",
    "CPT_ICD10PCS_mapping": "CPT_ICD10PCS_mapping.csv",
}


# ---------------------------------------------------------------------------
# SQL execution order
# ---------------------------------------------------------------------------

SQL_EXECUTION_ORDER = [
    "01_cohort.sql",
    "02_demographics.sql",
    "03_ward_info.sql",
    "04_labs.sql",
    "05_vitals.sql",
    "06_abx_class_subtype_lookup.sql",
    "07_prior_medications.sql",
    "08_antibiotic_class_exposure.sql",
    "09_antibiotic_subtype_exposure.sql",
    "10_microbial_resistance.sql",
    "11_prior_infecting_organism.sql",
    "12_comorbidities.sql",
    "13_prior_procedures.sql",
    "14_adi_scores.sql",
    "15_nursing_home_visits.sql",
    "16_implied_susceptibility.sql",
    "17_cleanup_temp_tables.sql",
]


# Linking keys used across all tables
LINKING_KEYS = ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded"]


# ---------------------------------------------------------------------------
# CSV export file names (match the published Dryad release)
# ---------------------------------------------------------------------------

CSV_EXPORT_NAMES = {
    "cohort": "microbiology_cultures_cohort.csv",
    "demographics": "microbiology_cultures_demographics.csv",
    "ward_info": "microbiology_cultures_ward_info.csv",
    "labs": "microbiology_cultures_labs.csv",
    "vitals": "microbiology_cultures_vitals.csv",
    "prior_medications": "microbiology_cultures_prior_med.csv",
    "abx_class_exposure": "microbiology_cultures_antibiotic_class_exposure.csv",
    "abx_subtype_exposure": "microbiology_cultures_antibiotic_subtype_exposure.csv",
    "microbial_resistance": "microbiology_cultures_microbial_resistance.csv",
    "prior_infecting_organism": "microbiology_culture_prior_infecting_organism.csv",
    "comorbidities": "microbiology_cultures_comorbidity.csv",
    "prior_procedures": "microbiology_cultures_priorprocedures.csv",
    "adi_scores": "microbiology_cultures_adi_scores.csv",
    "nursing_home_visits": "microbiology_cultures_nursing_home_visits.csv",
    "implied_susceptibility": "microbiology_cultures_implied_susceptibility.csv",
}


# ---------------------------------------------------------------------------
# Known reference values from the published ARMD paper (used for validation)
# Update after each refresh.
# ---------------------------------------------------------------------------

REFERENCE_STATS = {
    "total_culture_records": 751_075,
    "unique_patients": 283_715,
    "culture_type_pct": {
        "URINE": 50.0,
        "BLOOD": 38.8,
        "RESPIRATORY": 11.3,
    },
    "avg_age": 56.7,
    "min_age": 18,
    "sex_distribution": {
        "female_pct": 66.9,
        "male_pct": 33.0,
        "unknown_pct": 0.03,
    },
    "num_antibiotics": 55,
    "susceptibility_categories": [
        "Susceptible", "Resistant", "Intermediate", "Inconclusive", "Synergism"
    ],
    "culture_types": ["URINE", "BLOOD", "RESPIRATORY"],
    "data_start_year": 1999,
    "data_end_year": 2024,
    # Tolerance widened during the first 2024/2025 builds to absorb growth.
    "row_count_tolerance_pct": 30,
}
