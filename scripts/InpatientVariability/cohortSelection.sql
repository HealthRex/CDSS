-- Reconstruct cohort of inpatient cost data against clinical EMR data
-- Temp versions of some result tables saved to kush_db dataset.

WITH

-- Identify records to analyze; 56,149 records -- Inpatient encounter cost data available
# Q: how to handle scenarios where encounters overlap? ignoring for now
cohortCostAnon AS
(
    SELECT DISTINCT 
      MRN, 
      AdmitDate, DischargeDate, LOS, 
      MSDRGweight,
      Cost_Direct, Cost_Indirect, Cost_Total,
      Cost_Breakdown_Blood,
      Cost_Breakdown_Cardiac,
      Cost_Breakdown_ED,
      Cost_Breakdown_ICU,
      Cost_Breakdown_IICU,
      Cost_Breakdown_Imaging,
      Cost_Breakdown_Labs,
      Cost_Breakdown_Implants,
      Cost_Breakdown_Supplies,
      Cost_Breakdown_OR,
      Cost_Breakdown_OrganAcq,
      Cost_Breakdown_Other,
      Cost_Breakdown_PTOT,
      Cost_Breakdown_Resp,
      Cost_Breakdown_Accom,
      Cost_Breakdown_Pharmacy
    FROM `som-nero-phi-jonc101-secure.shc_cost.costUB`
    WHERE Inpatient_c = 'I' -- Inpatient
    AND DischargeDate IS NOT NULL
    --ORDER BY MRN DESC, AdmitTRUE
),

-- Match to anonymized ID to link to STARR anonymized database
-- Returns 44,205 records
cohortCostIdentified AS
(
    SELECT DISTINCT 
      map.MRN, map.MRN_INT, ANON_ID,
      JITTER,
      cca.* -- Capture all of the original info from the cost cohort table
    FROM cohortCostAnon as cca
        JOIN `som-nero-phi-jonc101-secure.starr_map.shc_map` as map
        # ON (a.MRN = CAST(b.MRN AS INT64)) -- MRN stored as INT64 vs. STRING; can't CAST to INT b/c some entries of format "<E12345789>"
        # ON (CAST(a.MRN AS STRING) LIKE b.MRN) -- JOINING using strings and 'LIKE' is slow, not scalable
        ON cca.MRN = map.MRN_INT
    --ORDER BY MRN_INT, ANON_ID, AdmitTRUE, DischTRUE
),

-- Encounters table, obtain relevant columns, join with departments
-- Returns 1672043 records
encountersAnonymized AS
(
    SELECT DISTINCT 
      anon_id, pat_enc_csn_id_coded, 
      hosp_admsn_time_jittered, hosp_dischrg_time_jittered,
      inpatient_data_id_coded , contact_date_jittered --, department_name, specialty
    FROM `mining-clinical-decisions.shc_core.encounter`
      --LEFT JOIN `mining-clinical-decisions.shc_core.dep_map`
      --  USING (department_id)
    WHERE enc_type = 'Hospital Encounter'
    AND appt_type IN ('Admission (Discharged)') -- many (1600+) app_type for enc_type='Hospital Encounter' such as radiology, infusion, etc.
    #AND LOWER(appt_type) LIKE '%admission%'
    #AND appt_type NOT IN ('Admission (Hospital Outpatient Visit)','Lab')
    #AND anon_id LIKE '%JCde8830%'
),

-- Link cost cohort with Encounters data via reidentified ID linkage
--  Trying to match based on same MRN and Date of admission
-- returned 12749 rows if exact match by admit date. 
--    15,389 if match by +/- 1 day of admit date, 17982 within +/- 7 days, 25567 +/- 30 days
-- >49K if match by same year, too blunt. Maybe should match by nearest matching date???? Or Manually reconstruct why some records not finding a match?
cohortEncounterIdentified AS
(
    SELECT DISTINCT
        cci.*,
        enc.pat_enc_csn_id_coded, hosp_admsn_time_jittered, hosp_dischrg_time_jittered
    FROM cohortCostIdentified cci
      JOIN encountersAnonymized as enc
      ON  (  cci.ANON_ID = enc.anon_id
            
            -- Join by exact date match
            -- AND AdmitDate + jitter = EXTRACT(DATE FROM enc.hosp_admsn_time_jittered) 
            
            -- Join by date match within +/- 7 day
            AND (DATE_DIFF(AdmitDate + JITTER, EXTRACT(DATE FROM enc.hosp_admsn_time_jittered), DAY) >= -0) 
            AND (DATE_DIFF(AdmitDate + JITTER, EXTRACT(DATE FROM enc.hosp_admsn_time_jittered), DAY) <= +0)
          )
    #AND enc = 131276303665
    --WHERE (enc IS NOT NULL) -- returned 31544 records
    --ORDER BY mrn, AdmitTRUE, DischTRUE, enc
),

