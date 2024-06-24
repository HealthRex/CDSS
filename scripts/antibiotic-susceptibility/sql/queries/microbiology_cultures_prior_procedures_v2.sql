CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_priorprocedures` AS (
WITH
antibiotic_cohort AS (
 select anon_id,
pat_enc_csn_id_coded,
order_proc_id_coded,
order_time_jittered_utc,
from `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort`
),
######################################################################################## 
# Dialysis procedures based on CPT codes 90935 to 90999
######################################################################################## 
dialysis AS (
  SELECT DISTINCT 
  procedures.anon_id, 
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  'dialysis' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,procedures.start_date_jittered_utc,day) as procedure_days_culture,
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort c using(anon_id)
  WHERE 
    SAFE_CAST(code as numeric) >= 90935 AND SAFE_CAST(code as numeric) <= 90999
    AND procedures.start_date_jittered_utc < c.order_time_jittered_utc
),
######################################################################################## 
# CVC procedures based on CPT codes 36555 to 36573
######################################################################################## 
cvc AS (
  SELECT DISTINCT procedures.anon_id, 
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  'cvc' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,procedures.start_date_jittered_utc,day) as procedure_days_culture,
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort c using(anon_id)
  WHERE 
    SAFE_CAST(code as numeric) >= 36555 AND SAFE_CAST(code as numeric) <= 36573
    AND procedures.start_date_jittered_utc < c.order_time_jittered_utc
),

######################################################################################## 
# Mechanical ventilation based on order for 'RESP - VENTILATOR SETTINGS' (2008 onwards)
######################################################################################## 
mechvent AS (
  SELECT  order_proc.anon_id, 
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  'mechvent' as procedure_description,
  order_proc.ordering_date_jittered_utc as procedure_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,order_proc.ordering_date_jittered_utc,day) as procedure_days_culture,
  FROM `som-nero-phi-jonc101.shc_core_2023.order_proc` as order_proc INNER JOIN
    antibiotic_cohort c using(anon_id)
  WHERE 
    order_proc.description = 'RESP - VENTILATOR SETTINGS'
    AND order_proc.ordering_date_jittered_utc < c.order_time_jittered_utc
),

######################################################################################## 
# Surgical procedures based on ICD10 and CPT mapping provided by Sanjat's team
######################################################################################## 
surgical_procedures AS (
  SELECT procedures.anon_id, 
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  'surgical_procedure' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,procedures.start_date_jittered_utc,day) as procedure_days_culture,
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort c using(anon_id)
  WHERE code IN (SELECT code FROM `som-nero-phi-jonc101.mvm_abx.CPT_ICD10PCS_mapping`)
    AND procedures.start_date_jittered_utc < c.order_time_jittered_utc
),

######################################################################################## 
# Parenteral nutrition from orders_med table
######################################################################################## 
parenteral_nutrition AS (
  SELECT orders.anon_id,
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  'parenteral_nutrition' as procedure_description,
  orders.ordering_date_jittered_utc as procedure_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,orders.ordering_date_jittered_utc,day) as procedure_days_culture,
  FROM `som-nero-phi-jonc101.shc_core_2023.order_med` as orders INNER JOIN
    antibiotic_cohort c using(anon_id)
  WHERE orders.med_description IN ('TPN ADULT STANDARD', 'TPN ADULT CYCLIC', 'TPN BMT', 'PPN ADULT STANDARD')
    AND orders.ordering_date_jittered_utc < c.order_time_jittered_utc
),

######################################################################################## 
# Urethral catheter based on CPT codes 51701, 51702, and 51703
######################################################################################## 
urethral_catheter AS (
  SELECT procedures.anon_id, 
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  'urethral_catheter' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,procedures.start_date_jittered_utc,day) as procedure_days_culture,

  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    antibiotic_cohort c using(anon_id)
  WHERE 
    SAFE_CAST(code as numeric) >= 51701 AND SAFE_CAST(code as numeric) <= 51703
    AND procedures.start_date_jittered_utc < c.order_time_jittered_utc
)

######################################################################################## 
# Combine into single table where each row is a unique culture order
######################################################################################## 
select *  from urethral_catheter
union all
select * from parenteral_nutrition
union all
select * from surgical_procedures
union all
select * from mechvent
union all
select * from cvc
union all
select * from dialysis
)
