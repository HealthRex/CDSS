# STAAR Annual Data Pipeline

*Location: `CDSS/setup/data_pipeline/`*

This folder contains the procedure and code for the annual STAAR data update — pulling fresh clinical data from the secure project into the lab's working project, applying standard transformations, and validating the result.

## When to use this

Once a year (or whenever STARR delivers a new data refresh), follow the steps in this folder to build `shc_core_YYYY` and `lpch_core_YYYY` in `som-nero-phi-jonc101`.

## Projects involved

| Project | Role |
|---|---|
| `som-nero-phi-jonc101-secure` | Source. Receives raw updates from STARR in `shc_core_updates` and `lpch_core_updates`. |
| `som-nero-phi-jonc101` | Destination. Where research happens. New yearly datasets live here. |

## The pipeline (4 steps)

### Step 1 — Build the yearly dataset

Copy raw tables from the secure project's `*_updates` datasets into new yearly datasets in the working project. See [`01_build_yearly_dataset.md`](./01_build_yearly_dataset.md).

Output: `shc_core_YYYY` and `lpch_core_YYYY` populated with raw data.

### Step 2 — Run conversions

Apply the standard transformations to each table:

1. Backup every table to `copy_<dataset>` (safety net before destructive operations).
2. Detect STRING columns containing date/datetime values and convert them to proper DATETIME/DATE types.
3. For every DATETIME/TIMESTAMP column, add a parallel `_utc` column (source data is in `America/Los_Angeles`).

Run [`02_run_conversions.py`](./02_run_conversions.py) once per dataset (change the `DATASET_NAME` constant at the top between runs).

### Step 3 — Validate

Spot-check the converted datasets. See [`03_validate.md`](./03_validate.md) for the standard checks:

- `_utc` columns exist on key tables
- Spot-check converted DATETIME columns visually
- Compare NULL counts between backup and converted tables
- Confirm row counts unchanged

### Step 4 — Announce

Once validation passes:

1. Drop the `copy_*` backup datasets after a 1–2 week validation period (during which researchers may flag issues).
2. Post an announcement in `#general` and `#devops` letting the lab know the new datasets are live.

## Important conventions

- **Yearly datasets are immutable snapshots.** Once `shc_core_YYYY` is built and validated, do not modify it. New refreshes go into the next year's dataset.
- **`shc_core` (no year) is the live working dataset.** Active research uses this.
- **Excluded from transfer:** `lpch_myc_mesg` stays in the secure project and is never copied to the working project.
- **All datetime data is jittered.** Real PHI dates are not present; the `_jittered` suffix on column names reflects this.

## What's in `archive/`

Historical documentation kept for reference:

- `BigQueryDataUpdateGuide.MD` — Original 2021 step-by-step guide with per-table conversion SQL. Useful when current automation fails on a specific table and you need to fall back to manual SQL.
- `shc_lpch_conversions.md` — Original notes describing the rationale for the conversion process.
- `new_SHCdata_Organize_DateTime.ipynb` — Original notebook used for the 2024 update.

## Future work

- **Automation.** The current pipeline is run manually once a year. A planned future state runs Steps 1 and 2 automatically on a weekly or daily schedule, populating a `shc_core_current` dataset that's always fresh, with yearly snapshots taken at year-end.
- **Schema drift handling.** Each year, source schemas may change (new columns, renamed tables). The current process surfaces these as errors during conversion; a more robust pipeline would detect drift up front.

## Questions

Contact [pipeline owner / your name] or post in `#devops`.
