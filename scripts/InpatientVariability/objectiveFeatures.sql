

/*
selectDRGs AS
(
    SELECT *
    #SELECT anon_id, enc, admsnTimeJTR
    FROM `som-nero-phi-jonc101-secure.kush_db.selectDRGs` # selectDRGs_sepsis
), */

-- From: Charlson, Apache, SOFA, etc.
features AS
(
    SELECT NULL
-- comorbidities / AHRQ CCSR
    -- MI: History of definite or probable MI (EKG changes and/or enzyme changes)
    -- CHF: DOE or PND that has responded to digitalis, diuretics, or afterload reducing agents
    -- PVD: Intermittent claudication or past bypass for chronic arterial insufficiency, history of gangrene or acute arterial insufficiency, or untreated thoracic or abdominal aneurysm (≥6 cm)
    -- TIA / CVD: History of a cerebrovascular accident with minor or no residua and transient ischemic attacks
    -- Dementia: Chronic cognitive deficit
    -- COPD
    -- Connective Tissue Disease
    -- PUD: Any history of treatment for ulcer disease or history of ulcer bleeding
    -- Liver Dz: Mild = chronic hepatitis (or cirrhosis without portal hypertension). Severe = cirrhosis and portal hypertension with variceal bleeding history, moderate = cirrhosis and portal hypertension but no variceal bleeding history
    -- Uncomplicated Diabetes
    -- Hemiplegia
    -- CKD: Severe = on dialysis, status post kidney transplant, uremia, moderate = creatinine >3 mg/dL (0.27 mmol/L)
    -- Localized Solid Tumor
    -- Metastatic Solid Tumor
    -- Leukemia
    -- Lymphoma
    -- AIDS
    -- ? Chronic renal failure?
    -- ? H/o severe organ insufficiency?
    -- ? Immunocompromised?

-- labs
    -- Platelets: >150, 100-149, 50-99, 20-49, <20
    -- PaO2 / FiO2: >=400, 300-399, 200-299, 100-199, <100
    -- Cr: <1.2, 1.2-1.9, 2.0-3.4, 3.5-4.9, >5.0
    -- Hct: cutoffs: >60, 50, 46, 30, 20, <20
    -- WBC: cutoffs: >40, 20, 15, 3, 1, <1
    -- PaO2: cutoffs: >70, 60, 55, <55
    -- Arterial pH: cutoffs: >7.7, 7.6, 7.5, 7.33, 7.25, 7.15, <7.15
    -- Sodium: cutoffs: >180, 160, 155, 150, 130, 120, 111, <111
    -- Potassium: cutoffs: >7, 6, 5.5, 3.5, 3, 2.5, <2.5
    -- Cr: cutoffs: >3.5, 2, 1.5, 0.6, <0.6
    -- Bilirubin: mg/dL: <1.2, 1.2-1.9, 2.0-5.9, 6.0-11.9, >12.0 (umol/L: <20, 20-32, 33-101, 102-204, >204)
    -- BUN: cutoffs: >84, <28
    -- Bicarbonate: cutoffs: <15, >20
    -- Acute renal failure?

-- vitals
    -- FiO2
    -- SpO2: >96, 94-95, 92-93, 88-92, 86-87, 84-85, <83
    -- Temperature: >41, 39-41, 38.5-39, 36-38.5, 34-36, 32-34, 30-32, <30
    -- MAP: cutoffs: >159, 129, 109, 69, 49, <49
    -- HR: cutoffs: >180, 140, 110, 70, 55, 40, <40

-- other
    -- Age: <44, 45-54, 55-64, 65-74, >74
    -- Urine Output 24H: cutoffs: <500, >1000


-- TO DO:
    -- Dopamine <5, >5
    -- Dobutamine (y/n)
    -- Epinephrine <0.1, >0.1
    -- Norepinephrne <0.1, >0.1
    -- Type of O2 Delivery: NC, simple face mask, non-rebreather, HFNC
    -- On mechanical ventilation
    -- On room air or supplemental?
    -- RR: cutoffs: >50, 35, 25, 12, 10, 6, <6
    -- Recent surgery
    -- Type of Admission: scheduled surgical, medical, unscheduled surgical
    -- GCS: (glasgow) 15, 13-14, 10-12, 6-9, <6
    -- Confusion?


),

