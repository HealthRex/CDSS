# mini study: 
# look at ordersets 

# create a cohort who recieved a very specific order set 

SELECT rit_uid, ss_sg_name, pat_enc_csn_id_coded, ss_section_name, protocol_name  	
FROM datalake_47618.med_orderset
WHERE ss_sg_name in ( 'IV Thrombolytic Therapy Stroke')

# 
