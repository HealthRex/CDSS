-- Table: stride_patient
-- Original Files:
--	* Chen_Demographics.csv.gz
-- 	* Chen_Demographics_Yr6_8.csv.gz
-- CSV Fields:
--	* "PAT_ID" (e.g. 11577528280870)
-- 	* "BIRTH_YEAR" (e.g. 1989)
-- 	* "GENDER" (e.g. "Male")
-- 	* "DEATH_DATE" (e.g. 03/18/2016)
-- 	* "RACE" (e.g. "White")
-- 	* "ETHNICITY" (e.g. "Hispanic/Latino")

CREATE TABLE IF NOT EXISTS stride_patient
(
	pat_id TEXT,
	birth_year TIMESTAMP,
	sex TEXT,
	death_date TIMESTAMP,
	race TEXT,
	ethnicity TEXT
);
CREATE INDEX IF NOT EXISTS index_patient_pat_id ON stride_patient(SUBSTRING(pat_id, 1, 16));
