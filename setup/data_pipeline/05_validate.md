# Step 5 — Validate

After Step 4, run these checks before announcing the dataset to the lab. Replace `YYYY` with the year you're processing.

## Check 1 — `_utc` columns exist

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%_utc'
ORDER BY table_name, column_name;
```

The count should match (or roughly match, if there are new tables) the previous year's count. In 2025: 66 for SHC, 69 for LPCH.

Run the same against `lpch_core_YYYY`.

## Check 2 — Confirm text columns stayed STRING

This is the check that would have caught the auto-detection bug. For SHC:

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'lab_result'
  AND column_name IN ('ord_value', 'reference_low', 'reference_high',
                      'extended_value_comment', 'extended_comp_comment')
ORDER BY column_name;
```

All five should be `STRING`. For LPCH:

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.lpch_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE (table_name = 'lpch_lab_result' AND column_name = 'ord_value')
   OR (table_name = 'lpch_flowsheet' AND column_name = 'meas_value')
   OR (table_name = 'lpch_allergy' AND column_name = 'reaction')
   OR (table_name = 'lpch_order_comment' AND column_name = 'ordering_comment')
ORDER BY table_name, column_name;
```

All four should be `STRING`. If any are DATE/DATETIME/TIMESTAMP, **stop and restore from backup** — something converted a text column.

## Check 3 — Spot-check a converted DATETIME

```sql
SELECT
  hosp_admsn_time_jittered,
  hosp_admsn_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_YYYY.encounter`
WHERE hosp_admsn_time_jittered IS NOT NULL
LIMIT 10;
```

The two columns should show times that differ by 7 or 8 hours (LA → UTC, depending on daylight saving). Both should display as proper datetime values, not as quoted strings.

## Check 4 — Row count growth makes sense

Compare 2025 to 2024 on the high-volume clinical tables:

```sql
SELECT 'encounter' AS t,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2024.encounter`) AS shc_2024,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.encounter`) AS shc_2025,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2024.lpch_encounter`) AS lpch_2024,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter`) AS lpch_2025
UNION ALL
SELECT 'order_proc',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2024.order_proc`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.order_proc`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2024.lpch_order_proc`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_proc`)
UNION ALL
SELECT 'lab_result',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2024.lab_result`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.lab_result`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2024.lpch_lab_result`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_lab_result`);
```

2025 should be larger than 2024 (cumulative data) by roughly 10–25%. If a table shrank or growth is dramatically outside that range, investigate.

For reference, 2025 growth was:

| Table | SHC growth | LPCH growth |
|---|---|---|
| `encounter` | +13% | +11% |
| `order_proc` | +16% | +12% |
| `lab_result` | +12% | +9% |

## Check 5 — Row counts unchanged by conversion

The conversion in Step 4 rewrites columns, not rows, so row counts should match the backup exactly:

```sql
SELECT 'encounter' AS t, COUNT(*) AS backup_n FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.encounter`
UNION ALL SELECT 'encounter (converted)', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.encounter`
UNION ALL SELECT 'order_proc', COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.order_proc`
UNION ALL SELECT 'order_proc (converted)', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.order_proc`
UNION ALL SELECT 'lab_result', COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.lab_result`
UNION ALL SELECT 'lab_result (converted)', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.lab_result`;
```

Each pair should be identical.

## Check 6 — Flowsheet numerical extraction worked

```sql
-- Confirm numerical_val columns exist and are FLOAT64
SELECT column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_YYYY.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'flowsheet'
  AND column_name LIKE '%numerical_val%'
ORDER BY column_name;
```

Expect 4 rows, all type `FLOAT64`. If type is `STRING`, the `SAFE_CAST` was missed in Step 4 — restore from backup and re-run.

```sql
-- Spot-check: some real measurements should produce numeric values
SELECT meas_value, numerical_val_1, numerical_val_2
FROM `som-nero-phi-jonc101.shc_core_YYYY.flowsheet`
WHERE meas_value LIKE '%/%'
  AND numerical_val_1 IS NOT NULL
LIMIT 10;
```

Blood-pressure-style values like `"120/80"` should split into `120` and `80`. Repeat for `lpch_flowsheet`.

## What to do if a check fails

- **`_utc` column missing on a table** → re-run the conversion query for just that table from Step 4
- **A text column is wrongly typed as DATE/DATETIME** → restore the affected table from `copy_*` backup, then re-run the conversion query for just that table
- **Row count regression** → likely a conversion query truncated something; restore from backup
- **A whole table missing from the dataset** → re-run the Step 2 build query for that table

Restore a single table from backup:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_YYYY.<table>` AS
SELECT * FROM `som-nero-phi-jonc101.copy_shc_core_YYYY.<table>`;
```

## Next step

[Step 6 — Announce & clean up](./06_announce_and_cleanup.md).
