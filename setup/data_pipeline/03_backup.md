# Step 3 — Backup Before Transforming

⚠️ **This is a mandatory gate.** Both the build (Step 2) and the conversions (Step 4) use `CREATE OR REPLACE TABLE`, which overwrites with no rollback. The `copy_*` datasets are the only recovery path beyond BigQuery's 7-day time travel.

In May 2026 this step was skipped and a conversion bug destroyed text columns with no way back — the datasets had to be rebuilt from source. Don't skip it.

## When to run this

**For a mid-year refresh into an existing dataset:** back up *before* Step 2, since the build itself overwrites live tables.

**For a brand-new yearly dataset:** back up after Step 2, before Step 4. There's nothing to lose until the raw build is done.

## 1. Delete stale backups

If `copy_*` datasets exist from a previous refresh, they hold outdated data and will be misleading. Drop them first.

```sql
SELECT schema_name, creation_time
FROM `som-nero-phi-jonc101.INFORMATION_SCHEMA.SCHEMATA`
WHERE schema_name LIKE 'copy_%';
```

```sql
DROP SCHEMA IF EXISTS `som-nero-phi-jonc101.copy_shc_core_2025` CASCADE;
DROP SCHEMA IF EXISTS `som-nero-phi-jonc101.copy_lpch_core_2025` CASCADE;
```

## 2. Create empty backup datasets

```sql
CREATE SCHEMA IF NOT EXISTS `som-nero-phi-jonc101.copy_shc_core_2025`
OPTIONS (location = 'US');

CREATE SCHEMA IF NOT EXISTS `som-nero-phi-jonc101.copy_lpch_core_2025`
OPTIONS (location = 'US');
```

## 3. Copy tables

Note: this list reflects the Aug 2026 table set. If the current dataset has tables not listed here, add them — a missing backup table means no rollback for that table.

### SHC

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.adt` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.adt`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alert` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alert`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alert_history` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alert_history`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alerts_orders` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alerts_orders`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.allergy` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.allergy`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.alt_com_action` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.alt_com_action`;
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
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.order_quest` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.order_quest`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.pharmacy_mar` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.pharmacy_mar`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.proc_orderset` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.proc_orderset`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.procedure` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.procedure`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.prov_map` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.prov_map`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.smrtdta` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.smrtdta`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.social_hx` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.social_hx`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.treatment_team` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.treatment_team`;
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.copy_shc_core_2025.zip` AS SELECT * FROM `som-nero-phi-jonc101.shc_core_2025.zip`;
```

### LPCH

```sql
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

## 4. Verify — mandatory gate

```sql
SELECT COUNT(*) AS n FROM `som-nero-phi-jonc101.copy_shc_core_2025.INFORMATION_SCHEMA.TABLES`;
SELECT COUNT(*) AS n FROM `som-nero-phi-jonc101.copy_lpch_core_2025.INFORMATION_SCHEMA.TABLES`;
```

Compare against the source dataset counts:

```sql
SELECT COUNT(*) AS n FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.TABLES`;
SELECT COUNT(*) AS n FROM `som-nero-phi-jonc101.lpch_core_2025.INFORMATION_SCHEMA.TABLES`;
```

**Counts must match. Do not proceed until they do.** As of Aug 2026: SHC 36, LPCH 37.

## Restoring from backup

Single table:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.<table>` AS
SELECT * FROM `som-nero-phi-jonc101.copy_shc_core_2025.<table>`;
```

Note that restoring puts the table back to its pre-conversion state — you'll need to re-run the Step 4 conversions (including flowsheet extraction) for that table.

## Next step

[Step 4 — Apply conversions](./04_apply_conversions.md).
