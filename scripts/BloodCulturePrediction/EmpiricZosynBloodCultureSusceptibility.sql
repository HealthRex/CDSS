WITH ZosynBloodCxResults as
( select distinct 
      EXTRACT(YEAR FROM om.order_time_jittered) as orderYear,
      om.jc_uid, om.pat_enc_csn_id_coded,
      om.order_med_id_coded, om.order_time_jittered as abxOrderTime, 
      op.order_proc_id_coded, op.order_time_jittered as cultureOrderTime, 
      cs.organism, cs.antibiotic, cs.suscept
  from `starr_datalake2018.order_med` as om 
      join `starr_datalake2018.order_proc` as op 
          on om.pat_enc_csn_id_coded = op.pat_enc_csn_id_coded
      join `starr_datalake2018.culture_sensitivity` as cs
          on op.order_proc_id_coded = cs.order_proc_id_coded
  where op.description like 'BLOOD CULT%'
  and (om.med_description like '%ZOSYN%' or om.med_description like 'PIPERACILLIN%')
  and Abs(TIMESTAMP_DIFF(op.order_time_jittered,om.order_time_jittered, MINUTE)) < 60 -- 1 hour = 60 minutes
) 

select susceptibleCounts.orderYear, susceptibleCounts.antibiotic, 
    susceptibleCounts.patientCount as susceptiblePatients, totalCounts.patientCount as totalPatients, 
    susceptibleCounts.patientCount / totalCounts.patientCount as percentSusceptiblePatients,
    1-(susceptibleCounts.patientCount / totalCounts.patientCount) as percentNotSusceptiblePatients,
    susceptibleCounts.abxCount as susceptibleAbx, totalCounts.abxCount as totalAbx, 
    susceptibleCounts.abxCount / totalCounts.abxCount as percentSusceptibleAbx,
    1-(susceptibleCounts.abxCount / totalCounts.abxCount) as percentNotSusceptibleAbx
from 
(
  select orderYear, antibiotic, suscept, count(distinct jc_uid) as patientCount, count(distinct order_med_id_coded) as abxCount, count(distinct order_proc_id_coded) as cultureCount
  from ZosynBloodCxResults
  where suscept = 'Susceptible'
  group by orderYear, antibiotic, suscept
) as susceptibleCounts
join
(
  select orderYear, antibiotic, count(distinct jc_uid) as patientCount, count(distinct order_med_id_coded) as abxCount, count(distinct order_proc_id_coded) as cultureCount
  from ZosynBloodCxResults
  group by orderYear, antibiotic
) as totalCounts
  on susceptibleCounts.antibiotic = totalCounts.antibiotic and susceptibleCounts.orderYear = totalCounts.orderYear
order by orderYear, antibiotic   
