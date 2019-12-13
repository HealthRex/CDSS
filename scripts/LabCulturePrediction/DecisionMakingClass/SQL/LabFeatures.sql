select distinct lab.order_proc_id_coded,
                lab.order_type,
                lab.proc_code,
                lab.order_time_jittered_utc as lab_order,
                labels.*
from
  conor_db.er_empiric_treatment as labels,
  starr_datalake2018.order_proc as lab
where
  lab.order_type = 'Lab'
  and labels.jc_uid = lab.jc_uid
  and lab.order_time_jittered_utc < labels.order_time_jittered_utc
  and timestamp_add(lab.order_time_jittered_utc, INTERVAL 24*365 HOUR) >= labels.order_time_jittered_utc
