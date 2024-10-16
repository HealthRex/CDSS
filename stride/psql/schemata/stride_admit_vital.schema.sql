-- Table: stride_admit_vitals
-- Description: Vitals measured for pat_anon_id at time of admission.
-- Raw Files:
--  * Chen_Active_Vitals.csv.gz
-- Clean Files:
--  * stride_admit_vitals.csv.gz
-- CSV Fields:
--  * "PAT_ID" (e.g. 11577528280870)
--  * "PAT_ENC_CSN_ID" (e.g. 431388)
--  * "BP_SYSTOLIC" (e.g. 120)
--  * "BP_DIASTOLIC" (e.g. 80)
--  * "TEMPERATURE" (e.g. 98.6)
--  * "PULSE" (e.g. 100)
--  * "RESPIRATIONS" (e.g. 15)

CREATE TABLE IF NOT EXISTS stride_admit_vital
(
  pat_id BIGINT,
  pat_enc_csn_id BIGINT,
  bp_systolic INTEGER,
  bp_diastolic INTEGER,
  temperature FLOAT,
  pulse INTEGER,
  RESPIRATIONS INTEGER
);
