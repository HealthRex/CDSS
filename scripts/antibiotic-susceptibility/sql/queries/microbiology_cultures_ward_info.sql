-- -- Extracting  Hospital department type (inpatient, outpatient, ER, ICU) table --
-- this query has 7 steps --
-- 1.	**Extract ER and ICU Information from adt Table** --

-- 2.	**Extract ER Information from order_proc Table**--

-- 3.	**Combine ER and ICU Information**--

-- 4.	**Extract IP and OP Information from order_proc Table**--

-- 5.	**Combine All Information into One Temporary Table**--

-- 6.   **Extract  ICU stay based on transfer orders.** --

-- 7.	**Create Final Table Using microbiology_cultures_cohort**--


###################################################################
-- Step 1: Extract ER and ICU Information from adt Table
###################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_icu_info_adt` AS
SELECT
    anon_id,
    pat_enc_csn_id_coded,
    CASE 
        WHEN pat_class = 'Emergency' OR pat_class = 'Emergency Services' THEN 1
        ELSE 0
    END AS hosp_ward_ER,
    CASE 
        WHEN pat_class = 'Intensive Care (IC)' THEN 1
        ELSE 0
    END AS hosp_ward_ICU,
    CASE 
        WHEN pat_lv_of_care LIKE "%Critical Care" THEN 1
        ELSE 0
    END AS hosp_ward_Critical_Care
FROM
    `som-nero-phi-jonc101.shc_core_2023.adt`;

###################################################################
-- Step 2: Extract ER Information from order_proc Table
###################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_info_order_proc` AS
SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    CASE 
        WHEN proc_pat_class = 'Emergency' OR proc_pat_class = 'Emergency Services' THEN 1
        ELSE 0
    END AS hosp_ward_ER_order_proc
FROM
    `som-nero-phi-jonc101.shc_core_2023.order_proc`;


###################################################################
-- Step 3: Combine ER and ICU Information
###################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_combined_er_icu_info` AS
SELECT
    adt.anon_id,
    adt.pat_enc_csn_id_coded,
    adt.hosp_ward_ER,
    adt.hosp_ward_ICU,
    adt.hosp_ward_Critical_Care,
    er.order_proc_id_coded,
    er.hosp_ward_ER_order_proc
FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_icu_info_adt` adt
LEFT JOIN
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_info_order_proc` er
ON
    adt.pat_enc_csn_id_coded = er.pat_enc_csn_id_coded;


###################################################################
-- Step 4: Extract IP and OP Information from order_proc Table
###################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_ip_op_info` AS
SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    order_time_jittered_utc,
    CASE 
        WHEN ordering_mode = 'Inpatient' THEN 1
        ELSE 0
    END AS hosp_ward_IP,
    CASE 
        WHEN ordering_mode = 'Outpatient' THEN 1
        ELSE 0
    END AS hosp_ward_OP
FROM
    `som-nero-phi-jonc101.shc_core_2023.order_proc`;

###################################################################
-- Step 5: Combine All Information into One Temporary Table
###################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_combined_hosp_ward_info` AS
SELECT
    ipop.anon_id,
    ipop.pat_enc_csn_id_coded,
    ipop.order_proc_id_coded,
    ipop.order_time_jittered_utc,
    ipop.hosp_ward_IP,
    ipop.hosp_ward_OP,
    COALESCE(icu.hosp_ward_ER, 0) AS hosp_ward_ER_adt,
    COALESCE(icu.hosp_ward_ER_order_proc, 0) AS hosp_ward_ER_order_proc,
    COALESCE(icu.hosp_ward_ICU, 0) AS hosp_ward_ICU,
    COALESCE(icu.hosp_ward_Critical_Care, 0) AS hosp_ward_Critical_Care
FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_ip_op_info` ipop
LEFT JOIN
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_combined_er_icu_info` icu
ON
    ipop.pat_enc_csn_id_coded = icu.pat_enc_csn_id_coded AND ipop.order_proc_id_coded = icu.order_proc_id_coded;


