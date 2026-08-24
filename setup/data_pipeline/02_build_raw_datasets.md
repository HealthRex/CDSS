# Step 2 — Build Raw Datasets

Copy raw tables from `som-nero-phi-jonc101-secure` into the working project.

⚠️ **If the destination dataset already exists and is in use, do Step 3 (backup) first.** Mid-year refreshes are destructive rebuilds. The SQL below overwrites tables researchers are actively querying.

## 1. Create destination datasets (new year only)

If starting a new yearly dataset, create it in the BigQuery console with location `US`. For a mid-year refresh into an existing dataset, skip this.

## 2. SHC build

Current as of the Aug 2026 refresh — 36 tables.

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.adt` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_adt`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alert` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_alert`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alert_history` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_alert_history`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alerts_orders` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_alerts_orders`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.allergy` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_allergy`;

-- added Aug 2026
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alt_com_action` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_alt_com_action`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.clinical_doc_meta` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_clinical_doc_meta`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.culture_sensitivity` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_culture_sensitivity`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.demographic` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_demographic`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.dep_map` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_dep_map`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.diagnosis` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_diagnosis`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.drg_code` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_drg_code`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.encounter` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_encounter`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.f_ip_hsp_admission` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_f_ip_hsp_admission`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.family_hx` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_family_hx`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.flowsheet` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_flowsheet`;

-- source has NO shc_ prefix
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.geolocation_from_omop` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.geolocation_from_omop`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.ib_messages` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_ib_messages`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.lab_result` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_lab_result`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.lda` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_lda`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.mapped_meds` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_mapped_meds`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.med_orderset` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_med_orderset`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.ndc_code` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_ndc_code`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.new_pats` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_new_pats`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_comment` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_order_comment`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_med` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_order_med`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_proc` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_order_proc`;

-- added Aug 2026
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_quest` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_order_quest`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.pharmacy_mar` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_pharmacy_mar`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.proc_orderset` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_proc_orderset`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.procedure` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_procedure`;

-- source has NO shc_ prefix
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.prov_map` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.prov_map`;

-- NOTE: 479.6M rows as of Aug 2026 (was 6.2M) — unfiltered SmartData elements
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.smrtdta` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_smrtdta`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.social_hx` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_social_hx`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.treatment_team` AS
SELECT * FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_treatment_team`;

-- zip: no fresh source. Leave existing table untouched.
-- If building a brand-new yearly dataset, carry it forward:
--   CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_YYYY.zip` AS
--   SELECT * FROM `som-nero-phi-jonc101.shc_core_YYYY-1.zip`;

-- EXCLUDED — stay in secure (see README):
--   shc_patients (contains mrn)
--   shc_myc_mesg
--   shc_lpch_geolocation_from_omop
--   shc_lpch_prov_map
```

## 3. LPCH build

37 tables.

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_adt` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_adt`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alert` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_alert`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alert_history` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_alert_history`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alerts_orders` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_alerts_orders`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_allergy` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_allergy`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alt_com_action` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_alt_com_action`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_clinical_doc_meta` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_clinical_doc_meta`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_culture_sensitivity` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_culture_sensitivity`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_demographic` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_demographic`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_dep_map` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_dep_map`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_diagnosis` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_diagnosis`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_drg_code` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_drg_code`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_encounter`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_f_ip_hsp_admission` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_f_ip_hsp_admission`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_family_hx` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_family_hx`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_flowsheet` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_flowsheet`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_geolocation_from_omop` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_geolocation_from_omop`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_ib_messages` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_ib_messages`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_lab_result` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_lab_result`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_lda` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_lda`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_mapped_meds` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_mapped_meds`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_med_orderset` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_med_orderset`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_ndc_code` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_ndc_code`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_new_pats` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_new_pats`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_comment` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_order_comment`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_med` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_order_med`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_proc` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_order_proc`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_quest` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_order_quest`;

-- NOTE: check for mrn column before including (see README exclusions)
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_patients` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_patients`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_pharmacy_mar` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_pharmacy_mar`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_proc_orderset` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_proc_orderset`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_procedure` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_procedure`;

-- NOTE: 102.5M rows as of Aug 2026 (was empty) — unfiltered SmartData elements
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_smrtdta` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_smrtdta`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_social_hx` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_social_hx`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_treatment_team` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.lpch_treatment_team`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.mom_baby` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.mom_baby`;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.prov_map` AS
SELECT * FROM `som-nero-phi-jonc101-secure.lpch_core_updates.prov_map`;

-- EXCLUDED — stay in secure (see README):
--   lpch_myc_mesg
--   shc_lpch_prov_map
```

## 4. Quick check

```sql
SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.encounter`;
SELECT COUNT(*) FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter`;
```

Full growth validation comes in Step 5.

## Common issues

- **`Not found: Table ...`** — source name is wrong. Check the actual names in `shc_core_updates` / `lpch_core_updates`. Watch for the tables with no prefix.
- **Permission denied** — need Data Viewer on secure, Data Editor on working.
- **Wrong location** — destination dataset must be in the same region as the source (`US`).

## Next step

[Step 4 — Apply conversions](./04_apply_conversions.md) (Step 3 backup should already be done).
