CREATE OR REPLACE TABLE som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_NoDerm_NONULL_ProcOrders AS
SELECT
    n.anon_id,
    n.jittered_note_date,
    n.question,
    n.answer,
    p.ordering_date_jittered_utc,
    p.description,
    p.order_proc_id_coded
FROM som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_No_Derm_NONULL n
LEFT JOIN som-nero-phi-jonc101.shc_core_2023.order_proc p
ON n.anon_id = p.anon_id
WHERE
    -- timestamp conversion
    TIMESTAMP(p.ordering_date_jittered_utc) BETWEEN TIMESTAMP(n.jittered_note_date) - INTERVAL 2 DAY AND TIMESTAMP(n.jittered_note_date) + INTERVAL 5 DAY;
