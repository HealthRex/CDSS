
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
####################################################################
#Outline Termination Pregnancy
####################################################################
All_Non_Terminted_Pregnancy as (
select lr.anon_id,
lr.pregnancy_time,
lr.order_proc_id_coded,
case when (Termination_Pregnancy_To_Culture_Order<7 and Termination_Pregnancy_To_Culture_Order>=0) then 'Termination of pregnancy censored 7 days ago'
when (Termination_Pregnancy_To_Culture_Order<14 and Termination_Pregnancy_To_Culture_Order>=0) then 'Termination of pregnancy censored 14 days ago'
when (Termination_Pregnancy_To_Culture_Order<30 and Termination_Pregnancy_To_Culture_Order>=0) then 'Termination of pregnancy censored 30 days ago'
when (Termination_Pregnancy_To_Culture_Order<90 and Termination_Pregnancy_To_Culture_Order>=0) then 'Termination of pregnancy censored 90 days ago'
when (Termination_Pregnancy_To_Culture_Order<180 and Termination_Pregnancy_To_Culture_Order>=0) then 'Termination of pregnancy censored 180 days ago'
when (Termination_Pregnancy_To_Culture_Order>180 and Termination_Pregnancy_To_Culture_Order is not null) then 'Pregnancy terminated before 180 days ago'
else 'Is pregnant' end as Pregnancy_Status
from All_Pregnant_lab_tests lr left join All_Terminated_Pregnancy tp using(anon_id,order_proc_id_coded)
)
select anon_id,
order_proc_id_coded,
case when Pregnancy_Status='Is pregnant' then 1 else 0 end As Preganat,
case when (Pregnancy_Status='Is pregnant' or Pregnancy_Status='Termination of pregnancy censored 7 days ago')then 1 else 0 end As Preganat_7days_ago,
case when (Pregnancy_Status='Is pregnant' or Pregnancy_Status='Termination of pregnancy censored 14 days ago') then 1 else 0 end As Preganat_14days,
case when (Pregnancy_Status='Is pregnant' or Pregnancy_Status='Termination of pregnancy censored 30 days ago') then 1 else 0 end As Preganat_30days,
case when (Pregnancy_Status='Is pregnant' or Pregnancy_Status='Termination of pregnancy censored 90 days ago') then 1 else 0 end As Preganat_90days,
case when (Pregnancy_Status='Is pregnant' or Pregnancy_Status='Termination of pregnancy censored 180 days ago') then 1 else 0 end As Preganat_180days,
from All_Non_Terminted_Pregnancy
)

