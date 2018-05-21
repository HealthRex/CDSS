-- Table: starr_treatment_team
-- Description: Treatment team for patient PAT_ID in encounter PAT_ENC_CSN_ID.
-- Original Files:
--	* Chen_TreatmentTeam_Yr1.csv.gz
--	* Chen_TreatmentTeam_Yr2.csv.gz
--	* Chen_TreatmentTeam_Yr3.csv.gz
--	* Chen_TreatmentTeam_Yr4.csv.gz
--	* Chen_TreatmentTeam_Yr5.csv.gz
--  * Chen_Treatment_Team_Yrs6.patchHeader.csv.gz
--  * Chen_Treatment_Team_Yrs7.patchHeader.csv.gz
--  * Chen_Treatment_Team_Yrs8.patchHeader.csv.gz
-- Clean Files:
--  * starr_treatment_team_year_1.csv.gz
--  * starr_treatment_team_year_2.csv.gz
--  * starr_treatment_team_year_3.csv.gz
--  * starr_treatment_team_year_4.csv.gz
--  * starr_treatment_team_year_5.csv.gz
--  * starr_treatment_team_year_6.csv.gz
--  * starr_treatment_team_year_7.csv.gz
--  * starr_treatment_team_year_8.csv.gz
-- CSV Fields:
--  * PAT_ID (e.g. 4505642352918)
--  * PAT_ENC_CSN_ID (e.g. 409048)
--  * LINE (e.g. 3)
--  * TRTMNT_TM_BEGIN_DATE (e.g. "10/15/2009 06:50:00")
--  * TRTMNT_TM_END_DATE (e.g. "11/16/2009 07:30:00")
--  * TREATMENT_TEAM (e.g. "Occupational Therapist")
--  * PROV_NAME (e.g. "DOE, JANE")

CREATE TABLE IF NOT EXISTS starr_treatment_team
(
  starr_treatment_team_id SERIAL, -- automatically create unique identifier
	pat_id TEXT,
	pat_enc_csn_id BIGINT,
	line INTEGER,
	trtmnt_tm_begin_date TIMESTAMP,
	trtmnt_tm_end_date TIMESTAMP,
	treatment_team TEXT,
	prov_name TEXT
);
