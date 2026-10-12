select 
  opCT.jc_uid, 
  opCT.pat_enc_csn_id_coded, 
  admit.event_type, 
  admit.pat_class, 
  admit.effective_time_jittered as emergencyAdmitTime, 
  min(opCT.order_inst_jittered) as ctHeadOrderTime
from 
  datalake_47618.adt as admit, 
  datalake_47618.order_proc as opCT

where admit.event_type_c = 1 -- Admission
and admit.pat_class_c = '112' -- Emergency Services
and TIMESTAMP_ADD(TIMESTAMP(admit.effective_time_jittered), INTERVAL -60 MINUTE) < TIMESTAMP(opCT.order_inst_jittered)
and TIMESTAMP_ADD(TIMESTAMP(admit.effective_time_jittered), INTERVAL 60 MINUTE) >= TIMESTAMP(opCT.order_inst_jittered)
and opCT.proc_code like 'IMGCTH%' -- CT Head orders
and admit.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
group by 
  opCT.jc_uid,
  opCT.pat_enc_csn_id_coded,
  admit.event_type, 
  admit.pat_class, 
  admit.effective_time_jittered
