-- Query to pull cohort of notes to be used for phenotyping

SELECT DISTINCT culture_orders.anon_id as anon_id, note_date_jittered, note_type
FROM (
  SELECT anon_id, order_proc_id_coded, ord_proc.description as description, order_time_jittered
  FROM `som-nero-phi-jonc101.shc_core_2022.order_proc` ord_proc
  JOIN `som-nero-phi-jonc101.gk_abx.abx_descriptions` abx_descriptions
  ON ord_proc.proc_code = abx_descriptions.proc_code AND ord_proc.description = abx_descriptions.description
) AS culture_orders
JOIN
(
  SELECT anon_id, note_date_jittered, note_type
  FROM `som-nero-phi-jonc101.shc_core_2022.clinical_doc_meta` 
  WHERE note_type not in ("Nursing Sign Out Note")
)
AS notes
ON culture_orders.anon_id = notes.anon_id
WHERE ABS(DATE_DIFF(culture_orders.order_time_jittered, notes.note_date_jittered, DAY)) <= 30


-- Output of query below is merged with descriptions manually selected (that otherwise wouldn't be included
-- because doesn't include 'CULT' in name). Saved as abx_descriptions.csv and to BQ table gk_abx.abx_descriptions

SELECT DISTINCT proc_code, proc_id, cpt_code, description
FROM `som-nero-phi-jonc101.shc_core_2022.order_proc` 
WHERE cpt_code NOT IN ("LABWDC", "LABWDCG", "LABWDCS", "LABDMCWDC") -- remove wound cultures
AND REGEXP_CONTAINS(UPPER(description), 'CULT') 
AND ( 
  SELECT LOGICAL_AND(NOT REGEXP_CONTAINS(UPPER(description), word))
  FROM UNNEST(['OCCULT', 'DIFFICULT', 'HEMOCULT', 'CULTIVATED', 'FACULTY', 'VASCULTIDES', 'VASCULITIS', 'GASTROCULT', 'FUNGAL', 'FUNGUS', 'VIRAL']) AS word
) -- created this list by examining descriptions that included CULT but not CULTURE
