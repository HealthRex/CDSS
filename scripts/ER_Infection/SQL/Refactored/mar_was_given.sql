WITH mar_interm AS (
SELECT abx.med_description, mar.line, mar.mar_action, mar.route, mar_duration, mar.taken_time_jittered_utc, om.discon_time_jittered_utc, om.order_status, om.freq_name, om.number_of_times, om.order_med_id_coded
FROM `mining-clinical-decisions.abx.abx_types` abx
LEFT JOIN `shc_core.order_med` om
USING (med_description)
INNER JOIN `shc_core.mar` mar
USING (order_med_id_coded)
WHERE abx.is_include_abx = 1 OR abx.affects_not_infected_label = 1
),

t as (
SELECT DISTINCT order_med_id_coded, mar_action, min(taken_time_jittered_utc) taken_time_jittered_utc
FROM mar_interm 
GROUP BY order_med_id_coded, mar_action),

tt as (
SELECT order_med_id_coded, STRING_AGG( mar_action ORDER BY taken_time_jittered_utc) action_list
FROM t
GROUP BY order_med_id_coded )

SELECT action_list, COUNT (DISTINCT order_med_id_coded) cnt
FROM tt
LEFT JOIN mar_interm mar
USING (order_med_id_coded)
WHERE action_list NOT LIKE "%Given%" AND action_list NOT LIKE "%Complete%" AND action_list NOT LIKE "%Stopped%"
AND action_list NOT LIKE "%New Bag%"
GROUP BY action_list
ORDER BY cnt DESC