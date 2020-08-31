-- Count up patients and claims for prescriptions for diabetes related drug classes
-- Broken up by Year
SELECT
	pc.YEAR,
	pc.THERCLS,
	-- pc.THERGRP,
	-- rb.GENNME,
	count(distinct pc.ENROLID) as n_patients,
  count(distinct pc.SEQNUM) as n_claims

FROM
	stanfordphs.ibm_marketscan_medicare_supplemental:141:v2_0.insurance_outpatient_pharmacy:6 AS pc
	   INNER JOIN
	stanfordphs.ibm_marketscan_redbook:14:v2_0.marketscan_redbook:1 AS rb ON (pc.`NDCNUM` = rb.`NDCNUM`)
WHERE
	   pc.THERCLS = 172 -- Insulins
	OR pc.THERCLS = 174 -- Miscellaneous Diabetes Meds: Includes Metformin, GLP-1 (e.g., Exenatide), DDP-4 (e.g., Linagliptin) 
	OR pc.THERCLS = 173 -- Sulfonylurea (e.g., glipizide)
	OR pc.THERCLS = 268 -- Thiazolidinediones (e.g., rosiglitazone)
	OR pc.THERCLS = 267 -- SGLT2 Inhibitor (e.g., empagliflozin)
	OR pc.THERCLS = 266 -- Meglitinides (e.g., repaglinide)
GROUP BY
	pc.YEAR,
	pc.THERCLS,
	pc.THERGRP
	--rb.GENNME
ORDER BY
	pc.YEAR desc,
	-- rb.GENNME,
	n_patients desc,
	n_claims desc

LIMIT 1000


-- Then do subsequent group by queries to get age, gender, race breakdowns
SELECT
	SEX,
	count(distinct ENROLID) as nPatients
FROM
	jonc101.test_project_multi_user:1.diabetes_med_patients_marketscan_output:27
GROUP BY
  SEX



SELECT
	CAST(FLOOR(AGE_FIRST_RX/10)*10 AS INT64) AS DECADE_FIRST_RX,
	count(distinct ENROLID) as nPatients
FROM
	jonc101.test_project_multi_user:1.diabetes_med_patients_marketscan_output:27
GROUP BY
  DECADE_FIRST_RX
ORDER BY
	DECADE_FIRST_RX


SELECT
	REGION,
	count(distinct ENROLID) as nPatients
FROM
	jonc101.test_project_multi_user:1.diabetes_med_patients_marketscan_output:27
GROUP BY
  REGION
ORDER BY
	REGION















