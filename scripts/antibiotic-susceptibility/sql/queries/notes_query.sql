-- Query to pull cohort of notes to be used for phenotyping

SELECT DISTINCT culture_anon_id as anon_id, note_date_jittered, note_type
FROM (
  SELECT culture.anon_id as culture_anon_id, culture.order_proc_id_coded as order_proc_id_coded, 
  culture.description as description, culture.order_time_jittered as order_time_jittered
  FROM `som-nero-phi-jonc101.shc_core_2022.culture_sensitivity` culture
  JOIN `som-nero-phi-jonc101.shc_core_2022.order_proc` ord_proc
  ON culture.order_proc_id_coded = ord_proc.order_proc_id_coded
  WHERE cpt_code not in ("LABWDC", "LABWDCG", "LABWDCS", "LABDMCWDC") -- wound cultures
) AS cultures
JOIN
(
  SELECT anon_id, note_date_jittered, note_type
  FROM `som-nero-phi-jonc101.shc_core_2022.clinical_doc_meta` 
  WHERE note_type not in ("Nursing Sign Out Note")
)
AS notes
ON culture_anon_id = notes.anon_id
WHERE ABS(DATE_DIFF(cultures.order_time_jittered, notes.note_date_jittered, DAY)) <= 30
