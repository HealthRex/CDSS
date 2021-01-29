SELECT distinct anon_id, pat_enc_csn_id_coded 

FROM `som-nero-phi-jonc101.shc_core.treatment_team`

WHERE prov_map_id IN ( -- Removed NSurg, ICU, CCU, removed anything with <100 patients 
'S176', 
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
'S19626') 

AND name = 'Primary Team'

EXCEPT DISTINCT SELECT anon_id, pat_enc_csn_id_coded  FROM `som-nero-phi-jonc101.shc_core.adt`


WHERE pat_service IN ('Neurocritical Care', 'ICU Trauma/GenSurg', 'Cardiovascular ICU', 'Critical Care', 'Emergency Critical Care')



LIMIT 1000