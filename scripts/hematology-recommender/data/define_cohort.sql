-- Script modified from https://github.com/HealthRex/CDSS/blob/master/scripts/OutpatientReferral/sampleQueries.sql

-- Define Cohort
-- 1. A) Find all patients that were referred to hematology (by their primary care physician?)
WITH
    referringEncounters AS
            (
                select op.anon_id, op.pat_enc_csn_id_coded as referringEncounterId, 
                enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
                from `mining-clinical-decisions.shc_core.order_proc` as op 
                join `mining-clinical-decisions.shc_core.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
                where proc_id = 34352 -- REFERRAL TO HEMATOLOGY CLINIC
                and ordering_mode = 'Outpatient'
                and appt_type in ('Office Visit','Appointment')
                -- and EXTRACT(YEAR from order_time_jittered) < 2019
                -- 16944 Historic Records - Hematology
            ),
    -- 2. B) Find all new patients that see a hematology specialist
    newPatientEncounters AS
        (
            select enc.anon_id, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
            from `mining-clinical-decisions.shc_core.encounter` as enc join `mining-clinical-decisions.shc_core.dep_map` as dep on enc.department_id = dep.department_id 
            where dep.specialty_dep_c = '14' -- dep.specialty like 'Hematology'
            and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
            -- LB q: what's the difference between NEW PATIENT VISIT 15 and NEW PATIENT VISIT 30?
            -- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
            and appt_status = 'Completed'
            -- 30592 historic records - Hematology
        ),

-- 3. A) and B), patients that were referred to hematology and actually got there
    baseCohort AS 
    (
        select henc.anon_id as anon_id, href.referralOrderDateTime, href.referringEncounterId, henc.specialtyEncounterDateTime, henc.specialtyEncounterId
        from newPatientEncounters as henc join referringEncounters as href on henc.anon_id = href.anon_id
        -- LB: Add WHERE SP.SP_app_datetime BETWEEN PC.PC_ref_datetime AND DATETIME_ADD(PC.PC_ref_datetime, INTERVAL 4 MONTH)?
 
        --  12364 patients

    ),

-- 4. Extract a basic table that I can manipulate to graph relevant info for understanding.
-- Table merges baseCohort on anon_id
-- LB: should I use anon_id or referringEncounterId for the join? anon_id, but referringEncounterId for T2 so I only get the data for that specific date (?) 
    demographicData AS
    (
        select demo.anon_id, demo.gender, demo.birth_date_jittered as birthDate, demo.canonical_race as race, demo.canonical_ethnicity as ethnicity, demo.bmi, 
        -- demo.INSURANCE_PAYOR_NAME, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL this may influence the lab results chosen
        from baseCohort as bc join `mining-clinical-decisions.shc_core.demographic` as demo on bc.anon_id  = demo.anon_id
    ),

    diagnosisT1 AS
    (
        select diag.anon_id, diag.icd9, diag.icd10, diag.dx_name, diag.start_date as diagDate, diag_ccsr.CCSR_CATEGORY_1 as cssr_code, diag_ccsr.Category_1_Description as cssr_description
        from baseCohort as bc join `mining-clinical-decisions.shc_core.diagnosis_code` as diag on bc.referringEncounterId  = diag.pat_enc_csn_id_jittered
        join `mining-clinical-decisions.mapdata.ahrq_ccsr_diagnosis` as diag_ccsr on diag.icd10 = diag_ccsr.icd10
        where diag.start_date <= bc.referralOrderDateTime
        
    ),
    -- For later: see if including the diag of the referral date (using the encounter in the join) is helpful as feats
    -- diagnosisReferralT1 AS
    -- (
    --     select diag.icd9, diag.icd10, diag.dx_name, diag.start_date as diagDate
    --     from baseCohort as bc RIGHT JOIN `mining-clinical-decisions.shc_core.diagnosis_code` as diag on bc.referringEncounterId  = diag.pat_enc_csn_id_jittered
    --     where diag.start_date <= bc.referralOrderDateTime
    -- ),

    -- also match on encounter id for proc and meds as extra feats
    orderedProceduresT1 AS
    (
        select op.anon_id, op.proc_id, op.proc_code, op.description, op.order_time_jittered as orderedProcedureDateTime
        from baseCohort as bc join `mining-clinical-decisions.shc_core.order_proc` as op on bc.referringEncounterId = op.pat_enc_csn_id_coded
        where op.order_time_jittered BETWEEN DATETIME_ADD(bc.referralOrderDateTime, INTERVAL -12 MONTH) and bc.referralOrderDateTime
        -- 1240172 observations
    ),

    orderedMedsT1 AS
    (
        select om.anon_id, om.pharm_class_name, om.thera_class_name, om.pharm_class_abbr, om.thera_class_abbr, om.order_start_time as medOrderDateTime
        from baseCohort as bc join `mining-clinical-decisions.shc_core.order_med`as om on bc.referringEncounterId = om.pat_enc_csn_id_coded
        where om.order_start_time BETWEEN DATETIME_ADD(bc.referralOrderDateTime, INTERVAL -6 MONTH) and bc.referralOrderDateTime
        -- 165645 observations
    ),

    labResultsT1 AS
    (
        select lr.anon_id, lr.component_id, lr.group_lab_name, lr.base_name, lr.ord_num_value, lr.result_flag, lr.order_time as labOrderedDateTime, lr.result_time as labResultDateTime
        -- other possible cols: lr.reference_low, lr.reference_high 
        from baseCohort as bc join `mining-clinical-decisions.shc_core.lab_result`as lr on bc.referringEncounterId = lr.pat_enc_csn_id_coded
        where lr.result_time BETWEEN DATETIME_ADD(bc.referralOrderDateTime, INTERVAL -6 MONTH) and bc.referralOrderDateTime
        -- 904939 observations
        -- lr.ordering_mode = 'Outpatient'
    ),

-- T2 information
    diagnosisT2 AS
    (
        select diag.anon_id, diag.icd9, diag.icd10, diag.dx_name, diag.start_date as diagDate, diag_ccsr.CCSR_CATEGORY_1 as cssr_code, diag_ccsr.Category_1_Description as cssr_description
        from baseCohort as bc join `mining-clinical-decisions.shc_core.diagnosis_code` as diag on bc.specialtyEncounterId  = diag.pat_enc_csn_id_jittered
        join `mining-clinical-decisions.mapdata.ahrq_ccsr_diagnosis` as diag_ccsr on diag.icd10 = diag_ccsr.icd10
        where diag.start_date BETWEEN bc.specialtyEncounterDateTime AND DATETIME_ADD(bc.specialtyEncounterDateTime, INTERVAL 2 MONTH)
        -- LB: how's time here = or =>?
    ),

    orderedProceduresT2 AS
    (
        select op.anon_id, op.proc_id, op.proc_code, op.description, op.order_time_jittered as orderedProcedureDateTime
        from baseCohort as bc RIGHT JOIN `mining-clinical-decisions.shc_core.order_proc` as op on bc.specialtyEncounterId  = op.pat_enc_csn_id_coded
        where op.order_time_jittered BETWEEN bc.specialtyEncounterDateTime AND DATETIME_ADD(bc.specialtyEncounterDateTime, INTERVAL 1 DAY)
    )

    -- Example on how to download a table: run the full query and download the result

    select *
    from baseCohort

    -- LB: should there be med orders in target? not for now
    -- orderedMedsT2 AS
    -- (
    --     select om.anon_id, om.pharm_class_name, om.thera_class_name, om.pharm_class_abbr, om.thera_class_abbr, om.order_start_time as medOrderDateTime
    --     from baseCohort as bc RIGHT JOIN `mining-clinical-decisions.shc_core.order_med`as om on bc.specialtyEncounterId = om.pat_enc_csn_id_coded
    --     where om.order_start_time = bc.referralOrderDateTime
    -- )
--  exploratory counts
    -- countsDiagnosisT1 AS
    -- (
    --     select diag.icd9, diag.icd10, diag.dx_name, count(*)
    --     from diagnosisHistT1 as diag
    --     group by diag.icd9, diag.icd10, diag.dx_name
    --     order by count(*) desc
    --     --  13920 diag codes
    -- ),


    --     countsOrderedProceduresT1 AS
    -- (
    --     select op.proc_id,	op.proc_code, op.description, count(*)
    --     from orderedProceduresT1 as op
    --     group by op.proc_id, op.proc_code, op.description
    --     order by count(*) desc
    --     -- 6750 distinct procedures
    -- ),
