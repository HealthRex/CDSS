-- Distinct pt encounters on the BMT service with DM coded —> 1242

SELECT count(distinct(pat_enc_csn_id_coded)) from `starr_datalake2018.diagnosis_code` 
  WHERE pat_enc_csn_id_coded IN (SELECT (pat_enc_csn_id_coded) from starr_datalake2018.treatment_team AS TT  
  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%") )
  AND UPPER(dx_name) LIKE '%DIABETES%'
