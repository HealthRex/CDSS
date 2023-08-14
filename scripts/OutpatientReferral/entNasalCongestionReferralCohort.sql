-- Define patient encounter cohorts using common table expressions (CTEs) based on referrals and arrivals at a particular specialty
-- Use the params options at the head to define different filters for different specialties.
-- Can subsequently use queries in encounterCohortDescription.sql to describe the cohorts.

WITH 
-- Set modifiable query parameters in one place here, so can abstract the subsequent queries structures below
-- Replace values to those of different cohorts of interest
-- https://stackoverflow.com/questions/29759628/setting-big-query-variables-like-mysql
-- https://medium.com/google-cloud/how-to-work-with-array-and-structs-in-bigquery-9c0a2ea584a6
params AS 
(
	select 
		2022
			as cohortYear,			-- Restrict to one year for simplicity

		[140027]				-- 34380 -- order_proc.proc_code = 'REF32' -- REFERRAL TO GASTROENTEROLOGY -- Should be the same thing, but database update seems to be missing proc_code for many records. Scan through order_proc table for to look for other referral order proc_ids
			as referralProcIds,	-- Related REF32A (GI UHA), REF516 (Peds GI), REF132 (GI-External) skipping here, as restricting to internal adult referrals for now
								-- 34378 -- proc_code = 'REF31' -- REFERRAL TO ENDOCRINE CLINIC
								-- 34352 -- proc_code = 'REF18' -- REFERRAL TO HEMATOLOGY CLINIC -- Should be the same thing, but 2020 database update seems to be missing proc_code for many records
								-- 140027 -- proc_code = 'REF99' -- REFERRAL to ENT/OTOLARYNGOLOGY
		['8']
			as specialtyDepIds, 	-- '10' -- dep_map.specialty = 'Gastroenterology' 
									-- '7' -- dep_map.specialty like 'Endocrin%'
									-- '14' -- dep_map.specialty like 'Hematology'
									-- '8' -- dep_map.specialty like 'ENT%'
		
		['R09.81','J34.89','J32.4','J32.9'] as referralDiagnosisICD10, -- Nasal congestion, obstruction or Chronic Sinusitis

		['9','17','125','2527']
			as primaryCareDepIds, -- dep_map.specialty in 'Family Medicine','Internal Medicine','Primary Care','Express Care'

		12	as followupMonths, -- Number of months after a referral to look for a New Patient visit in the respective specialty

		[	'210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250',  -- Endocrinology Injections, biopsies, etc. that would not be expected to be done by generalist.
			'LABBBPRBC','11500201','PATH16','11500202','PATH9','LABBBPPLT','NUR14606A','NUR14606B','NUR744','210936589' -- Hematology Blood transfusion, FNA, etc. that would not be expected to be done by generalist
		]  	as specialtySpecificProcCodes, -- Procedure orders that would not be expected to be done by generalist. Likely needs to be expanded / customized as track more specialties.

		[	90538, 2364, 25122, 199672, 210386, 199615, 86468, 199672, 210913, 126553, 94690, 115097, 7785, 541179, 2243, 84544, 115097, 2364, 213399, -- Endocrinology specialty meds
			213662,209509,226945,112594,126580,540302,211084,540301,540304,221562,85848,112593,230620,230501,10467,200346,206390,213297,96471,126580,10236,540145,122481,85848,540763,236322,205661,213978,94592,210518,221636,10236,540145,122481,85848,540763,236322,205661,213978,94592,210518,221636,213980,13531,237602,237606,205208,232098,213297,7319,114723,242838,114723,210379,80845,199389,210527,9062,77372,7319,115220,115220,127401,231363,10537,228717,9063,110888,7319,23204,115378,236322,94592,202044,7319,206291,237603,95354,126404,114814,88720,28921,31915,10248,3708,211638,36089,31025,870,23210,381,117152,80504,237599,237601,29481,5510,126917,121514,8679,209037,19292,7319,221638,242528,77867,127400,201699,212878,127420,91568,13733,119134,10000,2331,2364,203466,28871,237600,96053,21102,212882,110889,4871,2364,10177,127420,209888,91375,28870,9605,209878,43483,95803,234674,89428,239975,80845,4454,112403,542067,31916,112597,242207,1965,2131,241649,15861,231412,10531 -- Hematology specialty meds
		]	as specialtySpecificMedicationIds, -- Similar medication prescription list used in specialty clinics that would not expect a referring primary care physician to order, even with decision support.

		['3']	as excludeMedOrderClass, -- 'Historical Med' class, doesn't represent a new prescription
		10 as minPatientsForNonRareItems -- If an item has not been ordered for more than this number of patients, assume it is too rare to use/recommend

),


