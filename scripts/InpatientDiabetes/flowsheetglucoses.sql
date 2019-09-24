SELECT rit_uid, row_disp_name, meas_value  FROM `mining-clinical-decisions.starr_datalake2018.flowsheet`

WHERE (lower(row_disp_name) IN ('bedside fs glucose (mg/dl)', 'diabetes', 'diabetic control', 'diabetic type', 'glucose'))

ORDER BY row_disp_name, rit_uid 

LIMIT 10000

-- Bedside FS Glucose (mg/dL)
-- Blood sugar range: useless 
-- Diabetes Mellitus: useless 
-- Diabetes
-- Diabetic Control: "controlled" or "uncontrolled"
-- Diabetic Type: Type 1, Type 2, null, Type 2 Simultaneous filing, Type 2 Added and corrected by GA   
-- Glu: 19 values
-- Glucose: urinary (trace, null, negative, 0, 1+), also serum values w/ nursing comments
-- Glucose > 249 : useless 
