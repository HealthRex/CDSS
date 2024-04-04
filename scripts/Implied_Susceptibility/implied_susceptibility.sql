
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept` (
  anon_id STRING,
  order_proc_id_coded INT64,
  organism STRING,
  antibiotic STRING,
  susceptibility STRING,
  implied_susceptibility STRING
);


--add culture sensitvity to implied table

INSERT INTO `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  (anon_id, order_proc_id_coded, organism, antibiotic, susceptibility)
WITH More_Frequent_ABX AS (
  SELECT DISTINCT(antibiotic)
  FROM `som-nero-phi-jonc101.fateme_db.antibiotic_list_aim1a`
  WHERE total_tests >= 10
),
Base_cohort AS (
  SELECT
    anon_id,
    order_proc_id_coded,
    organism,
    antibiotic,
    suscept AS susceptibility
  FROM `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity`
  WHERE antibiotic IN (SELECT antibiotic FROM More_Frequent_ABX)
)
SELECT * FROM Base_cohort;



---------------------------------
--ACINETOBACTER
-------------------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
AND  
lower(antibiotic) like  any ('%amoxicillin%clavulanic%','ampicillin','%ampicillin%sulbactam%',
'aztreonam','cefazolin','cefotetan','cefoxitin','cefuroxime','%cephalexin%','clarithromycin','clindamycin',
'daptomycin','doxycycline','linezolid','metronidazole','minocycline','moxifloxacin','oxacillin','penicillin',
'%quinupristin%dalfopristin%','tetracycline','vancomycin')
AND
(susceptibility IS NULL OR susceptibility = '');
---------------------------
--* Cefepime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

---------------------------
--* Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

------------------
--*Cefotaxime if missing then E ceftriaxone; if missing then R
-------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
);


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility is NULL ;

-------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then R
------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility is NULL ;

----------------------------
-- *Doripenem E meropenem
-----------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
);
----------------------
--*Meropenem if missing then S if imipenem-S; if missing then .
-------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('imipenem')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------------
--*Piperacillin-Tazobactam if missing then S if piperacillin-S; if missing then .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ACINETOBACTER%' 
AND lower(antibiotic) IN ('piperacillin/tazobactam')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%ACINETOBACTER%'
  AND lower(antibiotic) like any ('piperacillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------STENOTROPHOMONAS--------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%STENOTROPHOMONAS%'
AND lower(antibiotic) like any ('oxacillin', '%ampicillin%sulbactam%', '%piperacillin%tazobactam%', 'cefazolin', 'ceftriaxone', 'ertapenem', 'meropenem', 'vancomycin')
AND (susceptibility IS NULL OR susceptibility = ''); -- This line is added to update only missing or non-reported susceptibilities





----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------Citrobacter-------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%'
AND
LOWER(antibiotic) like any ('ampicillin', 'cefazolin', 'cefotetan', 'cefoxitin', 'cefuroxime', 'clarithromycin', 'clindamycin', 'daptomycin', 'linezolid', 'metronidazole', 'oxacillin', 'penicillin', 'vancomycin','colistin','tetracycline')
AND susceptibility IS NULL;

------------------------------
--* Cefepime if missing then S if ceftriaxone-S or cefotaxime-S; else .
------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );


----------------
--* Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );

------------------------
--*Ceftriaxone if missing then E cefotaxime; if missing then .
-------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ceftriaxone')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );
  
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ceftriaxone')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
  );

------------------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then R
-------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
  );

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('cefotaxime')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
  );

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;



-----------------------
--*Cefotaxime if missing then E ceftriaxone; if missing then .
-------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('cefotaxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
  );
-------------
--*Doxycycline if missing then S if tetracycline-S; else R
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('doxycycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------------
--*Doripenem E meropenem
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );
  UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('doripenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('meropenem')
  AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
  );

-----
--* Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );

--------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );
-----
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S; or cefotaxime-S else .
-----
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );

-----------
--*Minocycline if missing then S if tetracycline-S; else R
---------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%CITROBACTER%' 
AND lower(antibiotic) IN ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
  SELECT order_proc_id_coded 
  FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
  WHERE UPPER(organism) LIKE '%CITROBACTER%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
  );

  UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%CITROBACTER%'
