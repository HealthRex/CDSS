###############################################################################################################
# Goal: Indicate exposure to an antibiotic *subtype* before specimen collection.
###############################################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_antibiotic_subtype_exposure` AS
WITH subtype_exposure AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        mcp.medication_name,
        mcp.medication_category,
        cl.antibiotic_subtype,
        mcp.medication_time_to_culturetime
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_medication_exposure` AS mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` AS cl
    ON
        LOWER(mcp.medication_name) = LOWER(cl.antibiotic)
)
SELECT *
FROM subtype_exposure
WHERE medication_time_to_culturetime >= 1;
