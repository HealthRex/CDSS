# Refresh Changelog

A record of each STAAR data refresh — what was delivered, what changed, and anything surprising. Add an entry every time you run the pipeline.

---

## 2026-08-24 — FY26 refresh #2

**Clarity data cut:** Aug 9, 2026
**Delivered by:** Shikha Kothari (Research Technology)
**Loaded into:** `shc_core_2025`, `lpch_core_2025` (in-place rebuild)

### Changes from the data team

- **LPCH `data_source` bug fixed.** Previously populated with `"CLARITY SHC"` for LPCH tables; now correctly `"CLARITY_LPCH"` (note: underscore, not space as described in the delivery email). Verified across all 42.4M rows of `lpch_encounter`. Any lab code filtering on the old string needs updating.
- **SmartData filter removed.** The data team had been filtering `smrtdta` to a single element. Because the lab didn't respond to their request for specific element IDs, they removed the filter entirely. Result: `shc_smrtdta` went 6.2M → 479.6M rows; `lpch_smrtdta` went from empty → 102.5M rows. Nick Marshall is reviewing which elements the lab actually needs; may re-filter upstream or via a view later.
- **New SmartData fields added:** `smartdata_element_description` (from `clarity_concept.name`), `smartdata_element_abbreviation` (from `clarity_concept.abbreviation`), plus several other Clarity-derived fields. Total `smrtdta` schema is now 23 columns.
- **Deid notes still pending** — data team expects them by end of Aug 2026.

### New tables added to the working project

| Table | Dataset | Notes |
|---|---|---|
| `alt_com_action` | `shc_core_2025` | SHC counterpart of `lpch_alt_com_action`; has `contact_date_jittered` → needs `_utc` |
| `order_quest` | `shc_core_2025` | SHC counterpart of `lpch_order_quest`; has `ord_quest_date_jittered` → needs `_utc` |

### New tables excluded

| Table | Reason |
|---|---|
| `shc_patients` | Contains `mrn` — direct PHI. Stays in secure. |
| `shc_myc_mesg` | MyChart messages, same treatment as `lpch_myc_mesg` (per Jonathan) |
| `shc_lpch_geolocation_from_omop` | Stays in secure (per Jonathan) |

### Growth (vs. pre-refresh state)

| Table | SHC | LPCH |
|---|---|---|
| encounter | +3.3% | +4.0% |
| order_proc | +4.2% | +4.6% |
| lab_result | +3.1% | +4.1% |
| flowsheet | +3.6% | +3.9% |
| order_med | +3.7% | +3.8% |
| diagnosis | +4.2% | +3.7% |

`smrtdta` excluded from the above — its jump is the filter removal, not organic growth.

### Open items

- **Which `starr_map` version is current?** The delivery email referenced `shc_map_2026-08-09` / `lpch_map_2026-08-09`, but `shc_map_2026_08_18` / `lpch_map_2026_08_18` also exist (created Aug 21, hyphens changed to underscores). Asked Shikha to confirm.
- **`lpch_patients` may contain `mrn`.** It has been in `lpch_core_2025` since the May build. Needs checking; if it has MRNs, that's PHI in the non-secure project and needs to be removed.
- **Nick to specify SmartData element IDs** so the data team can re-filter.

### Process notes

- Refresh cadence confirmed at **4–6 weeks** for FY27 (Priya Desai, Aug 2026). Every-2-weeks was declined because deid for notes is still manual.
- Source verified cumulative before rebuilding (source row count > current row count), so `CREATE OR REPLACE` was safe.

---

## 2026-05-12 — FY26 refresh #1 (initial 2025 build)

**Clarity data cut:** ~Feb–Apr 2026
**Loaded into:** `shc_core_2025`, `lpch_core_2025` (new datasets)

### What happened

First build of the 2025 datasets. Also the refresh where the conversion process was rewritten.

### New tables (vs. 2024)

- `lpch_alt_com_action`, `lpch_mapped_meds`, `lpch_order_quest`, `mom_baby` in `lpch_core_2025`
- `shc_lpch_prov_map` appeared in the source but was **not** copied (decision: skip)

### Incident — auto-detection destroyed text columns

An automated conversion script flagged any STRING column with at least one date-parseable value as a datetime column and converted it. This destroyed `lab_result.ord_value` (lab result values like `"5.2"`, `"negative"`) by turning them into mostly-NULL DATETIMEs.

The same bug appears to have affected the 2024 build: `lpch_allergy.reaction`, `lpch_flowsheet.meas_value`, and `lpch_order_comment.ordering_comment` are all typed DATE in `lpch_core_2024` but are text fields. These were **not** replicated in 2025.

**Resolution:** dropped and rebuilt both datasets from source, then applied conversions using explicit per-table column lists derived from the 2024 schema. Auto-detection is now prohibited — see README.

### Other findings

- The secure project now delivers properly-typed DATETIME columns. No `PARSE_DATETIME` needed; the conversion is just adding `_utc` columns.
- `flowsheet` numerical extraction (`numerical_val_1`–`4`) had been missing from the pipeline docs entirely. Added.
- Backups were skipped on the first attempt (the `copy_*` datasets were never created), which meant no rollback when the bug was found. Backups are now a mandatory gate before Step 4.

### Growth (vs. 2024)

| Table | SHC | LPCH |
|---|---|---|
| encounter | +13% | +11% |
| order_proc | +16% | +12% |
| lab_result | +12% | +9% |