-- Charlson Comorbidity Index (CCI): predicts 10y survival
charlson AS
(
    SELECT NULL
    -- MI: History of definite or probable MI (EKG changes and/or enzyme changes)
    -- CHF: DOE or PND that has responded to digitalis, diuretics, or afterload reducing agents
    -- PVD: Intermittent claudication or past bypass for chronic arterial insufficiency, history of gangrene or acute arterial insufficiency, or untreated thoracic or abdominal aneurysm (≥6 cm)
    -- TIA / CVD: History of a cerebrovascular accident with minor or no residua and transient ischemic attacks
    -- Dementia: Chronic cognitive deficit
    -- COPD
    -- Connective Tissue Disease
    -- PUD: Any history of treatment for ulcer disease or history of ulcer bleeding
    -- Liver Dz: Mild = chronic hepatitis (or cirrhosis without portal hypertension). Severe = cirrhosis and portal hypertension with variceal bleeding history, moderate = cirrhosis and portal hypertension but no variceal bleeding history
    -- Uncomplicated Diabetes
    -- Hemiplegia
    -- CKD: Severe = on dialysis, status post kidney transplant, uremia, moderate = creatinine >3 mg/dL (0.27 mmol/L)
    -- Localized Solid Tumor
    -- Metastatic Solid Tumor
    -- Leukemia
    -- Lymphoma
    -- AIDS
),


-- Sequential Organ Failure Assessment (SOFA) Score: predicts ICU mortality
sofa AS
(
    SELECT NULL
    -- PaO2 / FiO2: >=400, 300-399, 200-299, 100-199, <100
    -- On mechanical ventilation
    -- Platelets: >150, 100-149, 50-99, 20-49, <20
    -- GCS: (glasgow) 15, 13-14, 10-12, 6-9, <6
    -- Bilirubin: mg/dL: <1.2, 1.2-1.9, 2.0-5.9, 6.0-11.9, >12.0 (umol/L: <20, 20-32, 33-101, 102-204, >204)
    -- MAP: <70, >70
    -- Dopamine <5, >5
    -- Dobutamine (y/n)
    -- Epinephrine <0.1, >0.1
    -- Norepinephrne <0.1, >0.1
    -- Cr: <1.2, 1.2-1.9, 2.0-3.4, 3.5-4.9, >5.0
    -- Type of O2 Delivery: NC, simple face mask, non-rebreather, HFNC
),

-- APACHE2 (acute physiology and chronic health evaluation): predicts ICU mortality
apache2 AS
(
    SELECT NULL
    -- Age: <44, 45-54, 55-64, 65-74, >74
    -- H/o severe organ insufficiency
    -- Immunocompromised?
    -- Recent surgery
    -- Temperature: >41, 39-41, 38.5-39, 36-38.5, 34-36, 32-34, 30-32, <30
    -- MAP: cutoffs: >159, 129, 109, 69, 49, <49
    -- HR: cutoffs: >180, 140, 110, 70, 55, 40, <40
    -- RR: cutoffs: >50, 35, 25, 12, 10, 6, <6
    -- PaO2: cutoffs: >70, 60, 55, <55
    -- Arterial pH: cutoffs: >7.7, 7.6, 7.5, 7.33, 7.25, 7.15, <7.15
    -- Sodium: cutoffs: >180, 160, 155, 150, 130, 120, 111, <111
    -- Potassium: cutoffs: >7, 6, 5.5, 3.5, 3, 2.5, <2.5
    -- Cr: cutoffs: >3.5, 2, 1.5, 0.6, <0.6
    -- Acute renal failure?
    -- Chronic renal failure?
    -- Hct: cutoffs: >60, 50, 46, 30, 20, <20
    -- WBC: cutoffs: >40, 20, 15, 3, 1, <1
),

