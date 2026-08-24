# Step 4 — Apply Conversions

Two transformations after the raw build:

1. **Add `_utc` columns** for every DATETIME column (source times are `America/Los_Angeles`)
2. **Extract numerical values** from `flowsheet.meas_value` into FLOAT64 columns

⚠️ Both use `CREATE OR REPLACE TABLE`. [Step 3 backup](./03_backup.md) must be done first.

## Why explicit column lists, never auto-detection

The column lists below were derived by querying `INFORMATION_SCHEMA.COLUMNS` on the previous known-good dataset. **Never auto-detect which STRING columns are dates.**

A previous version of this pipeline used a script that flagged any STRING column with at least one date-parseable value as a datetime column, then converted it. `lab_result.ord_value` holds lab result text (`"5.2"`, `"negative"`, `"<0.1"`), a few of which parse as dates — so the whole column was converted to DATETIME and the text was destroyed. The same bug hit `lpch_allergy.reaction`, `lpch_flowsheet.meas_value`, and `lpch_order_comment.ordering_comment` in the 2024 build.

## Deriving the column list for a new year

If a table's schema has changed or you're starting a new yearly dataset:

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE data_type IN ('DATETIME', 'DATE', 'TIMESTAMP')
ORDER BY table_name, ordinal_position;
```

DATETIME columns need `_utc`. DATE columns do not (no time component). Existing TIMESTAMP columns are already-created `_utc` columns.

Also confirm nothing regressed to STRING:

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name LIKE '%date%' OR column_name LIKE '%time%'
ORDER BY table_name, ordinal_position;
```

## 1. SHC `_utc` conversions

```sql
-- adt
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.adt` AS
SELECT *,
  TIMESTAMP(effective_time_jittered, "America/Los_Angeles") AS effective_time_jittered_utc,
  TIMESTAMP(event_time_jittered, "America/Los_Angeles") AS event_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.adt`;

-- alert
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alert` AS
SELECT *,
  TIMESTAMP(update_date_jittered, "America/Los_Angeles") AS update_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.alert`;

-- alert_history
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alert_history` AS
SELECT *,
  TIMESTAMP(update_date_jittered, "America/Los_Angeles") AS update_date_jittered_utc,
  TIMESTAMP(contact_date, "America/Los_Angeles") AS contact_date_utc,
  TIMESTAMP(alt_action_inst, "America/Los_Angeles") AS alt_action_inst_utc
FROM `som-nero-phi-jonc101.shc_core_2025.alert_history`;

-- alerts_orders
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alerts_orders` AS
SELECT *,
  TIMESTAMP(update_date_jittered, "America/Los_Angeles") AS update_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.alerts_orders`;

-- allergy
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.allergy` AS
SELECT *,
  TIMESTAMP(date_noted_jittered, "America/Los_Angeles") AS date_noted_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.allergy`;

-- alt_com_action (added Aug 2026)
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.alt_com_action` AS
SELECT *,
  TIMESTAMP(contact_date_jittered, "America/Los_Angeles") AS contact_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.alt_com_action`;

-- clinical_doc_meta
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.clinical_doc_meta` AS
SELECT *,
  TIMESTAMP(filing_date_jittered, "America/Los_Angeles") AS filing_date_jittered_utc,
  TIMESTAMP(note_date_jittered, "America/Los_Angeles") AS note_date_jittered_utc,
  TIMESTAMP(activity_date_jittered, "America/Los_Angeles") AS activity_date_jittered_utc,
  TIMESTAMP(effective_time_jittered, "America/Los_Angeles") AS effective_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.clinical_doc_meta`;

-- culture_sensitivity
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.culture_sensitivity` AS
SELECT *,
  TIMESTAMP(order_time_jittered, "America/Los_Angeles") AS order_time_jittered_utc,
  TIMESTAMP(result_time_jittered, "America/Los_Angeles") AS result_time_jittered_utc,
  TIMESTAMP(sens_obs_inst_tm_jittered, "America/Los_Angeles") AS sens_obs_inst_tm_jittered_utc,
  TIMESTAMP(sens_anl_inst_tm_jittered, "America/Los_Angeles") AS sens_anl_inst_tm_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.culture_sensitivity`;

-- demographic
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.demographic` AS
SELECT *,
  TIMESTAMP(birth_date_jittered, "America/Los_Angeles") AS birth_date_jittered_utc,
  TIMESTAMP(death_date_jittered, "America/Los_Angeles") AS death_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.demographic`;

