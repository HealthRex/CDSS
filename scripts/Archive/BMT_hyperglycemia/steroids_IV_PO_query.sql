WHERE (ordering_mode_c) = 2
  AND 
 (lower(med_description) like '%hydrocortisone%'  OR  lower(med_description) like '%prednisone%'  
   OR lower(med_description) like '%methylprednisolone%' OR  lower(med_description) like '%dexamethasone%')
	AND (upper(med_description) not like  '%CIPROFLOXACIN' AND upper(med_description) not like '%CHEMO%' AND upper(med_description) not like '%OPHT%' AND upper(med_description) not like '%TP%' AND upper(med_description) not like '%PR %' AND upper(med_description) not like '%IT%' AND upper(med_description) not like '%OTIC%' AND upper(med_description) not like '%PLACEBO%' AND upper(med_description) not like '%ONDANSETRON%')
  AND mar.mar_action = "Given"
  
  
  -- partial query of pts receiving HC/dex/pred/solumedrol inpatient
