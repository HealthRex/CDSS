-- Table: stride_dx
-- Description: Diagnoses for patient pat_id in encounter pat_enc_csn_id.
-- Original Files:
--	* Chen_DX_List_5Yr.csv.gz
--  * Chen_Dx_List_Yrs6_8.csv.gz
-- Clean Files:
-- 	* stride_dx_2008_2014.csv.gz
--  * stride_dx_2014_2017.csv.gz
-- CSV Fields:
--	* pat_id (e.g. "11577528280870")
--  * pat_enc_csn_id (e.g. 431388)
--  * noted_date (e.g. 01-JAN-08)
--  * resolved_date (e.g. 10-OCT-10)
--  * dx_icd9_code (e.g. "585.3") (stride_dx_2008_2014.csv.gz only)
--  * dx_icd9_code_list (e.g. "564.09, E980.5")
--  * dx_icd10_code_list (e.g. "D70.9, R50.81") (stride_dx_2014_2017.csv.gz only)
--  * data_source (e.g. "PROBLEM_LIST")

CREATE TABLE IF NOT EXISTS stride_dx
(
  pat_id BIGINT,
  pat_enc_csn_id BIGINT,
  noted_date TIMESTAMP,
  resolved_date TIMESTAMP,
  dx_icd9_code TEXT,
  dx_icd9_code_list TEXT,
  dx_icd10_code_list TEXT,
  data_source TEXT
);
