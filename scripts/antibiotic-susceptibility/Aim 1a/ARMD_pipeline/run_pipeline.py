"""
ARMD Pipeline Runner

Executes all SQL queries in order to rebuild the ARMD dataset from STARR.

Each run produces a self-contained dataset named ARMD_<year> built from the
matching STARR source dataset shc_core_<year>.

Usage:
    python run_pipeline.py --year 2025                  # Build ARMD_2025 from shc_core_2025
    python run_pipeline.py --year 2024                  # Build ARMD_2024 from shc_core_2024
    python run_pipeline.py --year 2025 --step 01_cohort # Run a single step
    python run_pipeline.py --year 2025 --from 04_labs   # Resume from a specific step
    python run_pipeline.py --year 2025 --dry-run        # Print queries without executing
    python run_pipeline.py --year 2025 --export ./out/  # Export tables to CSV after building
    python run_pipeline.py --year 2025 --skip-setup     # Skip CSV upload step (assume already loaded)

Notes:
    - The destination dataset ARMD_<year> is created if it doesn't exist.
    - Reference CSVs (temp_antibiotics, prior_antibiotics_list, CPT_ICD10PCS_mapping)
      are uploaded into the destination dataset as the first action, so the
      pipeline is fully self-contained.
    - SQL files keep literal `shc_core_2023` and `antimicrobial_stewardship` so
      each remains independently runnable in the BigQuery UI; this runner
      replaces those strings at execution time.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from config import (
    BQ_PROJECT,
    CSV_EXPORT_NAMES,
    DEFAULT_YEAR,
    DEST_PLACEHOLDER_DATASET,
    REFERENCE_CSVS,
    SOURCE_PLACEHOLDER_DATASET,
    SQL_EXECUTION_ORDER,
    dest_dataset,
    fully_qualified_dest,
    fully_qualified_source,
    source_dataset,
    tables_for_year,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("armd_pipeline")

PIPELINE_DIR = Path(__file__).parent
SQL_DIR = PIPELINE_DIR / "sql"
# Reference CSVs live one level above (the "master scripts" folder).
REFERENCE_CSV_DIR = PIPELINE_DIR.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_dataset(client: bigquery.Client, dataset_id: str, location: str = "US") -> None:
    """Create the destination dataset if it doesn't already exist."""
    full_id = f"{client.project}.{dataset_id}"
    try:
        client.get_dataset(full_id)
        logger.info(f"Dataset already exists: {full_id}")
    except NotFound:
        ds = bigquery.Dataset(full_id)
        ds.location = location
        client.create_dataset(ds)
        logger.info(f"Created dataset: {full_id}")


# Explicit schemas for each reference CSV. Used instead of autodetect so that
# CRLF line endings, UTF-8 BOMs, and quoted fields in the header row can't
# corrupt the column names (we hit "Unrecognized name: antibiotic_name" before
# we added this).
REFERENCE_CSV_SCHEMAS = {
    "temp_antibiotics": [
        bigquery.SchemaField("antibiotic_name", "STRING"),
    ],
    "prior_antibiotics_list": [
        bigquery.SchemaField("antibiotic_name", "STRING"),
        bigquery.SchemaField("prescription_count", "INT64"),
        bigquery.SchemaField("class_name", "STRING"),
    ],
    "CPT_ICD10PCS_mapping": [
        bigquery.SchemaField("procedure_cat", "STRING"),
        bigquery.SchemaField("reference_code_set", "STRING"),
        bigquery.SchemaField("code", "STRING"),
        bigquery.SchemaField("proc_simple", "STRING"),
        bigquery.SchemaField("proc_simple_comment", "STRING"),
        bigquery.SchemaField("reference_description", "STRING"),
    ],
}


