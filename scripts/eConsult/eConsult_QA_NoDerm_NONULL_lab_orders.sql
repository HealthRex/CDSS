
CREATE OR REPLACE TABLE som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_NoDerm_NONULL_LabResults AS
SELECT
    n.anon_id,
    n.jittered_note_date,
    n.question,
    n.answer,
    l.result_time_jittered,
    l.lab_name,
    l.result_in_range_yn,
    l.result_flag
    
FROM som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_No_Derm_NONULL n
LEFT JOIN som-nero-phi-jonc101.shc_core_2023.lab_result l
ON n.anon_id = l.anon_id
WHERE
    -- no need for timestamp conversion
    l.result_time_jittered BETWEEN n.jittered_note_date - INTERVAL 2 DAY AND n.jittered_note_date + INTERVAL 5 DAY;