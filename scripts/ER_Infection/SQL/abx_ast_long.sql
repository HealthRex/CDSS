WITH infected_csns AS (
SELECT DISTINCT pat_enc_csn_id_coded
FROM `mining-clinical-decisions.conor_db.abx_cohort_not_censored_no_kids_no_prior` inf
WHERE infected = 1
),

culture_ids AS (
SELECT DISTINCT pat_enc_csn_id_coded, order_proc_id_coded
FROM `mining-clinical-decisions.conor_db.abx_culture_orders_within_4_hours` cults
INNER JOIN infected_csns
USING (pat_enc_csn_id_coded)
)

SELECT DISTINCT pat_enc_csn_id_coded, order_proc_id_coded, cs.sens_organism_sid, cs.line, cs.description, cs.organism, cs.antibiotic, cs.suscept
FROM `shc_core.culture_sensitivity` cs
INNER JOIN culture_ids
USING (order_proc_id_coded)
ORDER BY pat_enc_csn_id_coded, order_proc_id_coded, cs.sens_organism_sid, cs.line