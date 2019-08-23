-- BGs of pts who have had BMT as primary treatment team

SELECT rit_uid, lab_name, base_name, ord_value, ord_num_value FROM `starr_datalake2018.lab_result`  
  WHERE UPPER(lab_name) LIKE '%GLUCOSE%' AND (lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose") AND UPPER(ordering_mode) = 'INPATIENT' AND ord_num_value BETWEEN 0 AND 9999998 
  AND rit_uid IN (SELECT DISTINCT(rit_uid) FROM starr_datalake2018.treatment_team AS TT WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%"))


