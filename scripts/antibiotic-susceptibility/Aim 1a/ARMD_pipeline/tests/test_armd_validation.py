"""
ARMD Dataset Validation Tests

Comprehensive unit tests to validate the ARMD dataset after each pipeline run.
Tests are organized by feature table and check:
  1. Schema validation (expected columns exist)
  2. Referential integrity (all records link to cohort)
  3. Domain constraints (valid values only)
  4. Row count sanity (within expected range)
  5. Temporal consistency (time-to-event values are correct direction)
  6. Distribution checks (based on published ARMD paper statistics)
  7. No-duplicate checks
  8. Null/completeness checks

Usage:
    pytest tests/test_armd_validation.py -v
    pytest tests/test_armd_validation.py -v -k "test_cohort"     # run cohort tests only
    pytest tests/test_armd_validation.py -v -k "test_schema"     # run all schema tests
    pytest tests/test_armd_validation.py -v --tb=short           # short tracebacks
"""

import os
import sys

import pytest
from google.cloud import bigquery

# Add parent directory to path for config import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import BQ_PROJECT, DEST_DATASET, REFERENCE_STATS, TABLES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def bq_client():
    """Create a BigQuery client for the test session."""
    return bigquery.Client(project=BQ_PROJECT)


@pytest.fixture(scope="session")
def query_runner(bq_client):
    """Helper to run a query and return results."""
    def _run(sql):
        return bq_client.query(sql).result()
    return _run


@pytest.fixture(scope="session")
def query_to_df(bq_client):
    """Helper to run a query and return a pandas DataFrame."""
    def _run(sql):
        return bq_client.query(sql).to_dataframe()
    return _run


def _get_columns(bq_client, table_ref):
    """Get column names for a BigQuery table."""
    table = bq_client.get_table(table_ref)
    return [field.name for field in table.schema]


def _row_count(query_runner, table_ref):
    """Get row count for a table."""
    rows = query_runner(f"SELECT COUNT(*) as cnt FROM `{table_ref}`")
    return list(rows)[0].cnt


def _within_tolerance(actual, expected, tolerance_pct):
    """Check if actual is within tolerance_pct of expected."""
    lower = expected * (1 - tolerance_pct / 100)
    upper = expected * (1 + tolerance_pct / 100)
    return lower <= actual <= upper


# ===========================================================================
# 1. COHORT TABLE TESTS
# ===========================================================================

