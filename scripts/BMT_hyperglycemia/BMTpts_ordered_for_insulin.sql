SELECT count(distinct(pat_enc_csn_id_coded)) FROM `starr_datalake2018.order_med` 
	WHERE UPPER(med_description) LIKE '%INSULIN%'
	AND (ordering_mode_c) = 2
	AND pat_enc_csn_id_coded IN (SELECT (pat_enc_csn_id_coded) from starr_datalake2018.treatment_team AS TT  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%") )

 OR pat_enc_csn_id_coded IN (SELECT (Os.pat_enc_csn_id_coded) from starr_datalake2018.med_orderset as OS JOIN starr_datalake2018.treatment_team  AS TT ON OS.rit_uid = TT.rit_uid 
	WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%")
	AND  UPPER(OS.ss_section_name) LIKE '%SCALE%'AND  UPPER(Os.ss_section_name) LIKE '%SCALE%') 
  
-- patient encounters on BMT w/ insulin orders (ISS or just insulin)
