CREATE OR REPLACE TABLE `som-nero-phi-jonc101.francois_db.cost_drg` AS (
WITH
drg_tab AS (
SELECT DISTINCT
      a.anon_id, 
      a.pat_enc_csn_id_jittered as observation_id,
      a.hosp_adm_date_jittered as adm_date_jittered, 
      a.hosp_disch_date_jittered as disch_date_jittered,
      --b.drg_mpi_code,
      b.drg_id,
      b.drg_name,
      --b.DRG_CODE_SET_C,
      --b.drg_weight
  FROM `som-nero-phi-jonc101.shc_core_2021.f_ip_hsp_admission` a
  LEFT JOIN `som-nero-phi-jonc101.shc_core_2021.drg_code` b
  ON a.anon_id = b.anon_id AND a.pat_enc_csn_id_jittered = b.pat_enc_csn_id_coded
  WHERE EXTRACT(YEAR FROM a.hosp_disch_date_jittered) >= 2019
),

cost_tab AS (
  SELECT 
    b.anon_id,
    a.AdmitDate + b.jitter as adm_date_jittered,
    a.DischargeDate + b.jitter as disch_date_jittered,
    EXTRACT(YEAR FROM a.DischargeDate) AS discharge_year,
    --a.MSDRGWeight,
    a.Cost_Direct_Scaled,
    a.Cost_Indirect_Scaled,
    a.Cost_Total_Scaled,
    --a.Cost_Breakdown_OrganAcq_Scaled
  FROM `som-nero-phi-jonc101-secure.shc_cost.costUB` a
  LEFT JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map_2021` b
  ON LPAD(CAST(a.mrn AS string), 8, '0') = b.mrn
  WHERE a.Inpatient_C = 'I'
)

SELECT a.*, b.observation_id, b.drg_id, b.drg_name
FROM cost_tab as a INNER JOIN drg_tab as b 
ON a.anon_id = b.anon_id 
AND a.adm_date_jittered = b.adm_date_jittered
AND a.disch_date_jittered = b.disch_date_jittered
)