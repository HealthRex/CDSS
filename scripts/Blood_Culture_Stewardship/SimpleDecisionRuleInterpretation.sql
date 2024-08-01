-- Summarize 2x2 stats for different blood culture result subsets
--  based on total populations but also established or proposed simple decision rules
--  (e.g., SIRS criteria)
-- Define using common table expressions (CTEs)
-- Use the params options at the head to define different filters

WITH 
-- Set modifiable query parameters in one place here, so can abstract the subsequent queries structures below
-- Replace values to those of different cohorts of interest
-- https://stackoverflow.com/questions/29759628/setting-big-query-variables-like-mysql
-- https://medium.com/google-cloud/how-to-work-with-array-and-structs-in-bigquery-9c0a2ea584a6
params AS 
(
  select 
    [2022,2023]
      as cohortYears      -- Restrict years of reporting

),



--------------------------------------------------------------------
-- Add / modify columns
--------------------------------------------------------------------


-- Rename for general filters and subsequent comparisons
--  Eliminate duplicates (keep unit of observation at order level) (only track one IV antibiotic)
bloodCultureCohort AS
(
  SELECT DISTINCT
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    blood_culture_order_datetime,
    order_year,
    ed_arrival_datetime,
    positive_blood_culture,
    positive_blood_culture_in_week,
    earliest_iv_antibiotic_datetime,
    age,
    min_heartrate,
    max_heartrate,
    avg_heartrate,
    median_heartrate,
    min_resprate,
    max_resprate,
    avg_resprate,
    median_resprate,
    min_temp,
    max_temp,
    avg_temp,
    median_temp,
    min_sysbp,
    max_sysbp,
    avg_sysbp,
    median_sysbp,
    min_diasbp,
    max_diasbp,
    avg_diasbp,
    median_diasbp,
    min_wbc,
    max_wbc,
    avg_wbc,
    median_wbc,
    min_neutrophils,
    max_neutrophils,
    avg_neutrophils,
    median_neutrophils,
    min_lymphocytes,
    max_lymphocytes,
    avg_lymphocytes,
    median_lymphocytes,
    min_hgb,
    max_hgb,
    avg_hgb,
    median_hgb,
    min_plt,
    max_plt,
    avg_plt,
    median_plt,
    min_na,
    max_na,
    avg_na,
    median_na,
    min_hco3,
    max_hco3,
    avg_hco3,
    median_hco3,
    min_bun,
    max_bun,
    avg_bun,
    median_bun,
    min_cr,
    max_cr,
    avg_cr,
    median_cr,
    min_lactate,
    max_lactate,
    avg_lactate,
    median_lactate,
    min_procalcitonin,
    max_procalcitonin,
    avg_procalcitonin,
    median_procalcitonin
  FROM `som-nero-phi-jonc101.blood_culture_stewardship.cohort` as cohort, params
  WHERE order_year in UNNEST(params.cohortYears)
),

-- Rescale or normalize some fields that may use different units
bloodCultureCohortRescale AS
(
  SELECT *, 
    CASE WHEN max_wbc > 500 THEN max_wbc/1000 -- Some values are stored as thousands, though most are not. Scale these back
    ELSE max_wbc END as max_wbcRescale,

    CASE WHEN min_wbc > 500 THEN min_wbc/1000 -- Some values are stored as thousands, though most are not. Scale these back
    ELSE min_wbc END as min_wbcRescale,

    -- Looks like all available temperatures are in Farhanheit already, as minimum value is 90

  FROM bloodCultureCohort
),

