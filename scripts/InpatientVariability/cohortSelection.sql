####################################################################################
################## SAVE THIS AS INTERMEDIATE TABLE in KUSH_DB ######################
####################################################################################

WITH

-- Identify records to analyze; 56,149 records
# Q: how to handle scenarios where encounters overlap? ignoring for now
cohortCostAnon AS
(
    SELECT DISTINCT MRN, AdmitDate as AdmitTRUE, DischargeDate as DischTRUE, LOS, Cost_Direct
    FROM `som-nero-phi-jonc101-secure.shc_cost.costUB`
    WHERE LOWER(Inpatient) LIKE '%inpatient%'
    AND DischargeDate IS NOT NULL
    ORDER BY MRN DESC, AdmitTRUE
),

-- Match to anonymized ID to link to STARR anonymized database
-- Returns 44,205 records
cohortCostIdentified AS
(
    SELECT DISTINCT MRN_INT as mrn, ANON_ID, AdmitTRUE, DischTRUE, LOS, Cost_Direct, JITTER
    FROM cohortCostAnon as a
        JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map` as b
        # ON (a.MRN = CAST(b.MRN AS INT64)) -- MRN stored as INT64 vs. STRING; can't CAST to INT b/c some entries of format "<E12345789>"
        # ON (CAST(a.MRN AS STRING) LIKE b.MRN) -- JOINING using strings and 'LIKE' is slow, not scalable
        ON a.MRN = b.MRN_INT
    #WHERE AdmitDate = "2019-09-29"
    ORDER BY MRN_INT, ANON_ID, AdmitTRUE, DischTRUE
),

-- Clean Encounters table, obtain relevant columns, join with departments
-- Returns 1672043 records
encountersAnonymized AS
(
    SELECT DISTINCT anon_id, pat_enc_csn_id_coded as enc, hosp_admsn_time_jittered as admsnTimeJTR, hosp_dischrg_time_jittered as dischTimeJTR,
                    inpatient_data_id_coded as inptID, contact_date_jittered as contactDateJTR, department_name as dptName, specialty
    FROM `mining-clinical-decisions.shc_core.encounter`
    LEFT JOIN `mining-clinical-decisions.shc_core.dep_map`
    USING (department_id)
    WHERE enc_type = 'Hospital Encounter'
    AND appt_type IN ('Admission (Discharged)') -- many (1600+) app_type for enc_type='Hospital Encounter'
    #AND LOWER(appt_type) LIKE '%admission%'
    #AND appt_type NOT IN ('Admission (Hospital Outpatient Visit)','Lab')
    #AND anon_id LIKE '%JCde8830%'
),

-- link cohort with Encounters data
-- returned 12749 rows
-- LEFT JOINED and found that 31544 records in cohort do NOT match to encounters table when joining as above
cohortEncounterIdentified AS
(
    SELECT DISTINCT
        a.mrn, AdmitTRUE, DischTRUE, LOS, Cost_Direct, b.anon_id, enc, JITTER,
        admsnTimeJTR, dischTimeJTR--, contactDateJTR, dptName, specialty
    FROM cohortCostIdentified a
    LEFT JOIN encountersAnonymized as b
    ON (a.ANON_ID = b.anon_id
        AND AdmitTRUE + JITTER = EXTRACT(DATE FROM b.admsnTimeJTR))
        -- AND (DATE_DIFF(AdmitDate + JITTER, EXTRACT(DATE FROM c.event_time_jittered), DAY) >= -1) AND (DATE_DIFF(AdmitDate + JITTER, EXTRACT(DATE FROM c.event_time_jittered), DAY) <= 1)
    #AND enc = 131276303665
    WHERE (enc IS NOT NULL) -- returned 31544 records
    ORDER BY mrn, AdmitTRUE, DischTRUE, enc
),

-- Q: multiple records for same ENC & DRG that vary by drg_weight. Currently ignoring column. Should drg_weight be summed and taken into account?
-- drg_weight ∆= (per data dictionary): "From the list of DRGs filed to the hospital account, the weight for the DRG in this row."
-- 25849 records (avg 2.05 per encounter)
cohortDRG AS
(
    SELECT DISTINCT mrn, AdmitTRUE, DischTRUE, JITTER, LOS, Cost_Direct,
                    a.anon_id, enc, admsnTimeJTR, dischTimeJTR,
                    drg_name as drg,drg_mpi_code as drg_c#,drg_weight
    FROM cohortEncounterIdentified a
    JOIN `mining-clinical-decisions.shc_core.drg_code` b
    ON (a.anon_id = b.anon_id) AND (a.enc = b.pat_enc_csn_id_coded)
    ORDER BY MRN, enc, AdmitTRUE, DischTRUE, drg
),

-- Goal: Find top DRG by greatest A) volume, B) total cost, C) cost variation, D) LOS
-- option (1): take each DRG (multiple per enc) and associate with full admission cost. (2): take only 1 DRG per enc (idea: max(DRG_WEIGHT). idea: link with CMS DRG reimbursement, pick max)
-- CURRENTLY --> option (1), don't know how to do option (2) scalably
-- 908 DRGs records
topDRG AS
(
    -- could also do this with GROUP BY, but practicing window functions
    SELECT a.*, b.MS_DRG_NAME
    FROM
    (
        SELECT DISTINCT
                COUNT(enc) OVER drg_window AS nEnc,
                SUM(LOS) OVER drg_window AS totLOS,
                ROUND(SUM(Cost_Direct) OVER drg_window /1000,0) AS costDirectThou,
                ROUND(STDDEV_SAMP(Cost_Direct) OVER drg_window /1000,0) AS stdevDirectCostThou,
                ROUND((STDDEV_SAMP(Cost_Direct) OVER drg_window) / (SUM(Cost_Direct) OVER drg_window) * 100, 1) as stDevPctDirect,
                drg, drg_c
        FROM cohortDRG
        WINDOW drg_window AS (PARTITION BY drg)--ORDER BY drg)
        ORDER BY (stdevDirectCostThou * stdevDirectCostThou) * nEnc DESC
        #GROUP BY dx
    ) a
    LEFT JOIN `som-nero-phi-jonc101-secure.CMS_reimbursement.cms_drg_weights_2022` b
    ON (CAST(a.drg_c AS INT64) = b.MS_DRG_ID)
    ORDER BY (stdevDirectCostThou * stdevDirectCostThou) * nEnc DESC
),

selectDRGs AS
(

    SELECT *
    FROM cohortDRG # topDRG

    WHERE (drg_c IN ("870","871", "872")) -- SEVERE SEPSIS
    # WHERE (drg_c IN ("469","470") AND drg LIKE '%JOINT REPLACEMENT%') -- MAJOR HIP AND KNEE JOINT REPLACEMENT OR REATTACHMENT

    # WHERE (drg_c = "014") -- ALLOGENEIC BONE MARROW TRANSPLANT
    # WHERE (drg_c IN ("216","217","218","219","220","221") AND drg LIKE '%CARDIAC%') -- CARDIAC VALVE AND OTHER MAJOR CARDIOTHORACIC PROCEDURES: W VS W/O CARDIAC CATHETERIZATION; W VS W/O CC,MCC
    # WHERE (drg_c IN ("344","345","346") AND drg LIKE '%BOWEL%') -- MINOR SMALL & LARGE BOWEL PROCEDURES: W VS W/O CC,MCC
    # WHERE (drg_c IN ("456","457","458","459","460") AND drg LIKE '%SPINAL%') -- SPINAL FUSION EXCEPT CERVICAL
    # WHERE (drg_c IN ("881")) -- DEPRESSIVE NEUROSES
    # WHERE (drg_c IN ("885")) -- PSYCHOSES
    # WHERE (drg_c IN ("001") AND drg LIKE '%HEART TRANSPLANT%') -- HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM
    # WHERE (drg_c IN ("002") AND drg LIKE '%HEART TRANSPLANT%') -- HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM

    ORDER BY MRN, enc, AdmitTRUE, DischTRUE, drg, drg_c

),

# SELECT * FROM selectDRGs
