##############################################################################################################################################################
# Goal: Create microbiology_cultures_medication_exposure_peds
# This table identifies if a pediatric patient had been treated with a specific antibiotic before specimen collection,
# and assigns each medication a short category code.
##############################################################################################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_medication_exposure_peds` AS (

-- Step 1: Base microbiology cohort
WITH base_cohort AS (
    SELECT DISTINCT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort_peds`
),

-- Step 2: Merge LPCH meds with mapped names and clean text
cleaned_medications AS (
    SELECT 
        c.anon_id,
        c.pat_enc_csn_id_coded,
        c.order_proc_id_coded,
        c.order_time_jittered_utc,
        mo.ordering_date_jittered_utc AS medication_time,

        -- Clean medication name (fallback: mapped name or raw med_description)
        INITCAP(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    TRIM(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    LOWER(COALESCE(mm.name, mo.med_description)),  -- fallback to mapped name
                                    '\\s*\\d+(\\.\\d+)?\\s*(mg|mcg|gram|ml|%)', ''  -- remove dosage
                                ),
                                '\\(.*?\\)', ''  -- remove parentheses
                            ),
                            ' in.*$|tablet|capsule|intravenous|piggyback|' ||
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
                        )
                    ),
                    '\\d|\\sfor\\s*|\\ser\\s*|\\shr\\s*|/ml\\s*|' ||
                    '\\sml\\s*|\\sv\\s*|\\sg\\s*|\\sim\\s*', ''
                ),
                '\\s|\\/|\\.|-$', ''
            )
        ) AS medication_name,

        -- Time difference between med order and culture
        TIMESTAMP_DIFF(c.order_time_jittered_utc, mo.ordering_date_jittered_utc, DAY) AS medication_time_to_cultureTime       

    FROM 
        base_cohort c
    LEFT JOIN 
        `som-nero-phi-jonc101.lpch_core_2024.lpch_order_med` mo
        USING (anon_id)
    LEFT JOIN 
        `som-nero-phi-jonc101.shc_core_2024.mapped_meds` mm
        ON mo.medication_id = mm.medication_id
),

-- Step 3: Identify valid antibiotics from the master list
valid_antibiotics AS (
    SELECT DISTINCT
        cm.anon_id,
        cm.pat_enc_csn_id_coded,
        cm.order_proc_id_coded,
        cm.order_time_jittered_utc,
        cm.medication_time,
        cm.medication_time_to_cultureTime,
        cm.medication_name,
        ta.antibiotic_name AS matched_antibiotic
    FROM cleaned_medications cm
    INNER JOIN `som-nero-phi-jonc101.antimicrobial_stewardship.temp_antibiotics` ta
        ON LOWER(cm.medication_name) LIKE LOWER(CONCAT('%', ta.antibiotic_name, '%'))
)

-- Step 4: Final selection and classification
SELECT DISTINCT
    c.anon_id,
    c.pat_enc_csn_id_coded,
    c.order_proc_id_coded,
    c.order_time_jittered_utc,
    v.matched_antibiotic AS medication_name,
    v.medication_time,
    v.medication_time_to_cultureTime,

    -- Assign short medication category codes
CASE
    WHEN LOWER(v.matched_antibiotic) = 'minocycline' THEN 'MIN'
    WHEN LOWER(v.matched_antibiotic) = 'cefazolin' THEN 'CEF'
    WHEN LOWER(v.matched_antibiotic) = 'vancomycin' THEN 'VAN'
    WHEN LOWER(v.matched_antibiotic) = 'piperacillin-tazobactam' THEN 'PIP1'
    WHEN LOWER(v.matched_antibiotic) = 'trimethoprim' THEN 'TRI'
    WHEN LOWER(v.matched_antibiotic) = 'sulfamethoxazole-trimethoprim' THEN 'SUL'
    WHEN LOWER(v.matched_antibiotic) = 'cephalexin' THEN 'CEP'
    WHEN LOWER(v.matched_antibiotic) = 'nitrofurantoin' THEN 'NIT1'
    WHEN LOWER(v.matched_antibiotic) = 'amoxicillin' THEN 'AMO1'
    WHEN LOWER(v.matched_antibiotic) = 'metronidazole' THEN 'MET1'
    WHEN LOWER(v.matched_antibiotic) = 'ofloxacin' THEN 'OFL'
    WHEN LOWER(v.matched_antibiotic) = 'cipro' THEN 'CIP2'
    WHEN LOWER(v.matched_antibiotic) = 'ciprofloxacin' THEN 'CIP3'
    WHEN LOWER(v.matched_antibiotic) = 'ciprofloxacin-dexamethasone' THEN 'CIP4'
    WHEN LOWER(v.matched_antibiotic) = 'cefoxitin' THEN 'CEF5'
    WHEN LOWER(v.matched_antibiotic) = 'cefdinir' THEN 'CEF4'
    WHEN LOWER(v.matched_antibiotic) = 'azithromycin' THEN 'AZI'
    WHEN LOWER(v.matched_antibiotic) = 'ceftriaxone' THEN 'CEF2'
    WHEN LOWER(v.matched_antibiotic) = 'levofloxacin' THEN 'LEV'
    WHEN LOWER(v.matched_antibiotic) = 'meropenem' THEN 'MER'
    WHEN LOWER(v.matched_antibiotic) = 'macrodantin' THEN 'MAC1'
    WHEN LOWER(v.matched_antibiotic) = 'ampicillin' THEN 'AMP1'
    WHEN LOWER(v.matched_antibiotic) = 'gentamicin' THEN 'GEN1'
    WHEN LOWER(v.matched_antibiotic) = 'cefepime' THEN 'CEF6'
    WHEN LOWER(v.matched_antibiotic) = 'erythromycin' THEN 'ERY'
    WHEN LOWER(v.matched_antibiotic) = 'ceftazidime' THEN 'CEF11'
    WHEN LOWER(v.matched_antibiotic) = 'linezolid' THEN 'LIN'
    WHEN LOWER(v.matched_antibiotic) = 'keflex' THEN 'KEF'
    WHEN LOWER(v.matched_antibiotic) = 'bactrim' THEN 'BAC1'
    WHEN LOWER(v.matched_antibiotic) = 'tobramycin-dexamethasone' THEN 'TOB1'
    WHEN LOWER(v.matched_antibiotic) = 'amikacin' THEN 'AMI'
    WHEN LOWER(v.matched_antibiotic) = 'augmentin' THEN 'AUG'
    WHEN LOWER(v.matched_antibiotic) = 'isoniazid' THEN 'ISO'
    WHEN LOWER(v.matched_antibiotic) = 'penicillin' THEN 'PEN'
    WHEN LOWER(v.matched_antibiotic) = 'rifaximin' THEN 'RIF'
    WHEN LOWER(v.matched_antibiotic) = 'colistin' THEN 'COL'
    WHEN LOWER(v.matched_antibiotic) = 'rifampin' THEN 'RIF1'
    WHEN LOWER(v.matched_antibiotic) = 'clarithromycin' THEN 'CLA'
    WHEN LOWER(v.matched_antibiotic) = 'moxifloxacin' THEN 'MOX'
    WHEN LOWER(v.matched_antibiotic) = 'aztreonam' THEN 'AZT1'
    WHEN LOWER(v.matched_antibiotic) = 'xifaxan' THEN 'XIF'
    WHEN LOWER(v.matched_antibiotic) = 'dapsone' THEN 'DAP'
    WHEN LOWER(v.matched_antibiotic) = 'ethambutol' THEN 'ETH'
    WHEN LOWER(v.matched_antibiotic) = 'zithromax' THEN 'ZIT'
    WHEN LOWER(v.matched_antibiotic) = 'ertapenem' THEN 'ERT'
    WHEN LOWER(v.matched_antibiotic) = 'cefadroxil' THEN 'CEF8'
    WHEN LOWER(v.matched_antibiotic) = 'fidaxomicin' THEN 'FID'
    WHEN LOWER(v.matched_antibiotic) = 'dicloxacillin' THEN 'DIC'
    WHEN LOWER(v.matched_antibiotic) = 'cefpodoxime' THEN 'CEF3'
    WHEN LOWER(v.matched_antibiotic) = 'gatifloxacin' THEN 'GAT'
    WHEN LOWER(v.matched_antibiotic) = 'rifabutin' THEN 'RIF2'
    WHEN LOWER(v.matched_antibiotic) = 'zyvox' THEN 'ZYV'
    WHEN LOWER(v.matched_antibiotic) = 'flagyl' THEN 'FLA'
    WHEN LOWER(v.matched_antibiotic) = 'levaquin' THEN 'LEV2'
    WHEN LOWER(v.matched_antibiotic) = 'tedizolid' THEN 'TED'
    ELSE NULL
END AS medication_category



FROM 
    base_cohort c
LEFT JOIN 
    valid_antibiotics v
    USING (anon_id, pat_enc_csn_id_coded, order_proc_id_coded, order_time_jittered_utc)
WHERE 
    v.medication_time_to_cultureTime >= 1  -- antibiotic before culture
ORDER BY 
    anon_id, pat_enc_csn_id_coded, order_proc_id_coded, medication_time_to_cultureTime
);
