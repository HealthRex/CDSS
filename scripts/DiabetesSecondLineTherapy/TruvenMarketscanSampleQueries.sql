	
	
-- Look for example Redbook / NDC lookup for outpatient prescriptions of all the different types of diabetes medications
-- https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/diagnosis-treatment/drc-20351199
SELECT 
    THERCLS, THERGRP, THRDTDS, THRCLDS, THRGRDS, GENNME,
		count(distinct NDCNUM) as n_NDC,
FROM stanfordphs.marketscan_redbook:14:v2_0.marketscan_redbook:1 AS rb
WHERE
	   GENNME like 'Metform%'
	OR GENNME like 'Glipizide%'
	OR GENNME like 'Glyburide%'
	OR GENNME like 'Glimepiride%'
	OR GENNME like 'Repaglinide%'
	OR GENNME like 'Nateglinide%'
	OR GENNME like 'Rosiglitazone%'
	OR GENNME like 'Pioglitazone%'
	OR GENNME like 'Sitagliptin%'
	OR GENNME like 'Saxagliptin%'
	OR GENNME like 'Linagliptin%'
	OR GENNME like 'Exenatide%'
	OR GENNME like 'Liraglutide%'
	OR GENNME like 'Semaglutide%'
	OR GENNME like 'Canagliflozin%'
	OR GENNME like 'Dapagliflozin%'
	OR GENNME like 'Empagliflozin'
	OR GENNME like 'Insulin%'
GROUP BY
    THERCLS, THERGRP, THRDTDS, THRCLDS, THRGRDS, GENNME
ORDER BY
    THERCLS, THERGRP, THRDTDS, THRCLDS, THRGRDS, GENNME,
	n_NDC desc
LIMIT 1000





-- Look for example Redbook / NDC lookup for outpatient prescriptions of all the different types of diabetes medications by class
-- https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/diagnosis-treatment/drc-20351199
SELECT 
    THERCLS, THERGRP, THRDTDS, THRCLDS, THRGRDS, GENNME,
		count(distinct NDCNUM) as n_NDC,
FROM stanfordphs.marketscan_redbook:14:v2_0.marketscan_redbook:1 AS rb
WHERE
	   THERCLS = 172 -- Insulins
	OR THERCLS = 174 -- Miscellaneous Diabetes Meds: Includes Metformin, GLP-1 (e.g., Exenatide), DDP-4 (e.g., Linagliptin) 
	OR THERCLS = 173 -- Sulfonylurea (e.g., glipizide)
	OR THERCLS = 268 -- Thiazolidinediones (e.g., rosiglitazone)
	OR THERCLS = 267 -- SGLT2 Inhibitor (e.g., empagliflozin)
	OR THERCLS = 266 -- Meglitinides (e.g., repaglinide)
GROUP BY
    THERCLS, THERGRP, THRDTDS, THRCLDS, THRGRDS, GENNME
ORDER BY
    THERCLS, THERGRP, THRDTDS, THRCLDS, THRGRDS, GENNME,
	n_NDC desc
LIMIT 1000



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
