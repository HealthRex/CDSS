	
	
	
	
-- Look for example outpatient prescription fills of all the different types of diabetes medications
-- https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/diagnosis-treatment/drc-20351199
SELECT 
    AHFSCLSS, 
		SUBSTR(AHFSCLSS, 0, 6) as AHFSCLSS_LEAD_CODE,
		count(distinct PATID) as n_Patients, count(distinct CLMID) as n_Claims, count(distinct NPI) as n_NPIs
FROM stanfordphs.optum_zip5:139:v3_0:sample.rx_pharmacy:9 
WHERE
   GNRC_NM like 'METFORM%'
OR GNRC_NM like 'GLIPIZIDE%'
OR GNRC_NM like 'GLYBURIDE%'
OR GNRC_NM like 'GLIMEPIRIDE%'
OR GNRC_NM like 'REPAGLINIDE%'
OR GNRC_NM like 'NATEGLINIDE%'
OR GNRC_NM like 'ROSIGLITAZONE%'
OR GNRC_NM like 'PIOGLITAZONE%'
OR GNRC_NM like 'SITAGLIPTIN%'
OR GNRC_NM like 'SAXAGLIPTIN%'
OR GNRC_NM like 'LINAGLIPTIN%'
OR GNRC_NM like 'EXENATIDE%'
OR GNRC_NM like 'LIRAGLUTIDE%'
OR GNRC_NM like 'SEMAGLUTIDE%'
OR GNRC_NM like 'CANAGLIFLOZIN%'
OR GNRC_NM like 'DAPAGLIFLOZIN%'
OR GNRC_NM like 'EMPAGLIFLOZIN'
OR GNRC_NM like 'INSULIN%'
GROUP BY
   AHFSCLSS, AHFSCLSS_LEAD_CODE
ORDER BY
   AHFSCLSS_LEAD_CODE, n_Claims desc
LIMIT 100
	

-- Look for all outpatient prescription fills from one of the primary diabetes medication categories
-- Break out by year
SELECT 
	EXTRACT(YEAR from FILL_DT) as fill_year, 
	SUBSTR(AHFSCLSS, 0, 6) as AHFSCLSS_LEAD_CODE,
  AHFSCLSS, 
	count(distinct PATID) as n_Patients, count(distinct CLMID) as n_Claims, count(distinct NPI) as n_NPIs
FROM stanfordphs.optum_zip5:139:v3_0:sample.rx_pharmacy:9 
WHERE
   AHFSCLSS like '682004%' -- Biguanides (e.g., Metformin)
OR AHFSCLSS like '682092%' -- Miscellaneous Diabetes Meds
OR AHFSCLSS like '682008%' -- Insulins
OR AHFSCLSS like '682020%' -- Sulfonylurea (e.g., glipizide)
OR AHFSCLSS like '682005%' -- DPP-4 Inhibitors (e.g., sitagliptin)
OR AHFSCLSS like '682028%' -- Thiazolidinediones (e.g., rosiglitazone)
OR AHFSCLSS like '682006%' -- Incretin Mimetic / GLP-1 (e.g., exenatide)
OR AHFSCLSS like '682018%' -- SGLT2 Inhibitor (e.g., empagliflozin)
OR AHFSCLSS like '682016%' -- Meglitinides (e.g., repaglinide)

GROUP BY
   fill_year,
	 AHFSCLSS_LEAD_CODE,
	 AHFSCLSS
ORDER BY
   fill_year desc, 
   n_Claims desc
LIMIT 100




-- Patient Demographics for those who ever took some Diabetes medications
WITH 
-- Find all prescriptions for diabetes related drugs
dmRx AS
(
		SELECT 
			PATID, CLMID, NPI,
			SUBSTR(AHFSCLSS, 0, 6) as AHFSCLSS_LEAD_CODE,
			AHFSCLSS, 
			GNRC_NM,
			FILL_DT
		FROM stanfordphs.optum_dod:138:v3_0:sample.rx_pharmacy:6 AS t0
		WHERE
			 AHFSCLSS like '682004%' -- Biguanides (e.g., Metformin) -- This is sometimes used for non-diabetes (e.g., PCOS) so may want to exclude
		OR AHFSCLSS like '682092%' -- Miscellaneous Diabetes Meds
		OR AHFSCLSS like '682008%' -- Insulins
		OR AHFSCLSS like '682020%' -- Sulfonylurea (e.g., glipizide)
		OR AHFSCLSS like '682005%' -- DPP-4 Inhibitors (e.g., sitagliptin)
		OR AHFSCLSS like '682028%' -- Thiazolidinediones (e.g., rosiglitazone)
		OR AHFSCLSS like '682006%' -- Incretin Mimetic / GLP-1 (e.g., exenatide)
		OR AHFSCLSS like '682018%' -- SGLT2 Inhibitor (e.g., empagliflozin)
		OR AHFSCLSS like '682016%' -- Meglitinides (e.g., repaglinide)
)

