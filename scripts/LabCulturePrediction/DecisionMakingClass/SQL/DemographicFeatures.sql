select distinct demo.gender,
                demo.canonical_race,
                demo.canonical_ethnicity,
                demo.birth_date_jittered,
                labels.*
from
  conor_db.er_empiric_treatment as labels,
  starr_datalake2018.demographic as demo
where
  labels.jc_uid = demo.rit_uid
order by pat_enc_csn_id_coded, organism