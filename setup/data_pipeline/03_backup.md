# Step 3 — Backup Before Transforming

The conversion in Step 4 uses `CREATE OR REPLACE TABLE` which overwrites tables. **The `copy_*` backup datasets are the only rollback path** if anything goes wrong. Don't skip this step.

BigQuery's 7-day time-travel can recover from accidents but is awkward to use, and the window expires quickly. An explicit backup dataset is cleaner and lasts as long as you want.

## 1. Create backup datasets

In the BigQuery console, in `som-nero-phi-jonc101`, create two empty datasets:

- `copy_shc_core_YYYY` (e.g., `copy_shc_core_2025`)
- `copy_lpch_core_YYYY` (e.g., `copy_lpch_core_2025`)

Set location to `US`.

## 2. Copy every table to backup

```sql
-- Backup SHC
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.adt` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.adt`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alert` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alert`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alert_history` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alert_history`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alerts_orders` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alerts_orders`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.allergy` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.allergy`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.clinical_doc_meta` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.clinical_doc_meta`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.culture_sensitivity` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.culture_sensitivity`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.demographic` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.demographic`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.dep_map` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.dep_map`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.diagnosis` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.diagnosis`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.drg_code` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.drg_code`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.encounter` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.encounter`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.f_ip_hsp_admission` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.f_ip_hsp_admission`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.family_hx` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.family_hx`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.flowsheet` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.flowsheet`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.geolocation_from_omop` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.geolocation_from_omop`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.ib_messages` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.ib_messages`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.lab_result` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.lab_result`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.lda` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.lda`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.mapped_meds` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.mapped_meds`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.med_orderset` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.med_orderset`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.ndc_code` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.ndc_code`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.new_pats` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.new_pats`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.order_comment` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.order_comment`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.order_med` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.order_med`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.order_proc` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.order_proc`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.pharmacy_mar` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.pharmacy_mar`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.proc_orderset` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.proc_orderset`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.procedure` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.procedure`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.prov_map` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.prov_map`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.smrtdta` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.smrtdta`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.social_hx` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.social_hx`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.treatment_team` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.treatment_team`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.zip` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.zip`;

-- Backup LPCH
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_adt` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_adt`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_alert` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alert`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_alert_history` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alert_history`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_alerts_orders` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alerts_orders`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_allergy` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_allergy`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_alt_com_action` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alt_com_action`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_clinical_doc_meta` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_clinical_doc_meta`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_culture_sensitivity` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_culture_sensitivity`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_demographic` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_demographic`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_dep_map` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_dep_map`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_diagnosis` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_diagnosis`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_drg_code` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_drg_code`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_encounter` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_f_ip_hsp_admission` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_f_ip_hsp_admission`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_family_hx` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_family_hx`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_flowsheet` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_flowsheet`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_geolocation_from_omop` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_geolocation_from_omop`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_ib_messages` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_ib_messages`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_lab_result` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_lab_result`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_lda` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_lda`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_mapped_meds` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_mapped_meds`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_med_orderset` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_med_orderset`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_ndc_code` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_ndc_code`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_new_pats` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_new_pats`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_order_comment` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_comment`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_order_med` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_med`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_order_proc` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_proc`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_order_quest` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_quest`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_patients` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_patients`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_pharmacy_mar` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_pharmacy_mar`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_proc_orderset` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_proc_orderset`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_procedure` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_procedure`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_smrtdta` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_smrtdta`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_social_hx` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_social_hx`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.lpch_treatment_team` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_treatment_team`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.mom_baby` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.mom_baby`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_lpch_core_2025.prov_map` AS SELECT * FROM `som-nero-phi-jonc101.lpch_core_2025.prov_map`;
```

## 3. Verify backup counts

```sql
SELECT COUNT(*) AS table_count
FROM `som-nero-phi-jonc101.copy_shc_core_2025.INFORMATION_SCHEMA.TABLES`;
-- Should equal the table count in shc_core_2025 (34 in 2025)

SELECT COUNT(*) AS table_count
FROM `som-nero-phi-jonc101.copy_lpch_core_2025.INFORMATION_SCHEMA.TABLES`;
-- Should equal the table count in lpch_core_2025 (37 in 2025)
```

**Do not proceed to Step 4 until backup counts match.** If a backup table is missing, the next step would overwrite the original with no recovery.

## Next step

[Step 4 — Apply conversions](./04_apply_conversions.md).
