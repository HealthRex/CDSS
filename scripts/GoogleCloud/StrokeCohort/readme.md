[Google Big Query Stroke](https://console.cloud.google.com/bigquery?project=mining-clinical-decisions&j=bq:US:bquxjob_341287ce_16997f447ea&page=queryresults)

## Diagnostic Pathways 
select 
    op.jc_uid, op.pat_enc_csn_id_coded, 
    admit.event_type, admit.pat_class, admit.effective_time_jittered as emergencyAdmitTime, 
    min(opCT.order_inst_jittered) as ctHeadOrderTime,
    om.med_description as tpaDescription, min(om.order_time_jittered) as tpaOrderTime,
    min(mar.taken_time_jittered) as tpaAdminTime,
    inpatient.pat_class as inptClass, min(inpatient.effective_time_jittered) as inpatientAdmitTime
    from 
    datalake_47618.order_proc as op, 
    datalake_47618.adt as admit, 
    datalake_47618.order_proc as opCT,
    datalake_47618.order_med as om,
    datalake_47618.mar as mar,
    datalake_47618.adt as inpatient
    where op.display_name like 'Patient on TPA%'
    and op.pat_enc_csn_id_coded = admit.pat_enc_csn_id_coded
    and op.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
    and op.pat_enc_csn_id_coded = om.pat_enc_csn_id_coded
    and op.pat_enc_csn_id_coded = inpatient.pat_enc_csn_id_coded
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
  ))



## Emergency Department 

SQL Query 2
		- given those people describe them 
		- look at diagnosis codes (top 5 diagnosis codes) 
		- demographics 
		- common prescribed 24 hours 
		- top 10 lab tests (lab_result) 


## Communicating with Susan Weber to Get Data 