AND
LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL 
AND implied_susceptibility IS NULL ;
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------Enterobacter----------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('ampicillin', 'cefazolin', 'cefotetan', 'cefoxitin', 'clarithromycin', 'clindamycin', 'daptomycin', 'linezolid', 'metronidazole', 'oxacillin', 'penicillin','tetracycline')
AND susceptibility IS NULL;

----------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S; else .
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------
--*Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------
--*Ceftriaxone if missing then E cefotaxime; if missing then .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL;

------------------
--*Cefotaxime if missing then E ceftriaxone; if missing then .
------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;
----
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then .
-----
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;

----
--*Doxycycline if missing then S if tetracycline-S; else R
----
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------------
--*Doripenem E meropenem
-----------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL;

-------------
--*Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-------------
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S or cefotaxime-S; else .
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----------------
--*Minocycline if missing then S if tetracycline-S; else R
-----------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ENTEROBACTER%'
AND
LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------ESCHERICHIA COLI-------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('clindamycin', 'daptomycin', 'linezolid', 'metronidazole', 'oxacillin', 'penicillin', 'vancomycin','clarithromycin','tetracycline')
AND susceptibility IS NULL;

-------------------
--*Aztreonam if missing then E ceftriaxone; if missing then E cefotaxime; if missing then .
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'aztreonam'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'aztreonam'
AND susceptibility IS NULL;

-----------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

--------------------
--* Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

------------
--*Ceftriaxone if missing then E cefotaxime; if missing then S if cefazolin-S; else .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('Ceftriaxone')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------------
--*Cefotaxime if missing then E ceftriaxone; if missing then S if cefazolin-S; else .
------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND
LOWER(antibiotic) like any ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------------
--*Cefotetan if missing then S if cefazolin-S; else .
----------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefotetan')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

---------------------
--*Cefoxitin if missing then S if cefazolin-S; else .
----------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefoxitin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
---------------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then S if cefazolin-S; if missing then .
----------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

