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
      left join `starr_datalake2018.culture_sensitivity` as cs -- Outer join to catch blood culture orders that don't yield any bugs/susceptibility results
          on op.order_proc_id_coded = cs.order_proc_id_coded
  where op.description like 'BLOOD CULT%'
  and (om.med_description like '%ZOSYN%' or om.med_description like 'PIPERACILLIN%')
  and Abs(TIMESTAMP_DIFF(op.order_time_jittered,om.order_time_jittered, MINUTE)) < 60 -- 1 hour = 60 minutes
) 

select orderYear, organism, count(distinct jc_uid) patientCount, count(distinct order_med_id_coded) abxCount, count(distinct order_proc_id_coded) as cultureCount
from ZosynBloodCxResults
group by orderYear, organism
order by orderYear, count(distinct order_med_id_coded) desc
