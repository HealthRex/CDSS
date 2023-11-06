-- Create the new table
CREATE OR REPLACE TABLE `mining-clinical-decisions.fateme_db.implied_suscept` (
  anon_id STRING,
  order_proc_id_coded INT64,
  organism STRING,
  antibiotic STRING,
  susceptibility STRING,
  implied_susceptibility STRING
);

-- Populate the new table with data from culture_sensitivity
INSERT INTO `mining-clinical-decisions.fateme_db.implied_suscept` (anon_id, order_proc_id_coded, organism, antibiotic, susceptibility)
SELECT
  anon_id,
  order_proc_id_coded,
  organism AS organism,
  antibiotic AS antibiotic,
  suscept AS susceptibility
FROM
  `mining-clinical-decisions.shc_core.culture_sensitivity`;

-- Part 1 - Bug Specific Susceptibility Rules
-- Note: The rules have been split for clarity and to avoid potential conflicts, each bug is updated separately.

-- Pseudomonas
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE organism LIKE '%PSEUDOMONAS%'
AND (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%' OR
    antibiotic LIKE '%Ertapenem%' OR
    antibiotic LIKE '%Trimethoprim/sulfamethoxazole%'
);

-- Acinetobacter
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE organism LIKE '%ACINETOBACTER%'
AND (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%' OR
    antibiotic LIKE '%Ertapenem%' OR
    antibiotic LIKE '%Vancomycin%'
);

-- Stenotrophomonas
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE organism LIKE '%STENOTROPHOMONAS%'
AND (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Ampicillin/sulbactam%' OR
    antibiotic LIKE '%Piperacillin/tazobactam%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%' OR
    antibiotic LIKE '%Ertapenem%' OR
    antibiotic LIKE '%Meropenem%' OR
    antibiotic LIKE '%Vancomycin%'
);

-- Enterococcus
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE organism LIKE '%ENTEROCOCCUS%'
AND (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%' OR
    antibiotic LIKE '%Cefepime%' OR
    antibiotic LIKE '%Ceftazidime%' OR
    antibiotic LIKE '%Ertapenem%' OR
    antibiotic LIKE '%Meropenem%' OR
    antibiotic LIKE '%Trimethoprim/sulfamethoxazole%'
);


-- Streptococcus species: Beta-lactam susceptibility assumed to be Susceptible
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%STREPTOCOCCUS%'
AND UPPER(antibiotic) LIKE '%BETA-LACTAM%';


-- MSSA vs. MRSA: If oxacillin susceptible, assume susceptibility to other beta-lactams
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept` 
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%STAPHYLOCOCCUS AUREUS%' 
AND UPPER(antibiotic) LIKE '%BETA-LACTAM%'
AND EXISTS (
  SELECT 1
  FROM `mining-clinical-decisions.shc_core.culture_sensitivity`
  WHERE 
    UPPER(organism) LIKE '%STAPHYLOCOCCUS AUREUS%' 
    AND UPPER(antibiotic) = 'OXACILLIN'
    AND susceptibility = 'Susceptible'
    AND `mining-clinical-decisions.shc_core.culture_sensitivity`.order_proc_id_coded = `mining-clinical-decisions.fateme_db.implied_suscept`.order_proc_id_coded
    AND `mining-clinical-decisions.shc_core.culture_sensitivity`.anon_id = `mining-clinical-decisions.fateme_db.implied_suscept`.anon_id
);


-- Part 2 - Antibiotic Susceptibility Inferences
-- For resistance to Meropenem
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Ampicillin/sulbactam%' OR
    antibiotic LIKE '%Piperacillin/tazobactam%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%' OR
    antibiotic LIKE '%Cefepime%' OR
    antibiotic LIKE '%Ertapenem%'
)
AND order_proc_id_coded IN (
    SELECT order_proc_id_coded 
    FROM `mining-clinical-decisions.fateme_db.implied_suscept` 
    WHERE antibiotic LIKE '%Meropenem%' 
    AND susceptibility = 'Resistant'
);

-- For resistance to Ertapenem
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Ampicillin/sulbactam%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%'
)
AND order_proc_id_coded IN (
    SELECT order_proc_id_coded 
    FROM `mining-clinical-decisions.fateme_db.implied_suscept` 
    WHERE antibiotic LIKE '%Ertapenem%' 
    AND susceptibility = 'Resistant'
);

-- For resistance to Cefepime
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Ampicillin/sulbactam%' OR
    antibiotic LIKE '%Cefazolin%' OR
    antibiotic LIKE '%Ceftriaxone%'
)
AND order_proc_id_coded IN (
    SELECT order_proc_id_coded 
    FROM `mining-clinical-decisions.fateme_db.implied_suscept` 
    WHERE antibiotic LIKE '%Cefepime%' 
    AND susceptibility = 'Resistant'
);

-- For resistance to Ceftriaxone
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE (
    antibiotic LIKE '%Oxacillin%' OR
    antibiotic LIKE '%Ampicillin/sulbactam%' OR
    antibiotic LIKE '%Cefazolin%'
)
AND order_proc_id_coded IN (
    SELECT order_proc_id_coded 
    FROM `mining-clinical-decisions.fateme_db.implied_suscept` 
    WHERE antibiotic LIKE '%Ceftriaxone%' 
    AND susceptibility = 'Resistant'
);
