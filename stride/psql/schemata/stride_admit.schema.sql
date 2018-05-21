-- Table: stride_admit
-- Description: Admission summary data.
-- Raw Files:
--  * JChenv3_Admits_Table58.csv.gz
-- Clean Files:
--  * stride_admit_2014_2017.csv.gz
-- CSV Fields:
--  * PAT_ENC_CSN_ANON_ID (e.g. 885413)
--  * PAT_ANON_ID (e.g. 7046823672303)
--  * HSP_ACC_DEID (e.g. 54767284)
--  * SHIFTED_DEATH_DATE (e.g. 02-AUG-2015)
--  * ALIVE_DEAD (e.g. "Deceased")
--  * SHIFTED_ADMIT_DT_TM (e.g. 11-NOV-2015 19:00)
--  * SHIFTED_DISCH_DT_TM (e.g. 05-OCT-2014 12:40)
--  * LOS_DAYS (length of stay in days e.g. 2.08)
--  * DISCH_DEST (discharge destination e.g. "Home")

CREATE TABLE IF NOT EXISTS stride_admit
(
  pat_enc_csn_anon_id BIGINT,
  pat_anon_id BIGINT,
  hsp_acc_deid BIGINT,
  shifted_death_date TIMESTAMP,
  alive_dead TEXT,
  shifted_admit_dt_tm TIMESTAMP,
  shifted_disch_dt_tm TIMESTAMP,
  los_days FLOAT,
  disch_dest TEXT
);
