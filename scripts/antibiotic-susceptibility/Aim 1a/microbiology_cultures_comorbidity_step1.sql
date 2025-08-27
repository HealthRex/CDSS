###################
#Goal: Have table with binary indicators of a comorbidity being present within the given time frame before specimen collection.
#The process includes two steps. Step 1 is done with Biqquery SQL but Step2 has been done in Python. The notebook for Step 2 is being attached. 
######################

#####################
#Step1: Create a table to keep comorbidity being present within the given time frame before specimen collection.
###################
# base cohort 
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_comorbidity_temp` AS(
with base_cohort as (
select anon_id,
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
d.start_date_jittered_utc,
d.end_date_jittered_utc,
c.Category_Description as comorbidity_component
from  `som-nero-phi-jonc101.shc_core_2023.diagnosis` d inner join  CCSR_code c using(ICD10)
),
# Map diagnosis icd10 codes to elixhauser comorbidities 
elixhauser_components as (
select d.anon_id,
d.start_date_jittered_utc,
d.end_date_jittered_utc,
c.category as comorbidity_component
from  `som-nero-phi-jonc101.shc_core_2023.diagnosis` d inner join  elixhauser_codes c using(ICD10)
),
# Concat elixhauser comorbidities and CCSR-AHRQ comorbidities 
All_Components as (
  select * from elixhauser_components
  union all
  select * from AHRQ_CCSR
),
# Outline the time comorbidity being present with respect to the culture order
Present_components_timeline as(
  select c.anon_id,
  c.order_proc_id_coded,
  c.order_time_jittered_utc,
  case when (A.start_date_jittered_utc<=order_time_jittered_utc and A.end_date_jittered_utc>=order_time_jittered_utc) then  comorbidity_component end as present_component,
  case when (TIMESTAMP_DIFF(c.order_time_jittered_utc,A.start_date_jittered_utc,day)>=7 and TIMESTAMP_DIFF(c.order_time_jittered_utc,A.end_date_jittered_utc,day) <7) then  comorbidity_component end as component_7days,
  case when (TIMESTAMP_DIFF(c.order_time_jittered_utc,A.start_date_jittered_utc,day)>=14 and TIMESTAMP_DIFF(c.order_time_jittered_utc,A.end_date_jittered_utc,day) <14) then  comorbidity_component end as component_14days,
  case when (TIMESTAMP_DIFF(c.order_time_jittered_utc,A.start_date_jittered_utc,day)>=30 and TIMESTAMP_DIFF(c.order_time_jittered_utc,A.end_date_jittered_utc,day) <30) then  comorbidity_component end as component_30days,
  case when (TIMESTAMP_DIFF(c.order_time_jittered_utc,A.start_date_jittered_utc,day)>=90 and TIMESTAMP_DIFF(c.order_time_jittered_utc,A.end_date_jittered_utc,day) <90) then  comorbidity_component end as component_90days,
  case when (TIMESTAMP_DIFF(c.order_time_jittered_utc,A.start_date_jittered_utc,day)>=180 and TIMESTAMP_DIFF(c.order_time_jittered_utc,A.end_date_jittered_utc,day) <180) then  comorbidity_component end as component_180days,
from All_Components A inner join base_cohort c using(anon_id)  
where TIMESTAMP_DIFF(c.order_time_jittered_utc,A.end_date_jittered_utc,day)<=180
)
select * 
from Present_components_timeline 
where  present_component is not null 
OR component_7days is not null 
OR component_14days is not null 
OR component_30days is not null 
OR  component_90days is not null 
OR  component_180days is not null
);
##################################
# Step2: run Comorbidities jupyter notebook to one-hot code presence of comorbidities being present within the given time frame before specimen collection
##################################

# drop intermidiate table 
DROP TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_comorbidity_temp`


