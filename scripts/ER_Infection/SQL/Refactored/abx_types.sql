WITH er_admits AS (
SELECT anon_id, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time, max(effective_time_jittered_utc) as er_transfer_out_time
FROM `shc_core.adt`
WHERE pat_class_c = "112" AND pat_service = "Emergency"
GROUP BY anon_id, pat_enc_csn_id_coded),

antibiotics as (
SELECT COUNT (DISTINCT order_med_id_coded) cnt, REGEXP_EXTRACT(med_description, r'([^\s]+)') as simple_abx
FROM `shc_core.order_med` 
WHERE thera_class_name LIKE '%ANTIBIOTIC%'
GROUP BY simple_abx, med_description
ORDER BY simple_abx)

SELECT om.med_description, COUNT (DISTINCT om.order_med_id_coded) as num_times_ordered_4_hrs_into_ed,

CASE WHEN med_description LIKE "METHYLENE BLUE%" THEN 0 # gets picked up as abx - so this overrides it
WHEN med_description LIKE "PREDNISOLONE%" THEN 0 # gets picked up as abx - this overrides it
WHEN med_description LIKE "% IV%" THEN 1 #"IV"
WHEN med_description = "ZZZ IMS TEMPLATE" THEN 0
WHEN med_description LIKE "% IVPB %" THEN 1 #"IV"
WHEN med_description LIKE "%BAG%" THEN 1 #"IV"
WHEN med_description LIKE "% INJECTION%" THEN 1 #"IM"
WHEN med_description LIKE "% IM%" THEN 1 # "IM"
WHEN med_description LIKE "% INJ %" THEN 1 #"IM"
WHEN med_description LIKE "%VANCOMYCIN PER PHARMACY PROTOCOL%" OR med_description LIKE "%VANCOMYCIN ED ORDER%"  OR med_description LIKE "%VANCOMYCIN ORAL SOLUTION%" THEN 1 
ELSE 0 END is_include_abx,

CASE WHEN med_description LIKE "METHYLENE BLUE%" THEN 0 # gets picked up as abx - so this overrides it
WHEN med_description LIKE "PREDNISOLONE%" THEN 0 # gets picked up as abx - this overrides it
WHEN med_description LIKE "% IV%" THEN 1 #"IV"
WHEN med_description = "ZZZ IMS TEMPLATE" THEN 1
WHEN med_description LIKE "% IVPB %" THEN 1 #"IV"
WHEN med_description LIKE "%BAG%" THEN 1 #"IV"
WHEN med_description LIKE "% INJECTION%" THEN 1 #"IM"
WHEN med_description LIKE "% IM%" THEN 1 # "IM"
WHEN med_description LIKE "% INJ %" THEN 1 #"IM"
WHEN med_description LIKE "% PO%" THEN 1 # "Oral" 
WHEN med_description LIKE "%VANCOMYCIN PER PHARMACY PROTOCOL%" OR med_description LIKE "%VANCOMYCIN ED ORDER%"  OR med_description LIKE "%VANCOMYCIN ORAL SOLUTION%" THEN 1
ELSE 0 END affects_not_infected_label,

CASE WHEN med_description LIKE "METHYLENE BLUE%" THEN 0 # gets picked up as abx - so this overrides it
WHEN med_description LIKE "PREDNISOLONE%" THEN 0 # gets picked up as abx - this overrides it
WHEN med_description LIKE "% PO%" THEN 1 # "Oral" 
ELSE 0 END is_oral


FROM (
     -- Gets columns we need from order med and finds order time from 2018 extract when missing in 2020 extract 
     SELECT om.anon_id, om.med_description, om.order_med_id_coded,
     CASE WHEN om.order_inst_utc IS NULL THEN omm.order_time_jittered_utc ELSE om.order_inst_utc END order_time
     FROM `shc_core.order_med` om
     LEFT JOIN `starr_datalake2018.order_med` omm
     USING (order_med_id_coded)
) om
    
INNER JOIN er_admits
USING (anon_id)
INNER JOIN antibiotics
ON antibiotics.simple_abx =  REGEXP_EXTRACT(om.med_description, r'([^\s]+)')
WHERE TIMESTAMP_DIFF(om.order_time, er_admits.er_admit_time, HOUR) BETWEEN -24*14 AND 24*14 # two weeks before & two weeks after 
GROUP BY om.med_description
ORDER BY med_description desc
