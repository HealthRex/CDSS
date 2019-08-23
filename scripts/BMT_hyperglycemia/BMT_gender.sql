SELECT Demo.rit_uid, Demo.gender  FROM starr_datalake2018.demographic AS Demo

WHERE Demo.rit_uid IN (SELECT distinct (TT.rit_uid) FROM starr_datalake2018.treatment_team AS TT  WHERE (TT.name = "Primary Team" AND TT.prov_name LIKE "%BMT%"))

-- Gender of patients with primary team = BMT
