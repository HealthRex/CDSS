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

### Step 2 — Apply conversions

Run the per-table conversion SQL from [`../BigQueryDataUpdateGuide.MD`](../BigQueryDataUpdateGuide.MD). The guide lists, for every table, the exact columns that should be converted from STRING to DATETIME/DATE and the columns that should get a parallel `_utc` version.

See [`02_apply_conversions.md`](./02_apply_conversions.md) for how to use the guide.

⚠️ **Do not use auto-detection** to decide which columns to convert. A previous attempt at this misclassified columns like `lab_result.ord_value` (which contains lab result text, not dates) as datetimes, silently destroying data. Always use the explicit per-table column lists from the guide.

### Step 3 — Validate

Spot-check the converted datasets. See [`03_validate.md`](./03_validate.md) for the standard checks:

- `_utc` columns exist on key tables
- Spot-check converted DATETIME columns visually
- Confirm row counts unchanged between source and destination
- Confirm that columns the guide does NOT list for conversion remain as STRING (e.g., `lab_result.ord_value`, `lab_result.reference_low`)

### Step 4 — Announce

Once validation passes:

1. Post an announcement in `#general` and `#devops` letting the lab know the new datasets are live.
2. Note any new tables or schema changes compared to last year.

## Important conventions

- **Yearly datasets are immutable snapshots.** Once `shc_core_YYYY` is built and validated, do not modify it. New refreshes go into the next year's dataset.
- **`shc_core` (no year) is the live working dataset.** Active research uses this.
- **Excluded from transfer:** `lpch_myc_mesg` stays in the secure project and is never copied to the working project.
- **SHC destination tables drop the `shc_` prefix** (source `shc_encounter` → destination `encounter`).
- **LPCH destination tables keep the `lpch_` prefix** (source `lpch_encounter` → destination `lpch_encounter`).
- **All datetime data is jittered.** Real PHI dates are not present; the `_jittered` suffix on column names reflects this.
- **Source times are in America/Los_Angeles.** The conversion adds parallel `_utc` columns for timezone-correct analysis.

## Backups

Before running the conversion in Step 2, always back up the freshly-built yearly datasets. Create `copy_shc_core_YYYY` and `copy_lpch_core_YYYY` datasets first, then copy each table. Keep backups for at least 2 weeks after announcing the new datasets. Drop them only after validation passes and no researchers have flagged issues.

## Related files in `setup/`

The following files in the parent `setup/` folder are part of the annual data pipeline workflow:

- [`../BigQueryDataUpdateGuide.MD`](../BigQueryDataUpdateGuide.MD) — Per-table conversion SQL. The authoritative reference for Step 2.
- `../shc_lpch_conversions.md` — Original notes describing the rationale for the conversion process.
- `../new_SHCdata_Organize_DateTime.ipynb` — Original notebook used for past annual updates.
- `../lpch_conversion.py` — Original auto-detection script. **Do not use for new updates.** Auto-detection of which STRING columns are "dates" produces silent bugs on columns like `lab_result.ord_value` where some values coincidentally parse as dates. Kept only as a historical artifact.

## Future work

- **Automation.** The current pipeline is run manually once a year. A planned future state runs Steps 1 and 2 automatically on a weekly or daily schedule, populating a `shc_core_current` dataset that's always fresh, with yearly snapshots taken at year-end. Any automated solution must use explicit per-table column lists from the guide, not auto-detection.
- **Schema drift handling.** Each year, source schemas may change (new columns, renamed tables). The current process surfaces these as errors during conversion; a more robust pipeline would detect drift up front and flag it for human review.

## Questions
Contact [jonc101@stanford.edu/fnateghi@stanford.edu] or post in `#devops`.
