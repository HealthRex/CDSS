-- Pt encounters with BMT as primary treatment team &  A1c > 6.5% —> 281
 	
SELECT count(distinct(Lab.pat_enc_csn_id_coded))  FROM starr_datalake2018.lab_result AS Lab
	  WHERE  Lab.pat_enc_csn_id_coded IN (SELECT DISTINCT(TT.pat_enc_csn_id_coded) FROM starr_datalake2018.treatment_team AS TT 
      WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%"))
  AND UPPER(Lab.lab_name) LIKE '%A1C%' AND ord_num_value >= 6.5 AND ord_num_value != 9999999
  