-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------
-- Should not need to edit much of anything below this line. Standard queries with parameters that can be modified above
-- Could instead copy this entire set of queries as a prefix for subsequent encounterCohortDescription or encounterCohortItemAssociation queries
-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------


-- (1) Find all (outpatient) encounter referral orders for specialty
referringEncounterAny AS
(
	select op.anon_id, op.pat_enc_csn_id_coded as encounterId, 
      enc.appt_when_jittered as encounterDateTime, op.order_time_jittered as referralOrderDateTime
	from `shc_core_2022.order_proc` as op 
	  join `shc_core_2022.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded,
	  params
	where proc_id in UNNEST(params.referralProcIds)
	and ordering_mode = 'Outpatient'
	and EXTRACT(YEAR from order_time_jittered) = params.cohortYear 
),


-- Restrict to those where there was a relevant diagnosis code in the referring encounter
referringEncounter AS
(
	select 
		distinct
		referringEncounterAny.anon_id, 
		referringEncounterAny.encounterId,
		referringEncounterAny.encounterDateTime,
		referringEncounterAny.referralOrderDateTime
	from referringEncounterAny
	  join `shc_core_2022.diagnosis` as dx on referringEncounterAny.encounterId = dx.pat_enc_csn_id_jittered,
		params
	where
		dx.icd10 in UNNEST(params.referralDiagnosisICD10)
),

-- (1a) Find all (outpatient) encounters with referral orders for ANY specialty (use as reference baseline for relative risk estimates)
referringEncounterAnySpecialty AS
(
	select op.anon_id, op.pat_enc_csn_id_coded as encounterId, 
      enc.appt_when_jittered as encounterDateTime, op.order_time_jittered as referralOrderDateTime
	from `shc_core_2022.order_proc` as op 
	  join `shc_core_2022.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded,
	  params
	where order_type = 'Outpatient Referral' -- proc_code like 'REF%' 
	and ordering_mode = 'Outpatient'
	and EXTRACT(YEAR from order_time_jittered) = params.cohortYear 
),

-- (1b) Find clinic encounters from Primary Care specialities
primaryCareEncounter AS
(
	select enc.anon_id, enc.pat_enc_csn_id_coded as encounterId, 
		enc.appt_when_jittered as encounterDateTime, 
  	dep.specialty_dep_c, dep.specialty
	from `shc_core_2022.encounter` as enc 
	  	join `shc_core_2022.dep_map` as dep on enc.department_id = dep.department_id,
	  	params
	where dep.specialty_dep_c in UNNEST(params.primaryCareDepIds) 
	and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
	and appt_status = 'Completed'
	and extract(YEAR from enc.appt_time_jittered) = params.cohortYear
),

--(2) Find all (New Patient) clinic visits for the referred specialty
specialtyNewPatientEncounter AS
(
	select enc.anon_id, enc.pat_enc_csn_id_coded as encounterId, enc.appt_when_jittered as encounterDateTime
	from `shc_core_2022.encounter` as enc 
		join `shc_core_2022.dep_map` as dep on enc.department_id = dep.department_id,
		params
	where dep.specialty_dep_c in UNNEST(params.specialtyDepIds)
	and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
	-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
	and appt_status = 'Completed'
	and extract(YEAR from enc.appt_time_jittered) >= params.cohortYear	-- Use >= So capture follow-up visits as well
),

-- (2a) Find all NON-New Patient clinic visits for the referred specialty
specialtyNonNewPatientEncounter AS
(
	select enc.anon_id, enc.pat_enc_csn_id_coded as encounterId, enc.appt_when_jittered as encounterDateTime
	from `shc_core_2022.encounter` as enc 
		join `shc_core_2022.dep_map` as dep on enc.department_id = dep.department_id,
		params
	where dep.specialty_dep_c in UNNEST(params.specialtyDepIds)
	and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
	and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
	and appt_status = 'Completed'
	and extract(YEAR from enc.appt_time_jittered) >= params.cohortYear
),

-- (2b) Find all (New Patient) clinic visits for ANY specialty (use as reference baseline for relative risk estimates)

