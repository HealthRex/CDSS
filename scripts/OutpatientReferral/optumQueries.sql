-- (1) Overall Claims Database size and range

SELECT
	count(distinct PATID) as nPatients,
	min(FST_DT) as firstDate,
	max(fst_dt) as lastDate
FROM
	stanfordphs.optum_ses:145:v3_0:sample.medical_claims:7 AS t0

-- 1% Sample: 628,616 patients, 2003-01-01 to 2019-06-30
-- Full Data: 62,883,828 patients, 2003-01-01 to 2019-06-30


-- Top Visit Type / Locations

SELECT
	c.POS,
	count(distinct PATID) as nPatients,
	min(FST_DT) as firstDate,
	max(fst_dt) as lastDate
FROM
	stanfordphs.optum_ses:145:v3_0:sample.medical_claims:7 AS c
GROUP BY
  c.POS
ORDER BY nPatients DESC

-- 5.8M Office Visits, 3.7M Outpatient Hospital, 3.4M Inpatient Lab...


-- Top HCCC Type

SELECT
	c.HCCC,
	count(distinct PATID) as nPatients,
	min(FST_DT) as firstDate,
	max(fst_dt) as lastDate
FROM
	stanfordphs.optum_ses:145:v3_0:sample.medical_claims:7 AS c
GROUP BY
  c.HCCC
ORDER BY nPatients DESC

-- 4.9M Primary Care (01)
-- 4.5M Outpatient Facility (07)
-- 4.2M Specialty Physician (02)
-- 2.5M Allied Health Provider (03)
...


-- (2) Medication Prescriptions Total

SELECT
	count(distinct PATID) as nPatients,
	count(distinct CLMID) as nClaims,
	count(distinct gnrc_nm) as nGenericNames,
	count(distinct ahfsclss) as nClasses
FROM
	stanfordphs.optum_ses:145:v3_0:sample.rx_pharmacy:9 AS rx

-- 56M Patients
-- 2.8B Claims / Prescriptions
-- 3.8K Unique Generic Names
-- 610 Unique Classes of Medications


-- (3) Lab Results

SELECT
	count(distinct PATID) as nPatients,
	count(distinct LABCLMID) as nLabClaims,
	count(distinct LOINC_CD) as nLOINCCodes,
	count(*) as nRows
FROM
	stanfordphs.optum_ses:145:v3_0:sample.laboratory_results:1 AS lr

-- 26M patients
-- 3.5B rows of data
-- 2.0B unique lab claim IDs
-- 12K unique LOINC codes


-- Break down by year, relatively stable over years
SELECT
	extract(YEAR from fst_dt) as labYear,
	count(distinct PATID) as nPatients,
	count(distinct LABCLMID) as nLabClaims,
	count(distinct LOINC_CD) as nLOINCCodes,
	count(*) as nRows
FROM
	stanfordphs.optum_ses:145:v3_0:sample.laboratory_results:1 AS lr
GROUP BY
  labYear
ORDER BY
  labYear DESC
	

-- Those with a Hemoglobin A1c result based on LOINC Code
SELECT
	count(distinct PATID) as nPatients,
	count(distinct LABCLMID) as nLabClaims,
	count(distinct LOINC_CD) as nLOINCCodes,
	count(*) as nRows
FROM
	stanfordphs.optum_ses:145:v3_0:sample.laboratory_results:1 AS lr
WHERE 
	LOINC_CD in ('4548-4H','17856-6')
ORDER BY
  nPatients DESC

-- 400K Patients
-- 1.5M Lab Claims




-- (4) Diagnoses
SELECT
	count(distinct PATID) as nPatients,
	count(distinct CLMID) as nClaims,
	count(distinct DIAG) as nDiagnoses
FROM
	stanfordphs.optum_ses:145:v3_0:sample.medical_diagnosis:11 AS dx

-- 62M patients
-- 2.9B claims
-- 53K unique diagnosis codes


-- Top Diagnosis Codes
SELECT
  dl.DIAG_DESC,
	dl.DIAG_CD,
	dl.ICD_VER_CD,
  count(distinct PATID) as nPatients,
	count(distinct CLMID) as nClaims
	--md.DIAG,
	--md.ICD_FLAG
FROM
	stanfordphs.optum_ses:145:v3_0:sample.medical_diagnosis:11 AS md
	INNER JOIN 
	stanfordphs.optum_diagnosis_lookup:8:v1_1.optum_diagnosis_lookup:1 AS dl
	  ON (md.`DIAG` = dl.`DIAG_CD`)
	  AND (md.`ICD_FLAG` = dl.`ICD_VER_CD`)
WHERE 
   DIAG_DESC like '%DIABETES%' OR
	 DIAG_DESC like '%DM%' OR
	 DIAG_DESC like '%ANEMIA%' OR
	 DIAG_DESC like '%THYROID%'
GROUP BY
  dl.DIAG_DESC,
	dl.DIAG_CD,
	dl.ICD_VER_CD
ORDER BY 
  nPatients DESC
	


-- Category related diagnoses
SELECT
  count(distinct PATID) as nPatients,
	count(distinct CLMID) as nClaims
FROM
	stanfordphs.optum_ses:145:v3_0:sample.medical_diagnosis:11 AS md
	INNER JOIN 
	stanfordphs.optum_diagnosis_lookup:8:v1_1.optum_diagnosis_lookup:1 AS dl
	  ON (md.`DIAG` = dl.`DIAG_CD`)
	  AND (md.`ICD_FLAG` = dl.`ICD_VER_CD`)
WHERE 
	-- DIAG_CD in ('2859','D649','2809','D509','2851','2800') -- Most common Anemia related
	-- DIAG_CD in ('E039','2449','2448','2469','7945','E038','E079') -- Most common thyroid related
	DIAG_CD in ('E119','E1165','E1122','E1142','E1140','E1169','E118') -- Most common diabetes related
ORDER BY 
  nPatients DESC


-- Anemia: 6.7M Patients, 52M claims
-- Thyroid: 6.8M Patients, 66M claims
-- Diabetes: 3.8M Patients, 65M claims
				


-- (?) Break down by provider type? Doesn't work well. Provider.Taxonomy1 is null for 5.8M out of 9.1M and then sparse distribution from there

