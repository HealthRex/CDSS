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

any_growth as -- make sure coag neg staph is deemed a contaminent
(SELECT pat_enc_csn_id_coded, MAX(CASE WHEN organism IS NOT NULL AND organism <> "COAG NEGATIVE STAPHYLOCOCCUS" THEN 1 ELSE 0 END) any_positive
FROM cult_result
GROUP BY pat_enc_csn_id_coded),

start_stop_time as (
SELECT anon_id, pat_enc_csn_id_coded, max(was_given) any_abx_given, min(order_start_time_utc) first_abx_order_time, max(abx_stop_time) last_abx_stop_time
FROM `mining-clinical-decisions.conor_db.abx_temp_14_day_orders` 
GROUP BY anon_id, pat_enc_csn_id_coded
ORDER BY anon_id, pat_enc_csn_id_coded),

er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

-- Looks for positive cultures in include/exclude set of cultures that were ordered within 14 days of er_stay, but not within 4 hours. Patients with these should not be labelled not infected.
pos_cults_outside_4hrs AS (
SELECT DISTINCT ea.pat_enc_csn_id_coded
FROM er_admits ea
INNER JOIN (SELECT pat_enc_csn_id_coded FROM any_growth WHERE any_positive = 0) no_growth_in_4
USING (pat_enc_csn_id_coded)
RIGHT JOIN `shc_core.culture_sensitivity` cs
USING (anon_id)
INNER JOIN `mining-clinical-decisions.conor_db.abx_include_exclude_cultures` inec
USING (description)
WHERE TIMESTAMP_DIFF(cs.order_time_jittered_utc, ea.er_admit_time, DAY) BETWEEN 0 AND 14
AND (inec.included = 1 OR inec.excluded = 1)
),

abx_stop_time AS (
SELECT ss.pat_enc_csn_id_coded, TIMESTAMP_DIFF(ss.last_abx_stop_time, ea.er_admit_time, DAY) time_until_abx_stop
FROM start_stop_time ss
INNER JOIN er_admits ea
USING (pat_enc_csn_id_coded))

SELECT DISTINCT pat_enc_csn_id_coded
FROM cult_result cr
INNER JOIN (SELECT DISTINCT pat_enc_csn_id_coded FROM any_growth WHERE any_positive = 0) pos_csns -- must not have positive culture from 4 hr orders
USING (pat_enc_csn_id_coded)
LEFT JOIN pos_cults_outside_4hrs pos_cults_14
USING (pat_enc_csn_id_coded)
INNER JOIN abx_stop_time abx_stop
USING (pat_enc_csn_id_coded)
WHERE time_until_abx_stop = 0 -- must have stopped abx within first hour of admit time (and not have restarted the for 14 days).
AND pos_cults_14.pat_enc_csn_id_coded IS NULL -- must not be a csn with a positive culture within 14 days. 

