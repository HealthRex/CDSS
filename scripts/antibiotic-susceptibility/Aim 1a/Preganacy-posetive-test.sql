with pregnancy_results as (
select anon_id,
order_time_jittered_utc as order_time_utc ,
1 as pregnanat,
from `som-nero-phi-jonc101.shc_core_2023.lab_result` lr
where (LOWER(lr.group_lab_name) LIKE '%pregnancy%' or LOWER(lr.lab_name) like '%pregnancy%')
      AND LOWER(lr.ord_value) NOT LIKE '%neg%'
      AND LOWER(lr.ord_value) NOT LIKE '%device%'
      AND LEFT(lr.ord_value, 1) NOT LIKE '<'
),
base_cohort as (
select anon_id,order_proc_id_coded,order_time_jittered_utc from `som-nero-phi-jonc101.fateme_db.antibiotic_cohort_temp`
),
select b.*,
1 as Positive_pregnancy
from base_cohort b inner join pregnancy_results using (anon_id)
Where 
 (DATE_DIFF(EXTRACT(DATE FROM b.order_time_jittered_utc),EXTRACT(DATE FROM pregnancy_results.order_time_utc), DAY) <= +270)
 AND
 (DATE_DIFF(EXTRACT(DATE FROM b.order_time_jittered_utc),EXTRACT(DATE FROM pregnancy_results.order_time_utc), DAY) >= -1)
