-- Table: starr_patient
-- Description: Demographics of each patient in starr dataset.
-- Original Files:
--	* Chen_Demographics.csv.gz
-- 	* Chen_Demographics_Yr6_8.csv.gz
-- Clean Files:
-- 	* starr_demographics_2008_2014.csv.gz
-- 	* starr_demographics_2014_2017.csv.gz
-- CSV Fields:
--	* "PAT_ID" (e.g. 11577528280870)
-- 	* "BIRTH_YEAR" (e.g. 1989)
-- 	* "GENDER" (e.g. "Male")
-- 	* "DEATH_DATE" (e.g. 03/18/2016)
-- 	* "RACE" (e.g. "White")
-- 	* "ETHNICITY" (e.g. "Hispanic/Latino")

CREATE TABLE IF NOT EXISTS starr_patient
(
	pat_id TEXT,
	birth_year INTEGER,
	gender TEXT,
	death_date TIMESTAMP,
	race TEXT,
	ethnicity TEXT
);
