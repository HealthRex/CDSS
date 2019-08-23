
/* SELECT rit_uid, lab_name, base_name, ord_value, ord_num_value FROM `starr_datalake2018.lab_result`  
  WHERE UPPER(lab_name) LIKE '%GLUCOSE%' AND (lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose") AND UPPER(ordering_mode) = 'INPATIENT' AND ord_num_value BETWEEN 0 AND 9999998 
  AND rit_uid IN (SELECT DISTINCT(rit_uid) FROM starr_datalake2018.treatment_team AS TT WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%"))
-- BGs of pts who have ever had BMT as primary treatment team
*/


-- Individual BGs of patients who had BMT as their primary team during this patient encounter
SELECT Lab.rit_uid, Lab.pat_enc_csn_id_coded, Lab.lab_name, Lab.base_name, Lab.ord_value, Lab.ord_num_value, Lab.order_id_coded FROM starr_datalake2018.lab_result AS Lab

WHERE Lab.order_id_coded IN (SELECT distinct (Lab.order_id_coded)FROM starr_datalake2018.treatment_team AS TT JOIN starr_datalake2018.lab_result AS Lab ON Lab.pat_enc_csn_id_coded = TT.pat_enc_csn_id_coded  
  WHERE Lab.pat_enc_csn_id_coded IN (SELECT DISTINCT(pat_enc_csn_id_coded) FROM starr_datalake2018.treatment_team AS TT WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%"))
  AND   
  (UPPER(Lab.lab_name) LIKE '%GLUCOSE%' AND (Lab.lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose") AND UPPER(Lab.ordering_mode) = 'INPATIENT' AND Lab.ord_num_value BETWEEN 0 AND 9999998)
)

AND   
  (UPPER(Lab.lab_name) LIKE '%GLUCOSE%' AND (Lab.lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose") AND UPPER(Lab.ordering_mode) = 'INPATIENT' AND Lab.ord_num_value BETWEEN 0 AND 9999998)

Order by Lab.order_id_coded, pat_enc_csn_id_coded