-- diagnosis
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.diagnosis` AS
SELECT *,
  TIMESTAMP(start_date_jittered, "America/Los_Angeles") AS start_date_jittered_utc,
  TIMESTAMP(noted_date_jittered, "America/Los_Angeles") AS noted_date_jittered_utc,
  TIMESTAMP(hx_date_of_entry_jittered, "America/Los_Angeles") AS hx_date_of_entry_jittered_utc,
  TIMESTAMP(resolved_date_jittered, "America/Los_Angeles") AS resolved_date_jittered_utc,
  TIMESTAMP(end_date_jittered, "America/Los_Angeles") AS end_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.diagnosis`;

-- encounter
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.encounter` AS
SELECT *,
  TIMESTAMP(contact_date_jittered, "America/Los_Angeles") AS contact_date_jittered_utc,
  TIMESTAMP(adt_arrival_time_jittered, "America/Los_Angeles") AS adt_arrival_time_jittered_utc,
  TIMESTAMP(hosp_admsn_time_jittered, "America/Los_Angeles") AS hosp_admsn_time_jittered_utc,
  TIMESTAMP(hosp_disch_time_jittered, "America/Los_Angeles") AS hosp_disch_time_jittered_utc,
  TIMESTAMP(appt_time_jittered, "America/Los_Angeles") AS appt_time_jittered_utc,
  TIMESTAMP(appt_when_jittered, "America/Los_Angeles") AS appt_when_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.encounter`;

-- f_ip_hsp_admission
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.f_ip_hsp_admission` AS
SELECT *,
  TIMESTAMP(hosp_adm_date_jittered, "America/Los_Angeles") AS hosp_adm_date_jittered_utc,
  TIMESTAMP(hosp_disch_date_jittered, "America/Los_Angeles") AS hosp_disch_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.f_ip_hsp_admission`;

-- family_hx: DATE only, no UTC needed — skip

-- flowsheet
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.flowsheet` AS
SELECT *,
  TIMESTAMP(recorded_time_jittered, "America/Los_Angeles") AS recorded_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.flowsheet`;

-- ib_messages
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.ib_messages` AS
SELECT *,
  TIMESTAMP(create_time_jittered, "America/Los_Angeles") AS create_time_jittered_utc,
  TIMESTAMP(send_on_jittered, "America/Los_Angeles") AS send_on_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.ib_messages`;

-- lab_result
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.lab_result` AS
SELECT *,
  TIMESTAMP(order_time_jittered, "America/Los_Angeles") AS order_time_jittered_utc,
  TIMESTAMP(taken_time_jittered, "America/Los_Angeles") AS taken_time_jittered_utc,
  TIMESTAMP(result_time_jittered, "America/Los_Angeles") AS result_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.lab_result`;

-- lda
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.lda` AS
SELECT *,
  TIMESTAMP(placement_instant_jittered, "America/Los_Angeles") AS placement_instant_jittered_utc,
  TIMESTAMP(removal_instant_jittered, "America/Los_Angeles") AS removal_instant_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.lda`;

-- order_comment
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_comment` AS
SELECT *,
  TIMESTAMP(order_inst_jittered, "America/Los_Angeles") AS order_inst_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.order_comment`;

-- order_med
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_med` AS
SELECT *,
  TIMESTAMP(ordering_date_jittered, "America/Los_Angeles") AS ordering_date_jittered_utc,
  TIMESTAMP(start_date_jittered, "America/Los_Angeles") AS start_date_jittered_utc,
  TIMESTAMP(end_date_jittered, "America/Los_Angeles") AS end_date_jittered_utc,
  TIMESTAMP(order_start_time_jittered, "America/Los_Angeles") AS order_start_time_jittered_utc,
  TIMESTAMP(order_end_time_jittered, "America/Los_Angeles") AS order_end_time_jittered_utc,
  TIMESTAMP(order_inst_jittered, "America/Los_Angeles") AS order_inst_jittered_utc,
  TIMESTAMP(discon_time_jittered, "America/Los_Angeles") AS discon_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.order_med`;

