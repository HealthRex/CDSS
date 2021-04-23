-- For each CSN where abx were ordered and cultures were ordered both within 4 hrs of er admit, find all abx that were ordered within 14 days of er admit
-- and find the time the last antibiotic was stopped. Will use this as as my discontinued time to help build "not_infected" labels. This creates a temp table
-- that lists each abx order, whether it was administered, and the time it was stopped for all ordered IV, IM, Oral antibiotics within 14 days of er admit.
-- Need to group by csn, and take the max abx_stop_time to get discontinued time.  Saving this temp file for future sanity checks. 
WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

include_abx as (
SELECT med_description
FROM `mining-clinical-decisions.conor_db.abx_include` 
WHERE is_include_abx = 1
),

frteen_day_abx as (
SELECT ea.anon_id, ea.pat_enc_csn_id_coded, om.pat_enc_csn_id_coded om_csn, om.order_med_id_coded, om.med_description, om.order_start_time_utc
FROM `shc_core.order_med` om
INNER JOIN er_admits ea
USING (anon_id)
INNER JOIN 
  (SELECT DISTINCT anon_id FROM
   `mining-clinical-decisions.conor_db.abx_med_orders_given_and_stopped_info`) has_abx_orders
USING (anon_id)
INNER JOIN include_abx
USING (med_description)
WHERE TIMESTAMP_DIFF(om.order_start_time_utc, ea.er_admit_time, DAY) BETWEEN 0 AND 14
ORDER BY anon_id, om.order_start_time_utc),

mar_action_interim as (
SELECT abx.*, mar.line, mar.mar_action, mar.route, mar_duration, mar.taken_time_jittered_utc, om.discon_time_jittered_utc, om.order_status, om.freq_name, om.number_of_times
FROM frteen_day_abx abx
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
(SELECT DISTINCT abx.anon_id, abx.pat_enc_csn_id_coded, abx.order_start_time_utc, abx.med_description, ga.order_med_id_coded, ga.action_list, ga.last_mar_action_time,
-- Was_Given should be 1 if Given, Completed, or Stopped exists in action_list
CASE WHEN ga.action_list LIKE "%Given%" OR action_list  LIKE "%Completed%" OR action_list LIKE "%Stopped%" THEN 1
-- Shoudl be 1 if was_given flag from mar_action_was_given table is 1 
WHEN wg.was_given = 1 THEN 1
ELSE 0 END was_given,
FROM frteen_day_abx abx
LEFT JOIN grouped_actions ga
USING (order_med_id_coded)
LEFT JOIN `mining-clinical-decisions.conor_db.abx_mar_actions_was_given_flag` wg
USING (action_list))

SELECT DISTINCT owi.*, om.discon_time_jittered_utc,
CASE WHEN was_given = 0 AND action_list IS NULL AND om.discon_time_jittered_utc IS NULL THEN owi.order_start_time_utc
WHEN was_given = 0 AND action_list IS NULL THEN om.discon_time_jittered_utc 
WHEN was_given = 0 AND last_mar_action_time > discon_time_jittered_utc THEN last_mar_action_time
WHEN was_given = 0 AND last_mar_action_time < discon_time_jittered_utc THEN discon_time_jittered_utc
WHEN was_given = 1 AND discon_time_jittered_utc IS NULL THEN last_mar_action_time
WHEN was_given = 1 AND last_mar_action_time > discon_time_jittered_utc THEN last_mar_action_time
WHEN was_given = 1 AND last_mar_action_time < discon_time_jittered_utc THEN discon_time_jittered_utc END abx_stop_time
FROM orders_with_info owi
LEFT JOIN `shc_core.order_med` om
USING (order_med_id_coded)
LEFT JOIN `shc_core.mar` mar
USING (order_med_id_coded)
INNER JOIN 
  (SELECT DISTINCT pat_enc_csn_id_coded FROM
   `mining-clinical-decisions.conor_db.abx_med_orders_given_and_stopped_info`) has_abx_orders
ON owi.pat_enc_csn_id_coded = has_abx_orders.pat_enc_csn_id_coded  -- should only keep enc's from ER visit that had the cultures taken
ORDER BY anon_id, pat_enc_csn_id_coded, order_start_time_utc