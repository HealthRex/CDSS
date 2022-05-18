-- Gets all antibiotic orders that happen within 24 hours
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

include_abx as (
SELECT med_description
FROM `mining-clinical-decisions.abx.abx_types` 
WHERE is_include_abx = 1
)

SELECT ea.anon_id, ea.pat_enc_csn_id_coded, om.pat_enc_csn_id_coded om_csn, om.order_med_id_coded, om.med_description, om.order_time
FROM (
     -- Gets columns we need from order med and finds order time from 2018 extract when missing in 2020 extract 
     SELECT om.anon_id, om.pat_enc_csn_id_coded, om.med_description, om.order_med_id_coded,
     CASE WHEN om.order_inst_utc IS NULL THEN omm.order_time_jittered_utc ELSE om.order_inst_utc END order_time
     FROM `shc_core.order_med` om
     LEFT JOIN `starr_datalake2018.order_med` omm
     USING (order_med_id_coded)
     WHERE om.order_class_name <> "Historical Med"
) om

INNER JOIN er_admits_adults ea
USING (anon_id)
INNER JOIN include_abx
USING (med_description)
INNER JOIN has_inp_code
ON has_inp_code.pat_enc_csn_id_coded = ea.pat_enc_csn_id_coded
WHERE TIMESTAMP_DIFF(om.order_time, ea.er_admit_time, HOUR) BETWEEN 0 AND 24
ORDER BY anon_id, om.order_time