 SELECT 
          ADT.pat_enc_csn_id_coded, TT.prov_name, TT.name, ADT.pat_service
        FROM
          starr_datalake2018.adt AS ADT JOIN  -- Create a shorthand table alias for convenience when referencing
          starr_datalake2018.treatment_team AS TT ON ADT.pat_enc_csn_id_coded = TT.pat_enc_csn_id_coded
        WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%")
        AND ADT.pat_service LIKE 'Bone%'
        
        ORDER BY ADT.pat_service DESC
        
 -- Inner joins the ADT and treatment team tables on patient encounters where both service is BMT and primary team is BMT
 -- 6637 unique encounters
