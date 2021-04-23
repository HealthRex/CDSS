WITH cult_result as (
SELECT DISTINCT co.anon_id, co.pat_enc_csn_id_coded, co.order_proc_id_coded, cs.organism
FROM `mining-clinical-decisions.conor_db.abx_culture_orders_within_4_hours` co
INNER JOIN 
  (SELECT DISTINCT pat_enc_csn_id_coded FROM `mining-clinical-decisions.conor_db.abx_med_orders_given_and_stopped_info`) cults_and_abx_csns
USING (pat_enc_csn_id_coded)
LEFT JOIN `shc_core.culture_sensitivity` cs
USING (order_proc_id_coded)
ORDER BY co.anon_id, co.pat_enc_csn_id_coded
),

infected as ( -- make sure coag neg staph is deemed a contaminent
SELECT DISTINCT pat_enc_csn_id_coded
FROM
  (SELECT pat_enc_csn_id_coded, MAX(CASE WHEN organism IS NOT NULL AND organism <> "COAG NEGATIVE STAPHYLOCOCCUS" THEN 1 ELSE 0 END) any_positive
  FROM cult_result
  GROUP BY pat_enc_csn_id_coded) t
WHERE any_positive = 1
)

SELECT ROW_NUMBER() OVER (ORDER BY cr.pat_enc_csn_id_coded) obs_id, cr.anon_id, cr.pat_enc_csn_id_coded, 
CASE WHEN ni.pat_enc_csn_id_coded IS NOT NULL THEN 1 ELSE 0 END not_infected,
CASE WHEN i.pat_enc_csn_id_coded IS NOT NULL THEN 1 ELSE 0 END infected,
CASE WHEN ni.pat_enc_csn_id_coded IS NULL AND i.pat_enc_csn_id_coded IS NULL THEN 0 ELSE 1 END not_censored,  --- this is what we want to estimate P(C = 0 | x)
min(mo.order_start_time_utc) index_time
FROM cult_result cr
LEFT JOIN infected i
USING (pat_enc_csn_id_coded)
LEFT JOIN `mining-clinical-decisions.conor_db.abx_not_infected_csns` ni
USING (pat_enc_csn_id_coded)
LEFT JOIN `mining-clinical-decisions.conor_db.abx_med_orders_last_4_hours` mo
USING (pat_enc_csn_id_coded)
GROUP BY cr.anon_id, cr.pat_enc_csn_id_coded,  not_infected, infected, not_censored


