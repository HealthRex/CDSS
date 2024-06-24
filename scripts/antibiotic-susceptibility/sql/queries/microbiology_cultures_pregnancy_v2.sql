####################################################################################################################################################
#Create a new table for pregnancy information based on anon_id, pat_enc_csn_id_coded, and order_proc_id_coded from the microbiology_cultures_cohort
####################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_pregnancy_cohort` AS(

####################################################################
#Base cohort that we build our study cohort from
####################################################################
With Base_cohort as (
SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    order_time_jittered_utc, 
    FROM `som-nero-phi-jonc101.fateme_db.antibiotic_cohort_temp` 
),
####################################################################
#Extract All Positive Pregnancy Test
####################################################################
All_Pregnant_lab_tests as(
select lr.anon_id,
       lr.order_time_jittered_utc as pregnancy_time ,
       b.order_proc_id_coded,
       TIMESTAMP_DIFF(b.order_time_jittered_utc,lr.order_time_jittered_utc,day) AS Pregnancy_To_Culture_Order,
from `som-nero-phi-jonc101.shc_core_2023.lab_result` lr inner join Base_cohort b using(anon_id)
where LOWER(lr.group_lab_name) LIKE '%pregnancy test%'
      AND LOWER(lr.ord_value) NOT LIKE '%neg%'
      AND LOWER(lr.ord_value) NOT LIKE '%device%'
      AND LEFT(lr.ord_value, 1) NOT LIKE '<'
      AND (TIMESTAMP_DIFF(b.order_time_jittered_utc,lr.order_time_jittered_utc,day) between 0 and 270)
),
####################################################################
#Identify Pregnant Patients Whose Pregnancies Are Being Terminated.
####################################################################
All_Terminated_Pregnancy as(
  select b.anon_id,
          b.order_proc_id_coded,
        TIMESTAMP(pr.ordering_date) AS pregnancy_termination_time ,
        TIMESTAMP_DIFF(b.order_time_jittered_utc,TIMESTAMP(pr.ordering_date),day) AS Termination_Pregnancy_To_Culture_Order,
From  `som-nero-phi-jonc101.shc_core_2023.proc_note` pr inner join Base_cohort b using(anon_id)
where lower(pr.report) like any ('%termination%pregnancy%')
AND pr.order_status like 'Completed'
AND (TIMESTAMP_DIFF(b.order_time_jittered_utc,TIMESTAMP(pr.ordering_date),day) between 0 and 270)
),
Pregnencyinfo as (
  select Ap.anon_id,
        Ap.order_proc_id_coded,
        Ap.pregnancy_time as recorded_pregnancy_time,
        Ap.Pregnancy_To_Culture_Order as pregnancy_days_to_culture_order,
        Atp.pregnancy_termination_time as recorded_pregnancy_termination_time,
        Atp.Termination_Pregnancy_To_Culture_Order as terminated_pregnancy_days_to_culture_order,
  from All_Pregnant_lab_tests Ap left join All_Terminated_Pregnancy Atp using (anon_id,order_proc_id_coded)
  where 
  (pregnancy_termination_time is null or TIMESTAMP_DIFF(Atp.pregnancy_termination_time,Ap.pregnancy_time,day) between 0 and 270)
)
select p.anon_id,
p.order_proc_id_coded,
c.pat_enc_csn_id_coded,
c.order_time_jittered_utc,
p.recorded_pregnancy_time,
p.pregnancy_days_to_culture_order,
p.recorded_pregnancy_termination_time,
p.terminated_pregnancy_days_to_culture_order,
from Pregnencyinfo p left join base_cohort c using(anon_id,order_proc_id_coded)
)
