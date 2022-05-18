# For each bug, what fraction of the time is the antibiotic suscept listed?
WITH num_orders_with_bug AS (
SELECT organism, COUNT (DISTINCT CONCAT(CAST (order_proc_id_coded AS STRING), sens_organism_sid)) total_bugs_grown
FROM `mining-clinical-decisions.conor_db.abx_ast_long`
GROUP BY organism
ORDER BY total_bugs_grown DESC
)

SELECT organism,  antibiotic, COUNT (DISTINCT CONCAT(CAST (order_proc_id_coded AS STRING), sens_organism_sid)) total_times_ast_reported, total_bugs_grown
FROM `mining-clinical-decisions.conor_db.abx_ast_long` abx
INNER JOIN num_orders_with_bug total
USING (organism)
GROUP BY organism, antibiotic, total_bugs_grown
ORDER BY total_bugs_grown desc, organism, antibiotic 
