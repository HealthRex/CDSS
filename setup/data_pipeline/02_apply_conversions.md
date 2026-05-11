# Step 2 — Apply conversions

After Step 1, the yearly datasets contain raw data with STRING-typed date columns and no `_utc` columns. This step applies the standard transformations using the per-table SQL in [`BigQueryDataUpdateGuide.MD`](./BigQueryDataUpdateGuide.MD).

## Why this uses explicit per-table SQL (not auto-detection)

`BigQueryDataUpdateGuide.MD` lists, for every table, the exact columns that should be converted from STRING to DATETIME/DATE and the exact columns that should get a parallel `_utc` version. These lists were curated by hand by the original author of the pipeline because **auto-detecting which STRING columns are "dates" is unsafe**:

- `lab_result.ord_value` contains lab result text (e.g., `"5.2"`, `"negative"`, `"trace"`). Some values coincidentally parse as dates.
- `lab_result.reference_low`, `reference_high`, `extended_value_comment`, `extended_comp_comment` are the same — text fields where a few values may look date-shaped.
- Auto-detection that flags any column with at least one parseable date misclassifies these as datetime columns, and the subsequent `PARSE_DATETIME` call destroys the original text data by returning NULL for everything that isn't a date.

Always use the guide's explicit column lists. Do not auto-detect.

## Before you start

### Make backups

⚠️ **Critical.** The conversion uses `CREATE OR REPLACE TABLE` which overwrites tables. There is no rollback without a backup. (BigQuery's 7-day time-travel can recover from accidents but is awkward to use.)

In the BigQuery console, create two new empty datasets:

- `som-nero-phi-jonc101.copy_shc_core_YYYY`
- `som-nero-phi-jonc101.copy_lpch_core_YYYY`

Then copy every table:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_YYYY.<table>` AS
SELECT * FROM `som-nero-phi-jonc101.shc_core_YYYY.<table>`;
```

Repeat for every table in both yearly datasets. Verify the backup datasets exist before proceeding.

## Procedure

### 1. Open the guide

Open [`BigQueryDataUpdateGuide.MD`](./BigQueryDataUpdateGuide.MD). The relevant section is **"Re-formating datetime columns"** — it contains a separate SQL block for every table.

### 2. Adapt each block for the current year

The guide's SQL was written for an earlier year (e.g., `lpch_core_2021`). For each table's SQL block:

1. Change the `FROM` clause to point at the current year's dataset (e.g., `lpch_core_2021` → `lpch_core_YYYY`).
2. Wrap the `SELECT` in `CREATE OR REPLACE TABLE \`som-nero-phi-jonc101.shc_core_YYYY.<table>\` AS` so the converted result replaces the table in place.
3. Run the query.

### 3. Spot-check schema drift

Before running each table's conversion, confirm the columns in the guide still exist with the same names in this year's data. Quick check:

```sql
SELECT column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = '<table>'
ORDER BY ordinal_position;
```

If columns the guide expects are missing or renamed, adjust the conversion SQL accordingly and note the change for next year.

### 4. Handle tables not in the guide

If this year's dataset has tables that don't appear in the guide (e.g., `mom_baby`, `lpch_alt_com_action` added in 2025), inspect each one manually:

- Look at the schema (which columns are STRING?).
- For STRING columns that look like dates, sample a few values to confirm.
- Write a conversion SQL block following the guide's pattern.
- Add the new table to the guide (commit alongside the year's update).

## Tables that need no conversion

Some tables have no STRING-typed date columns. The guide skips these and you can too:

- Reference tables: `zip`, `prov_map`, `drg_code`, `ndc_code`, `dep_map`
- Anything where the schema is already correct (DATETIME types, no STRING dates)

Skipping is not a problem. The `_utc` columns are only added where a DATETIME or TIMESTAMP column exists.

## Common issues

- **`Could not parse value as DATETIME`** — a column the guide expects to convert has values in a format that doesn't match `%Y-%m-%d %H:%M:%S`. Inspect the source values and adjust the format string.
- **Column already converted** — if the schema shows the column is already DATETIME, skip that line of the conversion.
- **Source values use `NULL` instead of empty string** — the guide's `CASE WHEN col <> '' THEN col ELSE NULL END` pattern handles both, but worth confirming.

## Next step

Once all conversions are applied, proceed to [Step 3 — Validate](./03_validate.md).
