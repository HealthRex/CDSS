WHERE UPPER(lab_name) LIKE '%GLUCOSE%' 
AND (lab_name) NOT IN ( 'Glucose, Urine', 'Glucose Urine', 'Glucose, Fluid', "Est. Mean Glucose", "Glucose, CSF", "Collection Period Glucose", "Glucose Excretion", "Glucose Body Fluid", "Volume Glucose") 
AND UPPER(ordering_mode) = 'INPATIENT' AND ord_num_value BETWEEN 0 AND 9999998