-- order_proc
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_proc` AS
SELECT *,
  TIMESTAMP(ordering_date_jittered, "America/Los_Angeles") AS ordering_date_jittered_utc,
  TIMESTAMP(standing_exp_date_jittered, "America/Los_Angeles") AS standing_exp_date_jittered_utc,
  TIMESTAMP(proc_bgn_time_jittered, "America/Los_Angeles") AS proc_bgn_time_jittered_utc,
  TIMESTAMP(proc_end_time_jittered, "America/Los_Angeles") AS proc_end_time_jittered_utc,
  TIMESTAMP(order_inst_jittered, "America/Los_Angeles") AS order_inst_jittered_utc,
  TIMESTAMP(instantiated_time_jittered, "America/Los_Angeles") AS instantiated_time_jittered_utc,
  TIMESTAMP(order_time_jittered, "America/Los_Angeles") AS order_time_jittered_utc,
  TIMESTAMP(result_time_jittered, "America/Los_Angeles") AS result_time_jittered_utc,
  TIMESTAMP(proc_start_time_jittered, "America/Los_Angeles") AS proc_start_time_jittered_utc,
  TIMESTAMP(proc_date_jittered, "America/Los_Angeles") AS proc_date_jittered_utc,
  TIMESTAMP(last_stand_perf_dt_jittered, "America/Los_Angeles") AS last_stand_perf_dt_jittered_utc,
  TIMESTAMP(last_stand_perf_tm_jittered, "America/Los_Angeles") AS last_stand_perf_tm_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.order_proc`;

-- order_quest (added Aug 2026)
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.order_quest` AS
SELECT *,
  TIMESTAMP(ord_quest_date_jittered, "America/Los_Angeles") AS ord_quest_date_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.order_quest`;

-- pharmacy_mar
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.pharmacy_mar` AS
SELECT *,
  TIMESTAMP(taken_time_jittered, "America/Los_Angeles") AS taken_time_jittered_utc,
  TIMESTAMP(scheduled_time_jittered, "America/Los_Angeles") AS scheduled_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.pharmacy_mar`;

-- procedure
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.procedure` AS
SELECT *,
  TIMESTAMP(start_date_jittered, "America/Los_Angeles") AS start_date_jittered_utc,
  TIMESTAMP(proc_date_jittered, "America/Los_Angeles") AS proc_date_jittered_utc,
  TIMESTAMP(adm_date_time_jittered, "America/Los_Angeles") AS adm_date_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.procedure`;

-- smrtdta: has cur_value_datetime_jittered (DATETIME) but no _utc in the
-- established SHC convention — skip. (LPCH does have one; the asymmetry is
-- inherited from 2024 and preserved deliberately.)

-- social_hx: all DATE columns, no UTC needed — skip

-- treatment_team
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.treatment_team` AS
SELECT *,
  TIMESTAMP(trtmnt_tm_begin_dt_jittered, "America/Los_Angeles") AS trtmnt_tm_begin_dt_jittered_utc,
  TIMESTAMP(trtmnt_tm_end_dt_jittered, "America/Los_Angeles") AS trtmnt_tm_end_dt_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.treatment_team`;
```

## 2. LPCH `_utc` conversions

```sql
-- lpch_adt
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_adt` AS
SELECT *,
  TIMESTAMP(effective_time_jittered, "America/Los_Angeles") AS effective_time_jittered_utc,
  TIMESTAMP(event_time_jittered, "America/Los_Angeles") AS event_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_adt`;

-- lpch_alert
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alert` AS
SELECT *,
  TIMESTAMP(update_date_jittered, "America/Los_Angeles") AS update_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alert`;

-- lpch_alert_history
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alert_history` AS
SELECT *,
  TIMESTAMP(update_date_jittered, "America/Los_Angeles") AS update_date_jittered_utc,
  TIMESTAMP(contact_date, "America/Los_Angeles") AS contact_date_utc,
  TIMESTAMP(alt_action_inst, "America/Los_Angeles") AS alt_action_inst_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alert_history`;

-- lpch_alerts_orders
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alerts_orders` AS
SELECT *,
  TIMESTAMP(update_date_jittered, "America/Los_Angeles") AS update_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alerts_orders`;

-- lpch_allergy
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_allergy` AS
SELECT *,
  TIMESTAMP(date_noted_jittered, "America/Los_Angeles") AS date_noted_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_allergy`;

-- lpch_alt_com_action
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_alt_com_action` AS
SELECT *,
  TIMESTAMP(contact_date_jittered, "America/Los_Angeles") AS contact_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_alt_com_action`;

