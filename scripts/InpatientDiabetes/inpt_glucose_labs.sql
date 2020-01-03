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

--
-- Labs for the patient cohort of non-pump pts with no AKI who received insulin
-- SELECT AVG(ord_num_value) as average FROM `mining-clinical-decisions.starr_datalake2018.lab_result` 
SELECT COUNT(ord_num_value) as count FROM `mining-clinical-decisions.starr_datalake2018.lab_result` 
-- SELECT rit_uid, pat_enc_csn_id_coded, lab_name, base_name, ordering_mode, ord_value, ord_num_value, taken_time_jittered, result_time_jittered FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` 
-- SELECT ord_num_value, count(ord_num_value) as number FROM `mining-clinical-decisions.starr_datalake2018.lab_result`
WHERE UPPER(lab_name) LIKE '%GLUCOSE%' 
--AND (lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose urine', 'Glucose/Creat ratio', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose", "Glucose,GDM 3HR", "Glucose,GDM 2HR", "Glucose,GDM 1HR", "Glucose, 2 HR", "Glucose, 1 HR", "Glucose, Fasting (GDMF)", "Glucose,GTT 30 min", "Glucose,GTT 1HR", "Glucose,GTT 2HR", "Glucose,2HR - 75g", "Glucose, GDM Screen", "GLUCOSE", "Glucose") -- excludes glucoses not for insulin dose; also "GLUCOSE" and "Glucose" only used n=3 times
AND lab_name = "Glucose by Meter"
AND UPPER(ordering_mode) = 'INPATIENT' AND ord_num_value BETWEEN 0 AND 9999998
-- Checking BG by range 
	--    AND ord_num_value BETWEEN 80 AND 200 -- at goal
	--  AND ord_num_value < 70 -- hypogelyceia
 	-- AND ord_num_value > 200 -- hyperglycemia

AND pat_enc_csn_id_coded IN (SELECT DISTINCT(mar.pat_enc_csn_id_coded) FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar
  LEFT JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded=medord.order_med_id_coded 
	WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2
	     WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_description NOT LIKE "%U-500%" -- exlcudes U-500
       AND medord2.med_description NOT IN ("INSULIN NPH AND REGULAR HUMAN 100 UNIT/ML (70-30) SC SUSP", "INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC SUSP") -- removes 2 basal doses that were not excluded by basal clause below *(see below)
       AND medord2.med_route = 'Subcutaneous') --and subQ
     AND (mar.mar_action) IN ('Given') --medication actually given
   AND (mar.mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed', 'Bolus', 'Complete', 'Completed', 'Push')
   AND mar.dose_unit_c = 5 -- "units", not an infusion (not units/hr)
   AND mar.sig <> "0-10"
   AND CAST(mar.sig AS float64) > 0
   -- AND CAST(mar.sig AS float64) < 100 --set maximum insulin at 100 to minimize recording errors
   AND mar.sig IS NOT NULL 
   AND mar.sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND mar.infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
   AND mar.pat_enc_csn_id_coded NOT IN (SELECT lab.pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as lab -- excludes patient encounters with creatinine >2 
    WHERE (lab_name) LIKE "Creatinine, Ser/Plas" --most common creatinine order
    AND ord_num_value != 9999999
    AND taken_time_jittered IS NOT null
    AND ord_num_value > 2)
    
 --    /* 
    AND mar.pat_enc_csn_id_coded NOT IN (SELECT medord2.pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2 -- excludes patients who had basal insulin ordered * except for 2 orders of NPH that are excluded above
	     WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_description NOT LIKE "%U-500%" -- exlcudes U-500
       AND medord2.med_route = 'Subcutaneous' --and subQ
       AND UPPER(medord2.med_description) IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC SUSP", "NPH INSULIN HUMAN RECOMB 100 UNIT/ML SC SUSP", "INSULIN GLARGINE 100 UNIT/ML SC SOLN", "INSULIN DETEMIR 100 UNIT/ML SC SOLN", "INSULIN NPH ISOPH U-100 HUMAN 100 UNIT/ML SC SUSP", "INSULIN DETEMIR U-100 100 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC SUSP", "INSULIN NPH AND REGULAR HUMAN 100 UNIT/ML (70-30) SC SUSP", "INSULIN NPH AND REGULAR HUMAN 100 UNIT/ML (70/30) SUBCUTANEOUS VIAL", "INSULIN DETEMIR 100 UNIT/ML (3 ML) SC INPN", "INSULIN DETEMIR U-100 100 UNIT/ML SC SOLN", "INSULIN DEGLUDEC 100 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (50-50) SC SUSP", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC INPN", "INSULIN LISPRO PROTAMIN-LISPRO 100 UNIT/ML (75-25) SC INPN", "INSULIN GLARGINE 300 UNIT/3 ML SC INPN", "INSULIN GLARGINE 300 UNIT/ML (1.5 ML) SC INPN", "INSULIN DEGLUDEC 200 UNIT/ML (3 ML) SC INPN", "INSULIN GLARGINE 100 UNIT/ML (3 ML) SC INPN", "INSULIN NPH AND REGULAR HUMAN 100 UNIT/ML (70-30) SC SUSP", "INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC SUSP","INSULIN DETEMIR 100 UNIT/ML SC INPN", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC INPN") -- patients ordered for basal
       ) 
  --     */
       
    AND mar.taken_time_jittered BETWEEN "2018-01-01T00:00:00" AND "2018-12-31T23:59:59"       -- Date range
)




