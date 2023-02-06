/********************************************************************************************
Purpose: Tests to link clinical and cost data for GI procedure DRG admissions
Author: Selina Pi
Date run: 1/27/23-1/29/23
Notes:
-- SQL queries under each "#" comment should be copied and run separately in BigQuery editor
********************************************************************************************/

# Get total direct costs linked to anon_id and anonymized IP admission/discharge dates
SELECT  
  b.anon_id, 
  a.AdmitDate + b.jitter as adm_date_jittered, 
  a.DischargeDate + b.jitter as disch_date_jittered, 
  a.VisitCount, 
  a.MSDRGWeight, 
  a.Inpatient_C, 
  a.ServiceCategory_C, 
  a.Cost_Direct 
FROM `som-nero-phi-jonc101-secure.shc_cost.costUB` a 
LEFT JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map_2021` b 
ON cast(a.mrn AS string) = b.mrn 
 
 
# For cohort: Get total direct costs linked to anon_id and anonymized IP admission/discharge dates for cohort 
WITH  
gi_adms AS  
( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered as observation_id,  
    a.hosp_adm_date_jittered as adm_date, 
    a.hosp_disch_date_jittered as disch_date, 
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
  WHERE b.drg_mpi_code IN ('221', '245', '247') AND b.drg_id LIKE '2%' 
), 
 
Shc_costs AS 
( 
  SELECT  
    b.anon_id, 
    a.AdmitDate + b.jitter as adm_date_jittered, 
    a.DischargeDate + b.jitter as disch_date_jittered, 
    a.VisitCount, 
    a.MSDRGWeight, 
    a.Inpatient_C, 
    a.ServiceCategory_C, 
    a.Cost_Direct 
  FROM `som-nero-phi-jonc101-secure.shc_cost.costUB` a 
  LEFT JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map_2021` b 
  ON cast(a.mrn AS string) = b.mrn 
) 
 
SELECT * 
FROM gi_adms a 
LEFT JOIN Shc_costs b 
ON a.anon_id = b.anon_id AND a.adm_date = b.adm_date_jittered 
 
 
# Get costs and LOS in SHD cost data by DRG 
--Get anonymized admission DRG details 
WITH  
DRG_adms AS  
( 
  SELECT DISTINCT 
    a.anon_id,  
    a.pat_enc_csn_id_jittered as observation_id,  
    a.hosp_adm_date_jittered as adm_date, 
    a.hosp_disch_date_jittered as disch_date, 
    TIMESTAMP_DIFF(a.hosp_disch_date_jittered, a.hosp_adm_date_jittered, DAY) + 1 as LOS, 
    b.drg_mpi_code, 
    b.drg_id, 
    b.drg_name, 
    b.DRG_CODE_SET_C 
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a 
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b 
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded 
), 

--Link costs to anonymized ID 
SHC_costs AS 
( 
  SELECT  
    b.anon_id, 
    a.AdmitDate + b.jitter as adm_date_jittered, 
    a.DischargeDate + b.jitter as disch_date_jittered, 
    --a.VisitCount, 
    a.MSDRGWeight, 
    --a.Inpatient_C, 
    --a.ServiceCategory_C, 
    a.Cost_Direct 
  FROM `som-nero-phi-jonc101-secure.shc_cost.costUB` a 
  LEFT JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map_2021` b 
  ON cast(a.mrn AS string) = b.mrn 
) 

--Join admission DRG details and costs by patient ID and overlapping dates (NOTE: manually add all cost variables you want to keep; also consider filtering to inpatient-only costs after uncommenting the variable in the previous step [Inpatient_C = 'I']) 
SELECT DISTINCT 
  a.drg_mpi_code, 
  a.drg_id, 
  a.drg_name, 
  a.DRG_CODE_SET_C, 
  count(distinct observation_id) as ct_adms, 
  count(distinct a.anon_id) as ct_pts, 
  sum(Cost_Direct) as total_cost, 
  sum(Cost_Direct)/ count(distinct observation_id) as avg_adm_cost, 
  sum(LOS) as total_LOS, 
  sum(LOS)/ count(distinct observation_id) as avg_adm_los 
FROM DRG_adms a 
INNER JOIN SHC_costs b 
--ON a.anon_id = b.anon_id AND a.adm_date <= b.disch_date_jittered AND a.disch_date >= b.adm_date_jittered --Join by overlapping dates 
ON a.anon_id = b.anon_id AND a.adm_date <= b.adm_date_jittered AND b.disch_date_jittered <= a.disch_date --Join if cost dates are within IP admission dates 
GROUP BY  
    a.drg_mpi_code, 
    a.drg_id, 
    a.drg_name, 
    a.DRG_CODE_SET_C 
ORDER BY 
    ct_adms desc 
 
