# Adult patients with admit codes from the ER who get blood, urine, csf, or fluid cultures ordered. 
WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

er_admits_adults AS (
SELECT DISTINCT ea.* 
FROM er_admits ea
INNER JOIN `shc_core.demographic` demo
USING (anon_id)
WHERE DATE_DIFF(CAST(ea.er_admit_time as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
),

has_inp_code AS (
SELECT DISTINCT pat_enc_csn_id_coded
FROM
  (SELECT DISTINCT ea.pat_enc_csn_id_coded,
  MAX(CASE WHEN adt.base_pat_class_c = 1 THEN 1 ELSE 0 END) has_inpatient 
  FROM er_admits_adults ea
  INNER JOIN shc_core.adt adt
  USING (pat_enc_csn_id_coded)
  GROUP BY ea.pat_enc_csn_id_coded) t
WHERE has_inpatient = 1
),

include_culture as (
SELECT description
FROM `mining-clinical-decisions.abx.culture_types`  
WHERE include = 1
)

SELECT ea.anon_id, ea.pat_enc_csn_id_coded, op.pat_enc_csn_id_coded op_csn, op.order_proc_id_coded, op.description, op.order_time_jittered_utc
FROM `shc_core.order_proc` op
INNER JOIN er_admits_adults ea
USING (anon_id)
INNER JOIN include_culture
USING (description)
INNER JOIN has_inp_code
ON has_inp_code.pat_enc_csn_id_coded = ea.pat_enc_csn_id_coded
WHERE TIMESTAMP_DIFF(op.order_time_jittered_utc, ea.er_admit_time, HOUR) BETWEEN 0 AND 24
ORDER BY anon_id, op.order_time_jittered_utc