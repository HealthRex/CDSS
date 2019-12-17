--
-- Weight 
SELECT template, row_disp_name, line, num_value1, num_value2 FROM `mining-clinical-decisions.starr_datalake2018.flowsheet` 
WHERE (row_disp_name) LIKE "Weight"
AND num_value1 IS NOT NULL
ORDER BY num_value1 DESC
LIMIT 1000

--
-- Weights converted from ?oz to kg for pts who received insulin
SELECT rit_uid, row_disp_name, meas_value, num_value1, (num_value1*0.028) AS KG, num_value2, recorded_time_jittered FROM `som-nero-phi-jonc101.starr_datalake2018.flowsheet`
-- SELECT (num_value1*0.028) AS KG, count(meas_value) as count  FROM `som-nero-phi-jonc101.starr_datalake2018.flowsheet` 
WHERE rit_uid IN (select jc_uid from `som-nero-phi-jonc101.starr_datalake2018.mar` WHERE order_med_id_coded in --patient received subQ insulin
  (SELECT order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` 
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (ordering_mode_c) = 2 -- inpatient
       AND med_route = 'Subcutaneous') --and subQ
     AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push')
   AND (mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND dose_unit_c = 5 -- "units", not an infusion (not units/hr)
   AND sig <> "0-10"
   AND sig IS NOT NULL 
   AND sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
)
AND row_disp_name LIKE "Weight"
AND num_value1 IS NOT NULL --numeric value exists
--GROUP BY KG 
--ORDER BY count desc
Limit 1000

--
-- Wts converted from oz to kgs for adults, compared to their "most recent weight" from demographics
SELECT dem.rit_uid, flow.row_disp_name, flow.meas_value, flow.num_value1, (flow.num_value1*0.028) AS KG, dem.recent_wt_in_kgs, dem.bmi, flow.num_value2, flow.recorded_time_jittered, DATE_DIFF(DATE(flow.recorded_time_jittered), (dem.birth_date_jittered), YEAR) as ageYears FROM `som-nero-phi-jonc101.starr_datalake2018.flowsheet` AS flow
INNER JOIN `som-nero-phi-jonc101.starr_datalake2018.demographic` AS dem ON dem.rit_uid = flow.rit_uid 
--DATEDIFF(DATE(flow.recorded_time_jittered), DATE(dem.birth_date_jittered), year)  as ageYears
WHERE dem.rit_uid IN (SELECT rit_uid,FROM `som-nero-phi-jonc101.starr_datalake2018.flowsheet` where inpatient_data_id_coded IN
  (SELECT pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.mar` WHERE order_med_id_coded in --patient received subQ insulin
  (SELECT order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` 
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (ordering_mode_c) = 2 -- inpatient
       AND med_route = 'Subcutaneous') --and subQ
     AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push')
   AND (mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND dose_unit_c = 5 -- "units", not an infusion (not units/hr)
   AND sig <> "0-10"
   AND sig IS NOT NULL 
   AND sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
))
AND row_disp_name LIKE "Weight"
AND num_value1 IS NOT NULL --numeric value exists
AND DATE_DIFF(DATE(flow.recorded_time_jittered), (dem.birth_date_jittered), YEAR) >= 18
-- AND num_value1*0.028 < 45
ORDER BY KG


--
-- wt, time, age table for adults who got subQ insulin with wt > 45kg and < doubling in weight between time in flowsheet and "most recent wt"
SELECT dem.rit_uid, DATE_DIFF(DATE(flow.recorded_time_jittered), (dem.birth_date_jittered), YEAR) as ageYears, flow.row_disp_name, flow.meas_value, flow.recorded_time_jittered, (flow.num_value1*0.028) AS KG, dem.recent_wt_in_kgs, (dem.recent_wt_in_kgs-(flow.num_value1*0.028)) as wt_diff, ((dem.recent_wt_in_kgs-(flow.num_value1*0.028))/dem.recent_wt_in_kgs) as wt_diff_percent, bmi FROM `som-nero-phi-jonc101.starr_datalake2018.flowsheet` AS flow
INNER JOIN `som-nero-phi-jonc101.starr_datalake2018.demographic` AS dem ON dem.rit_uid = flow.rit_uid 
WHERE dem.rit_uid IN (SELECT rit_uid,FROM `som-nero-phi-jonc101.starr_datalake2018.flowsheet` where inpatient_data_id_coded IN
  (SELECT pat_enc_csn_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.mar` WHERE order_med_id_coded in --patient received subQ insulin
  (SELECT order_med_id_coded FROM `som-nero-phi-jonc101.starr_datalake2018.order_med` 
	     WHERE UPPER(med_description) LIKE '%INSULIN%'-- insulin ordered)
       AND (ordering_mode_c) = 2 -- inpatient
       AND med_route = 'Subcutaneous') --and subQ
     AND (mar_action) IN ('Bolus', 'Complete', 'Completed', 'Given', 'Push')
   AND (mar_action) NOT IN ('Bag Removal', 'Canceled Entry', 'Due', 'Existing Bag', 'Infusion Restarted', 'Infusion Started', 'Infusion Stopped', 'New Bag', 'Patch Removal', 'Patient\'s Own Med', 'Patient/Family Admin', 'Paused', 'Pending', 'Rate Changed', 'Rate Verify', 'Pump%', 'See Anesthesia Record', 'Self Administered Med', 'See Override Pull','Refused', 'Held', 'Stopped', 'Missed')
   AND dose_unit_c = 5 -- "units", not an infusion (not units/hr)
   AND sig <> "0-10"
   AND sig IS NOT NULL 
   AND sig NOT LIKE "%.%" -- removes any partial unit injections (assumed to be pump)
   AND infusion_rate IS NULL -- infusion_rate assumed to signify pump pt
))
AND row_disp_name LIKE "Weight"
AND UPPER(meas_value) NOT LIKE "%W%" -- removes "XweeksXdays"-- presumed misentered data
AND UPPER(meas_value) NOT LIKE "%/%" -- Removes fractions of lbs
AND UPPER(meas_value) NOT LIKE "%GMS%" --Removes gms
AND UPPER(meas_value) NOT LIKE "%LBS%" -- Removes lbs
AND UPPER(meas_value) NOT LIKE "% G%" -- Removes grams 
AND num_value1 IS NOT NULL --numeric value exists
AND (flow.num_value1*0.028) > 45 -- wt > 45kg (99lbs)
AND DATE_DIFF(DATE(flow.recorded_time_jittered), (dem.birth_date_jittered), YEAR) >= 18 -- ADULTS ONLY
AND dem.recent_wt_in_kgs != 0 -- recent wt not equal zero (there are no pts with recent wt = 0 but if I don't do this the percent returns an error)
AND ((dem.recent_wt_in_kgs-(flow.num_value1*0.028))/dem.recent_wt_in_kgs) < 0.5 -- Difference between flowsheet wt and last recorded wt <50%
ORDER BY wt_diff_percent desc



