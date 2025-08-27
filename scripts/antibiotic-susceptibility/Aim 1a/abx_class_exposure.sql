-- Extracting Class Exposure Table
-- This query has two steps. 
-- First query creates a table microbiology_cultures_prior_class_extracted that contains antibiotic class information along with the time frames for each exposure. 
-- Second query creates a table microbiology_cultures_class_exposure that includes binary indicators of exposure to each antibiotic class within different time frames

########### 1st query ############
##############################################################################################################################################################
-- It joins the cleaned microbiology cultures data with the class-subtype lookup table to associate each medication with its corresponding antibiotic class.
##############################################################################################################################################################
-- Create a table with class information along with the time frames
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_class_extracted` AS
WITH class_exposure AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        cl.antibiotic_class,
        mcp.time_frame
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_cleaned` mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` cl
    ON
        mcp.medication_name = cl.antibiotic
)
SELECT * FROM class_exposure;


########### 2nd query ############
##############################################################################################################################################################
-- Creating Binary Indicators for abx Class Exposure
##############################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_class_exposure` AS
WITH class_exposure AS (

    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc,
        antibiotic_class,
        time_frame,
        1 AS exposure
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_class_extracted`
), 
final_class_exposure AS (

    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc,

        MAX(IF(antibiotic_class = 'Beta Lactam' AND time_frame = '7', exposure, 0)) AS BL_7_days,
        MAX(IF(antibiotic_class = 'Beta Lactam' AND time_frame = '14', exposure, 0)) AS BL_14_days,
        MAX(IF(antibiotic_class = 'Beta Lactam' AND time_frame = '30', exposure, 0)) AS BL_30_days,
        MAX(IF(antibiotic_class = 'Beta Lactam' AND time_frame = '90', exposure, 0)) AS BL_90_days,
        MAX(IF(antibiotic_class = 'Beta Lactam' AND time_frame = '180', exposure, 0)) AS BL_180_days,
        MAX(IF(antibiotic_class = 'Beta Lactam' AND time_frame = 'ALL', exposure, 0)) AS BL_ALL_days,
        MAX(IF(antibiotic_class = 'Combination Antibiotic' AND time_frame = '7', exposure, 0)) AS CA_7_days,
        MAX(IF(antibiotic_class = 'Combination Antibiotic' AND time_frame = '14', exposure, 0)) AS CA_14_days,
        MAX(IF(antibiotic_class = 'Combination Antibiotic' AND time_frame = '30', exposure, 0)) AS CA_30_days,
        MAX(IF(antibiotic_class = 'Combination Antibiotic' AND time_frame = '90', exposure, 0)) AS CA_90_days,
        MAX(IF(antibiotic_class = 'Combination Antibiotic' AND time_frame = '180', exposure, 0)) AS CA_180_days,
        MAX(IF(antibiotic_class = 'Combination Antibiotic' AND time_frame = 'ALL', exposure, 0)) AS CA_ALL_days,
        MAX(IF(antibiotic_class = 'Tetracycline' AND time_frame = '7', exposure, 0)) AS TET_7_days,
        MAX(IF(antibiotic_class = 'Tetracycline' AND time_frame = '14', exposure, 0)) AS TET_14_days,
        MAX(IF(antibiotic_class = 'Tetracycline' AND time_frame = '30', exposure, 0)) AS TET_30_days,
        MAX(IF(antibiotic_class = 'Tetracycline' AND time_frame = '90', exposure, 0)) AS TET_90_days,
        MAX(IF(antibiotic_class = 'Tetracycline' AND time_frame = '180', exposure, 0)) AS TET_180_days,
        MAX(IF(antibiotic_class = 'Tetracycline' AND time_frame = 'ALL', exposure, 0)) AS TET_ALL_days,
        MAX(IF(antibiotic_class = 'Nitroimidazole' AND time_frame = '7', exposure, 0)) AS NIM_7_days,
        MAX(IF(antibiotic_class = 'Nitroimidazole' AND time_frame = '14', exposure, 0)) AS NIM_14_days,
        MAX(IF(antibiotic_class = 'Nitroimidazole' AND time_frame = '30', exposure, 0)) AS NIM_30_days,
        MAX(IF(antibiotic_class = 'Nitroimidazole' AND time_frame = '90', exposure, 0)) AS NIM_90_days,
        MAX(IF(antibiotic_class = 'Nitroimidazole' AND time_frame = '180', exposure, 0)) AS NIM_180_days,
        MAX(IF(antibiotic_class = 'Nitroimidazole' AND time_frame = 'ALL', exposure, 0)) AS NIM_ALL_days,
        MAX(IF(antibiotic_class = 'Glycopeptide' AND time_frame = '7', exposure, 0)) AS GLY_7_days,
        MAX(IF(antibiotic_class = 'Glycopeptide' AND time_frame = '14', exposure, 0)) AS GLY_14_days,
        MAX(IF(antibiotic_class = 'Glycopeptide' AND time_frame = '30', exposure, 0)) AS GLY_30_days,
        MAX(IF(antibiotic_class = 'Glycopeptide' AND time_frame = '90', exposure, 0)) AS GLY_90_days,
        MAX(IF(antibiotic_class = 'Glycopeptide' AND time_frame = '180', exposure, 0)) AS GLY_180_days,
        MAX(IF(antibiotic_class = 'Glycopeptide' AND time_frame = 'ALL', exposure, 0)) AS GLY_ALL_days,
        MAX(IF(antibiotic_class = 'Oxazolidinone' AND time_frame = '7', exposure, 0)) AS OXA_7_days,
        MAX(IF(antibiotic_class = 'Oxazolidinone' AND time_frame = '14', exposure, 0)) AS OXA_14_days,
        MAX(IF(antibiotic_class = 'Oxazolidinone' AND time_frame = '30', exposure, 0)) AS OXA_30_days,
        MAX(IF(antibiotic_class = 'Oxazolidinone' AND time_frame = '90', exposure, 0)) AS OXA_90_days,
        MAX(IF(antibiotic_class = 'Oxazolidinone' AND time_frame = '180', exposure, 0)) AS OXA_180_days,
        MAX(IF(antibiotic_class = 'Oxazolidinone' AND time_frame = 'ALL', exposure, 0)) AS OXA_ALL_days,
        MAX(IF(antibiotic_class = 'Aminoglycoside' AND time_frame = '7', exposure, 0)) AS AMG_7_days,
        MAX(IF(antibiotic_class = 'Aminoglycoside' AND time_frame = '14', exposure, 0)) AS AMG_14_days,
        MAX(IF(antibiotic_class = 'Aminoglycoside' AND time_frame = '30', exposure, 0)) AS AMG_30_days,
        MAX(IF(antibiotic_class = 'Aminoglycoside' AND time_frame = '90', exposure, 0)) AS AMG_90_days,
        MAX(IF(antibiotic_class = 'Aminoglycoside' AND time_frame = '180', exposure, 0)) AS AMG_180_days,
        MAX(IF(antibiotic_class = 'Aminoglycoside' AND time_frame = 'ALL', exposure, 0)) AS AMG_ALL_days,
        MAX(IF(antibiotic_class = 'Urinary Antiseptic' AND time_frame = '7', exposure, 0)) AS UA_7_days,
        MAX(IF(antibiotic_class = 'Urinary Antiseptic' AND time_frame = '14', exposure, 0)) AS UA_14_days,
        MAX(IF(antibiotic_class = 'Urinary Antiseptic' AND time_frame = '30', exposure, 0)) AS UA_30_days,
        MAX(IF(antibiotic_class = 'Urinary Antiseptic' AND time_frame = '90', exposure, 0)) AS UA_90_days,
        MAX(IF(antibiotic_class = 'Urinary Antiseptic' AND time_frame = '180', exposure, 0)) AS UA_180_days,
        MAX(IF(antibiotic_class = 'Urinary Antiseptic' AND time_frame = 'ALL', exposure, 0)) AS UA_ALL_days,
        MAX(IF(antibiotic_class = 'Antitubercular' AND time_frame = '7', exposure, 0)) AS AT_7_days,
        MAX(IF(antibiotic_class = 'Antitubercular' AND time_frame = '14', exposure, 0)) AS AT_14_days,
        MAX(IF(antibiotic_class = 'Antitubercular' AND time_frame = '30', exposure, 0)) AS AT_30_days,
        MAX(IF(antibiotic_class = 'Antitubercular' AND time_frame = '90', exposure, 0)) AS AT_90_days,
        MAX(IF(antibiotic_class = 'Antitubercular' AND time_frame = '180', exposure, 0)) AS AT_180_days,
        MAX(IF(antibiotic_class = 'Antitubercular' AND time_frame = 'ALL', exposure, 0)) AS AT_ALL_days,
        MAX(IF(antibiotic_class = 'Macrolide Lincosamide' AND time_frame = '7', exposure, 0)) AS MAC_7_days,
        MAX(IF(antibiotic_class = 'Macrolide Lincosamide' AND time_frame = '14', exposure, 0)) AS MAC_14_days,
        MAX(IF(antibiotic_class = 'Macrolide Lincosamide' AND time_frame = '30', exposure, 0)) AS MAC_30_days,
        MAX(IF(antibiotic_class = 'Macrolide Lincosamide' AND time_frame = '90', exposure, 0)) AS MAC_90_days,
        MAX(IF(antibiotic_class = 'Macrolide Lincosamide' AND time_frame = '180', exposure, 0)) AS MAC_180_days,
        MAX(IF(antibiotic_class = 'Macrolide Lincosamide' AND time_frame = 'ALL', exposure, 0)) AS MAC_ALL_days,
        MAX(IF(antibiotic_class = 'Fluoroquinolone' AND time_frame = '7', exposure, 0)) AS FLQ_7_days,
        MAX(IF(antibiotic_class = 'Fluoroquinolone' AND time_frame = '14', exposure, 0)) AS FLQ_14_days,
        MAX(IF(antibiotic_class = 'Fluoroquinolone' AND time_frame = '30', exposure, 0)) AS FLQ_30_days,
        MAX(IF(antibiotic_class = 'Fluoroquinolone' AND time_frame = '90', exposure, 0)) AS FLQ_90_days,
        MAX(IF(antibiotic_class = 'Fluoroquinolone' AND time_frame = '180', exposure, 0)) AS FLQ_180_days,
        MAX(IF(antibiotic_class = 'Fluoroquinolone' AND time_frame = 'ALL', exposure, 0)) AS FLQ_ALL_days,
        MAX(IF(antibiotic_class = 'Nitrofuran' AND time_frame = '7', exposure, 0)) AS NIT_7_days,
        MAX(IF(antibiotic_class = 'Nitrofuran' AND time_frame = '14', exposure, 0)) AS NIT_14_days,
        MAX(IF(antibiotic_class = 'Nitrofuran' AND time_frame = '30', exposure, 0)) AS NIT_30_days,
        MAX(IF(antibiotic_class = 'Nitrofuran' AND time_frame = '90', exposure, 0)) AS NIT_90_days,
        MAX(IF(antibiotic_class = 'Nitrofuran' AND time_frame = '180', exposure, 0)) AS NIT_180_days,
        MAX(IF(antibiotic_class = 'Nitrofuran' AND time_frame = 'ALL', exposure, 0)) AS NIT_ALL_days,
        MAX(IF(antibiotic_class = 'Sulfonamide' AND time_frame = '7', exposure, 0)) AS SUL_7_days,
        MAX(IF(antibiotic_class = 'Sulfonamide' AND time_frame = '14', exposure, 0)) AS SUL_14_days,
        MAX(IF(antibiotic_class = 'Sulfonamide' AND time_frame = '30', exposure, 0)) AS SUL_30_days,
        MAX(IF(antibiotic_class = 'Sulfonamide' AND time_frame = '90', exposure, 0)) AS SUL_90_days,
        MAX(IF(antibiotic_class = 'Sulfonamide' AND time_frame = '180', exposure, 0)) AS SUL_180_days,
        MAX(IF(antibiotic_class = 'Sulfonamide' AND time_frame = 'ALL', exposure, 0)) AS SUL_ALL_days,
        MAX(IF(antibiotic_class = 'Fosfomycin' AND time_frame = '7', exposure, 0)) AS FOS_7_days,
        MAX(IF(antibiotic_class = 'Fosfomycin' AND time_frame = '14', exposure, 0)) AS FOS_14_days,
        MAX(IF(antibiotic_class = 'Fosfomycin' AND time_frame = '30', exposure, 0)) AS FOS_30_days,
        MAX(IF(antibiotic_class = 'Fosfomycin' AND time_frame = '90', exposure, 0)) AS FOS_90_days,
        MAX(IF(antibiotic_class = 'Fosfomycin' AND time_frame = '180', exposure, 0)) AS FOS_180_days,
        MAX(IF(antibiotic_class = 'Fosfomycin' AND time_frame = 'ALL', exposure, 0)) AS FOS_ALL_days,
        MAX(IF(antibiotic_class = 'Monobactam' AND time_frame = '7', exposure, 0)) AS MON_7_days,
        MAX(IF(antibiotic_class = 'Monobactam' AND time_frame = '14', exposure, 0)) AS MON_14_days,
        MAX(IF(antibiotic_class = 'Monobactam' AND time_frame = '30', exposure, 0)) AS MON_30_days,
        MAX(IF(antibiotic_class = 'Monobactam' AND time_frame = '90', exposure, 0)) AS MON_90_days,
        MAX(IF(antibiotic_class = 'Monobactam' AND time_frame = '180', exposure, 0)) AS MON_180_days,
        MAX(IF(antibiotic_class = 'Monobactam' AND time_frame = 'ALL', exposure, 0)) AS MON_ALL_days,
        MAX(IF(antibiotic_class = 'Folate Synthesis Inhibitor' AND time_frame = '7', exposure, 0)) AS FSI_7_days,
        MAX(IF(antibiotic_class = 'Folate Synthesis Inhibitor' AND time_frame = '14', exposure, 0)) AS FSI_14_days,
        MAX(IF(antibiotic_class = 'Folate Synthesis Inhibitor' AND time_frame = '30', exposure, 0)) AS FSI_30_days,
        MAX(IF(antibiotic_class = 'Folate Synthesis Inhibitor' AND time_frame = '90', exposure, 0)) AS FSI_90_days,
        MAX(IF(antibiotic_class = 'Folate Synthesis Inhibitor' AND time_frame = '180', exposure, 0)) AS FSI_180_days,
        MAX(IF(antibiotic_class = 'Folate Synthesis Inhibitor' AND time_frame = 'ALL', exposure, 0)) AS FSI_ALL_days,
        MAX(IF(antibiotic_class = 'Polymyxin, Lipopeptide' AND time_frame = '7', exposure, 0)) AS POL_7_days,
        MAX(IF(antibiotic_class = 'Polymyxin, Lipopeptide' AND time_frame = '14', exposure, 0)) AS POL_14_days,
        MAX(IF(antibiotic_class = 'Polymyxin, Lipopeptide' AND time_frame = '30', exposure, 0)) AS POL_30_days,
        MAX(IF(antibiotic_class = 'Polymyxin, Lipopeptide' AND time_frame = '90', exposure, 0)) AS POL_90_days,
        MAX(IF(antibiotic_class = 'Polymyxin, Lipopeptide' AND time_frame = '180', exposure, 0)) AS POL_180_days,
        MAX(IF(antibiotic_class = 'Polymyxin, Lipopeptide' AND time_frame = 'ALL', exposure, 0)) AS POL_ALL_days,
        MAX(IF(antibiotic_class = 'Ansamycin' AND time_frame = '7', exposure, 0)) AS ANS_7_days,
        MAX(IF(antibiotic_class = 'Ansamycin' AND time_frame = '14', exposure, 0)) AS ANS_14_days,
        MAX(IF(antibiotic_class = 'Ansamycin' AND time_frame = '30', exposure, 0)) AS ANS_30_days,
        MAX(IF(antibiotic_class = 'Ansamycin' AND time_frame = '90', exposure, 0)) AS ANS_90_days,
        MAX(IF(antibiotic_class = 'Ansamycin' AND time_frame = '180', exposure, 0)) AS ANS_180_days,
        MAX(IF(antibiotic_class = 'Ansamycin' AND time_frame = 'ALL', exposure, 0)) AS ANS_ALL_days

    FROM
        class_exposure
    GROUP BY
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
)
SELECT * FROM final_class_exposure;

