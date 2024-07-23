CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_priorprocedures_augmented` AS (
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
  'dialysis' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  FROM  `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures 
  WHERE 
    SAFE_CAST(code as numeric) >= 90935 AND SAFE_CAST(code as numeric) <= 90999
),
######################################################################################## 
# CVC procedures based on CPT codes 36555 to 36573
######################################################################################## 
cvc AS (
  SELECT DISTINCT procedures.anon_id, 
  'cvc' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures
  WHERE 
    SAFE_CAST(code as numeric) >= 36555 AND SAFE_CAST(code as numeric) <= 36573
),
######################################################################################## 
# Mechanical ventilation based on order for 'RESP - VENTILATOR SETTINGS' (2008 onwards)
######################################################################################## 
mechvent AS (
  SELECT  order_proc.anon_id, 
  'mechvent' as procedure_description,
  order_proc.ordering_date_jittered_utc as procedure_time,
  FROM  `som-nero-phi-jonc101.shc_core_2023.order_proc` as order_proc 
  WHERE 
    order_proc.description = 'RESP - VENTILATOR SETTINGS'
),
######################################################################################## 
# Surgical procedures based on ICD10 and CPT mapping provided by Sanjat's team
######################################################################################## 
surgical_procedures AS (
  SELECT procedures.anon_id, 
  'surgical_procedure' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures 
  WHERE 
  code IN (SELECT code FROM `som-nero-phi-jonc101.mvm_abx.CPT_ICD10PCS_mapping`) 
  ),

######################################################################################## 
# Parenteral nutrition from orders_med table
######################################################################################## 
parenteral_nutrition AS (
  SELECT orders.anon_id,
  'parenteral_nutrition' as procedure_description,
  orders.ordering_date_jittered_utc as procedure_time,
  FROM `som-nero-phi-jonc101.shc_core_2023.order_med` as orders 
  WHERE orders.med_description IN ('TPN ADULT STANDARD', 'TPN ADULT CYCLIC', 'TPN BMT', 'PPN ADULT STANDARD')
),

######################################################################################## 
# Urethral catheter based on CPT codes 51701, 51702, and 51703
######################################################################################## 
urethral_catheter AS (
  SELECT procedures.anon_id, 
  'urethral_catheter' as procedure_description,
  procedures.start_date_jittered_utc as procedure_time,
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures 
  WHERE 
    SAFE_CAST(code as numeric) >= 51701 AND SAFE_CAST(code as numeric) <= 51703
   ),

######################################################################################## 
# Combine into single table where each row is a unique culture order
######################################################################################## 
all_procedure as(
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
select c.anon_id, 
  c.order_proc_id_coded,
  c.pat_enc_csn_id_coded,
  c.order_time_jittered_utc,
  ap.procedure_time,
  ap.procedure_description,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,ap.procedure_time,day) as procedure_days_culture,
  from antibiotic_cohort c left join all_procedure ap using (anon_id)
  where (ap.procedure_time is null 
  OR 
  ap.procedure_time <=c.order_time_jittered_utc)
  group by c.anon_id,c.order_proc_id_coded,c.pat_enc_csn_id_coded,c.order_time_jittered_utc,ap.procedure_description,ap.procedure_time
  order by  c.anon_id,c.order_proc_id_coded,c.pat_enc_csn_id_coded,c.order_time_jittered_utc,ap.procedure_description,ap.procedure_time
  )


