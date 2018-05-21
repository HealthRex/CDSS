-- Table: stride_patient_encounter
-- Description: Insurance and admit vitals for encounter pat_enc_csn_id.
-- Original Files:
--  * Chen_Active_Vitals.csv.gz
--	* Chen_Insurance_Info_5Yr.csv.gz
--  * Chen_Insurance_Info_Yrs6_8.csv.gz
-- Clean Files:
--  * stride_admit_vitals.csv.gz
-- 	* stride_insurance_2008_2014.csv.gz
--  * stride_insurance_2014_2017.csv.gz
-- CSV Fields:
--  * "PAT_ID" (e.g. 11577528280870)
--  * "PAT_ENC_CSN_ID" (e.g. 431388)
--  * PAYOR_NAME (e.g. "BLUE SHIELD")
--  * TITLE (e.g. "MANAGED CARE")
--  * "BP_SYSTOLIC" (e.g. 120)
--  * "BP_DIASTOLIC" (e.g. 80)
--  * "TEMPERATURE" (e.g. 98.6)
--  * "PULSE" (e.g. 100)
--  * "RESPIRATIONS" (e.g. 15)

CREATE TABLE IF NOT EXISTS stride_patient_encounter
(
  pat_id BIGINT,
  pat_enc_csn_id BIGINT,
  payor_name TEXT,
  title TEXT,
  bp_systolic INTEGER,
  bp_diastolic INTEGER,
  temperature FLOAT,
  pulse INTEGER,
  respirations INTEGER
);
