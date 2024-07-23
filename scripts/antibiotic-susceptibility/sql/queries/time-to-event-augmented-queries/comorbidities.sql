####################
##Goal: Have table indicats a comorbidity component being present before specimen collection.
######################
# base cohort 
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_comorbidity_augmented` AS(
with base_cohort as (
select anon_id,
pat_enc_csn_id_coded,
order_proc_id_coded,
order_time_jittered_utc,
from `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort`
),
# CCSR-AHRQ ICD10 codes for each component 
CCSR_code as (
  select ICD10,
  Category_Description
  from `som-nero-phi-jonc101.mapdata.ahrq_ccsr_diagnosis` 
),
# elixhauser ICD10 codes for each component
elixhauser_codes as (
  select ICD10,
  category
   from `som-nero-phi-jonc101.mapdata.elixhauser-comorbidity-components` 
),
# Map diagnosis icd10 codes to CCSR-AHRQ comorbidities 
AHRQ_CCSR as (
select d.anon_id,
d.start_date_jittered_utc as comorbidity_component_start_time,
d.end_date_jittered_utc as comorbidity_component_end_time,
c.Category_Description as comorbidity_component
from  `som-nero-phi-jonc101.shc_core_2023.diagnosis` d inner join  CCSR_code c using(ICD10)
),
# Map diagnosis icd10 codes to elixhauser comorbidities 
elixhauser_components as (
select d.anon_id,
d.start_date_jittered_utc as comorbidity_component_start_time,
d.end_date_jittered_utc as comorbidity_component_end_time,
c.category as comorbidity_component
from  `som-nero-phi-jonc101.shc_core_2023.diagnosis` d inner join  elixhauser_codes c using(ICD10)
),
# Concat elixhauser comorbidities and CCSR-AHRQ comorbidities 
All_Components as (
  select * from elixhauser_components
  union all
  select * from AHRQ_CCSR
)
# Outline the time comorbidity being present with respect to the culture order
  select c.anon_id,
  c.pat_enc_csn_id_coded,
  c.order_proc_id_coded,
  c.order_time_jittered_utc,
  A.comorbidity_component_start_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,A.comorbidity_component_start_time,day) as comorbidity_component_start_days_culture,
  A.comorbidity_component_end_time,
  TIMESTAMP_DIFF(c.order_time_jittered_utc,A.comorbidity_component_end_time,day) as comorbidity_component_end_days_culture,
from base_cohort c left join All_Components A using(anon_id)  
where
(c.order_time_jittered_utc>= A.comorbidity_component_start_time OR A.comorbidity_component_start_time is null) 
)
