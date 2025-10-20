##############################################################################################################################################################
# Goal:Creating the microbiology_cultures_medication_exposure Table. This table indicates of a patient having been treated with a specific antibiotic before specimen collection.
##############################################################################################################################################################

##########################################################################################
# 1. Extract prior antibiotic exposures with exact day difference to culture order
##########################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_extracted` AS
WITH microbiology_cultures AS (
    SELECT DISTINCT
        anon_id,
        pat_enc_csn_id_coded,
        order_proc_id_coded,
        order_time_jittered_utc
    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort`
),

cleaned_medications AS (
    SELECT 
        mc.anon_id,
        mc.pat_enc_csn_id_coded,
        mc.order_proc_id_coded,
        mc.order_time_jittered_utc,
        mo.ordering_date_jittered_utc,

        -- Clean medication name
        INITCAP(TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    LOWER(mm.name),
                    'penicillin[^a-z].*$', 'penicillin'
                ),
                '^[^a-z]*|\\s+\\S*[^a-z\\s]+.*$|\\.+$', ''
            )
        )) AS medication_name,

        -- Actual difference in days between med order and culture
        TIMESTAMP_DIFF(mc.order_time_jittered_utc, mo.ordering_date_jittered_utc, DAY) AS medication_time_to_culturetime

    FROM 
        microbiology_cultures mc
    LEFT JOIN 
        `som-nero-phi-jonc101.shc_core_2023.order_med` mo
    ON 
        mc.anon_id = mo.anon_id
    LEFT JOIN 
        `som-nero-phi-jonc101.shc_core_2023.mapped_meds` mm
    ON 
        mo.med_description = mm.name
)

SELECT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    order_time_jittered_utc,
    medication_name,
    medication_time_to_culturetime
FROM 
    cleaned_medications
WHERE 
    medication_time_to_culturetime >= 0;  -- optional: keep only prior or same-day exposures


##########################################################################################
# 2. Filter only antibiotics from the temp_antibiotics list (89 antibiotics) 
#    and add short category codes
##########################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_medication_exposure` AS
WITH antibiotic_list AS (
    SELECT DISTINCT LOWER(antibiotic_name) AS antibiotic_name
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.temp_antibiotics`
),

valid_antibiotics AS (
    SELECT 
        pae.anon_id,
        pae.pat_enc_csn_id_coded,
        pae.order_proc_id_coded,
        pae.order_time_jittered_utc,
        pae.medication_name,
        pae.medication_time_to_culturetime,
        
        -- Map each medication to its short category name
        CASE 
            WHEN medication_name = 'Nitrofurantoin' THEN 'NIT'
            WHEN medication_name = 'Cephalexin' THEN 'CEP'
            WHEN medication_name = 'Piperacillin-Tazobactam-Dextrs' THEN 'PIP'
            WHEN medication_name = 'Sulfamethoxazole-Trimethoprim' THEN 'SUL'
            WHEN medication_name = 'Ciprofloxacin Hcl' THEN 'CIP'
            WHEN medication_name = 'Cefazolin' THEN 'CEF'
            WHEN medication_name = 'Cefazolin In Dextrose' THEN 'CEF1'
            WHEN medication_name = 'Levofloxacin' THEN 'LEV'
            WHEN medication_name = 'Azithromycin' THEN 'AZI'
            WHEN medication_name = 'Amoxicillin-Pot Clavulanate' THEN 'AMO'
            WHEN medication_name = 'Metronidazole In Nacl' THEN 'MET'
            WHEN medication_name = 'Ceftriaxone' THEN 'CEF2'
            WHEN medication_name = 'Vancomycin' THEN 'VAN'
            WHEN medication_name = 'Levofloxacin In' THEN 'LEV1'
            WHEN medication_name = 'Vancomycin In Dextrose' THEN 'VAN1'
            WHEN medication_name = 'Metronidazole' THEN 'MET1'
            WHEN medication_name = 'Ciprofloxacin In' THEN 'CIP1'
            WHEN medication_name = 'Doxycycline Hyclate' THEN 'DOX'
            WHEN medication_name = 'Cefpodoxime' THEN 'CEF3'
            WHEN medication_name = 'Piperacillin-Tazobactam' THEN 'PIP1'
            WHEN medication_name = 'Rifaximin' THEN 'RIF'
            WHEN medication_name = 'Vancomycin-Diluent Combo' THEN 'VAN2'
            WHEN medication_name = 'Clindamycin In' THEN 'CLI'
            WHEN medication_name = 'Amoxicillin' THEN 'AMO1'
            WHEN medication_name = 'Nitrofurantoin Macrocrystal' THEN 'NIT1'
            WHEN medication_name = 'Macrobid' THEN 'MAC'
            WHEN medication_name = 'Gentamicin-Sodium Citrate' THEN 'GEN'
            WHEN medication_name = 'Cefdinir' THEN 'CEF4'
            WHEN medication_name = 'Clindamycin Phosphate' THEN 'CLI1'
            WHEN medication_name = 'Cefoxitin' THEN 'CEF5'
            WHEN medication_name = 'Cipro' THEN 'CIP2'
            WHEN medication_name = 'Clindamycin Hcl' THEN 'CLI2'
            WHEN medication_name = 'Vancomycin In' THEN 'VAN3'
            WHEN medication_name = 'Moxifloxacin' THEN 'MOX'
            WHEN medication_name = 'Gentamicin' THEN 'GEN1'
            WHEN medication_name = 'Linezolid' THEN 'LIN'
            WHEN medication_name = 'Zithromax' THEN 'ZIT'
            WHEN medication_name = 'Erythromycin' THEN 'ERY'
            WHEN medication_name = 'Bactrim Ds' THEN 'BAC'
            WHEN medication_name = 'Fosfomycin Tromethamine' THEN 'FOS'
            WHEN medication_name = 'Cefepime' THEN 'CEF6'
            WHEN medication_name = 'Keflex' THEN 'KEF'
            WHEN medication_name = 'Colistin' THEN 'COL'
            WHEN medication_name = 'Doxycycline Monohydrate' THEN 'DOX1'
            WHEN medication_name = 'Levaquin' THEN 'LEV2'
            WHEN medication_name = 'Clarithromycin' THEN 'CLA'
            WHEN medication_name = 'Rifampin' THEN 'RIF1'
            WHEN medication_name = 'Ciprofloxacin' THEN 'CIP3'
            WHEN medication_name = 'Cefuroxime Axetil' THEN 'CEF7'
            WHEN medication_name = 'Augmentin' THEN 'AUG'
            WHEN medication_name = 'Cefadroxil' THEN 'CEF8'
            WHEN medication_name = 'Methenamine Hippurate' THEN 'MET2'
            WHEN medication_name = 'Ertapenem' THEN 'ERT'
            WHEN medication_name = 'Linezolid In Dextrose' THEN 'LIN1'
            WHEN medication_name = 'Ofloxacin' THEN 'OFL'
            WHEN medication_name = 'Penicillin' THEN 'PEN'
            WHEN medication_name = 'Silver Sulfadiazine' THEN 'SIL'
            WHEN medication_name = 'Dapsone' THEN 'DAP'
            WHEN medication_name = 'Ciprofloxacin-Dexamethasone' THEN 'CIP4'
            WHEN medication_name = 'Ampicillin Sodium' THEN 'AMP'
            WHEN medication_name = 'Isoniazid' THEN 'ISO'
            WHEN medication_name = 'Bactrim' THEN 'BAC1'
            WHEN medication_name = 'Fidaxomicin' THEN 'FID'
            WHEN medication_name = 'Aztreonam In' THEN 'AZT'
            WHEN medication_name = 'Ethambutol' THEN 'ETH'
            WHEN medication_name = 'Tobramycin Sulfate' THEN 'TOB'
            WHEN medication_name = 'Cefepime In' THEN 'CEF9'
            WHEN medication_name = 'Ampicillin' THEN 'AMP1'
            WHEN medication_name = 'Minocycline' THEN 'MIN'
            WHEN medication_name = 'Ceftazidime-Dextrose' THEN 'CEF10'
            WHEN medication_name = 'Aztreonam' THEN 'AZT1'
            WHEN medication_name = 'Xifaxan' THEN 'XIF'
            WHEN medication_name = 'Erythromycin Ethylsuccinate' THEN 'ERY1'
            WHEN medication_name = 'Gentamicin In Nacl' THEN 'GEN2'
            WHEN medication_name = 'Meropenem' THEN 'MER'
            WHEN medication_name = 'Gatifloxacin' THEN 'GAT'
            WHEN medication_name = 'Flagyl' THEN 'FLA'
            WHEN medication_name = 'Macrodantin' THEN 'MAC1'
            WHEN medication_name = 'Amikacin' THEN 'AMI'
            WHEN medication_name = 'Trimethoprim' THEN 'TRI'
            WHEN medication_name = 'Tobramycin-Dexamethasone' THEN 'TOB1'
            WHEN medication_name = 'Dicloxacillin' THEN 'DIC'
            WHEN medication_name = 'Moxifloxacin-Sod.Chloride(Iso)' THEN 'MOX1'
            WHEN medication_name = 'Hiprex' THEN 'HIP'
            WHEN medication_name = 'Ceftazidime' THEN 'CEF11'
            WHEN medication_name = 'Zyvox' THEN 'ZYV'
            WHEN medication_name = 'Methenamine Mandelate' THEN 'MET3'
            WHEN medication_name = 'Rifabutin' THEN 'RIF2'
            WHEN medication_name = 'Tedizolid' THEN 'TED'
        END AS medication_category

    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_extracted` pae
    INNER JOIN 
        antibiotic_list al
    ON 
        LOWER(pae.medication_name) = al.antibiotic_name
)

SELECT *
FROM valid_antibiotics
ORDER BY anon_id, order_proc_id_coded, medication_time_to_culturetime;