def upload_reference_csvs(client: bigquery.Client, year: int, dry_run: bool = False) -> None:
    """Upload reference CSVs (temp_antibiotics etc.) into ARMD_<year>.

    Uses explicit schemas (REFERENCE_CSV_SCHEMAS) so column names come from
    the pipeline, not from the CSV header bytes.
    """
    dest_full = fully_qualified_dest(year)
    for table_name, csv_filename in REFERENCE_CSVS.items():
        # Look in the pipeline folder first (canonical, GitHub-checkout location),
        # then fall back to the parent folder for legacy local setups.
        csv_path = PIPELINE_DIR / csv_filename
        if not csv_path.exists():
            alt = REFERENCE_CSV_DIR / csv_filename
            if alt.exists():
                csv_path = alt
        if not csv_path.exists():
            logger.warning(
                f"Reference CSV not found, skipping: {csv_filename} "
                f"(looked in {PIPELINE_DIR} and {REFERENCE_CSV_DIR})"
            )
            continue

        table_id = f"{dest_full}.{table_name}"
        if dry_run:
            logger.info(f"[DRY RUN] Would upload {csv_path.name} -> {table_id}")
            continue

        schema = REFERENCE_CSV_SCHEMAS.get(table_name)
        if schema is None:
            logger.warning(
                f"No explicit schema for {table_name}; falling back to autodetect."
            )

        logger.info(f"Uploading {csv_path.name} -> {table_id}")
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            schema=schema,
            autodetect=schema is None,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            allow_quoted_newlines=True,
            allow_jagged_rows=True,
        )
        with open(csv_path, "rb") as f:
            job = client.load_table_from_file(f, table_id, job_config=job_config)
        job.result()
        table = client.get_table(table_id)
        logger.info(f"  Loaded {table.num_rows} rows into {table_id}")


def substitute_dataset_refs(sql_text: str, year: int) -> str:
    """Replace placeholder dataset names with year-specific ones.

    The SQL files reference:
        som-nero-phi-jonc101.shc_core_2023            -> source
        som-nero-phi-jonc101.antimicrobial_stewardship -> destination

    For step 13 the original SQL also referenced an external `mvm_abx` dataset
    for CPT_ICD10PCS_mapping. We rewrite that to the year-local copy we just
    uploaded so the pipeline is self-contained.
    """
    src = source_dataset(year)
    dst = dest_dataset(year)
    out = sql_text
    out = out.replace(SOURCE_PLACEHOLDER_DATASET, src)
    out = out.replace(DEST_PLACEHOLDER_DATASET, dst)
    # Step 13 historically pointed at mvm_abx.CPT_ICD10PCS_mapping; redirect to
    # the local copy.
    out = out.replace(
        f"{BQ_PROJECT}.mvm_abx.CPT_ICD10PCS_mapping",
        f"{BQ_PROJECT}.{dst}.CPT_ICD10PCS_mapping",
    )
    return out


def read_sql_file(filename: str) -> str:
    filepath = SQL_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"SQL file not found: {filepath}")
    return filepath.read_text(encoding="utf-8")


def split_sql_statements(sql_text: str) -> list[str]:
    """Split a SQL file into individual statements.

    Handles BigQuery's `#` and `--` comments, and semicolon-separated
    statements (some files contain multiple CREATE TABLE statements).
    """
    statements: list[str] = []
    current: list[str] = []

    for line in sql_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("--"):
            continue
        if not stripped:
            continue

        current.append(line)

        if stripped.endswith(";"):
            stmt = "\n".join(current).strip().rstrip(";").strip()
            if stmt:
                statements.append(stmt)
            current = []

    if current:
        stmt = "\n".join(current).strip()
        if stmt:
            statements.append(stmt)

    return statements


