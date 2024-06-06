-- This query is the main query for creating a table named microbiology_cultures_cohort that forms the basis of the microbiology cultures cohort. 
-- The table is generated through a series of steps, each designed to filter and enrich the dataset. 
-- Once the main cohort table is created, additional features will be added to this table to complete the dataset for analysis.


######################################################################################## 
-- Create or replace the cohort table named microbiology_cultures_cohort
######################################################################################## 

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` AS


######################################################################################## 
-- Step 1: Extract microbiology cultures for specific types (URINE, RESPIRATORY, BLOOD)
######################################################################################## 

WITH microbiology_cultures AS (
    SELECT DISTINCT
        op.anon_id, 
        op.pat_enc_csn_id_coded, 
        op.order_proc_id_coded, 
        op.order_time_jittered_utc, 
        op.ordering_mode,
        CASE 
            WHEN op.description LIKE '%URINE%' THEN 'URINE'
            WHEN op.description LIKE '%RESPIRATORY%' THEN 'RESPIRATORY'
            WHEN op.description LIKE '%BLOOD%' THEN 'BLOOD'
            ELSE 'OTHER' 
        END AS culture_description  -- Capture the culture type
    FROM 
        `som-nero-phi-jonc101.shc_core_2023.order_proc` op
    INNER JOIN
        `som-nero-phi-jonc101.shc_core_2023.lab_result` lr
    ON
        op.order_proc_id_coded = lr.order_id_coded
    WHERE
        op.order_type LIKE "Microbiology%"
        AND (op.description LIKE "%URINE%" OR op.description LIKE "%RESPIRATORY%" OR op.description LIKE "%BLOOD%")
),


######################################################################################## 
-- Step 2: Filter for adult patients only
########################################################################################    

adult_microbiology_cultures AS (
    SELECT 
        mc.anon_id, 
        mc.pat_enc_csn_id_coded, 
        mc.order_proc_id_coded, 
        mc.order_time_jittered_utc, 
        mc.ordering_mode,
        mc.culture_description  -- Include culture_description here
    FROM 
        microbiology_cultures mc
    INNER JOIN
        `som-nero-phi-jonc101.shc_core_2023.demographic` demo
    USING
        (anon_id)
    WHERE
        DATE_DIFF(CAST(mc.order_time_jittered_utc as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
),

    
######################################################################################## 
-- Step 3: Identify culture orders within the prior two weeks
########################################################################################     
    
order_in_prior_two_weeks AS (
    SELECT DISTINCT
         auc.order_proc_id_coded
    FROM 
        `som-nero-phi-jonc101.shc_core_2023.order_proc` op
    INNER JOIN
        `som-nero-phi-jonc101.shc_core_2023.lab_result` lr
    ON
        op.order_proc_id_coded = lr.order_id_coded
    INNER JOIN
        adult_microbiology_cultures auc 
    ON
        op.anon_id = auc.anon_id
    WHERE
        op.order_type LIKE "Microbiology%"
        AND (op.description LIKE "%URINE%" OR op.description LIKE "%RESPIRATORY%" OR op.description LIKE "%BLOOD%")
        AND auc.order_time_jittered_utc > op.order_time_jittered_utc
        AND TIMESTAMP_DIFF(auc.order_time_jittered_utc, op.order_time_jittered_utc, DAY) < 14
),

    
######################################################################################## 
-- Step 4: Exclude cultures with a prior culture order in the last two weeks
########################################################################################       

included_microbiology_cultures AS (
    SELECT DISTINCT
        amc.*
    FROM 
        adult_microbiology_cultures amc
    WHERE 
        amc.order_proc_id_coded NOT IN (SELECT order_proc_id_coded FROM order_in_prior_two_weeks)
),


    
###########################################################################################################
-- Step 5: Flag cultures as positive if they have corresponding entries in the culture_sensitivity table
###########################################################################################################    

all_cultures_with_flag AS (
    SELECT 
        imc.anon_id, 
        imc.pat_enc_csn_id_coded, 
        imc.order_proc_id_coded, 
        imc.order_time_jittered_utc, 
        imc.ordering_mode,
        imc.culture_description,
        IF(cs.order_proc_id_coded IS NOT NULL, 1, 0) AS was_positive
    FROM 
        included_microbiology_cultures imc
    LEFT JOIN 
        (SELECT DISTINCT order_proc_id_coded FROM `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity`) cs
    ON 
        imc.order_proc_id_coded = cs.order_proc_id_coded
),


    
#########################################################################################################################
-- Step 6: Get detailed information for positive cultures, clean antibiotic names, and exclude non-antibiotic entries
#########################################################################################################################     

positive_culture_details AS (
    SELECT 
        cs.order_proc_id_coded,
        cs.organism,
        INITCAP(LOWER(TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        LOWER(cs.antibiotic),  -- Convert to lowercase to ensure case-insensitive matching
                        '\\s*synergy\\s*$', ''),  -- Remove "Synergy"
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''  -- General cleaning, already lowercase due to the LOWER function
            ), 'penicillin.*', 'Penicillin'  -- Merge any 'Penicillin' variations with 'Penicillin', case-insensitive
        )))) AS antibiotic,
        cs.suscept as susceptibility,
        cs.specimen_source,
        cs.specimen_type
    FROM 
        `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity` cs
    INNER JOIN (
        SELECT 
            INITCAP(LOWER(TRIM(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            LOWER(antibiotic),  -- Convert to lowercase to ensure case-insensitive matching
                            '\\s*synergy\\s*$', ''),  -- Remove "Synergy"
                        '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''  -- General cleaning, already lowercase due to the LOWER function
                    ), 'penicillin.*', 'Penicillin'  -- Merge any 'Penicillin' variations with 'Penicillin', case-insensitive
            )))) AS cleaned_antibiotic,
            COUNT(*) AS count
        FROM 
            `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity`
        GROUP BY 
            cleaned_antibiotic
        HAVING 
            COUNT(*) >= 10
    ) AS antibiotic_counts ON INITCAP(LOWER(TRIM(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    LOWER(cs.antibiotic),  -- Convert to lowercase to ensure case-insensitive matching
                    '\\s*synergy\\s*$', ''),  -- Remove "Synergy"
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''  -- General cleaning, already lowercase due to the LOWER function
            ), 'penicillin.*', 'Penicillin'  -- Merge any 'Penicillin' variations with 'Penicillin', case-insensitive
    )))) = antibiotic_counts.cleaned_antibiotic
    WHERE
        NOT (
            cs.antibiotic LIKE '%InBasket%'  
            OR cs.antibiotic LIKE '%Beta Lactamase%'  
            OR cs.antibiotic LIKE '%BlaZ PCR%'  
            OR cs.antibiotic LIKE '%Carbapenemase%'  
            OR cs.antibiotic LIKE '%D-Test%'  
            OR cs.antibiotic LIKE '%Esbl%'  
            OR cs.antibiotic LIKE '%ermPCR%'  
            OR cs.antibiotic LIKE '%Mupirocin%'  
            OR cs.antibiotic LIKE '%IMP%'  
            OR cs.antibiotic LIKE '%Inducible Clindamycin%'  
            OR cs.antibiotic LIKE '%INTERNAL CONTROL%'  
            OR cs.antibiotic LIKE '%KPC%'  
            OR cs.antibiotic LIKE '%MecA PCR%'  
            OR cs.antibiotic LIKE '%NDM%'  
            OR cs.antibiotic LIKE '%Ox Plate Screen%'  
            OR cs.antibiotic LIKE '%OXA-48-LIKE%'  
            OR cs.antibiotic LIKE '%VIM%'  
            OR cs.antibiotic LIKE '%Method%'  
            OR cs.antibiotic LIKE '%INH%'   
            OR cs.antibiotic LIKE '%Polymyxin B%' 
            OR cs.antibiotic LIKE '%Nalidixic%'   
            OR cs.antibiotic LIKE '%Flucytosine%' 
            OR cs.antibiotic LIKE '%Rifampin%' 
            OR cs.antibiotic LIKE '%Ethambutol%' 
            OR cs.antibiotic LIKE '%Pyrazinamide%' 
            OR cs.antibiotic LIKE '%Clofazimine%' 
            OR cs.antibiotic LIKE '%Rifabutin%' 
            OR cs.antibiotic IN ('Posaconazole','Penicillin/Ampicillin','Omadacycline', 'Amphotericin B', 'Polymixin B', 'Fluconazole', 'Itraconazole', 'Caspofungin', 'Voriconazole', 'Anidulafungin', 'Micafungin', 'Isavuconazole', 'Antibiotic', 'OXA48-LIKE PCR', 'ESBL confirmation test', 'Oxacillin Screen')
        )
)

#########################################################################################################################
  -- Step 7: Final selection of required fields
#########################################################################################################################   

SELECT 
    acwf.anon_id,
    acwf.pat_enc_csn_id_coded,
    acwf.order_proc_id_coded,
acwf.order_time_jittered_utc,
acwf.ordering_mode,
acwf.culture_description,
acwf.was_positive,
pcd.organism,
pcd.antibiotic,
pcd.susceptibility,
pcd.specimen_source,
pcd.specimen_type
FROM
all_cultures_with_flag acwf
LEFT JOIN
positive_culture_details pcd
ON
acwf.order_proc_id_coded = pcd.order_proc_id_coded;
   
