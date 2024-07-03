##############################################################################################################################################################
#Goal: Indicating exposure to a class of antibiotics before specimen collection.
##############################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_class_exposure_augmented` AS (
WITH class_exposure AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        mcp.medication_category,
        mcp.medication_name,
        cl.antibiotic_class,
        mcp.medication_time,
        mcp.medication_time_to_cultureTime
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_med_augmented` mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` cl
    ON
        mcp.medication_name = cl.antibiotic
)
SELECT *
FROM class_exposure
)
