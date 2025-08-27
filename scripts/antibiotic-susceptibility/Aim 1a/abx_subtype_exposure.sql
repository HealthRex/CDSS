-- Extracting Subtype Exposure Table
-- This query has two steps. 
-- First query creates a table microbiology_cultures_prior_subtype_extracted that contains antibiotic subtype information along with the time frames for each exposure. 
-- Second query creates a table microbiology_cultures_suntype_exposure that includes binary indicators of exposure to each antibiotic class within different time frames

########### 1st query ############
##############################################################################################################################################################
-- It joins the cleaned microbiology cultures data with the class-subtype lookup table to associate each medication with its corresponding antibiotic subtype.
##############################################################################################################################################################
-- Create a table with subtype information along with the time frames
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_subtype_extracted` AS
WITH subtype_exposure AS (
    SELECT
        mcp.anon_id,
        mcp.pat_enc_csn_id_coded,
        mcp.order_proc_id_coded,
        mcp.order_time_jittered_utc,
        cl.antibiotic_subtype,
        mcp.time_frame
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_cleaned` mcp
    LEFT JOIN
        `som-nero-phi-jonc101.antimicrobial_stewardship.class_subtype_lookup` cl
    ON
        mcp.medication_name = cl.antibiotic
)
SELECT * FROM subtype_exposure;


