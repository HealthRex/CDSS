-- Patients who have ever been on the BMT service who were ordered for and received insulin 
	
  
 SELECT jc_uid, pat_enc_csn_id_coded, order_time_jittered, medication_id,  med_description, med_route_c, med_route, freq_display_name, hv_discrete_dose, hv_dose_unit, pharm_class_name, thera_class_name FROM `starr_datalake2018.order_med`
	WHERE UPPER(med_description) LIKE '%INSULIN%'
	AND (ordering_mode_c) = 2
	AND jc_uid IN (SELECT DISTINCT(jc_uid) FROM starr_datalake2018.adt WHERE pat_service LIKE 'Bone%') -- patients with "patient service" = Bone Marrow Transplant
	ORDER BY jc_uid, order_time_jittered asc 
	Patients who have ever been on the BMT service who were ordered for and received insulin
	SELECT jc_uid, pat_enc_csn_id_coded, order_med_id_coded, medication_id, med_description, ordering_mode, med_route from starr_datalake2018.order_med
	WHERE order_med_id_coded in 
	(SELECT order_med_id_coded FROM starr_datalake2018.mar 
	WHERE order_med_id_coded IN (SELECT order_med_id_coded FROM `starr_datalake2018.order_med`
	WHERE UPPER(med_description) LIKE '%INSULIN%'
	AND (ordering_mode_c) = 2
	AND jc_uid IN (SELECT DISTINCT(jc_uid) FROM starr_datalake2018.adt WHERE pat_service LIKE 'Bone%')) -- patients with "patient service" = Bone Marrow Transplant
	)
	ORDER BY jc_uid, med_description  asc 
