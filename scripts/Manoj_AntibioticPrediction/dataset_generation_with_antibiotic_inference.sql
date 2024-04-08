######################################################################################## 
# DECLARE variables
######################################################################################## 
DECLARE hours_limit INT64 DEFAULT 24;

#
# Antibiotic names
#
DECLARE abx_regex_ignore STRING DEFAULT NULL;
SET abx_regex_ignore = 'ESBL|METHOD|PCR|INBASKET|SCREEN|TEST|LACTAMASE|ANTIBIOTIC|IMP|CONTROL|KPC|OTHER|VIM|LIKE|NDM|SYNERGY|INDUC';

######################################################################################## 
######################################################################################## 
######################################################################################## 
#
#
# Create table of labels + features where each row is an individual culture
#
#
######################################################################################## 
######################################################################################## 
######################################################################################## 
CREATE OR REPLACE TABLE `mvm_abx.individual_culture_labels_features_inpatient_24h_with_inference` AS 

WITH
######################################################################################## 
# Create list of inpatient admissions
######################################################################################## 
adm AS (
  SELECT DISTINCT *
    FROM `shc_core_2023.adt`
  WHERE
  event_type_c = 1 AND -- Admission
  event_subtype_c = 1 -- Original encounter
),

######################################################################################## 
# Create list of inpatient culture sensitivities
######################################################################################## 
culture_labels AS (
  SELECT DISTINCT
  cs.anon_id, cs.order_proc_id_coded, cs.description, cs.organism,
  UPPER(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(antibiotic, r'(\.)|\s\([^()]*\)', ''), '/', '_'))) as antibiotic, cs.resistance, cs.order_time_jittered,
  cs.result_time_jittered, op.pat_enc_csn_id_coded, op.ordering_mode, op.order_status,
  adm.effective_time_jittered, 
  DATETIME_DIFF(cs.order_time_jittered, adm.effective_time_jittered, HOUR) as ordering_hrs_since_admission,
  CASE
  WHEN upper(cs.description) LIKE '%URINE CULT%' THEN 'urine'
  WHEN upper(cs.description) LIKE '%BLOOD CULT%' THEN 'blood'
  WHEN upper(cs.description) LIKE '%RESPIRATORY CULT%' THEN 'respiratory'
  ELSE cs.description
  END as culture_type
  FROM
  `mvm_abx.culture_sensitivity_inferred` AS cs INNER JOIN # Inner rather than left join as we have to get order_proc_id_coded and pat_enc_csn_id_coded
  `shc_core_2023.order_proc` AS op ON cs.order_proc_id_coded = op.order_proc_id_coded INNER JOIN -- To get pat_enc_csn_id_coded
  adm ON op.pat_enc_csn_id_coded = adm.pat_enc_csn_id_coded
  WHERE
  (upper(cs.description) LIKE '%URINE CULT%' OR -- Urine culture
    upper(cs.description) LIKE '%RESPIRATORY CULT%' -- Respiratory culture
    OR upper(cs.description) LIKE '%BLOOD CULT%') AND -- Blood culture
  upper(cs.description) NOT LIKE '%CYSTIC%' AND -- NOT Cystic Fibrosis    
  upper(cs.description) NOT LIKE '%BIOPSY%' AND -- NOT Biopsy
  upper(ordering_mode) LIKE '%INPATIENT%' AND -- Inpatient
  (NOT REGEXP_CONTAINS(UPPER(cs.antibiotic), abx_regex_ignore)) AND 
  DATETIME_DIFF(cs.order_time_jittered, adm.effective_time_jittered, HOUR) <= hours_limit -- Ordered within 24 hours of admission/encounter creation
), 
######################################################################################## 
# Create list of lab results
######################################################################################## 
lab_results AS (
  SELECT labs.anon_id, labs.pat_enc_csn_id_coded, order_id_coded, group_lab_name, lab_name, ord_value, ord_num_value,
  order_time_jittered, taken_time_jittered, result_time_jittered, base_pat_class, pat_service, accomodation, effective_time_jittered, reference_unit,
  CASE 
  WHEN upper(lab_name) IN ('WBC') THEN 'wbc'
  WHEN upper(lab_name) IN ('NEUTROPHIL, ABSOLUTE') THEN 'neutrophil'
  WHEN upper(lab_name) IN ('LYMPHOCYTE, ABSOLUTE') THEN 'lymphocyte'
  WHEN upper(lab_name) IN ('HEMOGLOBIN') THEN 'hgb'
  WHEN upper(lab_name) IN ('PLATELET COUNT') THEN 'plt'
  WHEN upper(lab_name) IN ('SODIUM, SER/PLAS') THEN 'sodium'
  WHEN upper(lab_name) IN ('BUN, SER/PLAS', 'UREA NITROGEN,SER/PLAS') THEN 'bun'
  WHEN upper(lab_name) IN ('CO2, SER/PLAS') THEN 'bicarb'
  WHEN upper(lab_name) IN ('CREATININE, SER/PLAS') THEN 'creat'
  WHEN upper(lab_name) IN ('AST (SGOT), SER/PLAS') THEN 'ast'
  WHEN upper(lab_name) IN ('ALT (SGPT), SER/PLAS') THEN 'alt'
  WHEN upper(lab_name) IN ('TOTAL BILIRUBIN, SER/PLAS', 'TOTAL BILIRUBIN') THEN 'bili'
  WHEN upper(lab_name) IN ('ALBUMIN, SER/PLAS') THEN 'album'
  WHEN upper(lab_name) IN ('GLUCOSE, SER/PLAS', 'GLUCOSE BY METER', 'GLUCOSE,ISTAT') THEN 'gluc'
  WHEN upper(lab_name) IN ('LACTATE, ISTAT', 'LACTATE, WHOLE BLD', 'LACTIC ACID', 'LACTATE, POC') THEN 'lactate'
  ELSE lab_name
  END as lab, 
  CASE
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), r'K/UL|X10E3/UL|THOUSAND/UL|KUL|10X3/UL|10\\*3/UL') THEN 'K/UL'
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), 'MEQ/L|MMOL/L|MMOLL|MM/L|MMOLE/L') THEN 'MMOL/L'
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), 'G/DL') THEN 'G/DL'
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), 'MG/L') THEN 'MG/L'
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), 'MG/DL') THEN 'MG/DL'
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), 'MM/HR|MM/H|^MM$') THEN 'MM/HR'
  WHEN REGEXP_CONTAINS(UPPER(reference_unit), 'IU/L|U/L|UNITS/L') THEN 'U/L'
  ELSE reference_unit
  END as unit,
  DATETIME_DIFF(labs.result_time_jittered, adm.effective_time_jittered, HOUR) as ordering_hrs_since_admission
  FROM
  `shc_core_2023.lab_result` as labs INNER JOIN # Inner join as every lab needs to have a pat_enc_csn_id_coded
  adm ON labs.pat_enc_csn_id_coded = adm.pat_enc_csn_id_coded
  WHERE
  (reference_unit IS NOT NULL) AND -- Exclude labs without a reference value
  (labs.pat_enc_csn_id_coded IN (SELECT pat_enc_csn_id_coded FROM culture_labels)) AND -- Only labs from the current encounter
  (DATETIME_DIFF(labs.result_time_jittered, adm.effective_time_jittered, HOUR) <= hours_limit) AND -- Ordered within 24 hours of admission/encounter creation

  ((upper(trim(group_lab_name)) IN ('CBC WITH DIFFERENTIAL', 'CBC', 'CBC WITH DIFF') AND upper(trim(lab_name)) IN ('WBC')) OR -- White blood cell count
   (upper(trim(group_lab_name)) IN ('CBC WITH DIFFERENTIAL') AND upper(trim(lab_name)) IN ('NEUTROPHIL, ABSOLUTE')) OR -- Absolute neutrophil count
   (upper(trim(group_lab_name)) IN ('CBC WITH DIFFERENTIAL') AND upper(trim(lab_name)) IN ('LYMPHOCYTE, ABSOLUTE')) OR -- Absolute lymphocyte count
   (upper(trim(group_lab_name)) IN ('CBC WITH DIFFERENTIAL', 'CBC', 'CBC WITH DIFF') AND upper(trim(lab_name)) IN ('HEMOGLOBIN')) OR -- Hemoglobin
   (upper(trim(group_lab_name)) IN ('CBC WITH DIFFERENTIAL', 'CBC', 'CBC WITH DIFF') AND upper(trim(lab_name)) IN ('PLATELET COUNT')) OR -- Platelets
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'METABOLIC PANEL, BASIC', 'CMP') AND upper(trim(lab_name)) IN ('SODIUM, SER/PLAS')) OR -- Sodium
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'METABOLIC PANEL, BASIC', 'CMP') AND upper(trim(lab_name)) IN ('CO2, SER/PLAS')) OR -- Serum bicarbonate
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'METABOLIC PANEL, BASIC', 'CMP') AND upper(trim(lab_name)) IN ('BUN, SER/PLAS', 'UREA NITROGEN,SER/PLAS')) OR -- BUN
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'METABOLIC PANEL, BASIC', 'CMP') AND upper(trim(lab_name)) IN ('CREATININE, SER/PLAS')) OR -- Creatinine    
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'CMP', 'HEPATIC FUNCTION PANEL A') AND upper(trim(lab_name)) IN ('AST (SGOT), SER/PLAS')) OR -- AST
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'CMP', 'HEPATIC FUNCTION PANEL A') AND upper(trim(lab_name)) IN ('ALT (SGPT), SER/PLAS')) OR -- ALT
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'CMP', 'HEPATIC FUNCTION PANEL A') AND upper(trim(lab_name)) IN ('TOTAL BILIRUBIN, SER/PLAS', 'TOTAL BILIRUBIN')) OR -- Total bilirubin
   (upper(trim(group_lab_name)) IN ('METABOLIC PANEL, COMPREHENSIVE', 'CMP', 'HEPATIC FUNCTION PANEL A') AND upper(trim(lab_name)) IN ('ALBUMIN, SER/PLAS')) OR -- Serum albumin
   (upper(trim(group_lab_name)) IN ('GLUCOSE BY METER', 'METABOLIC PANEL, COMPREHENSIVE', 'METABOLIC PANEL, BASIC', 'CMP', 'ISTAT CR, HCT/HB, CL , BUN, NA, K, GLUCOSE, ICA, TCO2') AND upper(trim(lab_name)) IN ('GLUCOSE, SER/PLAS', 'GLUCOSE BY METER', 'GLUCOSE,ISTAT')) OR -- Serum or fingerstick glucose
  (upper(trim(group_lab_name)) IN ('ISTAT ARTERIAL BLOOD GASES AND LACTATE', 'ISTAT VENOUS BLOOD GASES AND LACTATE', 'LACTIC ACID', 'LACTATE, WHOLE BLOOD', 'LACTIC ACID, AUTO-REPEAT IN 3HR IF 1ST LACTIC RESULT >2', 'ISTAT OTHERS BLOOD GASES AND LACTATE') AND upper(trim(lab_name)) IN ('LACTATE, ISTAT', 'LACTATE, WHOLE BLD', 'LACTIC ACID', 'LACTATE, POC'))) -- Serum, whole blood, or iSTAT lactate
),

