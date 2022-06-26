	SELECT  count(distinct(TT.pat_enc_csn_id_coded)) FROM starr_datalake2018.med_orderset as OS JOIN starr_datalake2018.treatment_team AS TT ON OS.rit_uid = TT.rit_uid 

	WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%")
	AND  UPPER(ss_section_name) LIKE '%SCALE%'

	-- Patient encounters with BMT pirmary and ISS (3571)
