# Step 1 — Inventory & Plan

Before building anything: verify the source is what you think it is, see what changed, and decide what's going in.

## 1. Verify the source before you trust it

Two checks that take 30 seconds each and prevent expensive mistakes.

### Is the source cumulative or delta-only?

The build uses `CREATE OR REPLACE TABLE ... AS SELECT *` — a full replacement. That's only safe if the source contains the **full history**, not just rows added since the last refresh.

```sql
SELECT
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_encounter`) AS source_rows,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter`) AS current_rows;
```

**Source should be larger than current.** If it's dramatically smaller, the delivery is delta-only and a full rebuild would wipe your history — stop and ask the data team.

Historically the source has always been cumulative, but check every time.

### Did the reported bug fixes actually land?

When the data team reports a fix, verify it across the whole source rather than assuming. Example from the Aug 2026 refresh, where `data_source` was reportedly corrected for LPCH:

```sql
SELECT data_source, COUNT(*) AS n
FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_encounter`
GROUP BY data_source;
```

A single correct value means the fix applies to all rows and a rebuild corrects everything. Two values means they only fixed new rows, and you'll need a patch after the rebuild.

## 2. Compare source tables to the current dataset

### SHC

```sql
WITH source AS (
  SELECT
    table_name AS source_table,
    REGEXP_REPLACE(table_name, r'^shc_', '') AS dest_table
  FROM `som-nero-phi-jonc101-secure.shc_core_updates.INFORMATION_SCHEMA.TABLES`
),
dest AS (
  SELECT table_name AS dest_table
  FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.TABLES`
)
SELECT
  s.source_table,
  COALESCE(s.dest_table, d.dest_table) AS dest_table,
  CASE
    WHEN s.source_table IS NULL THEN 'IN DEST ONLY (no fresh source)'
    WHEN d.dest_table IS NULL THEN 'NEW IN SOURCE'
    ELSE 'BOTH'
  END AS status
FROM source s
FULL OUTER JOIN dest d ON s.dest_table = d.dest_table
ORDER BY status, dest_table;
```

Note: the regex strips the `shc_` prefix for display, which mangles genuinely cross-system tables like `shc_lpch_prov_map`. Check the `source_table` column for the real name.

### LPCH

```sql
WITH source AS (
  SELECT table_name
  FROM `som-nero-phi-jonc101-secure.lpch_core_updates.INFORMATION_SCHEMA.TABLES`
),
dest AS (
  SELECT table_name
  FROM `som-nero-phi-jonc101.lpch_core_2025.INFORMATION_SCHEMA.TABLES`
)
SELECT
  COALESCE(s.table_name, d.table_name) AS table_name,
  CASE
    WHEN s.table_name IS NULL THEN 'IN DEST ONLY (no fresh source)'
    WHEN d.table_name IS NULL THEN 'NEW IN SOURCE'
    ELSE 'BOTH'
  END AS status
FROM source s
FULL OUTER JOIN dest d ON s.table_name = d.table_name
ORDER BY status, table_name;
```

## 3. Triage the results

**`BOTH`** — normal case, straight rebuild.

**`IN DEST ONLY`** — no fresh source. Expect `zip` (static reference, carried forward from 2024). These keep their current values since the build SQL doesn't touch them.

**`NEW IN SOURCE`** — needs a decision for each one:

1. **Check for PHI first.** Look at the schema before anything else:
   ```sql
   SELECT column_name, data_type
   FROM `som-nero-phi-jonc101-secure.shc_core_updates.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name = '<new_table>'
   ORDER BY ordinal_position;
   ```
   Any `mrn`, real names, addresses, or other direct identifiers → excluded, stays in secure. Add it to the exclusion list in the README.

2. **Check for datetime columns.** Any DATETIME column needs a `_utc` counterpart in Step 4.

3. **Check whether it's a counterpart of an existing table.** New SHC tables often mirror LPCH tables already in the pipeline (or vice versa) — those are usually safe to include and should follow the same conversion pattern.

4. **Cross-system bridging tables** (`shc_lpch_*`) have historically been excluded. Confirm with the PI if a new one appears.

Also expect noise in the SHC results: `shc_core_updates` contains some stale `lpch_*` tables. Ignore them — LPCH data comes from `lpch_core_updates`.

## 4. Check for big size changes

Schema changes upstream can dramatically change table sizes. Worth spotting before you load:

```sql
SELECT
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_smrtdta`) AS new_shc_smrtdta,
  (SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.smrtdta`) AS current_shc_smrtdta;
```

In Aug 2026 this caught `smrtdta` growing 77× (6.2M → 479.6M) because the data team removed a filter. Worth knowing before it lands, and worth mentioning in the announcement so researchers aren't surprised by query costs.

## 5. Check the permanent exclusion list

Before building, re-read the exclusions table in the [README](./README.md). Confirm none of them are in your build SQL.

## Next step

[Step 2 — Build raw datasets](./02_build_raw_datasets.md).