---------------
--*Cefuroxime if missing then S if cefazolin-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('cefuroxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-----------------
--*Doxycycline if missing then S if tetracycline-S; else R
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

-----------------
--*Doripenem E meropenem
------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL;
-------------------
--*Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-------------------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------------
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-------------------
--*Minocycline if missing then S if tetracycline-S; else R
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ESCHERICHIA%COLI%'
AND LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------KLEBSIELLA----------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND
LOWER(antibiotic) like any ('ampicillin', 'clindamycin', 'daptomycin', 'linezolid', 'metronidazole', 'oxacillin', 'penicillin', 'vancomycin','tetracycline')
AND susceptibility IS NULL;

------
--*Aztreonam if missing then E ceftriaxone; if missing then E cefotaxime; if missing then .
------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'aztreonam'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'aztreonam'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

------------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------
--*Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------
--*Ceftriaxone if missing then E cefotaxime; if missing then S if cefazolin-S; else .
----------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('ceftriaxone')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

------------
--*Cefotaxime if missing then E ceftriaxone; if missing then S if cefazolin-S; else .
-----------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-------------------
--*Cefotetan if missing then S if cefazolin-S; else .
--------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('cefotetan')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-----------------
--*Cefoxitin if missing then S if cefazolin-S; else .
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('cefoxitin')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
---------------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then S if cefazolin-S; if missing then .
-------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-------------
--*Cefuroxime if missing then S if cefazolin-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('cefuroxime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----------------
--*Clarithromycin if missing then E erythromycin; if missing then E azithromycin; if missing then R
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'erythromycin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'erythromycin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'clarithromycin'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'azithromycin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'azithromycin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'clarithromycin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND
LOWER(antibiotic) like any ('clarithromycin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;
--------------------
--*Doxycycline if missing then S if tetracycline-S; else R
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;
----------------
--*Doripenem E meropenem
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL;
-----------------------
--*Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
----------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
-------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------------
--* Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------
--*Minocycline if missing then S if tetracycline-S; else .
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
AND LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%KLEBSIELLA%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------Proteus species-------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND
LOWER(antibiotic) like any ('clindamycin', 'daptomycin', 'doxycycline', 'linezolid', 'metronidazole', 'minocycline', 'oxacillin', 'penicillin', 'tetracycline', 'tigecycline', 'vancomycin','clarithromycin','Colistin')
AND susceptibility IS NULL;

-----------------
--*Amoxicillin-Clavulanate if missing then S if ampicillin-S; else .
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('amoxicillin/clavulanic acid')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('ampicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----
--*Azithromycin if missing then E erythromycin; if missing then E clarithromycin; if missing then R
-----
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'erythromycin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'erythromycin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) = 'azithromycin'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'clarithromycin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'clarithromycin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) = 'azithromycin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND
LOWER(antibiotic) like any ('azithromycin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

-------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
--------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------
--*Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----
--* Ceftriaxone if missing then E cefotaxime; if missing then S if cefazolin-S; else .
----
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('ceftriaxone')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----
--*Cefotaxime if missing then E ceftriaxone; if missing then S if cefazolin-S; else .
------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------
--*Cefotetan if missing then S if cefazolin-S; else .
----------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('cefotetan')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------
--*Cefoxitin if missing then S if cefazolin-S; else .
--------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('cefoxitin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
---------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime;if missing then S if cefazolin-S; if missing then .
---------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------
--*Doripenem E meropenem
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PROTEUS%'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL;
------------
--*Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
------------
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S or cefotaxime-S or cefazolin-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PROTEUS%'
AND LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PROTEUS%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime','cefazolin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------Pseudomonas aeruginosa---------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE`som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant' 
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
AND (lower(antibiotic) like  any ('%amoxicillin%clavulanic%','ampicillin','ceftriaxone', 'cefazolin','cefotaxime',
'cefotetan','cefoxitin', 'cefpodoxime','ceftaroline','cefuroxime','cephalexin','clarithromycin','clindamycin',
'daptomycin','doxycycline','ertapenem','linezolid','metronidazole','minocycline','moxifloxacin','oxacillin','penicillin','quinupristin%dalfopristin',
'tetracycline','tigecycline','vancomycin','trimethoprim/sulfamethoxazole')
)
AND susceptibility IS NULL;
------------
--*Doripenem E meropenem
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL;

----------
--*Meropenem if missing then S if imipenem-S; if missing then .
---------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
AND LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
  AND lower(antibiotic) like any ('imipenem')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-------------------
--*Piperacillin-Tazobactam if missing then S if piperacillin-S; if missing then .
-------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
AND LOWER(antibiotic) like any ('piperacillin/tazobactam')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%' 
  AND lower(antibiotic) like any ('piperacillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------serratia------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND
LOWER(antibiotic) like any ('ampicillin', 'cefazolin', 'cefotetan', 'cefoxitin', 'cefuroxime', 'clarithromycin', 'clindamycin', 'daptomycin', 'linezolid', 'metronidazole', 'oxacillin', 'penicillin', 'vancomycin','colistin','tetracycline')
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND
LOWER(antibiotic) like any ('tigecycline', 'vancomycin','ceftaroline','daptomycin','linezolid')
AND susceptibility IS NULL;

-----------
--*Cefepime if missing then S if ceftriaxone-S or cefotaxime-S; else .
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
---------------------
--*Ceftazidime if missing then S if ceftriaxone-S or cefotaxime-S; else .
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('ceftazidime')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------------
--*Ceftriaxone if missing then E cefotaxime; if missing then .
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%' 
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL;

------------
--*Cefotaxime if missing then E ceftriaxone; if missing then .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%' 
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;

------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%' 
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%' 
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------------
--*Doxycycline if missing then S if tetracycline-S; else R
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

-----
--*Doripenem E meropenem
-----
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%' 
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE '%SERRATIA%'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

-------------
--*Ertapenem if missing then S if ceftriaxone-S or cefotaxime-S; else .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

------------
--*Imipenem if missing then S if ceftriaxone-S or cefotaxime-S; else
-----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

------------
--*Meropenem if missing then S if imipenem-S; if missing then S if ceftriaxone-S or cefotaxime-S; else .
-----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('imipenem','ceftriaxone','cefotaxime')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------------
--*Minocycline if missing then S if tetracycline-S; else R
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE '%SERRATIA%'
AND LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE '%SERRATIA%'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE  '%SERRATIA%'
AND
LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------STREPTOCOCCUS PNEUMONIAE----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('amikacin', 'aztreonam', 'ceftazidime', 'ciprofloxacin', 'colistin', 'gentamicin', 'metronidazole', 'tobramycin','cefotetan','cefoxitin'

)
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('tigecycline', 'vancomycin','ceftaroline','daptomycin','linezolid')
AND susceptibility IS NULL;

---------------
--*Ampicillin if missing then E penicillin; if missing then .
---------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'ampicillin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------
--*Cefepime if missing then E ceftriaxone; if missing then S if penicillin-S; if missing then .
-----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'cefepime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

--------
--*Ceftriaxone if missing then E cefotaxime; if missing then S if penicillin-S; if missing then .
-------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('ceftriaxone')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------
--*Cefazolin if missing then S if penicillin-S; if missing then .
------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('cefazolin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-------------
--*Cefotaxime if missing then E ceftriaxone; if missing then S if penicillin-S; if missing then .
---------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then S if penicillin-S; if missing then .
-------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----------
--*Cefuroxime if missing then S if penicillin-S; if missing then .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('cefuroxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-----------------
--*Clarithromycin if missing then E erythromycin; if missing then E azithromycin; if missing then .
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'erythromycin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'erythromycin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'clarithromycin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'azithromycin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'azithromycin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'clarithromycin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------------
--* Doxycycline if missing then S if tetracycline-S; else .
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-------------
--*Doripenem E meropenem
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

------------
--*Ertapenem if missing then S if ceftriaxone-S; if missing then S if cefotaxime-S; if missing then S if penicillin-S; if missing then .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-----------------
--*Imipenem if missing then S if ceftriaxone-S; if missing then S if cefotaxime-S; if missing then S if penicillin-S; if missing then .
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

--------------
--*Meropenem if missing then S if ceftriaxone-S; if missing then S if cefotaxime-S; if missing then S if penicillin-S; if missing then .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
--------------
--*Minocycline if missing then S if tetracycline-S; else .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);
-------------
--*Moxifloxacin if missing then E levofloxacin; if missing then .
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'levofloxacin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
        AND LOWER(antibiotic) = 'levofloxacin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS PNEUMONIAE'
AND LOWER(antibiotic) = 'moxifloxacin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

--------------
--*Oxacillin if missing then S if penicillin-S; if missing then .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
AND
LOWER(antibiotic) like any ('oxacillin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS PNEUMONIAE'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------Alpha-hemolytic-----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('amikacin', 'aztreonam', 'ceftazidime', 'cefotetan', 'ciprofloxacin', 'colistin', 'gentamicin', 'metronidazole', 'tobramycin','cefoxitin','tetracycline')
AND susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('ceftaroline','daptomycin','levofloxacin','linezolid','tigecycline','vancomycin')
AND susceptibility IS NULL;

------------
--*Ampicillin if missing then E penicillin; if missing then .
------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'ampicillin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------------
--*Cefepime if missing then E ceftriaxone; if missing then S if penicillin-S; if missing then .
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'cefepime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('cefepime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

----------
--*Ceftriaxone if missing then E cefotaxime; if missing then S if penicillin-S; if missing then .
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'ceftriaxone'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('ceftriaxone')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

---------
--*Cefazolin if missing then S if penicillin-S; if missing then .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('cefazolin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


-------------
--*Cefotaxime if missing then E ceftriaxone; if missing then S if penicillin-S; if missing then .
-------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'cefotaxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('cefotaxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


----------------
--*Cefpodoxime if missing then E ceftriaxone; if missing then E cefotaxime; if missing then S if penicillin-S; if missing then .
------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'ceftriaxone'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'ceftriaxone' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;



UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'cefotaxime'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'cefotaxime' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'cefpodoxime'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('cefpodoxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

-----------------
--*Cefuroxime if missing then S if penicillin-S; if missing then .
-----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('cefuroxime')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

---------------
--*Doxycycline if missing then S if tetracycline-S; else R
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('doxycycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


---------------
--*Doripenem E meropenem
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------------
--*Ertapenem if missing then S if ceftriaxone-S; if missing then S if cefotaxime-S; if missing then S if penicillin-S; if missing then .
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('ertapenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


---------------------
--*Imipenem if missing then S if ceftriaxone-S; if missing then S if cefotaxime-S; if missing then S if penicillin-S; if missing then .
--------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('imipenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);


-------------
--*Meropenem if missing then S if ceftriaxone-S; if missing then S if cefotaxime-S; if missing then S if penicillin-S; if missing then .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('meropenem')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('ceftriaxone','cefotaxime','penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

---------------
--*Minocycline if missing then S if tetracycline-S; else .
---------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('minocycline')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('tetracycline')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

----------
--*Oxacillin if missing then S if penicillin-S; if missing then .
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
AND
LOWER(antibiotic) like any ('oxacillin')
AND susceptibility IS NULL
AND implied_susceptibility IS NULL
AND order_proc_id_coded IN (
SELECT order_proc_id_coded 
FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
WHERE UPPER(organism) LIKE 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC'
  AND lower(antibiotic) like any ('penicillin')
  AND (susceptibility = 'Susceptible' OR  implied_susceptibility='Susceptible')
);

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------- Enterococcus-------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%ENTEROCOCCUS%'
AND UPPER(antibiotic) IN ('OXACILLIN', 'CEFAZOLIN', 'CEFTRIAXONE', 'CEFEPIME', 'CEFTAZIDIME', 'ERTAPENEM', 'MEROPENEM', 'TRIMETHOPRIM/SULFAMETHOXAZOLE')
AND (susceptibility IS NULL OR susceptibility = ''); -- This line is added to update only missing or non-reported susceptibilities



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------ENTEROCOCCUS SPECIES -------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND
 lower(antibiotic) like any ('amikacin', 'aztreonam', 'cefepime', 'ceftazidime', 'ceftriaxone', 'cefazolin', 'cefotaxime', 'cefotetan', 'cefoxitin', 'cefpodoxime', 'cefuroxime', 'ciprofloxacin', 'clarithromycin', 'clindamycin', 'colistin', 'doxycycline', 'ertapenem', 'gentamicin', 'levofloxacin', 'metronidazole', 'minocycline', 'moxifloxacin', 'oxacillin','tetracycline','tobramycin')
AND (susceptibility IS NULL OR susceptibility = '') ; 

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = 'Susceptible'
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND
lower(antibiotic) like any ('tigecycline','linezolid','daptomycin','ceftaroline')
AND (susceptibility IS NULL OR susceptibility = '') ; 


--------
--*Amoxicillin-Clavulanate('Amoxicillin/Clavulanic Acid') if missing then E ampicillin; if missing then E penicillin; if missing then .
--------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'amoxicillin/clavulanic acid'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'amoxicillin/clavulanic acid'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

---------------
--*Ampicillin if missing then E penicillin; if missing then .
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'ampicillin'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

--------------
--*Ampicillin-Sulbactam(ampicillin/sulbactam) if missing then E ampicillin; if missing then E penicillin; if missing then .
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'ampicillin/sulbactam'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'ampicillin/sulbactam'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------
--*Doripenem E meropenem
----------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'meropenem'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'meropenem' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'doripenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


--------------------
--*Imipenem if missing then E ampicillin; if missing then E penicillin; if missing then .
--------------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'imipenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'imipenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;

----------------
--*Meropenem if missing then E ampicillin; if missing then E penicillin; if missing then .
----------------
UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'ampicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'meropenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


UPDATE `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
SET implied_susceptibility = CASE 
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin'
        AND (susceptibility = 'Susceptible'  OR  implied_susceptibility='Susceptible')
    ) THEN 'Susceptible'
    WHEN order_proc_id_coded IN (
        SELECT order_proc_id_coded 
        FROM `som-nero-phi-jonc101.Fatemeh_db.implied_suscept`
        WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
        AND LOWER(antibiotic) = 'penicillin' 
        AND (susceptibility = 'Resistant' OR  implied_susceptibility='Resistant')
    ) THEN 'Resistant'
    ELSE implied_susceptibility
END
WHERE UPPER(organism) LIKE 'ENTEROCOCCUS SPECIES'
AND LOWER(antibiotic) = 'meropenem'
AND susceptibility IS NULL
AND implied_susceptibility IS NULL;


