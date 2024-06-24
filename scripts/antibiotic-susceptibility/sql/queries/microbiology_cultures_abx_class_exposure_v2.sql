##############################################################################################################################################################
#Goal: Indicating exposure to a class of antibiotics before specimen collection.
##############################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_antibiotic_class_expoosure` AS (
WITH class_exposure AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        mcp.medication_description,
        mcp.medication_name,
        cl.antibiotic_class,
        mcp.medication_time,
        mcp.medication_days_to_culture
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_medication_exposure` mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` cl
    ON
        mcp.medication_description = cl.antibiotic
)
SELECT *
FROM class_exposure
)

