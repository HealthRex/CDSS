-- TODO: Get review by Nick/Jon/project people to see if this is good or what changes I need to make!
-- e.g. do I need to add a distinct for patient_enc_csn or patient_id or something like that? if so, should it be here or downstream (probably here)

-- Pseudocode for my reference
-- SELECT all where Urine culture and antibiotic for presumptive UTI (antibiotic within same day)
-- Exclude antibiotic allergies, people with antibiotic prescription within last 30 days (before culture)
-- From above starting cohort, select 
-- (a) no growth of a predominant organism (i.e. lab results for urine culture were negative)
-- (b) organism not susceptible to the prescribed antibiotics (too narrow)
-- (c) organism is susceptible to narrower than the prescribed antibiotics (too broad)

-- Actual AIM 4 code below 
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.aim4_base_cohort` AS

-- Step 1: Extract microbiology cultures for only urine cultures with an antibiotic prescription
WITH urine_cultures AS (
    -- Do I need to make this select distinct?
    SELECT  *
    FROM 
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` mc
    WHERE
        mc.culture_description LIKE "%URINE%"
        --  AND mc.antibiotic IS NOT NULL
        -- how to handle the above? is it correct or do I need to change something
),

-- Step 2: Identify which cases need to be excluded for an antibiotic prescription within the last 30 days
-- TODO: Is this exclusion defined correctly? Even if it is, do I only need the anon_id or do I need other info?
prior_abx_prescription_exclusions AS (
    SELECT DISTINCT
        pm.anon_id
    FROM
        `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_med_augmented` pm
    WHERE
        pm.medication_time_to_cultureTime IS NOT NULL AND -30 < pm.medication_time_to_cultureTime AND pm.medication_time_to_cultureTime < 0
        -- change the above to use a greater than on the raw timestamps and then handle the positive magnitude of the 
),

-- Step 3: Identify which cases need to be excluded due to the patient having antibiotic allergies
-- TODO: See same comment as for step 2 (in this case, it only gets macrolide, sulfa, and dihydroaminopryidine as of now)
-- Consider doing based on allergen_id and/or both (i.e. not just description) if I can get access to list of appropriate IDs
antibiotic_allergy_exclusions AS (
    SELECT DISTINCT
        alrg.anon_id
    FROM
        `som-nero-phi-jonc101.shc_core_2023.allergy` alrg
    WHERE
        alrg.description LIKE '%ANTIBIOTIC%' OR alrg.description LIKE '%PENICILL%' OR alrg.description LIKE '%AMOXYCILL%'OR alrg.description LIKE '%CARBAPENEM%' OR alrg.description LIKE '%MEROPENEM%' OR alrg.description LIKE '%SULFA%' 
        OR alrg.description LIKE '%TETRACYCLINE%' OR alrg.description LIKE '%AMINOGLYCOSIDE%' OR alrg.description LIKE '%NITROFURANTOIN%' OR alrg.description LIKE '%CEPHALEXIN%' OR alrg.description LIKE '%PIPERACILL%' OR alrg.description LIKE '%TAZOBACTAM%' 
        OR alrg.description LIKE '%TRIMETHOPRIM%' OR alrg.description LIKE '%CIPROFLOXACIN%' OR alrg.description LIKE '%CEFAZOLIN%' OR alrg.description LIKE '%LEVOFLOXACIN%' OR alrg.description LIKE '%AZITHROMYCIN%' OR alrg.description LIKE '%METRONIDAZOLE%' 
        OR alrg.description LIKE '%CEFTRIAXONE%' OR alrg.description LIKE '%VANCOMYCIN%' OR alrg.description LIKE '%DOXYCYCLINE%' OR alrg.description LIKE '%CEFPODOXIME%' OR alrg.description LIKE '%RIFAXIMIN%' OR alrg.description LIKE '%CLINDAMYCIN%' 
        OR alrg.description LIKE '%MACROBID%' OR alrg.description LIKE '%GENTAMICIN%' OR alrg.description LIKE '%CEFDINIR%' OR alrg.description LIKE '%CEFOXITIN%' OR alrg.description LIKE '%CIPRO%' OR alrg.description LIKE '%MOXIFLOXACIN%' 
        OR alrg.description LIKE '%LINEZOLID%' OR alrg.description LIKE '%ZITHROMAX%' OR alrg.description LIKE '%ERYTHROMYCIN%' OR alrg.description LIKE '%BACTRIM%' OR alrg.description LIKE '%FOSFOMYCIN%' OR alrg.description LIKE '%CEFEPIME%' 
        OR alrg.description LIKE '%KEFLEX%'  OR alrg.description LIKE '%COLISTIN%' OR alrg.description LIKE '%LEVAQUIN%' OR alrg.description LIKE '%CLARITHROMYCIN%' OR alrg.description LIKE '%RIFAMPIN%' OR alrg.description LIKE '%CEFUROXIME%'
        OR alrg.description LIKE UPPER('%Augmentin%') OR alrg.description LIKE UPPER('%Cefadroxil%') OR alrg.description LIKE UPPER('%Methenamine Hippurate%') OR alrg.description LIKE UPPER('%Ertapenem%') OR alrg.description LIKE UPPER('%Linezolid In Dextrose%')
        OR alrg.description LIKE UPPER('%Ofloxacin%') OR alrg.description LIKE UPPER('%Penicillin%') OR alrg.description LIKE UPPER('%Silver Sulfadiazine%') OR alrg.description LIKE UPPER('%Dapsone%') OR alrg.description LIKE UPPER('%Ciprofloxacin-Dexamethasone%')
        OR alrg.description LIKE UPPER('%Ampicillin Sodium%') OR alrg.description LIKE UPPER('%Isoniazid%') OR alrg.description LIKE UPPER('%Bactrim%') OR alrg.description LIKE UPPER('%Fidaxomicin%') OR alrg.description LIKE UPPER('%Aztreonam In%')
        OR alrg.description LIKE UPPER('%Ethambutol%') OR alrg.description LIKE UPPER('%Tobramycin Sulfate%') OR alrg.description LIKE UPPER('%Cefepime In%') OR alrg.description LIKE UPPER('%Ampicillin%') OR alrg.description LIKE UPPER('%Minocycline%')
        OR alrg.description LIKE UPPER('%Ceftazidime-Dextrose%') OR alrg.description LIKE UPPER('%Aztreonam%') OR alrg.description LIKE UPPER('%Xifaxan%') OR alrg.description LIKE UPPER('%Erythromycin Ethylsuccinate%') OR alrg.description LIKE UPPER('%Gentamicin In Nacl%')
        OR alrg.description LIKE UPPER('%Meropenem%') OR alrg.description LIKE UPPER('%Gatifloxacin%') OR alrg.description LIKE UPPER('%Flagyl%') OR alrg.description LIKE UPPER('%Macrodantin%') OR alrg.description LIKE UPPER('%Amikacin%')
        OR alrg.description LIKE UPPER('%Trimethoprim%') OR alrg.description LIKE UPPER('%Tobramycin-Dexamethasone%') OR alrg.description LIKE UPPER('%Dicloxacillin%') OR alrg.description LIKE UPPER('%Moxifloxacin-Sod.Chloride(Iso)%')
        OR alrg.description LIKE UPPER('%Hiprex%') OR alrg.description LIKE UPPER('%Ceftazidime%') OR alrg.description LIKE UPPER('%Zyvox%') OR alrg.description LIKE UPPER('%Methenamine Mandelate%') OR alrg.description LIKE UPPER('%Rifabutin%') 
        OR alrg.description LIKE UPPER('%Tedizolid%')
    ),

