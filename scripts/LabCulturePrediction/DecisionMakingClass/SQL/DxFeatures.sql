select distinct dx.dx_id,
                dx.dx_name,
                dx.timestamp_utc as dx_time,
                labels.*
from
  conor_db.er_empiric_treatment as labels,
  starr_datalake2018.diagnosis_code as dx
where
  labels.jc_uid = dx.jc_uid
  and labels.pat_enc_csn_id_coded <> dx.pat_enc_csn_id_coded
  and dx.timestamp_utc < labels.order_time_jittered_utc
  and timestamp_add(dx.timestamp_utc, INTERVAL 24*365 HOUR) >= labels.order_time_jittered_utc
order by pat_enc_csn_id_coded, organism, dx_time