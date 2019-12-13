select distinct med.order_med_id_coded,
                med.med_description,
                med.pharm_class_name,
                med.thera_class_name,
                med.order_class,
                med.order_time_jittered_utc as med_order_time,
                labels.*
from
  conor_db.er_empiric_treatment as labels,
  starr_datalake2018.order_med as med
where
  labels.jc_uid = med.jc_uid
  and med.order_time_jittered_utc < labels.order_time_jittered_utc
  and timestamp_add(med.order_time_jittered_utc, INTERVAL 24*365 HOUR) >= labels.order_time_jittered_utc