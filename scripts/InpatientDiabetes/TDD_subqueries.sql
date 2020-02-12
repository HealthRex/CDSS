
-- 
-- Patients receiving 1-100u per dose inpatient subQ insulin that is not a pump, U500, or a rare order (<25 orders in dataset)
-- Verified that dose was given, dose 1-100, insulins as expected when removing pumps, partial units, insulins ordered <25x
-- If ORDER BY units DESC, top 10 rows should be 98-95U and time 2012 (1) & 2011 (10)

WITH inpt_insulin_given AS ( 
  SELECT mar.jc_uid, mar.pat_enc_csn_id_coded, mar.sig as units, mar.mar_action, medord.med_description, mar.route, medord.medication_id, mar.taken_time_jittered FROM `som-nero-phi-jonc101.starr_datalake2018.mar` as mar 
    LEFT JOIN `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord on mar.order_med_id_coded=medord.order_med_id_coded 
    WHERE mar.order_med_id_coded in 
    (SELECT medord2.order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` as medord2
         WHERE UPPER(medord2.med_description) LIKE '%INSULIN%'-- insulin ordered)
         AND (medord2.ordering_mode_c) = 2 -- inpatient
         AND UPPER(medord2.med_description) NOT LIKE '%PUMP%' --excludes pumps
         AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
         AND medord2.med_description NOT LIKE "%U-500%" -- exlcudes U-500
         AND (medord2.med_description) NOT IN ("INSULIN NPH HUMAN RECOMB 100 UNIT/ML SC CRTG", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (50-50) SC SUSP", "INSULIN GLARGINE 300 UNIT/ML (3 ML) SC INPN", "INSULIN NPH & REGULAR HUMAN 100 UNIT/ML (70-30) SC CRTG", "INSULIN NPH-REGULAR HUM S-SYN 100 UNIT/ML (70-30) SC CRTG", "INSULIN ASP PRT-INSULIN ASPART 100 UNIT/ML (70-30) SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC INPH", "INSULIN NPH HUMAN SEMI-SYN 100 UNIT/ML SC CRTG", "INSULIN ASPART PROTAMINE-ASPART (70/30) 100 UNIT/ML SUBCUTANEOUS PEN", "INSULIN LISPRO PROTAM-LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN GLULISINE 100 UNIT/ML SC CRTG", "INSULIN DEGLUDEC-LIRAGLUTIDE 100 UNIT-3.6 MG /ML (3 ML) SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC SUSP", "INSULIN REGULAR HUM U-500 CONC 500 UNIT/ML SC SOLN", "INSULIN LISPRO 100 UNIT/ML SC CRTG", "INSULIN ASPART 100 UNIT/ML SC CRTG") -- removes anything ordered <10 times
        AND (medord2.med_description) NOT IN ("INSULIN REGULAR 100 UNIT/ML SC VERY AGGRESSIVE SCALE FEEDING (BEDTIME)", "INSULIN GLULISINE 100 UNIT/ML SC SOLN", "INSULIN DEGLUDEC 200 UNIT/ML (3 ML) SC INPN", "INSULIN GLARGINE 300 UNIT/3 ML SC INPN", "INSULIN LISPRO PROTAM & LISPRO 100 UNIT/ML (75-25) SC INPN", "INSULIN GLARGINE 100 UNIT/ML (3 ML) SC INPN", " INV - INSULIN LISPRO SC (ORAL DIETS/BOLUS FEEDS) INTERVENTION", "INSULIN LISPRO PROTAMIN-LISPRO 100 UNIT/ML (75-25) SC INPN", "INSULIN ASPART 100 UNIT/ML AGGRESSIVE SCALE FEEDING", "INSULIN GLARGINE 300 UNIT/ML (1.5 ML) SC INPN") -- removes any insulin ordered < 25 times, conveniently excluding any U200 or U300
        AND medord2.med_description NOT LIKE "%CRTG%" -- excludes anything ordered as a cartridge to remove pumps
        AND medord2.med_route = 'Subcutaneous'
        ) --and subQ
      AND (mar.mar_action) IN ('Given') --medication actually given
      AND (mar.mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed', 'Bolus', 'Complete', 'Completed', 'Push')
      AND mar.dose_unit_c = 5 -- "units", not an infusion (not units/hr)
      AND mar.sig <> "0-10"
      AND CAST(mar.sig AS float64) > 0
      AND CAST(mar.sig AS float64) < 100 --set maximum insulin at 100 to minimize recording errors
      AND mar.sig IS NOT NULL 
      AND mar.sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
      AND mar.infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
    ),

--
-- Pt encounters with creatinine > 2 (will use to exclude hospitalizations where pt had Cr > 2)

cr_over_2 AS (
  SELECT lab.pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` as lab -- patient encounters with creatinine >2 
      WHERE (lab_name) LIKE "Creatinine, Ser/Plas" --most common creatinine order
      AND ord_num_value != 9999999
      AND taken_time_jittered IS NOT null
      AND ord_num_value > 2
      )

