# ER admissions between 2009 and 2019 where patient was admitted to the hospital and was above 18 yo
-- WITH er_admits AS (
-- SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
-- FROM `shc_core.adt`
-- WHERE pat_class_c = "112" AND pat_service = "Emergency"
-- GROUP BY anon_id, pat_enc_csn_id_coded),

-- er_admits_adults AS (
-- SELECT DISTINCT ea.* 
-- FROM er_admits ea
-- INNER JOIN `shc_core.demographic` demo
-- USING (anon_id)
-- WHERE DATE_DIFF(CAST(ea.er_admit_time as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
-- AND EXTRACT(YEAR FROM ea.er_admit_time) BETWEEN 2009 AND 2019
-- ),

-- has_inp_code AS (
-- SELECT DISTINCT anon_id, pat_enc_csn_id_coded
-- FROM
--   (SELECT DISTINCT ea.anon_id, ea.pat_enc_csn_id_coded,
--   MAX(CASE WHEN adt.base_pat_class_c = 1 THEN 1 ELSE 0 END) has_inpatient 
--   FROM er_admits_adults ea
--   INNER JOIN shc_core.adt adt
--   USING (pat_enc_csn_id_coded)
--   GROUP BY ea.anon_id, ea.pat_enc_csn_id_coded) t
-- WHERE has_inpatient = 1
-- )

-- SELECT DISTINCT anon_id FROM has_inp_code # Patients
-- SELECT DISTINCT pat_enc_csn_id_coded FROM has_inp_code # Admissions


### Abx ordered and Cultures Ordered Within 24 hours
# Admissions
-- SELECT DISTINCT
--   pat_enc_csn_id_coded
-- FROM
--   `mining-clinical-decisions.abx.abx_orders_within_24_hrs` a
-- INNER JOIN
--   `mining-clinical-decisions.abx.culture_orders_within_24_hrs` c
-- USING
--   (pat_enc_csn_id_coded)
-- WHERE
--   EXTRACT(YEAR FROM order_time) BETWEEN 2009 AND 2019 # slight difference than if using ER admit time but fine bc this is what we use in analysis anyway 
# Patients
-- SELECT DISTINCT
--   a.anon_id
-- FROM
--   `mining-clinical-decisions.abx.abx_orders_within_24_hrs` a
-- INNER JOIN
--   `mining-clinical-decisions.abx.culture_orders_within_24_hrs` c
-- USING
--   (pat_enc_csn_id_coded)
-- WHERE
--   EXTRACT(YEAR FROM order_time) BETWEEN 2009 AND 2019 # slight difference than if using ER admit time but fine bc this is what we use in analysis anyway 


# No Abx or cultures ordered in prior 2 weeks
# Admissions
-- SELECT DISTINCT pat_enc_csn_id_coded
-- FROM `mining-clinical-decisions.abx.final_ast_labels` 
-- WHERE EXTRACT(YEAR FROM index_time) BETWEEN 2009 AND 2019

# Patients
SELECT DISTINCT anon_id
FROM `mining-clinical-decisions.abx.final_cohort_table` 
WHERE EXTRACT(YEAR FROM index_time) BETWEEN 2009 AND 2019


