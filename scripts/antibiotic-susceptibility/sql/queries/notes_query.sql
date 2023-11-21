-- Query to pull cohort of notes to be used for phenotyping

SELECT DISTINCT ord_anon_id as anon_id, note_date_jittered, note_type
FROM (
  SELECT anon_id as ord_anon_id, order_proc_id_coded, abx_select.description as description, order_time_jittered
  FROM `som-nero-phi-jonc101.shc_core_2022.order_proc` ord_proc
  JOIN `som-nero-phi-jonc101.gk_abx.abx_select` abx_select
  ON ord_proc.proc_code = abx_select.proc_code AND 
  (
    (ord_proc.proc_id = abx_select.proc_id AND ord_proc.cpt_code = abx_select.cpt_code) OR 
    ord_proc.description = abx_select.description
  )
) AS cultures
JOIN
(
  SELECT anon_id, note_date_jittered, note_type
  FROM `som-nero-phi-jonc101.shc_core_2022.clinical_doc_meta` 
  WHERE note_type not in ("Nursing Sign Out Note")
)
AS notes
ON ord_anon_id = notes.anon_id
WHERE ABS(DATE_DIFF(cultures.order_time_jittered, notes.note_date_jittered, DAY)) <= 30
