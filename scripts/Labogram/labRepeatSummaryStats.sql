with
params AS 
(
	select 
		30 as repeatWindowHours, -- How many hours to look back to see if this is a repeat result (a little more than 24 hours, for slight variation in daily labs)
    ['WBC','HGB','PLT',  'NA','K','CL','CO2','BUN','CR','CA','CAION', 'MG','PHOS', 'TP','ALB','TBIL','AST','ALT'] as baseNames,
    'JC1303838' as samplePatientId
),

commonInpatientLabResultRepeats as 
(
  select lr.order_id_coded, base_name, 
    max(prior_lr.result_time) as mostRecentResultTime, -- Could have multiple within lookback window, so just look at most recent one
    -- max(prior_lr.order_id_coded) as mostRecentResultOrderId -- Better indexing based on ID, though no guarantee that database encoded the ids to be chronological order
  from shc_core_2021.lab_result as lr
    join shc_core_2021.lab_result as prior_lr
    using (anon_id, base_name, ordering_mode),
    params
  where ordering_mode = 'Inpatient'
  and base_name in UNNEST(params.baseNames)
  and DATETIME_DIFF(lr.result_time, prior_lr.result_time, HOUR) < params.repeatWindowHours
  --and anon_id = params.samplePatientId
  group by lr.order_id_coded, base_name
),

commonInpatientLabResultRepeatValues as
(
  select 
    lr.anon_id, lr.pat_enc_csn_id_coded, lr.order_id_coded,
    lr.base_name, lr.lab_name, 
    lr.ord_num_value, 
    lr.reference_low, lr.reference_high, lr.result_flag,
    lr.result_time,
    prior_lr.ord_num_value as priorValue,
    prior_lr.result_time as priorResultTime,
    abs(lr.ord_num_value - prior_lr.ord_num_value) as priorValueChange,
    abs(SAFE_CAST(lr.reference_high AS NUMERIC) - SAFE_CAST(lr.reference_low AS NUMERIC)) as referenceRange,
    abs(lr.ord_num_value - prior_lr.ord_num_value) / abs(SAFE_CAST(lr.reference_high AS NUMERIC) - SAFE_CAST(lr.reference_low AS NUMERIC)) as priorValueChangeReferenceScale
  from commonInpatientLabResultRepeats as cilrr
    join shc_core_2021.lab_result as lr
      using (order_id_coded, base_name)
    join shc_core_2021.lab_result as prior_lr
      using (anon_id, base_name),
    params
  where prior_lr.result_time = cilrr.mostRecentResultTime
),

commonInpatientLabResultRepeatStable as
(
  select cilrrv.*,
    cilrrv.priorValueChangeReferenceScale < 1.00 as changeWithinReferenceScale100,
    cilrrv.priorValueChangeReferenceScale < 0.50 as changeWithinReferenceScale050,
    cilrrv.priorValueChangeReferenceScale < 0.25 as changeWithinReferenceScale025,
    cilrrv.priorValueChangeReferenceScale < 0.10 as changeWithinReferenceScale010
  from commonInpatientLabResultRepeatValues as cilrrv
),

commonInpatientLabResultRepeatStableSummary as
(
  select 
    EXTRACT(YEAR from result_time) as resultYear,
    base_name, 
    max(lab_name) as commonLabName,
    min(referenceRange) as minReferenceRange, -- Sometimes have different labs with same base_name, but slightly different description or reference range. Just work off one of them for now
    avg(priorValueChange) as averageValueChange,
    count(*) as nRepeats,
    countif(changeWithinReferenceScale100) / count(*) as percentRepeatsWithinReferenceScale100,
    countif(changeWithinReferenceScale050) / count(*) as percentRepeatsWithinReferenceScale050,
    countif(changeWithinReferenceScale025) / count(*) as percentRepeatsWithinReferenceScale025,
    countif(changeWithinReferenceScale010) / count(*) as percentRepeatsWithinReferenceScale010,
    countif(changeWithinReferenceScale100) as nRepeatWithinReferenceScale100,
    countif(changeWithinReferenceScale050) as nRepeatWithinReferenceScale050,
    countif(changeWithinReferenceScale025) as nRepeatWithinReferenceScale025,
    countif(changeWithinReferenceScale010) as nRepeatWithinReferenceScale010
  from commonInpatientLabResultRepeatStable as cilrrs
  group by
    resultYear, base_name
  order by
    resultYear desc, nRepeats desc, base_name
),

spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

select *
from commonInpatientLabResultRepeatStableSummary
limit 1000