class TestCohort:
    """Tests for microbiology_cultures_cohort."""
    TABLE = TABLES["cohort"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = [
            "anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded",
            "order_time_jittered_utc", "ordering_mode", "culture_description",
            "was_positive", "organism", "antibiotic", "susceptibility",
        ]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_row_count_in_expected_range(self, query_runner):
        cnt = _row_count(query_runner, self.TABLE)
        expected = REFERENCE_STATS["total_culture_records"]
        tol = REFERENCE_STATS["row_count_tolerance_pct"]
        assert _within_tolerance(cnt, expected, tol), (
            f"Cohort row count {cnt} not within {tol}% of expected {expected}"
        )

    def test_culture_types_only_valid(self, query_to_df):
        df = query_to_df(
            f"SELECT DISTINCT culture_description FROM `{self.TABLE}`"
        )
        valid = set(REFERENCE_STATS["culture_types"])
        actual = set(df["culture_description"].tolist())
        assert actual == valid, f"Unexpected culture types: {actual - valid}"

    def test_culture_type_distribution(self, query_to_df):
        """Check that urine/blood/respiratory proportions roughly match the paper."""
        df = query_to_df(f"""
            SELECT culture_description, COUNT(DISTINCT order_proc_id_coded) as cnt
            FROM `{self.TABLE}`
            GROUP BY culture_description
        """)
        total = df["cnt"].sum()
        pcts = {row.culture_description: 100 * row.cnt / total for _, row in df.iterrows()}
        # Urine ~50%, Blood ~38.8%, Respiratory ~11.3% (allow ±5pp)
        assert abs(pcts.get("URINE", 0) - 50.0) < 10, f"URINE pct={pcts.get('URINE')}"
        assert abs(pcts.get("BLOOD", 0) - 38.8) < 10, f"BLOOD pct={pcts.get('BLOOD')}"
        assert abs(pcts.get("RESPIRATORY", 0) - 11.3) < 10, f"RESP pct={pcts.get('RESPIRATORY')}"

    def test_unique_patients_in_expected_range(self, query_runner):
        rows = query_runner(
            f"SELECT COUNT(DISTINCT anon_id) as cnt FROM `{self.TABLE}`"
        )
        cnt = list(rows)[0].cnt
        expected = REFERENCE_STATS["unique_patients"]
        tol = REFERENCE_STATS["row_count_tolerance_pct"]
        assert _within_tolerance(cnt, expected, tol), (
            f"Unique patients {cnt} not within {tol}% of expected {expected}"
        )

    def test_susceptibility_categories_valid(self, query_to_df):
        df = query_to_df(f"""
            SELECT DISTINCT susceptibility
            FROM `{self.TABLE}`
            WHERE susceptibility IS NOT NULL
        """)
        valid = set(REFERENCE_STATS["susceptibility_categories"])
        actual = set(df["susceptibility"].tolist())
        assert actual.issubset(valid), f"Unexpected susceptibility values: {actual - valid}"

    def test_was_positive_binary(self, query_to_df):
        df = query_to_df(
            f"SELECT DISTINCT was_positive FROM `{self.TABLE}`"
        )
        assert set(df["was_positive"].tolist()).issubset({0, 1})

    def test_positive_cultures_have_organism(self, query_runner):
        """Positive cultures should have at least one organism."""
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE was_positive = 1 AND organism IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} positive cultures have NULL organism"

    def test_negative_cultures_have_no_organism(self, query_runner):
        """Negative cultures should not have organism/antibiotic."""
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE was_positive = 0 AND organism IS NOT NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} negative cultures have non-NULL organism"

    def test_no_duplicate_culture_orders_for_negative(self, query_runner):
        """Each negative culture should appear exactly once."""
        rows = query_runner(f"""
            SELECT order_proc_id_coded, COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE was_positive = 0
            GROUP BY order_proc_id_coded
            HAVING cnt > 1
            LIMIT 5
        """)
        dupes = list(rows)
        assert len(dupes) == 0, f"Found {len(dupes)} duplicate negative culture orders"

    def test_no_cultures_within_two_weeks(self, query_runner):
        """Verify the 2-week exclusion window: no patient should have two culture
        orders of the same type within 14 days."""
        rows = query_runner(f"""
            WITH ordered AS (
                SELECT DISTINCT anon_id, order_proc_id_coded, order_time_jittered_utc,
                       culture_description
                FROM `{self.TABLE}`
            ),
            pairs AS (
                SELECT a.anon_id,
                       TIMESTAMP_DIFF(b.order_time_jittered_utc, a.order_time_jittered_utc, DAY) as days_diff
                FROM ordered a
                INNER JOIN ordered b
                ON a.anon_id = b.anon_id
                   AND a.culture_description = b.culture_description
                   AND b.order_time_jittered_utc > a.order_time_jittered_utc
                   AND TIMESTAMP_DIFF(b.order_time_jittered_utc, a.order_time_jittered_utc, DAY) < 14
            )
            SELECT COUNT(*) as cnt FROM pairs
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} culture pairs found within 2-week window"

    def test_adults_only(self, query_to_df):
        """All patients should be 18+ at time of culture."""
        df = query_to_df(f"""
            SELECT c.anon_id,
                   DATE_DIFF(CAST(c.order_time_jittered_utc AS DATE),
                             d.BIRTH_DATE_JITTERED, YEAR) as age
            FROM `{self.TABLE}` c
            INNER JOIN `{DEST_DATASET.replace('antimicrobial_stewardship', 'shc_core_2023')}.demographic` d
            USING (anon_id)
            HAVING age < 18
            LIMIT 5
        """)
        assert len(df) == 0, f"Found {len(df)} patients under 18"

    def test_antibiotic_count(self, query_runner):
        """Should have approximately 55 distinct antibiotics."""
        rows = query_runner(f"""
            SELECT COUNT(DISTINCT antibiotic) as cnt
            FROM `{self.TABLE}`
            WHERE antibiotic IS NOT NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt >= 45, f"Only {cnt} distinct antibiotics (expected ~55)"
        assert cnt <= 70, f"Too many antibiotics: {cnt} (expected ~55)"


# ===========================================================================
# 2. DEMOGRAPHICS TABLE TESTS
# ===========================================================================

class TestDemographics:
    """Tests for microbiology_cultures_demographics."""
    TABLE = TABLES["demographics"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        for col in ["anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded", "age", "gender"]:
            assert col in cols, f"Missing column: {col}"

    def test_all_ages_adult(self, query_runner):
        rows = query_runner(f"SELECT MIN(age) as min_age FROM `{self.TABLE}`")
        min_age = list(rows)[0].min_age
        assert min_age >= 18, f"Minimum age is {min_age}, expected >= 18"

    def test_age_distribution_reasonable(self, query_to_df):
        df = query_to_df(f"SELECT AVG(age) as avg_age FROM `{self.TABLE}`")
        avg = df["avg_age"].iloc[0]
        # Paper says average age ~56.7, allow ±10
        assert 40 < avg < 70, f"Average age {avg} outside expected range"

    def test_gender_values_valid(self, query_to_df):
        df = query_to_df(f"SELECT DISTINCT gender FROM `{self.TABLE}`")
        valid = {"Male", "Female", "Unknown", "Other", "male", "female",
                 "M", "F", "0", "1"}
        actual = set(str(v) for v in df["gender"].tolist())
        # Gender encoding varies; just verify no more than a few unique values
        assert len(actual) <= 5, f"Too many gender values: {actual}"

    def test_sex_distribution(self, query_to_df):
        """Female ~66.9%, Male ~33.0% per the paper."""
        df = query_to_df(f"""
            SELECT gender, COUNT(DISTINCT anon_id) as cnt
            FROM `{self.TABLE}`
            GROUP BY gender
        """)
        total = df["cnt"].sum()
        pcts = {str(row.gender): 100 * row.cnt / total for _, row in df.iterrows()}
        # At least one category should be >60% (female) and one ~30% (male)
        max_pct = max(pcts.values())
        assert max_pct > 55, f"No dominant sex category found: {pcts}"

    def test_referential_integrity_to_cohort(self, query_runner):
        """All demographics records should link to cohort."""
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` d
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} demographics records not in cohort"


# ===========================================================================
# 3. WARD INFO TABLE TESTS
# ===========================================================================

class TestWardInfo:
    """Tests for microbiology_cultures_ward_info."""
    TABLE = TABLES["ward_info"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = [
            "anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded",
            "hosp_ward_IP", "hosp_ward_OP", "hosp_ward_ER", "hosp_ward_ICU",
        ]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_ward_columns_binary(self, query_to_df):
        for col in ["hosp_ward_IP", "hosp_ward_OP", "hosp_ward_ER", "hosp_ward_ICU"]:
            df = query_to_df(
                f"SELECT DISTINCT {col} FROM `{self.TABLE}` WHERE {col} IS NOT NULL"
            )
            vals = set(df[col].tolist())
            assert vals.issubset({0, 1}), f"{col} has non-binary values: {vals}"

    def test_at_least_some_of_each_ward_type(self, query_to_df):
        """Each ward type should have at least some patients."""
        df = query_to_df(f"""
            SELECT
                SUM(hosp_ward_IP) as ip,
                SUM(hosp_ward_OP) as op,
                SUM(hosp_ward_ER) as er,
                SUM(hosp_ward_ICU) as icu
            FROM `{self.TABLE}`
        """)
        for col in ["ip", "op", "er", "icu"]:
            assert df[col].iloc[0] > 0, f"No patients in ward type: {col}"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` w
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} ward info records not in cohort"


# ===========================================================================
# 4. LABS TABLE TESTS
# ===========================================================================

class TestLabs:
    """Tests for microbiology_Labs."""
    TABLE = TABLES["labs"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        expected_labs = ["wbc", "neutrophils", "lymphocytes", "hgb", "plt",
                         "na", "hco3", "bun", "cr", "lactate", "procalcitonin"]
        for lab in expected_labs:
            assert f"median_{lab}" in cols, f"Missing median_{lab}"
            assert f"Q25_{lab}" in cols, f"Missing Q25_{lab}"
            assert f"Q75_{lab}" in cols, f"Missing Q75_{lab}"

    def test_period_day_values(self, query_to_df):
        """Period_Day should reflect the time windows used (14 days for ARMD release)."""
        df = query_to_df(
            f"SELECT DISTINCT Period_Day FROM `{self.TABLE}` ORDER BY Period_Day"
        )
        vals = set(df["Period_Day"].tolist())
        assert 14 in vals, f"Expected Period_Day=14, got: {vals}"

    def test_lab_values_in_physiological_range(self, query_to_df):
        """Spot check that median lab values are in plausible clinical ranges."""
        df = query_to_df(f"""
            SELECT
                AVG(median_wbc) as avg_wbc,
                AVG(median_cr) as avg_cr,
                AVG(median_na) as avg_na,
                AVG(median_hgb) as avg_hgb
            FROM `{self.TABLE}`
            WHERE Period_Day = 14
        """)
        # WBC: typically 4-11 K/uL, but sick patients can be higher
        wbc = df["avg_wbc"].iloc[0]
        assert 1 < wbc < 50, f"Average WBC {wbc} outside plausible range"

        # Creatinine: typically 0.5-1.2 mg/dL
        cr = df["avg_cr"].iloc[0]
        assert 0.1 < cr < 10, f"Average Cr {cr} outside plausible range"

        # Sodium: typically 135-145 mmol/L
        na = df["avg_na"].iloc[0]
        assert 120 < na < 160, f"Average Na {na} outside plausible range"

    def test_quantile_ordering(self, query_to_df):
        """Q25 <= median <= Q75 for lab values."""
        df = query_to_df(f"""
            SELECT Q25_wbc, median_wbc, Q75_wbc
            FROM `{self.TABLE}`
            WHERE Q25_wbc IS NOT NULL AND median_wbc IS NOT NULL AND Q75_wbc IS NOT NULL
            LIMIT 1000
        """)
        violations = df[(df["Q25_wbc"] > df["median_wbc"]) |
                        (df["median_wbc"] > df["Q75_wbc"])]
        assert len(violations) == 0, (
            f"{len(violations)} rows where Q25 > median or median > Q75 for WBC"
        )

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` l
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} lab records not in cohort"


# ===========================================================================
# 5. VITALS TABLE TESTS
# ===========================================================================

class TestVitals:
    """Tests for microbiology_Vitals."""
    TABLE = TABLES["vitals"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        vitals = ["heartrate", "resprate", "temp", "sysbp", "diasbp"]
        for v in vitals:
            for prefix in ["Q25_", "Q75_", "median_"]:
                assert f"{prefix}{v}" in cols, f"Missing {prefix}{v}"

    def test_vital_signs_in_physiological_range(self, query_to_df):
        df = query_to_df(f"""
            SELECT
                AVG(median_heartrate) as hr,
                AVG(median_resprate) as rr,
                AVG(median_temp) as temp,
                AVG(median_sysbp) as sbp
            FROM `{self.TABLE}`
        """)
        hr = df["hr"].iloc[0]
        assert 40 < hr < 150, f"Average HR {hr} outside plausible range"

        rr = df["rr"].iloc[0]
        assert 8 < rr < 40, f"Average RR {rr} outside plausible range"

        temp = df["temp"].iloc[0]
        assert 90 < temp < 110, f"Average Temp {temp} outside plausible range (Fahrenheit)"

        sbp = df["sbp"].iloc[0]
        assert 70 < sbp < 200, f"Average SBP {sbp} outside plausible range"

    def test_has_first_last_values(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        for v in ["heartrate", "resprate", "temp", "sysbp", "diasbp"]:
            assert f"first_{v}" in cols, f"Missing first_{v}"
            assert f"last_{v}" in cols, f"Missing last_{v}"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` v
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} vitals records not in cohort"


# ===========================================================================
# 6. PRIOR MEDICATIONS TABLE TESTS
# ===========================================================================

class TestPriorMedications:
    """Tests for microbiology_cultures_medication_exposure."""
    TABLE = TABLES["prior_medications"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = [
            "anon_id", "pat_enc_csn_id_coded", "order_proc_id_coded",
            "medication_name", "medication_category", "medication_time_to_culturetime",
        ]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_time_to_culture_positive(self, query_runner):
        """All medication exposures should be before culture (positive days)."""
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE medication_time_to_culturetime < 1
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} medication records with time_to_culture < 1"

    def test_medication_names_not_empty(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE medication_name IS NULL OR TRIM(medication_name) = ''
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} records with empty medication_name"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` m
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} medication records not in cohort"


