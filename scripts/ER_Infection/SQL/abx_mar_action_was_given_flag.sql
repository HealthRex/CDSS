-- This query created all unique mar_action lists for a particular order_id using timestamp of first time
-- a particular action was taken (eg. given can be listed more than once for a particular order_id). 
-- This table was then manually editted to add was_given and unsure_if_given columsn to state whether
-- the mar_action sequence implies the abx was actually administered and whether I was confident about
-- it. 
WITH t as (
SELECT DISTINCT order_med_id_coded, mar_action, min(taken_time_jittered_utc) taken_time_jittered_utc
FROM `mining-clinical-decisions.conor_db.abx_cohort_mar_interm` 
GROUP BY order_med_id_coded, mar_action),

tt as (
SELECT order_med_id_coded, STRING_AGG( mar_action ORDER BY taken_time_jittered_utc) action_list
FROM t
GROUP BY order_med_id_coded )

SELECT action_list, COUNT (DISTINCT order_med_id_coded) cnt
FROM tt
LEFT JOIN `mining-clinical-decisions.conor_db.abx_cohort_mar_interm` mar
USING (order_med_id_coded)
WHERE action_list NOT LIKE "%Given%" AND action_list NOT LIKE "%Completed%" AND action_list NOT LIKE "%Stopped%"
GROUP BY action_list
ORDER BY cnt DESC