-- lpch_clinical_doc_meta
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_clinical_doc_meta` AS
SELECT *,
  TIMESTAMP(filing_date_jittered, "America/Los_Angeles") AS filing_date_jittered_utc,
  TIMESTAMP(note_date_jittered, "America/Los_Angeles") AS note_date_jittered_utc,
  TIMESTAMP(activity_date_jittered, "America/Los_Angeles") AS activity_date_jittered_utc,
  TIMESTAMP(effective_time_jittered, "America/Los_Angeles") AS effective_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_clinical_doc_meta`;

-- lpch_culture_sensitivity
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_culture_sensitivity` AS
SELECT *,
  TIMESTAMP(order_time_jittered, "America/Los_Angeles") AS order_time_jittered_utc,
  TIMESTAMP(result_time_jittered, "America/Los_Angeles") AS result_time_jittered_utc,
  TIMESTAMP(sens_obs_inst_tm_jittered, "America/Los_Angeles") AS sens_obs_inst_tm_jittered_utc,
  TIMESTAMP(sens_anl_inst_tm_jittered, "America/Los_Angeles") AS sens_anl_inst_tm_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_culture_sensitivity`;

-- lpch_demographic
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_demographic` AS
SELECT *,
  TIMESTAMP(birth_date_jittered, "America/Los_Angeles") AS birth_date_jittered_utc,
  TIMESTAMP(death_date_jittered, "America/Los_Angeles") AS death_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_demographic`;

-- lpch_diagnosis
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_diagnosis` AS
SELECT *,
  TIMESTAMP(start_date_jittered, "America/Los_Angeles") AS start_date_jittered_utc,
  TIMESTAMP(noted_date_jittered, "America/Los_Angeles") AS noted_date_jittered_utc,
  TIMESTAMP(hx_date_of_entry_jittered, "America/Los_Angeles") AS hx_date_of_entry_jittered_utc,
  TIMESTAMP(resolved_date_jittered, "America/Los_Angeles") AS resolved_date_jittered_utc,
  TIMESTAMP(end_date_jittered, "America/Los_Angeles") AS end_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_diagnosis`;

-- lpch_encounter
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter` AS
SELECT *,
  TIMESTAMP(contact_date_jittered, "America/Los_Angeles") AS contact_date_jittered_utc,
  TIMESTAMP(adt_arrival_time_jittered, "America/Los_Angeles") AS adt_arrival_time_jittered_utc,
  TIMESTAMP(hosp_admsn_time_jittered, "America/Los_Angeles") AS hosp_admsn_time_jittered_utc,
  TIMESTAMP(hosp_disch_time_jittered, "America/Los_Angeles") AS hosp_disch_time_jittered_utc,
  TIMESTAMP(appt_time_jittered, "America/Los_Angeles") AS appt_time_jittered_utc,
  TIMESTAMP(appt_when_jittered, "America/Los_Angeles") AS appt_when_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_encounter`;

-- lpch_f_ip_hsp_admission
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_f_ip_hsp_admission` AS
SELECT *,
  TIMESTAMP(hosp_adm_date_jittered, "America/Los_Angeles") AS hosp_adm_date_jittered_utc,
  TIMESTAMP(hosp_disch_date_jittered, "America/Los_Angeles") AS hosp_disch_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_f_ip_hsp_admission`;

-- lpch_family_hx: DATE only, no UTC needed — skip

-- lpch_flowsheet
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_flowsheet` AS
SELECT *,
  TIMESTAMP(recorded_time_jittered, "America/Los_Angeles") AS recorded_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_flowsheet`;

-- lpch_ib_messages
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_ib_messages` AS
SELECT *,
  TIMESTAMP(create_time_jittered, "America/Los_Angeles") AS create_time_jittered_utc,
  TIMESTAMP(send_on_jittered, "America/Los_Angeles") AS send_on_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_ib_messages`;

-- lpch_lab_result
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_lab_result` AS
SELECT *,
  TIMESTAMP(order_time_jittered, "America/Los_Angeles") AS order_time_jittered_utc,
  TIMESTAMP(taken_time_jittered, "America/Los_Angeles") AS taken_time_jittered_utc,
  TIMESTAMP(result_time_jittered, "America/Los_Angeles") AS result_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_lab_result`;

