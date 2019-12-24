--
-- Glucose lab values by person
SELECT rit_uid, pat_enc_csn_id_coded, lab_name, ord_value, ord_num_value, taken_time_jittered, result_time_jittered FROM `mining-clinical-decisions.starr_datalake2018.lab_result` 
-- SELECT lab_name, COUNT(lab_name) as number FROM `mining-clinical-decisions.starr_datalake2018.lab_result` 
WHERE UPPER(lab_name) LIKE '%GLUCOSE%' 
AND (lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose urine', 'Glucose/Creat ratio', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose", "Glucose,GDM 3HR", "Glucose,GDM 2HR", 
"Glucose,GDM 1HR", "Glucose, 2 HR", "Glucose, 1 HR", "Glucose, Fasting (GDMF)", "Glucose,GTT 30 min", "Glucose,GTT 1HR", "Glucose,GTT 2HR", "Glucose,2HR - 75g", "Glucose, GDM Screen", "GLUCOSE", "Glucose") -- excludes glucoses not for insulin dose; also "GLUCOSE" and "Glucose" only used n=3 times
AND UPPER(ordering_mode) = 'INPATIENT' AND ord_num_value BETWEEN 0 AND 9999998
-- GROUP BY lab_name 
-- ORDER BY number

--
-- Glucose by meter lab values
SELECT rit_uid, pat_enc_csn_id_coded, lab_name, base_name, ordering_mode, ord_value, ord_num_value, taken_time_jittered, result_time_jittered FROM `mining-clinical-decisions.starr_datalake2018.lab_result` 
-- SELECT ord_num_value, count(ord_num_value) as number FROM `mining-clinical-decisions.starr_datalake2018.lab_result`
-- SELECT lab_name, COUNT(lab_name) as number FROM `mining-clinical-decisions.starr_datalake2018.lab_result` 
WHERE UPPER(lab_name) LIKE '%GLUCOSE%' 
--AND (lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose urine', 'Glucose/Creat ratio', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose", "Glucose,GDM 3HR", "Glucose,GDM 2HR", "Glucose,GDM 1HR", "Glucose, 2 HR", "Glucose, 1 HR", "Glucose, Fasting (GDMF)", "Glucose,GTT 30 min", "Glucose,GTT 1HR", "Glucose,GTT 2HR", "Glucose,2HR - 75g", "Glucose, GDM Screen", "GLUCOSE", "Glucose") -- excludes glucoses not for insulin dose; also "GLUCOSE" and "Glucose" only used n=3 times
AND lab_name = "Glucose by Meter"
AND UPPER(ordering_mode) = 'INPATIENT' AND ord_num_value BETWEEN 0 AND 9999998
AND ord_num_value BETWEEN 80 AND 200
order by rit_uid, taken_time_jittered, result_time_jittered 

--
-- Creatinine
SELECT rit_uid, pat_enc_csn_id_coded, lab_name, ord_num_value, taken_time_jittered    FROM `mining-clinical-decisions.datalake_47618.lab_result` 
WHERE (lab_name) LIKE "Creatinine, Ser/Plas" --most common creatinine order
AND ord_num_value != 9999999
AND taken_time_jittered IS NOT null

--
-- Patient encounters with AKI/CKD
SELECT rit_uid, pat_enc_csn_id_coded, lab_name, ord_num_value, taken_time_jittered    FROM `mining-clinical-decisions.datalake_47618.lab_result` as lab
WHERE (lab_name) LIKE "Creatinine, Ser/Plas" --most common creatinine order
AND ord_num_value != 9999999
AND taken_time_jittered IS NOT null
AND ord_num_value > 2 -- patient with AKI/CKD, rough approximation 

