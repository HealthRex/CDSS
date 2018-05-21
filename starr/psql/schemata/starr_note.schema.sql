-- Table: starr_note
-- Description: Metadata about patient notes (w/o content for deidentification).
-- Raw Files:
--  * Chen_Clinical_Notes_Yr1.csv.gz
--  * Chen_Clinical_Notes_Yr2.csv.gz
--  * Chen_Clinical_Notes_Yr3.csv.gz
--  * Chen_Clinical_Notes_Yr4.csv.gz
--  * Chen_Clinical_Notes_Yr5.csv.gz
--  * Chen_Clinical_Notes_Yr6.csv.gz
--  * Chen_Clinical_Notes_Yr7.csv.gz
--  * Chen_Clinical_Notes_Yr8.csv.gz
-- Clean Files:
--  * starr_clinical_notes_year_1.csv.gz
--  * starr_clinical_notes_year_2.csv.gz
--  * starr_clinical_notes_year_3.csv.gz
--  * starr_clinical_notes_year_4.csv.gz
--  * starr_clinical_notes_year_5.csv.gz
--  * starr_clinical_notes_year_6.csv.gz
--  * starr_clinical_notes_year_7.csv.gz
--  * starr_clinical_notes_year_8.csv.gz
-- CSV Fields:
--  * "PAT_ID" (e.g. 11577528280870)
--  * "PAT_ENC_CSN_ID" (e.g. 431388)
--  * "NOTE_DATE" (e.g. 12/22/2009 21:53:00)
--  * "NOTE_TYPE" (e.g. "Progress Notes")
--  * "AUTHOR_NAME" (e.g. "DOE, JANE")
--  * "PROVIDER_TYPE" (e.g. "Resident")
--  * "HOSPITAL_SERVICE" (e.g. "Interventional Radiology")
--  * "DEPARTMENT" (e.g. "D3")
--  * "SPECIALTY" (e.g. "Anesthesia")
--  * "COSIGNER_NAME" (e.g. "DOE, JOHN")
--  * "STATUS" (e.g. "Signed")

CREATE TABLE IF NOT EXISTS starr_note
(
	pat_id BIGINT,
	pat_enc_csn_id BIGINT,
	note_date TIMESTAMP,
	note_type TEXT,
	author_name TEXT,
	provider_type TEXT,
	hospital_service TEXT,
	department TEXT,
	specialty TEXT,
	cosigner_name TEXT,
	status TEXT
);
