
SELECT med.jc_uid, med.pat_enc_csn_id_coded, med.order_med_id_coded, mar.taken_time_jittered, med.med_description, med_route_c, med_route, freq_display_name, mar_action, hv_discrete_dose, hv_dose_unit, pharm_class_name, thera_class_name 
  FROM starr_datalake2018.order_med AS med JOIN starr_datalake2018.mar as mar on med.order_med_id_coded = mar.order_med_id_coded
	WHERE  med.pat_enc_csn_id_coded IN (SELECT (pat_enc_csn_id_coded) from starr_datalake2018.treatment_team AS TT  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%") )
  AND (ordering_mode_c) = 2
  AND 
 (lower(med_description) like '%hydrocortisone%'  OR  lower(med_description) like '%prednisone%'  
   OR lower(med_description) like '%methylprednisolone%' OR  lower(med_description) like '%dexamethasone%')
	AND (upper(med_description) not like  '%CIPROFLOXACIN' AND upper(med_description) not like '%CHEMO%' AND upper(med_description) not like '%OPHT%' AND upper(med_description) not like '%TP%' AND upper(med_description) not like '%PR %' AND upper(med_description) not like '%IT%' AND upper(med_description) not like '%OTIC%' AND upper(med_description) not like '%PLACEBO%' AND upper(med_description) not like '%ONDANSETRON%')
  AND mar.mar_action = "Given"
  
  
  -- Pts on BMT service who were ordered for and given HC/methylpred/pred/dex oral/IV
