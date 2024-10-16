-- Table: stride_patient
-- Description: Demographics of each patient in stride dataset.
-- Original Files:
--	* Chen_Demographics.csv.gz
-- 	* Chen_Demographics_Yr6_8.csv.gz
-- Clean Files:
-- 	* stride_demographics_2008_2014.csv.gz
-- 	* stride_demographics_2014_2017.csv.gz
-- CSV Fields:
--	* "PAT_ID" (e.g. 11577528280870)
-- 	* "BIRTH_YEAR" (e.g. 1989)
-- 	* "GENDER" (e.g. "Male")
-- 	* "DEATH_DATE" (e.g. 03/18/2016)
-- 	* "RACE" (e.g. "White")
-- 	* "ETHNICITY" (e.g. "Hispanic/Latino")

CREATE TABLE IF NOT EXISTS stride_patient
(
	pat_id BIGINT,
	birth_year INTEGER,
	gender TEXT,
	death_date TIMESTAMP,
	race TEXT,
	ethnicity TEXT
);
