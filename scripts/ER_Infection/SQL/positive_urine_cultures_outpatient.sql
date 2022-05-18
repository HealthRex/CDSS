-- URINE CULTURE TABLE
WITH pos_outpatient_urine_cultures AS (
    SELECT
        cs.anon_id,
        op.pat_enc_csn_id_coded,
        cs.description,
        cs.order_proc_id_coded,
        cs.organism,
        cs.order_time_jittered_utc
    FROM
        `mining-clinical-decisions.shc_core.culture_sensitivity` cs
    INNER JOIN 
        -- Need csn from order_proc to join to er_admits
        (SELECT pat_enc_csn_id_coded, order_proc_id_coded
         FROM `mining-clinical-decisions.shc_core.order_proc`
         WHERE order_type LIKE "Microbiology%"
         AND description LIKE "%URINE%"
         AND ordering_mode = 'Outpatient') op
    USING
        (order_proc_id_coded) 
),
-- Filter er admits to adult patients
adult_puc AS (
    SELECT DISTINCT
        puc.* 
    FROM 
        pos_outpatient_urine_cultures puc
    INNER JOIN
        `shc_core.demographic` demo
    USING
        (anon_id)
    WHERE
        DATE_DIFF(CAST(puc.order_time_jittered_utc as DATE), demo.BIRTH_DATE_JITTERED, YEAR) >= 18
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

-- Antibiotic orders within window of culture order time. window = -4 to 24 hours. 
abx_orders AS (
    SELECT 
        puc.anon_id,
        puc.pat_enc_csn_id_coded,
        om.order_med_id_coded,
        om.med_description,
        om.order_inst_utc
    FROM
        `mining-clinical-decisions.shc_core.order_med` om
    RIGHT JOIN -- preserve instances when no antibiotic are ordered
        adult_puc puc 
    USING
        (anon_id)
    INNER JOIN
        include_abx
    USING
        (med_description)
    WHERE 
        TIMESTAMP_DIFF(om.order_inst_utc, puc.order_time_jittered_utc, HOUR) BETWEEN -4 AND 24
),

--Other postive culture types ordered within window of urine culture. window = -4 ot 24 hours
pos_other_cultures_24_hours AS (
    SELECT
        puc.anon_id,
        puc.pat_enc_csn_id_coded,
        cs.description,
        cs.organism,
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
        adult_puc puc
    USING
        (anon_id)
    WHERE  
        TIMESTAMP_DIFF(cs.order_time_jittered_utc, puc.order_time_jittered_utc, HOUR)
    BETWEEN
        -4 AND 24
)

SELECT DISTINCT
    puc.*,
    ab.med_description,
    STRING_AGG(DISTINCT mar.mar_action) mar_actions,
    STRING_AGG(DISTINCT other.description) other_positive_cultures,
    STRING_AGG(DISTINCT other.organism) bugs_from_other_cultures
FROM
    adult_puc puc
LEFT JOIN
    abx_orders ab 
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
    order_time_jittered_utc, description,
    order_proc_id_coded, organism,
    med_description
ORDER BY 
    anon_id, order_time_jittered_utc
