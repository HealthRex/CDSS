	SELECT  rit_uid, ss_section_name  FROM `mining-clinical-decisions.starr_datalake2018.med_orderset` 
	WHERE UPPER(ss_section_name) LIKE '%SCALE%'
	ORDER BY ss_section_name ASC

	-- Patients on ISS (distinct pts = 50924; distinct pt encounters = 84859)