#######################################################################################################################
# Create temporary wide table for easier implementation of antibiotic inference logic
#######################################################################################################################

# Create/replace the existing culture_sensitivity_inferred table
CREATE OR REPLACE TABLE `mvm_abx.culture_sensitivity_inferred_temp_wide` AS 

# Create cleaned susceptibility table removing non-alphabetic characters from antibiotic name
# And selecting only urine, blood, or respiratory cultures
WITH culture_sensitivity_clean AS (
  SELECT anon_id, order_proc_id_coded, description, organism, order_time_jittered, result_time_jittered,
    UPPER(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(antibiotic, r'(\.)|\s\([^()]*\)', ''), '/', '_'))) as antibiotic_clean,
    CASE
      WHEN upper(suscept) = 'SUSCEPTIBLE' THEN 0
      ELSE 1
    END as resistance,
  FROM `shc_core_2023.culture_sensitivity`
)

# Create wide-format susceptibility table for a select list of antibiotics
SELECT DISTINCT * FROM culture_sensitivity_clean
PIVOT(MAX(resistance) FOR antibiotic_clean IN ('OXACILLIN', 'AMPICILLIN', 'CEFAZOLIN', 'CEFTRIAXONE', 'CEFEPIME', 
                                              'PIPERACILLIN_TAZOBACTAM', 'CIPROFLOXACIN', 'TRIMETHOPRIM_SULFAMETHOXAZOLE',
                                              'MEROPENEM', 'VANCOMYCIN'));

#######################################################################################################################
# Antibiotic susceptibility inference logic
#######################################################################################################################

# Infer intrinsic Pseudomonas resistance
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  OXACILLIN = CASE WHEN organism LIKE '%PSEUDOMONAS%' THEN 1 ELSE OXACILLIN END,
  AMPICILLIN = CASE WHEN organism LIKE '%PSEUDOMONAS%' THEN 1 ELSE AMPICILLIN END,
  CEFAZOLIN = CASE WHEN organism LIKE '%PSEUDOMONAS%' THEN 1 ELSE CEFAZOLIN END,
  CEFTRIAXONE = CASE WHEN organism LIKE '%PSEUDOMONAS%' THEN 1 ELSE CEFTRIAXONE END,
  TRIMETHOPRIM_SULFAMETHOXAZOLE = CASE WHEN organism LIKE '%PSEUDOMONAS%' THEN 1 ELSE TRIMETHOPRIM_SULFAMETHOXAZOLE END,
  VANCOMYCIN = CASE WHEN organism LIKE '%PSEUDOMONAS%' THEN 1 ELSE VANCOMYCIN END
WHERE true;

# Infer intrinsic Acinetobacter resistance
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  OXACILLIN = CASE WHEN organism LIKE '%ACINETOBACTER%' THEN 1 ELSE OXACILLIN END,
  AMPICILLIN = CASE WHEN organism LIKE '%ACINETOBACTER%' THEN 1 ELSE AMPICILLIN END,
  CEFAZOLIN = CASE WHEN organism LIKE '%ACINETOBACTER%' THEN 1 ELSE CEFAZOLIN END,
  CEFTRIAXONE = CASE WHEN organism LIKE '%ACINETOBACTER%' THEN 1 ELSE CEFTRIAXONE END,
  TRIMETHOPRIM_SULFAMETHOXAZOLE = CASE WHEN organism LIKE '%ACINETOBACTER%' THEN 1 ELSE TRIMETHOPRIM_SULFAMETHOXAZOLE END,
  VANCOMYCIN = CASE WHEN organism LIKE '%ACINETOBACTER%' THEN 1 ELSE VANCOMYCIN END
WHERE true;

# Infer intrinsic Enterococcus resistance
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  OXACILLIN = CASE WHEN organism LIKE '%ENTEROCOCCUS%' THEN 1 ELSE OXACILLIN END,
  CEFAZOLIN = CASE WHEN organism LIKE '%ENTEROCOCCUS%' THEN 1 ELSE CEFAZOLIN END,
  CEFTRIAXONE = CASE WHEN organism LIKE '%ENTEROCOCCUS%' THEN 1 ELSE CEFTRIAXONE END,
  CEFEPIME = CASE WHEN organism LIKE '%ENTEROCOCCUS%' THEN 1 ELSE CEFEPIME END,
  TRIMETHOPRIM_SULFAMETHOXAZOLE = CASE WHEN organism LIKE '%ENTEROCOCCUS%' THEN 1 ELSE TRIMETHOPRIM_SULFAMETHOXAZOLE END
WHERE true;

