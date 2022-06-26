-- Insulin orders (excluding ISS) for patients during encounters on the BMT service 

SELECT jc_uid, pat_enc_csn_id_coded, order_time_jittered, medication_id,  med_description, med_route_c, med_route, freq_display_name, hv_discrete_dose, hv_dose_unit, pharm_class_name, thera_class_name FROM `starr_datalake2018.order_med`
	WHERE UPPER(med_description) LIKE '%INSULIN%'
	AND (ordering_mode_c) = 2
	AND pat_enc_csn_id_coded IN (SELECT (pat_enc_csn_id_coded) from starr_datalake2018.treatment_team AS TT  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%") )
	ORDER BY jc_uid, order_time_jittered asc 
