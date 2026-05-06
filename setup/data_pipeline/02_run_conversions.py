"""
STAAR Annual Data Pipeline — Step 2: Conversions

Converts a freshly-built yearly dataset (e.g., shc_core_2025) into research-ready
format by:
  1. Backing up every table to copy_<dataset>
  2. Converting STRING columns containing date/datetime values to proper types
  3. Adding a parallel _utc column for every DATETIME/TIMESTAMP column
     (source data is in America/Los_Angeles)

USAGE:
    1. Set DATASET_NAME below to the dataset you want to process.
    2. Make sure the backup destination dataset (copy_<DATASET_NAME>) exists
       and is empty in the BigQuery console.
    3. Authenticate locally: `gcloud auth application-default login`
    4. Run: `python 02_run_conversions.py`
    5. Repeat for the other dataset (e.g., run once for shc_core_2025,
       then change DATASET_NAME and run for lpch_core_2025).

IMPORTANT:
    This script uses CREATE OR REPLACE TABLE — the original raw data is
    overwritten. The backup in copy_<dataset> is your only rollback path.
    Do not delete the backup until validation passes (see 03_validate.md).

    The script is NOT idempotent. Running it twice on the same dataset will
    produce columns like <col>_utc_utc. If you need to re-run, restore from
    backup first.
"""

from google.cloud import bigquery

# ============================================================
# CONFIG — change DATASET_NAME between runs
# ============================================================
PROJECT_ID = "som-nero-phi-jonc101"
DATASET_NAME = "shc_core_2025"        # change to "lpch_core_2025" for LPCH run
BACKUP_DATASET = f"copy_{DATASET_NAME}"

# Tables to skip entirely (e.g., already processed, or known to fail)
SKIP_TABLES = []

# ============================================================
# Initialize BigQuery client
# ============================================================
client = bigquery.Client(project=PROJECT_ID)


# ============================================================
# Helpers
# ============================================================

def list_tables(dataset_name):
    """Return list of table names in a dataset."""
    dataset_ref = client.dataset(dataset_name, project=PROJECT_ID)
    return [t.table_id for t in client.list_tables(dataset_ref)]


def backup_table(table_name, source_dataset, backup_dataset):
    """Copy a single table from source_dataset to backup_dataset."""
    src = f"{PROJECT_ID}.{source_dataset}.{table_name}"
    dst = f"{PROJECT_ID}.{backup_dataset}.{table_name}"
    print(f"  Backup: {src} -> {dst}")
    job = client.copy_table(
        src, dst,
        job_config=bigquery.CopyJobConfig(write_disposition="WRITE_TRUNCATE"),
    )
    job.result()


def get_timestamp_columns(table_name, dataset_name):
    """Return columns whose type is already TIMESTAMP or DATETIME."""
    full = f"{PROJECT_ID}.{dataset_name}.{table_name}"
    table = client.get_table(full)
    return [
        f.name for f in table.schema
        if f.field_type in ("TIMESTAMP", "DATETIME")
    ]


def detect_string_date_columns(table_name, dataset_name):
    """
    Find STRING columns whose values parse as DATETIME or DATE.
    Returns (datetime_cols, date_cols).
    Datetime takes priority — if a column parses as both, treat as datetime.
    """
    full = f"{PROJECT_ID}.{dataset_name}.{table_name}"
    table = client.get_table(full)
    string_cols = [f.name for f in table.schema if f.field_type == "STRING"]

    datetime_cols, date_cols = [], []
    for col in string_cols:
        query = f"""
            SELECT
              COUNTIF(SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', `{col}`) IS NOT NULL) AS dt_count,
              COUNTIF(SAFE.PARSE_DATE('%Y-%m-%d', `{col}`) IS NOT NULL) AS d_count
            FROM `{full}`
        """
        try:
            row = next(iter(client.query(query).result()))
            if row.dt_count > 0:
                datetime_cols.append(col)
            elif row.d_count > 0:
                date_cols.append(col)
        except Exception:
            # Column can't be parsed at all — skip silently
            pass
    return datetime_cols, date_cols


def fix_string_datetime_columns(table_name, dataset_name, datetime_cols, date_cols):
    """Rewrite the table converting string date columns to proper types."""
    if not datetime_cols and not date_cols:
        return
    full = f"{PROJECT_ID}.{dataset_name}.{table_name}"
    all_cols = datetime_cols + date_cols
    expressions = []
    for col in datetime_cols:
        expressions.append(
            f"SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', `{col}`) AS `{col}`"
        )
    for col in date_cols:
        expressions.append(
            f"SAFE.PARSE_DATE('%Y-%m-%d', `{col}`) AS `{col}`"
        )

    except_clause = ", ".join(f"`{c}`" for c in all_cols)
    select_clause = ", ".join(expressions)

    query = f"""
        CREATE OR REPLACE TABLE `{full}` AS
        SELECT * EXCEPT({except_clause}), {select_clause}
        FROM `{full}`
    """
    print(f"  Converting STRING dates -> DATETIME/DATE: {all_cols}")
    client.query(query).result()


def add_utc_columns(table_name, dataset_name):
    """For every DATETIME/TIMESTAMP column, add a parallel <col>_utc column."""
    cols = get_timestamp_columns(table_name, dataset_name)
    if not cols:
        return
    full = f"{PROJECT_ID}.{dataset_name}.{table_name}"
    utc_exprs = [
        f"TIMESTAMP(`{c}`, 'America/Los_Angeles') AS `{c}_utc`" for c in cols
    ]
    query = f"""
        CREATE OR REPLACE TABLE `{full}` AS
        SELECT *, {', '.join(utc_exprs)}
        FROM `{full}`
    """
    print(f"  Adding UTC columns for: {cols}")
    client.query(query).result()


# ============================================================
# MAIN
# ============================================================

def main():
    print(f"\n{'=' * 60}")
    print(f"Processing dataset: {DATASET_NAME}")
    print(f"Backup target: {BACKUP_DATASET}")
    print(f"{'=' * 60}\n")

    tables = list_tables(DATASET_NAME)
    tables = [t for t in tables if t not in SKIP_TABLES]
    print(f"Found {len(tables)} tables to process.\n")

    failed = []
    for i, table in enumerate(tables, 1):
        print(f"[{i}/{len(tables)}] {table}")
        try:
            backup_table(table, DATASET_NAME, BACKUP_DATASET)

            dt_cols, d_cols = detect_string_date_columns(table, DATASET_NAME)
            fix_string_datetime_columns(table, DATASET_NAME, dt_cols, d_cols)

            add_utc_columns(table, DATASET_NAME)

            print(f"  ✔ Done\n")
        except Exception as e:
            print(f"  ✗ FAILED: {e}\n")
            failed.append((table, str(e)))

    print(f"{'=' * 60}")
    print(f"Finished {DATASET_NAME}")
    if failed:
        print(f"\n{len(failed)} table(s) failed:")
        for t, err in failed:
            print(f"  - {t}: {err}")
    else:
        print("All tables processed successfully.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
