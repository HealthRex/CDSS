/********************************************************************************************
Purpose: Initial BigQuery explorations for selecting DRG codes associated with higher length of stay (LOS) 
  burden at SHC to focus on in rotation project
Author: Selina Pi
Date run: 1/16/23
Notes: 
-- SQL queries under each "#" comment should be copied and run separately in BigQuery editor
-- Outcomes: DRGs for septicemia and knee or hip joint replacement high number of hospitalizations in the shc_core_2021 dataset. 
  However, the LOS for knee or hip joint replacement was low. DRG 220 (major stomach, esophageal & duodenal procedures) had
  relatively high average LOS and standard deviation and sufficiently high case count across the entire data.
********************************************************************************************/

# Identify the most common DRGs: Number of admissions by DRG 
SELECT drg_id, 
  drg_name, 
  count(distinct anon_id) as pt_ct, 
  count(distinct pat_enc_csn_id_coded) as case_ct 
FROM `som-nero-phi-jonc101.shc_core_2021.drg_code` 
GROUP BY drg_id, drg_name 
ORDER BY case_ct desc 
 
# Analyze range of LOS 
SELECT DISTINCT 
  a.anon_id,  
  a.pat_enc_csn_id_jittered,  
  TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
  b.drg_id, 
  b.drg_name 
FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 

# Combining the above 2 queries, get number of admissions and LOS summary statistics by DRG  
SELECT DISTINCT drg_mpi_code, 
  count(distinct anon_id) as pt_ct,  
  count(distinct pat_enc_csn_id_jittered) as case_ct, 
  avg(LOS) as mean_LOS, 
  min(LOS) as min_LOS, 
  max(LOS) as max_LOS, 
  stddev(LOS) as sd_LOS 
FROM ( 
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
) 
GROUP BY drg_mpi_code 
ORDER BY case_ct desc 
 
