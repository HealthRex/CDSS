-- Table: stride_culture_micro
-- Description: Orders and detailed results for blood culture labs.
-- Raw Files:
--  * JChen_cult_micro_7yr.patchIds.csv.gz
-- Clean Files:
--  * stride_culture_micro_7_year.csv.gz
-- CSV Fields:
--  * ORDER_PROC_ANON_ID (e.g. 354125129)
--  * PAT_ANON_ID (e.g. 3512885273857)
--  * PAT_ENC_CSN_ANON_ID (e.g. 863055)
--  * PROC_CODE (e.g. LABFLDB)
--  * DESCRIPTION (e.g. STOOL CULTURE)
--  * ORGANISM_ID (e.g. 433)
--  * ORGANISM_NAME (e.g. STREPTOCOCCUS PNEUMONIAE)
--  * ORGANISM_GROUP_C (e.g. 123061008)
--  * ORGANISM_GROUP (e.g. Yeast)
--  * ANTIBIOTIC_C (e.g. 313)
--  * ANTIBIOTIC_NAME (e.g. Ceftriaxone)
--  * ORD_SENSITIV_LINE (e.g. 22)
--  * SENSITIVITY_VALUE (e.g. >=64)
--  * SENSITIVITY_UNITS (e.g. "")
--  * SENS_REF_RANGE (e.g. "")
--  * SHIFTED_ORDER_TIME (e.g. 12/10/2011 14:44)
--  * SHIFTED_SPECIMN_TAKEN_TIME (e.g. 8/30/2011 21:10)
--  * SHIFTED_RESULT_TIME (e.g. 12/6/2009 15:22)
--  * LAB_STATUS_C (e.g. 3)
--  * LAB_STATUS (e.g. Final result)

CREATE TABLE IF NOT EXISTS stride_culture_micro
(
  order_proc_anon_id BIGINT,
  pat_anon_id BIGINT,
  pat_enc_csn_anon_id BIGINT,
  proc_code TEXT,
  description TEXT,
  organism_id BIGINT,
  organism_name TEXT,
  organism_group_c BIGINT,
  organism_group TEXT,
  antibiotic_c BIGINT,
  antibiotic_name TEXT,
  ord_sensitiv_line INTEGER,
  sensitivity_value TEXT,
  sensitivity_units TEXT,
  suseptibility TEXT,
  sens_ref_range TEXT,
  shifted_order_time TEXT,
  shifted_specimn_taken_time TEXT,
  shifted_result_time TEXT,
  lab_status_c BIGINT,
  lab_status TEXT
);