--  Add in derivative features for SIRS and other criteria
--  That can be used as breakpoints for decision rules
bloodCultureCohortWithSingleCriteria AS
(
    SELECT *,
      -- SIRS Criteria
      CASE WHEN(min_temp < 96.8) or (max_temp > 100.4) THEN 1 ELSE 0 END as sirsTemp, -- 36 and 38 Celsius thresholds. Beware that vitals may be recorded in different units. Assume Farhanheit for now
      CASE WHEN(max_heartrate > 90) THEN 1 ELSE 0 END as sirsHeartRate,
      CASE WHEN(max_resprate > 20) THEN 1 ELSE 0 END as sirsRespRate, -- Also based on PaCO2, but not as readily available
      CASE WHEN(min_wbcRescale < 4.0) or (max_wbcRescale > 12.0) THEN 1 ELSE 0 END as sirsWBC, -- Should also be based on >10% bands. *TO DO* Add on later

      -- Hypotension / Hypoperfusion / Unstable indicators
      CASE WHEN(min_sysbp < 90) THEN 1 ELSE 0 END as lowBP,
      CASE WHEN(max_lactate > 2.0) THEN 1 ELSE 0 END as highLactate,

      CASE WHEN(max_procalcitonin > 0.5) THEN 1 ELSE 0 END as highProcalcitonin, -- Some reference ranges use 0.25 and others use 5 or 10, suggesting different units for representation that should be standardized

      -- Additional criteria suggested by previous Shapiro study decision rule
      -- https://doi.org/10.1016/j.jemermed.2008.04.001
      CASE WHEN(max_cr > 2.0) THEN 1 ELSE 0 END as shapiroHighCr,
      CASE WHEN(max_temp > 101.0) THEN 1 ELSE 0 END as shapiroHighTemp,
      CASE WHEN(max_neutrophils > 80) THEN 1 ELSE 0 END as shapiroHighNeutrophils,
      CASE WHEN(max_wbc > 18) THEN 1 ELSE 0 END as shapiroHighWBC,
      CASE WHEN(min_plt < 150) THEN 1 ELSE 0 END as shapiroLowPlt,
      CASE WHEN(age > 65) THEN 1 ELSE 0 END as shapiroHighAge

    FROM
      bloodCultureCohortRescale
),
bloodCultureCohortWithDerivatives AS
(
    SELECT *, 
      sirsTemp + sirsHeartRate + sirsRespRate + sirsWBC as sirsScore,
      (sirsTemp + sirsHeartRate + sirsRespRate + sirsWBC) >= 2 as sirsPositive,
      (sirsTemp + sirsHeartRate + sirsRespRate + sirsWBC) >= 1 as anySIRS,
      (sirsTemp + sirsHeartRate + sirsRespRate + sirsWBC) >= 2 or (lowBP + highLactate) >= 1 as sirs2orLowBPorHighLactate,
      (sirsTemp + sirsHeartRate + sirsRespRate + sirsWBC + lowBP + highLactate) >= 1 as anySIRSorLowBPorHighLactate,
      (shapiroHighTemp + shapiroHighAge + lowBP + shapiroHighWBC + shapiroHighNeutrophils + shapiroLowPlt + shapiroHighCr) >= 2 as shapiroCriteria2orMore,
      (shapiroHighTemp + shapiroHighAge + lowBP + shapiroHighWBC + shapiroHighNeutrophils + shapiroLowPlt + shapiroHighCr) >= 1 as shapiroCriteria1orMore
    FROM
      bloodCultureCohortWithSingleCriteria
),


--------------------------------------------------------------------
-- Aggregate Results
--------------------------------------------------------------------


-- Overall culture positivity rate summary
culturePositiveRate AS
(
  SELECT 
    avg(positive_blood_culture) as positiveRate,
    avg(positive_blood_culture | positive_blood_culture_in_week) as positiveRateAnyWithinWeek,
    count(distinct anon_id) as nPatients,
    count(distinct order_proc_id_coded) as nOrders,
    count(positive_blood_culture) as nResults,
    sum(positive_blood_culture | positive_blood_culture_in_week) as nPositiveWithinWeek,
    count(positive_blood_culture) - sum((positive_blood_culture | positive_blood_culture_in_week)) as nNegativeWithinWeek
  FROM 
    bloodCultureCohortWithDerivatives
),

