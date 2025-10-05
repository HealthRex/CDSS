#########################################################################################################################################################
-- Create a new table for demographics information based on anon_id, pat_enc_csn_id_coded, and order_proc_id_coded from the 
microbiology_cultures_cohort_peds with age calculated in years (≥1y) or days (<1y)
#########################################################################################################################################################


CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_demographics_peds` AS

WITH microbiology_cultures AS (
    SELECT DISTINCT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort_peds`
),

demographics AS (
    SELECT 
        mc.anon_id,
        mc.pat_enc_csn_id_coded,
        mc.order_proc_id_coded,
        demo.gender,

        -- Compute both year and day difference (absolute values to handle jitter)
        ABS(DATE_DIFF(CAST(mc.order_time_jittered_utc AS DATE), CAST(demo.birth_date_jittered AS DATE), YEAR)) AS diff_years,
        ABS(DATE_DIFF(CAST(mc.order_time_jittered_utc AS DATE), CAST(demo.birth_date_jittered AS DATE), DAY)) AS diff_days
    FROM 
        microbiology_cultures mc
    INNER JOIN 
        `som-nero-phi-jonc101.lpch_core_2024.lpch_demographic` demo
    ON 
        mc.anon_id = demo.anon_id
),

final AS (
    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        gender,

        -- Choose the correct age unit:
        CASE 
            WHEN diff_years < 1 THEN diff_days
            ELSE diff_years
        END AS age_value,

        CASE 
            WHEN diff_years < 1 THEN 'days'
            ELSE 'years'
        END AS age_unit
    FROM demographics
)

SELECT * FROM final;
