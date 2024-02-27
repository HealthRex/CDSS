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
        END AS culture_description  -- This line is added to capture the culture type
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


-- Filter to adult only
adult_microbiology_cultures AS (
    SELECT 
        mc.anon_id, 
        mc.pat_enc_csn_id_coded, 
        mc.order_proc_id_coded, 
        mc.order_time_jittered_utc, 
        mc.ordering_mode,
        mc.culture_description  -- Include culture_description here
    FROM 
        microbiology_cultures mc  -- Assume mc is the alias for microbiology_cultures
    INNER JOIN
        `som-nero-phi-jonc101.shc_core_2023.demographic` demo
    USING
        (anon_id)
    WHERE
        DATE_DIFF(CAST(mc.order_time_jittered_utc as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
),


-- Must not have any culture orders (that go on to result in lab results) in prior two weeks

-- This finds cultures that do have other cultures orders in prior two weeks
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


-- Remove cultures that have a prior culture order in the last two weeks
included_microbiology_cultures AS (
    SELECT DISTINCT
        amc.*
    FROM 
        adult_microbiology_cultures amc
    WHERE 
        amc.order_proc_id_coded NOT IN (SELECT order_proc_id_coded FROM order_in_prior_two_weeks)
),


-- Prior antibiotics ordered within 14 days before the culture order
prior_antibiotics AS (
    SELECT 
        amc.anon_id, 
        amc.order_proc_id_coded, 
        STRING_AGG(om.med_description, ', ') AS prior_antibiotics
    FROM 
        included_microbiology_cultures amc
    INNER JOIN
        `som-nero-phi-jonc101.shc_core_2023.order_med` om
    ON
        amc.anon_id = om.anon_id
    WHERE
        TIMESTAMP_DIFF(amc.order_time_jittered_utc, om.ordering_date_jittered_utc, DAY) BETWEEN 0 AND 14
    GROUP BY 
        amc.anon_id, amc.order_proc_id_coded
),


-- Identify all cultures and flag them as positive if they have corresponding entries in the culture_sensitivity table
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

-- Get detailed info for positive cultures, cleaning antibiotic names, excluding non-antibiotic entries, and merging dose variations
positive_culture_details AS (
    SELECT 
        cs.order_proc_id_coded,
        cs.organism,
        -- Standardize antibiotic names by merging dose variations and similar names
        CASE
            WHEN cs.antibiotic LIKE 'Amikacin%' THEN 'Amikacin'
            WHEN cs.antibiotic LIKE 'Cefazolin%' THEN 'Cefazolin'
            WHEN cs.antibiotic LIKE 'Cefotaxime%' THEN 'Cefotaxime'
            WHEN cs.antibiotic LIKE 'Ceftazidime%' THEN 'Ceftazidime'
            WHEN cs.antibiotic LIKE 'Ceftriaxone%' THEN 'Ceftriaxone'
            WHEN cs.antibiotic LIKE 'Cefuroxime%' THEN 'Cefuroxime'
            WHEN cs.antibiotic LIKE 'Ethambutol%' THEN 'Ethambutol'
            WHEN cs.antibiotic LIKE 'Gentamicin%' THEN 'Gentamicin'
            WHEN cs.antibiotic LIKE 'Imipenem%' THEN 'Imipenem'
            WHEN cs.antibiotic LIKE 'INH%' THEN 'INH'
            WHEN cs.antibiotic LIKE 'Meropenem%' THEN 'Meropenem'
            WHEN cs.antibiotic LIKE 'Penicillin%' OR cs.antibiotic LIKE 'PENICILLIN%' THEN 'Penicillin'
            WHEN cs.antibiotic LIKE 'Rifampin%' THEN 'Rifampin'
            WHEN cs.antibiotic LIKE 'Streptomycin%' THEN 'Streptomycin'
            WHEN cs.antibiotic LIKE '5-Flucytosine%' OR cs.antibiotic LIKE 'Flucytosine%' THEN 'Flucytosine' -- Merge "5-Flucytosine" and "Flucytosine"
            ELSE REGEXP_REPLACE(cs.antibiotic, '\\.+$', '')  -- Clean up other antibiotic names by removing trailing periods
        END AS antibiotic,
        cs.suscept as susceptibility,
        cs.specimen_source,
        cs.specimen_type
    FROM 
        `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity` cs
    WHERE
        -- Exclude non-antibiotic entries
        cs.antibiotic NOT LIKE '%InBasket%'  
        AND cs.antibiotic NOT LIKE '%Beta Lactamase%'  
        AND cs.antibiotic NOT LIKE '%BlaZ PCR%'  
        AND cs.antibiotic NOT LIKE '%Carbapenemase%'  
        AND cs.antibiotic NOT LIKE '%D-Test%'  
        AND cs.antibiotic NOT LIKE '%Esbl%'  
        AND cs.antibiotic NOT LIKE '%ermPCR%'  
        AND cs.antibiotic NOT LIKE '%Mupirocin%'  
        AND cs.antibiotic NOT LIKE '%IMP%'  
        AND cs.antibiotic NOT LIKE '%Inducible Clindamycin%'  
        AND cs.antibiotic NOT LIKE '%INTERNAL CONTROL%'  
        AND cs.antibiotic NOT LIKE '%KPC%'  
        AND cs.antibiotic NOT LIKE '%MecA PCR%'  
        AND cs.antibiotic NOT LIKE '%NDM%'  
        AND cs.antibiotic NOT LIKE '%Ox Plate Screen%'  
        AND cs.antibiotic NOT LIKE '%OXA-48-LIKE%'  
        AND cs.antibiotic NOT LIKE '%VIM%'  
        AND cs.antibiotic NOT LIKE '%Method%'  
),

-- CTE for identifying other positive cultures within a specified window
orders_with_other_pos_cultures AS (
    SELECT DISTINCT
        acwf.anon_id,
        acwf.order_proc_id_coded,
        1 AS had_other_pos_culture,
        STRING_AGG(DISTINCT cs.description, '; ') AS other_pos_site,
        STRING_AGG(DISTINCT cs.organism, '; ') AS other_organism
    FROM 
        all_cultures_with_flag acwf
    INNER JOIN 
        `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity` cs
    ON 
        acwf.anon_id = cs.anon_id AND acwf.order_proc_id_coded != cs.order_proc_id_coded
    WHERE 
        ABS(TIMESTAMP_DIFF(cs.result_time_jittered_utc, acwf.order_time_jittered_utc, HOUR)) <= 24
        AND cs.description NOT LIKE '%URINE%' 
        AND cs.description NOT LIKE '%BLOOD%' 
        AND cs.description NOT LIKE '%RESPIRATORY%'
    GROUP BY 
        acwf.anon_id, acwf.order_proc_id_coded
),


-- Final selection including prior antibiotics, detailed info for positive cultures, culture description, and other positive culture details
final_selection AS (
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
        pcd.specimen_type,
        pa.prior_antibiotics,
        COALESCE(opc.had_other_pos_culture, 0) AS had_other_pos_culture,
        opc.other_pos_site,
        opc.other_organism
    FROM 
        all_cultures_with_flag acwf
    LEFT JOIN 
        positive_culture_details pcd
    ON 
        acwf.order_proc_id_coded = pcd.order_proc_id_coded
    LEFT JOIN 
        prior_antibiotics pa
    ON 
        acwf.anon_id = pa.anon_id AND acwf.order_proc_id_coded = pa.order_proc_id_coded
    LEFT JOIN 
        orders_with_other_pos_cultures opc
    ON 
        acwf.anon_id = opc.anon_id AND acwf.order_proc_id_coded = opc.order_proc_id_coded
)

SELECT * FROM final_selection;