-- (3) Join to match referral orders to respective (first) patient visits within X months of referral
--- ??? No restriction on FIRST visit, as will catch any New Patient visit, even if patient has multiple with same specialty?
referralSpecialtyEncounterTime AS
(
	select 
		anon_id, 
		refEnc.encounterId as referringEncounterId, refEnc.encounterDateTime as referringDateTime,
		specEnc.encounterId as encounterId, specEnc.encounterDateTime as specialtyDateTime,
		referralOrderDateTime,
	 	DATETIME_DIFF(specEnc.encounterDateTime, refEnc.referralOrderDateTime, DAY) as referralDelayDays
	from referringEncounter as refEnc 
		join specialtyNewPatientEncounter as specEnc using (anon_id),
		params
	where DATETIME_DIFF(specEnc.encounterDateTime, refEnc.referralOrderDateTime, MONTH) BETWEEN 0 AND (params.followupMonths-1) -- Follow-up time
),
-- Assess distribution of referral time by summarizing results in Excel

-- Outer join to count how many with no follow-up visit at all
referralEncounterLostFollowup AS
(
	select anon_id, encounterId, encounterDateTime, referralOrderDateTime
	from referringEncounter as refEnc

	except distinct

	select anon_id, referringEncounterId as encounterId, referringDateTime as encounterDateTime, referralOrderDateTime
	from referralSpecialtyEncounterTime
),


--(7) New (specialty) specialty encounters that do NOT include a specialty only procedure (e.g., biopsy, injection)
specialtyNewPatientNonSpecializedEncounter AS
(
	select specEnc.anon_id, specEnc.encounterId, specEnc.encounterDateTime 
	from specialtyNewPatientEncounter as specEnc,
		params
	where extract(YEAR FROM encounterDateTime) = params.cohortYear 

	except distinct

	select specEnc.anon_id, specEnc.encounterId, specEnc.encounterDateTime 
	from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2022.order_proc` as op on specEnc.encounterId = op.pat_enc_csn_id_coded,
		  params
	where op.proc_code in UNNEST(params.specialtySpecificProcCodes) 

	except distinct 

	select specEnc.anon_id, specEnc.encounterId, specEnc.encounterDateTime
	from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2022.order_med` as om on specEnc.encounterId = om.pat_enc_csn_id_coded ,
		  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
	and om.medication_id in UNNEST(params.specialtySpecificMedicationIds) 
),

specialtyNewPatientNoMedsOrProcsEncounter AS
(
	select specEnc.anon_id, specEnc.encounterId, specEnc.encounterDateTime 
	from specialtyNewPatientEncounter as specEnc,
	 	params
	where extract(YEAR FROM encounterDateTime) = params.cohortYear

	except distinct

	select specEnc.anon_id, specEnc.encounterId, specEnc.encounterDateTime 
	from specialtyNewPatientEncounter as specEnc
	  join `shc_core_2022.order_proc` as op on specEnc.encounterId = op.pat_enc_csn_id_coded ,
	  params
	where op.proc_code in UNNEST(params.specialtySpecificProcCodes)

	except distinct 

	select specEnc.anon_id, specEnc.encounterId, specEnc.encounterDateTime
	from specialtyNewPatientEncounter as specEnc
	  join `shc_core_2022.order_med` as om on specEnc.encounterId = om.pat_enc_csn_id_coded ,
	  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
),


-- (8) Join to find New Patient specialty visits that did not include specialized treatment and are followed by another visit
-- Implies that the actions in the New Patient visit could have been done before hand and then 
--	the follow-up could have happened immediately, eliminating the need for the extra follow-up visit
specialtyNonSpecialEncounterFollowup AS
(
	select newEnc.*, min(followupEnc.encounterId) AS firstFollowupEncounterId, min(followupEnc.encounterDateTime) AS firstFollowupDateTime,
    	DATETIME_DIFF(min(followupEnc.encounterDateTime), newEnc.encounterDateTime, DAY) as daysUntilFollowup, 
    	DATETIME_DIFF(min(followupEnc.encounterDateTime), newEnc.encounterDateTime, MONTH) as monthsUntilFollowup
	from specialtyNewPatientNoMedsOrProcsEncounter as newEnc 
		join specialtyNonNewPatientEncounter as followupEnc using (anon_id),
		params
	where DATETIME_DIFF(followupEnc.encounterDateTime, newEnc.encounterDateTime, MONTH) BETWEEN 0 AND (params.followupMonths)
  	group by anon_id, encounterId, encounterDateTime
 ),