-- lpch_lda
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_lda` AS
SELECT *,
  TIMESTAMP(placement_instant_jittered, "America/Los_Angeles") AS placement_instant_jittered_utc,
  TIMESTAMP(removal_instant_jittered, "America/Los_Angeles") AS removal_instant_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_lda`;

-- lpch_order_comment
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_comment` AS
SELECT *,
  TIMESTAMP(order_inst_jittered, "America/Los_Angeles") AS order_inst_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_comment`;

-- lpch_order_med
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_med` AS
SELECT *,
  TIMESTAMP(ordering_date_jittered, "America/Los_Angeles") AS ordering_date_jittered_utc,
  TIMESTAMP(start_date_jittered, "America/Los_Angeles") AS start_date_jittered_utc,
  TIMESTAMP(end_date_jittered, "America/Los_Angeles") AS end_date_jittered_utc,
  TIMESTAMP(order_start_time_jittered, "America/Los_Angeles") AS order_start_time_jittered_utc,
  TIMESTAMP(order_end_time_jittered, "America/Los_Angeles") AS order_end_time_jittered_utc,
  TIMESTAMP(order_inst_jittered, "America/Los_Angeles") AS order_inst_jittered_utc,
  TIMESTAMP(discon_time_jittered, "America/Los_Angeles") AS discon_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_med`;

-- lpch_order_proc
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_proc` AS
SELECT *,
  TIMESTAMP(ordering_date_jittered, "America/Los_Angeles") AS ordering_date_jittered_utc,
  TIMESTAMP(standing_exp_date_jittered, "America/Los_Angeles") AS standing_exp_date_jittered_utc,
  TIMESTAMP(proc_bgn_time_jittered, "America/Los_Angeles") AS proc_bgn_time_jittered_utc,
  TIMESTAMP(proc_end_time_jittered, "America/Los_Angeles") AS proc_end_time_jittered_utc,
  TIMESTAMP(order_inst_jittered, "America/Los_Angeles") AS order_inst_jittered_utc,
  TIMESTAMP(instantiated_time_jittered, "America/Los_Angeles") AS instantiated_time_jittered_utc,
  TIMESTAMP(order_time_jittered, "America/Los_Angeles") AS order_time_jittered_utc,
  TIMESTAMP(result_time_jittered, "America/Los_Angeles") AS result_time_jittered_utc,
  TIMESTAMP(proc_start_time_jittered, "America/Los_Angeles") AS proc_start_time_jittered_utc,
  TIMESTAMP(proc_date_jittered, "America/Los_Angeles") AS proc_date_jittered_utc,
  TIMESTAMP(last_stand_perf_dt_jittered, "America/Los_Angeles") AS last_stand_perf_dt_jittered_utc,
  TIMESTAMP(last_stand_perf_tm_jittered, "America/Los_Angeles") AS last_stand_perf_tm_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_proc`;

-- lpch_order_quest
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_order_quest` AS
SELECT *,
  TIMESTAMP(ord_quest_date_jittered, "America/Los_Angeles") AS ord_quest_date_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_order_quest`;

-- lpch_pharmacy_mar
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_pharmacy_mar` AS
SELECT *,
  TIMESTAMP(taken_time_jittered, "America/Los_Angeles") AS taken_time_jittered_utc,
  TIMESTAMP(scheduled_time_jittered, "America/Los_Angeles") AS scheduled_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_pharmacy_mar`;

-- lpch_procedure
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_procedure` AS
SELECT *,
  TIMESTAMP(start_date_jittered, "America/Los_Angeles") AS start_date_jittered_utc,
  TIMESTAMP(proc_date_jittered, "America/Los_Angeles") AS proc_date_jittered_utc,
  TIMESTAMP(adm_date_time_jittered, "America/Los_Angeles") AS adm_date_time_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_procedure`;

-- lpch_smrtdta (LPCH does get a _utc here, unlike SHC — inherited from 2024)
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_smrtdta` AS
SELECT *,
  TIMESTAMP(cur_value_datetime_jittered, "America/Los_Angeles") AS cur_value_datetime_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_smrtdta`;

-- lpch_social_hx: all DATE columns, no UTC needed — skip