-- NEWS2 (National Early Warning Score), SAPS (Simplified Acute Physiology Score)
other AS
(
    SELECT NULL
    -- SpO2: >96, 94-95, 92-93, 88-92, 86-87, 84-85, <83
    -- On room air or supplemental?
    -- Confusion?
    -- BUN: cutoffs: >84, <28
    -- Urine Output 24H: cutoffs: <500, >1000
    -- Bicarbonate: cutoffs: <15, >20
    -- Type of Admission: scheduled surgical, medical, unscheduled surgical
),

-- patient age, comorbidities, demographic
patientFactors AS
(
    SELECT enc, admsnTimeJTR, GENDER, CANONICAL_ETHNICITY, CANONICAL_RACE, INTRPTR_NEEDED_YN, INSURANCE_PAYOR_NAME, BMI, # CHARLSON_SCORE, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL,
            case when DATETIME_DIFF(admsnTimeJTR, BIRTH_DATE_JITTERED, YEAR) >= 75 then ">=75"
                when DATETIME_DIFF(admsnTimeJTR, BIRTH_DATE_JITTERED, YEAR) between 65 and 75 then "65-75"
                when DATETIME_DIFF(admsnTimeJTR, BIRTH_DATE_JITTERED, YEAR) between 55 and 65 then "55-65"
                when DATETIME_DIFF(admsnTimeJTR, BIRTH_DATE_JITTERED, YEAR) between 45 and 55 then "45-55"
                when DATETIME_DIFF(admsnTimeJTR, BIRTH_DATE_JITTERED, YEAR) < 45 then "<45"
                else null
                end as age
    FROM selectDRGs a
    JOIN `mining-clinical-decisions.shc_core.demographic`
    -- should LEFT JOIN, but this loses some data (current use case: 4 out of 521 rows), don't want to deal with missing data imputation right now
    USING(anon_id)
),

-- Gather select labs that were collected within the first 24 hours of admission
-- Glucose, AST/ALT, PaO2/FiO2, Plt, Bili, Cr, pHA, Na, K, Hct, WBC, BUN, HCO3, + vitals (SpO2, HR, RR, MAP, temp)
-- UNITS?! GLUCOSE (base_name = "GLU") AST/ALT (base_name IN "AST","ALT"), PaO2/FiO2 (base_name IN "FIO2", "PO2A")
labs_all AS
(
    SELECT  enc, admsnTimeJTR, result_time,
            DATETIME_DIFF(result_time, admsnTimeJTR, HOUR) as hrsAfterAdmit,
            lab_name, base_name, ord_num_value, result_flag, -- component_id, order_type, proc_code
            -- reference_unit # reference units for most are either mg/dL (standardized) or, when they vary, mEq/L vs. mmol/L (which are both on same scale, a.k.a. interchangeable)
            #COUNT(result_time) OVER (PARTITION BY enc, base_name ORDER BY result_time DESC) AS latest, -- filter by "latest=1" to take the latest value for any given lab in 24h period
            case when base_name = "CR" then ord_num_value else null end as cr, -- creatinine
            case when base_name IN ("LAC","LACWBL") then ord_num_value else null end as lactate, -- lactate
            case when base_name = "PO2V" then ord_num_value else null end as pO2v, -- pO2 (venous); arterial = PO2A
            case when base_name = "PCO2V" then ord_num_value else null end as pCO2v, -- pCO2 (venous); arterial = PCO2A
            case when base_name = "O2SATV" then ord_num_value else null end as spO2v, -- O2 saturation (venous); arterial = O2SATA
            case when base_name = "PHV" then ord_num_value else null end as pHv, -- pH (venous); arterial = PHA
            case when base_name = "HCO3V" then ord_num_value else null end as hco3v, -- HCO3 (venous); arterial = HCO3A
            case when base_name = "BUN" then ord_num_value else null end as bun, -- BUN
            case when base_name = "TNI" then ord_num_value else null end as trop, -- troponin
            case when base_name = "TBIL" then ord_num_value else null end as tbili, -- total bilirubin ("DBIL" = direct bili; "IBIL" = indirect bili)
            case when base_name = "PLT" then ord_num_value else null end as plt, -- platelets
            case when base_name = "NA" then ord_num_value else null end as na, -- sodium
            case when base_name = "K" then ord_num_value else null end as k, -- potassium
            case when base_name = "WBC" AND reference_unit = "/uL" then ord_num_value/1000
                 when base_name = "WBC" then ord_num_value else null end as wbc, -- WBC count
            #case when base_name = "XUWBC" then ord_num_value else null end as u_wbc, -- urine WBC
            case when base_name = "HCT" then ord_num_value else null end as hct -- hematocrit

    FROM selectDRGs a

    LEFT JOIN `mining-clinical-decisions.shc_core.lab_result` b
        ON a.enc = b.pat_enc_csn_id_coded
        AND DATETIME_DIFF(result_time, admsnTimeJTR, HOUR) <= 24
        AND base_name IN ("CR", "LAC", "LACWBL", "PO2V", "PCO2V", "O2SATV", "PHV", "HCO3V", "BUN", "TNI", "TBIL", "PLT", "NA", "K", "WBC", "XUWBC", "HCT")
        AND ord_num_value != 9999999 -- discard junk values

    ORDER BY enc, hrsAfterAdmit DESC
    #ORDER BY latest DESC

    #missing data imputation -> avoid for now
    #use result_flag (lump HIGH + HIGH PANIC, and LOW + LOW PANIC)
),

