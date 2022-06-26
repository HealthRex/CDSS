-- Pts with “bone marrow transplant” Dx: 229740 —> 4371 distinct patients

SELECT distinct(jc_uid) from `starr_datalake2018.diagnosis_code` 
WHERE UPPER(dx_name) LIKE '%BONE MARROW%' AND UPPER(dx_name) LIKE '%TRANSPLANT%’
