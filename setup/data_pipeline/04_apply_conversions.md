# Step 4 — Apply Conversions

The yearly datasets now have raw data with DATETIME/DATE columns already correctly typed (the secure project delivers proper types now). The only transformation needed is **adding parallel `_utc` columns** for every DATETIME column. Source times are in `America/Los_Angeles`; `_utc` columns let researchers do timezone-correct analysis.

## Why this approach

Previous versions of this pipeline used auto-detection — a Python script that inspected each STRING column, flagged any with at least one date-parseable value as a "datetime" column, and converted it. This was unsafe: columns like `lab_result.ord_value` (containing values like `"5.2"`, `"negative"`, `"<0.1"`) had some values that coincidentally parsed as dates, so the whole column got reformatted, silently destroying the text data.

The correct approach is to **use last year's schema as the source of truth**. Last year's `shc_core_YYYY-1` has been in production for a year and is known-good. Every column that was DATETIME in last year's schema should be DATETIME in this year's. Every column with a `_utc` version in last year's schema needs the same `_utc` in this year's.

## 1. Derive the column list from last year's schema

Run this against last year's dataset to see exactly which columns need conversion:

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2024.INFORMATION_SCHEMA.COLUMNS`
WHERE data_type IN ('DATETIME', 'DATE', 'TIMESTAMP')
ORDER BY table_name, ordinal_position;
```

The DATETIME entries are what to convert. The TIMESTAMP entries (already `_utc` columns from last year) tell you which `_utc` columns to recreate. DATE columns don't need `_utc` versions.

Same for LPCH using `lpch_core_2024`.

## 2. Confirm current state of this year's dataset

```sql
SELECT table_name, column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE data_type IN ('DATETIME', 'DATE', 'TIMESTAMP')
   OR column_name LIKE '%date%'
   OR column_name LIKE '%time%'
ORDER BY table_name, ordinal_position;
```

The DATETIME/DATE columns should match last year's. If anything is STRING that should be a datetime, the secure project may have regressed — investigate before proceeding.

## 3. Apply SHC conversions

```sql
-- ============================================================
-- shc_core_2025 — Add _utc columns to existing DATETIME columns
-- ============================================================

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

-- smrtdta: DATETIME but no UTC in 2024 schema — skip

-- social_hx: all DATE columns, no UTC needed — skip

-- treatment_team
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_2025.treatment_team` AS
SELECT *,
  TIMESTAMP(trtmnt_tm_begin_dt_jittered, "America/Los_Angeles") AS trtmnt_tm_begin_dt_jittered_utc,
  TIMESTAMP(trtmnt_tm_end_dt_jittered, "America/Los_Angeles") AS trtmnt_tm_end_dt_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2025.treatment_team`;
```

## 4. Apply LPCH conversions

```sql
-- ============================================================
-- lpch_core_2025 — Add _utc columns to existing DATETIME columns
-- ============================================================

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

-- lpch_alt_com_action (NEW table in 2025)
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

-- lpch_order_quest (NEW table in 2025)
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

-- lpch_smrtdta
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

## 5. Extract numerical values from `flowsheet.meas_value`

The `flowsheet` table has a STRING column called `meas_value` that holds whatever was recorded during a measurement. Because it's text, the values can be many different things:

- A simple number: `"98.6"` (temperature)
- A blood pressure reading: `"120/80"` (two numbers in one cell)
- A range: `"100-120"`
- A value with units in the text: `"5.2 mEq/L"`
- Non-numeric text: `"refused"`, `"unable to obtain"`, `"see comment"`

Because `meas_value` is STRING, researchers can't do math on it directly (no `AVG`, no `WHERE meas_value > 100`, no use as a feature in ML models). To make the numeric content usable, we extract every number found in `meas_value` and pivot the results into four parallel FLOAT64 columns: `numerical_val_1`, `numerical_val_2`, `numerical_val_3`, `numerical_val_4`.

A blood pressure value of `"120/80"` becomes `numerical_val_1 = 120`, `numerical_val_2 = 80`. A temperature of `"98.6"` becomes `numerical_val_1 = 98.6`. Text like `"refused"` produces all NULLs.

The original `meas_value` column is preserved unchanged — nothing is lost.

### SHC flowsheet extraction

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

### LPCH flowsheet extraction

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

### Important details to get right

These details matter — getting any wrong will produce silently bad output:

- **List columns explicitly, not `SELECT A.*`.** The pivot needs an unambiguous grouping. If you use `SELECT A.*`, columns added by future schema changes can break the pivot grouping and inflate row counts. Always enumerate the columns.
- **Use `SAFE_CAST(num AS FLOAT64)`.** `REGEXP_EXTRACT_ALL` returns STRING. Without the cast, the resulting `numerical_val_*` columns are STRING — which defeats the purpose. `SAFE_CAST` returns NULL on failure (e.g., on `"."` alone) rather than erroring.
- **The pivot's `IN (1, 2, 3, 4)`** caps extraction at the first 4 numbers found. This covers virtually all real measurements; values with more than 4 numbers (extremely rare) get truncated.

### Verify row count is unchanged

The extraction rewrites columns, not rows. Row count should match the source exactly. Confirm:

```sql
SELECT COUNT(*) FROM `som-nero-phi-jonc101.shc_core_2025.flowsheet`;
-- Should match the row count from the backup: copy_shc_core_2025.flowsheet
```

If the count is wildly different (e.g., 10× larger), the pivot grouping is broken — restore from backup and check the column list in the inner SELECT.

### Verify column types

```sql
SELECT column_name, data_type
FROM `som-nero-phi-jonc101.shc_core_2025.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'flowsheet'
  AND column_name LIKE '%numerical_val%';
```

All four `numerical_val_*` columns should be `FLOAT64`. If they're `STRING`, you forgot the `SAFE_CAST`.

### Known caveats

- **Date-shaped values get split into 3 numbers.** A `meas_value` of `"05/04/2022"` becomes `numerical_val_1 = 5`, `numerical_val_2 = 4`, `numerical_val_3 = 2022`. Dates shouldn't normally appear in measurement fields, but if they do, this is what happens. Researchers can filter by `row_disp_name` to scope to known numeric measurement types (temperature, BP, etc.) and avoid this.
- **Extreme values may overflow FLOAT64.** Some `meas_value` strings contain very long digit sequences (often malformed IDs or test data) that exceed FLOAT64's range, producing `Infinity` or `-Infinity`. To filter these out: `WHERE numerical_val_1 BETWEEN -1e10 AND 1e10` or similar.
- **The `flowsheet` table is huge** (several billion rows). These queries take 10–30 minutes each. Run when you have time.

## What if a STRING column needs parsing?

If a future year's secure data delivers STRING columns where the previous year had DATETIME (regression), use this pattern instead of plain `TIMESTAMP(col, ...)`:

```sql
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.shc_core_YYYY.<table>` AS
SELECT * EXCEPT(<col>),
  PARSE_DATETIME('%Y-%m-%d %H:%M:%S', NULLIF(<col>, '')) AS <col>,
  TIMESTAMP(NULLIF(<col>, ''), "America/Los_Angeles") AS <col>_utc
FROM `som-nero-phi-jonc101.shc_core_YYYY.<table>`;
```

Use `NULLIF(col, '')` rather than `CASE WHEN col <> '' THEN col ELSE NULL END` — BigQuery handles the typing correctly with `NULLIF`.

## Next step

[Step 5 — Validate](./05_validate.md).
