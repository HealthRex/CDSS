WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

include_abx as (
SELECT med_description
FROM `mining-clinical-decisions.conor_db.abx_include` 
WHERE is_include_abx = 1
)

SELECT ea.anon_id, ea.pat_enc_csn_id_coded, om.pat_enc_csn_id_coded om_csn, om.order_med_id_coded, om.med_description, om.order_start_time_utc
FROM `shc_core.order_med` om
INNER JOIN er_admits ea
USING (anon_id)
INNER JOIN include_abx
USING (med_description)
WHERE TIMESTAMP_DIFF(om.order_start_time_utc, ea.er_admit_time, HOUR) BETWEEN 0 AND 4
ORDER BY anon_id, om.order_start_time_utc