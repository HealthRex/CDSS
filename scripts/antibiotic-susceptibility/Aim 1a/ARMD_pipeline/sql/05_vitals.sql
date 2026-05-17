-- microbiology_Vitals: vital sign quantiles + first/last per culture, over the
-- 48 hours preceding the culture order.
--
-- Bug fixes vs. original Vitals.sql:
--   * Q25_diasbp was computed from APPROX_QUANTILES(sysbp, ...). Fixed.
--   * median_sysbp was missing entirely. Added.
--   * Q75/median_diasbp were missing the ROUND(..., 2) precision argument.
--     Added for consistency.
--   * LAST_VALUE(...) calls were missing the
--     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING frame, so each
--     last_* column returned the current row's value instead of the partition
--     last. Fixed with a named WINDOW clause.
--
-- Schema adaptation for shc_core_2024+ flowsheet:
--   The old `numerical_val_1` / `numerical_val_2` numeric columns no longer
--   exist. All measurements are stored as a STRING in `meas_value`. For
--   blood pressure, systolic and diastolic are combined as "SYS/DIA"
--   (e.g. "120/80"), so we parse them with SPLIT(meas_value, '/').

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_Vitals` AS

WITH vitals AS (
    SELECT
        c.*,
        v.recorded_time_jittered_utc AS vitaltime,
        CASE
            WHEN UPPER(v.row_disp_name) IN ('PULSE', 'HEART RATE')
            THEN ROUND(SAFE_CAST(v.meas_value AS FLOAT64), 2)
        END AS heartrate,
        CASE
            WHEN UPPER(v.row_disp_name) IN ('RESP', 'RESP RATE')
            THEN ROUND(SAFE_CAST(v.meas_value AS FLOAT64), 2)
        END AS resprate,
        CASE
            WHEN UPPER(v.row_disp_name) IN ('TEMP')
            THEN ROUND(SAFE_CAST(v.meas_value AS FLOAT64), 2)
        END AS tempt,
        -- BP is stored as "systolic/diastolic" in meas_value
        CASE
            WHEN UPPER(TRIM(v.row_disp_name)) IN ('BP', 'NIBP')
                 AND SAFE_CAST(TRIM(SPLIT(v.meas_value, '/')[SAFE_OFFSET(0)]) AS NUMERIC) >= 40
            THEN ROUND(SAFE_CAST(TRIM(SPLIT(v.meas_value, '/')[SAFE_OFFSET(0)]) AS FLOAT64), 2)
        END AS sysbp,
        CASE
            WHEN UPPER(TRIM(v.row_disp_name)) IN ('BP', 'NIBP')
                 AND SAFE_CAST(TRIM(SPLIT(v.meas_value, '/')[SAFE_OFFSET(1)]) AS NUMERIC) >= 30
            THEN ROUND(SAFE_CAST(TRIM(SPLIT(v.meas_value, '/')[SAFE_OFFSET(1)]) AS FLOAT64), 2)
        END AS diasbp
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` c
    LEFT JOIN `som-nero-phi-jonc101.shc_core_2023.flowsheet` v
        ON v.anon_id = c.anon_id
    WHERE
        (
            (UPPER(TRIM(v.row_disp_name)) IN ('PULSE', 'HEART RATE')
                AND SAFE_CAST(v.meas_value AS NUMERIC) >= 30)
         OR (UPPER(TRIM(v.row_disp_name)) IN ('RESP', 'RESP RATE')
                AND SAFE_CAST(v.meas_value AS NUMERIC) BETWEEN 4 AND 60)
         OR (UPPER(TRIM(v.row_disp_name)) IN ('TEMP')
                AND SAFE_CAST(v.meas_value AS NUMERIC) >= 90)
         OR (UPPER(TRIM(v.row_disp_name)) IN ('WEIGHT')
                AND SAFE_CAST(v.meas_value AS NUMERIC) BETWEEN 480 AND 8000)
         OR (UPPER(TRIM(v.row_disp_name)) IN ('BP', 'NIBP')
                AND SAFE_CAST(TRIM(SPLIT(v.meas_value, '/')[SAFE_OFFSET(0)]) AS NUMERIC) >= 40)
         OR (UPPER(TRIM(v.row_disp_name)) IN ('BP', 'NIBP')
                AND SAFE_CAST(TRIM(SPLIT(v.meas_value, '/')[SAFE_OFFSET(1)]) AS NUMERIC) >= 30)
        )
        AND TIMESTAMP_DIFF(v.recorded_time_jittered_utc, c.order_time_jittered_utc, HOUR) BETWEEN -48 AND 0
),
vitalsQ AS (
    SELECT
        anon_id, pat_enc_csn_id_coded, order_proc_id_coded,
        ROUND(APPROX_QUANTILES(heartrate, 100)[OFFSET(25)], 2) AS Q25_heartrate,
        ROUND(APPROX_QUANTILES(heartrate, 100)[OFFSET(75)], 2) AS Q75_heartrate,
        ROUND(APPROX_QUANTILES(heartrate, 100)[OFFSET(50)], 2) AS median_heartrate,
        ROUND(APPROX_QUANTILES(resprate,  100)[OFFSET(25)], 2) AS Q25_resprate,
        ROUND(APPROX_QUANTILES(resprate,  100)[OFFSET(75)], 2) AS Q75_resprate,
        ROUND(APPROX_QUANTILES(resprate,  100)[OFFSET(50)], 2) AS median_resprate,
        ROUND(APPROX_QUANTILES(tempt,     100)[OFFSET(25)], 2) AS Q25_temp,
        ROUND(APPROX_QUANTILES(tempt,     100)[OFFSET(75)], 2) AS Q75_temp,
        ROUND(APPROX_QUANTILES(tempt,     100)[OFFSET(50)], 2) AS median_temp,
        ROUND(APPROX_QUANTILES(sysbp,     100)[OFFSET(25)], 2) AS Q25_sysbp,
        ROUND(APPROX_QUANTILES(sysbp,     100)[OFFSET(75)], 2) AS Q75_sysbp,
        ROUND(APPROX_QUANTILES(sysbp,     100)[OFFSET(50)], 2) AS median_sysbp,
        ROUND(APPROX_QUANTILES(diasbp,    100)[OFFSET(25)], 2) AS Q25_diasbp,
        ROUND(APPROX_QUANTILES(diasbp,    100)[OFFSET(75)], 2) AS Q75_diasbp,
        ROUND(APPROX_QUANTILES(diasbp,    100)[OFFSET(50)], 2) AS median_diasbp
    FROM vitals
    GROUP BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded
),
Vitalsfirstlast AS (
    SELECT DISTINCT
        anon_id, pat_enc_csn_id_coded, order_proc_id_coded,
        ROUND(FIRST_VALUE(heartrate) OVER w, 2)      AS first_heartrate,
        ROUND(LAST_VALUE(heartrate)  OVER w_full, 2) AS last_heartrate,
        ROUND(FIRST_VALUE(resprate)  OVER w, 2)      AS first_resprate,
        ROUND(LAST_VALUE(resprate)   OVER w_full, 2) AS last_resprate,
        ROUND(FIRST_VALUE(tempt)     OVER w, 2)      AS first_temp,
        ROUND(LAST_VALUE(tempt)      OVER w_full, 2) AS last_temp,
        ROUND(FIRST_VALUE(sysbp)     OVER w, 2)      AS first_sysbp,
        ROUND(LAST_VALUE(sysbp)      OVER w_full, 2) AS last_sysbp,
        ROUND(FIRST_VALUE(diasbp)    OVER w, 2)      AS first_diasbp,
        ROUND(LAST_VALUE(diasbp)     OVER w_full, 2) AS last_diasbp
    FROM vitals
    WINDOW
        w      AS (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY vitaltime),
        w_full AS (PARTITION BY anon_id, pat_enc_csn_id_coded, order_proc_id_coded ORDER BY vitaltime
                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)
SELECT a.*,
       b.first_heartrate, b.last_heartrate,
       b.first_resprate,  b.last_resprate,
       b.first_temp,      b.last_temp,
       b.first_sysbp,     b.last_sysbp,
       b.first_diasbp,    b.last_diasbp
FROM vitalsQ a
INNER JOIN Vitalsfirstlast b USING (anon_id, pat_enc_csn_id_coded, order_proc_id_coded);
