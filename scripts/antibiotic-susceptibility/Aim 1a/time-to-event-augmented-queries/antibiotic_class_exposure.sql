###############################################################################################################
# Goal: Indicate exposure to an antibiotic *class* before specimen collection.
###############################################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_antibiotic_class_exposure` AS
WITH class_exposure AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        mcp.medication_name,
        mcp.medication_category,
        cl.antibiotic_class,
        mcp.medication_time_to_culturetime
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_medication_exposure` AS mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` AS cl
    ON
        LOWER(mcp.medication_name) = LOWER(cl.antibiotic)
)
SELECT *
FROM class_exposure
WHERE medication_time_to_culturetime >= 1;
