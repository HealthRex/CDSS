CREATE OR REPLACE TABLE `mvm_abx.antibiotic_dataset_procedures_6mo` AS 

WITH

antibiotic_cohort AS (
  SELECT * FROM `som-nero-phi-jonc101.fateme_db.antibiotic_cohort_temp`
),

######################################################################################## 
# Dialysis procedures based on CPT codes 90935 to 90999
######################################################################################## 
dialysis_6mo AS (
  SELECT DISTINCT procedures.anon_id, antibiotic_cohort.order_proc_id_coded, 1 as dialysis
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort on antibiotic_cohort.anon_id = procedures.anon_id
  WHERE 
    SAFE_CAST(code as numeric) >= 90935 AND SAFE_CAST(code as numeric) <= 90999
    AND procedures.start_date_jittered_utc < antibiotic_cohort.order_time_jittered_utc
    AND TIMESTAMP_DIFF(antibiotic_cohort.order_time_jittered_utc, procedures.start_date_jittered_utc, DAY) < 180
),

######################################################################################## 
# CVC procedures based on CPT codes 36555 to 36573
######################################################################################## 
cvc_6mo AS (
  SELECT DISTINCT procedures.anon_id, antibiotic_cohort.order_proc_id_coded, 1 as cvc
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort on antibiotic_cohort.anon_id = procedures.anon_id
  WHERE 
    SAFE_CAST(code as numeric) >= 36555 AND SAFE_CAST(code as numeric) <= 36573
    AND procedures.start_date_jittered_utc < antibiotic_cohort.order_time_jittered_utc
    AND TIMESTAMP_DIFF(antibiotic_cohort.order_time_jittered_utc, procedures.start_date_jittered_utc, DAY) < 180
),

######################################################################################## 
# Mechanical ventilation based on order for 'RESP - VENTILATOR SETTINGS' (2008 onwards)
######################################################################################## 
mechvent_6mo AS (
  SELECT DISTINCT order_proc.anon_id, antibiotic_cohort.order_proc_id_coded, 1 as mechvent
  FROM `som-nero-phi-jonc101.shc_core_2023.order_proc` as order_proc INNER JOIN
    antibiotic_cohort on antibiotic_cohort.anon_id = order_proc.anon_id
  WHERE 
    order_proc.description = 'RESP - VENTILATOR SETTINGS'
    AND order_proc.ordering_date_jittered_utc < antibiotic_cohort.order_time_jittered_utc
    AND TIMESTAMP_DIFF(antibiotic_cohort.order_time_jittered_utc, order_proc.ordering_date_jittered_utc, DAY) < 180
),

######################################################################################## 
# Surgical procedures based on ICD10 and CPT mapping provided by Sanjat's team
######################################################################################## 
surgical_procedures_6mo AS (
  SELECT antibiotic_cohort.anon_id, antibiotic_cohort.order_proc_id_coded, 1 as surgical_procedure
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort on antibiotic_cohort.anon_id = procedures.anon_id
  WHERE code IN (SELECT code FROM `som-nero-phi-jonc101.mvm_abx.CPT_ICD10PCS_mapping`)
    AND procedures.start_date_jittered_utc < antibiotic_cohort.order_time_jittered_utc
    AND TIMESTAMP_DIFF(antibiotic_cohort.order_time_jittered_utc, procedures.start_date_jittered_utc, DAY) < 180
),

######################################################################################## 
# Parenteral nutrition from orders_med table
######################################################################################## 
parenteral_nutrition_6mo AS (
  SELECT antibiotic_cohort.anon_id, antibiotic_cohort.order_proc_id_coded, 1 as parenteral_nutrition
  FROM `som-nero-phi-jonc101.shc_core_2023.order_med` as orders INNER JOIN
    antibiotic_cohort on antibiotic_cohort.anon_id = orders.anon_id
  WHERE orders.med_description IN ('TPN ADULT STANDARD', 'TPN ADULT CYCLIC', 'TPN BMT', 'PPN ADULT STANDARD')
    AND orders.ordering_date_jittered_utc < antibiotic_cohort.order_time_jittered_utc
    AND TIMESTAMP_DIFF(antibiotic_cohort.order_time_jittered_utc, orders.ordering_date_jittered_utc, DAY) < 180
),

######################################################################################## 
# Urethral catheter based on CPT codes 51701, 51702, and 51703
######################################################################################## 
urethral_catheter_6mo AS (
  SELECT DISTINCT procedures.anon_id, antibiotic_cohort.order_proc_id_coded, 1 as urethral_catheter
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort on antibiotic_cohort.anon_id = procedures.anon_id
  WHERE 
    SAFE_CAST(code as numeric) >= 51701 AND SAFE_CAST(code as numeric) <= 51703
    AND procedures.start_date_jittered_utc < antibiotic_cohort.order_time_jittered_utc
    AND TIMESTAMP_DIFF(antibiotic_cohort.order_time_jittered_utc, procedures.start_date_jittered_utc, DAY) < 180
)

######################################################################################## 
# Combine into single table where each row is a unique culture order
# And binary indicator columns for dialysis, cvc, mechvent, surgerical procedures,
# paraenteral nutrition, and urethral (e.g., Foley) catheters in 6 months prior to culture
######################################################################################## 
SELECT DISTINCT antibiotic_cohort.anon_id, 
  antibiotic_cohort.pat_enc_csn_id_coded,
  antibiotic_cohort.order_proc_id_coded,
  antibiotic_cohort.order_time_jittered_utc, 
  IFNULL(dialysis_6mo.dialysis, 0) as dialysis_6mo,
  IFNULL(cvc_6mo.cvc, 0) as cvc_6mo,
  IFNULL(mechvent_6mo.mechvent, 0) as mechvent_6mo,
  IFNULL(surgical_procedures_6mo.surgical_procedure, 0) as surgical_procedure_6mo,
  IFNULL(parenteral_nutrition_6mo.parenteral_nutrition, 0) as parenteral_nutrition_6mo,
  IFNULL(urethral_catheter_6mo.urethral_catheter, 0) as urethral_catheter_6mo
FROM antibiotic_cohort LEFT JOIN dialysis_6mo ON (
  antibiotic_cohort.anon_id = dialysis_6mo.anon_id AND
  antibiotic_cohort.order_proc_id_coded = dialysis_6mo.order_proc_id_coded
) LEFT JOIN cvc_6mo ON (
  antibiotic_cohort.anon_id = cvc_6mo.anon_id AND
  antibiotic_cohort.order_proc_id_coded = cvc_6mo.order_proc_id_coded
) LEFT JOIN mechvent_6mo ON (
  antibiotic_cohort.anon_id = mechvent_6mo.anon_id AND
  antibiotic_cohort.order_proc_id_coded = mechvent_6mo.order_proc_id_coded
) LEFT JOIN surgical_procedures_6mo ON (
  antibiotic_cohort.anon_id = surgical_procedures_6mo.anon_id AND
  antibiotic_cohort.order_proc_id_coded = surgical_procedures_6mo.order_proc_id_coded
) LEFT JOIN parenteral_nutrition_6mo ON (
  antibiotic_cohort.anon_id = parenteral_nutrition_6mo.anon_id AND
  antibiotic_cohort.order_proc_id_coded = parenteral_nutrition_6mo.order_proc_id_coded
) LEFT JOIN urethral_catheter_6mo ON (
  antibiotic_cohort.anon_id = urethral_catheter_6mo.anon_id AND
  antibiotic_cohort.order_proc_id_coded = urethral_catheter_6mo.order_proc_id_coded
)