WITH
maceDx1Sample AS
(
	-- Find Facilty Header cases where FIRST diagnosis matches major adverse cardiovascular event cases
	-- This is NOT comprehensive as only captures some ICD10 codes, not ICD9, not procedure codes, only FIRST DX1, and not necessarily DX2,DX3,DX4,etc.
	SELECT
		AGE,
		DX1,
		DXVER,
		ENROLID,
		SVCDATE,
		DOBYR,
		REGION,
		AGEGRP,
		YEAR,
		SEX
	FROM
  	stanfordphs.ibm_marketscan_medicare_supplemental:141:v2_0.insurance_facility_header:5 AS t0
	WHERE
		-- DXVER = 0 -- ICD10, but most are null?
		-- Myocardial Infarction
		DX1 LIKE 'I21%' OR
		DX1 LIKE 'I210%' OR
		DX1 LIKE 'I2101%' OR
		DX1 LIKE 'I2102%' OR
		DX1 LIKE 'I2109%' OR
		DX1 LIKE 'I211%' OR
		DX1 LIKE 'I2111%' OR
		DX1 LIKE 'I2119%' OR
		DX1 LIKE 'I212%' OR
		DX1 LIKE 'I2121%' OR
		DX1 LIKE 'I2129%' OR
		DX1 LIKE 'I213%' OR
		DX1 LIKE 'I214%' OR
		DX1 LIKE 'I22%' OR
		DX1 LIKE 'I220%' OR
		DX1 LIKE 'I221%' OR
		DX1 LIKE 'I222%' OR
		DX1 LIKE 'I228%' OR
		DX1 LIKE 'I229%' OR
		DX1 LIKE 'I23%' OR
		DX1 LIKE 'I230%' OR
		DX1 LIKE 'I231%' OR
		DX1 LIKE 'I232%' OR
		DX1 LIKE 'I233%' OR
		DX1 LIKE 'I234%' OR
		DX1 LIKE 'I235%' OR
		DX1 LIKE 'I236%' OR
		DX1 LIKE 'I237%' OR
		DX1 LIKE 'I238%' OR
		DX1 LIKE 'I252%' OR

		-- Ischemic stroke 
		DX1 LIKE 'I63%' OR

		-- Heart failure
		DX1 LIKE 'I099%' OR
		DX1 LIKE 'I110%' OR
		DX1 LIKE 'I130%' OR
		DX1 LIKE 'I132%' OR
		DX1 LIKE 'I255%' OR
		DX1 LIKE 'I420%' OR
		DX1 LIKE '1425%' OR
		DX1 LIKE '1426%' OR
		DX1 LIKE '1427%' OR
		DX1 LIKE '1428%' OR
		DX1 LIKE '1429%' OR
		DX1 LIKE 'I43%' OR
		DX1 LIKE 'I50%' OR
		DX1 LIKE 'P290%' OR

		-- Acute coronary syndrome
		DX1 LIKE 'I200%' OR
		DX1 LIKE 'I2109%' OR
		DX1 LIKE 'I2111%' OR
		DX1 LIKE 'I2119%' OR
		DX1 LIKE 'I2129%' OR
		DX1 LIKE 'I213%' OR
		DX1 LIKE 'I214%' OR
		DX1 LIKE 'I240%' OR



		-- Myocardial Infarction
		DX2 LIKE 'I21%' OR
		DX2 LIKE 'I210%' OR
		DX2 LIKE 'I2101%' OR
		DX2 LIKE 'I2102%' OR
		DX2 LIKE 'I2109%' OR
		DX2 LIKE 'I211%' OR
		DX2 LIKE 'I2111%' OR
		DX2 LIKE 'I2119%' OR
		DX2 LIKE 'I212%' OR
		DX2 LIKE 'I2121%' OR
		DX2 LIKE 'I2129%' OR
		DX2 LIKE 'I213%' OR
		DX2 LIKE 'I214%' OR
		DX2 LIKE 'I22%' OR
		DX2 LIKE 'I220%' OR
		DX2 LIKE 'I221%' OR
		DX2 LIKE 'I222%' OR
		DX2 LIKE 'I228%' OR
		DX2 LIKE 'I229%' OR
		DX2 LIKE 'I23%' OR
		DX2 LIKE 'I230%' OR
		DX2 LIKE 'I231%' OR
		DX2 LIKE 'I232%' OR
		DX2 LIKE 'I233%' OR
		DX2 LIKE 'I234%' OR
		DX2 LIKE 'I235%' OR
		DX2 LIKE 'I236%' OR
		DX2 LIKE 'I237%' OR
		DX2 LIKE 'I238%' OR
		DX2 LIKE 'I252%' OR

		-- Ischemic stroke 
		DX2 LIKE 'I63%' OR

		-- Heart failure
		DX2 LIKE 'I099%' OR
		DX2 LIKE 'I110%' OR
		DX2 LIKE 'I130%' OR
		DX2 LIKE 'I132%' OR
		DX2 LIKE 'I255%' OR
		DX2 LIKE 'I420%' OR
		DX2 LIKE 'I425%' OR
		DX2 LIKE 'I426%' OR
		DX2 LIKE 'I427%' OR
		DX2 LIKE 'I428%' OR
		DX2 LIKE 'I429%' OR
		DX2 LIKE 'I43%' OR
		DX2 LIKE 'I50%' OR
		DX2 LIKE 'P290%' OR

		-- Acute coronary syndrome
		DX2 LIKE 'I200%' OR
		DX2 LIKE 'I2109%' OR
		DX2 LIKE 'I2111%' OR
		DX2 LIKE 'I2119%' OR
		DX2 LIKE 'I2129%' OR
		DX2 LIKE 'I213%' OR
		DX2 LIKE 'I214%' OR
		DX2 LIKE 'I240%' OR


		-- Myocardial Infarction
		DX3 LIKE 'I21%' OR
		DX3 LIKE 'I210%' OR
		DX3 LIKE 'I2101%' OR
		DX3 LIKE 'I2102%' OR
		DX3 LIKE 'I2109%' OR
		DX3 LIKE 'I211%' OR
		DX3 LIKE 'I2111%' OR
		DX3 LIKE 'I2119%' OR
		DX3 LIKE 'I212%' OR
		DX3 LIKE 'I2121%' OR
		DX3 LIKE 'I2129%' OR
		DX3 LIKE 'I213%' OR
		DX3 LIKE 'I214%' OR
		DX3 LIKE 'I22%' OR
		DX3 LIKE 'I220%' OR
		DX3 LIKE 'I221%' OR
		DX3 LIKE 'I222%' OR
		DX3 LIKE 'I228%' OR
		DX3 LIKE 'I229%' OR
		DX3 LIKE 'I23%' OR
		DX3 LIKE 'I230%' OR
		DX3 LIKE 'I231%' OR
		DX3 LIKE 'I232%' OR
		DX3 LIKE 'I233%' OR
		DX3 LIKE 'I234%' OR
		DX3 LIKE 'I235%' OR
		DX3 LIKE 'I236%' OR
		DX3 LIKE 'I237%' OR
		DX3 LIKE 'I238%' OR
		DX3 LIKE 'I252%' OR

		-- Ischemic stroke 
		DX3 LIKE 'I63%' OR

		-- Heart failure
		DX3 LIKE 'I099%' OR
		DX3 LIKE 'I110%' OR
		DX3 LIKE 'I130%' OR
		DX3 LIKE 'I132%' OR
		DX3 LIKE 'I255%' OR
		DX3 LIKE 'I420%' OR
		DX3 LIKE '1425%' OR
		DX3 LIKE '1426%' OR
		DX3 LIKE '1427%' OR
		DX3 LIKE '1428%' OR
		DX3 LIKE '1429%' OR
		DX3 LIKE 'I43%' OR
		DX3 LIKE 'I50%' OR
		DX3 LIKE 'P290%' OR

		-- Acute coronary syndrome
		DX3 LIKE 'I200%' OR
		DX3 LIKE 'I2109%' OR
		DX3 LIKE 'I2111%' OR
		DX3 LIKE 'I2119%' OR
		DX3 LIKE 'I2129%' OR
		DX3 LIKE 'I213%' OR
		DX3 LIKE 'I214%' OR
		DX3 LIKE 'I240%' OR


		-- Myocardial Infarction
		DX4 LIKE 'I21%' OR
		DX4 LIKE 'I210%' OR
		DX4 LIKE 'I2101%' OR
		DX4 LIKE 'I2102%' OR
		DX4 LIKE 'I2109%' OR
		DX4 LIKE 'I211%' OR
		DX4 LIKE 'I2111%' OR
		DX4 LIKE 'I2119%' OR
		DX4 LIKE 'I212%' OR
		DX4 LIKE 'I2121%' OR
		DX4 LIKE 'I2129%' OR
		DX4 LIKE 'I213%' OR
		DX4 LIKE 'I214%' OR
		DX4 LIKE 'I22%' OR
		DX4 LIKE 'I220%' OR
		DX4 LIKE 'I221%' OR
		DX4 LIKE 'I222%' OR
		DX4 LIKE 'I228%' OR
		DX4 LIKE 'I229%' OR
		DX4 LIKE 'I23%' OR
		DX4 LIKE 'I230%' OR
		DX4 LIKE 'I231%' OR
		DX4 LIKE 'I232%' OR
		DX4 LIKE 'I233%' OR
		DX4 LIKE 'I234%' OR
		DX4 LIKE 'I235%' OR
		DX4 LIKE 'I236%' OR
		DX4 LIKE 'I237%' OR
		DX4 LIKE 'I238%' OR
		DX4 LIKE 'I252%' OR

		-- Ischemic stroke 
		DX4 LIKE 'I63%' OR

		-- Heart failure
		DX4 LIKE 'I099%' OR
		DX4 LIKE 'I110%' OR
		DX4 LIKE 'I130%' OR
		DX4 LIKE 'I132%' OR
		DX4 LIKE 'I255%' OR
		DX4 LIKE 'I420%' OR
		DX4 LIKE '1425%' OR
		DX4 LIKE '1426%' OR
		DX4 LIKE '1427%' OR
		DX4 LIKE '1428%' OR
		DX4 LIKE '1429%' OR
		DX4 LIKE 'I43%' OR
		DX4 LIKE 'I50%' OR
		DX4 LIKE 'P290%' OR

		-- Acute coronary syndrome
		DX4 LIKE 'I200%' OR
		DX4 LIKE 'I2109%' OR
		DX4 LIKE 'I2111%' OR
		DX4 LIKE 'I2119%' OR
		DX4 LIKE 'I2129%' OR
		DX4 LIKE 'I213%' OR
		DX4 LIKE 'I214%' OR
		DX4 LIKE 'I240%' OR


		-- Myocardial Infarction
		DX5 LIKE 'I21%' OR
		DX5 LIKE 'I210%' OR
		DX5 LIKE 'I2101%' OR
		DX5 LIKE 'I2102%' OR
		DX5 LIKE 'I2109%' OR
		DX5 LIKE 'I211%' OR
		DX5 LIKE 'I2111%' OR
		DX5 LIKE 'I2119%' OR
		DX5 LIKE 'I212%' OR
		DX5 LIKE 'I2121%' OR
		DX5 LIKE 'I2129%' OR
		DX5 LIKE 'I213%' OR
		DX5 LIKE 'I214%' OR
		DX5 LIKE 'I22%' OR
		DX5 LIKE 'I220%' OR
		DX5 LIKE 'I221%' OR
		DX5 LIKE 'I222%' OR
		DX5 LIKE 'I228%' OR
		DX5 LIKE 'I229%' OR
		DX5 LIKE 'I23%' OR
		DX5 LIKE 'I230%' OR
		DX5 LIKE 'I231%' OR
		DX5 LIKE 'I232%' OR
		DX5 LIKE 'I233%' OR
		DX5 LIKE 'I234%' OR
		DX5 LIKE 'I235%' OR
		DX5 LIKE 'I236%' OR
		DX5 LIKE 'I237%' OR
		DX5 LIKE 'I238%' OR
		DX5 LIKE 'I252%' OR

		-- Ischemic stroke 
		DX5 LIKE 'I63%' OR

		-- Heart failure
		DX5 LIKE 'I099%' OR
		DX5 LIKE 'I110%' OR
		DX5 LIKE 'I130%' OR
		DX5 LIKE 'I132%' OR
		DX5 LIKE 'I255%' OR
		DX5 LIKE 'I420%' OR
		DX5 LIKE '1425%' OR
		DX5 LIKE '1426%' OR
		DX5 LIKE '1427%' OR
		DX5 LIKE '1428%' OR
		DX5 LIKE '1429%' OR
		DX5 LIKE 'I43%' OR
		DX5 LIKE 'I50%' OR
		DX5 LIKE 'P290%' OR

		-- Acute coronary syndrome
		DX5 LIKE 'I200%' OR
		DX5 LIKE 'I2109%' OR
		DX5 LIKE 'I2111%' OR
		DX5 LIKE 'I2119%' OR
		DX5 LIKE 'I2129%' OR
		DX5 LIKE 'I213%' OR
		DX5 LIKE 'I214%' OR
		DX5 LIKE 'I240%' 

),
dmRx AS
( -- Records of Diabetes related medication prescriptions
	SELECT
		pc.SEQNUM,
		pc.ENROLID,	
		pc.SVCDATE,
		pc.YEAR,
		pc.THERCLS,
		rb.GENNME,
		pc.REGION,
		pc.AGEGRP,
		pc.SEX,
	  pc.DOBYR,
		pc.AGE
	FROM
  	stanfordphs.ibm_marketscan_medicare_supplemental:141:v2_0.insurance_outpatient_pharmacy:6 AS pc
			 INNER JOIN
		stanfordphs.ibm_marketscan_redbook:14:v2_0.marketscan_redbook:1 AS rb USING (NDCNUM)
	WHERE
			 pc.THERCLS = 172 -- Insulins
		OR pc.THERCLS = 174 -- Miscellaneous Diabetes Meds: Includes Metformin, GLP-1 (e.g., Exenatide), DDP-4 (e.g., Linagliptin) 
		OR pc.THERCLS = 173 -- Sulfonylurea (e.g., glipizide)
		OR pc.THERCLS = 268 -- Thiazolidinediones (e.g., rosiglitazone)
		OR pc.THERCLS = 267 -- SGLT2 Inhibitor (e.g., empagliflozin)
		OR pc.THERCLS = 266 -- Meglitinides (e.g., repaglinide)
),


-- Find demographic info on patients who received at least one diabetes drug prescription 
-- and a cardiovascular event sample diagnosis anytime after
-- Beware that diagnosis coding by ICD10 only inconsistently starting in 2015 and
--  many misses described above, so this is an underestimate
dmRxMACEDx1SamplePatients AS
(
    SELECT
			dx.ENROLID,
			dx.SEX,
			dx.REGION,
			MIN(dx.YEAR) YEAR_FIRST_DX1,
			MIN(dx.AGE) AGE_FIRST_DX1,
			MIN(dx.SVCDATE) FIRST_SVCDATE
		FROM
			maceDx1Sample as dx
			  INNER JOIN 
		  dmRx USING (ENROLID)
    WHERE dmRx.SVCDATE < dx.SVCDATE
		GROUP BY
			dx.ENROLID,
			dx.SEX,
			dx.REGION
)

SELECT
	YEAR_FIRST_DX1, count(distinct ENROLID) as nPatients
FROM dmRxMACEDx1SamplePatients
GROUP BY
	YEAR_FIRST_DX1
ORDER BY
	YEAR_FIRST_DX1
	














