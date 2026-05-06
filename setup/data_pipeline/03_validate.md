# Step 3 — Validate the conversions

After running `02_run_conversions.py`, run these checks before announcing the dataset to the lab. Replace `YYYY` with the year you're processing.

## Check 1 — `_utc` columns exist

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%_utc'
ORDER BY table_name, column_name;
```

Expect lots of `_utc` columns of type `TIMESTAMP`. Tables like `encounter`, `order_proc`, and `lab_result` should each have multiple. If a clinical table has zero, the conversion failed for that table — check the script log.

Run the same against `lpch_core_YYYY`.

## Check 2 — Spot-check a converted DATETIME

```sql
SELECT
  hosp_admsn_time_jittered,
  hosp_admsn_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_YYYY.encounter`
WHERE hosp_admsn_time_jittered IS NOT NULL
LIMIT 10;
```

The two columns should show times that differ by 7 or 8 hours (LA → UTC, depending on daylight saving). Both should display as proper datetime values, not as quoted strings.

## Check 3 — No silent NULL explosion

The biggest risk is a STRING column that mostly parsed but partially became NULL. Compare NULL counts between the backup and the converted table:

```sql
SELECT
  'backup' AS source,
  COUNTIF(hosp_admsn_time_jittered IS NULL) AS null_count,
  COUNT(*) AS total_rows
FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.encounter`
UNION ALL
SELECT
  'converted' AS source,
  COUNTIF(hosp_admsn_time_jittered IS NULL) AS null_count,
  COUNT(*) AS total_rows
FROM `som-nero-phi-jonc101.shc_core_YYYY.encounter`;
```

NULL counts should be identical or very close (empty strings `''` parse to NULL — that small difference is expected). A dramatic increase in NULLs means the format string didn't match the data.

Repeat for one or two big tables in each dataset (`order_proc`, `lab_result`, `flowsheet`).

## Check 4 — Row counts unchanged

```sql
SELECT 'encounter' AS t, COUNT(*) AS backup_n FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.encounter`
UNION ALL SELECT 'encounter (converted)', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.encounter`
UNION ALL SELECT 'order_proc', COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.order_proc`
UNION ALL SELECT 'order_proc (converted)', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.order_proc`
UNION ALL SELECT 'lab_result', COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.lab_result`
UNION ALL SELECT 'lab_result (converted)', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.lab_result`;
```

Backup and converted should have identical row counts. The conversion rewrites columns, not rows.

## Check 5 — Review the script log

Scroll back through the script's output. Any line starting with `✗ FAILED:` is a table that errored. Common failures:

- **"Cannot access field"** — column was already DATETIME, not STRING. Usually safe to ignore.
- **"Could not parse"** — date format didn't match `%Y-%m-%d %H:%M:%S`. May need manual SQL using a different format string.
- **Permission errors** — IAM issue, escalate.

For each failed table, decide whether to fix manually (use the per-table SQL in `archive/BigQueryDataUpdateGuide.MD` as a template) or accept the table as-is.

## After validation passes

1. Wait 1–2 weeks for researchers to surface any issues.
2. Drop the backup datasets:

   ```sql
   DROP SCHEMA `som-nero-phi-jonc101.copy_shc_core_YYYY` CASCADE;
   DROP SCHEMA `som-nero-phi-jonc101.copy_lpch_core_YYYY` CASCADE;
   ```

3. BigQuery's 7-day time-travel still provides a fallback during the validation window even after dropping backups.
