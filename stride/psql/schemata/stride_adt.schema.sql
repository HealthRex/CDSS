-- Table: stride_adt
-- Description: Admission, Discharge, and Transfer (ADT) for patient pat_anon_id.
--  Each row is modeled as a time window in which a patient was in place X,
--  rather than the discrete event  of each ADT.
-- Original Files:
--	* JChenv3_ADTTable10.csv.gz
--  * JChenv3_ADTTable56.csv.gz
-- Clean Files:
--	* stride_adt_2008_2014.csv.gz
--  * stride_adt_2014_2017.csv.gz
-- CSV Fields:
--  * PAT_ANON_ID (e.g. 4242249324038)
--  * PAT_ENC_CSN_ANON_ID (e.g. 451502)
--  * SEQ_NUM_IN_BED_MIN (e.g. 3)
--  * SEQ_NUM_IN_ENC (e.g. 5)
--  * PATIENT_CLASS (e.g. "OP Surgery/Procedure")
--  * BED (e.g. "OVRFLW")
--  * BED_STATUS (e.g. "ACTIVE")
--  * SHIFTED_TRANSF_IN_DT_TM (e.g. "17-MAR-13 16:35")
--  * DEPARTMENT_IN (e.g. "MOR INTRA-OP")
--  * EVENT_IN (e.g. "Admission")
--  * SHIFTED_TRANSF_OUT_DT_TM (e.g. "19-APR-12 17:00")
--  * EVENT_OUT (e.g. "Discharge")

CREATE TABLE IF NOT EXISTS stride_adt
(
  pat_anon_id BIGINT,
  pat_enc_csn_anon_id BIGINT,
  seq_num_in_bed_min INTEGER,
  seq_num_in_enc INTEGER,
  patient_class TEXT,
  bed TEXT,
  bed_status TEXT,
  shifted_transf_in_dt_tm TIMESTAMP,
  department_in TEXT,
  event_in TEXT,
  shifted_transf_out_dt_tm TIMESTAMP,
  event_out TEXT
);