def run_sql_file(client: bigquery.Client, filename: str, year: int, dry_run: bool = False) -> None:
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Running: {filename}  (year={year})")
    raw = read_sql_file(filename)
    sql_text = substitute_dataset_refs(raw, year)
    statements = split_sql_statements(sql_text)

    if not statements:
        logger.warning(f"No executable statements found in {filename}")
        return

    for i, stmt in enumerate(statements, 1):
        table_name = ""
        for line in stmt.split("\n"):
            upper = line.upper()
            if "CREATE OR REPLACE TABLE" in upper or "CREATE TABLE" in upper:
                if "`" in line:
                    table_name = line.split("`")[1]
                break

        desc = f"  Statement {i}/{len(statements)}"
        if table_name:
            desc += f" -> {table_name}"

        if dry_run:
            logger.info(f"[DRY RUN] {desc}")
            logger.info(f"  First 200 chars: {stmt[:200]}...")
            continue

        logger.info(desc)
        start = time.time()
        try:
            query_job = client.query(stmt)
            query_job.result()
            elapsed = time.time() - start
            if query_job.total_bytes_processed:
                gb = query_job.total_bytes_processed / (1024 ** 3)
                logger.info(f"  Done in {elapsed:.1f}s, processed {gb:.2f} GB")
            else:
                logger.info(f"  Done in {elapsed:.1f}s")
        except Exception as e:
            logger.error(f"  FAILED: {e}")
            raise


def export_tables(client: bigquery.Client, year: int, export_dir: str) -> None:
    export_path = Path(export_dir)
    export_path.mkdir(parents=True, exist_ok=True)
    tables = tables_for_year(year)

    for table_key, csv_name in CSV_EXPORT_NAMES.items():
        if table_key not in tables:
            continue
        table_ref = tables[table_key]
        dest_file = export_path / csv_name
        logger.info(f"Exporting {table_ref} -> {dest_file}")
        df = client.query(f"SELECT * FROM `{table_ref}`").to_dataframe()
        df.to_csv(dest_file, index=False)
        logger.info(f"  Exported {len(df)} rows")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ARMD Pipeline Runner")
    parser.add_argument(
        "--year",
        type=int,
        default=DEFAULT_YEAR,
        help=f"STARR year to build (default: {DEFAULT_YEAR}). "
             f"Source dataset: shc_core_<year>, destination: ARMD_<year>.",
    )
    parser.add_argument("--step", help="Run only a specific step (e.g. 01_cohort)")
    parser.add_argument("--from", dest="from_step", help="Resume from a specific step")
    parser.add_argument("--dry-run", action="store_true", help="Print queries without executing")
    parser.add_argument("--skip-setup", action="store_true",
                        help="Skip dataset creation and reference CSV upload")
    parser.add_argument("--export", metavar="DIR", help="Export tables to CSV after building")
    parser.add_argument("--project", default=BQ_PROJECT, help="BigQuery project ID")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    year = args.year

    logger.info(f"ARMD Pipeline: year={year}")
    logger.info(f"  Source dataset: {fully_qualified_source(year)}")
    logger.info(f"  Destination dataset: {fully_qualified_dest(year)}")

    # ---------- Setup: dataset + reference CSVs ----------
    if not args.skip_setup:
        if args.dry_run:
            logger.info(f"[DRY RUN] Would ensure dataset {dest_dataset(year)} exists")
        else:
            ensure_dataset(client, dest_dataset(year))
        upload_reference_csvs(client, year, dry_run=args.dry_run)

    # ---------- Determine which SQL steps to run ----------
    steps = SQL_EXECUTION_ORDER

    if args.step:
        match = [s for s in steps if args.step in s]
        if not match:
            logger.error(f"Step '{args.step}' not found. Available: {steps}")
            sys.exit(1)
        steps = match
    elif args.from_step:
        idx = None
        for i, s in enumerate(steps):
            if args.from_step in s:
                idx = i
                break
        if idx is None:
            logger.error(f"Step '{args.from_step}' not found. Available: {SQL_EXECUTION_ORDER}")
            sys.exit(1)
        steps = steps[idx:]

    logger.info(f"Executing {len(steps)} SQL step(s): {[s.split('.')[0] for s in steps]}")

    total_start = time.time()
    for step_file in steps:
        run_sql_file(client, step_file, year, dry_run=args.dry_run)
    total_elapsed = time.time() - total_start
    logger.info(f"Pipeline completed in {total_elapsed:.1f}s ({total_elapsed/60:.1f}m)")

    if args.export:
        export_tables(client, year, args.export)


if __name__ == "__main__":
    main()
