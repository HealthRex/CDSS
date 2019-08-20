library(dplyr)
library(bigrquery)
project <- "mining-clinical-decisions"
testquery <- "SELECT 
cast ADT.pat_enc_csn_id_coded
FROM
starr_datalake2018.adt AS ADT JOIN  -- Create a shorthand table alias for convenience when referencing
starr_datalake2018.treatment_team AS TT ON ADT.pat_enc_csn_id_coded = TT.pat_enc_csn_id_coded


LIMIT 1000" #the sql query we're trying to run

sql <- "
select 
opCT.jc_uid, 
cast(opCT.pat_enc_csn_id_coded as string) as string_id, 
admit.event_type,  
admit.pat_class, 
admit.effective_time_jittered as emergencyAdmitTime, 
min(opCT.order_inst_jittered) as ctHeadOrderTime,
dc.dx_name,
dc.icd10
from 
datalake_47618.adt as admit, 
datalake_47618.order_proc as opCT,
datalake_47618.diagnosis_code as dc
where admit.event_type_c = 1 -- Admission
and admit.pat_class_c = '112' -- Emergency Services
and TIMESTAMP_ADD(TIMESTAMP(admit.effective_time_jittered), INTERVAL -60 MINUTE) < TIMESTAMP(opCT.order_inst_jittered)
and TIMESTAMP_ADD(TIMESTAMP(admit.effective_time_jittered), INTERVAL 60 MINUTE) >= TIMESTAMP(opCT.order_inst_jittered)
and opCT.proc_code like 'IMGCTH%' -- CT Head orders
and admit.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
and dc.pat_enc_csn_id_coded = admit.pat_enc_csn_id_coded 
and dc.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
group by 
opCT.jc_uid,
opCT.pat_enc_csn_id_coded,
admit.event_type, 
admit.pat_class, 
admit.effective_time_jittered,
dc.dx_name,
dc.icd10
" #sample sql query without patient encounter bug

#download_bq <- function(project, sql){
  tb <- bq_project_query(project, sql)
  tb.dtx <- bq_table_download(tb)
#  return(tb.dtx)
  
#}
data <- download_bq(project,testquery)
