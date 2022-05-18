SELECT abx.*, mar.line, mar.mar_action, mar.route, mar_duration, mar.taken_time_jittered_utc, om.discon_time_jittered_utc, om.order_status, om.freq_name, om.number_of_times
FROM `mining-clinical-decisions.conor_db.abx_med_orders_last_4_hours` abx
INNER JOIN `mining-clinical-decisions.conor_db.abx_culture_orders_within_4_hours` cult
USING (anon_id, pat_enc_csn_id_coded)
LEFT JOIN `shc_core.mar` mar
USING (order_med_id_coded)
LEFT JOIN `shc_core.order_med` om
USING (order_med_id_coded) 
ORDER BY anon_id, order_start_time_utc, order_med_id_coded, taken_time_jittered_utc