########### 2nd query ############
##############################################################################################################################################################
-- Creating Binary Indicators for Subtype Exposure
##############################################################################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_subtype_exposure` AS
WITH subtype_exposure AS (

    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc,
        antibiotic_subtype,
        time_frame,
        1 AS exposure
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_subtype_extracted`
), 
final_subtype_exposure AS (

    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc,

        MAX(IF(antibiotic_subtype = 'Fluoroquinolone' AND time_frame = '7', exposure, 0)) AS FLQ_7_days,
        MAX(IF(antibiotic_subtype = 'Fluoroquinolone' AND time_frame = '14', exposure, 0)) AS FLQ_14_days,
        MAX(IF(antibiotic_subtype = 'Fluoroquinolone' AND time_frame = '30', exposure, 0)) AS FLQ_30_days,
        MAX(IF(antibiotic_subtype = 'Fluoroquinolone' AND time_frame = '90', exposure, 0)) AS FLQ_90_days,
        MAX(IF(antibiotic_subtype = 'Fluoroquinolone' AND time_frame = '180', exposure, 0)) AS FLQ_180_days,
        MAX(IF(antibiotic_subtype = 'Fluoroquinolone' AND time_frame = 'ALL', exposure, 0)) AS FLQ_ALL_days,
        MAX(IF(antibiotic_subtype = 'Nitrofuran' AND time_frame = '7', exposure, 0)) AS NIT_7_days,
        MAX(IF(antibiotic_subtype = 'Nitrofuran' AND time_frame = '14', exposure, 0)) AS NIT_14_days,
        MAX(IF(antibiotic_subtype = 'Nitrofuran' AND time_frame = '30', exposure, 0)) AS NIT_30_days,
        MAX(IF(antibiotic_subtype = 'Nitrofuran' AND time_frame = '90', exposure, 0)) AS NIT_90_days,
        MAX(IF(antibiotic_subtype = 'Nitrofuran' AND time_frame = '180', exposure, 0)) AS NIT_180_days,
        MAX(IF(antibiotic_subtype = 'Nitrofuran' AND time_frame = 'ALL', exposure, 0)) AS NIT_ALL_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide' AND time_frame = '7', exposure, 0)) AS SUL_7_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide' AND time_frame = '14', exposure, 0)) AS SUL_14_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide' AND time_frame = '30', exposure, 0)) AS SUL_30_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide' AND time_frame = '90', exposure, 0)) AS SUL_90_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide' AND time_frame = '180', exposure, 0)) AS SUL_180_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide' AND time_frame = 'ALL', exposure, 0)) AS SUL_ALL_days,
        MAX(IF(antibiotic_subtype = 'Fosfomycin' AND time_frame = '7', exposure, 0)) AS FOS_7_days,
        MAX(IF(antibiotic_subtype = 'Fosfomycin' AND time_frame = '14', exposure, 0)) AS FOS_14_days,
        MAX(IF(antibiotic_subtype = 'Fosfomycin' AND time_frame = '30', exposure, 0)) AS FOS_30_days,
        MAX(IF(antibiotic_subtype = 'Fosfomycin' AND time_frame = '90', exposure, 0)) AS FOS_90_days,
        MAX(IF(antibiotic_subtype = 'Fosfomycin' AND time_frame = '180', exposure, 0)) AS FOS_180_days,
        MAX(IF(antibiotic_subtype = 'Fosfomycin' AND time_frame = 'ALL', exposure, 0)) AS FOS_ALL_days,
        MAX(IF(antibiotic_subtype = 'Folate Synthesis Inhibitor' AND time_frame = '7', exposure, 0)) AS FSI_7_days,
        MAX(IF(antibiotic_subtype = 'Folate Synthesis Inhibitor' AND time_frame = '14', exposure, 0)) AS FSI_14_days,
        MAX(IF(antibiotic_subtype = 'Folate Synthesis Inhibitor' AND time_frame = '30', exposure, 0)) AS FSI_30_days,
        MAX(IF(antibiotic_subtype = 'Folate Synthesis Inhibitor' AND time_frame = '90', exposure, 0)) AS FSI_90_days,
        MAX(IF(antibiotic_subtype = 'Folate Synthesis Inhibitor' AND time_frame = '180', exposure, 0)) AS FSI_180_days,
        MAX(IF(antibiotic_subtype = 'Folate Synthesis Inhibitor' AND time_frame = 'ALL', exposure, 0)) AS FSI_ALL_days,
        MAX(IF(antibiotic_subtype = 'Monobactam' AND time_frame = '7', exposure, 0)) AS MON_7_days,
        MAX(IF(antibiotic_subtype = 'Monobactam' AND time_frame = '14', exposure, 0)) AS MON_14_days,
        MAX(IF(antibiotic_subtype = 'Monobactam' AND time_frame = '30', exposure, 0)) AS MON_30_days,
        MAX(IF(antibiotic_subtype = 'Monobactam' AND time_frame = '90', exposure, 0)) AS MON_90_days,
        MAX(IF(antibiotic_subtype = 'Monobactam' AND time_frame = '180', exposure, 0)) AS MON_180_days,
        MAX(IF(antibiotic_subtype = 'Monobactam' AND time_frame = 'ALL', exposure, 0)) AS MON_ALL_days,
        MAX(IF(antibiotic_subtype = 'Polymyxin' AND time_frame = '7', exposure, 0)) AS POL_7_days,
        MAX(IF(antibiotic_subtype = 'Polymyxin' AND time_frame = '14', exposure, 0)) AS POL_14_days,
        MAX(IF(antibiotic_subtype = 'Polymyxin' AND time_frame = '30', exposure, 0)) AS POL_30_days,
        MAX(IF(antibiotic_subtype = 'Polymyxin' AND time_frame = '90', exposure, 0)) AS POL_90_days,
        MAX(IF(antibiotic_subtype = 'Polymyxin' AND time_frame = '180', exposure, 0)) AS POL_180_days,
        MAX(IF(antibiotic_subtype = 'Polymyxin' AND time_frame = 'ALL', exposure, 0)) AS POL_ALL_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen1' AND time_frame = '7', exposure, 0)) AS CEP1_7_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen1' AND time_frame = '14', exposure, 0)) AS CEP1_14_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen1' AND time_frame = '30', exposure, 0)) AS CEP1_30_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen1' AND time_frame = '90', exposure, 0)) AS CEP1_90_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen1' AND time_frame = '180', exposure, 0)) AS CEP1_180_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen1' AND time_frame = 'ALL', exposure, 0)) AS CEP1_ALL_days,
        MAX(IF(antibiotic_subtype = 'Beta Lactam Combo' AND time_frame = '7', exposure, 0)) AS BLC_7_days,
        MAX(IF(antibiotic_subtype = 'Beta Lactam Combo' AND time_frame = '14', exposure, 0)) AS BLC_14_days,
        MAX(IF(antibiotic_subtype = 'Beta Lactam Combo' AND time_frame = '30', exposure, 0)) AS BLC_30_days,
        MAX(IF(antibiotic_subtype = 'Beta Lactam Combo' AND time_frame = '90', exposure, 0)) AS BLC_90_days,
        MAX(IF(antibiotic_subtype = 'Beta Lactam Combo' AND time_frame = '180', exposure, 0)) AS BLC_180_days,
        MAX(IF(antibiotic_subtype = 'Beta Lactam Combo' AND time_frame = 'ALL', exposure, 0)) AS BLC_ALL_days,
        MAX(IF(antibiotic_subtype = 'Tetracycline' AND time_frame = '7', exposure, 0)) AS TET_7_days,
        MAX(IF(antibiotic_subtype = 'Tetracycline' AND time_frame = '14', exposure, 0)) AS TET_14_days,
        MAX(IF(antibiotic_subtype = 'Tetracycline' AND time_frame = '30', exposure, 0)) AS TET_30_days,
        MAX(IF(antibiotic_subtype = 'Tetracycline' AND time_frame = '90', exposure, 0)) AS TET_90_days,
        MAX(IF(antibiotic_subtype = 'Tetracycline' AND time_frame = '180', exposure, 0)) AS TET_180_days,
        MAX(IF(antibiotic_subtype = 'Tetracycline' AND time_frame = 'ALL', exposure, 0)) AS TET_ALL_days,
        MAX(IF(antibiotic_subtype = 'Urinary Antiseptic' AND time_frame = '7', exposure, 0)) AS UA_7_days,
        MAX(IF(antibiotic_subtype = 'Urinary Antiseptic' AND time_frame = '14', exposure, 0)) AS UA_14_days,
        MAX(IF(antibiotic_subtype = 'Urinary Antiseptic' AND time_frame = '30', exposure, 0)) AS UA_30_days,
        MAX(IF(antibiotic_subtype = 'Urinary Antiseptic' AND time_frame = '90', exposure, 0)) AS UA_90_days,
        MAX(IF(antibiotic_subtype = 'Urinary Antiseptic' AND time_frame = '180', exposure, 0)) AS UA_180_days,
        MAX(IF(antibiotic_subtype = 'Urinary Antiseptic' AND time_frame = 'ALL', exposure, 0)) AS UA_ALL_days,
        MAX(IF(antibiotic_subtype = 'Carbapenem' AND time_frame = '7', exposure, 0)) AS CAR_7_days,
        MAX(IF(antibiotic_subtype = 'Carbapenem' AND time_frame = '14', exposure, 0)) AS CAR_14_days,
        MAX(IF(antibiotic_subtype = 'Carbapenem' AND time_frame = '30', exposure, 0)) AS CAR_30_days,
        MAX(IF(antibiotic_subtype = 'Carbapenem' AND time_frame = '90', exposure, 0)) AS CAR_90_days,
        MAX(IF(antibiotic_subtype = 'Carbapenem' AND time_frame = '180', exposure, 0)) AS CAR_180_days,
        MAX(IF(antibiotic_subtype = 'Carbapenem' AND time_frame = 'ALL', exposure, 0)) AS CAR_ALL_days,
        MAX(IF(antibiotic_subtype = 'Penicillin' AND time_frame = '7', exposure, 0)) AS PEN_7_days,
        MAX(IF(antibiotic_subtype = 'Penicillin' AND time_frame = '14', exposure, 0)) AS PEN_14_days,
        MAX(IF(antibiotic_subtype = 'Penicillin' AND time_frame = '30', exposure, 0)) AS PEN_30_days,
        MAX(IF(antibiotic_subtype = 'Penicillin' AND time_frame = '90', exposure, 0)) AS PEN_90_days,
        MAX(IF(antibiotic_subtype = 'Penicillin' AND time_frame = '180', exposure, 0)) AS PEN_180_days,
        MAX(IF(antibiotic_subtype = 'Penicillin' AND time_frame = 'ALL', exposure, 0)) AS PEN_ALL_days,
        MAX(IF(antibiotic_subtype = 'Nitroimidazole' AND time_frame = '7', exposure, 0)) AS NIM_7_days,
        MAX(IF(antibiotic_subtype = 'Nitroimidazole' AND time_frame = '14', exposure, 0)) AS NIM_14_days,
        MAX(IF(antibiotic_subtype = 'Nitroimidazole' AND time_frame = '30', exposure, 0)) AS NIM_30_days,
        MAX(IF(antibiotic_subtype = 'Nitroimidazole' AND time_frame = '90', exposure, 0)) AS NIM_90_days,
        MAX(IF(antibiotic_subtype = 'Nitroimidazole' AND time_frame = '180', exposure, 0)) AS NIM_180_days,
        MAX(IF(antibiotic_subtype = 'Nitroimidazole' AND time_frame = 'ALL', exposure, 0)) AS NIM_ALL_days,
        MAX(IF(antibiotic_subtype = 'Glycopeptide' AND time_frame = '7', exposure, 0)) AS GLY_7_days,
        MAX(IF(antibiotic_subtype = 'Glycopeptide' AND time_frame = '14', exposure, 0)) AS GLY_14_days,
        MAX(IF(antibiotic_subtype = 'Glycopeptide' AND time_frame = '30', exposure, 0)) AS GLY_30_days,
        MAX(IF(antibiotic_subtype = 'Glycopeptide' AND time_frame = '90', exposure, 0)) AS GLY_90_days,
        MAX(IF(antibiotic_subtype = 'Glycopeptide' AND time_frame = '180', exposure, 0)) AS GLY_180_days,
        MAX(IF(antibiotic_subtype = 'Glycopeptide' AND time_frame = 'ALL', exposure, 0)) AS GLY_ALL_days,
        MAX(IF(antibiotic_subtype = 'Oxazolidinone' AND time_frame = '7', exposure, 0)) AS OXA_7_days,
        MAX(IF(antibiotic_subtype = 'Oxazolidinone' AND time_frame = '14', exposure, 0)) AS OXA_14_days,
        MAX(IF(antibiotic_subtype = 'Oxazolidinone' AND time_frame = '30', exposure, 0)) AS OXA_30_days,
        MAX(IF(antibiotic_subtype = 'Oxazolidinone' AND time_frame = '90', exposure, 0)) AS OXA_90_days,
        MAX(IF(antibiotic_subtype = 'Oxazolidinone' AND time_frame = '180', exposure, 0)) AS OXA_180_days,
        MAX(IF(antibiotic_subtype = 'Oxazolidinone' AND time_frame = 'ALL', exposure, 0)) AS OXA_ALL_days,
        MAX(IF(antibiotic_subtype = 'Aminoglycoside' AND time_frame = '7', exposure, 0)) AS AMG_7_days,
        MAX(IF(antibiotic_subtype = 'Aminoglycoside' AND time_frame = '14', exposure, 0)) AS AMG_14_days,
        MAX(IF(antibiotic_subtype = 'Aminoglycoside' AND time_frame = '30', exposure, 0)) AS AMG_30_days,
        MAX(IF(antibiotic_subtype = 'Aminoglycoside' AND time_frame = '90', exposure, 0)) AS AMG_90_days,
        MAX(IF(antibiotic_subtype = 'Aminoglycoside' AND time_frame = '180', exposure, 0)) AS AMG_180_days,
        MAX(IF(antibiotic_subtype = 'Aminoglycoside' AND time_frame = 'ALL', exposure, 0)) AS AMG_ALL_days,
        MAX(IF(antibiotic_subtype = 'Antitubercular' AND time_frame = '7', exposure, 0)) AS AT_7_days,
        MAX(IF(antibiotic_subtype = 'Antitubercular' AND time_frame = '14', exposure, 0)) AS AT_14_days,
        MAX(IF(antibiotic_subtype = 'Antitubercular' AND time_frame = '30', exposure, 0)) AS AT_30_days,
        MAX(IF(antibiotic_subtype = 'Antitubercular' AND time_frame = '90', exposure, 0)) AS AT_90_days,
        MAX(IF(antibiotic_subtype = 'Antitubercular' AND time_frame = '180', exposure, 0)) AS AT_180_days,
        MAX(IF(antibiotic_subtype = 'Antitubercular' AND time_frame = 'ALL', exposure, 0)) AS AT_ALL_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide Combo' AND time_frame = '7', exposure, 0)) AS SULC_7_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide Combo' AND time_frame = '14', exposure, 0)) AS SULC_14_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide Combo' AND time_frame = '30', exposure, 0)) AS SULC_30_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide Combo' AND time_frame = '90', exposure, 0)) AS SULC_90_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide Combo' AND time_frame = '180', exposure, 0)) AS SULC_180_days,
        MAX(IF(antibiotic_subtype = 'Sulfonamide Combo' AND time_frame = 'ALL', exposure, 0)) AS SULC_ALL_days,
        MAX(IF(antibiotic_subtype = 'Macrolide' AND time_frame = '7', exposure, 0)) AS MAC_7_days,
        MAX(IF(antibiotic_subtype = 'Macrolide' AND time_frame = '14', exposure, 0)) AS MAC_14_days,
        MAX(IF(antibiotic_subtype = 'Macrolide' AND time_frame = '30', exposure, 0)) AS MAC_30_days,
        MAX(IF(antibiotic_subtype = 'Macrolide' AND time_frame = '90', exposure, 0)) AS MAC_90_days,
        MAX(IF(antibiotic_subtype = 'Macrolide' AND time_frame = '180', exposure, 0)) AS MAC_180_days,
        MAX(IF(antibiotic_subtype = 'Macrolide' AND time_frame = 'ALL', exposure, 0)) AS MAC_ALL_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen2' AND time_frame = '7', exposure, 0)) AS CEP2_7_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen2' AND time_frame = '14', exposure, 0)) AS CEP2_14_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen2' AND time_frame = '30', exposure, 0)) AS CEP2_30_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen2' AND time_frame = '90', exposure, 0)) AS CEP2_90_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen2' AND time_frame = '180', exposure, 0)) AS CEP2_180_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen2' AND time_frame = 'ALL', exposure, 0)) AS CEP2_ALL_days,
        MAX(IF(antibiotic_subtype = 'Ansamycin' AND time_frame = '7', exposure, 0)) AS ANS_7_days,
        MAX(IF(antibiotic_subtype = 'Ansamycin' AND time_frame = '14', exposure, 0)) AS ANS_14_days,
        MAX(IF(antibiotic_subtype = 'Ansamycin' AND time_frame = '30', exposure, 0)) AS ANS_30_days,
        MAX(IF(antibiotic_subtype = 'Ansamycin' AND time_frame = '90', exposure, 0)) AS ANS_90_days,
        MAX(IF(antibiotic_subtype = 'Ansamycin' AND time_frame = '180', exposure, 0)) AS ANS_180_days,
        MAX(IF(antibiotic_subtype = 'Ansamycin' AND time_frame = 'ALL', exposure, 0)) AS ANS_ALL_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen3' AND time_frame = '7', exposure, 0)) AS CEP3_7_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen3' AND time_frame = '14', exposure, 0)) AS CEP3_14_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen3' AND time_frame = '30', exposure, 0)) AS CEP3_30_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen3' AND time_frame = '90', exposure, 0)) AS CEP3_90_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen3' AND time_frame = '180', exposure, 0)) AS CEP3_180_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen3' AND time_frame = 'ALL', exposure, 0)) AS CEP3_ALL_days,
        MAX(IF(antibiotic_subtype = 'Lincosamide' AND time_frame = '7', exposure, 0)) AS LIN_7_days,
        MAX(IF(antibiotic_subtype = 'Lincosamide' AND time_frame = '14', exposure, 0)) AS LIN_14_days,
        MAX(IF(antibiotic_subtype = 'Lincosamide' AND time_frame = '30', exposure, 0)) AS LIN_30_days,
        MAX(IF(antibiotic_subtype = 'Lincosamide' AND time_frame = '90', exposure, 0)) AS LIN_90_days,
        MAX(IF(antibiotic_subtype = 'Lincosamide' AND time_frame = '180', exposure, 0)) AS LIN_180_days,
        MAX(IF(antibiotic_subtype = 'Lincosamide' AND time_frame = 'ALL', exposure, 0)) AS LIN_ALL_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen4' AND time_frame = '7', exposure, 0)) AS CEP4_7_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen4' AND time_frame = '14', exposure, 0)) AS CEP4_14_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen4' AND time_frame = '30', exposure, 0)) AS CEP4_30_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen4' AND time_frame = '90', exposure, 0)) AS CEP4_90_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen4' AND time_frame = '180', exposure, 0)) AS CEP4_180_days,
        MAX(IF(antibiotic_subtype = 'Cephalosporin Gen4' AND time_frame = 'ALL', exposure, 0)) AS CEP4_ALL_days

    FROM
        subtype_exposure
    GROUP BY
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
)
SELECT * FROM final_subtype_exposure;
