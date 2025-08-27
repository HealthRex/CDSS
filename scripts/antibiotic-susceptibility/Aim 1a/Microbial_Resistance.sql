###################
#Goal:patient's past resistance to specific antibiotics within the given time frame before the current specimen collection.  
######################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_microbial_resistance` AS(
###############
## our base cohort to build our population study
###############
with base_cohort as (
select anon_id,
pat_enc_csn_id_coded,
order_proc_id_coded,
order_time_jittered_utc,
from `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort`
),
###############
## Relevent antibutics 
###############
Frequent_ABX AS (
  SELECT DISTINCT(antibiotic_name)
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.prior_antibiotics_list` 
)
  SELECT
    c.anon_id,
    c.pat_enc_csn_id_coded,
    c.order_proc_id_coded,
    c.order_time_jittered_utc,
    cs.organism,
    cs.antibiotic,
    cs.order_time_jittered_utc as recorded_resistsant_time,
    TIMESTAMP_DIFF(c.order_time_jittered_utc,cs.order_time_jittered_utc,day) as resistsant_time_to_cultureTime
  FROM `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity` cs
  inner join base_cohort c using (anon_id)
  WHERE cs.antibiotic IN (SELECT antibiotic_name FROM Frequent_ABX)
  and cs.suscept='Resistant'
  and TIMESTAMP_DIFF(c.order_time_jittered_utc,cs.order_time_jittered_utc,day)>=0
)

