# STAAR Data Pipeline

*Location: `CDSS/setup/data_pipeline/`*

This folder is the complete, self-contained guide for loading STAAR clinical data refreshes — pulling fresh data from the secure project into the lab's working project, transforming it for research use, and validating the result.

All SQL needed to run a refresh is included in these files. The historical docs in the parent `setup/` folder (`BigQueryDataUpdateGuide.MD`, `shc_lpch_conversions.md`, the auto-detection scripts) are kept for reference but are no longer the procedure to follow.

## Refresh cadence

As of FY27, Stanford's Research Technology team delivers refreshes **every 4–6 weeks** (confirmed with Priya Desai, Aug 2026). Previously this was an annual process.

Each refresh follows the same six steps below. Whether a refresh creates a new yearly dataset or updates the existing one depends on the calendar — see below.

## Which dataset does a refresh go into?

**All refreshes for a given calendar year land in that year's dataset.** A refresh delivered in Aug 2026 with a Clarity cut date of Aug 2026 goes into `shc_core_2025` / `lpch_core_2025` — the dataset is *replaced in place* with the fuller cumulative extract.

A new yearly dataset (`shc_core_2026`) is created only once 2026 has finished and the lab decides to snapshot it. The yearly datasets are cumulative snapshots, not calendar-year slices — `shc_core_2025` contains all data through the most recent cut, not just 2025 data.

This means mid-year refreshes are **destructive rebuilds** of a dataset researchers are actively using. Always back up first (Step 3).

## Projects involved

| Project | Role |
|---|---|
| `som-nero-phi-jonc101-secure` | Source. Receives refreshes in `shc_core_updates` and `lpch_core_updates`. Also holds `starr_map`. |
| `som-nero-phi-jonc101` | Destination. Where research happens. Yearly datasets live here. |

## Pipeline overview

1. **[Step 1 — Inventory & plan](./01_inventory_and_plan.md)** — verify the source, compare to current dataset, decide what to include
2. **[Step 2 — Build raw datasets](./02_build_raw_datasets.md)** — copy raw tables from secure → working
3. **[Step 3 — Backup before transforming](./03_backup.md)** — copy current datasets to `copy_*` (safety net)
4. **[Step 4 — Apply conversions](./04_apply_conversions.md)** — `_utc` columns, flowsheet numerical extraction
5. **[Step 5 — Validate](./05_validate.md)** — schema checks, PHI checks, growth checks
6. **[Step 6 — Announce & clean up](./06_announce_and_cleanup.md)** — Slack message, drop backups when stable

See [`CHANGELOG.md`](./CHANGELOG.md) for a record of past refreshes.

## Permanent exclusions — never copy to the working project

These tables exist in the secure project and must **stay there**. They contain PHI or were excluded by decision.

| Table / dataset | Reason |
|---|---|
| `starr_map` (entire dataset) | Contains `mrn`, `anon_id`, `jitter`, and offset columns — the re-identification key. Never copy anything from this dataset. |
| `shc_patients` | Contains `mrn` (direct PHI) |
| `lpch_patients` | Same table on the pediatric side — check for `mrn` before including |
| `shc_myc_mesg` | MyChart patient-provider messages (per Jonathan) |
| `lpch_myc_mesg` | Same, pediatric side (per Jonathan) |
| `shc_lpch_geolocation_from_omop` | Stays in secure (per Jonathan) |
| `shc_lpch_prov_map` | Cross-system bridging table, decided not to copy (Apr 2026) |

Before each refresh, check any **new** table for `mrn` or other direct identifiers before adding it to the build.

## Naming conventions

- **SHC destination tables drop the `shc_` prefix** — source `shc_encounter` → destination `encounter`
- **LPCH destination tables keep the `lpch_` prefix** — source `lpch_encounter` → destination `lpch_encounter`
- Some tables in `shc_core_updates` have no prefix in the source (`geolocation_from_omop`, `prov_map`) — use the source name as-is
- All datetime data is jittered; the `_jittered` suffix reflects this
- Source times are in `America/Los_Angeles`; the conversion adds parallel `_utc` columns

## Key lessons

- **Use the current dataset's schema as the source of truth** when deciding which columns need conversion. Query `INFORMATION_SCHEMA.COLUMNS` on the live dataset (or last year's) rather than trusting an outdated guide.
- **Never auto-detect which STRING columns are dates.** A previous version of this pipeline used a Python script that flagged any STRING column with at least one date-parseable value as a datetime column, then converted it. This silently destroyed text columns like `lab_result.ord_value` (values like `"5.2"`, `"negative"`, `"<0.1"` — a few of which happened to parse as dates). Always use explicit column lists.
- **Always back up before a rebuild.** `CREATE OR REPLACE TABLE` overwrites with no rollback. The `copy_*` datasets are the only recovery path beyond BigQuery's 7-day time travel.
- **The secure project delivers properly-typed DATETIME columns.** Older docs assume STRING columns needing `PARSE_DATETIME`. As of 2025 this is no longer true — conversion is just adding `_utc` columns.
- **`flowsheet.meas_value` needs numerical extraction.** It's STRING, so researchers can't aggregate on it. The pipeline adds `numerical_val_1`–`4` (FLOAT64) extracted via regex. This step is easy to forget after a rebuild — it gets wiped every time.
- **Verify the source before rebuilding.** Confirm the source is cumulative (not delta-only) and that any bug fixes the data team reports actually landed. See Step 1.

## Related files in `setup/`

Historical references, not the current procedure:

- `../BigQueryDataUpdateGuide.MD` — Original 2021 guide with per-table conversion SQL
- `../shc_lpch_conversions.md` — Original notes on the conversion rationale
- `../new_SHCdata_Organize_DateTime.ipynb` — Notebook used in past updates
- `../lpch_conversion.py` — Auto-detection script. **Do not use.**

## Questions

Contact [pipeline owner / your name] or post in `#devops`.
