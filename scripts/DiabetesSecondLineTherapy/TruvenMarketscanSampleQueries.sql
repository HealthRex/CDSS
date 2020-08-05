	
	
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



-- Count up patients and claims for prescriptions for diabetes related drug classes
-- Broken up by Year
SELECT
	pc.YEAR,
	pc.THERCLS,
	pc.THERGRP,
	-- rb.GENNME,
	count(distinct pc.PATID) as n_patients,
  count(distinct pc.SEQNUM) as n_claims

FROM
	stanfordphs.marketscan:142:v2_0:sample.outpatient_pharmaceutical_claims:7 AS pc
	   INNER JOIN
	stanfordphs.marketscan_redbook:14:v2_0.marketscan_redbook:1 AS rb ON (pc.`NDCNUM` = rb.`NDCNUM`)
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
	pc.THERGRP,
	rb.GENNME
ORDER BY
	pc.YEAR desc,
	-- rb.GENNME,
	n_patients desc

LIMIT 1000
