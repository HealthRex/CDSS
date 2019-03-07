/*
SELECT department_name, department_id
FROM datalake_47618.dep_map
WHERE department_name like ("EMER%")
ORDER BY department_name
*/

#EMERGENCY DEPARTMENT, 2001002 
#EMERGENCY DEPT, 320	

# returns different types of order types 
/*
SELECT order_type 
FROM datalake_47618.order_proc
GROUP BY order_type
ORDER BY order_type
*/

# sub query for population that recieved IV (tpa) 
#IV Thrombolytic Therapy Stroke

 /*
  SELECT a.department_id, a.pat_enc_csn_id_coded, a.jc_uid, a.contact_date_jittered #, b.department_name
  FROM datalake_47618.encounter as a
  #JOIN datalake_47618.dep_map as b
  #ON a.department_id = b.department_id
  WHERE pat_enc_csn_id_coded 
  IN ( 
              SELECT pat_enc_csn_id_coded 
                    FROM (
                    SELECT rit_uid, ss_sg_name, pat_enc_csn_id_coded 	
                    FROM datalake_47618.med_orderset
                    WHERE ss_sg_name in ( 'IV Thrombolytic Therapy Stroke', 
                                          'Thrombolysis Infusions',
                                          'Thrombolysis with Alteplase',
                                          'Thrombolysis with Alteplase and Heparin',
                                          'Thrombolysis Infusions'
                                          ) 
                    )
              )
              
 # AND department_id in (2001002, 320) 
*/

/*
SELECT ss_sg_name
FROM datalake_47618.med_orderset
WHERE ss_sg_name like "Hepar%"
GROUP BY ss_sg_name
ORDER BY ss_sg_name
*/
# Heparin
# Heparin -  Acute Coronary Syndrome
# Heparin - Atrial Fibrillation ( A-Fib & INR < 2)
# Heparin - Atrial Fibrillation ( A-Fib & INR > 2)
# Heparin - Atrial Fibrillation ( A-Fib & Therapeutic INR > 2)
# Heparin - Atrial Fibrillation ( A-Fib & INR > OR =  2)
# Heparin - Atrial Fibrillation ( A-Fib & Therapeutic INR > 2)
# Heparin - Cardiac Electrophysiology
# Heparin - DVT/PE
# Heparin - DVT/PE (General)
# Heparin - DVT/PE (HIGH Bleeding RISK/POST-PROCEDURE)
# Heparin - DVT/PE (High Bleeding Risk/Post-procedure)
# Heparin - DVT/PE (Post-procedure)
# Heparin - High Bleeding Risk
# Heparin - Mechanical Heart Valve ( INR is NOT Therapeutic )
# Heparin IV Infusion Protocols
# Heparin IV infusion
# Heparin Infusion
# Heparin Infusion Protocols
# Heparin and Alteplase Infusions
# Alteplase Protocol for Arterial and DVT Thrombolysis: High Dose (0.05 mg/mL)
# Alteplase Protocol for Arterial and DVT Thrombolysis: High-Volume; Low-Dose (0.01 mg/mL)
# Alteplase Protocol for Arterial and DVT Thrombolysis: High-Volume; Low-Dose (0.01mg/mL)
# Alteplase Protocol for Arterial and DVT Thrombolysis: Low-Volume; Low-Dose (0.02 mg/mL)
# Thrombolysis with Alteplase
# Thrombolysis with Alteplase and Heparin
# Thrombolysis Infusions
# IV Thrombolytic Therapy Stroke

/*
tPA sample Dataset for Diagnosis Matrix
2.1 Extract and merged 2,000,000 rows of MEDICATION (5% of MEDICATION) and 12,000,000 rows of DIAGNOSIS ( about 17%)
2.2 Filtered by Medication_Pharmaceutical_Subclass = Thrombolytic - Tissue Plasminogen Activators (1769 Medications) or Medication_ Pharmaceutical _Class =THROMBOLYTIC ENZYMES or Medication Name contains Alteplase, Reteplase or Tenecteplase. Then filtered by Diagnosis Name include any “stroke”(ignore case) and excluded any “sunstroke”. 220 rows remains. This does not exclude ICD codes such as history of stroke or encounter type of stroke like office visit or telephone.
2.3 Count the percentage of related columns
*/

# 9089987
/*
                    SELECT rit_uid, ss_sg_name, pat_enc_csn_id_coded, ss_section_name, protocol_name  	
                    FROM datalake_47618.med_orderset
                    WHERE ss_sg_name in ( 'IV Thrombolytic Therapy Stroke', 
                                          'Thrombolysis Infusions',
                                          'Thrombolysis with Alteplase',
                                          'Thrombolysis with Alteplase and Heparin'
                                          ) 
*/
# 314
/*
  SELECT a.department_id, a.pat_enc_csn_id_coded, a.jc_uid, a.contact_date_jittered, a.appt_type, a.visit_type 
  FROM datalake_47618.encounter as a
 # JOIN datalake_47618.dep_map as b
#  ON a.department_id = b.department_id
  WHERE pat_enc_csn_id_coded 
  IN ( SELECT pat_enc_csn_id_coded
        FROM (
                    SELECT rit_uid, ss_sg_name, pat_enc_csn_id_coded, ss_section_name, protocol_name  	
                    FROM datalake_47618.med_orderset
                    WHERE ss_sg_name in ( 'IV Thrombolytic Therapy Stroke', 
                                          'Thrombolysis Infusions',
                                          'Thrombolysis with Alteplase',
                                          'Thrombolysis with Alteplase and Heparin',
                                          'Alteplase Protocol for Arterial and DVT Thrombolysis: High Dose (0.05 mg/mL)',
                                          'Alteplase Protocol for Arterial and DVT Thrombolysis: High-Volume; Low-Dose (0.01 mg/mL)',
                                          'Alteplase Protocol for Arterial and DVT Thrombolysis: High-Volume; Low-Dose (0.01mg/mL)',
                                          'Alteplase Protocol for Arterial and DVT Thrombolysis: Low-Volume; Low-Dose (0.02 mg/mL)'
                                           )
                                          ))

#AND a.department_id in (2001002, 320) 
*/

/*
  SELECT a.department_id, a.pat_enc_csn_id_coded, a.jc_uid, a.contact_date_jittered, a.appt_type, a.visit_type 
  FROM datalake_47618.encounter as a
  WHERE jc_uid 
  IN ( SELECT jc_uid
        FROM (
SELECT rit_uid as jc_uid, pat_enc_csn_id_coded, ss_section_name, ss_sg_name
FROM `datalake_47618.proc_orderset`  
WHERE ss_section_name like "STROKE%"))
*/
# jc_uid, pat_enc_csn_id_coded, order_med_id_coded, medication_id, 


# stroke population: 

SELECT *
FROM (
      SELECT jc_uid, pat_enc_csn_id_coded, department_id, enc_type, appt_type
      FROM `datalake_47618.encounter` 
      WHERE 
      jc_uid IN (
            SELECT distinct jc_uid
            FROM (
                  SELECT jc_uid, pat_enc_csn_id_coded, order_med_id_coded, medication_id, med_description 
                  FROM `datalake_47618.order_med` 
                  WHERE med_description like 'ALTEPLASE %'
                 )
      )
)
WHERE department_id in (2001002, 320)

# 27821


#GROUP BY med_description
#ORDER BY med_description 




