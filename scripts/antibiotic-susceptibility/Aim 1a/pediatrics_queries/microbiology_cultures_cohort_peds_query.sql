######################################################################################## 
-- Create or replace the cohort table named microbiology_cultures_cohort_peds
######################################################################################## 

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort_peds` AS

-- Step 1: Extract microbiology cultures for specific types (URINE, RESPIRATORY, BLOOD)
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
        `som-nero-phi-jonc101.lpch_core_2024.lpch_order_proc` op
    INNER JOIN
        `som-nero-phi-jonc101.lpch_core_2024.lpch_lab_result` lr
    ON
        op.order_proc_id_coded = lr.order_id_coded
    WHERE
        op.order_type LIKE "Microbiology%"
        AND (op.description LIKE "%URINE%" OR op.description LIKE "%RESPIRATORY%" OR op.description LIKE "%BLOOD%")
        AND not op.order_status like any ('Discontinued','Canceled')
),


######################################################################################## 
-- Step 2: Filter for pediatric patients only (90 days to <18 years)
########################################################################################    

pediatric_microbiology_cultures AS (
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
        `som-nero-phi-jonc101.lpch_core_2024.lpch_demographic` demo
    USING
        (anon_id)
    WHERE
        -- at least 90 days old
        DATE_DIFF(CAST(mc.order_time_jittered_utc AS DATE), demo.birth_date_jittered, DAY) >= 90
        -- but younger than 18 years
        AND DATE_DIFF(CAST(mc.order_time_jittered_utc AS DATE), demo.birth_date_jittered, YEAR) < 18
),

    
######################################################################################## 
-- Step 3: Identify culture orders within the prior two weeks
########################################################################################     
    
order_in_prior_two_weeks AS (
    SELECT DISTINCT
         auc.order_proc_id_coded
    FROM 
        `som-nero-phi-jonc101.lpch_core_2024.lpch_order_proc` op
    INNER JOIN
        `som-nero-phi-jonc101.lpch_core_2024.lpch_lab_result` lr
    ON
        op.order_proc_id_coded = lr.order_id_coded
    INNER JOIN
        pediatric_microbiology_cultures auc 
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
        pmc.*
    FROM 
        pediatric_microbiology_cultures pmc
    WHERE 
        pmc.order_proc_id_coded NOT IN (SELECT order_proc_id_coded FROM order_in_prior_two_weeks)
),

   
###########################################################################################################
-- Step 5: Growth-based positivity using lab result interpretation + organism
###########################################################################################################

growth_based_positivity AS (
  SELECT DISTINCT
    imc.anon_id,
    imc.pat_enc_csn_id_coded,
    imc.order_proc_id_coded,
    imc.order_time_jittered_utc,
    imc.ordering_mode,
    imc.culture_description,
    CASE
      WHEN cs.organism IS NOT NULL 
       AND NOT LOWER(lr.ord_value) LIKE ANY ('%no%grow%', '%not%detect%', '%negative%')
       AND (lr.extended_value_comment IS NULL OR 
            NOT UPPER(COALESCE(lr.extended_value_comment, lr.extended_comp_comment)) LIKE ANY (
                '%NO GROWTH%',
                '%CONTAMIN%',
                '%NORMAL RESP%',
                '%MIXED%',
                '%COAG% NEG%',
                '%GRAM%POS%RODS%',
                '%GRAM%+%RODS%'
            )
           )
      THEN 1 ELSE 0 END AS was_positive
  FROM included_microbiology_cultures imc
  LEFT JOIN `som-nero-phi-jonc101.lpch_core_2024.lpch_lab_result` lr
    ON imc.order_proc_id_coded = lr.order_id_coded
   AND imc.pat_enc_csn_id_coded = lr.pat_enc_csn_id_coded
   AND imc.anon_id = lr.anon_id
  LEFT JOIN (
    SELECT DISTINCT order_proc_id_coded, organism
    FROM `som-nero-phi-jonc101.lpch_core_2024.lpch_culture_sensitivity`
    WHERE organism IS NOT NULL AND TRIM(organism) != ''
  ) cs
    ON imc.order_proc_id_coded = cs.order_proc_id_coded
),


#########################################################################################################################
-- Step 6: Get detailed information for positive cultures, clean antibiotic names, and exclude non-antibiotic entries
#########################################################################################################################     
positive_culture_details AS (
    SELECT 
        cs.order_proc_id_coded,
        cs.organism,
        -- Clean and standardize the antibiotic name using the updated cleaning approach
        INITCAP(TRIM(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    LOWER(cs.antibiotic),
                    'penicillin[^a-z].*$', 'penicillin'
                ),
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''
            ),
              '\\s*\\d+(\\.\\d+)?\\s*(mg|mcg|gram|ml|%)', ''  -- Remove dosages or concentrations
          ),
          '\\(.*?\\)', ''  -- Remove text in parentheses
        ),' in.*$|tablet|capsule|intravenous|piggyback|' ||
                            'solution|suspension|oral|sodium|chloride|' ||
                            'injection|citrate|soln|dextrose|iv|' ||
                            'macrocrystals|macrocrystal|axetil|potassium|packet|' ||
                            'monohydrate|ethylsuccinate|powder|mandelate|' ||
                            'hyclate|hcl|hippurate|tromethamine|' ||
                            'million|unit|syrup|chewable|delayed|mphase|' ||
                            'release|benzathine|syringe|dispersible|' ||
                            'sulfate|procaine|blue|hyos|sod*phos|' ||
                            'susp|and|fosamil|extended|succinate|granules|' ||
                            'delay|pot|ext|rel|cyam|salicylate|salicyl|' ||
                            'sodphos|methylene|stearate|synergy', ''                   
        ),
        '\\d|\\sfor\\s*|/ml\\s*|\\sml\\s*|\\-+\\s*|\\,+\\s*',''
        )
        )
      )  AS antibiotic,
        cs.suscept AS susceptibility
    FROM 
        som-nero-phi-jonc101.lpch_core_2024.lpch_culture_sensitivity cs
    INNER JOIN (
        -- Subquery to get antibiotic counts for those with more than 10 occurrences
        SELECT 
          INITCAP(TRIM(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    LOWER(antibiotic),
                    'penicillin[^a-z].*$', 'penicillin'
                ),
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''
            ),
              '\\s*\\d+(\\.\\d+)?\\s*(mg|mcg|gram|ml|%)', ''  -- Remove dosages or concentrations
          ),
          '\\(.*?\\)', ''  -- Remove text in parentheses
        ),' in.*$|tablet|capsule|intravenous|piggyback|' ||
                            'solution|suspension|oral|sodium|chloride|' ||
                            'injection|citrate|soln|dextrose|iv|' ||
                            'macrocrystals|macrocrystal|axetil|potassium|packet|' ||
                            'monohydrate|ethylsuccinate|powder|mandelate|' ||
                            'hyclate|hcl|hippurate|tromethamine|' ||
                            'million|unit|syrup|chewable|delayed|mphase|' ||
                            'release|benzathine|syringe|dispersible|' ||
                            'sulfate|procaine|blue|hyos|sod*phos|' ||
                            'susp|and|fosamil|extended|succinate|granules|' ||
                            'delay|pot|ext|rel|cyam|salicylate|salicyl|' ||
                            'sodphos|methylene|stearate|synergy', ''                   
        ),
        '\\d|\\sfor\\s*|/ml\\s*|\\sml\\s*|\\-+\\s*|\\,+\\s*',''
        )
        )
      )AS cleaned_antibiotic,
            COUNT(*) AS count
        FROM 
            som-nero-phi-jonc101.lpch_core_2024.lpch_culture_sensitivity
        GROUP BY 
            cleaned_antibiotic
        HAVING 
            COUNT(*) >= 10  -- Include only antibiotics that appear 10 times or more
    ) AS antibiotic_counts 
    ON 


      INITCAP(TRIM(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
          REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    LOWER(cs.antibiotic),
                    'penicillin[^a-z].*$', 'penicillin'
                ),
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''
            ),
              '\\s*\\d+(\\.\\d+)?\\s*(mg|mcg|gram|ml|%)', ''  -- Remove dosages or concentrations
          ),
          '\\(.*?\\)', ''  -- Remove text in parentheses
        ),' in.*$|tablet|capsule|intravenous|piggyback|' ||
                            'solution|suspension|oral|sodium|chloride|' ||
                            'injection|citrate|soln|dextrose|iv|' ||
                            'macrocrystals|macrocrystal|axetil|potassium|packet|' ||
                            'monohydrate|ethylsuccinate|powder|mandelate|' ||
                            'hyclate|hcl|hippurate|tromethamine|' ||
                            'million|unit|syrup|chewable|delayed|mphase|' ||
                            'release|benzathine|syringe|dispersible|' ||
                            'sulfate|procaine|blue|hyos|sod*phos|' ||
                            'susp|and|fosamil|extended|succinate|granules|' ||
                            'delay|pot|ext|rel|cyam|salicylate|salicyl|' ||
                            'sodphos|methylene|stearate|synergy', ''                   
        ),
        '\\d|\\sfor\\s*|/ml\\s*|\\sml\\s*|\\-+\\s*|\\,+\\s*',''
        )
        )
      )= antibiotic_counts.cleaned_antibiotic
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
            OR cs.antibiotic LIKE '%Inh%'  
            OR cs.antibiotic LIKE '%Polymyxin B%' 
            OR cs.antibiotic LIKE '%Nalidixic%'   
            OR cs.antibiotic LIKE '%Flucytosine%' 
            OR cs.antibiotic LIKE '%Rifampin%' 
            OR cs.antibiotic LIKE '%Ethambutol%' 
            OR cs.antibiotic LIKE '%Pyrazinamide%' 
            OR cs.antibiotic LIKE '%Clofazimine%' 
            OR cs.antibiotic LIKE '%Rifabutin%' 
            OR cs.antibiotic LIKE '%Fluconazole%' 
            OR cs.antibiotic LIKE '%Dtest%' 
            OR cs.antibiotic LIKE '%Strep%' 
            OR cs.antibiotic LIKE '%Genta%'
            OR cs.antibiotic LIKE '%D-Test%' OR
            LOWER(cs.antibiotic) LIKE '%inbasket%' OR
    LOWER(cs.antibiotic) LIKE '%beta lactamase%' OR
    LOWER(cs.antibiotic) LIKE '%blaz%' OR
    LOWER(cs.antibiotic) LIKE '%carbapenemase%' OR
    LOWER(cs.antibiotic) LIKE '%dtest%' OR
    LOWER(cs.antibiotic) LIKE '%d-test%' OR
    LOWER(cs.antibiotic) LIKE '%esbl%' OR
    LOWER(cs.antibiotic) LIKE '%ermpcr%' OR
    LOWER(cs.antibiotic) LIKE '%mupirocin%' OR
    LOWER(cs.antibiotic) LIKE '%internal control%' OR
    LOWER(cs.antibiotic) LIKE '%kpc%' OR
    LOWER(cs.antibiotic) LIKE '%meca%' OR
    LOWER(cs.antibiotic) LIKE '%ndm%' OR
    LOWER(cs.antibiotic) LIKE '%oxa%' OR
    LOWER(cs.antibiotic) LIKE '%vim%' OR
    LOWER(cs.antibiotic) LIKE '%method%' OR
    LOWER(cs.antibiotic) LIKE '%inh%' OR
    LOWER(cs.antibiotic) LIKE '%nalidixic%' OR
    LOWER(cs.antibiotic) LIKE '%flucytosine%' OR
    LOWER(cs.antibiotic) LIKE '%rifampin%' OR
    LOWER(cs.antibiotic) LIKE '%ethambutol%' OR
    LOWER(cs.antibiotic) LIKE '%pyrazinamide%' OR
    LOWER(cs.antibiotic) LIKE '%clofazimine%' OR
    LOWER(cs.antibiotic) LIKE '%rifabutin%' OR
    LOWER(cs.antibiotic) LIKE '%fluconazole%' OR
    LOWER(cs.antibiotic) LIKE '%voriconazole%' OR
    LOWER(cs.antibiotic) LIKE '%itraconazole%' OR
    LOWER(cs.antibiotic) LIKE '%caspofungin%' OR
    LOWER(cs.antibiotic) LIKE '%micafungin%' OR
    LOWER(cs.antibiotic) LIKE '%anidulafungin%' OR
    LOWER(cs.antibiotic) LIKE '%isavuconazole%' OR
    LOWER(cs.antibiotic) LIKE '%amphotericin%' OR
    LOWER(cs.antibiotic) LIKE '%ticarcillin/clavulanate%' OR
    LOWER(cs.antibiotic) LIKE '%ticarcillin/clavulanic acid%' OR cs.antibiotic IN ('Posaconazole','Penicillin/Ampicillin','Omadacycline', 'Amphotericin B', 'Polymixin B', 'Fluconazole', 'Itraconazole', 'Caspofungin', 'Voriconazole', 'Anidulafungin', 'Micafungin', 'Isavuconazole', 'Antibiotic', 'OXA48-LIKE PCR', 'ESBL confirmation test', 'Oxacillin Screen','Amphotericin B', 'Ticarcillin/Clavulanate','Ticarcillin/Clavulanic Acid','Inh','Esbl Check','Dtest','Imipenem/Ebactam')
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
    CASE
        WHEN pcd.susceptibility IS NULL THEN NULL  -- Keep NULL values unchanged
        WHEN pcd.susceptibility IN ('Susceptible', 'Not Detected', 'Negative' ) THEN 'Susceptible'
        WHEN pcd.susceptibility IN ('Resistant', 'Non Susceptible', 'Positive', 'Detected') THEN 'Resistant'
        WHEN pcd.susceptibility IN ('Intermediate', 'Susceptible - Dose Dependent') THEN 'Intermediate'
        WHEN pcd.susceptibility IN ('No Interpretation', 'Not done', 'Inconclusive', 'See Comment') THEN 'Inconclusive'
        WHEN pcd.susceptibility IN ('Synergy', 'No Synergy') THEN 'Synergism'
        ELSE 'Unknown'  -- Mark unexpected values as Unknown
    END AS susceptibility
FROM
    growth_based_positivity acwf
LEFT JOIN
    positive_culture_details pcd
ON
    acwf.order_proc_id_coded = pcd.order_proc_id_coded
WHERE
    -- Exclude rows where susceptibility would be 'Unknown'
    (pcd.susceptibility IS NULL OR
    pcd.susceptibility IN ('Susceptible', 'Positive', 'Detected',
                           'Resistant', 'Non Susceptible', 'Negative',
                           'Intermediate', 'Susceptible - Dose Dependent',
                           'No Interpretation', 'Not done', 'Inconclusive', 'See Comment',
                           'Synergy', 'No Synergy', 'Not Detected'));
