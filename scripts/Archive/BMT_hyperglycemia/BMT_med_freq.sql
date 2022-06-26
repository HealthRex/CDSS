
-- Most freqeuently given meds to patient encounters on BMT service 

SELECT  med.med_description, count(med.med_description) 
  FROM starr_datalake2018.order_med AS med JOIN starr_datalake2018.mar as mar on med.order_med_id_coded = mar.order_med_id_coded
	WHERE  med.pat_enc_csn_id_coded IN (SELECT (pat_enc_csn_id_coded) from starr_datalake2018.treatment_team AS TT  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%") )
  AND (ordering_mode_c) = 2
  AND mar.mar_action = "Given"
  
 Group by med.med_description
 Order by count(med.med_description) desc
 
