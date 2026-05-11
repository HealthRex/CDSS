# Step 1 — Build the yearly dataset

Copy raw tables from `som-nero-phi-jonc101-secure` into new yearly datasets in `som-nero-phi-jonc101`.

## Prerequisites

- Read access to `som-nero-phi-jonc101-secure`
- Write access to `som-nero-phi-jonc101`
- BigQuery console access

## Procedure

### 1. Inventory the source

Before building anything, list what's in the source datasets to spot new tables, removed tables, and anything unexpected.

In the BigQuery console, switch to project `som-nero-phi-jonc101-secure` and expand:

- `shc_core_updates` (adult tables, prefixed `shc_*`)
- `lpch_core_updates` (pediatric tables, prefixed `lpch_*`)

Compare against the previous year's datasets (`shc_core_YYYY-1`, `lpch_core_YYYY-1`):

- **Tables in source but not in last year's dataset** → new tables. Decide whether to include.
- **Tables in last year's dataset but not in source** → may need to carry forward from last year, or skip.
- **`lpch_myc_mesg`** → always exclude (stays in secure project).

### 2. Create destination datasets

In `som-nero-phi-jonc101`, create:

- `shc_core_YYYY` (e.g., `shc_core_2025`)
- `lpch_core_YYYY` (e.g., `lpch_core_2025`)

Set location to `US` (must match source).

### 3. Run the build SQL

For each table, run a `CREATE OR REPLACE TABLE ... AS SELECT *` from the corresponding source table. Pattern:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_YYYY.<table>` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_<table>`;
```

Notes on naming:

- **SHC destination tables drop the `shc_` prefix.** Source `shc_encounter` → destination `encounter`.
- **LPCH destination tables keep the `lpch_` prefix.** Source `lpch_encounter` → destination `lpch_encounter`.
- A few tables in `shc_core_updates` have no `shc_` prefix in the source (e.g., `geolocation_from_omop`, `prov_map`) — adjust the `FROM` clause accordingly.

### 4. Validate row counts

After the build, run a count query to confirm every table populated:

```sql
SELECT 'encounter' AS t, COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.encounter`
UNION ALL SELECT 'order_proc', COUNT(*) FROM `som-nero-phi-jonc101.shc_core_YYYY.order_proc`
-- ... etc for every table
ORDER BY t;
```

Zero counts on a clinical table indicate a failed build. Reference tables (`zip`, `prov_map`) may have stable counts year over year; cumulative tables (`encounter`, `order_proc`, `lab_result`) should grow ~15–25% from the previous year.

## Common issues

- **`Not found: Table ...`** — the source name in the `FROM` clause is wrong. Check `shc_core_updates` in the BigQuery console for actual names.
- **Permission denied** — check IAM on both projects (Data Viewer on secure, Data Editor on working).
- **Wrong location** — destination dataset must be in the same region as the source (`US`).

## Next step

Once all tables are built and row counts look correct, proceed to [Step 2 — Apply conversions](./02_apply_conversions.md).
