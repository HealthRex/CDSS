WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

-- Finds included cultures in order_proc, removes ED stays with excluded cultures,
-- Forces cultures to appear in lab_results
culture_orders as (
SELECT DISTINCT ea.anon_id, ea.pat_enc_csn_id_coded, op.pat_enc_csn_id_coded as op_csn, op.description, op.order_proc_id_coded, op.order_time_jittered_utc,
ec.included, ec.excluded
FROM `shc_core.order_proc` op
INNER JOIN er_admits ea
USING (anon_id) --- will include overlapping csns assciated with order (if they exist)
INNER JOIN `shc_core.lab_result` lr -- Forces order to appear in lab results - this is where selection bias could creep in. 
ON op.order_proc_id_coded = lr.order_id_coded
INNER JOIN `mining-clinical-decisions.conor_db.abx_include_exclude_cultures` ec 
USING (description)
WHERE TIMESTAMP_DIFF(op.order_time_jittered_utc, ea.er_admit_time, HOUR) BETWEEN 0 AND 4),

-- HAS AT LEAST ONE INCLUDE CULTURE AND NO EXCLUDE CULTRES
c_o_include_flag as (
SELECT pat_enc_csn_id_coded, MAX(included) included, MAX(excluded) excluded
FROM culture_orders 
GROUP BY pat_enc_csn_id_coded)

SELECT DISTINCT culture_orders.* 
FROM culture_orders
INNER JOIN c_o_include_flag co
USING (pat_enc_csn_id_coded)
WHERE co.included = 1 AND co.excluded = 0
ORDER BY pat_enc_csn_id_coded, order_time_jittered_utc