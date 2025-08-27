-- Extracting Nursing Home Visits
-- This query has two steps. 
-- First query creates a table nursing_home_visits_temp that contains nursing home visit information along with the time frames extracted from three diffrent tables.
-- procedure, f_ip_hsp_admission, and encounter tables have the nursing home info.
-- Second query creates a table microbiology_cultures_nursing_home_visits that includes binary indicators of nursing home visits within different time frames

########### 1st query ############
##############################################################################################################################################################
-- Update the Temporary Nursing Home Visits Table
##############################################################################################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.nursing_home_visits_temp` AS
WITH procedure_nursing_home_visits AS (
    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        proc_date_jittered AS visit_date,
        'procedure' AS source,
        'Yes' AS nursing_home_visit
    FROM `som-nero-phi-jonc101.shc_core_2023.procedure`
    WHERE (code BETWEEN '99304' AND '99318')
    OR description LIKE '%nursing facility%'
),

admission_nursing_home_visits AS (
    SELECT
        anon_id,
        pat_enc_csn_id_jittered AS pat_enc_csn_id_coded,
        hosp_adm_date_jittered AS visit_date,
        'admission' AS source,
        'Yes' AS nursing_home_visit
    FROM `som-nero-phi-jonc101.shc_core_2023.f_ip_hsp_admission`
    WHERE admit_source_name IN ('SNF or ICF', 'Other Health Care Facility (Includes Nursing Homes)')
),

encounter_nursing_home_visits AS (
    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        hosp_disch_time_jittered AS visit_date,
        'encounter' AS source,
        'Yes' AS nursing_home_visit
    FROM `som-nero-phi-jonc101.shc_core_2023.encounter`
    WHERE disch_dest LIKE '%Nursing%' OR disch_dest LIKE '%SNF%' OR disch_dest LIKE '%RES%'
)

-- Combine All Results
SELECT * FROM procedure_nursing_home_visits
UNION ALL
SELECT * FROM admission_nursing_home_visits
UNION ALL
SELECT * FROM encounter_nursing_home_visits;


########### 2nd query ############
##############################################################################################################################################################
-- Calculate Nursing Home Visit Features Relative to Culture Order Date
##############################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_nursing_home_visits` AS
SELECT
    a.anon_id,
    a.pat_enc_csn_id_coded,
    a.order_proc_id_coded,
    a.order_time_jittered_utc,
    MAX(CASE 
        WHEN b.visit_date IS NOT NULL 
            AND b.source = 'procedure' 
            AND TIMESTAMP_DIFF(a.order_time_jittered_utc, TIMESTAMP(b.visit_date), DAY) >= 0 
        THEN 1
        ELSE 0 
    END) AS nursing_home_7_days,
    MAX(CASE 
        WHEN b.visit_date IS NOT NULL 
            AND b.source = 'admission' 
            AND TIMESTAMP_DIFF(a.order_time_jittered_utc, TIMESTAMP(b.visit_date), DAY) >= 0 
        THEN 1
        ELSE 0 
    END) AS nursing_home_14_days,
    MAX(CASE 
        WHEN b.visit_date IS NOT NULL 
            AND b.source = 'encounter' 
            AND TIMESTAMP_DIFF(a.order_time_jittered_utc, TIMESTAMP(b.visit_date), DAY) >= 0 
        THEN 1
        ELSE 0 
    END) AS nursing_home_30_days,
    MAX(CASE 
        WHEN b.visit_date IS NOT NULL 
            AND b.source = 'procedure' 
            AND TIMESTAMP_DIFF(a.order_time_jittered_utc, TIMESTAMP(b.visit_date), DAY) >= 0 
        THEN 1
        ELSE 0 
    END) AS nursing_home_90_days
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` a
LEFT JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.nursing_home_visits_temp` b
ON a.anon_id = b.anon_id
AND a.pat_enc_csn_id_coded = b.pat_enc_csn_id_coded
GROUP BY a.anon_id, a.pat_enc_csn_id_coded, a.order_proc_id_coded, a.order_time_jittered_utc;
