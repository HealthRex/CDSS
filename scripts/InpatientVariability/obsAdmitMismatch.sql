-- Find Observation Admits vs. Inpatient Admits
-- Count how often conversions happening or times until discharge
WITH

procCodesForAdmitVsObs AS
(
    select proc_id, proc_code, description, display_name, count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
    from `som-nero-phi-jonc101.shc_core_2021.order_proc`
    where description like 'DISCHARGE%'
    and order_Type = 'ADT Discharge' -- 'Admission'

    -- and proc_code in ('ADT20','ADT13','ADT15')   -- PLACE IN OBSERVATION or PLACE IN OBSERVATION-CDA/CDU or -OTHER
    -- and proc_code in ('ADT22')   -- CONVERT INPATIENT TO OBSERVATION
    -- and proc_code in ('ADT1','ADT100')   -- ADMIT TO INPATIENT or ADMIT/PLACE PATIENT (this is not perfectly clean, as some comments reference place/convert to observation)
    -- and proc_code in ('ADT12')   -- DISCHARGE PATIENT

    group by proc_id, proc_code, description, display_name
    order by nEncounters desc
),

obsOrderSample AS
(
    select *
    from `som-nero-phi-jonc101.shc_core_2021.order_proc`
    where proc_code in ('ADT22')
    and order_status <> 'Canceled'
),

adtSample AS
(
    select *
    from `som-nero-phi-jonc101.shc_core_2021.adt`
    where pat_enc_csn_id_coded = 131297273359
    order by event_time_jittered
),
admitOrderSample AS
(
    select *
    from `som-nero-phi-jonc101.shc_core_2021.order_proc`
    where order_type in ('Admission','ADT Discharge')
    and pat_enc_csn_id_coded = 131297273359


    order by order_inst_jittered
),


adtPatClassOptions AS
(
    select pat_class, count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
    from `som-nero-phi-jonc101.shc_core_2021.adt`

    -- and pat_class in ('Outpatient','Emergency Services','Inpatient','Observation')
    -- and pat_class_c in               112 = Emergency Services, 126 = Inpatient, 128 = Observation
    group by pat_class
    order by nEncounters desc
),

-- Find all Place in Observation Orders
-- Find all Admit (to Inpatient) Orders
-- Find all Discharge Orders
-- Find all Convert Inpatient to Observation Orders

-- Find all Encounters and their earliest ADT records for Admission, Discharge and Inpatient, Observation status
encounterEarliestAdmissionADT AS
(
    select anon_id, pat_enc_csn_id_coded, min(event_time_jittered) as admitTime
    from `som-nero-phi-jonc101.shc_core_2021.adt` as admissionEvent
    where  admissionEvent.event_type_c = 1 -- Admission
    group by anon_id, pat_enc_csn_id_coded
),
encounterEarliestDischargeADT AS
(
    select anon_id, pat_enc_csn_id_coded, min(event_time_jittered) as dischargeTime
    from `som-nero-phi-jonc101.shc_core_2021.adt` as admissionEvent
    where  admissionEvent.event_type_c = 2 -- Discharge
    group by anon_id, pat_enc_csn_id_coded
),
encounterEarliestInpatientADT AS
(
    select anon_id, pat_enc_csn_id_coded, min(event_time_jittered) as earliestInpatientTime
    from `som-nero-phi-jonc101.shc_core_2021.adt` as inpatientADT
    where inpatientADT.pat_class_c = '126' -- Inpatient
    group by anon_id, pat_enc_csn_id_coded
),
encounterEarliestObservationADT AS
(
    select anon_id, pat_enc_csn_id_coded, min(event_time_jittered) as earliestObservationTime
    from `som-nero-phi-jonc101.shc_core_2021.adt` as inpatientADT
    where inpatientADT.pat_class_c = '128' -- Observation
    group by anon_id, pat_enc_csn_id_coded
),

-- Find all Encounters in ADT Records with an Inpatient pat_class_c = 126
    -- Calculate Admission duration: Final event_type = Discharge (event_type_c = 2) minus event_tye = Admission (event_type_c = 1)
    -- Add columns for whether time within 24hr, 48hr, 72hr
encounterInpatientDuration AS
(
    select anon_id, pat_enc_csn_id_coded, 
        admitTime, earliestInpatientTime, dischargeTime,
        dischargeTime-admitTime as encounterDuration,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) as encounterDurationHour,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <24 as encounterDurationWithin24hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <48 as encounterDurationWithin48hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <72 as encounterDurationWithin72hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR)>=72 as encounterDurationBeyond72hr,
    from encounterEarliestInpatientADT
        inner join encounterEarliestAdmissionADT using (anon_id, pat_enc_csn_id_coded)
        inner join encounterEarliestDischargeADT using (anon_id, pat_enc_csn_id_coded)
    where admitTime <= dischargeTime -- Filter out abberant results where have out of order admit-discharge times that likely reflect some missing data
),
-- Find all Encounters in ADT Records with an Observation pat_class_c = 128
    -- Calculate Admission duration: Final event_type = Discharge (event_type_c = 2) minus event_tye = Admission (event_type_c = 2)
    -- Add columns for whether time within 24hr, 48hr, 72hr
