SELECT cens.*, DATE_DIFF(CAST(cens.index_time as DATE), demo.BIRTH_DATE_JITTERED, YEAR) age,
demo.CANONICAL_RACE, demo.CANONICAL_ETHNICITY, demo.GENDER, demo.LANGUAGE, demo.MARITAL_STATUS, demo.INSURANCE_PAYOR_NAME, demo.DEATH_DATE_JITTERED
FROM `mining-clinical-decisions.conor_db.abx_cohort_not_censored_label` cens
INNER JOIN `shc_core.demographic` demo
USING (anon_id)
WHERE DATE_DIFF(CAST(cens.index_time as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
ORDER BY obs_id