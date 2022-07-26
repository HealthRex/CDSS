-- Find admissions with lactic acidosis within 24 hours of admission, but not in problem list / diagnosis codes???
-- Group by admission service line and DRG or diagnosis

WITH
-- Admission Times and service admitted with Inpatient designation
admissionServiceTime AS
(
    select
      anon_id, pat_enc_csn_id_coded, 
      pat_service_c, pat_service,
      event_time_jittered AS admission_time,
      EXTRACT(YEAR FROM event_time_jittered) as admission_year
    from `shc_core_2021.adt`
    where in_event_type_c = 1 -- Admission
    and base_pat_class_c = 1 -- Inpatient
),
-- 343,361 distinct pat_enc_csn_id_coded

-- Find all lactic acid results
lacticAcidResult AS
(
    select 
      lr.anon_id, lr.pat_enc_csn_id_coded,
      op.order_proc_id_coded, lr.order_time, lr.result_time,
      lr.base_name, lr.lab_name, 
      lr.ord_num_value, lr.result_flag
    from 
      `shc_core_2021.lab_result` as lr
        inner join `shc_core_2021.order_proc` as op on (lr.order_id_coded = op.order_proc_id_coded)
    where
      base_name in ('LACWBL','LAC','LACTATEPOC','SPLACW','PCLAM','LACC')
),

-- Find all Lactic Acidosis Diagnosis Code
lacticAcidDiagnosisCode AS
(  
    select 
      anon_id, pat_enc_csn_id_jittered
      noted_date, start_date,
      poa, present_on_adm, hospital_pl
    from `shc_core_2021.diagnosis` as dc
    where
      icd9 in ('276.2','790.6')
      or
      icd10 in ('E87.2','R79.89')
),

-- Find all admission encounters where lactic acid result is available within 24 hours of admission
-- Consider making this an outer join without the time-range filter, so can apply in a subsequent step
--  to do a single summary query that generates total encounters as well as "lactate checked" encounters.
cohortLacticAcidResult AS
(
  select
      ast.anon_id, ast.pat_enc_csn_id_coded, 
      ast.pat_service_c, ast.pat_service,
      ast.admission_time, ast.admission_year,

      lar.order_proc_id_coded, lar.order_time, lar.result_time,
      lar.base_name, lar.lab_name, 
      lar.ord_num_value, lar.result_flag,
      -- IF(lar.result_time is null, null, DATETIME_DIFF(lar.result_time, ast.admission_time, HOUR)) as hours_until_lactic_acid_result  -- Null check if outer join
      DATETIME_DIFF(lar.result_time, ast.admission_time, HOUR) as hours_until_lactic_acid_result
  from
    admissionServiceTime AS ast
      INNER JOIN lacticAcidResult AS lar 
        USING (anon_id)
  where
    DATETIME_DIFF(lar.result_time, ast.admission_time, HOUR) >= -24 and -- Find admissions where lactic acid result available within +/- 24 hours of admission time
    DATETIME_DIFF(lar.result_time, ast.admission_time, HOUR) <  +24 
),
-- 86,067 distinct pat_enc_csn_ud_coded
-- 26,758 distinct pat_enc_csn_id_coded where result_flag is not null (i.e., abnormal lactate)

-- One row per encounter, with indicator of whether any lactic acid result exists within 24 hours, and if so, if it's abnormal
cohortLacticAcidIndicator AS
(
  select
      anon_id, pat_enc_csn_id_coded, 
      pat_service_c, pat_service,
      admission_time, admission_year,

      min(result_time) as firstLactateResultTime,
      max(result_flag) as anyLactateResultFlag,
  from
    cohortLacticAcidResult
  group by
    anon_id, pat_enc_csn_id_coded, 
    pat_service_c, pat_service,
    admission_time, admission_year
),

-- Summarize counts for admissions with a lactate result within +/- 24 hours and how many of those with abnormal result flags
cohortLacticAcidSummary AS
(
  select
    count(distinct anon_id) as nPatients,
    count(distinct pat_enc_csn_id_coded) as nEncounters,
    countif(firstLactateResultTime is not null) as nEncountersLactateChecked,
    countif(anyLactateResultFlag is not null) as nEncountersLactateAbnormal
  from
    cohortLacticAcidIndicator
),
cohortLacticAcidSummaryByYear AS
(
  select
    admission_year,
    count(distinct anon_id) as nPatients,
    count(distinct pat_enc_csn_id_coded) as nEncounters,
    countif(firstLactateResultTime is not null) as nEncountersLactateChecked,
    countif(anyLactateResultFlag is not null) as nEncountersLactateAbnormal
  from
    cohortLacticAcidIndicator
  group by admission_year
  order by admission_year desc
),
-- 2020 - 8,259 patients, 10,368 encounters where lactate checked within +/- 24 hours of admission. 4,028 of those with an abnormal lactate result.

placeholder AS
(
  select * 
  from `som-nero-phi-jonc101.shc_core_2021.lab_result`
  limit 1
)

select * -- count(distinct pat_enc_csn_id_coded)
from cohortLacticAcidSummaryByYear
limit 1000