# STAAR Annual Data Pipeline

*Location: `CDSS/setup/data_pipeline/`*

This folder is the complete, self-contained guide for the annual STAAR data update — pulling fresh clinical data from the secure project into the lab's working project, transforming it for research use, and validating the result.

All SQL needed to run a year's update is included in these files. The historical docs in the parent `setup/` folder (`BigQueryDataUpdateGuide.MD`, `shc_lpch_conversions.md`, the auto-detection scripts) are kept for reference but are no longer the procedure to follow.

## When to use this

Once a year (or whenever STARR delivers a new data refresh), follow the steps in this folder to build `shc_core_YYYY` and `lpch_core_YYYY` in `som-nero-phi-jonc101`.

## Projects involved

| Project | Role |
|---|---|
| `som-nero-phi-jonc101-secure` | Source. Receives raw updates from STARR in `shc_core_updates` and `lpch_core_updates`. |
| `som-nero-phi-jonc101` | Destination. Where research happens. New yearly datasets live here. |

## Pipeline overview

1. **[Step 1 — Inventory & plan](./01_inventory_and_plan.md)** — list source tables, compare to last year's structure, decide what to include
2. **[Step 2 — Build raw datasets](./02_build_raw_datasets.md)** — copy raw tables from secure → working
3. **[Step 3 — Backup before transforming](./03_backup.md)** — copy yearly datasets to `copy_*` (safety net)
4. **[Step 4 — Apply conversions](./04_apply_conversions.md)** — add `_utc` columns derived from previous year's schema
5. **[Step 5 — Validate](./05_validate.md)** — schema checks, row counts, sanity queries
6. **[Step 6 — Announce & clean up](./06_announce_and_cleanup.md)** — Slack message, drop backups when stable

## Important conventions

- **Yearly datasets are immutable snapshots.** Once `shc_core_YYYY` is built and validated, do not modify it. New refreshes go into the next year's dataset.
- **`shc_core` (no year) is the live working dataset.** Active research uses this.
- **SHC destination tables drop the `shc_` prefix** (source `shc_encounter` → destination `encounter`).
- **LPCH destination tables keep the `lpch_` prefix** (source `lpch_encounter` → destination `lpch_encounter`).
- **Excluded from transfer:** `lpch_myc_mesg` stays in the secure project and is never copied.
- **All datetime data is jittered.** Real PHI dates are not present.
- **Source times are in America/Los_Angeles.** The conversion adds parallel `_utc` columns.

## Key lessons from past updates

- **Use last year's schema as the source of truth.** When deciding which columns need conversion, query `INFORMATION_SCHEMA.COLUMNS` of the previous year's dataset. Don't trust outdated guides or auto-detection.
- **Auto-detection of "date-shaped" STRING columns is unsafe.** A previous version of the pipeline used a Python script that flagged any STRING column with at least one date-parseable value as a datetime column. This silently destroyed text columns like `lab_result.ord_value` that contained values like `"5.2"` or `"negative"` — some of which happened to parse as dates.
- **Always back up before destructive operations.** The conversion uses `CREATE OR REPLACE TABLE` which overwrites tables. The `copy_*` backup datasets are the only rollback path.
- **The `flowsheet.meas_value` column needs numerical extraction.** `meas_value` is STRING — researchers can't aggregate or filter on it. The pipeline adds `numerical_val_1` through `numerical_val_4` columns (FLOAT64) extracted from `meas_value` via regex. See Step 4 for the SQL.
- **The secure project now delivers properly-typed DATETIME columns.** Past versions of the pipeline assumed STRING columns needed `PARSE_DATETIME`. As of the 2025 update, this is no longer needed — the conversion is just adding `_utc` columns alongside the existing DATETIME ones.

## Related files in `setup/`

These are historical references, not the current procedure:

- `../BigQueryDataUpdateGuide.MD` — Original 2021 guide with per-table conversion SQL. Useful only as a historical record.
- `../shc_lpch_conversions.md` — Original notes on the conversion process.
- `../new_SHCdata_Organize_DateTime.ipynb` — Notebook used in past updates. Contains auto-detection logic that is no longer used.
- `../lpch_conversion.py` — Auto-detection script. **Do not use.** Kept for historical reference only.

## Questions

Contact [fnateghi@stanford.edu/jonc101@stanford.edu] or post in `#devops`.
