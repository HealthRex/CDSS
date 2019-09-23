select distinct labels.jc_uid, labels.pat_enc_csn_id_coded, labels.emergencyAdmitTime, labels.tpaAdminTime, med.pat_enc_csn_id_coded as med_enc,
                med.order_time_jittered, med.start_time_jittered, med.end_time_jittered, med.med_description
from
(select 
  op.jc_uid, op.pat_enc_csn_id_coded, inpatient.event_id_coded, enc.inpatient_data_id_coded,
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
  op.jc_uid, op.pat_enc_csn_id_coded, inpatient.event_id_coded, enc.inpatient_data_id_coded,
  admit.event_type, admit.pat_class, admit.effective_time_jittered, 
  om.med_description,
  inpatient.pat_class
order by emergencyAdmitTime) labels
LEFT JOIN
  (select jc_uid, pat_enc_csn_id_coded, order_time_jittered, start_time_jittered, end_time_jittered, med_description
  from starr_datalake2018.order_med
  where med_description like '%ASPIRIN%') med
ON med.jc_uid = labels.jc_uid
WHERE med.order_time_jittered < labels.tpaAdminTime
ORDER BY labels.jc_uid, labels.pat_enc_csn_id_coded, med.order_time_jittered

