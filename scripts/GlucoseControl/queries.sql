--ID
SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null)
      ORDER BY
        a.rit_uid


--ID (new version)
SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null)
      ORDER BY
        a.rit_uid


--ID, gender, date of birth
SELECT 
  DISTINCT a.rit_uid, 
  c.gender, DATE(CAST(c.birth_date_jittered as TIMESTAMP)) as dob
FROM 
  `datalake_47618.lab_result` as a
  JOIN 
    `datalake_47618.demographic` as c on a.rit_uid=c.rit_uid
WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null)
ORDER BY
  a.rit_uid


--Weights
SELECT fs.rit_uid, fs.inpatient_data_id_coded, fs.template, fs.row_disp_name, fs.meas_value, fs.recorded_time_jittered
FROM 
  `datalake_47618.flowsheet` as fs
WHERE
   lower(fs.row_disp_name) like '%weight%'
   AND 
   fs.recorded_time_jittered > '2014-01-01'
   AND
   NOT SAFE_CAST(fs.meas_value AS FLOAT64) is null
   AND 
   fs.rit_uid in 
          (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null)
      ORDER BY
        a.rit_uid
            )
ORDER BY
   fs.recorded_time_jittered


--Lab test: GLU
SELECT 
  e.rit_uid, e.pat_enc_csn_id_coded, e.taken_time_jittered, e.ord_value, e.reference_unit, e.result_in_range_yn, SAFE_CAST(e.ord_value AS int64) as result

FROM 
  `datalake_47618.lab_result` as e

WHERE

  e.rit_uid in 
          (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))

  AND
   e.taken_time_jittered > '2014-01-01'  
   AND
    lower(e.lab_name) like '%glucose by meter%' 
    -- AND ((SAFE_CAST(e.ord_value AS float64) > 180) OR (SAFE_CAST(e.ord_value AS float64)<70)) )
   -- OR 
   -- (lower(e.lab_name) like '%a1c%' AND SAFE_CAST(e.ord_value AS float64) >6.5) 
   -- )

ORDER BY
  e.rit_uid, e.taken_time_jittered, e.pat_enc_csn_id_coded


--Lab test: A1c
SELECT 
  e.rit_uid, e.pat_enc_csn_id_coded, e.lab_name, e.taken_time_jittered, e.ord_value, e.reference_unit, e.result_in_range_yn, SAFE_CAST(e.ord_value AS int64) as result

FROM 
  `datalake_47618.lab_result` as e

WHERE

  e.rit_uid in 
          (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))

  AND
   e.taken_time_jittered > '2014-01-01'  
   AND
    lower(e.lab_name) like '%a1c%' 
    -- AND ((SAFE_CAST(e.ord_value AS float64) > 180) OR (SAFE_CAST(e.ord_value AS float64)<70)) )
   -- OR 
   -- (lower(e.lab_name) like '%a1c%' AND SAFE_CAST(e.ord_value AS float64) >6.5) 
   -- )

ORDER BY
  e.rit_uid, e.taken_time_jittered, e.pat_enc_csn_id_coded



--Common lab tests (patient)
SELECT 
lr.lab_name,
COUNT(DISTINCT lr.rit_uid) as total

FROM 
  `datalake_47618.lab_result` as lr

WHERE
  lr.rit_uid in 
          (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))

  AND
   lr.taken_time_jittered > '2014-01-01'  

GROUP BY
          lr.lab_name
ORDER BY
          COUNT(DISTINCT lr.rit_uid) DESC
LIMIT 
  100;

--Common lab tests (order)
SELECT 
lr.lab_name,
COUNT(DISTINCT lr.order_id_coded) as total

FROM 
  `datalake_47618.lab_result` as lr

WHERE
  lr.rit_uid in 
          (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))

  AND
   lr.taken_time_jittered > '2014-01-01'  

GROUP BY
          lr.lab_name
ORDER BY
          COUNT(DISTINCT lr.order_id_coded) DESC
LIMIT 
  100;


--Order Insulin

SELECT c.jc_uid, c.order_med_id_coded, CAST(c.sig as FLOAT64) as sig, c.dose_unit, 
c.taken_time_jittered, d.med_description, d.freq_display_name 
FROM 
  `datalake_47618.mar` as c
JOIN 
  `datalake_47618.order_med` as d ON c.order_med_id_coded=d.order_med_id_coded
WHERE
  c.jc_uid IN (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))
    AND
    (
    (lower(d.med_description) like '%insulin%'
    AND
    lower(c.route) like '%subcutaneous%')
    )
    AND 
    lower(c.mar_action) like 'given'
    AND 
    c.taken_time_jittered > '2014-01-01'
   
ORDER BY
    c.jc_uid, c.taken_time_jittered; 


--Order Steroid

SELECT c.jc_uid, c.order_med_id_coded, CAST(c.sig as FLOAT64) as sig, c.dose_unit, 
c.route, --c.infusion_rate, c.mar_duration, 
c.taken_time_jittered, d.med_description, d.freq_display_name 
FROM 
  `datalake_47618.mar` as c
JOIN 
  `datalake_47618.order_med` as d ON c.order_med_id_coded=d.order_med_id_coded
