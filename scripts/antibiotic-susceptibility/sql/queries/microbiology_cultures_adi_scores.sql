-- Extracting ADI scores Table
-- This query has two steps. 
-- First query creates a table microbiology_cultures_adi_scores that contains ADI scores information
-- Second query creates a table microbiology_cultures_adi_scores_imputed that impute the ADI scores for those records in the microbiology_cultures_adi_scores table 
-- that have a 5-digit ZIP code by averaging the ADI scores of the corresponding 9-digit ZIP codes from the ADI_data_CA table.

###################Query 1##################
##########################################################################################
-- Step 1: Create the intermediate table cohort_adi
##########################################################################################

-- Create an intermediate table with cohort and ADI data
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.cohort_adi` AS
WITH cohort_zip AS (
    SELECT distinct
        mc.anon_id,
        mc.pat_enc_csn_id_coded,
        mc.order_proc_id_coded,
        mc.order_time_jittered_utc,
        REPLACE(z.zip, '-', '') AS zip
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` mc
    LEFT JOIN
        `som-nero-phi-jonc101.shc_core_2023.zip` z
    ON
        mc.anon_id = z.anon_id
)
SELECT
    cz.anon_id,
    cz.pat_enc_csn_id_coded,
    cz.order_proc_id_coded,
    cz.order_time_jittered_utc,
    cz.zip,
    adi.adi_score,
    adi.adi_state_rank
FROM
    cohort_zip cz
LEFT JOIN
    `som-nero-phi-jonc101.mapdata.ADI_data_CA` adi
ON
    cz.zip = adi.zip;

#####################################################################################################
-- Step 2: Create the final table microbiology_cultures_adi_scores using the intermediate table
#####################################################################################################

-- Create the final table with the desired columns
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_adi_scores` AS
SELECT distinct
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    order_time_jittered_utc,
    zip,
    adi_score,
    adi_state_rank
FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.cohort_adi`;


################### Query 2 ##################
############################################################################################################
-- Impute Missing ADI Values for 5-Digit ZIP Code
############################################################################################################
-- Step 1: Create the table for averaged ADI scores based on 5-digit ZIP codes
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.averaged_adi_scores` AS
SELECT 
    LEFT(zip, 5) AS zip5,
    AVG(CAST(adi_score AS FLOAT64)) AS avg_adi_score
FROM 
    `som-nero-phi-jonc101.mapdata.ADI_data_CA`
WHERE 
    LENGTH(zip) = 9
    AND SAFE_CAST(adi_score AS FLOAT64) IS NOT NULL -- Ensure that only numeric values are considered
GROUP BY 
    zip5;

-- Step 2: Update the microbiology_cultures_adi_scores table with imputed ADI scores for 5-digit ZIP codes
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_adi_scores_imputed` AS
WITH adi_imputed AS (
    SELECT
        mc.*,
        COALESCE(SAFE_CAST(mc.adi_score AS FLOAT64), aas.avg_adi_score) AS imputed_adi_score
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_adi_scores` mc
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.averaged_adi_scores` aas
    ON
        LEFT(mc.zip, 5) = aas.zip5
)
SELECT DISTINCT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    order_time_jittered_utc,
    zip,
    imputed_adi_score AS adi_score,
    adi_state_rank
FROM 
    adi_imputed;