-- Step 4: Extract which cases have the antibiotic prescription within same day as urine culture
-- TODO: Can I do this based on microbiology_cultures_prior_med_augmented? Or do I need to build it from scratch
-- using very similar code except for the med being after not before?
same_day_prescription_inclusions AS (
    SELECT DISTINCT
        om.anon_id,
        om.medication_id,
        om.med_description
    FROM
        `som-nero-phi-jonc101.shc_core_2023.order_med` om
    INNER JOIN
        urine_cultures uc
    ON
        om.anon_id = uc.anon_id
    WHERE
         om.ordering_date_jittered_utc > uc.order_time_jittered_utc
         AND TIMESTAMP_DIFF(om.ordering_date_jittered_utc, uc.order_time_jittered_utc, DAY) = 0
        --  Should this ^ be = 0 or <= 1
        AND om.med_description LIKE '%ANTIBIOTIC%' OR om.med_description LIKE '%PENICILL%' OR om.med_description LIKE '%AMOXYCILL%'OR om.med_description LIKE '%CARBAPENEM%' OR om.med_description LIKE '%MEROPENEM%' OR om.med_description LIKE '%SULFA%' OR om.med_description LIKE '%TETRACYCLINE%' OR om.med_description LIKE '%AMINOGLYCOSIDE%'
)

-- Step 5: Finalize the base cohort table using the above inclusions and exclusions
-- Below is currently a placeholder. TODO: Actually finalize the above intermediates and use that to finalize the below query
SELECT uc.*, sdpi.medication_id, sdpi.med_description
FROM urine_cultures uc
INNER JOIN same_day_prescription_inclusions sdpi
ON uc.anon_id = sdpi.anon_id
where uc.anon_id NOT IN (SELECT * FROM prior_abx_prescription_exclusions) 
AND uc.anon_id NOT IN (SELECT * FROM antibiotic_allergy_exclusions);