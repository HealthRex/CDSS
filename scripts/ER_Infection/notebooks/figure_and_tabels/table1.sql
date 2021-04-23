WITH cohort AS (
SELECT DISTINCT
  anon_id, pat_enc_csn_id_coded, index_time, EXTRACT(YEAR FROM index_time) year
FROM 
  `mining-clinical-decisions.abx.final_ast_labels`
WHERE 
    EXTRACT(YEAR FROM index_time) BETWEEN 2009 AND 2019
),

adt_dep as (
SELECT DISTINCT
  adt.pat_enc_csn_id_coded, 
  FIRST_VALUE(dm.department_name) OVER 
  (PARTITION BY adt.pat_enc_csn_id_coded ORDER BY adt.effective_time_jittered_utc) department_name,
FROM 
  `shc_core.adt` adt
INNER JOIN
  `som-nero-phi-jonc101.shc_core.dep_map` dm
USING
  (department_id)
)

SELECT DISTINCT 
  dep.department_name,
  DATE_DIFF(CAST(c.index_time as DATE), d.BIRTH_DATE_JITTERED, year) age,
  c.pat_enc_csn_id_coded,
  c.year,
  d.ANON_ID, d.GENDER, d.CANONICAL_RACE, d.CANONICAL_ETHNICITY,
  CASE WHEN d.LANGUAGE = "English" THEN "English"
  ELSE "Non-English" END LANGUAGE,
  CASE WHEN d.INSURANCE_PAYOR_NAME = "MEDICARE" THEN "Medicare"
  WHEN d.INSURANCE_PAYOR_NAME = "MEDI-CAL" THEN "Medi-Cal"
  ELSE "Other" END INSURANCE_PAYOR_NAME
FROM 
  `som-nero-phi-jonc101.shc_core.demographic` d
INNER JOIN
  cohort c
ON
  d.ANON_ID = c.anon_id
INNER JOIN
  adt_dep dep
ON
  c.pat_enc_csn_id_coded = dep.pat_enc_csn_id_coded
