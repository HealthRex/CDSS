
#########################################################################################################################################################
-- Create a new table for demographics information based on anon_id, pat_enc_csn_id_coded, and order_proc_id_coded from the microbiology_cultures_cohort
#########################################################################################################################################################


CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_demographics` AS

WITH microbiology_cultures AS (
    SELECT DISTINCT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort`
),


############################################################
-- Join with the demographic table to get age and gender
############################################################

demographics AS (
    SELECT 
        mc.anon_id,
        mc.pat_enc_csn_id_coded,
        mc.order_proc_id_coded,
        DATE_DIFF(CAST(mc.order_time_jittered_utc AS DATE), CAST(demo.birth_date_jittered AS DATE), YEAR) AS age,
        demo.gender
    FROM 
        microbiology_cultures mc
    INNER JOIN 
        `som-nero-phi-jonc101.shc_core_2023.demographic` demo
    ON 
        mc.anon_id = demo.anon_id
)



############################################################
-- Select the relevant columns and save to the new table
############################################################

SELECT DISTINCT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    age,
    gender
FROM 
    demographics;
