
--
--Patients ordered for and receiving subQ insulin inpatient (n=51,887 patients in 88,372 encounters)
SELECT jc_uid, pat_enc_csn_id_coded, order_med_id_coded, medication_id, med_description, ordering_mode, med_route from starr_datalake2018.order_med
	WHERE order_med_id_coded in 
  (SELECT order_med_id_coded FROM starr_datalake2018.mar --insulin given
	   WHERE order_med_id_coded IN (SELECT order_med_id_coded FROM `starr_datalake2018.order_med`
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered
     	AND (ordering_mode_c) = 2 -- inpatient
      AND med_route = 'Subcutaneous')) --and subQ
	ORDER BY jc_uid, med_description  ASC 


-- 
-- MAR insulin
SELECT jc_uid, pat_enc_csn_id_coded, order_med_id_coded, infusion_rate, sig, dose_unit_c, dose_unit, mar_action, route, route_c FROM `mining-clinical-decisions.starr_datalake2018.mar` 
-- SELECT  mar_action FROM `mining-clinical-decisions.starr_datalake2018.mar` 
	WHERE order_med_id_coded in 
  (SELECT order_med_id_coded FROM starr_datalake2018.order_med 
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (ordering_mode_c) = 2 -- inpatient
       AND med_route = 'Subcutaneous') --and subQ
   AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push', 'Refused', 'Held', 'Stopped', 'Missed') 
   AND (mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull')
   AND dose_unit_c = 5 -- "units", not an infusion (not units/hr)
--   AND (mar_action) IN ('Bolus', 'PUMP Bolus', 'Pump Check', 'Restarted', 'Stopped', 'Given')
   AND (mar_action) IN ('Completed', 'Given', 'Push', 'Refused', 'Held', 'Stopped', 'Missed')       
-- GROUP BY mar_action   
ORDER BY mar_action, jc_uid 


--
-- Evaluating if "sig" is the insulin dose given
SELECT sig, COUNT(sig) as number FROM `mining-clinical-decisions.starr_datalake2018.mar` 
	WHERE order_med_id_coded in 
  (SELECT order_med_id_coded FROM starr_datalake2018.order_med 
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (ordering_mode_c) = 2 -- inpatient
       AND med_route = 'Subcutaneous') --and subQ
   AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push', 'Refused', 'Held', 'Stopped', 'Missed') 
   AND (mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull')
   AND dose_unit_c = 5 -- "units", not an infusion (not units/hr)
--   AND (mar_action) IN ('Bolus', 'PUMP Bolus', 'Pump Check', 'Restarted', 'Stopped', 'Given')
   AND sig <> "0-10" 
   AND sig IS NOT NULL 
GROUP BY sig  
ORDER BY CAST(sig AS float64) --converts string to number


--
-- MAR insulin given, excluding pump dosing (assumed that partial units = pump)
SELECT jc_uid, pat_enc_csn_id_coded, order_med_id_coded, sig, dose_unit, mar_action, route FROM `mining-clinical-decisions.starr_datalake2018.mar` 
-- SELECT  infusion_rate  FROM `mining-clinical-decisions.starr_datalake2018.mar` 
-- SELECT sig, COUNT(sig) as number FROM `mining-clinical-decisions.starr_datalake2018.mar` 
	WHERE order_med_id_coded in 
  (SELECT order_med_id_coded FROM starr_datalake2018.order_med 
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (ordering_mode_c) = 2 -- inpatient
       AND med_route = 'Subcutaneous') --and subQ
     AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push')
--   AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push', 'Refused', 'Held', 'Stopped', 'Missed') 
   AND (mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND dose_unit_c = 5 -- "units", not an infusion (not units/hr)
--   AND (mar_action) IN ('Bolus', 'PUMP Bolus', 'Pump Check', 'Restarted', 'Stopped', 'Given')
   AND sig <> "0-10"
   AND sig IS NOT NULL 
   AND sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
-- GROUP BY sig  
ORDER BY CAST(sig AS float64) --converts string to number


--
-- MAR insulin given joined to name of insulin 
SELECT mar.jc_uid, mar.pat_enc_csn_id_coded, mar.order_med_id_coded,  medord.med_description, mar.sig,  mar.dose_unit, mar.mar_action, mar.route FROM `mining-clinical-decisions.starr_datalake2018.mar` as mar 
  LEFT JOIN starr_datalake2018.order_med as medord on mar.order_med_id_coded=medord.order_med_id_coded 
	WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM starr_datalake2018.order_med as medord2
	     WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND medord2.med_route = 'Subcutaneous') --and subQ
     AND (mar.mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push')
--   AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push', 'Refused', 'Held', 'Stopped', 'Missed') 
   AND (mar.mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND mar.dose_unit_c = 5 -- "units", not an infusion (not units/hr)
--   AND (mar_action) IN ('Bolus', 'PUMP Bolus', 'Pump Check', 'Restarted', 'Stopped', 'Given')
   AND mar.sig <> "0-10"
   AND mar.sig IS NOT NULL 
   AND mar.sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND mar.infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
-- GROUP BY sig  
ORDER BY CAST(mar.sig AS float64) --converts string to number


--
-- MAR insulin given w/ name of insulin, excluding insulin cartridges and types ordered <10x
SELECT mar.jc_uid, mar.pat_enc_csn_id_coded, mar.order_med_id_coded,  medord.med_description, mar.sig,  mar.dose_unit, mar.mar_action, mar.route, mar.taken_time_jittered FROM `mining-clinical-decisions.starr_datalake2018.mar` as mar 
-- SELECT  medord.med_description, count(medord.med_description) as number FROM `mining-clinical-decisions.starr_datalake2018.mar` as mar 
  LEFT JOIN starr_datalake2018.order_med as medord on mar.order_med_id_coded=medord.order_med_id_coded 
	WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM starr_datalake2018.order_med as medord2
	     WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_route = 'Subcutaneous') --and subQ
     AND (mar.mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push') --medication actually given
   AND (mar.mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND mar.dose_unit_c = 5 -- "units", not an infusion (not units/hr)
   AND mar.sig <> "0-10"
   AND mar.sig IS NOT NULL 
   AND mar.sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND mar.infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
ORDER BY CAST(mar.sig AS float64) --converts string to number
-- ORDER BY mar.taken_time_jittered 


-- 
-- NERO version of MAR insulin given w/ name of insulin, excluding insulin cartridges and types ordered <10x
SELECT mar.jc_uid, mar.pat_enc_csn_id_coded, mar.order_med_id_coded,  medord.med_description, mar.sig,  mar.dose_unit, mar.mar_action, mar.route, mar.taken_time_jittered FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar 
-- SELECT  medord.med_description, count(medord.med_description) as number FROM `mining-clinical-decisions.starr_datalake2018.mar` as mar 
  LEFT JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded=medord.order_med_id_coded 
  WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2
       WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_route = 'Subcutaneous') --and subQ
     AND (mar.mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push') --medication actually given
   AND (mar.mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND mar.dose_unit_c = 5 -- "units", not an infusion (not units/hr)
   AND mar.sig <> "0-10"
   AND mar.sig IS NOT NULL 
   AND mar.sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND mar.infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
ORDER BY CAST(mar.sig AS float64) --converts string to number
-- ORDER BY mar.taken_time_jittered 






