-- For each abx order, find whether it was given, and an abx stop time. 
CREATE OR REPLACE TABLE mining-clinical-decisions.abx.abx_orders_given_and_stopped_include_oral AS (
WITH mar_action_interim as (
SELECT abx.*, mar.line, mar.mar_action, mar.route, mar_duration, mar.taken_time_jittered_utc, om.discon_time_jittered_utc, om.order_status, om.freq_name, om.number_of_times
FROM `mining-clinical-decisions.abx.abx_orders_within_24_hrs_include_oral`  abx
INNER JOIN `mining-clinical-decisions.abx.culture_orders_within_24_hrs`  cult
USING (anon_id, pat_enc_csn_id_coded)
LEFT JOIN `shc_core.mar` mar
USING (order_med_id_coded)
LEFT JOIN `shc_core.order_med` om
USING (order_med_id_coded) 
ORDER BY anon_id, order_start_time_utc, order_med_id_coded, taken_time_jittered_utc
), 

distinct_actions as (
SELECT DISTINCT order_med_id_coded, mar_action, min(taken_time_jittered_utc) taken_time_jittered_utc
FROM mar_action_interim 
GROUP BY order_med_id_coded, mar_action),

grouped_actions as (
SELECT order_med_id_coded, 
max(taken_time_jittered_utc) last_mar_action_time,
CASE WHEN STRING_AGG(mar_action) IS NULL THEN NULL
ELSE STRING_AGG( mar_action ORDER BY taken_time_jittered_utc) END action_list
FROM distinct_actions
GROUP BY order_med_id_coded),

orders_with_info as 
(SELECT DISTINCT abx.anon_id, abx.pat_enc_csn_id_coded, abx.order_time, abx.med_description, ga.order_med_id_coded, ga.action_list, ga.last_mar_action_time,
-- Was_Given should be 1 if Given, Complete(d), New Bag, or Stopped exists in action_list
CASE WHEN ga.action_list LIKE "%Given%" OR action_list  LIKE "%Complete%" OR action_list LIKE "%Stopped%"
OR action_list LIKE "%New Bag%" THEN 1
-- Should be 1 if was_given flag from mar_action_was_given table is 1 
WHEN wg.was_given = 1 THEN 1
ELSE 0 END was_given, -- should handle when action_list is null 
FROM `mining-clinical-decisions.abx.abx_orders_within_24_hrs_include_oral`  abx
INNER JOIN `mining-clinical-decisions.abx.culture_orders_within_24_hrs`  cult
USING (anon_id, pat_enc_csn_id_coded)
LEFT JOIN grouped_actions ga
USING (order_med_id_coded)
LEFT JOIN `mining-clinical-decisions.abx.mar_was_given`  wg
USING (action_list))

SELECT DISTINCT owi.*, om.discon_time_jittered_utc,
-- When no mar actions listed for order than infer wasn't given and abx stop time will be order time
CASE WHEN was_given = 0 AND action_list IS NULL AND om.discon_time_jittered_utc IS NULL THEN owi.order_time
-- If not in mar actions but discontinued time listed in order_med then abx stop time is discontinued time
WHEN was_given = 0 AND action_list IS NULL THEN om.discon_time_jittered_utc 
-- If in mar but nothing to infer was actually given, then take last known timestamp as stop time. 
WHEN was_given = 0 AND last_mar_action_time > discon_time_jittered_utc THEN last_mar_action_time
WHEN was_given = 0 AND last_mar_action_time < discon_time_jittered_utc THEN discon_time_jittered_utc
-- If in mar and was given but not discontinued time listed in order_med, then take timestamp of last mar action
WHEN was_given = 1 AND discon_time_jittered_utc IS NULL THEN last_mar_action_time
-- If in mar and was given and there exists a discontinued time, then take latest timestamp between that and last mar action
WHEN was_given = 1 AND last_mar_action_time > discon_time_jittered_utc THEN last_mar_action_time
WHEN was_given = 1 AND last_mar_action_time < discon_time_jittered_utc THEN discon_time_jittered_utc END abx_stop_time
FROM orders_with_info owi
LEFT JOIN (
     -- Gets columns we need from order med and finds order time from 2018 extract when missing in 2020 extract 
     SELECT om.anon_id, om.pat_enc_csn_id_coded, om.med_description, om.order_med_id_coded, om.discon_time_jittered_utc,
     CASE WHEN om.order_inst_utc IS NULL THEN omm.order_time_jittered_utc ELSE om.order_inst_utc END order_time
     FROM `shc_core.order_med` om
     LEFT JOIN `starr_datalake2018.order_med` omm
     USING (order_med_id_coded)
) om
USING (order_med_id_coded)
LEFT JOIN `shc_core.mar` mar
USING (order_med_id_coded)
ORDER BY anon_id, pat_enc_csn_id_coded, order_time
)