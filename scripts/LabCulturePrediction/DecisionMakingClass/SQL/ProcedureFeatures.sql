select distinct proc.order_proc_id_coded,
                proc.order_type,
                proc.proc_code,
                proc.description,
                proc.order_time_jittered_utc as proc_order_time,
                labels.*
from
  conor_db.er_empiric_treatment as labels,
  starr_datalake2018.order_proc as proc
where
  proc.order_type = 'Procedures'
  and labels.jc_uid = proc.jc_uid
  and proc.order_time_jittered_utc < labels.order_time_jittered_utc
  and timestamp_add(proc.order_time_jittered_utc, INTERVAL 24*365 HOUR) >= labels.order_time_jittered_utc
order by pat_enc_csn_id_coded, organism, proc_order_time