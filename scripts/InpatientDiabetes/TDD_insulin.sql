-- TDD by day by patient. Insulin not pumps or U500 or rare. Patient without AKI during that encounter. 

SELECT mar.jc_uid, (SUM(CAST(mar.sig AS float64))) as TDD, DATE(mar.taken_time_jittered) as date FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar 
  LEFT JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded=medord.order_med_id_coded 
  WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2
       WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_description NOT LIKE "%U-500%" -- exlcudes U-500
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
    AND ord_num_value > 2
    )
    
GROUP BY date, mar.jc_uid
ORDER BY mar.jc_uid, date 


-- 
-- Average BG on days when every BG between 100-180
SELECT a.rit_uid, DATE(a.taken_time_jittered) as date  FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as a 

WHERE UPPER(a.lab_name) LIKE '%GLUCOSE%' 
AND a.lab_name = "Glucose by Meter"
AND UPPER(a.ordering_mode) = 'INPATIENT' AND a.ord_num_value BETWEEN 0 AND 9999998
-- AND a.ord_num_value NOT BETWEEN 100 AND 180 

AND a.pat_enc_csn_id_coded IN (SELECT DISTINCT(mar.pat_enc_csn_id_coded) FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar
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
)

GROUP BY a.rit_uid, date

EXCEPT DISTINCT SELECT b.rit_uid, DATE(b.taken_time_jittered) as date FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as b
WHERE UPPER(b.lab_name) LIKE '%GLUCOSE%' 
AND b.lab_name = "Glucose by Meter"
AND UPPER(b.ordering_mode) = 'INPATIENT' AND b.ord_num_value BETWEEN 0 AND 9999998
AND b.ord_num_value NOT BETWEEN 100 AND 180 

GROUP BY b.rit_uid, date

ORDER BY rit_uid, date


-- 
-- TDD on days where BG was 100-180
SELECT jc_uid, TDD, date FROM
(SELECT mar.jc_uid, DATE(mar.taken_time_jittered) as date, (SUM(CAST(mar.sig AS float64))) as TDD, FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar 
  LEFT JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded=medord.order_med_id_coded 
  WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2
       WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_description NOT LIKE "%U-500%" -- exlcudes U-500
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
    AND ord_num_value > 2
    )
    
GROUP BY date, mar.jc_uid
ORDER BY mar.jc_uid, date 
)


WHERE CONCAT(jc_uid,date)  IN

(SELECT CONCAT(rit_uid,date) FROM

(SELECT a.rit_uid, DATE(a.taken_time_jittered) as date FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as a 

WHERE UPPER(a.lab_name) LIKE '%GLUCOSE%' 
AND a.lab_name = "Glucose by Meter"
AND UPPER(a.ordering_mode) = 'INPATIENT' AND a.ord_num_value BETWEEN 0 AND 9999998
-- AND a.ord_num_value NOT BETWEEN 100 AND 180 

AND a.pat_enc_csn_id_coded IN (SELECT DISTINCT(mar.pat_enc_csn_id_coded) FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar
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

    
)

GROUP BY a.rit_uid, date

EXCEPT DISTINCT SELECT b.rit_uid, DATE(b.taken_time_jittered) as date  FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as b

WHERE UPPER(b.lab_name) LIKE '%GLUCOSE%' 
AND b.lab_name = "Glucose by Meter"
AND UPPER(b.ordering_mode) = 'INPATIENT' AND b.ord_num_value BETWEEN 0 AND 9999998
AND b.ord_num_value NOT BETWEEN 100 AND 180 

GROUP BY b.rit_uid, date

)
)


ORDER BY jc_uid, date

--
-- Avg BG on days where all checks between 100-180 and at least 3 checks
SELECT jc_uid, TDD, date FROM
(SELECT mar.jc_uid, DATE(mar.taken_time_jittered) as date, (SUM(CAST(mar.sig AS float64))) as TDD, FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar 
  LEFT JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded=medord.order_med_id_coded 
  WHERE mar.order_med_id_coded in 
  (SELECT medord2.order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2
       WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (medord2.ordering_mode_c) = 2 -- inpatient
       AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
       AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
       AND medord2.med_description NOT LIKE "%U-500%" -- exlcudes U-500
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
    AND ord_num_value > 2
    )
    
GROUP BY date, mar.jc_uid
ORDER BY mar.jc_uid, date 
)


WHERE CONCAT(jc_uid,date)  IN

