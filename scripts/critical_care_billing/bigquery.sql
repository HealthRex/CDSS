WITH

med7_csn AS (
  SELECT DISTINCT
    ANY_VALUE(anon_id) AS anon_id,
    pat_enc_csn_id_coded,
    ANY_VALUE(prov_name) AS prov_name,
    MIN(DATE(trtmnt_tm_begin_dt_jittered)) AS med7_start_date,
  FROM `som-nero-phi-jonc101.shc_core_2024.treatment_team` 
  WHERE (
    prov_name LIKE '%MED UNIV 7%'
    OR prov_name LIKE '%MED UNIV HOSP MED%'
    OR prov_name LIKE '%MED UNIV LOLA%'
    OR prov_name LIKE '%MED UNIV SURGE%'
  )
  AND trtmnt_tm_begin_dt_jittered BETWEEN DATE('2022-01-01') AND DATE('2023-12-31')
  GROUP BY pat_enc_csn_id_coded
),

med7_notes AS (
  SELECT
    med7_csn.pat_enc_csn_id_coded,
    med7_csn.prov_name,
    DATE(notes.jittered_note_date) AS note_date,
    notes.note_type_desc,
    notes.author_prov_map_id,
    prov_map.prov_type,
    prov_map.specialty_or_dept,
    dep_map.department_name
  FROM `som-nero-phi-jonc101-secure.Deid_Notes_Jchen.Deid_Notes_SHC_JChen` as notes
  INNER JOIN med7_csn 
    ON med7_csn.pat_enc_csn_id_coded = notes.offest_csn
  INNER JOIN `som-nero-phi-jonc101.shc_core_2024.dep_map` as dep_map
    ON notes.effective_dept_id = dep_map.department_id
  INNER JOIN `som-nero-phi-jonc101.shc_core_2024.prov_map` as prov_map
    ON SUBSTR(notes.author_prov_map_id, 2) = prov_map.shc_prov_id
),

med7_cpt AS (
  SELECT
    cpt.pat_enc_csn_id_coded,
    DATE(cpt.start_date_jittered) AS cpt_date,    
    cpt.code,
    prov_map.prov_type,
    prov_map.specialty_or_dept
  FROM `som-nero-phi-jonc101.shc_core_2024.procedure` as cpt
  INNER JOIN med7_csn
    ON med7_csn.pat_enc_csn_id_coded = cpt.pat_enc_csn_id_coded
  INNER JOIN `som-nero-phi-jonc101.shc_core_2024.prov_map` as prov_map
    ON SUBSTR(cpt.billing_prov_map_id, 2) = prov_map.shc_prov_id
  
),

code_blue_notes AS (
  SELECT
    med7_notes.pat_enc_csn_id_coded,
    note_date,
    prov_name AS note_writer,
    med7_notes.prov_type AS note_writer_type,
    med7_notes.specialty_or_dept as note_writer_dept,
    department_name,
    med7_cpt.code,
    med7_cpt.prov_type AS billing_type,
    med7_cpt.specialty_or_dept as billing_dept
  FROM med7_notes
  LEFT JOIN med7_cpt
    ON med7_notes.pat_enc_csn_id_coded = med7_cpt.pat_enc_csn_id_coded
    AND med7_notes.note_date = med7_cpt.cpt_date
    AND (med7_cpt.code = '99291' OR med7_cpt.code = '92950')
  WHERE lower(note_type_desc) LIKE '%code%'
  GROUP BY pat_enc_csn_id_coded, note_date, prov_name, department_name, note_writer_type, note_writer_dept, code, billing_type, billing_dept
),

acp_notes AS (
  SELECT
    med7_notes.pat_enc_csn_id_coded,
    note_date,
    prov_name AS note_writer,
    med7_notes.prov_type AS note_writer_type,
    med7_notes.specialty_or_dept as note_writer_dept,
    department_name,
    med7_cpt.prov_type AS billing_type,
    med7_cpt.specialty_or_dept as billing_dept
  FROM med7_notes
  LEFT JOIN med7_cpt
    ON med7_notes.pat_enc_csn_id_coded = med7_cpt.pat_enc_csn_id_coded
    AND med7_notes.note_date = med7_cpt.cpt_date
    AND med7_cpt.code = '99497'
  WHERE lower(note_type_desc) LIKE '%goals%'
  GROUP BY pat_enc_csn_id_coded, note_date, prov_name, department_name, note_writer_type, note_writer_dept, billing_type, billing_dept
)

SELECT * FROM acp_notes
