-- Table: stride_icd10_cm
-- Description: ICD-10 CM (International Classification of Diseases, Ninth
--              Revision, Clinical Modification)
-- Original Files:
--  * export_ICD-10-CM_2016.csv.gz
-- Clean Files:
--  * stride_icd10_cm_2016.csv.gz
-- CSV Fields:
--  * ORDER_NUMBER (e.g. 76464)
--  * ICD10 (e.g. M60849)
--  * HIPAA_COVERED (e.g. 1)
--  * SHORT_DESCRIPTION (e.g. "Acute lymphangitis of trunk, unspecified")
--  * FULL_DESCRIPTION (e.g. "Varicella pneumonia")
--  * ICD10_CODE (e.g. S72.355H)

CREATE TABLE IF NOT EXISTS stride_icd10_cm
(
  order_number BIGINT,
	icd10 TEXT,
	hipaa_covered INTEGER,
	short_description TEXT,
	full_description TEXT,
	icd10_code TEXT
);
