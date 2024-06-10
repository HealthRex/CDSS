####The goal is to create the microbiology_cultures_prior_med table, which includes binary indicators for specific medication exposure within various time frames.


######## Steps ###############

#######################################################################################################
1. Creating the microbiology_cultures_prior_antibiotics_extracted Table
#######################################################################################################

# Purpose: To extract microbiology cultures and their associated medications, along with the time frames of medication exposure.

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_extracted` AS
WITH microbiology_cultures AS (
    SELECT DISTINCT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort`
),

cleaned_medications AS (
    SELECT 
        mc.anon_id,
        mc.pat_enc_csn_id_coded,
        mc.order_proc_id_coded,
        mc.order_time_jittered_utc,
        mo.ordering_date_jittered_utc,
        INITCAP(TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    LOWER(mm.name),
                    'penicillin[^a-z].*$', 'penicillin'
                ),
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''
            )
        )) AS medication_name
    FROM 
        microbiology_cultures mc
    INNER JOIN 
        `som-nero-phi-jonc101.shc_core_2023.order_med` mo
    ON 
        mc.anon_id = mo.anon_id
    LEFT JOIN 
        `som-nero-phi-jonc101.shc_core_2023.mapped_meds` mm
    ON 
        mo.med_description = mm.name
),

prior_antibiotics_exposure AS (
    SELECT 
        cm.anon_id,
        cm.pat_enc_csn_id_coded,
        cm.order_proc_id_coded,
        cm.order_time_jittered_utc,
        cm.medication_name,
        CASE 
            WHEN TIMESTAMP_DIFF(cm.order_time_jittered_utc, cm.ordering_date_jittered_utc, DAY) <= 7 THEN '7'
            WHEN TIMESTAMP_DIFF(cm.order_time_jittered_utc, cm.ordering_date_jittered_utc, DAY) <= 14 THEN '14'
            WHEN TIMESTAMP_DIFF(cm.order_time_jittered_utc, cm.ordering_date_jittered_utc, DAY) <= 30 THEN '30'
            WHEN TIMESTAMP_DIFF(cm.order_time_jittered_utc, cm.ordering_date_jittered_utc, DAY) <= 90 THEN '90'
            WHEN TIMESTAMP_DIFF(cm.order_time_jittered_utc, cm.ordering_date_jittered_utc, DAY) <= 180 THEN '180'
            ELSE 'ALL'
        END AS time_frame
    FROM 
        cleaned_medications cm
)

SELECT * FROM prior_antibiotics_exposure;


