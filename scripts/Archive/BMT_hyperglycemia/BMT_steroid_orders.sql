SELECT  med_description  FROM `starr_datalake2018.order_med` 
	WHERE  pat_enc_csn_id_coded IN (SELECT (pat_enc_csn_id_coded) from starr_datalake2018.treatment_team AS TT  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%") )
  AND (ordering_mode_c) = 2
  AND 
 (lower(med_description) like '%hydrocortisone%'  OR  lower(med_description) like '%prednisone%'  
   OR lower(med_description) like '%methylprednisolone%' OR  lower(med_description) like '%dexamethasone%')
	AND (upper(med_description) not like  '%CIPROFLOXACIN' AND upper(med_description) not like '%CHEMO%' AND upper(med_description) not like '%OPHT%' AND upper(med_description) not like '%TP%' AND upper(med_description) not like '%PR %' AND upper(med_description) not like '%IT%' AND upper(med_description) not like '%OTIC%' AND upper(med_description) not like '%PLACEBO%' AND upper(med_description) not like '%ONDANSETRON%')


-- Pts on bmt getting steroids
