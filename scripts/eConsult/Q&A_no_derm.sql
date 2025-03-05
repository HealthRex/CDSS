SELECT 
    note.anon_id,
    note.jittered_note_date,
    -- Extract Question
    TRIM(
        SUBSTR(
            note.deid_note_text, 
            INSTR(UPPER(note.deid_note_text), 'ECONSULT QUESTION') + LENGTH('ECONSULT QUESTION'),
            INSTR(UPPER(note.deid_note_text), 'ECONSULT RESPONSE') - 
            (INSTR(UPPER(note.deid_note_text), 'ECONSULT QUESTION') + LENGTH('ECONSULT QUESTION'))
        )
    ) AS question,
    -- Extract Answer
    TRIM(
        SUBSTR(
            note.deid_note_text,
            INSTR(UPPER(note.deid_note_text), 'ECONSULT RESPONSE') + LENGTH('ECONSULT RESPONSE')
        )
    ) AS answer,
    m.prov_type,
    m.dept_specialty,
    m.dept_name
FROM 
    `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` AS note
INNER JOIN 
    `som-nero-phi-jonc101.shc_core_2023.prov_map` AS m
    ON m.shc_prov_id = CAST(SUBSTR(note.author_prov_map_id, 2) AS STRING)
WHERE 
    UPPER(note.deid_note_text) LIKE '%ECONSULT QUESTION%'
    AND UPPER(note.deid_note_text) LIKE '%ECONSULT RESPONSE%'
    AND INSTR(UPPER(note.deid_note_text), 'ECONSULT RESPONSE') > 
        INSTR(UPPER(note.deid_note_text), 'ECONSULT QUESTION')
    AND UPPER(m.dept_specialty) != 'DERMATOLOGY'
ORDER BY 
    note.jittered_note_date DESC;
