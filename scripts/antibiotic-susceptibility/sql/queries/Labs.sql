CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_Labs` AS
WITH last2weeklabs AS (
    SELECT 
        c.*,
        lr.order_time_jittered_utc as labtime,
        14 as Period_Day,
        CASE 
            WHEN (LOWER(lr.base_name) = 'wbc' AND LOWER(lr.reference_unit) IN ('thousand/ul','k/ul','10x3/ul','10*3/ul','x10e3/ul')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'wbc' AND lr.reference_unit = '/uL' THEN SAFE_CAST(lr.ord_value AS FLOAT64)/1000
        END AS wbc,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE '%neutrophils%' AND lr.reference_unit = '%' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS neutrophils,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE '%lymphocytes%' AND lr.reference_unit = '%' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS lymphocytes,
        -- CASE WHEN LOWER(lr.base_name) LIKE '%bands%' THEN SAFE_CAST(lr.ord_value AS FLOAT64) END AS bands,
        CASE 
            WHEN LOWER(lr.base_name) = 'hgb' AND lr.reference_unit = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'hgb' AND LOWER(lr.reference_unit) = 'g/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64) * 1000
        END AS hgb,
        CASE 
            WHEN LOWER(lr.base_name) = 'plt' AND LOWER(lr.reference_unit) IN ('x10e3/ul','10x3/ul','k/ul','10*3/ul','thousand/ul') THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'plt' AND LOWER(lr.reference_unit) = 'ul' THEN SAFE_CAST(lr.ord_value AS FLOAT64) / 1000
        END AS plt,
        CASE 
            WHEN LOWER(lr.base_name) = 'na' AND LOWER(lr.reference_unit) = 'mmol/l' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS na,
        CASE 
            WHEN (LOWER(lr.base_name) = 'hco3' AND LOWER(lr.reference_unit) like any ('meq/l','mmol/l')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN (LOWER(lr.base_name) = 'co2' AND LOWER(lr.reference_unit) like any ('meq/l','mmol/l')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS hco3,      
        CASE 
            WHEN LOWER(lr.base_name) = 'bun' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS bun,
        CASE 
            WHEN LOWER(lr.base_name) = 'cr' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS cr,
        -- CASE WHEN LOWER(lr.base_name) LIKE 'glucose' THEN SAFE_CAST(lr.ord_value AS FLOAT64) END AS glucose,
        CASE 
            WHEN LOWER(lr.base_name) = 'lac' AND LOWER(lr.reference_unit) IN ('mmol/l', 'mmole/l') THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS lactate,               
        CASE 
            WHEN LOWER(lr.base_name) = 'crp' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'crp' AND LOWER(lr.reference_unit) = 'mg/l' THEN SAFE_CAST(lr.ord_value AS FLOAT64) / 10
        END AS crp,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE 'procalcitonin' AND LOWER(lr.reference_unit) = 'ng/ml' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS procalcitonin
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` c
    LEFT JOIN `som-nero-phi-jonc101.shc_core_2023.lab_result` lr 
    USING (anon_id, pat_enc_csn_id_coded)
    WHERE TIMESTAMP_DIFF(lr.order_time_jittered_utc, c.order_time_jittered_utc, Day) BETWEEN -14 AND 0
    and lr.ord_value is not null 
),
last2week_Quantiles as (
    SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    Period_Day,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(75)], 2) AS Q75_wbc,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(25)], 2) AS Q25_wbc,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(50)], 2) AS median_wbc,

    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(25)], 2) AS Q25_neutrophils,
    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(75)], 2) AS Q75_neutrophils,
    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(50)], 2) AS median_neutrophils,

    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(25)], 2) AS Q25_lymphocytes,
    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(75)], 2) AS Q75_lymphocytes,
    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(50)], 2) AS median_lymphocytes,

    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(25)], 2) AS Q25_hgb,
    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(75)], 2) AS Q75_hgb,
    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(50)], 2) AS median_hgb,

    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(25)], 2) AS Q25_plt,
    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(75)], 2) AS Q75_plt,
    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(50)], 2) AS median_plt,


    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(75)], 2) AS Q75_na,
    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(25)], 2) AS Q25_na,
    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(50)], 2) AS median_na,

    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(75)], 2) AS Q75_hco3,
    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(25)], 2) AS Q25_hco3,
    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(50)], 2) AS median_hco3,

    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(75)], 2) AS Q75_bun,
    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(25)], 2) AS Q25_bun,
    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(50)], 2) AS median_bun,

    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(75)], 2) AS Q75_cr,
    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(25)], 2) AS Q25_cr,
    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(50)], 2) AS median_cr,

    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(75)], 2) AS Q75_lactate,
    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(25)], 2) AS Q25_lactate,
    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(50)], 2) AS median_lactate,

    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(75)], 2) AS Q75_procalcitonin,
    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(25)], 2) AS Q25_procalcitonin,
    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(50)], 2) AS median_procalcitonin

    from last2weeklabs
    where wbc is not null
    or procalcitonin is not null 
    or lactate is not null 
    or cr is not null 
    or bun is not null 
    or hco3 is not null 
    or na is not null 
    or plt is not null 
    or hgb is not null 
    or lymphocytes is not null 
    or neutrophils is not null 
    group by anon_id,pat_enc_csn_id_coded,order_proc_id_coded,Period_Day

),
last2weekfirst_last as (
SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    Period_Day,
    Round(FIRST_VALUE(wbc) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY labtime
        ),2) AS first_wbc,
    Round(FIRST_VALUE(wbc) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY labtime
        ),2) AS last_wbc,
    
    
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_neutrophils,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_neutrophils,
   
    

    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_lymphocytes,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_lymphocytes,
    
    
    
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_hgb,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_hgb,
   
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_plt,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_plt,
   
    -- Na
    ROUND(FIRST_VALUE(na) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_na,
    ROUND(LAST_VALUE(na) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_na,
    

    ROUND(FIRST_VALUE(hco3) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_hco3,
    ROUND(LAST_VALUE(hco3) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_hco3,
    

    ROUND(FIRST_VALUE(bun) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_bun,
    ROUND(LAST_VALUE(bun) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_bun,
    

    ROUND(FIRST_VALUE(cr) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_cr,
    ROUND(LAST_VALUE(cr) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_cr,
    


    ROUND(FIRST_VALUE(lactate) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_lactate,
    ROUND(LAST_VALUE(lactate) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_lactate,
    

    ROUND(FIRST_VALUE(procalcitonin) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_procalcitonin,
    ROUND(LAST_VALUE(procalcitonin) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_procalcitonin,
    
FROM last2weeklabs
where wbc is not null
    or procalcitonin is not null 
    or lactate is not null 
    or cr is not null 
    or bun is not null 
    or hco3 is not null 
    or na is not null 
    or plt is not null 
    or hgb is not null 
    or lymphocytes is not null 
    or neutrophils is not null 
    ),
last2weekstats as (
select a.*,
b.first_procalcitonin,b.last_procalcitonin,
b.last_lactate,b.first_lactate,
b.last_cr,b.first_cr,b.last_bun,b.first_bun,b.last_hco3,b.first_hco3,b.last_na,b.first_na,b.last_plt,b.first_plt,
b.last_hgb,b.first_hgb,b.last_lymphocytes,b.first_lymphocytes,b.last_neutrophils,b.first_neutrophils,
b.last_wbc,b.first_wbc
from last2weekfirst_last b inner join 
last2week_Quantiles a using (anon_id,pat_enc_csn_id_coded,order_proc_id_coded,Period_Day)
),
---------------------------------------------------------------------------------
last4weeklabs AS (
    SELECT 
        c.*,
        lr.order_time_jittered_utc as labtime,
        14 as Period_Day,
        CASE 
            WHEN (LOWER(lr.base_name) = 'wbc' AND LOWER(lr.reference_unit) IN ('thousand/ul','k/ul','10x3/ul','10*3/ul','x10e3/ul')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'wbc' AND lr.reference_unit = '/uL' THEN SAFE_CAST(lr.ord_value AS FLOAT64)/1000
        END AS wbc,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE '%neutrophils%' AND lr.reference_unit = '%' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS neutrophils,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE '%lymphocytes%' AND lr.reference_unit = '%' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS lymphocytes,
        -- CASE WHEN LOWER(lr.base_name) LIKE '%bands%' THEN SAFE_CAST(lr.ord_value AS FLOAT64) END AS bands,
        CASE 
            WHEN LOWER(lr.base_name) = 'hgb' AND lr.reference_unit = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'hgb' AND LOWER(lr.reference_unit) = 'g/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64) * 1000
        END AS hgb,
        CASE 
            WHEN LOWER(lr.base_name) = 'plt' AND LOWER(lr.reference_unit) IN ('x10e3/ul','10x3/ul','k/ul','10*3/ul','thousand/ul') THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'plt' AND LOWER(lr.reference_unit) = 'ul' THEN SAFE_CAST(lr.ord_value AS FLOAT64) / 1000
        END AS plt,
        CASE 
            WHEN LOWER(lr.base_name) = 'na' AND LOWER(lr.reference_unit) = 'mmol/l' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS na,
        CASE 
            WHEN (LOWER(lr.base_name) = 'hco3' AND LOWER(lr.reference_unit) like any ('meq/l','mmol/l')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN (LOWER(lr.base_name) = 'co2' AND LOWER(lr.reference_unit) like any ('meq/l','mmol/l')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS hco3,      
        CASE 
            WHEN LOWER(lr.base_name) = 'bun' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS bun,
        CASE 
            WHEN LOWER(lr.base_name) = 'cr' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS cr,
        -- CASE WHEN LOWER(lr.base_name) LIKE 'glucose' THEN SAFE_CAST(lr.ord_value AS FLOAT64) END AS glucose,
        CASE 
            WHEN LOWER(lr.base_name) = 'lac' AND LOWER(lr.reference_unit) IN ('mmol/l', 'mmole/l') THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS lactate,               
        CASE 
            WHEN LOWER(lr.base_name) = 'crp' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'crp' AND LOWER(lr.reference_unit) = 'mg/l' THEN SAFE_CAST(lr.ord_value AS FLOAT64) / 10
        END AS crp,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE 'procalcitonin' AND LOWER(lr.reference_unit) = 'ng/ml' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS procalcitonin
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` c
    LEFT JOIN `som-nero-phi-jonc101.shc_core_2023.lab_result` lr 
    USING (anon_id, pat_enc_csn_id_coded)
    WHERE TIMESTAMP_DIFF(lr.order_time_jittered_utc, c.order_time_jittered_utc, Day) BETWEEN -30 AND 0
),
last4week_Quantiles as (
    SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    Period_Day,

    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(75)], 2) AS Q75_wbc,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(25)], 2) AS Q25_wbc,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(50)], 2) AS median_wbc,

    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(25)], 2) AS Q25_neutrophils,
    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(75)], 2) AS Q75_neutrophils,
    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(50)], 2) AS median_neutrophils,

    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(25)], 2) AS Q25_lymphocytes,
    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(75)], 2) AS Q75_lymphocytes,
    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(50)], 2) AS median_lymphocytes,

    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(25)], 2) AS Q25_hgb,
    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(75)], 2) AS Q75_hgb,
    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(50)], 2) AS median_hgb,

    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(25)], 2) AS Q25_plt,
    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(75)], 2) AS Q75_plt,
    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(50)], 2) AS median_plt,


    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(75)], 2) AS Q75_na,
    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(25)], 2) AS Q25_na,
    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(50)], 2) AS median_na,

    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(75)], 2) AS Q75_hco3,
    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(25)], 2) AS Q25_hco3,
    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(50)], 2) AS median_hco3,

    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(75)], 2) AS Q75_bun,
    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(25)], 2) AS Q25_bun,
    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(50)], 2) AS median_bun,

    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(75)], 2) AS Q75_cr,
    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(25)], 2) AS Q25_cr,
    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(50)], 2) AS median_cr,

    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(75)], 2) AS Q75_lactate,
    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(25)], 2) AS Q25_lactate,
    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(50)], 2) AS median_lactate,

    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(75)], 2) AS Q75_procalcitonin,
    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(25)], 2) AS Q25_procalcitonin,
    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(50)], 2) AS median_procalcitonin

    from last4weeklabs
    where wbc is not null
    or procalcitonin is not null 
    or lactate is not null 
    or cr is not null 
    or bun is not null 
    or hco3 is not null 
    or na is not null 
    or plt is not null 
    or hgb is not null 
    or lymphocytes is not null 
    or neutrophils is not null 
    group by anon_id,pat_enc_csn_id_coded,order_proc_id_coded,Period_Day

),
last4weekfirst_last as (
SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    Period_Day,
    Round(FIRST_VALUE(wbc) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY labtime
        ),2) AS first_wbc,
    Round(FIRST_VALUE(wbc) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY labtime
        ),2) AS last_wbc,
    
    
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_neutrophils,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_neutrophils,
   
    

    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_lymphocytes,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_lymphocytes,
    
    
    
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_hgb,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_hgb,
   
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_plt,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_plt,
   
    -- Na
    ROUND(FIRST_VALUE(na) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_na,
    ROUND(LAST_VALUE(na) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_na,
    

    ROUND(FIRST_VALUE(hco3) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_hco3,
    ROUND(LAST_VALUE(hco3) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_hco3,
    

    ROUND(FIRST_VALUE(bun) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_bun,
    ROUND(LAST_VALUE(bun) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_bun,
    

    ROUND(FIRST_VALUE(cr) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_cr,
    ROUND(LAST_VALUE(cr) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_cr,
    


    ROUND(FIRST_VALUE(lactate) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_lactate,
    ROUND(LAST_VALUE(lactate) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_lactate,
    

    ROUND(FIRST_VALUE(procalcitonin) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_procalcitonin,
    ROUND(LAST_VALUE(procalcitonin) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_procalcitonin,
    
FROM last4weeklabs
where wbc is not null
    or procalcitonin is not null 
    or lactate is not null 
    or cr is not null 
    or bun is not null 
    or hco3 is not null 
    or na is not null 
    or plt is not null 
    or hgb is not null 
    or lymphocytes is not null 
    or neutrophils is not null 
    ),
last4weekstats as (
select a.*,
b.first_procalcitonin,b.last_procalcitonin,
b.last_lactate,b.first_lactate,
b.last_cr,b.first_cr,b.last_bun,b.first_bun,b.last_hco3,b.first_hco3,b.last_na,b.first_na,b.last_plt,b.first_plt,
b.last_hgb,b.first_hgb,b.last_lymphocytes,b.first_lymphocytes,b.last_neutrophils,b.first_neutrophils,
b.last_wbc,b.first_wbc
from last4weekfirst_last b inner join 
last4week_Quantiles a using (anon_id,pat_enc_csn_id_coded,order_proc_id_coded,Period_Day)
),
-----------------------------------------------------------------------
last24weeklabs AS (
    SELECT 
        c.*,
        lr.order_time_jittered_utc as labtime,
        14 as Period_Day,
        CASE 
            WHEN (LOWER(lr.base_name) = 'wbc' AND LOWER(lr.reference_unit) IN ('thousand/ul','k/ul','10x3/ul','10*3/ul','x10e3/ul')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'wbc' AND lr.reference_unit = '/uL' THEN SAFE_CAST(lr.ord_value AS FLOAT64)/1000
        END AS wbc,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE '%neutrophils%' AND lr.reference_unit = '%' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS neutrophils,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE '%lymphocytes%' AND lr.reference_unit = '%' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS lymphocytes,
        -- CASE WHEN LOWER(lr.base_name) LIKE '%bands%' THEN SAFE_CAST(lr.ord_value AS FLOAT64) END AS bands,
        CASE 
            WHEN LOWER(lr.base_name) = 'hgb' AND lr.reference_unit = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'hgb' AND LOWER(lr.reference_unit) = 'g/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64) * 1000
        END AS hgb,
        CASE 
            WHEN LOWER(lr.base_name) = 'plt' AND LOWER(lr.reference_unit) IN ('x10e3/ul','10x3/ul','k/ul','10*3/ul','thousand/ul') THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'plt' AND LOWER(lr.reference_unit) = 'ul' THEN SAFE_CAST(lr.ord_value AS FLOAT64) / 1000
        END AS plt,
        CASE 
            WHEN LOWER(lr.base_name) = 'na' AND LOWER(lr.reference_unit) = 'mmol/l' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS na,
        CASE 
            WHEN (LOWER(lr.base_name) = 'hco3' AND LOWER(lr.reference_unit) like any ('meq/l','mmol/l')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN (LOWER(lr.base_name) = 'co2' AND LOWER(lr.reference_unit) like any ('meq/l','mmol/l')) THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS hco3,      
        CASE 
            WHEN LOWER(lr.base_name) = 'bun' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS bun,
        CASE 
            WHEN LOWER(lr.base_name) = 'cr' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS cr,
        -- CASE WHEN LOWER(lr.base_name) LIKE 'glucose' THEN SAFE_CAST(lr.ord_value AS FLOAT64) END AS glucose,
        CASE 
            WHEN LOWER(lr.base_name) = 'lac' AND LOWER(lr.reference_unit) IN ('mmol/l', 'mmole/l') THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS lactate,               
        CASE 
            WHEN LOWER(lr.base_name) = 'crp' AND LOWER(lr.reference_unit) = 'mg/dl' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
            WHEN LOWER(lr.base_name) = 'crp' AND LOWER(lr.reference_unit) = 'mg/l' THEN SAFE_CAST(lr.ord_value AS FLOAT64) / 10
        END AS crp,
        CASE 
            WHEN LOWER(lr.lab_name) LIKE 'procalcitonin' AND LOWER(lr.reference_unit) = 'ng/ml' THEN SAFE_CAST(lr.ord_value AS FLOAT64)
        END AS procalcitonin
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` c
    LEFT JOIN `som-nero-phi-jonc101.shc_core_2023.lab_result` lr 
    USING (anon_id, pat_enc_csn_id_coded)
    WHERE TIMESTAMP_DIFF(lr.order_time_jittered_utc, c.order_time_jittered_utc, Day) BETWEEN -180 AND 0
),
last24week_Quantiles as (
    SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    Period_Day,

    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(75)], 2) AS Q75_wbc,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(25)], 2) AS Q25_wbc,
    ROUND(APPROX_QUANTILES(wbc, 100)[OFFSET(50)], 2) AS median_wbc,

    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(25)], 2) AS Q25_neutrophils,
    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(75)], 2) AS Q75_neutrophils,
    ROUND(APPROX_QUANTILES(neutrophils, 100)[OFFSET(50)], 2) AS median_neutrophils,

    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(25)], 2) AS Q25_lymphocytes,
    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(75)], 2) AS Q75_lymphocytes,
    ROUND(APPROX_QUANTILES(lymphocytes, 100)[OFFSET(50)], 2) AS median_lymphocytes,

    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(25)], 2) AS Q25_hgb,
    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(75)], 2) AS Q75_hgb,
    ROUND(APPROX_QUANTILES(hgb, 100)[OFFSET(50)], 2) AS median_hgb,

    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(25)], 2) AS Q25_plt,
    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(75)], 2) AS Q75_plt,
    ROUND(APPROX_QUANTILES(plt, 100)[OFFSET(50)], 2) AS median_plt,


    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(75)], 2) AS Q75_na,
    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(25)], 2) AS Q25_na,
    ROUND(APPROX_QUANTILES(na, 100)[OFFSET(50)], 2) AS median_na,

    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(75)], 2) AS Q75_hco3,
    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(25)], 2) AS Q25_hco3,
    ROUND(APPROX_QUANTILES(hco3, 100)[OFFSET(50)], 2) AS median_hco3,

    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(75)], 2) AS Q75_bun,
    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(25)], 2) AS Q25_bun,
    ROUND(APPROX_QUANTILES(bun, 100)[OFFSET(50)], 2) AS median_bun,

    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(75)], 2) AS Q75_cr,
    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(25)], 2) AS Q25_cr,
    ROUND(APPROX_QUANTILES(cr, 100)[OFFSET(50)], 2) AS median_cr,

    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(75)], 2) AS Q75_lactate,
    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(25)], 2) AS Q25_lactate,
    ROUND(APPROX_QUANTILES(lactate, 100)[OFFSET(50)], 2) AS median_lactate,

    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(75)], 2) AS Q75_procalcitonin,
    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(25)], 2) AS Q25_procalcitonin,
    ROUND(APPROX_QUANTILES(procalcitonin, 100)[OFFSET(50)], 2) AS median_procalcitonin

    from last24weeklabs
    where wbc is not null
    or procalcitonin is not null 
    or lactate is not null 
    or cr is not null 
    or bun is not null 
    or hco3 is not null 
    or na is not null 
    or plt is not null 
    or hgb is not null 
    or lymphocytes is not null 
    or neutrophils is not null 
    group by anon_id,pat_enc_csn_id_coded,order_proc_id_coded,Period_Day

),
last24weekfirst_last as (
SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    order_proc_id_coded,
    Period_Day,
    Round(FIRST_VALUE(wbc) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY labtime
        ),2) AS first_wbc,
    Round(LAST_VALUE(wbc) OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded 
            ORDER BY labtime
        ),2) AS last_wbc,
    
    
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_neutrophils,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_neutrophils,
   
    

    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_lymphocytes,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_lymphocytes,
    
    
    
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_hgb,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_hgb,
   
    ROUND(FIRST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_plt,
    ROUND(LAST_VALUE(neutrophils) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_plt,
   
    -- Na
    ROUND(FIRST_VALUE(na) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_na,
    ROUND(LAST_VALUE(na) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_na,
    

    ROUND(FIRST_VALUE(hco3) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_hco3,
    ROUND(LAST_VALUE(hco3) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_hco3,
    

    ROUND(FIRST_VALUE(bun) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_bun,
    ROUND(LAST_VALUE(bun) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_bun,
    

    ROUND(FIRST_VALUE(cr) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_cr,
    ROUND(LAST_VALUE(cr) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_cr,
    


    ROUND(FIRST_VALUE(lactate) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_lactate,
    ROUND(LAST_VALUE(lactate) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_lactate,
    

    ROUND(FIRST_VALUE(procalcitonin) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime), 2) AS first_procalcitonin,
    ROUND(LAST_VALUE(procalcitonin) OVER (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY labtime ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING), 2) AS last_procalcitonin,
    
FROM last24weeklabs
where wbc is not null
    or procalcitonin is not null 
    or lactate is not null 
    or cr is not null 
    or bun is not null 
    or hco3 is not null 
    or na is not null 
    or plt is not null 
    or hgb is not null 
    or lymphocytes is not null 
    or neutrophils is not null 
    ),
last24weekstats as (
select a.*,
b.first_procalcitonin,b.last_procalcitonin,
b.last_lactate,b.first_lactate,
b.last_cr,b.first_cr,b.last_bun,b.first_bun,b.last_hco3,b.first_hco3,b.last_na,b.first_na,b.last_plt,b.first_plt,
b.last_hgb,b.first_hgb,b.last_lymphocytes,b.first_lymphocytes,b.last_neutrophils,b.first_neutrophils,
b.last_wbc,b.first_wbc
from last24weekfirst_last b inner join 
last24week_Quantiles a using (anon_id,pat_enc_csn_id_coded,order_proc_id_coded,Period_Day)
),
--------------------------------------------
all_labs as(
select * from last2weekstats
union all
select * from last4weekstats
union all
select * from last24weekstats
)
select distinct * from all_labs


