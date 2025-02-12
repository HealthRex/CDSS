
CREATE OR REPLACE TABLE som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_NoDerm_NoteExtraction AS
WITH ranked_notes AS (
    SELECT
        n.anon_id,
        n.jittered_note_date AS jittered_note_date_derm_table,
        d.jittered_note_date AS jittered_note_date_note,
        d.deid_note_text,
        n.question,
        n.answer,
        -- compute time difference of the jittered note date columns.
        ABS(TIMESTAMP_DIFF(n.jittered_note_date, d.jittered_note_date, SECOND)) AS time_diff,
        LENGTH(d.deid_note_text) AS note_length,
        -- configured to rank by closest then longest note. 
        ROW_NUMBER() OVER (
            PARTITION BY n.anon_id, n.jittered_note_date
            ORDER BY ABS(TIMESTAMP_DIFF(n.jittered_note_date, d.jittered_note_date, SECOND)) ASC,
                     LENGTH(d.deid_note_text) DESC
        ) AS rn
    FROM `som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_No_Dermatology` n
    JOIN `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` d
    ON n.anon_id = d.anon_id --join condition
)
SELECT 
    anon_id,
    jittered_note_date_derm_table,
    jittered_note_date_note,
    question,
    answer,
    deid_note_text
FROM ranked_notes
WHERE rn = 1; --we only want 1-1 matching.
