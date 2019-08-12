-- Pts who have been on BMT service with A1c > 6.5% —> 379
 	
 SELECT count (DISTINCT(rit_uid))  FROM `starr_datalake2018.lab_result` 
  WHERE UPPER(lab_name) LIKE '%A1C%’ AND ord_num_value >= 6.5 
  AND rit_uid IN (SELECT DISTINCT(jc_uid) FROM starr_datalake2018.adt WHERE pat_service LIKE 'Bone%’)