######################################################################################## 
# Create list of vital signs
######################################################################################## 
vital_signs AS (
  SELECT vitals.anon_id, template, row_disp_name, meas_value, numerical_val_1, numerical_val_2, units,
  data_source, recorded_time_jittered,
  CASE
  WHEN upper(row_disp_name) IN ('PULSE', 'HEART RATE') THEN 'hrate'
  WHEN upper(row_disp_name) in ('RESP', 'RESP RATE') THEN 'rrate'
  WHEN upper(row_disp_name) IN ('TEMP') THEN 'temp'
  WHEN upper(row_disp_name) in ('WEIGHT') THEN 'weight'
  --- WHEN REGEXP_CONTAINS(UPPER(row_disp_name), spo2_regex) THEN 'spo2'
  --- WHEN REGEXP_CONTAINS(UPPER(row_disp_name), o2_delivery_regex) THEN 'o2_delivery'
  ELSE row_disp_name
  END as vital_sign
  FROM
  `shc_core_2023.flowsheet` as vitals INNER JOIN # Inner rather than left join to only get vitals for patients with culture labels
  culture_labels ON vitals.anon_id = culture_labels.anon_id
  WHERE
  ((upper(trim(row_disp_name)) IN ('PULSE', 'HEART RATE') AND SAFE_CAST(numerical_val_1 AS numeric) >= 30) OR -- Heart rate
   (upper(trim(row_disp_name)) in ('RESP', 'RESP RATE') AND SAFE_CAST(numerical_val_1 AS numeric) >= 4 AND SAFE_CAST(numerical_val_1 AS numeric) <= 60) OR -- Respiratory rate
   (upper(trim(row_disp_name)) IN ('TEMP') AND SAFE_CAST(numerical_val_1 AS numeric) >= 90) OR -- Temperature in F
   (upper(trim(row_disp_name)) IN ('WEIGHT') AND SAFE_CAST(numerical_val_1 AS numeric) >= 480 AND SAFE_CAST(numerical_val_1 AS numeric) <= 8000) --- OR -- Weight 
   ---(upper(trim(row_disp_name)) IN ('SPO2', 'RESTING SPO2') AND CAST(numerical_val_1 AS numeric) >= 70) OR -- SpO2
   --- (REGEXP_CONTAINS(UPPER(template), vs_group_name) AND REGEXP_CONTAINS(UPPER(row_disp_name), o2_delivery_regex) AND NOT REGEXP_CONTAINS(UPPER(row_disp_name), o2_delivery_regex_negate)) -- O2 Delivery (SpO2 is different)
  )
),

