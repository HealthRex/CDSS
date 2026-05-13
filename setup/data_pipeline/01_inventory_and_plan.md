# Step 1 — Inventory & Plan

Before building anything, take stock of what's in the source datasets and decide what's going into this year's update.

## 1. List source tables

In the BigQuery console, switch to project `som-nero-phi-jonc101-secure` and expand:

- `shc_core_updates` (adult tables, prefixed `shc_*`)
- `lpch_core_updates` (pediatric tables, prefixed `lpch_*`)

Or programmatically:

```sql
SELECT table_name, creation_time, last_modified_time
FROM `som-nero-phi-jonc101-secure.shc_core_updates.INFORMATION_SCHEMA.TABLES`
ORDER BY table_name;
```

Same for `lpch_core_updates`.

## 2. Compare to last year's dataset

Run this to see what was in `shc_core_YYYY-1` (e.g., `shc_core_2024`):

```sql
SELECT table_name
FROM `som-nero-phi-jonc101.shc_core_2024.INFORMATION_SCHEMA.TABLES`
ORDER BY table_name;
```

Compare the two lists. Categorize each table:

- **In both** → carry forward as-is
- **In source only** → new table this year, decide whether to include
- **In last year only** → no fresh data, decide whether to carry forward last year's version (e.g., static reference tables like `zip`)

## 3. Note exclusions and decisions

Standing exclusions:

- **`lpch_myc_mesg`** — never copied. Stays in the secure project.

Per-year decisions to document:

- New tables in source that aren't in last year's dataset (e.g., in 2025: `lpch_alt_com_action`, `lpch_mapped_meds`, `lpch_order_quest`, `mom_baby`)
- Whether `shc_lpch_prov_map` or other bridging tables should be included
- Any research-derived tables in the previous year's dataset that should NOT be copied to the new year (e.g., `ot_real_phase0_*` tables in 2024 — these were research outputs, not raw data, and don't belong in the yearly snapshot)

## 4. Naming conventions

When building the destination tables:

- **SHC**: drop the `shc_` prefix. Source `shc_encounter` → destination `encounter`.
- **LPCH**: keep the `lpch_` prefix. Source `lpch_encounter` → destination `lpch_encounter`.
- A few tables in `shc_core_updates` have no `shc_` prefix in the source (e.g., `geolocation_from_omop`, `prov_map`). Use the source name as-is.

## Next step

Once you have the plan, proceed to [Step 2 — Build raw datasets](./02_build_raw_datasets.md).
