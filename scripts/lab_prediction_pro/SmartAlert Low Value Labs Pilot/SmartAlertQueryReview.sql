-- Queries to extract out results of Low Value Labs SmartAlert pilot RCT

WITH 
-- Set modifiable query parameters in one place here, so can abstract the subsequent queries structures below
-- Replace values to those of different cohorts of interest
-- https://stackoverflow.com/questions/29759628/setting-big-query-variables-like-mysql
-- https://medium.com/google-cloud/how-to-work-with-array-and-structs-in-bigquery-9c0a2ea584a6
params AS
(
  select
    'SHC#6051' as randomization_concept_id,
    '1' as flag_treatment,
    '2' as flag_control,
    ['B3', 'C3', 'M7', 'L7', '1%WEST%', '2%NORTH%', '2%WEST%', '3%WEST%'] as target_department_units,
    DATE('2024-08-15') as study_start_date,
    DATE('2025-03-15') as study_end_date,
    ['SHC AIML LAB CBC STABILITY BASE - LOUD PILOT', 'SHC AIML LAB CBC STABILITY BASE - SILENT'] as alert_descriptions,
    'SHC AIML LAB CBC STABILITY BASE - SILENT' as alert_description_silent,
    28 as followup_hours
),

-- See which encounters have been randomized to intervention vs. control?
random_flag AS
(
  SELECT anon_id, pat_enc_csn_id_coded, smrtdta_elem_value AS random_flag 
  FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_smrtdta`, params
  WHERE concept_id = params.randomization_concept_id -- Move to separate parameter list
),

-- Look for any discharges from the units of interest (note that this misses patients who were on those units at different times but moved to a different unit for discharge)
discharges_selected AS
(
  SELECT anon_id, pat_enc_csn_id_coded, effective_time_jittered, department_name 
  FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_adt`
    INNER JOIN `som-nero-phi-jonc101-secure.shc_core_updates.shc_dep_map` USING(department_id) 
    INNER JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map_2025-04-15` USING (anon_id), -- Specific dated mapping table could become out of date?
    params
    WHERE event_type = 'Discharge' AND UPPER(department_name) LIKE ANY UNNEST(params.target_department_units)
    AND (effective_time_jittered - INTERVAL jitter DAY) BETWEEN params.study_start_date AND params.study_end_date
),

-- Look for any admission events
admissions AS
(
  SELECT anon_id, pat_enc_csn_id_coded, effective_time_jittered 
  FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_adt` 
  WHERE event_type = 'Admission'
),

-- Match Admission with Discharge events to calculate encounter durations
-- ???This may be fraught, as some ADT data is confusing in how it tracks encounters (not directly corresponding to hospitalization if patient goes in and out of OR or other procedures)
hospital_stays_selected AS
(
  SELECT anon_id, pat_enc_csn_id_coded, adm.effective_time_jittered AS adm_time, dis.effective_time_jittered AS dis_time, department_name,
    DATETIME_DIFF(dis.effective_time_jittered, adm.effective_time_jittered, DAY)+1 AS duration, --for normalization
    DATETIME_DIFF(dis.effective_time_jittered, adm.effective_time_jittered, MINUTE)/60 AS los_hours --for secondary outcome
  FROM admissions adm 
  INNER JOIN discharges_selected dis USING (anon_id, pat_enc_csn_id_coded)
),

-- Find all alert records for the SmartAlert of interest across the encounters in the unit discharges? (May be issue with repeated alerts)
alerts_cbc AS
(
  SELECT DISTINCT anon_id, pat_enc_csn_id_coded, alt_id_coded, alert_desc, his.update_date_jittered 
  FROM `som-nero-phi-jonc101-secure.shc_core_updates.shc_alert` alt 
  INNER JOIN `som-nero-phi-jonc101-secure.shc_core_updates.shc_alert_history` his USING (anon_id, alt_id_coded)
  INNER JOIN hospital_stays_selected USING (anon_id, pat_enc_csn_id_coded),
  params
  WHERE alert_desc IN UNNEST(params.alert_descriptions)
),

