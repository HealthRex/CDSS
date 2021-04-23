WITH cohort_bugs AS (
SELECT DISTINCT
  a.anon_id, a.pat_enc_csn_id_coded, a.index_time, cs.organism, cs.description
FROM  
  `mining-clinical-decisions.abx.final_ast_labels` a
INNER JOIN
  `mining-clinical-decisions.abx.culture_orders_within_24_hrs` cult_orders
USING
  (pat_enc_csn_id_coded)
INNER JOIN 
  `som-nero-phi-jonc101.shc_core.culture_sensitivity` cs
USING
  (order_proc_id_coded)
WHERE EXTRACT(YEAR FROM a.index_time) BETWEEN 2009 and 2019
), 

adt_dep as (
SELECT DISTINCT
  adt.pat_enc_csn_id_coded, 
  FIRST_VALUE(dm.department_name) OVER 
  (PARTITION BY adt.pat_enc_csn_id_coded ORDER BY adt.effective_time_jittered_utc) department_name,
FROM 
  `shc_core.adt` adt
INNER JOIN
  `som-nero-phi-jonc101.shc_core.dep_map` dm
USING
  (department_id)
)

SELECT c.*, a.department_name
FROM cohort_bugs c
INNER JOIN adt_dep a
USING (pat_enc_csn_id_coded)

