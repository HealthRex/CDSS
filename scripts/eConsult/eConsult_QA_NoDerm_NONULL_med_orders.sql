CREATE OR REPLACE TABLE som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_NoDerm_NONULL_MedOrders AS
SELECT
    n.anon_id,
    n.jittered_note_date,
    n.question,
    n.answer,
    m.order_inst_jittered_utc,
    m.medication_id,
    m.med_description,
    m.amb_med_disp_name
FROM som-nero-phi-jonc101.Digital_Medical_Con.eConsult_QA_No_Derm_NONULL n
LEFT JOIN som-nero-phi-jonc101.shc_core_2023.order_med m
ON n.anon_id = m.anon_id
WHERE
    --different timestamp notation that need to be changed (utc v t)
    TIMESTAMP(m.order_inst_jittered_utc) BETWEEN TIMESTAMP(n.jittered_note_date) - INTERVAL 2 DAY AND TIMESTAMP(n.jittered_note_date) + INTERVAL 5 DAY;