encounterObservationDuration AS
(
    select anon_id, pat_enc_csn_id_coded, 
        admitTime, earliestObservationTime, dischargeTime,
        dischargeTime-admitTime as encounterDuration,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) as encounterDurationHour,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <24 as encounterDurationWithin24hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <48 as encounterDurationWithin48hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <72 as encounterDurationWithin72hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR)>=72 as encounterDurationBeyond72hr,
    from encounterEarliestObservationADT
        inner join encounterEarliestAdmissionADT using (anon_id, pat_enc_csn_id_coded)
        inner join encounterEarliestDischargeADT using (anon_id, pat_enc_csn_id_coded)
    where admitTime <= dischargeTime -- Filter out abberant results where have out of order admit-discharge times that likely reflect some missing data
),

-- Find Encounters where had both an Observation and Inpatient period (join above results)
    -- Calculate earliest Inpatient time minus earliest Observation time
        -- If positive or negative, indicates which way the conversion was made
    -- Add columns for whether Inpatient to Observation time within 24hr, 48hr, 72hr
    -- Add columns for whether Observation to Inpatient time within 24hr, 48hr, 72hr
encounterObservationAndInpatientDuration AS
(
    select anon_id, pat_enc_csn_id_coded, 
        admitTime, earliestObservationTime, earliestInpatientTime, dischargeTime,
        dischargeTime-admitTime as encounterDuration,
        earliestObservationTime-admitTime as timeUntilObservation,
        earliestInpatientTime-admitTime as timeUntilInpatient,
        earliestInpatientTime-earliestObservationTime as timeFromObservationToInpatient,    -- Could be negative if started Inpatient then converted back to Obs

        DATETIME_DIFF(dischargeTime, admitTime, HOUR) as encounterDurationHour,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <24 as encounterDurationWithin24hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <48 as encounterDurationWithin48hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR) <72 as encounterDurationWithin72hr,
        DATETIME_DIFF(dischargeTime, admitTime, HOUR)>=72 as encounterDurationBeyond72hr,

        DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) as observationToInpatientHours,
        DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) >= 0 and DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) <24 as observationToInpatientWithin24hr,
        DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) >= 0 and DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) <48 as observationToInpatientWithin48hr,
        DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) >= 0 and DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) <72 as observationToInpatientWithin72hr,
        DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) >= 0 and DATETIME_DIFF(earliestInpatientTime, earliestObservationTime, HOUR) >=72 as observationToInpatientBeyond72hr,

        DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) as inpatientToObservationHours, -- Just flip the above for convenience to avoid negative number interpretation
        DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) >= 0 and DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) <24 as inpatientToObservationWithin24hr,
        DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) >= 0 and DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) <48 as inpatientToObservationWithin48hr,
        DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) >= 0 and DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) <72 as inpatientToObservationWithin72hr,
        DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) >= 0 and DATETIME_DIFF(earliestObservationTime, earliestInpatientTime, HOUR) >=72 as inpatientToObservationBeyond72hr,

    from encounterEarliestObservationADT
        inner join encounterEarliestInpatientADT using (anon_id, pat_enc_csn_id_coded)
        inner join encounterEarliestAdmissionADT using (anon_id, pat_enc_csn_id_coded)
        inner join encounterEarliestDischargeADT using (anon_id, pat_enc_csn_id_coded)
    where admitTime <= dischargeTime -- Filter out abberant results where have out of order admit-discharge times that likely reflect some missing data
),

