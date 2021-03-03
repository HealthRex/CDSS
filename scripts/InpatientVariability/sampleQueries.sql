-- (Elective) Orthopedic Surgery as Example
WITH

-- Identify Cases by Diagnosis Related Group
surgeryDiagnosisRelatedGroup AS
(
    select *
    from `mining-clinical-decisions.shc_core.drg_code`
    where drg_mpi_code in 
    (   '301' -- Hip Joint Replacement
        --'470',    -- Hip and Knee Joint Replacement or Reattachment w/o MCC    14K encounters
        --'301',    -- Hip Joint Replacement    9.7K encounters
        --'302'     -- Knee Joint Replacement   8.6K encounters
    )
),

-- Find all Specialty Primary Team Assignments
surgeryPrimaryEncounter AS
(
    select distinct anon_id, pat_enc_csn_id_coded
    from `mining-clinical-decisions.shc_core.treatment_team`
    where name = 'Primary Team'
    and prov_name like 'ORTHO ARTHRITIS%'
    -- Up to 1,000 cases per year
),

-- Exclude all those that passed through Emergency Department (only capture "elective" cases)
emergencyAdmissionEncounter AS
(
    select distinct anon_id, pat_enc_csn_id_coded
    from `mining-clinical-decisions.shc_core.adt`
    where pat_service_c in ('100','187') -- Emergency and Emergency Services
    and in_event_type_c = 1 -- Admission
),
surgeryNonEmergencyEncounter AS
(
    select anon_id, pat_enc_csn_id_coded
    from surgeryPrimaryEncounter 
    EXCEPT DISTINCT
    select anon_id, pat_enc_csn_id_coded
    from emergencyAdmissionEncounter 
),
surgeryNonEmergencyEncounterByYear AS
(
    select EXTRACT(YEAR FROM trtmnt_tm_begin_dt_jittered) as assignYear, count(distinct anon_id) nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
    from surgeryNonEmergencyEncounter join shc_core.treatment_team using (anon_id, pat_enc_csn_id_coded)
    group by assignYear
    order by assignYear desc
    -- Close to 1,000 patients per year, confirming most of these admissions are elective / non-emergency
),

-- Find top Admission Diagnoses for those Encounters
surgeryDiagnosisCounts AS
(  
    select source, icd9, icd10, dx_name, count(distinct snee.anon_id) as nPatients, count(distinct snee.pat_enc_csn_id_coded) as nEncounters, count(*) as nDiagnoses
    from `mining-clinical-decisions.shc_core.diagnosis_code` as dc 
        join surgeryNonEmergencyEncounter as snee on (snee.anon_id = dc.anon_id and snee.pat_enc_csn_id_coded = dc.pat_enc_csn_id_jittered)
    group by source, icd9, icd10, dx_name
    order by nPatients desc
),
surgeryDiagnosisRelatedGroupCounts AS
(
    select drg_mpi_code, drg_name, count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters, count(*) as nDiagnoses
    from `mining-clinical-decisions.shc_core.drg_code`
    group by drg_mpi_code, drg_name
    order by nEncounters desc
),

-- Calculate Length of Stay Distribution for Top Admission Diagnosis
surgeryDiagnosisRelatedGroupLengthOfStay
(
    select drg_mpi_code, drg_name, anon_id, pat_enc_csn_id_coded, 
        min(event_time_jittered) as firstEventTime,
        DATETIME_DIFF(max(event_time_jittered), min(event_time_jittered), HOUR) as lenghthOfStayHour, 
        ROUND(DATETIME_DIFF(max(event_time_jittered), min(event_time_jittered), HOUR) / 24, 2) as lenghthOfStayDay,
    from surgeryDiagnosisRelatedGroup
        join surgeryNonEmergencyEncounter using (anon_id, pat_enc_csn_id_coded)
        join shc_core.adt using (anon_id, pat_enc_csn_id_coded)
    group by drg_mpi_code, drg_name, anon_id, pat_enc_csn_id_coded
),
surgeryDRGLengthOfStayHistogram
(
    lengthOfStayHour/24 as lengthOfStayDayMin,
    count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
)
spacer AS ( select * from `mining-clinical-decisions.shc_core.demographic`)



-- Break out LoS Distribution by Primary Attending


-- Correlate Discharge Order time Relative to Discharge Time vs. Length of Stay


select *
from surgeryDRGLengthOfStayHistogram
limit 100