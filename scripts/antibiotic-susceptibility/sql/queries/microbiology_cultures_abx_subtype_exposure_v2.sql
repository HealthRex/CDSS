##############################################################################################################################################################
-- Goal: Creating table that indicates exposure to a subclass of antibiotics before specimen collection.
##############################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_antibiotic_subtype_expoosure` AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        mcp.medication_description,
        mcp.medication_name,
        cl.antibiotic_subtype,
        CASE WHEN antibiotic_subtype = 'Fluoroquinolone' THEN 'FLQ'
WHEN antibiotic_subtype = 'Nitrofuran' THEN 'NIT'
WHEN antibiotic_subtype = 'Sulfonamide' THEN 'SUL'
WHEN antibiotic_subtype = 'Fosfomycin' THEN 'FOS'
WHEN antibiotic_subtype = 'Folate Synthesis Inhibitor' THEN 'FSI'
WHEN antibiotic_subtype = 'Monobactam' THEN 'MON'
WHEN antibiotic_subtype = 'Polymyxin' THEN 'POL'
WHEN antibiotic_subtype = 'Cephalosporin Gen1' THEN 'CEP1'
WHEN antibiotic_subtype = 'Beta Lactam Combo' THEN 'BLC'
WHEN antibiotic_subtype = 'Tetracycline' THEN 'TET'
WHEN antibiotic_subtype = 'Urinary Antiseptic' THEN 'UA'
WHEN antibiotic_subtype = 'Carbapenem' THEN 'CAR'
WHEN antibiotic_subtype = 'Penicillin' THEN 'PEN'
WHEN antibiotic_subtype = 'Nitroimidazole' THEN 'NIM'
WHEN antibiotic_subtype = 'Glycopeptide' THEN 'GLY'
WHEN antibiotic_subtype = 'Oxazolidinone' THEN 'OXA'
WHEN antibiotic_subtype = 'Aminoglycoside' THEN 'AMG'
WHEN antibiotic_subtype = 'Antitubercular' THEN 'AT'
WHEN antibiotic_subtype = 'Sulfonamide Combo' THEN 'SULC'
WHEN antibiotic_subtype = 'Macrolide' THEN 'MAC'
WHEN antibiotic_subtype = 'Cephalosporin Gen2' THEN 'CEP2'
WHEN antibiotic_subtype = 'Ansamycin' THEN 'ANS'
WHEN antibiotic_subtype = 'Cephalosporin Gen3' THEN 'CEP3'
WHEN antibiotic_subtype = 'Lincosamide' THEN 'LIN'
WHEN antibiotic_subtype = 'Cephalosporin Gen4' THEN 'CEP4'
END as antibiotic_subtype_category,
        mcp.medication_time,
        mcp.medication_days_to_culture

    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_medication_exposure` mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` cl
    ON
        mcp.medication_description = cl.antibiotic

)

