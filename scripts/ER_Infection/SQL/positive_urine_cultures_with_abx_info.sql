-- URINE CULTURE TABLE
WITH er_admits AS (
  SELECT 
    anon_id,
    pat_enc_csn_id_coded,
    min(effective_time_jittered_utc) as er_admit_time,
    max(effective_time_jittered_utc) as er_transfer_out_time
  FROM
    `shc_core.adt`
  WHERE
    pat_class_c = "112" AND pat_service = "Emergency"
  GROUP BY 
    anon_id, pat_enc_csn_id_coded
),

-- Filter er admits to adult patients
er_admits_adults AS (
    SELECT DISTINCT
        ea.* 
    FROM 
        er_admits ea
    INNER JOIN
        `shc_core.demographic` demo
    USING
        (anon_id)
    WHERE
        DATE_DIFF(CAST(ea.er_admit_time as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
),

-- Set of antibiotics that show up in order_med (may not be totally all encompassing) 
include_abx AS (
    SELECT
        med_description
    FROM
        `mining-clinical-decisions.abx.abx_types` 
    WHERE
        is_include_abx = 1 OR is_oral = 1
),

-- Antibiotic orders within 24 hours of er visit (IV/IM/Oral)
abx_orders_24_hours AS (
    SELECT 
        ea.anon_id,
        ea.pat_enc_csn_id_coded,
        om.order_med_id_coded,
        om.med_description,
        om.order_inst_utc
    FROM
        `mining-clinical-decisions.shc_core.order_med` om
    RIGHT JOIN -- preserve instances when no antibiotic are ordered
        er_admits_adults ea 
    USING
        (anon_id)
    INNER JOIN
        include_abx
    USING
        (med_description)
    WHERE 
        TIMESTAMP_DIFF(om.order_inst_utc, ea.er_admit_time, HOUR) BETWEEN 0 AND 24
),

-- Positive urine cultures ordered within 24 hours of ER visit
pos_urine_cultures_24_hours AS (
    SELECT
        cs.anon_id,
        op.pat_enc_csn_id_coded,
        er.er_admit_time,
        cs.description,
        cs.order_proc_id_coded,
        cs.organism,
    FROM
        `mining-clinical-decisions.shc_core.culture_sensitivity` cs
    INNER JOIN 
        -- Need csn from order_proc to join to er_admits
        (SELECT pat_enc_csn_id_coded, order_proc_id_coded
         FROM `mining-clinical-decisions.shc_core.order_proc`
         WHERE order_type LIKE "Microbiology%"
         AND description LIKE "%URINE%") op
    USING
        (order_proc_id_coded) 
    INNER JOIN
        er_admits_adults er
    USING
        (pat_enc_csn_id_coded)
    WHERE  
        TIMESTAMP_DIFF(cs.order_time_jittered_utc, er.er_admit_time, HOUR)
    BETWEEN
        0 AND 24
),

--Other postive culture types ordered within 24 hours of er visit
pos_other_cultures_24_hours AS (
    SELECT
        er.pat_enc_csn_id_coded,
        description,
        organism,
    FROM
        `mining-clinical-decisions.shc_core.culture_sensitivity` cs
    INNER JOIN 
        -- Need csn from order_proc to join to er_admits
        (SELECT pat_enc_csn_id_coded, order_proc_id_coded
         FROM `mining-clinical-decisions.shc_core.order_proc`
         WHERE order_type LIKE "Microbiology%"
         AND description NOT LIKE "%URINE%") op
    USING
        (order_proc_id_coded) 
    INNER JOIN
        er_admits_adults er
    USING
        (pat_enc_csn_id_coded)
    WHERE  
        TIMESTAMP_DIFF(cs.order_time_jittered_utc, er.er_admit_time, HOUR)
    BETWEEN
        0 AND 24
)

SELECT DISTINCT
    uc.*,
    ab.med_description,
    STRING_AGG(DISTINCT mar.mar_action) mar_actions,
    STRING_AGG(DISTINCT other.description) other_positive_cultures,
    STRING_AGG(DISTINCT other.organism) bugs_from_other_cultures
FROM
    pos_urine_cultures_24_hours uc
LEFT JOIN
    abx_orders_24_hours ab 
USING
    (pat_enc_csn_id_coded)
LEFT JOIN
    `mining-clinical-decisions.shc_core.mar` mar
USING
    (order_med_id_coded)
LEFT JOIN
    pos_other_cultures_24_hours other
USING 
    (pat_enc_csn_id_coded)
GROUP BY 
    anon_id, pat_enc_csn_id_coded,
    er_admit_time, description,
    order_proc_id_coded, organism,
    med_description
ORDER BY 
    anon_id, er_admit_time
