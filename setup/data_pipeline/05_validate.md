# Step 5 — Validate

Run all seven checks before announcing. Each has caught a real problem at least once.

## Check 1 — PHI hasn't leaked into the working project

Most important check. Run it first.

```sql
SELECT table_name
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN ('patients', 'myc_mesg', 'lpch_geolocation_from_omop', 'lpch_prov_map');
```

```sql
SELECT table_name
FROM `som-nero-phi-jonc101.lpch_core_2025.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN ('lpch_myc_mesg', 'shc_lpch_prov_map');
```

Both should return **zero rows**. If a table appears, drop it and check the build SQL.

Also scan for identifier columns anywhere in either dataset:

```sql
SELECT table_name, column_name
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE LOWER(column_name) IN ('mrn', 'ssn', 'patient_name', 'address', 'phone')
UNION ALL
SELECT table_name, column_name
FROM `som-nero-phi-jonc101.lpch_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE LOWER(column_name) IN ('mrn', 'ssn', 'patient_name', 'address', 'phone');
```

Zero rows expected. Anything here is a compliance issue — raise it with the PI immediately rather than quietly dropping the table.

## Check 2 — `_utc` columns present

```sql
SELECT COUNT(*) AS utc_columns
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%_utc';

SELECT COUNT(*) AS utc_columns
FROM `som-nero-phi-jonc101.lpch_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%_utc';
```

**As of Aug 2026: SHC 68, LPCH 69.** If a refresh adds tables with datetime columns, expect the count to rise by that many. A count that *drops* means a conversion was skipped.

To see which table is missing one:

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%_utc'
ORDER BY table_name, column_name;
```

## Check 3 — Text columns stayed STRING

The check that catches the auto-detection regression.

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'lab_result'
  AND column_name IN ('ord_value', 'reference_low', 'reference_high',
                      'extended_value_comment', 'extended_comp_comment')
ORDER BY column_name;
```

All five must be `STRING`.

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.lpch_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE (table_name = 'lpch_lab_result' AND column_name = 'ord_value')
   OR (table_name = 'lpch_flowsheet' AND column_name = 'meas_value')
   OR (table_name = 'lpch_allergy' AND column_name = 'reaction')
   OR (table_name = 'lpch_order_comment' AND column_name = 'ordering_comment')
ORDER BY table_name, column_name;
```

All four must be `STRING`. (These four were typed DATE in `lpch_core_2024` due to the auto-detection bug — do not replicate that.)

Sample the values to confirm they look like text:

```sql
SELECT DISTINCT ord_value
FROM `som-nero-phi-jonc101.shc_core_2025.lab_result`
WHERE ord_value IS NOT NULL
LIMIT 20;
```

## Check 4 — Reported bug fixes landed

Whatever the data team said they fixed, verify. Example from Aug 2026:

```sql
SELECT DISTINCT data_source
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter`;
```

Expected `CLARITY_LPCH` only. If both old and new values appear, only new rows were fixed.

## Check 5 — Flowsheet numerical extraction

```sql
SELECT column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'flowsheet' AND column_name LIKE '%numerical_val%'
ORDER BY column_name;
```

Four rows, all `FLOAT64`. `STRING` means the `SAFE_CAST` was missed. Missing entirely means the extraction wasn't run after the rebuild.

Spot-check:

```sql
SELECT meas_value, numerical_val_1, numerical_val_2
FROM `som-nero-phi-jonc101.shc_core_2025.flowsheet`
WHERE meas_value LIKE '%/%' AND numerical_val_1 IS NOT NULL
LIMIT 10;
```

Blood-pressure values should split into two numbers. Repeat for `lpch_flowsheet`.

## Check 6 — Spot-check a converted DATETIME

```sql
SELECT hosp_admsn_time_jittered, hosp_admsn_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.encounter`
WHERE hosp_admsn_time_jittered IS NOT NULL
LIMIT 10;
```

The `_utc` value should be 7 or 8 hours ahead (depending on daylight saving).

## Check 7 — Growth is positive and plausible

Compare against the backup, which holds the pre-refresh state.

```sql
SELECT 'encounter' AS t,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_2025.encounter`) AS before,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.encounter`) AS after
UNION ALL SELECT 'order_proc',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_2025.order_proc`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.order_proc`)
UNION ALL SELECT 'lab_result',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_2025.lab_result`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.lab_result`)
UNION ALL SELECT 'flowsheet',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_2025.flowsheet`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.flowsheet`)
UNION ALL SELECT 'order_med',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_2025.order_med`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.order_med`)
UNION ALL SELECT 'diagnosis',
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.copy_shc_core_2025.diagnosis`),
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.diagnosis`)
ORDER BY t;
```

Same for LPCH with `copy_lpch_core_2025` and the `lpch_*` table names.

**Expected growth depends on the interval:**

| Interval | Expected growth on clinical tables |
|---|---|
| 4–6 week refresh | +3% to +5% |
| Full year | +10% to +25% |

**Any table that shrank is a red flag** — cumulative data should never lose rows. Don't drop the backups; investigate.

Tables affected by an upstream filter change (e.g. `smrtdta` in Aug 2026) will be wildly outside these ranges. That's expected when you know about it from Step 1, and should be noted in the changelog rather than treated as an anomaly.

## If a check fails

| Symptom | Fix |
|---|---|
| Missing `_utc` on one table | Re-run that table's Step 4 statement |
| Text column typed as DATE/DATETIME | Restore that table from backup, re-run its conversion |
| `numerical_val_*` missing or STRING | Re-run flowsheet extraction with `SAFE_CAST` |
| Row count shrank | Restore from backup, check whether the source was delta-only |
| Table missing entirely | Re-run its Step 2 build statement, then its Step 4 conversion |
| PHI table present | Drop it, notify the PI, add to the README exclusion list |

Restore a single table:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.<table>` AS
SELECT * FROM `som-nero-phi-jonc101.copy_shc_core_2025.<table>`;
```

Then re-run its Step 4 conversion — restoring reverts to the pre-conversion state.

## Next step

[Step 6 — Announce & clean up](./06_announce_and_cleanup.md).