-- (8a) Look for any New Patient specialty visits (whether specialized treatment or not) that had a follow-up
specialtyEncounterFollowup AS
(
	select newEnc.*, min(followupEnc.encounterId) AS firstFollowupEncounterId, min(followupEnc.encounterDateTime) AS firstFollowupDateTime,
    	DATETIME_DIFF(min(followupEnc.encounterDateTime), newEnc.encounterDateTime, DAY) as daysUntilFollowup, 
    	DATETIME_DIFF(min(followupEnc.encounterDateTime), newEnc.encounterDateTime, MONTH) as monthsUntilFollowup
	from specialtyNewPatientEncounter as newEnc 
		join specialtyNonNewPatientEncounter as followupEnc using (anon_id),
		params
	where DATETIME_DIFF(followupEnc.encounterDateTime, newEnc.encounterDateTime, MONTH) BETWEEN 0 AND (params.followupMonths)
  	group by anon_id, encounterId, encounterDateTime
 ),

-- (8b) New Patient specialty visits that did not have a follow-up within X months
specialtyNewEncounterNoFollowup AS 
(
	select anon_id, encounterId, encounterDateTime
	from specialtyNewPatientEncounter as newEnc 

	except distinct

	select anon_id, encounterId, encounterDateTime
	from specialtyEncounterFollowup
),

-- spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

-- Example result query for individual encounter rows
-- Replace or uncomment below with specific cohort query to preview results of interest.
-- Once an encounter cohort of interest is defined, look to examples in encounterCohortDescription.sql to
--	describe the cohort (e.g., top diagnoses, medications, procedure orders, source department, etc.)
--  or encounterCohortItemAssociation.sql to compare items between cohorts

-- select * from referringEncounter
-- select * from referringEncounterAnySpecialty
-- select * from primaryCareEncounter
-- select * from specialtyNewPatientEncounter
-- select * from specialtyNonNewPatientEncounter
-- select * from referralSpecialtyEncounterTime
-- select * from referralEncounterLostFollowup
-- select * from specialtyNewPatientNonSpecializedEncounter
-- select * from specialtyNewPatientNoMedsOrProcsEncounter
-- select * from specialtyNonSpecialEncounterFollowup
-- select * from specialtyEncounterFollowup
-- select * from specialtyNewEncounterNoFollowup
-- limit 100	






cohortEncounter AS
(	-- Specific cohort of interest
	select
		distinct
		referringEncounter.anon_id, 
		referringEncounter.encounterId,
		referringEncounter.encounterDateTime
	from referringEncounter
),

referenceEncounter AS
(	-- This is a sample placeholder of all NEW PATIENT encounters in any clinic
	-- Replace this with a specific cohort of interest, which can be constructed through a separate series of common table expressions
	-- E.g., See specialtyReferralEncounterCohortDefinitions.sql, copy in those CTE queries above, then
	--	replace the below with something like "select anon_id, encounterId, encounterDateTime from referringEncounter"
	-- %%% REPLACE BELOW WITH COHORT DEFINITION OF INTEREST %%% --
	select 
		anon_id, 
		encounterId,
		encounterDateTime
	from primaryCareEncounter
),


-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------
-- Should not need to edit much of anything below this line. Standard queries with parameters and 
--   designation of a cohort of encounters of interest that can be modified above.
-- Can modify last result lines to extract reports of interest to describe the cohort
-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------

cohortEncounterDiagnosis AS
(
	select 
		dx.icd9, dx.icd10, dx_name, 
		count(*) as nDiagnosis, count(distinct cohortEnc.anon_id) as nPatient, count(distinct cohortEnc.encounterId) as nEncounter
	from cohortEncounter as cohortEnc 
	  join `shc_core_2022.diagnosis` as dx on cohortEnc.encounterId = dx.pat_enc_csn_id_jittered 
	group by dx.icd9, dx.icd10, dx_name
	order by count(*) desc
),

cohortEncounterSourceDepartment AS
(
	select 
		specialty_dep_c, specialty, department_id, dept_abbreviation, department_name, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from cohortEncounter as cohortEnc 
		join shc_core_2022.encounter as enc on (cohortEnc.encounterId = enc.pat_enc_csn_id_coded)
		join shc_core_2022.dep_map as dep using (department_id)
	group by
		specialty_dep_c, specialty, department_id, dept_abbreviation, department_name
	order by nEncounters desc
),

