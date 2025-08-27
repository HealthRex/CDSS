##############################################################################################################################################################
-- GOAL:Indicates whether the patient has been in a nursing home
##############################################################################################################################################################

CREATE OR REPLACE TABLE `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_nursing_home_visits_augmented` as(
WITH procedure_nursing_home_visits AS (
    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        proc_date_jittered AS visit_date,
        'procedure' AS source,
        'Yes' AS nursing_home_visit
    FROM `som-nero-phi-jonc101.shc_core_2023.procedure`
    WHERE (code BETWEEN '99304' AND '99318')
    OR description LIKE '%nursing facility%'
),
admission_nursing_home_visits AS (
    SELECT
        anon_id,
        pat_enc_csn_id_jittered AS pat_enc_csn_id_coded,
        hosp_adm_date_jittered AS visit_date,
        'admission' AS source,
        'Yes' AS nursing_home_visit
    FROM `som-nero-phi-jonc101.shc_core_2023.f_ip_hsp_admission`
    WHERE admit_source_name IN ('SNF or ICF', 'Other Health Care Facility (Includes Nursing Homes)')
),
encounter_nursing_home_visits AS (
    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        hosp_disch_time_jittered AS visit_date,
        'encounter' AS source,
        'Yes' AS nursing_home_visit
    FROM `som-nero-phi-jonc101.shc_core_2023.encounter`
    WHERE disch_dest LIKE '%Nursing%' OR disch_dest LIKE '%SNF%' OR disch_dest LIKE '%RES%'
),
nursing_home_visits_temp as(
-- Combine All Results
SELECT * FROM procedure_nursing_home_visits
UNION ALL
SELECT * FROM admission_nursing_home_visits
UNION ALL
SELECT * FROM encounter_nursing_home_visits
)
SELECT
    a.anon_id,
    a.pat_enc_csn_id_coded,
    a.order_proc_id_coded,
    a.order_time_jittered_utc,
    b.visit_date,
    TIMESTAMP_DIFF(a.order_time_jittered_utc, TIMESTAMP(b.visit_date), DAY)  as nursing_home_visit_culture
FROM `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` a
LEFT JOIN nursing_home_visits_temp b
using(anon_id,pat_enc_csn_id_coded)
where (TIMESTAMP(b.visit_date)<=a.order_time_jittered_utc OR b.visit_date is null )
GROUP BY a.anon_id, a.pat_enc_csn_id_coded, a.order_proc_id_coded, a.order_time_jittered_utc,b.visit_date
ORder By a.anon_id, a.pat_enc_csn_id_coded, a.order_proc_id_coded, a.order_time_jittered_utc,b.visit_date
)