-- Unclear how to process instances where multiple timepoints within 24h range are outside reference.... what if taking the most recent timepoint is wrong (ie. transfusions to correct for low HCT)
-- ex: SELECT * FROM labs_all WHERE enc=131275787339 ORDER BY base_name, hrsAfterAdmit DESC -- this query shows instance with MULTIPLE labs (ie. HCT) drawn for same pt in given 24h period
labs_processed AS
(
    SELECT enc, max(cr) as cr, max(lactate) as lactate, min(pO2v) as pO2v, max(pCO2v) as pCO2v, min(spO2v) as spO2v,
            max(bun) as bun, max(tbili) as tbili, max(trop) as trop, min(hct) as hct,
            max(wbc) as wbc, min(na) as na, min(k) as k, min(plt) as plt, min(hco3v) as hco3v, min(pHv) as pHv -- this row of features could have MIN + MAX per feature (as WBC, for instance, that's too low is just as bad as too high. unclear what to do.
            -- min(wbc) as wbc, max(na) as na, max(k) as k, max(plt) as plt, max(hco3v) as hco3v, max(pHv) as pHv -- what if both min(wbc) and max(wbc) are outside range (ie. WBC 3, 17) --> take the latest value
    FROM labs_all
    GROUP BY enc
),

labs_5buckets AS
(
    SELECT
        enc,
        case when cr >= 5.0 then ">=5.0"
            when cr between 3.5 and 5.0 then "3.5-5.0"
            when cr between 2.0 and 3.5 then "2.0-3.5"
            when cr between 1.5 and 2.0 then "1.5-2.0"
            when cr between 0.6 and 1.5 then "0.6-1.5"
            when cr < 0.6 then "<0.6"
            else "unmeasured"
            end as cr,
        case when lactate >= 3.5 then ">=3.5"
            when lactate between 2.5 and 3.5 then "2.5-3.5"
            when lactate between 1.5 and 2.5 then "1.5-2.5"
            when lactate between 1.0 and 1.5 then "1.0-1.5"
            when lactate < 1.0 then "<1.0"
            else "unmeasured"
            end as lactate,
        case when pO2v >= 45 then ">=45"
            when pO2v between 35 and 45 then "35-45"
            when pO2v between 25 and 35 then "25-35"
            when pO2v < 25 then "<25"
            else "unmeasured"
            end as pO2v,
        case when pCO2v >= 60 then ">=60"
            when pCO2v between 50 and 60 then "50-60"
            when pCO2v between 40 and 50 then "40-50"
            when pCO2v between 30 and 40 then "30-40"
            when pCO2v < 30 then "<30"
            else "unmeasured"
            end as pCO2v,
        case when spO2v >= 85 then ">=85"
            when spO2v between 75 and 85 then "75-85"
            when spO2v between 65 and 75 then "65-75"
            when spO2v between 55 and 65 then "55-65"
            when spO2v < 55 then "<55"
            else "unmeasured"
            end as spO2v,
        case when bun >= 60 then ">=60"
            when bun between 30 and 60 then "30-60"
            when bun between 5 and 30 then "5-30"
            when bun < 5 then "<5"
            else "unmeasured"
            end as bun,
        case when tbili >= 3.5 then ">=3.5"
            when tbili between 1.2 and 3.5 then "1.2-3.5"
            when tbili between 0.3 and 1.2 then "0.3-1.2"
            when tbili < 0.3 then "<0.3"
            else "unmeasured"
            end as tbili,
        case when trop >= 0.5 then ">=0.5"
            when trop between 0.1 and 0.5 then "0.1-0.5"
            when trop < 0.1 then "<0.1"
            else "unmeasured"
            end as trop,
        case when hct >= 47 then ">=47"
            when hct between 33 and 47 then "33-47"
            when hct between 24 and 33 then "24-33"
            when hct between 18 and 24 then "18-24"
            when hct < 18 then "<18"
            else "unmeasured"
            end as hct,
        case when wbc >= 18.0 then ">=18.0"
            when wbc between 11.0 and 18.0 then "11.0-18.0"
            when wbc between 4.0 and 11.0 then "4.0-11.0"
            when wbc between 2.5 and 4.0 then "2.5-4.0"
            when wbc < 2.5 then "<2.5"
            else "unmeasured"
            end as wbc,
        case when na >= 155 then ">=155"
            when na between 145 and 155 then "145-155"
            when na between 130 and 145 then "130-145"
            when na between 120 and 130 then "120-130"
            when na < 120 then "<120"
            else "unmeasured"
            end as na,
        case when k >= 6.5 then ">=6.5"
            when k between 5.0 and 6.5 then "5.0-6.5"
            when k between 3.5 and 5.0 then "3.5-5.0"
            when k between 2.5 and 3.5 then "2.5-3.5"
            when k < 2.5 then "<2.5"
            else "unmeasured"
            end as k,
        case when plt >= 600 then ">=600"
            when plt between 450 and 600 then "450-600"
            when plt between 150 and 450 then "150-450"
            when plt between 50 and 150 then "50-150"
            when plt < 50 then "<50"
            else "unmeasured"
            end as plt,
        case when hco3v >= 38.0 then ">=38.0"
            when hco3v between 33.0 and 38.0 then "33.0-38.0"
            when hco3v between 23.0 and 33.0 then "23.0-33.0"
            when hco3v between 17.0 and 23.0 then "17.0-23.0"
            when hco3v < 17.0 then "<17.0"
            else "unmeasured"
            end as hco3v,
        case when pHv >= 7.55 then ">=7.55"
            when pHv between 7.45 and 7.55 then "7.45-7.55"
            when pHv between 7.30 and 7.45 then "7.30-7.45"
            when pHv between 7.20 and 7.30 then "7.20-7.30"
            when pHv < 7.20 then "<7.20"
            else "unmeasured"
            end as pHv,
    FROM labs_processed
    ORDER BY enc
),

labs_2buckets AS
(
    SELECT
        enc,
        case when cr >= 3.0 then ">=3.0"
            when cr < 3.0 then "<3.0"
            else "unmeasured"
            end as cr,
        case when lactate >= 2.5 then ">=2.5"
            when lactate < 2.5 then "<2.5"
            else "unmeasured"
            end as lactate,
        case when pO2v >= 30 then ">=30"
            when pO2v < 30 then "<30"
            else "unmeasured"
            end as pO2v,
        case when pCO2v >= 50 then ">=50"
            when pCO2v < 50 then "<50"
            else "unmeasured"
            end as pCO2v,
        case when spO2v >= 60 then ">=60"
            when spO2v < 60 then "<60"
            else "unmeasured"
            end as spO2v,
        case when bun >= 40 then ">=40"
            when bun < 40 then "<40"
            else "unmeasured"
            end as bun,
        case when tbili >= 1.5 then ">=1.5"
            when tbili < 1.5 then "<1.5"
            else "unmeasured"
            end as tbili,
        case when trop >= 0.1 then ">=0.1"
            when trop < 0.1 then "<0.1"
            else "unmeasured"
            end as trop,
        case when hct >= 27 then ">=27"
            when hct < 27 then "<27"
            else "unmeasured"
            end as hct,
        case when wbc >= 14.0 then ">=14.0"
            when wbc < 14.0 then "<14.0"
            else "unmeasured"
            end as wbc,
        case when na >= 125 then ">=125"
            when na < 125 then "<125"
            else "unmeasured"
            end as na,
        case when k >= 3.0 then ">=3.0"
            when k < 3.0 then "<3.0"
            else "unmeasured"
            end as k,
        case when plt >= 100 then ">=100"
            when plt < 100 then "<100"
            else "unmeasured"
            end as plt,
        case when hco3v >= 35.0 then ">=35.0"
            when hco3v < 35.0 then "<35.0"
            else "unmeasured"
            end as hco3v,
        case when pHv >= 7.50 then ">=7.50"
            when pHv < 7.50 then "<7.50"
            else "unmeasured"
            end as pHv,
    FROM labs_processed
    ORDER BY enc

    #CR > 3 --> YES, NO (include MISSING for data extraction, but for regression, convert all MISSING -> NO ... there would be negative interaction btwn MISSING & NO)
),

-- Note: not sure if I can trust values... many temperatures are in 60s... doesn't make sense for either Celsius or Fahrenheit. Furthermore, some temperatures labeled as Fahrenheit are in mid/high 30s (a.k.a. clearly in Celsius). Tabling this for now
flowsheet_all AS
(

    SELECT DISTINCT
      enc, admsnTimeJTR, template, row_disp_name, num_value1, num_value2, units, recorded_time, DATETIME_DIFF(b.recorded_time, a.admsnTimeJTR, HOUR) AS difference,
      case when row_disp_name IN ("Urine Output (mL)", "Last 24Hrs - Total Urine Output") then num_value1 else null end as uop, -- urine output
      case when row_disp_name IN ("Heart Rate", "Pulse") then num_value1 else null end as hr, -- heart rate
      case when row_disp_name IN ("FiO2","FiO2 (%)") then num_value1 else null end as fiO2, -- fractional inspired O2
      case when row_disp_name IN ("SpO2") then num_value1 else null end as spO2, -- pulse ox
      --case when row_disp_name IN ("") then num_value1 else null end as rr, -- respiratory rate
      case when row_disp_name IN ("In last 6 hours temperature < 36 C or > 38.3 C","Temp < 36 C (96.8 F) or >38.3C (100.9 F)") then TRUE
           when (row_disp_name="Temp" and num_value1 < 96.8) then TRUE
           when (row_disp_name="Temp" and num_value1 > 100.9) then TRUE
           when (row_disp_name="Temp (in Celsius)" and num_value1 < 36) then TRUE
           when (row_disp_name="Temp (in Celsius)" and num_value1 > 38.3) then TRUE
           else FALSE end as tempAbnormal, -- temperature abnormal
      case when row_disp_name = "Temp" then (num_value1-32)*5/9
           when row_disp_name = "Temp (in Celsius)" then num_value1
           # "RLE Temperature/Condition","LLE Temperature/Condition","LUE Temperature/Condition","RUE Temperature/Condition","Temperature"
           else null end as temp, -- temperature
      case when row_disp_name IN ("MAP","MAP ","Mean Arterial Pressure (Calculated)","Mean Arterial Pressure") then num_value1 else null end as map,
      case when row_disp_name IN ("MAP","MAP ","Mean Arterial Pressure (Calculated)","Mean Arterial Pressure") AND num_value1 <65 then TRUE else FALSE end as mapBelow65,
      case when row_disp_name IN ("MAP","MAP ","Mean Arterial Pressure (Calculated)","Mean Arterial Pressure") AND num_value1 >130 then TRUE else FALSE end as mapAbove130
      --case when row_disp_name IN ("Vent Mode","Ventilation support mode","O2 Delivery","O2 Delivery Method","Ventilation device","Ventilation device status","Ventilation type","Ventilation mode","Ventilator on") then num_value1 else null end as vent -- breath support, oxygenation delivery, ventilator mode
      #COUNT(result_time) OVER (PARTITION BY enc, base_name ORDER BY result_time DESC) AS latest, -- filter by "latest=1" to take the latest value for any given lab in 24h period
    FROM selectDRGs a
    LEFT JOIN `mining-clinical-decisions.shc_core.flowsheet` b
        ON a.anon_id = b.anon_id
        AND DATETIME_DIFF(recorded_time, admsnTimeJTR, HOUR) >= 0
        AND DATETIME_DIFF(recorded_time, admsnTimeJTR, HOUR) <= 24
        -- use inpatient_data_id_coded?

        AND row_disp_name IN ("Urine Output (mL)", "Last 24Hrs - Total Urine Output",
                                "Heart Rate", "Pulse",
                                "FiO2","FiO2 (%)",
                                "SpO2",
                                "In last 6 hours temperature < 36 C or > 38.3 C","Temp < 36 C (96.8 F) or >38.3C (100.9 F)",
                                "Temp","Temp (in Celsius)", -- "RLE Temperature/Condition","LLE Temperature/Condition","LUE Temperature/Condition","RUE Temperature/Condition","Temperature",
                                "MAP","MAP ","Mean Arterial Pressure (Calculated)","Mean Arterial Pressure") -- "BP","NIBP","Blood Pressure","Arterial Systolic BP ","Arterial Diastolic BP ","In last 6 hours SBP < 90 or MAP < 65"
                                -- "Vent Mode","Ventilation support mode","O2 Delivery","O2 Delivery Method","Ventilation device","Ventilation device status","Ventilation type","Ventilation mode","Ventilator on")
    ORDER BY enc, recorded_time

    /*
    # smoothing --> ensure not capturing just an outlier / error decreased SpO2 (due to artifact) but rather a true, sustained deterioration
    # message Morteza, Conor, Grace
    # highest HR w/in 24h

    */
),