-- lpch_treatment_team
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_treatment_team` AS
SELECT *,
  TIMESTAMP(trtmnt_tm_begin_dt_jittered, "America/Los_Angeles") AS trtmnt_tm_begin_dt_jittered_utc,
  TIMESTAMP(trtmnt_tm_end_dt_jittered, "America/Los_Angeles") AS trtmnt_tm_end_dt_jittered_utc
FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_treatment_team`;
```

## 3. Flowsheet numerical extraction

`flowsheet.meas_value` is a STRING holding whatever was recorded — a number (`"98.6"`), a blood pressure (`"120/80"`), a range (`"100-120"`), a value with units (`"5.2 mEq/L"`), or plain text (`"refused"`, `"unable to obtain"`).

Because it's STRING, researchers can't aggregate or filter numerically on it. This step extracts every number found and pivots them into four FLOAT64 columns. `"120/80"` → `numerical_val_1 = 120`, `numerical_val_2 = 80`. Text-only values produce all NULLs. **`meas_value` itself is preserved unchanged.**

⚠️ **This step gets wiped by every rebuild.** Easy to forget — it's the last thing in the pipeline.

First confirm the column list still matches (a refresh could add columns, and the explicit list would silently drop them):

```sql
SELECT column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'flowsheet'
ORDER BY ordinal_position;
```

### SHC

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.flowsheet` AS
SELECT * FROM (
  SELECT
    A.anon_id,
    A.inpatient_data_id_coded,
    A.line,
    A.template,
    A.row_disp_name,
    A.meas_value,
    A.units,
    A.data_source,
    A.recorded_time_jittered,
    A.recorded_time_jittered_utc,
    offset + 1 AS offset,
    SAFE_CAST(num AS FLOAT64) AS num
  FROM `som-nero-phi-jonc101.shc_core_2025.flowsheet` A
  LEFT JOIN UNNEST(REGEXP_EXTRACT_ALL(A.meas_value, r'(-?[\d\.]+)')) num WITH offset
)
PIVOT (MIN(num) AS numerical_val FOR offset IN (1, 2, 3, 4));
```

### LPCH

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.lpch_core_2025.lpch_flowsheet` AS
SELECT * FROM (
  SELECT
    A.anon_id,
    A.inpatient_data_id_coded,
    A.line,
    A.template,
    A.row_disp_name,
    A.meas_value,
    A.units,
    A.data_source,
    A.recorded_time_jittered,
    A.recorded_time_jittered_utc,
    offset + 1 AS offset,
    SAFE_CAST(num AS FLOAT64) AS num
  FROM `som-nero-phi-jonc101.lpch_core_2025.lpch_flowsheet` A
  LEFT JOIN UNNEST(REGEXP_EXTRACT_ALL(A.meas_value, r'(-?[\d\.]+)')) num WITH offset
)
PIVOT (MIN(num) AS numerical_val FOR offset IN (1, 2, 3, 4));
```

### Details that matter

- **List columns explicitly, never `SELECT A.*`.** The pivot needs an unambiguous grouping; `A.*` can break it.
- **Use `SAFE_CAST(num AS FLOAT64)`.** `REGEXP_EXTRACT_ALL` returns STRING. Without the cast the columns come out as STRING, defeating the purpose. `SAFE_CAST` returns NULL on failure rather than erroring.
- **`IN (1, 2, 3, 4)`** caps at the first 4 numbers. Covers essentially all real measurements.

### Known caveats

- **Date-shaped values split into 3 numbers.** `"05/04/2022"` → `5`, `4`, `2022`. Researchers should filter by `row_disp_name` to scope to known numeric measurement types.
- **Extreme values can overflow FLOAT64**, producing `Infinity`. Filter with `WHERE numerical_val_1 BETWEEN -1e10 AND 1e10` if needed.
- **flowsheet is the largest table in the dataset** (7.5B rows SHC, 2.9B LPCH as of Aug 2026). These queries take 10–30 minutes.

## What if a column regresses to STRING?

If a future refresh delivers STRING where DATETIME is expected:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.<table>` AS
SELECT * EXCEPT(<col>),
  PARSE_DATETIME('%Y-%m-%d %H:%M:%S', NULLIF(<col>, '')) AS <col>,
  TIMESTAMP(NULLIF(<col>, ''), "America/Los_Angeles") AS <col>_utc
FROM `som-nero-phi-jonc101.shc_core_2025.<table>`;
```

Use `NULLIF(col, '')`, not `CASE WHEN col <> '' THEN col ELSE NULL END` — BigQuery's type inference handles `NULLIF` correctly and errors on the `CASE` form.

## Next step

[Step 5 — Validate](./05_validate.md).
