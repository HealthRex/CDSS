-- Distinct pts with BMT and DM coded —> 1018

SELECT count (DISTINCT(jc_uid)) from `starr_datalake2018.diagnosis_code` 
  WHERE jc_uid IN (SELECT (jc_uid) from `starr_datalake2018.diagnosis_code` 
    WHERE UPPER(dx_name) LIKE '%BONE MARROW%' AND UPPER(dx_name) LIKE '%TRANSPLANT%') 
  AND UPPER(dx_name) LIKE '%DIABETES%’