WHERE
  c.jc_uid IN (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))
    AND NOT c.sig is null
    AND
    (
    lower(d.med_description) like '%hydrocortisone%' 
--     OR 
--     lower(d.med_description) like '%prednisone%'  
--     OR 
--     lower(d.med_description) like '%methylprednisolone%' 
--     OR 
--     lower(d.med_description) like '%dexamethasone%'  
    )
    AND 
    lower(c.mar_action) like 'given'
    AND 
    c.taken_time_jittered > '2014-01-01'
   
ORDER BY
    c.jc_uid, c.taken_time_jittered; 


--Diet 

SELECT c.jc_uid, c.order_proc_id_coded, c.pat_enc_csn_id_coded,
c.proc_start_time_jittered,
c.description
FROM 
  `datalake_47618.order_proc` as c
WHERE
  c.jc_uid IN (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))
    AND
    (NOT lower(c.order_status) like '%canceled%')
    AND
    (lower(c.ordering_mode) like '%inpatient%')
    AND
    (
    (lower(c.description) like '%npo%'
    OR
    lower(c.description) like '%diet%')
    )
    AND 
    c.proc_start_time_jittered > '2014-01-01'
   
ORDER BY
    c.jc_uid, c.proc_start_time_jittered; 


--Diet (updated: not used, just for comparison)
SELECT c.jc_uid, c.order_proc_id_coded, c.pat_enc_csn_id_coded,
c.proc_start_time_jittered,
c.description
FROM 
  `datalake_47618.order_proc` as c
WHERE
  c.jc_uid IN (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like 'glucose by meter' 
                AND (a.ord_num_value > 200) OR (a.ord_num_value<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND a.ord_num_value >6.5) 
               
               AND NOT (a.ord_num_value is null))
    AND
    lower(c.ordering_mode) like 'inpatient'
    AND 
    c.proc_start_time_jittered > '2014-01-01'
   
ORDER BY
    c.jc_uid, c.proc_start_time_jittered; 



-- Kidney: CREATININE 
--Lab test: creatinine
SELECT 
  e.rit_uid, e.pat_enc_csn_id_coded, e.lab_name, e.taken_time_jittered, e.ord_num_value, e.reference_unit, e.result_in_range_yn

FROM 
  `datalake_47618.lab_result` as e

WHERE

  e.rit_uid in 
          (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a 
              -- JOIN
              -- `datalake_47618.order_proc` as b ON a.rit_uid=b.jc_uid
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               ((
               (lower(a.lab_name) like 'glucose by meter' 
                AND (a.ord_num_value > 200) OR (a.ord_num_value<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND a.ord_num_value >6.5)) 
               -- AND NOT
               -- lower(b.description) like '%hemodialysis%'
               AND NOT (a.ord_num_value is null))

  AND
   e.taken_time_jittered > '2014-01-01'  
   AND
    lower(e.lab_name) like '%creatinine%' 

ORDER BY
  e.rit_uid, e.taken_time_jittered, e.pat_enc_csn_id_coded


--Filter Hemodialysis (description) out
SELECT DISTINCT 
  b.jc_uid
FROM 
  `datalake_47618.order_proc` as b
WHERE
  lower(b.description) like '%hemodialysis%'
ORDER BY
  b.jc_uid;


--Diet (not used)

SELECT c.jc_uid, c.order_med_id_coded, 
CAST(c.sig as FLOAT64) as sig, c.dose_unit, 
c.taken_time_jittered, e.med_description, e.freq_display_name, 
d.ss_section_name, d.ss_sg_name, d.protocol_name 
FROM 
  `datalake_47618.mar` as c
JOIN 
  (`datalake_47618.med_orderset` as d ON c.order_med_id_coded=d.order_med_id_coded
  JOIN `datalake_47618.order_med` as e ON d.order_med_id_coded=e.order_med_id_coded)
WHERE
  c.jc_uid IN (SELECT DISTINCT a.rit_uid
            FROM 
              `datalake_47618.lab_result` as a
            WHERE
               a.taken_time_jittered > '2014-01-01' 
               AND
               (
               (lower(a.lab_name) like '%glucose by meter%' 
                AND ((SAFE_CAST(a.ord_value AS float64) > 200) OR (SAFE_CAST(a.ord_value AS float64)<70)) )
               OR 
               (lower(a.lab_name) like '%a1c%' AND SAFE_CAST(a.ord_value AS float64) >6.5) 
               )
               AND NOT (SAFE_CAST(a.ord_value AS float64) is null))
    AND
    (
    (lower(d.ss_section_name) like '%npo%'
    OR
    lower(d.ss_section_name) like '%diet%')
    )
    AND
    (
    (lower(e.med_description) like '%insulin%'
    AND
    lower(c.route) like '%subcutaneous%')
    )
    AND 
    lower(c.mar_action) like 'given'
    AND 
    c.taken_time_jittered > '2014-01-01'
   
ORDER BY
    c.jc_uid, c.taken_time_jittered; 







-------

SELECT DISTINCT
  *
FROM 
  `datalake_47618.lab_result` as a


 SELECT DISTINCT
         dem.rit_uid,
         DATE_DIFF(DATE('2016-01-01'), DATE(dem.birth_date_jittered), YEAR) as ageYears
       FROM
         starr_datalake2018.demographic AS dem JOIN  -- Create a shorthand table alias for convenience when referencing
         starr_datalake2018.encounter AS enc ON dem.rit_uid = jc_uid
       WHERE
         enc.appt_type = 'Anesthesia' AND
         enc.contact_date_jittered = '2016-01-01'