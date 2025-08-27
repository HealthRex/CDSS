Create or replace table  `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_Vitals` AS
WITH vitals as (
  SELECT c.*,
  vitals.recorded_time_jittered_utc as vitaltime,
  CASE WHEN upper(row_disp_name) IN ('PULSE', 'HEART RATE') THEN round(SAFE_CAST(numerical_val_1 AS FLOAT64),2) end as heartrate,
  CASE WHEN upper(row_disp_name) IN ('RESP', 'RESP RATE') THEN round(SAFE_CAST(numerical_val_1 AS FLOAT64),2) end as resprate,
  CASE WHEN upper(row_disp_name) IN ('TEMP') THEN round(SAFE_CAST(numerical_val_1 AS FLOAT64),2) end as tempt,
  CASE WHEN (upper(trim(row_disp_name)) IN ('BP', 'NIBP') AND SAFE_CAST(numerical_val_1 AS numeric) >= 40) THEN round(SAFE_CAST(numerical_val_1 AS FLOAT64),2) end as sysbp ,
  CASE WHEN (upper(trim(row_disp_name)) IN ('BP', 'NIBP') AND SAFE_CAST(numerical_val_2 AS numeric) >= 30)  THEN round(SAFE_CAST(numerical_val_2 AS FLOAT64),2) end as diasbp,
  FROM
    `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` c LEFT JOIN
  `som-nero-phi-jonc101.shc_core_2023.flowsheet` as vitals
   ON vitals.anon_id = c.anon_id
  WHERE
   ((upper(trim(row_disp_name)) IN ('PULSE', 'HEART RATE') AND SAFE_CAST(numerical_val_1 AS numeric) >= 30) OR -- Heart rate
   (upper(trim(row_disp_name)) in ('RESP', 'RESP RATE') AND SAFE_CAST(numerical_val_1 AS numeric) >= 4 AND SAFE_CAST(numerical_val_1 AS numeric) <= 60) OR -- Respiratory rate
   (upper(trim(row_disp_name)) IN ('TEMP') AND SAFE_CAST(numerical_val_1 AS numeric) >= 90) OR -- Temperature in F
   (upper(trim(row_disp_name)) IN ('WEIGHT') AND SAFE_CAST(numerical_val_1 AS numeric) >= 480 AND SAFE_CAST(numerical_val_1 AS numeric) <= 8000)  OR -- Weight 
  (upper(trim(row_disp_name)) IN ('BP', 'NIBP') AND SAFE_CAST(numerical_val_1 AS numeric) >= 40) OR -- Systolic BP
   (upper(trim(row_disp_name)) IN ('BP', 'NIBP') AND SAFE_CAST(numerical_val_2 AS numeric) >= 30) -- diastolic BP
  )
  AND
  (TIMESTAMP_DIFF(vitals.recorded_time_jittered_utc, c.order_time_jittered_utc, hour) between -48 and 0 )
),
vitalsQ as (
select anon_id,
       pat_enc_csn_id_coded,
       order_proc_id_coded,
       ROUND(APPROX_QUANTILES(heartrate, 100)[OFFSET(25)],2) AS Q25_heartrate,
       ROUND(APPROX_QUANTILES(heartrate, 100)[OFFSET(75)],2) AS Q75_heartrate,
       ROUND(APPROX_QUANTILES(heartrate, 100)[OFFSET(50)],2) AS median_heartrate,
       ROUND(APPROX_QUANTILES(resprate, 100)[OFFSET(25)],2) AS Q25_resprate,
       ROUND(APPROX_QUANTILES(resprate, 100)[OFFSET(75)],2) AS Q75_resprate,
       ROUND(APPROX_QUANTILES(resprate, 100)[OFFSET(50)],2) AS median_resprate,
       ROUND(APPROX_QUANTILES(tempt, 100)[OFFSET(25)],2) AS Q25_temp,
       ROUND(APPROX_QUANTILES(tempt, 100)[OFFSET(75)],2) AS Q75_temp,
       ROUND(APPROX_QUANTILES(tempt, 100)[OFFSET(50)],2) AS median_temp,
       ROUND(APPROX_QUANTILES(sysbp, 100)[OFFSET(25)],2) AS Q25_sysbp,
       ROUND(APPROX_QUANTILES(sysbp, 100)[OFFSET(75)],2) AS Q75_sysbp,
       ROUND(APPROX_QUANTILES(sysbp, 100)[OFFSET(25)],2) AS Q25_diasbp,
       ROUND(APPROX_QUANTILES(diasbp, 100)[OFFSET(75)]) AS Q75_diasbp,
       ROUND(APPROX_QUANTILES(diasbp, 100)[OFFSET(50)]) AS median_diasbp,
from vitals
group by anon_id,pat_enc_csn_id_coded,order_proc_id_coded
),
Vitalsfirstlast as (
select anon_id,
       pat_enc_csn_id_coded,
       order_proc_id_coded,

       Round(FIRST_VALUE(heartrate) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS first_heartrate,
    Round(LAST_VALUE(heartrate) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS last_heartrate,


        Round(FIRST_VALUE(resprate) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS first_resprate,
    Round(LAST_VALUE(resprate) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS last_resprate,


        Round(FIRST_VALUE(tempt) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS first_temp,  
    Round(LAST_VALUE(tempt) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS last_temp,


        Round(FIRST_VALUE(sysbp) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS first_sysbp,
    Round(LAST_VALUE(sysbp) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS last_sysbp,


        Round(FIRST_VALUE(diasbp) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS first_diasbp,
    Round(LAST_VALUE(diasbp) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY vitaltime
        ),2) AS last_diasbp,

from vitals
),
vitals_all as (
select a.*,
b.first_diasbp,b.last_diasbp,
b.last_sysbp,b.first_sysbp,
b.last_temp,b.first_temp,
b.last_resprate,b.first_resprate,
b.last_heartrate,b.first_heartrate
from Vitalsfirstlast b inner join 
vitalsQ a using (anon_id,pat_enc_csn_id_coded,order_proc_id_coded)
)
select distinct * from vitals_all
