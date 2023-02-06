/********************************************************************************************
Purpose: Sanity checks for filtering to gastrointestinal (GI) procedure hospitalizations
Author: Selina Pi
Date run: 1/16/23-1/17/23
Notes: 
-- SQL queries under each "#" comment should be copied and run separately in BigQuery editor
-- Redacted patient IDs are indicated by [FILL IN]
-- APR-DRG 220-284: GI tract hospitalizations 
********************************************************************************************/

# Test selecting GI tract hospitalizations. Results: Weird, Cardiovascular hospitalizations show up 
SELECT DISTINCT 
  a.anon_id,  
  a.pat_enc_csn_id_jittered,  
  TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
  b.drg_mpi_code, 
  b.drg_id, 
  b.drg_name 
FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
WHERE '220' <= b.drg_mpi_code AND b.drg_mpi_code <= '284' 
 
 
# Look for duplicates in DRG. Results: Multiple DRG systems; digestive ones have drg_id of 2XXX; choose DRG MPI code of 221, 230, 231 for small or large bowel procedures; 245 for IBD; 247 for intestinal obstruction 
SELECT 
  drg_mpi_code, 
  drg_id, 
  drg_name, 
  drg_code_set_c, 
  count(distinct pat_enc_csn_id_coded) as case_ct 
FROM `som-nero-phi-jonc101.shc_core_2021.drg_code` 
WHERE '220' <= drg_mpi_code AND drg_mpi_code <= '284' 
GROUP BY drg_mpi_code, drg_id, drg_name, drg_code_set_c 
ORDER BY drg_mpi_code, drg_id 


# Get relevant GI hospitalizations 
SELECT DISTINCT 
  a.anon_id,  
  a.pat_enc_csn_id_jittered,  
  TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
  b.drg_mpi_code, 
  b.drg_id, 
  b.drg_name, 
  b.DRG_CODE_SET_C 
FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
WHERE b.drg_mpi_code IN ('221', '230', '231', '245', '247') AND b.drg_id LIKE '2%' 
 
 
# Get relevant GI tract hospitalizations summary stats (using wrapped code from step above) 
WITH  
gi_adms AS  
( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered,  
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
  WHERE b.drg_mpi_code IN ('221', '230', '231', '245', '247') AND b.drg_id LIKE '2%' 
) 

SELECT drg_mpi_code, 
  drg_id,  
  drg_name,  
  count(distinct anon_id) as pt_ct,  
  count(distinct pat_enc_csn_id_jittered) as case_ct, 
  avg(LOS) as mean_LOS, 
  min(LOS) as min_LOS, 
  max(LOS) as max_LOS, 
  stddev(LOS) as sd_LOS 
FROM gi_adms 
GROUP BY drg_mpi_code, drg_id, drg_name 
ORDER BY case_ct desc 

 
# Get sample of GI hospitalization order sets to understand (adapting code from step above) 
WITH  
gi_adms AS  
( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered,  
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
  WHERE b.drg_mpi_code IN ('221', '245', '247') AND b.drg_id LIKE '2%' 
  LIMIT 100 
) 
 
SELECT * 
FROM `som-nero-phi-jonc101.shc_core_2021.proc_orderset` 
WHERE pat_enc_csn_id_coded in (SELECT DISTINCT pat_enc_csn_id_jittered from gi_adms) 
LIMIT 20 
 

# Take 2 patients from above with a given protocol ID to see what specific examples look like
SELECT *  
FROM `som-nero-phi-jonc101.shc_core_2021.order_proc`  
WHERE order_proc_id_coded IN ([FILL IN], [FILL IN])


# What are the most common diagnosis codes in our GI patient sample? ***[DX RESULT REDACTED]
WITH  
gi_adms AS  
  ( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered,  
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
  WHERE b.drg_mpi_code IN ('221', '245', '247') AND b.drg_id LIKE '2%' 
) 
 
SELECT DISTINCT  
  dx_id,  
  dx_name,  
  icd9,  
  icd10, 
  count(distinct anon_id) as pt_ct,  
  count(distinct pat_enc_csn_id_jittered) as case_ct 
FROM `som-nero-phi-jonc101.shc_core_2021.diagnosis`  
WHERE pat_enc_csn_id_jittered in (select pat_enc_csn_id_jittered from gi_adms) 
GROUP BY dx_id, dx_name, icd9, icd10 
ORDER BY pt_ct desc 
 
 
# What are the most common order sets in our GI patient sample? ***[ORDER SET RESULT REDACTED]
WITH  
gi_adms AS  
( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered,  
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
  WHERE b.drg_mpi_code IN ('221', '245', '247') AND b.drg_id LIKE '2%' 
) 
 
SELECT DISTINCT 
  protocol_id, 
  protocol_name, 
  count(distinct anon_id) as pt_ct,  
  count(distinct pat_enc_csn_id_coded) as case_ct 
FROM `som-nero-phi-jonc101.shc_core_2021.proc_orderset` 
WHERE pat_enc_csn_id_coded in (select pat_enc_csn_id_jittered from gi_adms) 
GROUP BY protocol_id, protocol_name 
ORDER BY pt_ct desc 
 
 
# What are the most common procedures in our GI patient sample? ***[PROCEDURE RESULT REDACTED] 
WITH  
gi_adms AS  
( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered,  
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
  WHERE b.drg_mpi_code IN ('221', '245', '247') AND b.drg_id LIKE '2%' 
)
 
SELECT DISTINCT 
  px_id, 
  code, 
  description, 
  code_type, 
  count(distinct anon_id) as pt_ct,  
  count(distinct pat_enc_csn_id_coded) as case_ct 
FROM `som-nero-phi-jonc101.shc_core_2021.procedure` 
WHERE pat_enc_csn_id_coded in (select pat_enc_csn_id_jittered, from gi_adms) 
GROUP BY px_id, code, description, code_type 
ORDER BY pt_ct desc 
