select mg.name, count(distinct jc_uid) as patientCount, count(*) accessCount
from
(
  select datetime_diff(al.access_time_jittered, cohort.tpaAdminTime, MINUTE) as accessTimeDiff, 
    *
  from
  (
    select 
      op.jc_uid, op.pat_enc_csn_id_coded,
      admit.event_type, admit.pat_class, admit.effective_time_jittered as emergencyAdmitTime, 
      min(opCT.order_inst_jittered) as ctHeadOrderTime,
      om.med_description as tpaDescription, min(om.order_time_jittered) as tpaOrderTime,
      min(mar.taken_time_jittered) as tpaAdminTime,
      inpatient.pat_class as inptClass, min(inpatient.effective_time_jittered) as inpatientAdmitTime
    from 
      starr_datalake2018.order_proc as op, 
      starr_datalake2018.adt as admit, 
      starr_datalake2018.order_proc as opCT,
      starr_datalake2018.order_med as om,
      starr_datalake2018.mar as mar,
      starr_datalake2018.adt as inpatient,
      starr_datalake2018.encounter as enc
    where op.display_name like 'Patient on TPA%'
      and op.pat_enc_csn_id_coded = admit.pat_enc_csn_id_coded
      and op.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
      and op.pat_enc_csn_id_coded = om.pat_enc_csn_id_coded
      and op.pat_enc_csn_id_coded = inpatient.pat_enc_csn_id_coded
      and op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded
      and om.order_med_id_coded = mar.order_med_id_coded
      and admit.event_type_c = 1 -- Admission
      and admit.pat_class_c = '112' -- Emergency Services
      and opCT.proc_code like 'IMGCTH%' -- CT Head orders
      and om.medication_id = 86145 -- ALTEPLASE 100mg infusion
      and inpatient.pat_class_c = '126' -- Inpatient
    group by 
      op.jc_uid, op.pat_enc_csn_id_coded, 
      admit.event_type, admit.pat_class, admit.effective_time_jittered, 
      om.med_description,
      inpatient.pat_class
    order by emergencyAdmitTime
  ) as cohort
  join `starr_access_log.shc_access_log_de` as al on cohort.jc_uid  = al.rit_uid 
where datetime_diff(al.access_time_jittered, cohort.tpaAdminTime, MINUTE) >= -360 
  and datetime_diff(al.access_time_jittered, cohort.tpaAdminTime, MINUTE) < 0
) as cohortAccessLog
join `starr_access_log.access_log_metric` as alm using (metric_id)
join `starr_access_log.zc_metric_group` as mg using (metric_group_c)
group by mg.name
order by patientCount desc