-- Find all DRGs per encounter
-- Q: multiple records for same ENC & DRG that vary by drg_weight. Currently ignoring column. Should drg_weight be summed and taken into account?
-- drg_weight ∆= (per data dictionary): "From the list of DRGs filed to the hospital account, the weight for the DRG in this row."
-- 25849 records (avg 2.05 per encounter)
cohortDRG AS
(
    SELECT DISTINCT 
      cei.*,
      drg.drg_name, drg.drg_mpi_code --, drg.drg_weight
    FROM cohortEncounterIdentified AS cei
      JOIN `mining-clinical-decisions.shc_core.drg_code` AS drg
      USING (anon_id, pat_enc_csn_id_coded)
    -- ORDER BY MRN, enc, AdmitTRUE, DischTRUE, drg
),

-- Goal: Find top DRG by greatest A) volume, B) total cost, C) cost variation, D) LOS
-- option (1): take each DRG (multiple per enc) and associate with full admission cost. (2): take only 1 DRG per enc (idea: max(DRG_WEIGHT). idea: link with CMS DRG reimbursement, pick max)
-- CURRENTLY --> option (1), don't know how to do option (2) scalably
-- could also do this with GROUP BY, but practicing window functions
costVarPerDRG AS
(
    SELECT DISTINCT
      drg_mpi_code, drg_name, 
      count(distinct anon_id) AS nPatients,
      COUNT(distinct pat_enc_csn_id_coded) AS nEncounters,
      ROUND(AVG(LOS),2) AS LOSAverage,
      ROUND(STDDEV_SAMP(LOS),2) AS LOSStdDevS,
      --SUM(LOS) AS LOSTotal,
      ROUND(AVG(Cost_Direct)) AS costDirectAverage,
      SUM(Cost_Direct) AS costDirectTotal,
      ROUND(STDDEV_SAMP(Cost_Direct)) AS costDirectStdDevS,
      ROUND(AVG(Cost_Direct/LOS)) AS costDirectOverLOSAverage,
      ROUND(STDDEV_SAMP(Cost_Direct/LOS)) AS costDirectOverLOSStdDevS,  -- If most variability explained by LOS, try scaling by it to see what's lingering
      ROUND(STDDEV_SAMP(Cost_Direct) * COUNT(distinct pat_enc_csn_id_coded)) AS costVariabilityScore,
      ROUND(STDDEV_SAMP(Cost_Direct/LOS) * COUNT(distinct pat_enc_csn_id_coded)) AS costVariabilityOverLOSScore
    FROM cohortDRG
    GROUP BY drg_mpi_code, drg_name
    ORDER BY costVariabilityOverLOSScore DESC
),

/*
-- Goal: Find top DRG by greatest A) volume, B) total cost, C) cost variation, D) LOS
-- option (1): take each DRG (multiple per enc) and associate with full admission cost. (2): take only 1 DRG per enc (idea: max(DRG_WEIGHT). idea: link with CMS DRG reimbursement, pick max)
-- CURRENTLY --> option (1), don't know how to do option (2) scalably
-- 908 DRGs records
topDRG AS
(
    SELECT a.*, cms_drg_weights.MS_DRG_NAME
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
        ORDER BY (stdevDirectCostThou) * nEnc DESC
        #GROUP BY dx
    ) as 
    LEFT JOIN `som-nero-phi-jonc101-secure.CMS_reimbursement.cms_drg_weights_2022` AS cms_drg_weights
    ON (CAST(a.drg_c AS INT64) = cms_drg_weights.MS_DRG_ID)
    -- ORDER BY (stdevDirectCostThou) * nEnc DESC
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
*/
placeholder AS (select 1 from `som-nero-phi-jonc101.shc_core_2021.demographic`)

SELECT *
from costVarPerDRG

limit 1000