-- Aggregate description, broken down by (Diagnosis) positive vs. negative cases
cohortDescriptionByCultureResult AS
(
  SELECT
    (positive_blood_culture | positive_blood_culture_in_week) as anyPositiveWithinWeek, -- Take the "or" of this culture being positive, or any within next (small fraction of the latter)
    count(distinct anon_id) as nPatients,
    count(distinct order_proc_id_coded) as nOrders,

    avg(min_temp) as avgMinTemp,
    avg(max_temp) as avgMaxTemp,
    avg(min_heartrate) as avgMinHeartRate,
    avg(max_heartrate) as avgMaxHeartRate,
    avg(min_sysbp) as avgMinSysBP,
    avg(max_sysbp) as avgMaxSysBP,
    avg(min_diasbp) as avgMinDiasBP,
    avg(max_diasbp) as avgMaxDiasBP,
    avg(min_resprate) as avgMinRespRate,
    avg(max_resprate) as avgMaxRespRate,

    avg(min_wbc) as avgMinWBC,
    avg(max_wbc) as avgMaxWBC,
    avg(min_neutrophils) as avgMinNeutrophils,
    avg(max_neutrophils) as avgMaxNeutrophils,
    avg(min_lymphocytes) as avgMinLymphocytes,
    avg(max_lymphocytes) as avgMaxLymphocytes,

    avg(min_hgb) as avgMinHgb,
    avg(max_hgb) as avgMaxHgb,
    avg(min_plt) as avgMinPlt,
    avg(max_plt) as avgMaxPlt,
    avg(min_na) as avgMinNa,
    avg(max_na) as avgMaxNa,
    avg(min_hco3) as avgMinHCO3,
    avg(max_hco3) as avgMaxHCO3,
    avg(min_bun) as avgMinBUN,
    avg(max_bun) as avgMaxBUN,
    avg(min_cr) as avgMinCr,
    avg(max_cr) as avgMaxCr,
    avg(min_lactate) as avgMinLactate,
    avg(max_lactate) as avgMaxLactate,
    avg(min_procalcitonin) as avgMinProcalcitonin,
    avg(max_procalcitonin) as avgMaxProcalcitonin,

    avg(sirsTemp) as rateSIRSTemp,
    avg(sirsHeartRate) as rateSIRSHeartRate,
    avg(sirsRespRate) as rateSIRSRespRate,
    avg(sirsWBC) as rateSIRSWBC,
    avg(sirsScore) as avgSIRSScore


  FROM 
    bloodCultureCohortWithDerivatives
  GROUP BY
    anyPositiveWithinWeek
),

-- Culture (Diagnosis) Positive Rate broken down by a (Test) decision criteria
-- Forms the basis for a 2x2 contingency table of "Test" vs. "Diagnosis"
culturePositiveSummaryByDecisionCriteria AS
(
  SELECT 
    sirsPositive as decisionCriteria,
    avg(positive_blood_culture) as positiveRate,
    avg(positive_blood_culture | positive_blood_culture_in_week) as positiveRateAnyWithinWeek,
    count(distinct anon_id) as nPatients,
    count(distinct order_proc_id_coded) as nOrders,
    count(positive_blood_culture) as nResults,
    sum(positive_blood_culture | positive_blood_culture_in_week) as nPositiveWithinWeek,
    count(positive_blood_culture) - sum((positive_blood_culture | positive_blood_culture_in_week)) as nNegativeWithinWeek
  FROM 
    bloodCultureCohortWithDerivatives
  GROUP BY
    sirsPositive  -- Replace this with other criteria to consider
),

-- Calculate diagnostic stats from the 2x2 table info
culturePositiveDiagnosticStatsByDecisionCriteria AS
(
    SELECT
      testPos.positiveRate as positivePredictiveValue,
      (1-testNeg.positiveRate) as negativePredictiveValue,
      (testPos.nPositiveWithinWeek / (testPos.nPositiveWithinWeek+testNeg.nPositiveWithinWeek)) as sensitivity,
      (testNeg.nNegativeWithinWeek / (testNeg.nNegativeWithinWeek+testPos.nNegativeWithinWeek)) as specificity
    FROM
      culturePositiveSummaryByDecisionCriteria AS testPos,
      culturePositiveSummaryByDecisionCriteria AS testNeg
    WHERE
      testPos.decisionCriteria AND
      NOT testNeg.decisionCriteria
),

spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

-- select * from bloodCultureCohortWithDerivatives
-- select * from culturePositiveRate
-- select * from cohortDescriptionByCultureResult
-- select * from culturePositiveSummaryByDecisionCriteria
select * from culturePositiveDiagnosticStatsByDecisionCriteria

limit 100  