-- Looking for number of lab orders like "%CBC%" with a "HGB" result within 28 hours of an alert firing
-- ???Double check if separate subquery for just CBC results and try joining
num_cbc_orders_alert AS
(
  SELECT a.anon_id, a.pat_enc_csn_id_coded, alt_id_coded, alert_desc, update_date_jittered, 
    COUNT(base_name) AS cbc_count -- Counts number of base names? Could have multiple counts, but filter below screens to only 'HGB' exact match?
  FROM alerts_cbc a, params
  LEFT OUTER JOIN `som-nero-phi-jonc101-secure.shc_core_updates.shc_lab_result` l 
    ON a.anon_id = l.anon_id AND a.pat_enc_csn_id_coded = l.pat_enc_csn_id_coded
    AND UPPER(group_lab_name) LIKE '%CBC%' AND base_name = 'HGB' 
    AND l.result_time_jittered BETWEEN a.update_date_jittered AND a.update_date_jittered + INTERVAL params.followup_hours HOUR
    -- Look for labs that RESULT within 28 hours of alert firing (maybe should be collected, not resulted, otherwise catching some cases where got collected just before order? Fatemeh A said she tried "taken_time" instead, and didn't make much difference)
  GROUP BY a.anon_id, pat_enc_csn_id_coded, alt_id_coded, alert_desc, update_date_jittered
),

-- Subset results based on randomization flag.
-- If get all of the "Silent" fires, isn't this counting q6hours for those patients, even if no one ever tried to order anything?
--  May need to look to actual CBC order entry (order_proc) for the silent ones to show someone actually tried to order something (vs. loud that should have only triggered if someone actually attempted an order)?
--??? Double check if just use random flag and only "Silent" alerts (should happen at same time as loud alerts)
alertStudyResults AS
(
  SELECT mrn, anon_id, pat_enc_csn_id_coded, alt_id_coded, alert_desc, update_date_jittered - INTERVAL jitter DAY AS update_date, cbc_count, random_flag.random_flag 
  FROM num_cbc_orders_alert INNER JOIN random_flag USING (anon_id, pat_enc_csn_id_coded)
  INNER JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map_2025-04-15` USING (anon_id),
  params
  WHERE NOT (alert_desc = params.alert_description_silent AND random_flag.random_flag = params.flag_treatment) 
  -- Is this getting intervention or control??? Or screens out the "silent" alerts for the "loud" implementation, to avoid confusion?
  ORDER BY update_date
)
/*
select count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEnc, count(*) as altCount
from hospital_stays_selected
where los_hours > 72
limit 100
*/

select alert_desc, count(distinct mrn) as nPatients, count(distinct pat_enc_csn_id_coded) as nEnc, count(*) as altCount
from alertStudyResults
group by alert_desc
limit 100


/*
Here’s the code for analysis: 

dd = pd.read_gbq(f'SELECT * FROM `som-nero-phi-jonc101-secure.jyx_db.SmartAlertMay12`', progress_bar_type='tqdm')
dd['cbc_binary'] = dd['cbc_count']>0
treatment = dd[dd['random_flag'] == '1']
control = dd[dd['random_flag'] == '2']

mean_cbc_count_treatment = np.mean(treatment['cbc_count'])
mean_cbc_count_control = np.mean(control['cbc_count'])
print(f'Mean_cbc_count_treament = {mean_cbc_count_treatment:.2f}, Mean_cbc_count_control = {mean_cbc_count_control:.2f}, Percentage reduction = {(mean_cbc_count_control - mean_cbc_count_treatment)/mean_cbc_count_control * 100:.2f}%')
statistic, p_value = stats.ttest_ind(list(treatment['cbc_count']), list(control['cbc_count']))
print(f't-statistic = {statistic:.2f}, p_value = {p_value:.3f}')
*/