CREATE OR REPLACE TABLE `mining-clinical-decisions.abx.final_cohort_table` AS
(
SELECT anon_id, pat_enc_csn_id_coded, index_time,
CASE WHEN abx_stopped_2_days = 1
AND not_discharged_with_orals = 1
AND no_pos_cult_2_weeks_later = 1
AND no_pos_cult_within_day = 1
AND no_inf_dx_codes = 1
THEN 1 ELSE 0 END not_infected
FROM `mining-clinical-decisions.abx.cohort_not_infected_rules`
);

CREATE OR REPLACE TABLE `mining-clinical-decisions.abx.final_cohort_table` AS (
WITH joined_table AS (
SELECT c.*, l.Cefazolin, l.Ceftriaxone, l.Cefepime, l.Zosyn, l.Vancomycin, l.Meropenem,
l.Ampicillin, l.Ciprofloxacin, l.Vancomycin_Meropenem, l.Vancomycin_Zosyn, l.Vancomycin_Ceftriaxone,
l.Vancomycin_Cefepime
FROM `mining-clinical-decisions.abx.final_cohort_table` c
LEFT JOIN `mining-clinical-decisions.abx.final_ast_labels` l
USING (pat_enc_csn_id_coded)
),

labels as (SELECT anon_id, pat_enc_csn_id_coded, index_time,
CASE WHEN Cefazolin = 1 OR (Cefazolin IS NULL AND not_infected = 1) THEN 1 # if suscept or not infected
WHEN Cefazolin = 0 THEN 0 # if resistant
ELSE NULL END Cefazolin, # if no bug growth but not necessarily not infected
CASE WHEN Ceftriaxone = 1 OR (Ceftriaxone IS NULL AND not_infected = 1) THEN 1
WHEN Ceftriaxone = 0 THEN 0
ELSE NULL END Ceftriaxone,
CASE WHEN Cefepime = 1 OR (Cefepime IS NULL AND not_infected = 1) THEN 1
WHEN Cefepime = 0 THEN 0
ELSE NULL END Cefepime,
CASE WHEN Zosyn = 1 OR (Zosyn IS NULL AND not_infected = 1) THEN 1
WHEN Zosyn = 0 THEN 0
ELSE NULL END Zosyn,
CASE WHEN Vancomycin = 1 OR (Vancomycin IS NULL AND not_infected = 1) THEN 1
WHEN Vancomycin = 0 THEN 0
ELSE NULL END Vancomycin,
CASE WHEN Meropenem = 1 OR (Meropenem IS NULL AND not_infected = 1) THEN 1
WHEN Meropenem = 0 THEN 0
ELSE NULL END Meropenem,
CASE WHEN Ampicillin = 1 OR (Ampicillin IS NULL AND not_infected = 1) THEN 1
WHEN Ampicillin = 0 THEN 0
ELSE NULL END Ampicillin,
CASE WHEN Ciprofloxacin = 1 OR (Ciprofloxacin IS NULL AND not_infected = 1) THEN 1
WHEN Ciprofloxacin = 0 THEN 0
ELSE NULL END Ciprofloxacin,
CASE WHEN Vancomycin_Cefepime = 1 OR (Vancomycin_Cefepime IS NULL AND not_infected = 1) THEN 1
WHEN Vancomycin_Cefepime = 0 THEN 0
ELSE NULL END Vancomycin_Cefepime,
CASE WHEN Vancomycin_Ceftriaxone = 1 OR (Vancomycin_Ceftriaxone IS NULL AND not_infected = 1) THEN 1
WHEN Vancomycin_Ceftriaxone = 0 THEN 0
ELSE NULL END Vancomycin_Ceftriaxone,
CASE WHEN Vancomycin_Meropenem = 1 OR (Vancomycin_Meropenem IS NULL AND not_infected = 1) THEN 1
WHEN Vancomycin_Meropenem = 0 THEN 0
ELSE NULL END Vancomycin_Meropenem,
CASE WHEN Vancomycin_Zosyn = 1 OR (Vancomycin_Zosyn IS NULL AND not_infected = 1) THEN 1
WHEN Vancomycin_Zosyn = 0 THEN 0
ELSE NULL END Vancomycin_Zosyn




FROM joined_table)

SELECT l.*, CASE WHEN l.Cefazolin IS NULL THEN 1 ELSE 0 END label_unobserved
FROM labels l
)
