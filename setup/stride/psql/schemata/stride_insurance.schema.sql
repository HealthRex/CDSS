-- Table: stride_insurance
-- Description: Payor for patient PAT_ID on encounter PAT_ENC_CSN_ID.
-- Original Files:
--	* Chen_Insurance_Info_5Yr.csv.gz
--  * Chen_Insurance_Info_Yrs6_8.csv.gz
-- Clean Files:
-- 	* stride_insurance_2008_2014.csv.gz
--  * stride_insurance_2014_2017.csv.gz
-- CSV Fields:
--  * PAT_ID (e.g. 11577528280870)
--  * PAT_ENC_CSN_ID (e.g. 431388)
--  * PAYOR_NAME (e.g. "BLUE SHIELD")
--  * TITLE (e.g. "MANAGED CARE")

CREATE TABLE IF NOT EXISTS stride_insurance
(
  pat_id BIGINT,
  pat_enc_csn_id BIGINT,
  payor_name TEXT,
  title TEXT
);
