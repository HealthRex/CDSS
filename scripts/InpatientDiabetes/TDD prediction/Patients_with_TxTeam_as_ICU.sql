SELECT extract(year from trtmnt_tm_begin_dt_jittered) as asgnment_yr, count(distinct anon_id) as num_pt, count(anon_id) as tot_assignments_icu, count(distinct pat_enc_csn_id_coded) as num_enc 

FROM `som-nero-phi-jonc101.shc_core.treatment_team`

WHERE prov_map_id IN ('S176',
'S358',
'SUNK00008',
'S400',
'SG1000003',
'SG1000007',
'SG1000005',
'SG1000009',
'S1398',
'S3395',
'S3399',
'S3396',
'SG1000041',
'SG1000044',
'S224',
'SG1000046',
'SG1000031',
'SG1000027',
'S19626') -- Removed NSurg, ICU, CCU, removed anything with <100  

AND name = 'Primary Team'

GROUP BY asgnment_yr
ORDER BY asgnment_yr

LIMIT 1000