###################################################################
-- Step 6: Extract  ICU stay based on transfer orders
###################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_cohortOfInterest` AS
SELECT DISTINCT
    pat_enc_csn_id_coded,
    hosp_disch_time_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2023.encounter`
WHERE hosp_disch_time_jittered_utc IS NOT NULL;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_ordersTransfer` AS
SELECT DISTINCT
    pat_enc_csn_id_coded,
    description,
    level_of_care,
    service,
    order_inst_jittered_utc
FROM `som-nero-phi-jonc101.shc_core_2023.order_proc` AS procedures
WHERE (description LIKE "CHANGE LEVEL OF CARE/TRANSFER PATIENT" OR description LIKE "ADMIT TO INPATIENT") AND level_of_care IS NOT NULL;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.temp_icuTransferCount` AS
SELECT
    mc.pat_enc_csn_id_coded,
    COUNT(CASE WHEN level_of_care LIKE "Critical Care" THEN 1 END) AS numICUTransfers
FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` mc
LEFT JOIN
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_ordersTransfer` ot
ON
    mc.pat_enc_csn_id_coded = ot.pat_enc_csn_id_coded
GROUP BY
    mc.pat_enc_csn_id_coded;

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_with_icu_flag` AS
SELECT DISTINCT
    mc.anon_id,
    mc.pat_enc_csn_id_coded,
    mc.order_proc_id_coded,
    mc.order_time_jittered_utc,
    CASE WHEN itc.numICUTransfers > 0 THEN 1 ELSE 0 END AS icu_flag
FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` mc
LEFT JOIN
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_icuTransferCount` itc
ON
    mc.pat_enc_csn_id_coded = itc.pat_enc_csn_id_coded;

#######################################################################################################
-- Step 7: Create the Final Table with Correct Binary Indicators for Each Hospital Ward and ICU Flag
#######################################################################################################
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_ward_info` AS
SELECT
    mc.anon_id,
    mc.pat_enc_csn_id_coded,
    mc.order_proc_id_coded,
    mc.order_time_jittered_utc,
    MAX(CASE WHEN chwi.hosp_ward_IP = 1 THEN 1 ELSE 0 END) AS hosp_ward_IP,
    MAX(CASE WHEN chwi.hosp_ward_OP = 1 THEN 1 ELSE 0 END) AS hosp_ward_OP,
    MAX(CASE WHEN chwi.hosp_ward_ER_adt = 1 OR chwi.hosp_ward_ER_order_proc = 1 THEN 1 ELSE 0 END) AS hosp_ward_ER,
    MAX(
        CASE 
            WHEN chwi.hosp_ward_ICU = 1 THEN 1 
            WHEN icu_flag.icu_flag = 1 THEN 1 
            WHEN chwi.hosp_ward_Critical_Care = 1 THEN 1
            ELSE 0 
        END
    ) AS hosp_ward_ICU
FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` mc
LEFT JOIN
    `som-nero-phi-jonc101.antimicrobial_stewardship.temp_combined_hosp_ward_info` chwi
ON
    mc.anon_id = chwi.anon_id 
    AND mc.pat_enc_csn_id_coded = chwi.pat_enc_csn_id_coded 
    AND mc.order_proc_id_coded = chwi.order_proc_id_coded
LEFT JOIN
    `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_with_icu_flag` icu_flag
ON
    mc.anon_id = icu_flag.anon_id 
    AND mc.pat_enc_csn_id_coded = icu_flag.pat_enc_csn_id_coded 
    AND mc.order_proc_id_coded = icu_flag.order_proc_id_coded
GROUP BY
    mc.anon_id, 
    mc.pat_enc_csn_id_coded, 
    mc.order_proc_id_coded, 
    mc.order_time_jittered_utc;

    
