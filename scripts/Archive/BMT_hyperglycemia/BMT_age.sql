SELECT Demo.rit_uid, pat_enc_csn_id_coded, gender, birth_date_jittered, trtmnt_tm_begin_dt_jittered, trtmnt_tm_end_dt_jittered, DATE_DIFF(DATE(trtmnt_tm_begin_dt_jittered), DATE(Demo.birth_date_jittered), YEAR) as ageYears,  prov_name FROM starr_datalake2018.demographic AS Demo JOIN starr_datalake2018.treatment_team AS TT ON Demo.rit_uid = TT.rit_uid 
WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%")



Order by rit_uid, ageYears, pat_enc_csn_id_coded asc

--Age at time of treamtent team assignment for pts on BMT (with duplicates)