(SELECT CONCAT(rit_uid,date) FROM

(SELECT a.rit_uid, DATE(a.taken_time_jittered) as date FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as a 

WHERE UPPER(a.lab_name) LIKE '%GLUCOSE%' 
AND a.lab_name = "Glucose by Meter"
AND UPPER(a.ordering_mode) = 'INPATIENT' AND a.ord_num_value BETWEEN 0 AND 9999998
-- AND a.ord_num_value NOT BETWEEN 100 AND 180 

AND a.pat_enc_csn_id_coded IN (SELECT DISTINCT(mar.pat_enc_csn_id_coded) FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar
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

    
)

GROUP BY a.rit_uid, date

EXCEPT DISTINCT SELECT b.rit_uid, DATE(b.taken_time_jittered) as date  FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as b

WHERE UPPER(b.lab_name) LIKE '%GLUCOSE%' 
AND b.lab_name = "Glucose by Meter"
AND UPPER(b.ordering_mode) = 'INPATIENT' AND b.ord_num_value BETWEEN 0 AND 9999998
AND b.ord_num_value NOT BETWEEN 100 AND 180 

GROUP BY b.rit_uid, date having (count(b.lab_name) >2) -- at least 3 lab checks on that date

)
)

ORDER BY jc_uid desc, date 




---
WITH patientDatesWithAtLeast3POCGlucoseWithinRange AS
(
  SELECT rit_uid as jc_uid, DATE(taken_time_jittered) AS patientDate, count(ord_num_value) AS numBG, min(ord_num_value) AS minBG, max(ord_num_value) AS maxBG
  FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result`
  WHERE proc_code = 'LABPOCGLU' -- Point of care glucose
  AND base_name = 'GLU' -- Glucose by Meter (lab_name)
  AND ord_num_value < 9999999
  GROUP BY rit_uid, patientDate
  HAVING numBG >= 3
  AND minBG >= 100
  AND maxBG < 180
),
--- Make separate query to eliminate patient days WHere ever used pump or other of the undesired insulin types
patientDatesTotalDailyDoseSubQInsulinNoAKI AS
(
  SELECT mar.jc_uid, DATE(mar.taken_time_jittered) as patientDate, SUM(CAST(mar.sig AS float64)) as TDD
  FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar
  JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded = medord.order_med_id_coded
  WHERE UPPER(medord.med_description) LIKE '%INSULIN%'-- insulin ordered)
  AND medord.ordering_mode_c = 2 -- inpatient
  AND medord.med_route = 'Subcutaneous' --and subQ
  AND mar.mar_action = 'Given' --medication actually given
  AND mar.dose_unit_c = 5 -- "units", not an infusion (not units/hr)
  AND mar.sig <> "0-10"
  AND CAST(mar.sig AS float64) > 0
  AND CAST(mar.sig AS float64) < 100 --set maximum insulin at 100 to minimize recording errors
  AND mar.sig IS NOT NULL
  
  -- Exclude other types of insulin don't want to capture
  AND mar.pat_enc_csn_id_coded IN 
    (SELECT pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med`
       WHERE UPPER(med_description) NOT LIKE '%PUMP%' --excludes pumps
       AND med_description NOT IN
       (   "INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG"
      ) -- removes anything ordered <10 times
      AND med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
      AND med_description NOT LIKE "%U-500%" -- exlcudes U-500
   )
     AND mar.pat_enc_csn_id_coded IN 
    (SELECT pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.mar`
      WHERE (mar_action) NOT IN 
        ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed', 'Bolus', 'Complete', 'Completed', 'Push'
        )
      AND sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
      AND infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
    )
  -- Exclude any encounter where patient EVER had an elevated creatinine > 2 (even if it was days later or before)
  AND mar.pat_enc_csn_id_coded NOT IN
  ( SELECT lab.pat_enc_csn_id_coded
    FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as lab -- excludes patient encounters with creatinine >2
    WHERE (lab_name) LIKE "Creatinine, Ser/Plas" --most common creatinine order
    AND ord_num_value != 9999999
    AND taken_time_jittered IS NOT null
    AND ord_num_value > 2
  )

  GROUP BY patientDate, mar.jc_uid
  ORDER BY mar.jc_uid, patientDate
)


SELECT a.*, b.TDD
from patientDatesWithAtLeast3POCGlucoseWithinRange as a
join patientDatesTotalDailyDoseSubQInsulinNoAKI as b on (a.jc_uid = b.jc_uid and a.patientDate = b.patientDate)