flowsheet_2buckets AS
(
  SELECT enc, admsnTimeJTR,
          case when max(uop) <= 500 then "<= 500cc"
               else ">500cc"
               end as uop,
               -- SpO2: >96, 94-95, 92-93, 88-92, 86-87, 84-85, <83
               -- Temperature: >41, 39-41, 38.5-39, 36-38.5, 34-36, 32-34, 30-32, <30
               -- MAP: cutoffs: >159, 129, 109, 69, 49, <49
               -- HR: cutoffs: >180, 140, 110, 70, 55, 40, <40
          case when max(hr) >= 140 then ">=140bpm"
               else "<140"
               end as hr_max,
          case when avg(fiO2) >= 75 then ">=75%"
               else "<75%"
               end as fiO2_avg,
          case when min(spO2) <= 85 then "<=85%"
               else ">85%"
               end as spO2_Min,
          max(tempAbnormal) as tempEverAbnormal,
          max(mapBelow65) as mapEverBelow65,
          max(mapAbove130) as mapEverAbove130,
          case when avg(map) >= 115 then ">=115"
               when avg(map) between 75 and 115 then "between 75 and 115"
               else "<75"
               end as map_Avg

  FROM flowsheet_all # `som-nero-phi-jonc101-secure.kush_db.vitals`
  GROUP BY enc, admsnTimeJTR
),


-- aggregate lab values + vitals flowchart data
gatherObjectiveFeatures AS
(
    SELECT *
    FROM selectDRGs a
    JOIN patientFactors USING (enc,admsnTimeJTR)
    LEFT JOIN labs_2buckets USING(enc)
    LEFT JOIN flowsheet_2buckets USING (enc,admsnTimeJTR)

)

SELECT * FROM gatherObjectiveFeatures

-- SELECT * FROM labs_all WHERE enc=131275787339 ORDER BY base_name, hrsAfterAdmit DESC -- this query shows instance with MULTIPLE labs (ie. HCT) drawn for same pt in given 24h period
