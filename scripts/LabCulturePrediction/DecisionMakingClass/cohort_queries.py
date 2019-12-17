from google.cloud import bigquery


def test():
	query = """select distinct er_admits.*, labs.order_id_coded, labs.proc_code,
	           labs.group_lab_name, labs.result_flag, labs.order_time_jittered_utc,
	           labs.result_time_jittered_utc
			from
			    starr_datalake2018.lab_result as labs,
			    (select jc_uid, pat_enc_csn_id_coded, min(effective_time_jittered_utc) as er_admit_time,
			     		max(effective_time_jittered_utc) as er_transfer_out_time 
			     from starr_datalake2018.adt
			     where pat_class_c = "112"
			     and pat_service = "Emergency"
			     group by jc_uid, pat_enc_csn_id_coded
			     order by pat_enc_csn_id_coded) er_admits
			    
			where er_admits.pat_enc_csn_id_coded = labs.pat_enc_csn_id_coded
			and labs.order_type = "Microbiology Culture"
			and labs.order_time_jittered_utc <= er_admits.er_transfer_out_time
			and labs.order_time_jittered_utc >= er_admits.er_admit_time
			order by pat_enc_csn_id_coded, labs.order_time_jittered_utc"""
	query_job = client.query(query)
	return query_job.result().to_dataframe()