######################################################################################## 
# Create list of systolic BP
######################################################################################## 
sysbp AS (
  SELECT vitals.anon_id, template, row_disp_name, numerical_val_1 as meas_value, numerical_val_1, numerical_val_2, units,
  data_source, recorded_time_jittered, 'sysbp' as vital_sign
  FROM 
  `shc_core_2023.flowsheet` as vitals INNER JOIN # Inner rather than left join to only get vitals for patients with culture labels
  culture_labels ON vitals.anon_id = culture_labels.anon_id
  WHERE
  (upper(trim(row_disp_name)) IN ('BP', 'NIBP') AND SAFE_CAST(numerical_val_1 AS numeric) >= 40) -- Systolic BP
),

######################################################################################## 
# Create list of diastolic BP
######################################################################################## 
diasbp AS (
  SELECT vitals.anon_id, template, row_disp_name, numerical_val_2 as meas_value, numerical_val_1, numerical_val_2, units,
  data_source, recorded_time_jittered, 'diasbp' as vital_sign
  FROM 
  `shc_core_2023.flowsheet` as vitals INNER JOIN # Inner rather than left join to only get vitals for patients with culture labels
  culture_labels ON vitals.anon_id = culture_labels.anon_id
  WHERE
  (upper(trim(row_disp_name)) IN ('BP', 'NIBP') AND SAFE_CAST(numerical_val_2 AS numeric) >= 30) -- Diastolic BP
),

######################################################################################## 
# Create list of patients who had order for catecholamine vasopressors prior to culture order
######################################################################################## 
vasopressor AS (
  SELECT distinct culture_labels.anon_id, culture_labels.order_proc_id_coded, 1 AS vasopressor
  FROM `shc_core_2023.order_med` as meds INNER JOIN
    culture_labels on (meds.anon_id = culture_labels.anon_id AND meds.pat_enc_csn_id_coded = culture_labels.pat_enc_csn_id_coded)
  WHERE 
    pharm_class_name IN ('SYMPATHOMIMETIC AGENTS', 'ADRENERGIC AGENTS,CATECHOLAMINES') AND
    DATETIME_DIFF(meds.order_inst_jittered, culture_labels.order_time_jittered, HOUR) <= 0
),

######################################################################################## 
# Create list of patients who have received CPT code for dialysis
######################################################################################## 
dialysis AS (
  SELECT DISTINCT procedures.anon_id, culture_labels.order_proc_id_coded, 1 as dialysis
  FROM `som-nero-phi-jonc101.shc_core_2023.procedure` as procedures INNER JOIN
    culture_labels on culture_labels.anon_id = procedures.anon_id
  WHERE 
    SAFE_CAST(code as numeric) >= 90935 AND SAFE_CAST(code as numeric) <= 90999 AND
    procedures.start_date_jittered < culture_labels.order_time_jittered
),

######################################################################################## 
# Create list of demographics (age, gender)
######################################################################################## 
demographics AS (
  SELECT DISTINCT(demographics.anon_id), culture_labels.order_proc_id_coded, ABS(DATETIME_DIFF(culture_labels.order_time_jittered, demographics.birth_date_jittered, YEAR)) as age_at_order,
  CASE
    WHEN demographics.gender = 'Female' THEN 1
    ELSE 0
    END as female
  FROM `shc_core_2023.demographic` as demographics INNER JOIN # Inner join to only get demographics for patients with culture labels
    culture_labels ON culture_labels.anon_id = demographics.anon_id
),

######################################################################################## 
# Create list of prior oral antibiotic prescriptions
######################################################################################## 
rx_abx_oral AS (
  SELECT DISTINCT unique_culture_labels.anon_id, unique_culture_labels.order_proc_id_coded, count(meds.order_med_id_coded) as count_rx
  FROM `shc_core_2023.order_med` as meds INNER JOIN # Inner join to only get rx data on patients with culture labels
    (SELECT DISTINCT anon_id, order_proc_id_coded, order_time_jittered FROM culture_labels) as unique_culture_labels
    ON meds.anon_id = unique_culture_labels.anon_id
  WHERE 
    meds.anon_id = unique_culture_labels.anon_id AND
    meds.order_start_time_jittered < unique_culture_labels.order_time_jittered AND
    thera_class_name = 'ANTIBIOTICS' AND
    med_route_c = 15 -- Oral
  GROUP BY unique_culture_labels.anon_id, unique_culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create list of prior IV antibiotic prescriptions
######################################################################################## 
rx_abx_iv AS (
  SELECT DISTINCT unique_culture_labels.anon_id, unique_culture_labels.order_proc_id_coded, count(meds.order_med_id_coded) as count_rx
  FROM `shc_core_2023.order_med` as meds INNER JOIN # Inner join to only get rx data on patients with culture labels
    (SELECT DISTINCT anon_id, order_proc_id_coded, order_time_jittered FROM culture_labels) as unique_culture_labels
    ON meds.anon_id = unique_culture_labels.anon_id
  WHERE 
    meds.anon_id = unique_culture_labels.anon_id AND
    meds.order_start_time_jittered < unique_culture_labels.order_time_jittered AND
    thera_class_name = 'ANTIBIOTICS' AND
    med_route_c = 11 -- Intravenous
  GROUP BY unique_culture_labels.anon_id, unique_culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create list of prior antibiotic resistance counts within 6 months prior to culture_labels order
# Using inferred susceptibility table
######################################################################################## 
prior_abx_resistance_within_6mo AS (
  SELECT DISTINCT * FROM (
    SELECT  unique_culture_labels.anon_id, unique_culture_labels.order_proc_id_coded,
      UPPER(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(prior_sensitivities.antibiotic, r'(\.)|\s\([^()]*\)', ''), '/', '_'))) as prior_culture_antibiotic, 
      CASE
        WHEN prior_sensitivities.suscept = 'Susceptible' THEN 0
        ELSE 1
      END AS resistance
    FROM `shc_core_2023.culture_sensitivity` as prior_sensitivities INNER JOIN
      (SELECT DISTINCT anon_id, order_proc_id_coded, order_time_jittered FROM culture_labels) as unique_culture_labels
      on prior_sensitivities.anon_id = unique_culture_labels.anon_id
    WHERE
      DATETIME_DIFF(prior_sensitivities.result_time_jittered, unique_culture_labels.order_time_jittered, DAY) <= 0 AND
      DATETIME_DIFF(prior_sensitivities.result_time_jittered, unique_culture_labels.order_time_jittered, DAY) > -180 AND
      (upper(prior_sensitivities.description) LIKE '%URINE CULT%' OR -- Urine culture
       upper(prior_sensitivities.description) LIKE '%RESPIRATORY CULT%' OR -- Respiratory culture
       upper(prior_sensitivities.description) LIKE '%BLOOD CULT%') AND -- Blood culture
       upper(prior_sensitivities.description) NOT LIKE '%CYSTIC%' AND -- NOT Cystic Fibrosis    
       upper(prior_sensitivities.description) NOT LIKE '%BIOPSY%' AND -- NOT Biopsy
      ((UPPER(prior_sensitivities.antibiotic) LIKE '%CIPROFLOXACIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%CEFAZOLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%CEFTRIAXONE%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%CEFEPIME%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%OXACILLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%AMPICILLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%MEROPENEM%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%PIPERACILLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%VANCOMYCIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%TRIMETHOPRIM%')))
  PIVOT (SUM(resistance) FOR prior_culture_antibiotic IN ('OXACILLIN', 'AMPICILLIN', 'CEFAZOLIN', 'CEFTRIAXONE', 'CEFEPIME', 'CIPROFLOXACIN', 'PIPERACILLIN_TAZOBACTAM', 'MEROPENEM', 'TRIMETHOPRIM_SULFAMETHOXAZOLE', 'VANCOMYCIN'))
),

