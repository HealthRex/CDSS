SELECT count(pat_enc_csn_id_coded) FROM `mining-clinical-decisions.starr_datalake2018.treatment_team` 

WHERE name = "Primary Team" AND prov_name LIKE "%BMT%"

-- Count = 7786 patient encounters with BMT as a primary team