# Infer intrinsic Staph aureus resistance, if methicillin/oxacillin resistant
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  AMPICILLIN = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE AMPICILLIN END,
  CEFAZOLIN = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE CEFAZOLIN END,
  CEFTRIAXONE = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE CEFTRIAXONE END,
  CEFEPIME = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE CEFEPIME END,
  PIPERACILLIN_TAZOBACTAM = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE PIPERACILLIN_TAZOBACTAM END,
  MEROPENEM = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE MEROPENEM END,
  TRIMETHOPRIM_SULFAMETHOXAZOLE = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE TRIMETHOPRIM_SULFAMETHOXAZOLE END,
  CIPROFLOXACIN = CASE WHEN organism LIKE '%STAPH%' AND organism LIKE '%AUREUS%' AND OXACILLIN = 1 THEN 1 ELSE CIPROFLOXACIN END
WHERE true;

# Infer cefazolin resistance based on other cephalosporins or penicillins (wide to narrow logic)
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  CEFAZOLIN = CASE WHEN CEFAZOLIN IS NULL AND (CEFTRIAXONE = 1 OR CEFEPIME = 1 OR PIPERACILLIN_TAZOBACTAM = 1 OR MEROPENEM = 1) THEN 1 ELSE CEFAZOLIN END
WHERE true;

# Infer ceftriaxone sensitivities based on other cephalosporins or penicillins (both wide to narrow and narrow to wide logic)
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  CEFTRIAXONE = CASE WHEN CEFTRIAXONE IS NULL AND (CEFEPIME = 1 OR MEROPENEM = 1 OR PIPERACILLIN_TAZOBACTAM = 1) THEN 1
                     WHEN CEFTRIAXONE IS NULL AND (CEFAZOLIN = 0 OR (AMPICILLIN = 0 AND organism NOT LIKE '%ENTEROCOCCUS') OR OXACILLIN = 0) THEN 0 
                     ELSE CEFTRIAXONE END
WHERE true;

# Infer cefepime sensitivities based on other cephalosporins or penicillins (narrow to wide logic)
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  CEFEPIME = CASE WHEN CEFEPIME IS NULL AND (CEFAZOLIN = 0 OR (AMPICILLIN = 0 AND organism NOT LIKE '%ENTEROCOCCUS') OR OXACILLIN = 0 OR CEFTRIAXONE = 0) THEN 0
                  ELSE CEFEPIME END
WHERE true;

# Infer meropenem sensitivities based on other cephalosporisn or penicillins (narrow to wide logic)
UPDATE `mvm_abx.culture_sensitivity_inferred_temp_wide`
SET
  MEROPENEM = CASE WHEN MEROPENEM IS NULL AND (CEFAZOLIN = 0 OR (AMPICILLIN = 0 AND organism NOT LIKE '%ENTEROCOCCUS') OR OXACILLIN = 0 OR CEFTRIAXONE = 0 OR CEFEPIME = 0) THEN 0
                   ELSE MEROPENEM END
WHERE true;

#
# Any pip/tazo inference?
#

#######################################################################################################################
# Pivot back to longer format
#######################################################################################################################

CREATE OR REPLACE TABLE `mvm_abx.culture_sensitivity_inferred` AS 
SELECT 
  t.anon_id,  t.order_proc_id_coded, t.description, t.organism,
  t.order_time_jittered, t.result_time_jittered,
  x.antibiotic, x.resistance
FROM 
  `mvm_abx.culture_sensitivity_inferred_temp_wide` t,
UNNEST(
  [STRUCT("OXACILLIN" AS antibiotic, OXACILLIN AS resistance),
   STRUCT("AMPICILLIN", AMPICILLIN),
   STRUCT("CEFAZOLIN", CEFAZOLIN),
   STRUCT("CEFTRIAXONE", CEFTRIAXONE),
   STRUCT("CEFEPIME", CEFEPIME),
   STRUCT("PIPERACILLIN_TAZOBACTAM", PIPERACILLIN_TAZOBACTAM),
   STRUCT("CIPROFLOXACIN", CIPROFLOXACIN),
   STRUCT("TRIMETHOPRIM_SULFAMETHOXAZOLE", TRIMETHOPRIM_SULFAMETHOXAZOLE),
   STRUCT("MEROPENEM", MEROPENEM),
   STRUCT("VANCOMYCIN", VANCOMYCIN)
  ]
) x
WHERE x.resistance IS NOT NULL;

# Drop temporary wide table
DROP TABLE IF EXISTS `mvm_abx.culture_sensitivity_inferred_temp_wide`