######################################################################################## 
# Create list of prior antibiotic resistance counts more than 6 months prior to culture_labels order
# Using inferred susceptibility table
######################################################################################## 
prior_abx_resistance_before_6mo AS (
  SELECT DISTINCT * FROM (
    SELECT  unique_culture_labels.anon_id, unique_culture_labels.order_proc_id_coded,
      UPPER(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(prior_sensitivities.antibiotic, r'(\.)|\s\([^()]*\)', ''), '/', '_'))) as prior_culture_antibiotic, 
      CASE
        WHEN prior_sensitivities.suscept = 'Susceptible' THEN 0
        ELSE 1
      END AS resistance
    FROM `shc_core_2023.culture_sensitivity` as prior_sensitivities INNER JOIN
      (SELECT DISTINCT anon_id, order_proc_id_coded, order_time_jittered FROM culture_labels) as unique_culture_labels
      on prior_sensitivities.anon_id = unique_culture_labels.anon_id
    WHERE
      DATETIME_DIFF(prior_sensitivities.result_time_jittered, unique_culture_labels.order_time_jittered, DAY) < -180 AND
      (upper(prior_sensitivities.description) LIKE '%URINE CULT%' OR -- Urine culture
       upper(prior_sensitivities.description) LIKE '%RESPIRATORY CULT%' OR -- Respiratory culture
       upper(prior_sensitivities.description) LIKE '%BLOOD CULT%') AND -- Blood culture
       upper(prior_sensitivities.description) NOT LIKE '%CYSTIC%' AND -- NOT Cystic Fibrosis    
       upper(prior_sensitivities.description) NOT LIKE '%BIOPSY%' AND -- NOT Biopsy
      ((UPPER(prior_sensitivities.antibiotic) LIKE '%CIPROFLOXACIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%CEFAZOLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%CEFTRIAXONE%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%CEFEPIME%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%OXACILLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%AMPICILLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%MEROPENEM%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%PIPERACILLIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%VANCOMYCIN%') OR
       (UPPER(prior_sensitivities.antibiotic) LIKE '%TRIMETHOPRIM%')))
  PIVOT (SUM(resistance) FOR prior_culture_antibiotic IN ('OXACILLIN', 'AMPICILLIN', 'CEFAZOLIN', 'CEFTRIAXONE', 'CEFEPIME', 'CIPROFLOXACIN', 'PIPERACILLIN_TAZOBACTAM', 'MEROPENEM', 'TRIMETHOPRIM_SULFAMETHOXAZOLE', 'VANCOMYCIN'))
),
######################################################################################## 
# Create list of prior hospital admissions
######################################################################################## 
prior_admissions AS (
  SELECT admissions.anon_id, culture_labels.order_proc_id_coded, count(distinct admissions.pat_enc_csn_id_jittered) as number_of_admissions
  FROM `shc_core_2023.f_ip_hsp_admission` as admissions INNER JOIN
    culture_labels on culture_labels.anon_id = admissions.anon_id
  WHERE
    admissions.hosp_disch_date_jittered < culture_labels.order_time_jittered
  GROUP BY admissions.anon_id, culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create table of prior antibiograms
# Using inferred susceptibility table
######################################################################################## 
all_susceptibilities_perc AS (
  SELECT distinct year, antibiotic_clean, resistance, count(*) as cnt,
    ROUND(100 * count(*)/sum(count(*)) over(partition by year, antibiotic_clean)) as perc,
  FROM (SELECT extract(Year from order_time_jittered) as year,
    UPPER(TRIM(REGEXP_REPLACE(REGEXP_REPLACE(antibiotic, r'(\.)|\s\([^()]*\)', ''), '/', '_'))) as antibiotic_clean,
    CASE
      WHEN suscept = 'Susceptible' THEN 0
      ELSE 1
    END as resistance
    FROM `shc_core_2023.culture_sensitivity`
    WHERE NOT REGEXP_CONTAINS(UPPER(antibiotic), abx_regex_ignore))
  group by year, antibiotic_clean, resistance
  order by year desc, antibiotic_clean
),

prior_antibiogram AS (
SELECT * FROM 
(SELECT year, antibiotic_clean, perc 
  FROM all_susceptibilities_perc
  WHERE resistance = 0)
PIVOT (max(perc) for antibiotic_clean in ('OXACILLIN', 'AMPICILLIN', 'CEFAZOLIN', 'CEFTRIAXONE', 'CEFEPIME', 'CIPROFLOXACIN', 'PIPERACILLIN_TAZOBACTAM', 'MEROPENEM', 'TRIMETHOPRIM_SULFAMETHOXAZOLE', 'VANCOMYCIN'))
),

######################################################################################## 
# Create a table of number of prior Pseudomonas culture results 
# (from any culture source, not limited to inferred urine/blood/respiratory)
######################################################################################## 
prior_pseudomonas_culture AS (
  SELECT DISTINCT culture_labels.anon_id, culture_labels.order_proc_id_coded,
    count(distinct prior_sensitivities.order_proc_id_coded) as prior_pseudomonas_culture --prior_sensitivities.order_proc_id_coded
  FROM `shc_core_2023.culture_sensitivity` as prior_sensitivities INNER JOIN 
    culture_labels on prior_sensitivities.anon_id = culture_labels.anon_id
  WHERE
    DATETIME_DIFF(prior_sensitivities.result_time_jittered, culture_labels.order_time_jittered, DAY) < 0 AND
    upper(prior_sensitivities.organism) LIKE '%PSEUDOMONAS%'
  GROUP BY culture_labels.anon_id, culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create a table of number of prior Staph Aureus culture results
# (from any culture source, not limited to inferred urine/blood/respiratory)
######################################################################################## 
prior_staph_aureus_culture AS (
  SELECT DISTINCT culture_labels.anon_id, culture_labels.order_proc_id_coded,
    count(distinct prior_sensitivities.order_proc_id_coded) as prior_staph_aureus_culture --prior_sensitivities.order_proc_id_coded
  FROM `shc_core_2023.culture_sensitivity` as prior_sensitivities INNER JOIN
    culture_labels on prior_sensitivities.anon_id = culture_labels.anon_id
  WHERE
    DATETIME_DIFF(prior_sensitivities.result_time_jittered, culture_labels.order_time_jittered, DAY) < 0 AND
    (upper(prior_sensitivities.organism) LIKE '%STAPH%' AND upper(prior_sensitivities.organism) LIKE '%AUREUS%')
  GROUP BY culture_labels.anon_id, culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create a table of number of prior Enterococcus culture results
# (from any culture source, not limited to inferred urine/blood/respiratory)
######################################################################################## 
prior_enterococcus_culture AS (
  SELECT DISTINCT culture_labels.anon_id, culture_labels.order_proc_id_coded,
    count(distinct prior_sensitivities.order_proc_id_coded) as prior_enterococcus_culture --prior_sensitivities.order_proc_id_coded
  FROM `shc_core_2023.culture_sensitivity` as prior_sensitivities INNER JOIN
    culture_labels on prior_sensitivities.anon_id = culture_labels.anon_id
  WHERE
    DATETIME_DIFF(prior_sensitivities.result_time_jittered, culture_labels.order_time_jittered, DAY) < 0 AND
    upper(prior_sensitivities.organism) LIKE '%ENTEROCOCCUS%'
  GROUP BY culture_labels.anon_id, culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create a list of prior ICD9 codes for each patient and order result
######################################################################################## 
icd9s_wide AS (
  SELECT distinct culture_labels.anon_id, culture_labels.order_proc_id_coded,
    STRING_AGG(distinct diagnoses.icd9) as icd9s
  FROM `shc_core_2023.diagnosis` as diagnoses INNER JOIN
  culture_labels on culture_labels.anon_id = diagnoses.anon_id
  WHERE DATETIME_DIFF(culture_labels.order_time_jittered, diagnoses.start_date_jittered, DAY) > 0
  GROUP BY culture_labels.anon_id, culture_labels.order_proc_id_coded
),

######################################################################################## 
# Create WIDE table of maximum lab values
######################################################################################## 
labs_max AS (
  SELECT DISTINCT * FROM (
    SELECT culture_labels.anon_id, culture_labels.order_proc_id_coded, lab, ord_value, culture_labels.order_time_jittered, 
    ---culture_labels.description, culture_labels.culture_type, culture_labels.organism, culture_labels.antibiotic, culture_labels.suscept, 
    FROM culture_labels INNER JOIN lab_results ON
    (culture_labels.anon_id = lab_results.anon_id AND
      culture_labels.pat_enc_csn_id_coded = lab_results.pat_enc_csn_id_coded)
    WHERE
    DATETIME_DIFF(culture_labels.order_time_jittered, lab_results.result_time_jittered, HOUR) <= 0 -- Labs available before culture ordered (already filtered to be same CSN)
  )
  PIVOT (MAX(ord_value) FOR lab IN ('wbc', 'neutrophil', 'bun', 'creat', 'ast', 'alt', 'bili', 'lactate'))
),
######################################################################################## 
# Create WIDE table of minimum lab values
######################################################################################## 
labs_min AS (
  SELECT DISTINCT * FROM (
    SELECT culture_labels.anon_id, culture_labels.order_proc_id_coded, lab, ord_value
    --- culture_labels.description, culture_labels.organism, culture_labels.antibiotic, culture_labels.suscept, 
    FROM culture_labels INNER JOIN lab_results ON
    (culture_labels.anon_id = lab_results.anon_id AND
      culture_labels.pat_enc_csn_id_coded = lab_results.pat_enc_csn_id_coded)
    WHERE
    DATETIME_DIFF(culture_labels.order_time_jittered, lab_results.result_time_jittered, HOUR) <= 0 -- Labs available before culture ordered (already filtered to be same CSN)
  )
  PIVOT (MIN(ord_value) FOR lab IN ('lymphocyte', 'hgb', 'plt', 'sodium', 'bicarb', 'album', 'gluc'))
),

######################################################################################## 
# Create WIDE table of maximum vital sign values (except Systolic BP -- separate table)
######################################################################################## 
vitals_max AS (
  SELECT DISTINCT * FROM (
    SELECT culture_labels.anon_id, culture_labels.order_proc_id_coded, vital_sign, meas_value
    --- culture_labels.description, culture_labels.organism, culture_labels.antibiotic, culture_labels.suscept, 
    FROM culture_labels INNER JOIN vital_signs ON
    culture_labels.anon_id = vital_signs.anon_id
    WHERE
    DATETIME_DIFF(culture_labels.order_time_jittered, vital_signs.recorded_time_jittered, HOUR) <= 0 AND -- Vitals available within 24 hours of culture order
    DATETIME_DIFF(culture_labels.order_time_jittered, vital_signs.recorded_time_jittered, HOUR) > -24 -- Vitals available within 24 hours of culture order
  )
  PIVOT (MAX(meas_value) FOR vital_sign IN ('hrate', 'rrate', 'temp'))
),

######################################################################################## 
# Create WIDE table of minimum vital sign values (except Systolic BP -- separate table)
######################################################################################## 
vitals_min AS (
  SELECT DISTINCT * FROM (
    SELECT culture_labels.anon_id, culture_labels.order_proc_id_coded, vital_sign, meas_value
    -- culture_labels.description, culture_labels.organism, culture_labels.antibiotic, culture_labels.suscept, 
    FROM culture_labels INNER JOIN vital_signs ON
    culture_labels.anon_id = vital_signs.anon_id
    WHERE
    DATETIME_DIFF(culture_labels.order_time_jittered, vital_signs.recorded_time_jittered, HOUR) <= 0 AND -- Vitals available within 24 hours of culture order
    DATETIME_DIFF(culture_labels.order_time_jittered, vital_signs.recorded_time_jittered, HOUR) > -24 -- Vitals available within 24 hours of culture order
  )
  PIVOT (MIN(meas_value) FOR vital_sign IN ('weight'))
),

######################################################################################## 
# Create WIDE table of minimum systolic BP values 
######################################################################################## 
sysbp_min AS (
  SELECT DISTINCT * FROM (
    SELECT culture_labels.anon_id, culture_labels.order_proc_id_coded, vital_sign, meas_value
    -- culture_labels.description, culture_labels.organism, culture_labels.antibiotic, culture_labels.suscept, 
    FROM culture_labels INNER JOIN sysbp ON
    culture_labels.anon_id = sysbp.anon_id
    WHERE
    DATETIME_DIFF(culture_labels.order_time_jittered, sysbp.recorded_time_jittered, HOUR) <= 0 AND -- Vitals available within 24 hours of culture order
    DATETIME_DIFF(culture_labels.order_time_jittered, sysbp.recorded_time_jittered, HOUR) > -24 -- Vitals available within 24 hours of culture order
  )
  PIVOT (MIN(meas_value) FOR vital_sign IN ('sysbp'))
), 

######################################################################################## 
# Create WIDE table of minimum diastolic BP values 
######################################################################################## 
diasbp_min AS (
  SELECT DISTINCT * FROM (
    SELECT culture_labels.anon_id, culture_labels.order_proc_id_coded, vital_sign, meas_value
    -- culture_labels.description, culture_labels.organism, culture_labels.antibiotic, culture_labels.suscept, 
    FROM culture_labels INNER JOIN diasbp ON
    culture_labels.anon_id = diasbp.anon_id
    WHERE
    DATETIME_DIFF(culture_labels.order_time_jittered, diasbp.recorded_time_jittered, HOUR) <= 0 AND -- Vitals available within 24 hours of culture order
    DATETIME_DIFF(culture_labels.order_time_jittered, diasbp.recorded_time_jittered, HOUR) > -24 -- Vitals available within 24 hours of culture order
  )
  PIVOT (MIN(meas_value) FOR vital_sign IN ('diasbp'))
), 

######################################################################################## 
# Create combined WIDE table of features and labels
######################################################################################## 
individual_culture_labels_features AS (
  SELECT DISTINCT culture_labels.anon_id, SAFE_CAST(culture_labels.pat_enc_csn_id_coded as STRING) as csn, culture_labels.order_proc_id_coded,
  culture_labels.description, culture_labels.culture_type,
  culture_labels.organism, culture_labels.antibiotic, culture_labels.resistance,
  culture_labels.order_time_jittered, extract(year from culture_labels.order_time_jittered) as year,
  wbc as wbch, neutrophil as neutrophilh, lymphocyte as lymphocytel, hgb as hgbl, plt as pltl,
  sodium as sodiuml, bicarb as bicarbl, bun as bunh,
  creat as creath, ast as asth, alt as alth, bili as bilih, album as albuml, gluc as glucl, lactate as lactateh, 
  hrate as hrateh, rrate as rrateh, temp as temph, sysbp as sysbpl, diasbp as diasbpl, weight as weightl,
  age_at_order as age, female, icd9s_wide.icd9s as icd9s,
  IFNULL(vasopressor.vasopressor, 0) as vasopressor,
  IFNULL(prior_admissions.number_of_admissions, 0) as number_of_admissions,
  IFNULL(dialysis.dialysis, 0) as dialysis,
  IFNULL(rx_abx_oral.count_rx, 0) as count_rx_oral, IFNULL(rx_abx_iv.count_rx, 0) as count_rx_iv,
  IFNULL(prior_abx_resistance_within_6mo.CIPROFLOXACIN, 0) as count_ciprofloxacin_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.OXACILLIN, 0) as count_oxacillin_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.AMPICILLIN, 0) as count_ampicillin_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.CEFAZOLIN, 0) as count_cefazolin_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.CEFTRIAXONE, 0) as count_ceftriaxone_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.CEFEPIME, 0) as count_cefepime_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.MEROPENEM, 0) as count_meropenem_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.VANCOMYCIN, 0) as count_vancomycin_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.PIPERACILLIN_TAZOBACTAM, 0) as count_pip_tazo_resistance_within_6mo,
  IFNULL(prior_abx_resistance_within_6mo.TRIMETHOPRIM_SULFAMETHOXAZOLE, 0) as count_trim_sulfa_resistance_within_6mo,
  IFNULL(prior_abx_resistance_before_6mo.CIPROFLOXACIN, 0) as count_ciprofloxacin_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.OXACILLIN, 0) as count_oxacillin_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.AMPICILLIN, 0) as count_ampicillin_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.CEFAZOLIN, 0) as count_cefazolin_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.CEFTRIAXONE, 0) as count_ceftriaxone_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.CEFEPIME, 0) as count_cefepime_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.MEROPENEM, 0) as count_meropenem_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.VANCOMYCIN, 0) as count_vancomycin_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.PIPERACILLIN_TAZOBACTAM, 0) as count_pip_tazo_resistance_before_6mo,
  IFNULL(prior_abx_resistance_before_6mo.TRIMETHOPRIM_SULFAMETHOXAZOLE, 0) as count_trim_sulfa_resistance_before_6mo,
  IFNULL(prior_pseudomonas_culture.prior_pseudomonas_culture, 0) as count_prior_pseudomonas_culture,
  IFNULL(prior_staph_aureus_culture.prior_staph_aureus_culture, 0) as count_prior_staph_aureus_culture,
  IFNULL(prior_enterococcus_culture.prior_enterococcus_culture, 0) as count_prior_enterococcus_culture,
  prior_antibiogram.OXACILLIN as prior_year_antibiogram_oxacillin,
  prior_antibiogram.AMPICILLIN as prior_year_antibiogram_ampicillin,
  prior_antibiogram.CEFAZOLIN as prior_year_antibiogram_cefazolin,
  prior_antibiogram.CEFTRIAXONE as prior_year_antibiogram_ceftriaxone,
  prior_antibiogram.CEFEPIME as prior_year_antibiogram_cefepime,
  prior_antibiogram.CIPROFLOXACIN as prior_year_antibiogram_ciprofloxacin,
  prior_antibiogram.PIPERACILLIN_TAZOBACTAM as prior_year_antibiogram_pip_tazo,
  prior_antibiogram.MEROPENEM as prior_year_antibiogram_meropenem,
  prior_antibiogram.TRIMETHOPRIM_SULFAMETHOXAZOLE as prior_year_antibiogram_trim_sulfa,
  prior_antibiogram.VANCOMYCIN as prior_year_antibiogram_vancomycin,

  FROM culture_labels LEFT JOIN vitals_max ON (
    culture_labels.anon_id = vitals_max.anon_id AND
    culture_labels.order_proc_id_coded = vitals_max.order_proc_id_coded
  ) LEFT JOIN vitals_min ON (
    culture_labels.anon_id = vitals_min.anon_id AND
    culture_labels.order_proc_id_coded = vitals_min.order_proc_id_coded
  ) LEFT JOIN sysbp_min ON (
    culture_labels.anon_id = sysbp_min.anon_id AND
    culture_labels.order_proc_id_coded = sysbp_min.order_proc_id_coded
  ) LEFT JOIN diasbp_min ON (
    culture_labels.anon_id = diasbp_min.anon_id AND
    culture_labels.order_proc_id_coded = diasbp_min.order_proc_id_coded
  ) LEFT JOIN labs_max ON (
    culture_labels.anon_id = labs_max.anon_id AND
    culture_labels.order_proc_id_coded = labs_max.order_proc_id_coded
  ) LEFT JOIN labs_min ON (
    culture_labels.anon_id = labs_min.anon_id AND
    culture_labels.order_proc_id_coded = labs_min.order_proc_id_coded
  ) LEFT JOIN vasopressor ON (
    culture_labels.anon_id = vasopressor.anon_id AND
    culture_labels.order_proc_id_coded = vasopressor.order_proc_id_coded
  ) LEFT JOIN demographics ON (
    culture_labels.anon_id = demographics.anon_id AND
    culture_labels.order_proc_id_coded = demographics.order_proc_id_coded
  ) LEFT JOIN prior_admissions ON (
    culture_labels.anon_id = prior_admissions.anon_id AND
    culture_labels.order_proc_id_coded = prior_admissions.order_proc_id_coded
  ) LEFT JOIN dialysis ON (
    culture_labels.anon_id = dialysis.anon_id AND
    culture_labels.order_proc_id_coded = dialysis.order_proc_id_coded
  ) LEFT JOIN rx_abx_oral ON (
    culture_labels.anon_id = rx_abx_oral.anon_id AND
    culture_labels.order_proc_id_coded = rx_abx_oral.order_proc_id_coded
  ) LEFT JOIN rx_abx_iv ON (
    culture_labels.anon_id = rx_abx_iv.anon_id AND
    culture_labels.order_proc_id_coded = rx_abx_iv.order_proc_id_coded
  ) LEFT JOIN prior_abx_resistance_within_6mo ON (
    culture_labels.anon_id = prior_abx_resistance_within_6mo.anon_id AND
    culture_labels.order_proc_id_coded = prior_abx_resistance_within_6mo.order_proc_id_coded
  ) LEFT JOIN prior_abx_resistance_before_6mo ON (
    culture_labels.anon_id = prior_abx_resistance_before_6mo.anon_id AND
    culture_labels.order_proc_id_coded = prior_abx_resistance_before_6mo.order_proc_id_coded
  ) LEFT JOIN prior_antibiogram ON (
    extract(Year from culture_labels.order_time_jittered)-1 = prior_antibiogram.year
  ) LEFT JOIN prior_pseudomonas_culture ON (
    culture_labels.anon_id = prior_pseudomonas_culture.anon_id AND
    culture_labels.order_proc_id_coded = prior_pseudomonas_culture.order_proc_id_coded
  ) LEFT JOIN prior_staph_aureus_culture ON (
    culture_labels.anon_id = prior_staph_aureus_culture.anon_id AND
    culture_labels.order_proc_id_coded = prior_staph_aureus_culture.order_proc_id_coded
  ) LEFT JOIN prior_enterococcus_culture ON (
    culture_labels.anon_id = prior_enterococcus_culture.anon_id AND
    culture_labels.order_proc_id_coded = prior_enterococcus_culture.order_proc_id_coded
  ) LEFT JOIN icd9s_wide ON (
    culture_labels.anon_id = icd9s_wide.anon_id AND
    culture_labels.order_proc_id_coded = icd9s_wide.order_proc_id_coded
  )
)