-- Summarize Inpatient Durations (includes those who convert in or out of Observation, so may need to subtract some from joint counts)
--  2020 - 32,947 encounters in 2020. 1,219 (3.7%) discharged within 24 hours, 6,527 (20%) discharged within 48 hours
summaryInpatientDuration AS
(
    select 
        EXTRACT(YEAR from admitTime) as admitYear,
        count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters,
        avg(encounterDurationHour) as encounterDurationHourAvg, stddev_samp(encounterDurationHour) as encounterDurationHourStdDevS,
        countif(encounterDurationWithin24hr) as nEncounterDurationWithin24hr,
        countif(encounterDurationWithin48hr) as nEncounterDurationWithin48hr,
        countif(encounterDurationWithin72hr) as nEncounterDurationWithin72hr,
        countif(encounterDurationBeyond72hr) as nEncounterDurationBeyond72hr
    from encounterInpatientDuration
    group by admitYear
    order by admitYear desc
),
-- Summarize Observation Durations (includes those who convert in or out of Inpatient, so may need to subtract some from joint counts)
--  2020 - 12,717 encounters in 2020. 3,646 (29%) discharged within 24 hours, 8,545 (67%) discharged within 48 hours
summaryObservationDuration AS
(
    select 
        EXTRACT(YEAR from admitTime) as admitYear,
        count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters,
        avg(encounterDurationHour) as encounterDurationHourAvg, stddev_samp(encounterDurationHour) as encounterDurationHourStdDevS,
        countif(encounterDurationWithin24hr) as nEncounterDurationWithin24hr,
        countif(encounterDurationWithin48hr) as nEncounterDurationWithin48hr,
        countif(encounterDurationWithin72hr) as nEncounterDurationWithin72hr,
        countif(encounterDurationBeyond72hr) as nEncounterDurationBeyond72hr
    from encounterObservationDuration
    group by admitYear
    order by admitYear desc
),
-- Summarize Durations when both an Observation and Inpatient period (indicating a conversion in one direction or the other)
summaryInpatientAndObservationDuration AS
(
    select 
        EXTRACT(YEAR from admitTime) as admitYear,
        count(distinct anon_id) as nPatients, 

        -- 2020 - 4,439 encounters, 337 (7.6%) discharge within 24 hours, 1166 (26%) discharge within 48 hours
        count(distinct pat_enc_csn_id_coded) as nEncounters,
        avg(encounterDurationHour) as encounterDurationHourAvg, stddev_samp(encounterDurationHour) as encounterDurationHourStdDevS,
        countif(encounterDurationWithin24hr) as nEncounterDurationWithin24hr,
        countif(encounterDurationWithin48hr) as nEncounterDurationWithin48hr,
        countif(encounterDurationWithin72hr) as nEncounterDurationWithin72hr,
        countif(encounterDurationBeyond72hr) as nEncounterDurationBeyond72hr,

        -- 2020 - 3719 encounters where observation before inpatient, 1923 (52%) converted to inpatient within 24 hours, 3156 (85%) within 48 hours
        countif(observationToInpatientHours >=0 ) as nEncounterObservationBeforeInpatient,
        avg(observationToInpatientHours) as observationToInpatientHourAvg, stddev_samp(observationToInpatientHours) as observationToInpatientStdDevS,
        countif(observationToInpatientWithin24hr) as observationToInpatientWithin24hr,
        countif(observationToInpatientWithin48hr) as observationToInpatientWithin48hr,
        countif(observationToInpatientWithin72hr) as observationToInpatientWithin72hr,
        countif(observationToInpatientBeyond72hr) as observationToInpatientBeyond72hr,

        -- 2020 - 1006 encounters where inpatient converted to observation, 923 (92%) converted to observation with 24 hours, 992 (98%) within 48 hours
        countif(inpatientToObservationHours >=0 ) as nEncounterInpatientBeforeObservation,
        avg(inpatientToObservationHours) as inpatientToObservationHourAvg, stddev_samp(inpatientToObservationHours) as inpatientToObservationStdDevS,
        countif(inpatientToObservationWithin24hr) as inpatientToObservationWithin24hr,
        countif(inpatientToObservationWithin48hr) as inpatientToObservationWithin48hr,
        countif(inpatientToObservationWithin72hr) as inpatientToObservationWithin72hr,
        countif(inpatientToObservationBeyond72hr) as inpatientToObservationBeyond72hr
    from encounterObservationAndInpatientDuration
    group by admitYear
    order by admitYear desc
),


-- Summary of the observation ONLY cases who never made it to inpatient admission status
-- Approximate it by taking the summaryObservationDuration results and subtract out those who went from obs to Inaptient
summaryObserationOnlyDuration AS
(
    select
        admitYear,
        obs.nEncounters - obsInpt.nEncounterObservationBeforeInpatient as nEncounterObsOnly,
        obs.nEncounterDurationWithin24Hr - obsInpt.observationToInpatientWithin24hr as nEncounterObsOnlyDurationWithin24Hr,
        obs.nEncounterDurationWithin48Hr - obsInpt.observationToInpatientWithin48hr as nEncounterObsOnlyDurationWithin48Hr,
        obs.nEncounterDurationWithin72Hr - obsInpt.observationToInpatientWithin72hr as nEncounterObsOnlyDurationWithin72Hr,
        obs.nEncounterDurationBeyond72Hr - obsInpt.observationToInpatientBeyond72hr as nEncounterObsOnlyDurationBeyond72Hr
    from 
        summaryObservationDuration as obs
        join summaryInpatientAndObservationDuration obsInpt
        using (admitYear)
    order by 
        admitYear desc
),
placeholder AS (select 1 from `som-nero-phi-jonc101.shc_core_2021.demographic`)

select * 
from summaryObserationOnlyDuration
limit 1000

