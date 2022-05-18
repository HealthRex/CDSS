-- Finds subset of csns in mining-clinical-decisions.conor_db.abx_cohort_not_censored_no_kids 
-- where cultures/abx have not been ordered for patient within 14 days prior of the admit time for the ER encounter
-- we are using for our observation. 
WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

csns_with_prior_abx AS (
SELECT DISTINCT c.pat_enc_csn_id_coded
FROM `mining-clinical-decisions.conor_db.abx_cohort_not_censored_no_kids` c
INNER JOIN (SELECT pat_enc_csn_id_coded, er_admit_time FROM er_admits) ea
USING (pat_enc_csn_id_coded)
LEFT JOIN 
  (SELECT *
  FROM `shc_core.order_med` om
  INNER JOIN `mining-clinical-decisions.conor_db.abx_include` abx
  USING (med_description)
  WHERE abx.is_include_abx = 1) abx
USING (anon_id)
WHERE TIMESTAMP_DIFF(ea.er_admit_time, abx.order_start_time_utc, MINUTE) BETWEEN 0 AND 14*24*60 
), 

csns_with_prior_pos_cult AS (
SELECT DISTINCT c.pat_enc_csn_id_coded
FROM `mining-clinical-decisions.conor_db.abx_cohort_not_censored_no_kids` c
INNER JOIN (SELECT pat_enc_csn_id_coded, er_admit_time FROM er_admits) ea
USING (pat_enc_csn_id_coded)
LEFT JOIN 
  (SELECT * 
  FROM `shc_core.culture_sensitivity` cs
  INNER JOIN `mining-clinical-decisions.conor_db.abx_include_exclude_cultures` c
  USING (description)
  WHERE c.included = 1 OR c.excluded = 1) pc
USING (anon_id)
WHERE TIMESTAMP_DIFF(ea.er_admit_time, pc.order_time_jittered_utc, MINUTE) BETWEEN 0 AND 14*24*60
),

csns_to_remove as (
SELECT pat_enc_csn_id_coded
FROM csns_with_prior_abx

UNION DISTINCT

SELECT pat_enc_csn_id_coded
FROM csns_with_prior_pos_cult
)

SELECT c.*
FROM `mining-clinical-decisions.conor_db.abx_cohort_not_censored_no_kids` c
LEFT JOIN csns_to_remove rm
USING (pat_enc_csn_id_coded)
WHERE rm.pat_enc_csn_id_coded IS NULL
