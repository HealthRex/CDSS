-- Table: starr_income
-- Description: Income range for patient pat_id.
-- Original Files:
--	* Chen_income_vs_zip.csv.gz
--  * Chen_income_vs_zip_Yrs6_8.csv.gz
-- Clean Files:
-- 	* starr_income_2008_2014.csv.gz
--  * starr_income_2014_2017.csv.gz
-- CSV Fields:
--	* PAT_ID (e.g. "11577528280870")
--  * INCOME_RANGE (e.g. "32001-36000")

CREATE TABLE IF NOT EXISTS starr_income
(
  PAT_ID BIGINT,
  INCOME_RANGE TEXT
);