SELECT * from individual_culture_labels_features;

######################################################################################## 
######################################################################################## 
######################################################################################## 
#
#
# Create table of labels + features where each row is combined culture results
# From an individual encounter
#
#
######################################################################################## 
######################################################################################## 
######################################################################################## 
CREATE OR REPLACE TABLE `mvm_abx.encounter_culture_labels_features_inpatient_24h_with_inference` AS 

WITH individual_culture_labels_features_wide AS (
  SELECT * FROM `som-nero-phi-jonc101.mvm_abx.individual_culture_labels_features_inpatient_24h_with_inference`
  PIVOT (max(resistance) for antibiotic IN ('OXACILLIN', 'AMPICILLIN', 'CEFAZOLIN', 'CEFTRIAXONE', 'CEFEPIME', 
                                                'PIPERACILLIN_TAZOBACTAM', 'CIPROFLOXACIN', 'TRIMETHOPRIM_SULFAMETHOXAZOLE',
                                                'MEROPENEM', 'VANCOMYCIN'))
),

encounter_culture_labels_features_wide AS (
  SELECT anon_id, csn, 
    MAX(order_time_jittered) as order_time_jittered, MIN(year) as year,
    -- MAX(effective_time_jittered) as effective_time_jittered,
    -- MAX(result_time_jittered) as result_time_jittered,
    MAX(wbch) as wbch, MAX(neutrophilh) as neutrophilh, MIN(lymphocytel) as lymphocytel, MIN(hgbl) as hgbl, MIN(pltl) as pltl, 
    MIN(sodiuml) as sodiuml, MIN(bicarbl) as bicarbl, MAX(bunh) as bunh, MAX(creath) as creath,
    MAX(asth) as asth, MAX(alth) as alth, MAX(bilih) as bilih, MIN(albuml) as albuml, MIN(glucl) as glucl, MAX(lactateh) as lactateh,
    MAX(hrateh) as hrateh, MAX(rrateh) as rrateh, MAX(temph) as temph, MIN(sysbpl) as sysbpl, MIN(diasbpl) as diasbpl, MIN(weightl) as weightl,
    MAX(age) as age, MAX(female) as female,
    STRING_AGG(icd9s, ',') as icd9s,
    MAX(vasopressor) as vasopressor,
    MAX(number_of_admissions) as number_of_admissions,
    MAX(dialysis) as dialysis,
    MAX(count_rx_oral) as count_rx_oral, MAX(count_rx_iv) as count_rx_iv,
    MAX(count_ciprofloxacin_resistance_within_6mo) as count_ciprofloxacin_resistance_within_6mo,
    MAX(count_oxacillin_resistance_within_6mo) as count_oxacillin_resistance_within_6mo,
    MAX(count_ampicillin_resistance_within_6mo) as count_ampicillin_resistance_within_6mo,
    MAX(count_cefazolin_resistance_within_6mo) as count_cefazolin_resistance_within_6mo,
    MAX(count_ceftriaxone_resistance_within_6mo) as count_ceftriaxone_resistance_within_6mo,
    MAX(count_cefepime_resistance_within_6mo) as count_cefepime_resistance_within_6mo, 
    MAX(count_meropenem_resistance_within_6mo) as count_meropenem_resistance_within_6mo,
    MAX(count_vancomycin_resistance_within_6mo) as count_vancomycin_resistance_within_6mo, 
    MAX(count_pip_tazo_resistance_within_6mo) as count_pip_tazo_resistance_within_6mo,
    MAX(count_trim_sulfa_resistance_within_6mo) as count_trim_sulfa_resistance_within_6mo,
    MAX(count_ciprofloxacin_resistance_before_6mo) as count_ciprofloxacin_resistance_before_6mo,
    MAX(count_oxacillin_resistance_before_6mo) as count_oxacillin_resistance_before_6mo,
    MAX(count_ampicillin_resistance_before_6mo) as count_ampicillin_resistance_before_6mo,
    MAX(count_cefazolin_resistance_before_6mo) as count_cefazolin_resistance_before_6mo,
    MAX(count_ceftriaxone_resistance_before_6mo) as count_ceftriaxone_resistance_before_6mo,
    MAX(count_cefepime_resistance_before_6mo) as count_cefepime_resistance_before_6mo, 
    MAX(count_meropenem_resistance_before_6mo) as count_meropenem_resistance_before_6mo,
    MAX(count_vancomycin_resistance_before_6mo) as count_vancomycin_resistance_before_6mo, 
    MAX(count_pip_tazo_resistance_before_6mo) as count_pip_tazo_resistance_before_6mo,
    MAX(count_trim_sulfa_resistance_before_6mo) as count_trim_sulfa_resistance_before_6mo,
    MAX(count_prior_pseudomonas_culture) as count_prior_pseudomonas_culture,
    MAX(count_prior_staph_aureus_culture) as count_prior_staph_aureus_culture,
    MAX(count_prior_enterococcus_culture) as count_prior_enterococcus_culture,
    MIN(prior_year_antibiogram_oxacillin) as prior_year_antibiogram_oxacillin,
    MIN(prior_year_antibiogram_ampicillin) as prior_year_antibiogram_ampicillin,
    MIN(prior_year_antibiogram_cefazolin) as prior_year_antibiogram_cefazolin,
    MIN(prior_year_antibiogram_ceftriaxone) as prior_year_antibiogram_ceftriaxone,
    MIN(prior_year_antibiogram_cefepime) as prior_year_antibiogram_cefepime,
    MIN(prior_year_antibiogram_ciprofloxacin) as prior_year_antibiogram_ciprofloxacin,
    MIN(prior_year_antibiogram_pip_tazo) as prior_year_antibiogram_pip_tazo,
    MIN(prior_year_antibiogram_meropenem) as prior_year_antibiogram_meropenem,
    MIN(prior_year_antibiogram_trim_sulfa) as prior_year_antibiogram_trim_sulfa,
    MIN(prior_year_antibiogram_vancomycin) as prior_year_antibiogram_vancomycin,    
    MAX(OXACILLIN) as OXACILLIN, MAX(AMPICILLIN) as AMPICILLIN, MAX(CEFAZOLIN) as CEFAZOLIN, MAX(CEFTRIAXONE) as CEFTRIAXONE, MAX(CEFEPIME) as CEFEPIME,
    MAX(PIPERACILLIN_TAZOBACTAM) as PIPERACILLIN_TAZOBACTAM, MAX(CIPROFLOXACIN) as CIPROFLOXACIN, MAX(TRIMETHOPRIM_SULFAMETHOXAZOLE) as TRIMETHOPRIM_SULFAMETHOXAZOLE,
    MAX(MEROPENEM) as MEROPENEM, MAX(VANCOMYCIN) as VANCOMYCIN
  FROM individual_culture_labels_features_wide
  GROUP BY
    anon_id, csn
),

