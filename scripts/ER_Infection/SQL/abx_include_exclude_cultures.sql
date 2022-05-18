DECLARE culture_names ARRAY<STRING>;

SET culture_names = ["URINE CULTURE", "BLOOD CULTURE (2 AEROBIC BOTTLES)", "BLOOD CULTURE (AEROBIC & ANAEROBIC BOTTLES)", "BLOOD CULTURE (AEROBIC & ANAEROBIC BOTTLE)", "ANAEROBIC CULTURE", "RESPIRATORY CULTURE AND GRAM STAIN", "RESPIRATORY CULTURE", "FLUID CULTURE AND GRAM STAIN", "WOUND CULTURE", "STOOL CULTURE", "CSF CULTURE AND GRAM STAIN", "BLOOD CULT - FIRST SET, VIA PHLEBOTOMY", "BLOOD CULT CENTRAL LINE CATHETER BY NURSE", "WOUND CULTURE AND GRAM STAIN", "WOUND CULTURE AND GRAM STAIN, DEEP / SURGICAL / ASP", "FLUID CULTURE / BB GRAM STAIN", "CYSTIC FIBROSIS RESPIRATORY CULTURE"];

WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

in_micro AS (
SELECT DISTINCT op.description 
FROM `shc_core.order_proc` op
WHERE op.order_type = "Microbiology"
),

in_micro_cult AS (
SELECT DISTINCT op.description 
FROM `shc_core.order_proc` op
WHERE op.order_type = "Microbiology Culture"
),

in_micro_not_micro_cult AS (
SELECT DISTINCT op.description, op.order_proc_id_coded, CASE WHEN op.order_type = "Microbiology" THEN 1 ELSE 0 END in_micro,
CASE WHEN op.order_type = "Microbiology Culture" THEN 1 ELSE 0 END in_micro_culture
FROM `shc_core.order_proc` op
INNER JOIN er_admits ea
USING (anon_id)
WHERE TIMESTAMP_DIFF(op.order_time_jittered_utc, ea.er_admit_time, HOUR) BETWEEN 0 AND 4
AND (op.description IN UNNEST(culture_names) OR op.order_type LIKE "Microbiology%")
)


SELECT description, COUNT (DISTINCT order_proc_id_coded) num_orders_4_hrs_into_stay,
-- Include cultures from array defined above
CASE WHEN description IN UNNEST(culture_names) THEN 1 ELSE 0 END included,
-- Exclude cultures not in array defined above except for descriptions that appear in order_type microbiology but not order_type microbiology_culture - ex: gram stain shouldn't be excluded
CASE WHEN description NOT IN UNNEST(culture_names) AND NOT (MAX(in_micro) = 1 AND MAX(in_micro_culture) = 0) THEN 1 ELSE 0 END excluded 
FROM in_micro_not_micro_cult
GROUP BY description
ORDER BY description