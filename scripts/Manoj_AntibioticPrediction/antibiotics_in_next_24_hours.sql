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
CREATE OR REPLACE TABLE `mvm_abx.antibiotics_24h_after_culture_order` AS 

SELECT DISTINCT unique_culture_labels.anon_id, unique_culture_labels.csn,
  meds.order_med_id_coded, meds.med_description,
  unique_culture_labels.order_time_jittered, meds.order_start_time_jittered,
  thera_class_name, thera_class_abbr, med_route_c,
  CASE
    WHEN REGEXP_CONTAINS(upper(med_description), 'PIPERACILLIN') THEN 'PIPERACILLIN_TAZOBACTAM'
    WHEN REGEXP_CONTAINS(upper(med_description), 'CEFAZOLIN') THEN 'CEFAZOLIN'
    WHEN REGEXP_CONTAINS(upper(med_description), 'CEFTRIAXONE') THEN 'CEFTRIAXONE'
    WHEN REGEXP_CONTAINS(upper(med_description), 'CEFEPIME') THEN 'CEFEPIME'
    WHEN REGEXP_CONTAINS(upper(med_description), 'CIPROFLOXACIN') THEN 'CIPROFLOXACIN'
    WHEN REGEXP_CONTAINS(upper(med_description), 'AMPICILLIN') AND NOT REGEXP_CONTAINS(upper(med_description), 'SULBACTAM') THEN 'AMPICILLIN'
    WHEN REGEXP_CONTAINS(upper(med_description), 'VANCOMYCIN') THEN 'VANCOMYCIN'
    WHEN REGEXP_CONTAINS(upper(med_description), 'ERTAPENEM') THEN 'ERTAPENEM'
    WHEN REGEXP_CONTAINS(upper(med_description), 'MEROPENEM') THEN 'MEROPENEM'
    ELSE upper(med_description)
  END as antibiotic_24h
FROM `shc_core_2023.order_med` as meds INNER JOIN # Inner join to only get rx data on patients with culture labels
  (SELECT DISTINCT anon_id, csn, order_time_jittered
   FROM `mvm_abx.encounter_culture_labels_features_inpatient_24h_with_inference`) as unique_culture_labels
  on meds.anon_id = unique_culture_labels.anon_id
WHERE 
  DATETIME_DIFF(meds.order_start_time_jittered, unique_culture_labels.order_time_jittered, HOUR) >= 0 AND
  DATETIME_DIFF(meds.order_start_time_jittered, unique_culture_labels.order_time_jittered, HOUR) <= 24 AND
  (REGEXP_CONTAINS(upper(med_description), 'PIPERACILLIN') OR
   REGEXP_CONTAINS(upper(med_description), 'CEFAZOLIN') OR
   REGEXP_CONTAINS(upper(med_description), 'CEFTRIAXONE') OR
   REGEXP_CONTAINS(upper(med_description), 'CEFEPIME') OR
   REGEXP_CONTAINS(upper(med_description), 'CIPROFLOXACIN') OR
   (REGEXP_CONTAINS(upper(med_description), 'AMPICILLIN') AND NOT REGEXP_CONTAINS(upper(med_description), 'SULBACTAM')) OR
   REGEXP_CONTAINS(upper(med_description), 'VANCOMYCIN') OR
   REGEXP_CONTAINS(upper(med_description), 'ERTAPENEM') OR
   REGEXP_CONTAINS(upper(med_description), 'MEROPENEM'))