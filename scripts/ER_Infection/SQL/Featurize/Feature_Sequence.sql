--- Creates Long Form Patient Feature Timeline From the following tables.  This is an expensive query - costs roughly $1 each time you run it.
-- order_proc
-- diagnois_code
-- order_med
-- lab_results
-- flowsheets -- gets first and second value and appends value number to feature name
-- demographic

CREATE OR REPLACE TABLE `mining-clinical-decisions.abx.feature_timeline_long` AS
(
-- Get order proc feautres from previous year
SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, lab.order_proc_id_coded as order_id, lab.order_type feature_type, lab.description features, NULL as value, lab.order_time_jittered_utc observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
INNER JOIN shc_core.order_proc as lab
USING (anon_id)
WHERE lab.order_time_jittered_utc < labels.index_time
AND lab.order_time_jittered_utc IS NOT NULL
AND timestamp_add(lab.order_time_jittered_utc, INTERVAL 24*365 HOUR) >= labels.index_time

UNION DISTINCT

-- Get icd10 codes from full timeline
SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, dx.pat_enc_csn_id_jittered order_id, -- fill in bc dx does not have order_id
'Diagnosis' as feature_type,
dx.icd10 as features,
NULL as value,
CAST(dx.start_date_utc AS TIMESTAMP) observation_time
FROM
`mining-clinical-decisions.abx.final_cohort_table` as labels
INNER JOIN shc_core.diagnosis_code as dx
USING (anon_id)
WHERE labels.pat_enc_csn_id_coded <> dx.pat_enc_csn_id_jittered 
AND timestamp_add(CAST(dx.start_date_utc AS TIMESTAMP), INTERVAL 24*14 HOUR) < labels.index_time 
AND dx.icd10 is not NULL

UNION DISTINCT

-- Get med orders from order_med from last year
SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, med.order_med_id_coded order_id,
'Meds' as feature_type,
med.med_description as features,
NULL as value,
med.order_inst_utc as observeration_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
INNER JOIN shc_core.order_med as med
USING (anon_id)
WHERE med.order_inst_utc < labels.index_time
AND timestamp_add(med.order_inst_utc, INTERVAL 24*365 HOUR) >= labels.index_time
AND med.order_inst_utc IS NOT NULL

UNION DISTINCT

-- Lab Results From Previous Year - fills 999999's with corresponding high or low value form ord_num
SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, lr.order_id_coded order_id,
'Lab Results' as feature_type,
lr.base_name as features,
CASE WHEN lr.ord_num_value = 9999999 AND lr.ord_value LIKE "%<%"  OR lr.ord_value LIKE "%>%"
THEN CAST(REGEXP_EXTRACT(lr.ord_value, r'(\d+(?:\.\d+)?)') AS FLOAT64) 
ELSE lr.ord_num_value END value,
lr.result_time_utc as observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.lab_result` lr
USING(anon_id)
WHERE lr.result_time_utc < labels.index_time
AND TIMESTAMP_ADD(lr.result_time_utc, INTERVAL 24*365 HOUR) >= labels.index_time
AND lr.base_name IN ('AG','AGAP','ALB','ALT','AST','BASOAB','BE','BUN','CA','CL','CO2','CR','EOSAB','GLOB','GLU','HCO3','HCO3A', 'HCO3V','HCT','HGB','INR','K','LAC','LACWBL','LYMAB','MG','MONOAB','NEUTAB','O2SATA','O2SATV','PCAGP','PCBUN','PCCL','PCO2A',
'PCO2V','PH','PHA','PHCAI','PHOS','PHV','PLT','PO2A','PO2V','PT','RBC','TBIL','TCO2A','TCO2V','TNI','UPH','WBC','XLEUKEST','XUKET')
AND (lr.ord_num_value <> 9999999 OR lr.ord_value LIKE "%<%" OR ord_value LIKE "%>%")

UNION DISTINCT

-- Flowsheets From Previous Year
SELECT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, fl.line order_id, # not selecting distinct bc no unique identifier for flowsheet entry
'Flowsheet' feature_type, 
CONCAT(fl.row_disp_name, "_val_1") features,
fl.num_value1 value,
fl.recorded_time_utc observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.flowsheet` fl
USING (anon_id)
WHERE fl.recorded_time_utc < labels.index_time
AND TIMESTAMP_ADD(fl.recorded_time_utc, INTERVAL 24*365 HOUR) >= labels.index_time
AND fl.row_disp_name IN ("BP", "NIBP", "Resting BP", "Pulse", "Heart Rate", "Resting HR", "Weight", "Height", "Temp", "Resp", 
"Resp Rate", "Resting RR", "SpO2", "Resting SpO2", "O2 (LPM) Arterial Systolic BP", "Arterial Diastolic BP", "Temp (in Celsius)",
"Blood Pressure", "Oxygen Saturation", "Glasgow Coma Scale Score", "Altered Mental Status (GCS<15)", "Total GCS Points", "GCS Score")
AND fl.num_value1 IS NOT NULL

UNION DISTINCT 

SELECT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, fl.line order_id, # not selecting distinct bc no unique identifier for flowsheet entry
'Flowsheet' feature_type, 
CONCAT(fl.row_disp_name, "_val_2") features,
fl.num_value2 value,
fl.recorded_time_utc observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.flowsheet` fl
USING (anon_id)
WHERE fl.recorded_time_utc < labels.index_time
AND TIMESTAMP_ADD(fl.recorded_time_utc, INTERVAL 24*365 HOUR) >= labels.index_time
AND fl.row_disp_name IN ("BP", "NIBP", "Resting BP", "Pulse", "Heart Rate", "Resting HR", "Weight", "Height", "Temp", "Resp", 
"Resp Rate", "Resting RR", "SpO2", "Resting SpO2", "O2 (LPM) Arterial Systolic BP", "Arterial Diastolic BP", "Temp (in Celsius)",
"Blood Pressure", "Oxygen Saturation", "Glasgow Coma Scale Score", "Altered Mental Status (GCS<15)", "Total GCS Points", "GCS Score")
AND fl.num_value2 IS NOT NULL

UNION DISTINCT

-- Demographics

SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, labels.pat_enc_csn_id_coded order_id,
'Demographics' as feature_type, demo.GENDER as feature, NULL as value, CAST(NULL AS TIMESTAMP) observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.demographic` demo
ON labels.anon_id = demo.ANON_ID

UNION DISTINCT

SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, labels.pat_enc_csn_id_coded order_id,
'Demographics' as feature_type, demo.CANONICAL_RACE as feature, NULL as value,
CAST(NULL AS TIMESTAMP) observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.demographic` demo
ON labels.anon_id = demo.ANON_ID

UNION DISTINCT

SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, labels.pat_enc_csn_id_coded order_id,
'Demographics' as feature_type, demo.CANONICAL_ETHNICITY feature, NULL as value,
CAST(NULL AS TIMESTAMP) observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.demographic` demo
ON labels.anon_id = demo.ANON_ID

UNION DISTINCT

SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, labels.pat_enc_csn_id_coded order_id,
'Demographics' as feature_type, demo.INSURANCE_PAYOR_NAME as feature, NULL as value,
CAST(NULL AS TIMESTAMP) observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.demographic` demo
ON labels.anon_id = demo.ANON_ID

UNION DISTINCT

SELECT DISTINCT labels.anon_id, labels.pat_enc_csn_id_coded, labels.index_time, labels.pat_enc_csn_id_coded order_id,
'Demographics' as feature_type,
'Age' as feature, DATE_DIFF(CAST(labels.index_time AS date), demo.BIRTH_DATE_JITTERED, YEAR) as value,
CAST(NULL AS TIMESTAMP) observation_time
FROM `mining-clinical-decisions.abx.final_cohort_table` as labels
LEFT JOIN `shc_core.demographic` demo
ON labels.anon_id = demo.ANON_ID
)