CREATE OR REPLACE TABLE `mining-clinical-decisions.abx.feature_counts_long` AS (

SELECT anon_id, pat_enc_csn_id_coded, index_time, feature_type, features, COUNT(*) value 
FROM `mining-clinical-decisions.abx.feature_timeline_long` 
WHERE feature_type NOT IN ("Demographics", "Lab Results", "Flowsheet")
AND feature_type IS NOT NULL
AND features IS NOT NULL
GROUP BY anon_id, pat_enc_csn_id_coded, index_time, order_id, feature_type, features

UNION DISTINCT

SELECT anon_id, pat_enc_csn_id_coded, index_time, feature_type, features, 
CASE WHEN value IS NOT NULL THEN value
ELSE 1 END value
FROM `mining-clinical-decisions.abx.feature_timeline_long` 
WHERE feature_type = "Demographics"
AND feature_type IS NOT NULL
AND features IS NOT NULL

)