-- Find demographic info on patients who received at least one diabetes drug prescription and their age at the first date it happened

    SELECT
			m.PATID,
			m.GDR_CD,
			m.RACE,
			m.YRDOB,
			MIN(dmRx.FILL_DT) AS FIRST_FILL_DT,
			EXTRACT(YEAR FROM MIN(dmRx.FILL_DT)) - m.YRDOB AS AGE_AT_FIRST_FILL
		FROM
			stanfordphs.optum_dod:138:v3_0:sample.member_enrollment:3 AS m
			INNER JOIN 
		  dmRx USING (PATID)
    GROUP BY
			m.PATID,
			m.GDR_CD,
			m.RACE,
			m.YRDOB


-- Further subquery to group by decade of age, race, gender
-- Round/floor patient age at first diabetes Rx fill to decade
SELECT
	CAST(FLOOR(AGE_AT_FIRST_FILL/10)*10 AS INT64) AS DECADE_AT_FIRST_FILL,
	COUNT(DISTINCT PATID) AS nPatients
FROM
	jonc101.test_project_multi_user:1.diabetes_med_patients_output:19 AS dmPatient
GROUP BY
	DECADE_AT_FIRST_FILL
ORDER By
  DECADE_AT_FIRST_FILL 














-- Construct number of patients who had a MACE sample diagnosis who received at least one diabetes med presricption before

