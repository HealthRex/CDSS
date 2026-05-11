# Step 3 — Validate the conversions

After Step 2, run these checks before announcing the dataset to the lab. Replace `YYYY` with the year you're processing.

## Check 1 — `_utc` columns exist on key tables

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%_utc'
ORDER BY table_name, column_name;
```

Expect lots of `_utc` columns of type `TIMESTAMP`. Tables like `encounter`, `order_proc`, and `lab_result` should each have multiple. If a clinical table has zero, the conversion was skipped or failed.

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

## Check 3 — Confirm STRING columns stayed STRING

This is the check that would have caught the `lab_result.ord_value` regression. For every table, the columns the guide does NOT list for conversion must remain STRING.

Specifically verify:

```sql
SELECT column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'lab_result'
  AND column_name IN ('ord_value', 'reference_low', 'reference_high',
                      'extended_value_comment', 'extended_comp_comment')
ORDER BY column_name;
```

All five should still be `STRING`. If any are `DATETIME`, `DATE`, or `TIMESTAMP`, the conversion was wrong — restore from backup and re-run with the correct per-table SQL.

Sample the values to confirm they look like text data, not dates:

```sql
SELECT DISTINCT ord_value
FROM `som-nero-phi-jonc101.shc_core_YYYY.lab_result`
WHERE ord_value IS NOT NULL
LIMIT 20;
```

Values should be things like `"5.2"`, `"negative"`, `"trace"`, `"<0.1"` — not datetime strings.

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

## Check 5 — No silent NULL explosion

A converted DATETIME column should have nearly the same NULL count as the source STRING (modulo empty strings that parse to NULL).

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

NULL counts should match closely. A dramatic increase means a parse format didn't match the data.

Repeat for one or two big tables in each dataset (`order_proc`, `lab_result`, `flowsheet`).

## After validation passes

1. Wait 1–2 weeks for researchers to surface any issues.
2. Drop the backup datasets:

   ```sql
   DROP SCHEMA `som-nero-phi-jonc101.copy_shc_core_YYYY` CASCADE;
   DROP SCHEMA `som-nero-phi-jonc101.copy_lpch_core_YYYY` CASCADE;
   ```

3. BigQuery's 7-day time-travel still provides a fallback during the validation window even after dropping backups.
