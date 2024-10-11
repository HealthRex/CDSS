-- Step 1: Create empty table and copy all the culture sensitivity to this table 
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` (
  anon_id STRING,
  pat_enc_csn_id_coded INT64,
  order_proc_id_coded INT64,
  organism STRING,
  antibiotic STRING,
  susceptibility STRING,
  implied_susceptibility STRING
);

--Insert prior culture sensitivity into the implied table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic, susceptibility)
WITH More_Frequent_ABX AS (
  SELECT DISTINCT(medication_name)
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_cleaned`
),
Base_cohort AS (
  SELECT
    c.anon_id,
    t.pat_enc_csn_id_coded,
    c.order_proc_id_coded,
    c.organism,
    c.antibiotic,
    c.suscept AS susceptibility
  FROM `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity` c
  INNER JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` t
  USING (anon_id, order_proc_id_coded)
  WHERE c.antibiotic IN (SELECT medication_name FROM More_Frequent_ABX)
)
SELECT * FROM Base_cohort;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------ACINETOBACTER----------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
AND lower(antibiotic) IN ('aztreonam', 'cefazolin', 'minocycline', 'tetracycline')
AND (susceptibility IS NULL OR susceptibility = '');


-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['aztreonam', 'cefazolin', 'minocycline', 'tetracycline']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic, implied_susceptibility)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
  'Resistant' AS implied_susceptibility
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

----------------------------
-- *Doripenem E meropenem
-----------------------------

-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['doripenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

# Update the missing value
UPDATE`som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
);
----------------------
--*Meropenem if missing then S if imipenem-S; if missing then .
-------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['meropenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;



 -- Update missing values 
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('imipenem')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------Citrobacter-------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ampicillin', 'cefazolin', 'cefotetan', 'cefoxitin']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

-- step3: Update implied susceptibility records based on rules 
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%'
AND
LOWER(antibiotic) like any ('ampicillin', 'cefazolin', 'cefotetan', 'cefoxitin')
AND susceptibility IS NULL;

------------------------------
--* Cefepime if missing then S if ceftriaxone-S or cefotaxime-S; else .
------------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefepime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

-- step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
  );

----------------
--* Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ceftazidime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

-- step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
  );

------------------------
--*Ceftriaxone if missing then E cefotaxime; if missing then .
-------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ceftriaxone']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules 
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ceftriaxone')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Susceptible')
  );
  
UPDATE`som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ceftriaxone')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Resistant')
  );

-----------------------
--*Cefotaxime if missing then E ceftriaxone; if missing then .
-------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefotaxime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Susceptible')
  );
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Resistant')
  );

---------------
--*Doripenem E meropenem
------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['doripenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Susceptible')
  );
  UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Resistant')
  );

-----
--* Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ertapenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
  );

--------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['imipenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
  );
-----
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S; or cefotaxime-S else .
-----
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['meropenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
  );

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------Enterobacter----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ampicillin', 'cefazolin']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('ampicillin', 'cefazolin')
AND susceptibility IS NULL;

----------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S; else .
----------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefepime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);
------------
--*Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ceftazidime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);
------------
--*Ceftriaxone if missing then E cefotaxime; if missing then .
---------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ceftriaxone']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL;

------------------
--*Cefotaxime if missing then E ceftriaxone; if missing then .
------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefotaxime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;
--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;


----
--*Doxycycline if missing then S if tetracycline-S; else R
----
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['doxycycline']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible')
);

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------------
--*Doripenem E meropenem
-----------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['doripenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL;

-------------
--*Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
---------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ertapenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);
------------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['imipenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);
-------------
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S or cefotaxime-S; else .
-------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['meropenem']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------ESCHERICHIA COLI-------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
--------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefepime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);

--------------------
--* Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
--------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ceftazidime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible')
);

------------
--*Ceftriaxone if missing then E cefotaxime; if missing then S if cefazolin-S; else .
------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ceftriaxone']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('Ceftriaxone')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible')
);
--------------
--*Cefotaxime if missing then E ceftriaxone; if missing then S if cefazolin-S; else .
------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefotaxime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible')
);
----------------
--*Cefotetan if missing then S if cefazolin-S; else .
----------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefotetan']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefotetan')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible')
);

---------------------
--*Cefoxitin if missing then S if cefazolin-S; else .
----------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefoxitin']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefoxitin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible')
);
---------------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then S if cefazolin-S; if missing then .
----------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefpodoxime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible')
);

---------------
--*Cefuroxime if missing then S if cefazolin-S; else .
---------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['cefuroxime']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefuroxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible')
);

-----------------
--*Doxycycline if missing then S if tetracycline-S; else R
-----------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['doxycycline']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible')
);

UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------KLEBSIELLA----------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ampicillin']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND
LOWER(antibiotic) like any ('ampicillin')
AND susceptibility IS NULL;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------Proteus species-------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%PROTEUS%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['tetracycline', 'tigecycline','colistin']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND
LOWER(antibiotic) like any ('tetracycline', 'tigecycline','colistin')
AND susceptibility IS NULL;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------Pseudomonas aeruginosa---------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ampicillin','ceftriaxone', 'cefazolin','ertapenem','tetracycline','tigecycline']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE`som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant' 
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
AND (lower(antibiotic) like  any ('ampicillin','ceftriaxone', 'cefazolin','ertapenem',
'tetracycline','tigecycline')
)
AND susceptibility IS NULL;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------serratia------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Step 1: Create a temporary table to store missing Acinetobacter records
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records` AS
WITH Acinetobacter_Cases AS (
  -- Base cohort of Acinetobacter cases
  SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    organism
  FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  WHERE UPPER(organism) LIKE '%SERRATIA%'
),
Missing_ABX_Records AS (
  -- Find cases with Acinetobacter where the specific antibiotics are missing
  SELECT
    ac.anon_id,
    ac.pat_enc_csn_id_coded,
    ac.order_proc_id_coded,
    ac.organism,
    abx
  FROM Acinetobacter_Cases ac
  CROSS JOIN UNNEST(['ampicillin', 'cefazolin','tetracycline']) AS abx  -- Remove the parentheses
  LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility` mis
  ON ac.anon_id = mis.anon_id
  AND ac.pat_enc_csn_id_coded = mis.pat_enc_csn_id_coded
  AND ac.order_proc_id_coded = mis.order_proc_id_coded
  AND LOWER(mis.antibiotic) = abx  -- Refer to `abx` directly
  WHERE mis.antibiotic IS NULL -- Filters cases where antibiotics are missing
)
SELECT * FROM Missing_ABX_Records;

-- Step 2: Insert missing implied susceptibility records into the target table
INSERT INTO `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
  (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, organism, antibiotic)
SELECT
  anon_id,
  pat_enc_csn_id_coded,
  order_proc_id_coded,
  organism,
  abx as antibiotic,
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;

--step3: Update implied susceptibility records based on rules
UPDATE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND
LOWER(antibiotic) like any ('ampicillin', 'cefazolin','tetracycline')
AND susceptibility IS NULL;

-- Remove duplicates and save results in table microbiology-implied-susceptibility
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology-implied-susceptibility` as
select * from `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`
where 
susceptibility is not null
OR 
implied_susceptibility is not null
group by anon_id,pat_enc_csn_id_coded,order_proc_id_coded,organism,antibiotic,susceptibility,implied_susceptibility
order by anon_id,pat_enc_csn_id_coded,order_proc_id_coded,organism,antibiotic,susceptibility,implied_susceptibility;

drop table  `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_implied_susceptibility`;