cohortEncounterMed AS
(
	select 
		medication_id, med_description,
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from cohortEncounter as cohortEnc
	  join `shc_core_2022.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
	  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
	group by medication_id, med_description
	order by count(*) desc
),

-- Number of distinct Med Orders per Encounter
cohortEncounterMedCount AS
(
	select avg(nDistinctOrderMed) as avgDistinctOrderMed, max(nDistinctOrderMed) as maxDistinctOrderMed
	from
	(
	  select cohortEnc.encounterId, count(distinct om.medication_id) as nDistinctOrderMed
	  from cohortEncounter as cohortEnc
	    join `shc_core_2022.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
	    params
	  where order_class_c not in UNNEST(params.excludeMedOrderClass)
	  group by cohortEnc.encounterId 
	)
),


-- Order Proc from encounters
cohortEncounterProc AS
(
	select 
		op.proc_code, description, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	  from cohortEncounter as cohortEnc
	  join `shc_core_2022.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
	group by proc_code, description
	order by count(*) desc
),

-- Number of distinct Med Orders per Encounter
cohortEncounterProcCount AS
(
	select avg(nDistinctOrderProcs) as avgDistinctOrderProcs, max(nDistinctOrderProcs) as maxDistinctOrderProcs
	from
	(
	  select cohortEnc.encounterId, count(distinct op.proc_code) as nDistinctOrderProcs
	  from cohortEncounter as cohortEnc
	    join `shc_core_2022.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
	  group by cohortEnc.encounterId 
	)
),


-- Medications from cohort encounter Visits that are (rarely) ordered in reference cohort encounter (e.g., Primary Care)
cohortSpecificMeds AS
(
	select 
		medication_id, med_description,
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from cohortEncounter as cohortEnc
	  join `shc_core_2022.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
	  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
	and medication_id not in
	(
		select medication_id
		from referenceEncounter as refEnc
		  join `shc_core_2022.order_med` as om on refEnc.encounterId = om.pat_enc_csn_id_coded ,
		  params
		where order_class_c not in UNNEST(params.excludeMedOrderClass)
		group by medication_id, params.minPatientsForNonRareItems
		having count(distinct refEnc.anon_id) >= params.minPatientsForNonRareItems
	)
	group by medication_id, med_description
	order by count(*) desc
),

-- Procedures in specialty care that are rarely encountered in primary care
cohortSpecificProc AS
(
	select 
		op.proc_code, description, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	  from cohortEncounter as cohortEnc
	  join `shc_core_2022.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded ,
	  params
	where proc_id not in
	(
		select proc_id
		from referenceEncounter as refEnc
		  join `shc_core_2022.order_proc` as op on refEnc.encounterId = op.pat_enc_csn_id_coded 
		group by proc_id, params.minPatientsForNonRareItems
		having count(distinct refEnc.anon_id) >= params.minPatientsForNonRareItems
	)
	group by proc_code, description
	order by count(*) desc
),

spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

-------------------------------------------------------------------------------------------------
-- Replace or uncomment below with specific items to query to generate results of interest
-------------------------------------------------------------------------------------------------

-- Reidentify cases with mappping table
-- Restrict to referral intervals > 0 days to avoid confusing cases
-- Some repeats are possible if multiple referral orders or New Patient specialty visits occurred
select 
	anon_id, mrn, 
	DATETIME_SUB(referralOrderDateTime, INTERVAL jitter DAY) as realReferralOrderDateTime,
	DATETIME_SUB(referringDateTime, INTERVAL jitter DAY) as realReferralVisitDateTime,
	DATETIME_SUB(specialtyDateTime, INTERVAL jitter DAY) as realSpecialtyVisitDateTime,
 	referralDelayDays
from 
	referralSpecialtyEncounterTime
	join som-nero-phi-jonc101-secure.starr_map.shc_map_2022 using (anon_id)
where referralDelayDays > 0
order by mrn

-- select * from cohortEncounterDiagnosis
-- select * from cohortEncounterSourceDepartment
-- select * from cohortEncounterMed
-- select * from cohortEncounterMedCount
-- select * from cohortEncounterProc
-- select * from cohortEncounterProcCount
-- select * from cohortSpecificMeds
-- select * from cohortSpecificProc

limit 1000