WITH 
-- Find all prescriptions for diabetes related drugs
dmRx AS
(
		SELECT 
			PATID, CLMID, NPI,
			SUBSTR(AHFSCLSS, 0, 6) as AHFSCLSS_LEAD_CODE,
			AHFSCLSS, 
			GNRC_NM,
			FILL_DT
		FROM stanfordphs.optum_dod:138:v3_0:sample.rx_pharmacy:6 AS t0
		WHERE
			 AHFSCLSS like '682004%' -- Biguanides (e.g., Metformin) -- This is sometimes used for non-diabetes (e.g., PCOS) so may want to exclude
		OR AHFSCLSS like '682092%' -- Miscellaneous Diabetes Meds
		OR AHFSCLSS like '682008%' -- Insulins
		OR AHFSCLSS like '682020%' -- Sulfonylurea (e.g., glipizide)
		OR AHFSCLSS like '682005%' -- DPP-4 Inhibitors (e.g., sitagliptin)
		OR AHFSCLSS like '682028%' -- Thiazolidinediones (e.g., rosiglitazone)
		OR AHFSCLSS like '682006%' -- Incretin Mimetic / GLP-1 (e.g., exenatide)
		OR AHFSCLSS like '682018%' -- SGLT2 Inhibitor (e.g., empagliflozin)
		OR AHFSCLSS like '682016%' -- Meglitinides (e.g., repaglinide)
),
maceDxSample AS
(
	-- Pull out diagnoses where matches one of the ICD10 codes for select Major Adverse Cardiovascular Events
	-- Doesn't capture all of them however, as the full list appears to include other procedure codes and this is only for ICD10 
	-- (whereas the database appears to have ICD9 codes prior to ~2015)
	-- https://www.ahajournals.org/doi/pdf/10.1161/JAHA.119.014402
	SELECT
		PATID,
		CLMID,
		DIAG,
		ICD_FLAG,
		FST_DT,
		EXTRACT(YEAR FROM FST_DT) as FST_YEAR
	FROM
		stanfordphs.optum_dod:138:v3_0:sample.medical_diagnosis:13
	WHERE
	  ICD_FLAG = 10 AND
	  (
		-- Myocardial Infarction
		DIAG LIKE 'I21%' OR
		DIAG LIKE 'I210%' OR
		DIAG LIKE 'I2101%' OR
		DIAG LIKE 'I2102%' OR
		DIAG LIKE 'I2109%' OR
		DIAG LIKE 'I211%' OR
		DIAG LIKE 'I2111%' OR
		DIAG LIKE 'I2119%' OR
		DIAG LIKE 'I212%' OR
		DIAG LIKE 'I2121%' OR
		DIAG LIKE 'I2129%' OR
		DIAG LIKE 'I213%' OR
		DIAG LIKE 'I214%' OR
		DIAG LIKE 'I22%' OR
		DIAG LIKE 'I220%' OR
		DIAG LIKE 'I221%' OR
		DIAG LIKE 'I222%' OR
		DIAG LIKE 'I228%' OR
		DIAG LIKE 'I229%' OR
		DIAG LIKE 'I23%' OR
		DIAG LIKE 'I230%' OR
		DIAG LIKE 'I231%' OR
		DIAG LIKE 'I232%' OR
		DIAG LIKE 'I233%' OR
		DIAG LIKE 'I234%' OR
		DIAG LIKE 'I235%' OR
		DIAG LIKE 'I236%' OR
		DIAG LIKE 'I237%' OR
		DIAG LIKE 'I238%' OR
		DIAG LIKE 'I252%' OR

		-- Ischemic stroke 
		DIAG LIKE 'I63%' OR

		-- Heart failure
		DIAG LIKE 'I099%' OR
		DIAG LIKE 'I110%' OR
		DIAG LIKE 'I130%' OR
		DIAG LIKE 'I132%' OR
		DIAG LIKE 'I255%' OR
		DIAG LIKE 'I420%' OR
		DIAG LIKE 'I425%' OR
		DIAG LIKE 'I426%' OR
		DIAG LIKE 'I427%' OR
		DIAG LIKE 'I428%' OR
		DIAG LIKE 'I429%' OR
		DIAG LIKE 'I43%' OR
		DIAG LIKE 'I50%' OR
		DIAG LIKE 'P290%' OR

		-- Acute coronary syndrome
		DIAG LIKE 'I200%' OR
		DIAG LIKE 'I2109%' OR
		DIAG LIKE 'I2111%' OR
		DIAG LIKE 'I2119%' OR
		DIAG LIKE 'I2129%' OR
		DIAG LIKE 'I213%' OR
		DIAG LIKE 'I214%' OR
		DIAG LIKE 'I240%' 
	  )
),

dmRxMACESamplePatients AS (
-- Find demographic info on patients who received at least one diabetes drug prescription 
-- and a cardiovascular event sample diagnosis anytime after
-- Beware that diagnosis coding by ICD10 only starts ~2016, so this is not counting before then

    SELECT
			m.PATID,
			m.GDR_CD,
			m.RACE,
			m.YRDOB,
			MIN(dmRx.FILL_DT) AS FIRST_FILL_DT,
			EXTRACT(YEAR FROM MIN(dmRx.FILL_DT)) - m.YRDOB AS AGE_AT_FIRST_FILL,
			MIN(maceDxSample.FST_DT) AS FIRST_MACE_SAMPLE_DX_DT,
			EXTRACT(YEAR FROM MIN(maceDxSample.FST_DT)) - m.YRDOB AS AGE_AT_FIRST_MACE_SAMPLE_DX,
		FROM
			stanfordphs.optum_dod:138:v3_0:sample.member_enrollment:3 AS m
			  INNER JOIN 
		  dmRx USING (PATID)
				INNER JOIN
			maceDxSample USING (PATID)
    WHERE dmRx.FILL_DT < maceDxSample.FST_DT
		GROUP BY
			m.PATID,
			m.GDR_CD,
			m.RACE,
			m.YRDOB
)

SELECT 
	EXTRACT(YEAR FROM FIRST_MACE_SAMPLE_DX_DT) as FIRST_MACE_SAMPLE_DX_YEAR,
	-- CAST(FLOOR(AGE_AT_FIRST_MACE_SAMPLE_DX/10)*10 AS INT64) AS DECADE_AT_FIRST_MACE_SAMPLE_DX,
	COUNT(DISTINCT PATID) as nPatients,
FROM dmRxMACESamplePatients
GROUP BY 
  FIRST_MACE_SAMPLE_DX_YEAR
ORDER BY
  FIRST_MACE_SAMPLE_DX_YEAR
	
