encounter_culture_labels_features AS (
  SELECT 
    t.anon_id,  t.csn, t.order_time_jittered, t.year,
    t.wbch, t.neutrophilh, t.lymphocytel, t.hgbl, t.pltl, 
    t.sodiuml, t.bicarbl, t.bunh, t.creath, t.asth, t.alth, t.bilih, t.albuml, t.glucl, t.lactateh,
    t.hrateh, t.rrateh, t.temph, t.sysbpl, t.diasbpl, t.weightl,
    t.age, t.female, t.icd9s, t.vasopressor, 
    t.number_of_admissions, t.dialysis,
    t.count_rx_oral, t.count_rx_iv, 
    t.count_ciprofloxacin_resistance_within_6mo,
    t.count_oxacillin_resistance_within_6mo,
    t.count_ampicillin_resistance_within_6mo,
    t.count_cefazolin_resistance_within_6mo,
    t.count_ceftriaxone_resistance_within_6mo,
    t.count_cefepime_resistance_within_6mo,
    t.count_meropenem_resistance_within_6mo,
    t.count_vancomycin_resistance_within_6mo,
    t.count_pip_tazo_resistance_within_6mo,
    t.count_trim_sulfa_resistance_within_6mo,
    t.count_ciprofloxacin_resistance_before_6mo,
    t.count_oxacillin_resistance_before_6mo,
    t.count_ampicillin_resistance_before_6mo,
    t.count_cefazolin_resistance_before_6mo,
    t.count_ceftriaxone_resistance_before_6mo,
    t.count_cefepime_resistance_before_6mo,
    t.count_meropenem_resistance_before_6mo,
    t.count_vancomycin_resistance_before_6mo,
    t.count_pip_tazo_resistance_before_6mo,
    t.count_trim_sulfa_resistance_before_6mo,
    t.count_prior_pseudomonas_culture,
    t.count_prior_staph_aureus_culture,
    t.count_prior_enterococcus_culture,
    t.prior_year_antibiogram_oxacillin,
    t.prior_year_antibiogram_ampicillin,
    t.prior_year_antibiogram_cefazolin,
    t.prior_year_antibiogram_ceftriaxone,
    t.prior_year_antibiogram_cefepime,
    t.prior_year_antibiogram_ciprofloxacin,
    t.prior_year_antibiogram_pip_tazo,
    t.prior_year_antibiogram_meropenem,
    t.prior_year_antibiogram_trim_sulfa,
    t.prior_year_antibiogram_vancomycin,
    x.antibiotic, x.resistance
  FROM 
    encounter_culture_labels_features_wide t,
  UNNEST(
    [STRUCT('OXACILLIN' AS antibiotic, OXACILLIN AS resistance),
    STRUCT('AMPICILLIN', AMPICILLIN),
    STRUCT('CEFAZOLIN', CEFAZOLIN),
    STRUCT('CEFTRIAXONE', CEFTRIAXONE),
    STRUCT('CEFEPIME', CEFEPIME),
    STRUCT('PIPERACILLIN_TAZOBACTAM', PIPERACILLIN_TAZOBACTAM),
    STRUCT('CIPROFLOXACIN', CIPROFLOXACIN),
    STRUCT('TRIMETHOPRIM_SULFAMETHOXAZOLE', TRIMETHOPRIM_SULFAMETHOXAZOLE),
    STRUCT('MEROPENEM', MEROPENEM),
    STRUCT('VANCOMYCIN', VANCOMYCIN)
    ]
  ) x
  WHERE x.resistance IS NOT NULL
)

SELECT * FROM encounter_culture_labels_features;