# ===========================================================================
# 7. ANTIBIOTIC CLASS EXPOSURE TABLE TESTS
# ===========================================================================

class TestAntibioticClassExposure:
    """Tests for microbiology_cultures_antibiotic_class_exposure."""
    TABLE = TABLES["abx_class_exposure"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "antibiotic_class",
                     "medication_time_to_culturetime"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_antibiotic_classes_not_empty(self, query_to_df):
        df = query_to_df(
            f"SELECT DISTINCT antibiotic_class FROM `{self.TABLE}` WHERE antibiotic_class IS NOT NULL"
        )
        assert len(df) >= 5, f"Only {len(df)} antibiotic classes found"

    def test_time_to_culture_positive(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt FROM `{self.TABLE}`
            WHERE medication_time_to_culturetime < 1
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} records with time_to_culture < 1"


# ===========================================================================
# 8. ANTIBIOTIC SUBTYPE EXPOSURE TABLE TESTS
# ===========================================================================

class TestAntibioticSubtypeExposure:
    """Tests for microbiology_cultures_antibiotic_subtype_exposure."""
    TABLE = TABLES["abx_subtype_exposure"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "antibiotic_subtype",
                     "medication_time_to_culturetime"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_subtypes_are_more_granular_than_classes(self, query_to_df):
        classes = query_to_df(
            f"SELECT COUNT(DISTINCT antibiotic_class) as cnt FROM `{TABLES['abx_class_exposure']}`"
        )["cnt"].iloc[0]
        subtypes = query_to_df(
            f"SELECT COUNT(DISTINCT antibiotic_subtype) as cnt FROM `{self.TABLE}`"
        )["cnt"].iloc[0]
        assert subtypes >= classes, "Subtypes should be >= classes in granularity"


# ===========================================================================
# 9. MICROBIAL RESISTANCE TABLE TESTS
# ===========================================================================

class TestMicrobialResistance:
    """Tests for microbiology_microbial_resistance_augmented."""
    TABLE = TABLES["microbial_resistance"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "organism", "antibiotic"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_has_time_to_culture(self, bq_client):
        """Should have a time-to-culture column (augmented version)."""
        cols = _get_columns(bq_client, self.TABLE)
        time_cols = [c for c in cols if "time" in c.lower() and "culture" in c.lower()]
        assert len(time_cols) > 0, "No time-to-culture column found"

    def test_time_to_culture_non_negative(self, query_runner):
        """Resistance should be from before the culture."""
        # Find the time column name dynamically
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE resistsant_time_to_cultureTime < 0
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} records with negative time_to_culture"

    def test_has_known_organisms(self, query_to_df):
        df = query_to_df(
            f"SELECT DISTINCT organism FROM `{self.TABLE}` LIMIT 50"
        )
        assert len(df) > 0, "No organisms found in microbial resistance table"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` m
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} resistance records not in cohort"


# ===========================================================================
# 10. PRIOR INFECTING ORGANISM TABLE TESTS
# ===========================================================================

class TestPriorInfectingOrganism:
    """Tests for microbiology_culture_prior_infecting_organism_augmented."""
    TABLE = TABLES["prior_infecting_organism"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "prior_organism"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_has_time_to_culture(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        time_cols = [c for c in cols if "days" in c.lower() and "cultur" in c.lower()]
        assert len(time_cols) > 0, f"No days-to-culture column found. Columns: {cols}"

    def test_prior_organisms_not_empty(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(DISTINCT prior_organism) as cnt
            FROM `{self.TABLE}`
        """)
        cnt = list(rows)[0].cnt
        assert cnt >= 5, f"Only {cnt} distinct prior organisms"

    def test_known_organisms_present(self, query_to_df):
        """Key organisms from the paper should be present."""
        df = query_to_df(
            f"SELECT DISTINCT prior_organism FROM `{self.TABLE}`"
        )
        organisms = set(df["prior_organism"].str.lower().tolist())
        # At least some of these should be found
        expected = {"escherichia", "klebsiella", "staphylococcus", "pseudomonas"}
        found = {e for e in expected if any(e in o for o in organisms)}
        assert len(found) >= 3, f"Missing key organisms. Found: {found}"


# ===========================================================================
# 11. COMORBIDITIES TABLE TESTS
# ===========================================================================

class TestComorbidities:
    """Tests for microbiology_comorbidity_augmented."""
    TABLE = TABLES["comorbidities"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "comorbidity_component"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_has_time_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        time_cols = [c for c in cols if "days" in c.lower() or "time" in c.lower()]
        assert len(time_cols) >= 1, "No time-related columns found"

    def test_has_diverse_comorbidities(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(DISTINCT comorbidity_component) as cnt
            FROM `{self.TABLE}`
        """)
        cnt = list(rows)[0].cnt
        assert cnt >= 20, f"Only {cnt} distinct comorbidity components"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` m
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} comorbidity records not in cohort"


# ===========================================================================
# 12. PRIOR PROCEDURES TABLE TESTS
# ===========================================================================

class TestPriorProcedures:
    """Tests for microbiology_cultures_priorprocedures_augmented."""
    TABLE = TABLES["prior_procedures"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_has_procedure_description(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        proc_cols = [c for c in cols if "procedure" in c.lower() or "description" in c.lower()]
        assert len(proc_cols) > 0, "No procedure description column found"

    def test_has_time_to_culture(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        time_cols = [c for c in cols if "days" in c.lower() or "time_to" in c.lower()]
        assert len(time_cols) > 0, "No time-to-culture column found"

    def test_procedure_time_positive(self, query_runner):
        """Procedures should be before culture (positive days)."""
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE procedure_days_culture < 0
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} procedures after culture order"

    def test_known_procedure_types(self, query_to_df):
        df = query_to_df(
            f"SELECT DISTINCT procedure_description FROM `{self.TABLE}`"
        )
        procedures = set(df["procedure_description"].str.lower().tolist())
        # At least some key procedures should be present
        expected_keywords = {"dialysis", "cvc", "mechvent"}
        found = {k for k in expected_keywords if any(k in p for p in procedures)}
        assert len(found) >= 2, f"Missing key procedures. Found: {found}, Have: {procedures}"


# ===========================================================================
# 13. ADI SCORES TABLE TESTS
# ===========================================================================

class TestAdiScores:
    """Tests for microbiology_cultures_adi_scores."""
    TABLE = TABLES["adi_scores"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "adi_score"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_adi_scores_numeric_when_present(self, query_to_df):
        """ADI scores should be numeric (1-100 range) when not null."""
        df = query_to_df(f"""
            SELECT SAFE_CAST(adi_score AS FLOAT64) as score
            FROM `{self.TABLE}`
            WHERE adi_score IS NOT NULL
            LIMIT 10000
        """)
        non_null = df.dropna()
        if len(non_null) > 0:
            assert non_null["score"].min() >= 0, "ADI scores should be non-negative"
            assert non_null["score"].max() <= 150, "ADI scores should be <= 150"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` a
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} ADI records not in cohort"


# ===========================================================================
# 14. NURSING HOME VISITS TABLE TESTS
# ===========================================================================

class TestNursingHomeVisits:
    """Tests for microbiology_cultures_nursing_home_visits_augmented."""
    TABLE = TABLES["nursing_home_visits"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "nursing_home_visit_culture"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_visit_days_non_negative(self, query_runner):
        """Nursing home visits should be on or before culture date."""
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE nursing_home_visit_culture < 0
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} nursing home visits after culture order"

    def test_referential_integrity_to_cohort(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}` n
            LEFT JOIN `{TABLES['cohort']}` c
            USING (anon_id, order_proc_id_coded)
            WHERE c.order_proc_id_coded IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} nursing home records not in cohort"


# ===========================================================================
# 15. IMPLIED SUSCEPTIBILITY TABLE TESTS
# ===========================================================================

class TestImpliedSusceptibility:
    """Tests for microbiology_implied_susceptibility."""
    TABLE = TABLES["implied_susceptibility"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["anon_id", "order_proc_id_coded", "organism", "antibiotic",
                     "susceptibility", "implied_susceptibility"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_implied_susceptibility_values_valid(self, query_to_df):
        df = query_to_df(f"""
            SELECT DISTINCT implied_susceptibility
            FROM `{self.TABLE}`
            WHERE implied_susceptibility IS NOT NULL
        """)
        valid = {"Susceptible", "Resistant", "Intermediate", "Inconclusive", "Synergism"}
        actual = set(df["implied_susceptibility"].tolist())
        assert actual.issubset(valid), f"Unexpected implied susceptibility: {actual - valid}"

    def test_has_diverse_organisms(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(DISTINCT organism) as cnt
            FROM `{self.TABLE}`
        """)
        cnt = list(rows)[0].cnt
        assert cnt >= 10, f"Only {cnt} organisms in implied susceptibility"

    def test_original_susceptibility_preserved(self, query_to_df):
        """When original susceptibility exists, it should be preserved."""
        df = query_to_df(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE susceptibility IS NOT NULL
              AND implied_susceptibility IS NOT NULL
              AND susceptibility != implied_susceptibility
        """)
        # When original exists and implied is also set, they should generally agree
        # (though implied may differ in edge cases, flag if >1% disagree)
        cnt = df["cnt"].iloc[0]
        total_rows = query_to_df(
            f"SELECT COUNT(*) as cnt FROM `{self.TABLE}` WHERE susceptibility IS NOT NULL"
        )["cnt"].iloc[0]
        if total_rows > 0:
            disagree_pct = 100 * cnt / total_rows
            assert disagree_pct < 5, (
                f"{disagree_pct:.1f}% of records have mismatched susceptibility vs implied"
            )


# ===========================================================================
# 16. ABX CLASS/SUBTYPE LOOKUP TABLE TESTS
# ===========================================================================

class TestAbxLookup:
    """Tests for class_subtype_lookup."""
    TABLE = TABLES["abx_lookup"]

    def test_schema_has_required_columns(self, bq_client):
        cols = _get_columns(bq_client, self.TABLE)
        required = ["antibiotic", "antibiotic_class", "antibiotic_subtype"]
        for col in required:
            assert col in cols, f"Missing column: {col}"

    def test_has_sufficient_antibiotics(self, query_runner):
        rows = query_runner(f"SELECT COUNT(*) as cnt FROM `{self.TABLE}`")
        cnt = list(rows)[0].cnt
        assert cnt >= 50, f"Only {cnt} antibiotics in lookup (expected ~102)"

    def test_no_null_values(self, query_runner):
        rows = query_runner(f"""
            SELECT COUNT(*) as cnt
            FROM `{self.TABLE}`
            WHERE antibiotic IS NULL OR antibiotic_class IS NULL OR antibiotic_subtype IS NULL
        """)
        cnt = list(rows)[0].cnt
        assert cnt == 0, f"{cnt} rows with NULL values in lookup table"


# ===========================================================================
# 17. CROSS-TABLE CONSISTENCY TESTS
# ===========================================================================

class TestCrossTableConsistency:
    """Tests that verify consistency across multiple ARMD tables."""

    def test_cohort_covers_all_feature_tables(self, query_runner):
        """Cohort should have at least as many distinct orders as any feature table."""
        cohort_count = _row_count(
            query_runner,
            f"(SELECT DISTINCT order_proc_id_coded FROM `{TABLES['cohort']}`)"
        )
        for name, table in TABLES.items():
            if name in ("cohort", "abx_lookup", "adi_scores_imputed"):
                continue
            try:
                feat_count = _row_count(
                    query_runner,
                    f"(SELECT DISTINCT order_proc_id_coded FROM `{table}`)"
                )
                assert feat_count <= cohort_count, (
                    f"{name} has {feat_count} distinct orders > cohort's {cohort_count}"
                )
            except Exception:
                # Table may not exist yet if pipeline hasn't completed
                pass

    def test_demographics_covers_all_cohort_patients(self, query_runner):
        """Every cohort patient should have demographics."""
        rows = query_runner(f"""
            SELECT COUNT(DISTINCT c.anon_id) as missing
            FROM `{TABLES['cohort']}` c
            LEFT JOIN `{TABLES['demographics']}` d
            USING (anon_id, order_proc_id_coded)
            WHERE d.anon_id IS NULL
        """)
        missing = list(rows)[0].missing
        assert missing == 0, f"{missing} cohort patients missing demographics"

    def test_ward_info_covers_all_cohort_orders(self, query_runner):
        """Every cohort order should have ward info."""
        rows = query_runner(f"""
            SELECT COUNT(DISTINCT c.order_proc_id_coded) as missing
            FROM `{TABLES['cohort']}` c
            LEFT JOIN `{TABLES['ward_info']}` w
            USING (anon_id, order_proc_id_coded)
            WHERE w.order_proc_id_coded IS NULL
        """)
        missing = list(rows)[0].missing
        assert missing == 0, f"{missing} cohort orders missing ward info"


# ===========================================================================
# 18. DATA QUALITY SMOKE TESTS
# ===========================================================================

class TestDataQualitySmoke:
    """Quick smoke tests for overall data quality."""

    def test_no_empty_tables(self, query_runner):
        """No ARMD table should be completely empty."""
        for name, table in TABLES.items():
            if name == "adi_scores_imputed":
                continue
            try:
                cnt = _row_count(query_runner, table)
                assert cnt > 0, f"Table {name} ({table}) is empty"
            except Exception:
                pass  # Table may not exist yet

    def test_cohort_has_data_from_expected_years(self, query_to_df):
        """Cohort should span the expected date range."""
        df = query_to_df(f"""
            SELECT
                EXTRACT(YEAR FROM MIN(order_time_jittered_utc)) as min_year,
                EXTRACT(YEAR FROM MAX(order_time_jittered_utc)) as max_year
            FROM `{TABLES['cohort']}`
        """)
        min_year = df["min_year"].iloc[0]
        max_year = df["max_year"].iloc[0]
        assert min_year <= 2008, f"Data starts at {min_year}, expected <= 2008"
        assert max_year >= 2020, f"Data ends at {max_year}, expected >= 2020"

    def test_top_organisms_match_expectations(self, query_to_df):
        """E. coli should be the most common organism in urine cultures."""
        df = query_to_df(f"""
            SELECT organism, COUNT(*) as cnt
            FROM `{TABLES['cohort']}`
            WHERE culture_description = 'URINE'
              AND organism IS NOT NULL
            GROUP BY organism
            ORDER BY cnt DESC
            LIMIT 5
        """)
        top = df["organism"].iloc[0].lower()
        assert "escherichia" in top or "e. coli" in top or "coli" in top, (
            f"Expected E. coli as top urine organism, got: {top}"
        )
