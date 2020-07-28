	
	
	
	
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
