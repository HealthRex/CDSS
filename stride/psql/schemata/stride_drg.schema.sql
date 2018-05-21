-- Table: stride_drg
-- Description: Discharge Diagnosis Related Group (DRG) summary data.
-- Raw Files:
--  * JChenv3_DRG_Table57.csv.gz
-- Clean Files:
--  * stride_drg.csv.gz
-- CSV Fields:
--  * HSP_ACC_DEID (e.g. 57779988)
--  * HSP_ACCOUNT_ID (e.g. 57730295)
--  * PAT_ENC_CSN_ANON_ID (e.g. 851217)
--  * PAT_ANON_ID (e.g. 5212716573247)
--  * DRG_MPI_CODE (e.g. 455)
--  * ENC_MS_DRG_WEIGHT (e.g. 1.00)
--  * ENC_MS_DRG_DESC (e.g. MAJOR SMALL & LARGE BOWEL PROCEDURES W CC)
--  * ENC_PRIMARY_ICD9_ICD10 (e.g. M48.06)
--  * ENC_PRIMARY_ICD_DESC (e.g. Malignant neoplasm of prostate)
--  * DRG_WEIGHT (e.g. 2.5822)
--  * CODE_TYPE (e.g. ICD-10-PCS)
--  * ENC_BILL_CODE_PRIM_SURG (e.g. 8E09XBH)
--  * ENC_DESC_PRIM_SURG (e.g. CORONAR ARTERIOGR-2 CATH)

CREATE TABLE IF NOT EXISTS stride_drg
(
  hsp_acc_deid BIGINT,
	hsp_account_id BIGINT,
	pat_enc_csn_anon_id BIGINT,
	pat_anon_id BIGINT,
	drg_mpi_code INTEGER,
	enc_ms_drg_weight FLOAT,
	enc_ms_drg_desc TEXT,
	enc_primary_icd9_icd10 TEXT,
	enc_primary_icd_desc TEXT,
	drg_weight FLOAT,
	code_type TEXT,
	enc_bill_code_prim_surg TEXT,
	enc_desc_prim_surg TEXT
);
