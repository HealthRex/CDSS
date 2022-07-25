-- extract anon_ids and save the result in proj_cms_sf.costUB_with_anonid
SELECT B.mrn as mrn_in_codebook
      , B.anon_id
      , A.*
FROM `som-nero-phi-jonc101-secure.shc_cost.costUB` A
JOIN `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.codebook` B
ON CAST(A.MRN AS STRING) = B.mrn

-- Filter and save in costUB_with_anonid_filtered
SELECT *
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid` 
WHERE Inpatient ='Inpatient'
AND DATE_DIFF(DischargeDate, AdmitDate, DAY) >= 3

-- Find frequent base_names and save them in frequent_base_name
WITH dist_base_names AS
(
(SELECT DISTINCT B.base_name
      , A.anon_id
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
JOIN `som-nero-phi-jonc101.shc_core_2021.lab_result` B
ON A.anon_id = B.anon_id )
)
SELECT base_name
      , count(*) as num_patients
FROM dist_base_names
GROUP BY base_name
ORDER BY num_patients DESC

-- Find frequent base_names and save them in frequent_pharm_class_abbr
WITH dist_phr AS
(
(SELECT DISTINCT B.pharm_class_abbr
      , A.anon_id
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
JOIN `som-nero-phi-jonc101.shc_core_2021.order_med` B
ON A.anon_id = B.anon_id )
)
SELECT pharm_class_abbr
      , count(*) as num_patients
FROM dist_phr
GROUP BY pharm_class_abbr
ORDER BY num_patients DESC

-- Find frequent base_names and save them in frequent_proc_id
WITH dist_proc_id AS
(
(SELECT DISTINCT B.proc_id
      , A.anon_id
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
JOIN `som-nero-phi-jonc101.shc_core_2021.order_proc` B
ON A.anon_id = B.anon_id )
)
SELECT proc_id
      , count(*) as num_patients
FROM dist_proc_id
GROUP BY proc_id
ORDER BY num_patients DESC


-- icd10
WITH dist_icd10 AS
(
(SELECT DISTINCT B.icd10
      , A.anon_id
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
JOIN `som-nero-phi-jonc101.shc_core_2021.diagnosis` B
ON A.anon_id = B.anon_id )
)
SELECT icd10
      , count(*) as num_patients
FROM dist_icd10
GROUP BY icd10
ORDER BY num_patients DESC


--icd9
WITH dist_icd9 AS
(
(SELECT DISTINCT B.icd9
      , A.anon_id
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
JOIN `som-nero-phi-jonc101.shc_core_2021.diagnosis` B
ON A.anon_id = B.anon_id )
)
SELECT icd9
      , count(*) as num_patients
FROM dist_icd9
GROUP BY icd9
ORDER BY num_patients DESC

-- Extract lab results
SELECT B.anon_id
      , B.base_name
      , B.proc_code
      , B.result_flag
      , B.order_time_utc
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
INNER JOIN `som-nero-phi-jonc101.shc_core_2021.lab_result` B
ON A.anon_id = B.anon_id
WHERE base_name IN
(
      SELECT A.base_name
      FROM `som-nero-phi-jonc101-secure.proj_cms_sf.frequent_base_name` A
      WHERE A.base_name is not NULL
      ORDER BY num_patients DESC
      LIMIT 100
)


-- Extract diagnosis
SELECT B.anon_id
      , B.icd9
      , B.icd10
      , B.start_date_utc
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
INNER JOIN `som-nero-phi-jonc101.shc_core_2021.diagnosis` B
ON A.anon_id = B.anon_id
WHERE icd10 IN
(
      SELECT A.icd10
      FROM `som-nero-phi-jonc101-secure.proj_cms_sf.frequent_icd10` A
      WHERE A.icd10 IS NOT NULL
      ORDER BY num_patients DESC
      LIMIT 100
)
OR icd9 IN
(
      SELECT A.icd9
      FROM `som-nero-phi-jonc101-secure.proj_cms_sf.frequent_icd9` A
      WHERE A.icd9 IS NOT NULL
      ORDER BY num_patients DESC
      LIMIT 100
)



-- med
SELECT B.anon_id
      , B.pharm_class_abbr
      , B.order_time_jittered 
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
INNER JOIN `som-nero-phi-jonc101.shc_core_2021.order_med` B
ON A.anon_id = B.anon_id
WHERE pharm_class_abbr IN
(
      SELECT A.pharm_class_abbr
      FROM `som-nero-phi-jonc101-secure.proj_cms_sf.frequent_pharm_class_abbr` A
      WHERE A.pharm_class_abbr is not NULL
      ORDER BY num_patients DESC
      LIMIT 100
)

-- order_proc
SELECT B.anon_id
      , B.proc_id
      , B.ordering_date_jittered
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
INNER JOIN `som-nero-phi-jonc101.shc_core_2021.order_proc` B
ON A.anon_id = B.anon_id
WHERE proc_id IN
(
      SELECT A.proc_id
      FROM `som-nero-phi-jonc101-secure.proj_cms_sf.frequent_proc_id` A
      WHERE A.proc_id is not NULL
      ORDER BY num_patients DESC
      LIMIT 100
)


SELECT B.*
FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A
INNER JOIN `som-nero-phi-jonc101.shc_core_2021.demographic` B
ON A.anon_id = B.anon_id


-- ===================
-- Find descriptions

-- This script finds most frequent med_descriptions
WITH med_desc_freq AS
(
SELECT pharm_class_abbr
        , med_description
       , COUNT(DISTINCT anon_id) as num_patient
FROM `som-nero-phi-jonc101.shc_core_2021.order_med` 
WHERE pharm_class_abbr IS NOT NULL
GROUP BY pharm_class_abbr, med_description
)

SELECT pharm_class_abbr, med_description, num_patient
FROM med_desc_freq
WHERE TRUE
QUALIFY ROW_NUMBER() OVER (PARTITION BY pharm_class_abbr ORDER BY num_patient DESC) <= 5
ORDER BY pharm_class_abbr, num_patient DESC




-- Diagnosis
WITH diag_records AS
(SELECT A.*
        , B.CCSR_CATEGORY_1
        , B.Category_1_Description
        , B.ICD_10_CODE_Description
FROM `som-nero-phi-jonc101.shc_core_2021.diagnosis` A
LEFT JOIN  `mining-clinical-decisions.mapdata.ahrq_ccsr_diagnosis` B
ON A.icd10 = B.ICD10),

diag_desc_freq AS
(SELECT CCSR_CATEGORY_1
        , dx_name
       , COUNT(DISTINCT anon_id) as num_patient
FROM diag_records
WHERE CCSR_CATEGORY_1 IS NOT NULL
GROUP BY CCSR_CATEGORY_1, dx_name)

SELECT CCSR_CATEGORY_1, dx_name, num_patient
FROM diag_desc_freq
WHERE TRUE
QUALIFY ROW_NUMBER() OVER (PARTITION BY CCSR_CATEGORY_1 ORDER BY num_patient DESC) <= 5
ORDER BY CCSR_CATEGORY_1, num_patient DESC


--
WITH proc_desc_freq AS
(SELECT proc_id
       , description
       , COUNT(DISTINCT anon_id) as num_patient
FROM `som-nero-phi-jonc101.shc_core_2021.order_proc`  
WHERE proc_id IS NOT NULL
GROUP BY proc_id, description)

SELECT proc_id, description, num_patient
FROM proc_desc_freq
WHERE TRUE
QUALIFY ROW_NUMBER() OVER (PARTITION BY proc_id ORDER BY num_patient DESC) <= 5
ORDER BY proc_id, num_patient DESC

--
WITH lab_desc_freq AS
(SELECT base_name
       , lab_name
       , COUNT(DISTINCT anon_id) as num_patient
FROM `som-nero-phi-jonc101.shc_core_2021.lab_result` 
WHERE base_name IS NOT NULL
GROUP BY base_name, lab_name)

SELECT base_name, lab_name, num_patient
FROM lab_desc_freq
WHERE TRUE
QUALIFY ROW_NUMBER() OVER (PARTITION BY base_name ORDER BY num_patient DESC) <= 5
ORDER BY base_name, num_patient DESC

