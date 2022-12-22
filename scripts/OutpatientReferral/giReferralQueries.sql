-- Define patient encounter cohorts using common table expressions (CTEs) based on referrals and arrivals at a particular specialty
-- Use the params options at the head to define different filters for different specialties.

WITH 
-- Set modifiable query parameters in one place here, so can abstract the subsequent queries structures below
-- Replace values to those of different cohorts of interest
-- https://stackoverflow.com/questions/29759628/setting-big-query-variables-like-mysql
-- https://medium.com/google-cloud/how-to-work-with-array-and-structs-in-bigquery-9c0a2ea584a6
params AS 
(
	select 
		2020
			as cohortYear,			-- Restrict to one year for simplicity

		[34380]					-- order_proc.proc_code = 'REF32' -- REFERRAL TO GASTROENTEROLOGY -- Should be the same thing, but database update seems to be missing proc_code for many records. Scan through order_proc table for to look for other referral order proc_ids
			as referralProcIds,	-- Related REF32A (GI UHA), REF516 (Peds GI), REF132 (GI-External) skipping here, as restricting to internal adult referrals for now
								-- 34378 -- proc_code = 'REF31' -- REFERRAL TO ENDOCRINE CLINIC
								-- 34352 -- proc_code = 'REF18' -- REFERRAL TO HEMATOLOGY CLINIC -- Should be the same thing, but 2020 database update seems to be missing proc_code for many records
		['10']
			as specialtyDepIds, 	-- dep_map.specialty = 'Gastroenterology' 
									-- '7' -- dep.specialty like 'Endocrin%'
									-- '14' -- dep.specialty like 'Hematology'

		['9','17','125','2527']
			as primaryCareDepIds, -- dep_map.specialty in 'Family Medicine','Internal Medicine','Primary Care','Express Care'

		12	as followupMonths, -- Number of months after a referral to look for a New Patient visit in the respective specialty

		[	'210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250',  -- Endocrinology Injections, biopsies, etc. that would not be expected to be done by generalist.
			'LABBBPRBC','11500201','PATH16','11500202','PATH9','LABBBPPLT','NUR14606A','NUR14606B','NUR744','210936589' -- Hematology Blood transfusion, FNA, etc. that would not be expected to be done by generalist
		]  	as specialtySpecificProcCodes, -- Procedure orders that would not be expected to be done by generalist. Likely needs to be expanded / customized as track more specialties.

		[	90538, 2364, 25122, 199672, 210386, 199615, 86468, 199672, 210913, 126553, 94690, 115097, 7785, 541179, 2243, 84544, 115097, 2364, 213399, -- Endocrinology specialty meds
			213662,209509,226945,112594,126580,540302,211084,540301,540304,221562,85848,112593,230620,230501,10467,200346,206390,213297,96471,126580,10236,540145,122481,85848,540763,236322,205661,213978,94592,210518,221636,10236,540145,122481,85848,540763,236322,205661,213978,94592,210518,221636,213980,13531,237602,237606,205208,232098,213297,7319,114723,242838,114723,210379,80845,199389,210527,9062,77372,7319,115220,115220,127401,231363,10537,228717,9063,110888,7319,23204,115378,236322,94592,202044,7319,206291,237603,95354,126404,114814,88720,28921,31915,10248,3708,211638,36089,31025,870,23210,381,117152,80504,237599,237601,29481,5510,126917,121514,8679,209037,19292,7319,221638,242528,77867,127400,201699,212878,127420,91568,13733,119134,10000,2331,2364,203466,28871,237600,96053,21102,212882,110889,4871,2364,10177,127420,209888,91375,28870,9605,209878,43483,95803,234674,89428,239975,80845,4454,112403,542067,31916,112597,242207,1965,2131,241649,15861,231412,10531 -- Hematology specialty meds
		]	as specialtySpecificMedicationIds, -- Similar medication prescription list used in specialty clinics that would not expect a referring primary care physician to order, even with decision support.

		[3]	as excludeMedOrderClass -- 'Historical Med' class, doesn't represent a new prescription

),

-- (1) Find all (outpatient) encounter referral orders for specialty
referringEncounter AS
(
	select op.anon_id, op.pat_enc_csn_id_coded as referringEncounterId, 
      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
	from `shc_core_2021.order_proc` as op 
	  join `shc_core_2021.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded,
	  params
	where proc_id in UNNEST(params.referralProcIds)
	and ordering_mode = 'Outpatient'
	and EXTRACT(YEAR from order_time_jittered) = params.cohortYear 
),

-- (1a) Find all (outpatient) encounters with referral orders for ANY specialty (use as reference baseline for relative risk estimates)
referringEncounterAnySpecialty AS
(
	select op.anon_id, op.pat_enc_csn_id_coded as referringEncounterId, 
      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
	from `shc_core_2021.order_proc` as op 
	  join `shc_core_2021.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded,
	  params
	where order_type = 'Outpatient Referral' -- proc_code like 'REF%' 
	and ordering_mode = 'Outpatient'
	and EXTRACT(YEAR from order_time_jittered) = params.cohortYear 
),

-- (1b) Find clinic encounters from Primary Care specialities
primaryCareEncounter AS
(
	select enc.anon_id, enc.pat_enc_csn_id_coded as primaryEncounterId, enc.appt_when_jittered as primaryEncounterDateTime, 
  		dep.specialty_dep_c, dep.specialty
	from `shc_core_2021.encounter` as enc 
	  	join `shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id,
	  	params
	where dep.specialty_dep_c in UNNEST(params.primaryCareDepIds) 
	and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
	and appt_status = 'Completed'
	and extract(YEAR from enc.appt_time_jittered) = params.cohortYear
),

--(2) Find all (New Patient) clinic visits for the referred specialty
specialtyNewPatientEncounter AS
(
	select enc.anon_id, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
	from `shc_core_2021.encounter` as enc 
		join `shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id,
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
	select enc.anon_id, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
	from `shc_core_2021.encounter` as enc 
		join `shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id,
		params
	where dep.specialty_dep_c in UNNEST(params.specialtyDepIds)
	and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
	and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
	and appt_status = 'Completed'
	and extract(YEAR from enc.appt_time_jittered) >= params.cohortYear
),

-- (2b) Find all (New Patient) clinic visits for ANY specialty (use as reference baseline for relative risk estimates)

-- (3) Join to match referral orders to respective (first) patient visits within X months of referral
referralSpecialtyEncounterTime AS
(
	select *, DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, DAY) as referralDelayDays
	from referringEncounter as refEnc 
		join specialtyNewPatientEncounter as specEnc using (anon_id),
		params
	where DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, MONTH) BETWEEN 0 AND (params.followupMonths-1) -- Follow-up time
),
-- Assess distribution of referral time by summarizing results in Excel

-- Outer join to count how many with no follow-up visit at all
referralEncounterLostFollowup AS
(
	select anon_id, referringEncounterId, referringApptDateTime, referralOrderDateTime
	from referringEncounter as refEnc

	except distinct

	select anon_id, referringEncounterId, referringApptDateTime, referralOrderDateTime
	from referralSpecialtyEncounterTime
),


--(7) New (specialty) specialty encounters that do NOT include a specialty only procedure (e.g., biopsy, injection)
specialtyNewPatientNonSpecializedEncounter AS
(
	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc,
		params
	where extract(YEAR FROM specialtyEncounterDateTime) = params.cohortYear 

	except distinct

	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded,
		  params
	where op.proc_code in UNNEST(params.specialtySpecificProcCodes) 

	except distinct 

	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
	from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded ,
		  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
	and om.medication_id in UNNEST(params.specialtySpecificMedicationIds) 
),

specialtyNewPatientNoMedsOrProcsEncounter AS
(
	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc,
	 	params
	where extract(YEAR FROM specialtyEncounterDateTime) = params.cohortYear

	except distinct

	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc
	  join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded ,
	  params
	where op.proc_code in UNNEST(params.specialtySpecificProcCodes)

	except distinct 

	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
	from specialtyNewPatientEncounter as specEnc
	  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded ,
	  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
),


-- (8) Join to find New Patient specialty visits that did not include specialized treatment and are followed by another visit
-- Implies that the actions in the New Patient visit could have been done before hand and then 
--	the follow-up could have happened immediately, eliminating the need for the extra follow-up visit
specialtyNonSpecialEncounterFollowup AS
(
	select newEnc.*, min(nonNewSpecialtyEncounterId) AS firstFollowupEncounterId, min(nonNewSpecialtyEncounterDateTime) AS firstFollowupDateTime,
    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY) as daysUntilFollowup, 
    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH) as monthsUntilFollowup
	from specialtyNewPatientNoMedsOrProcsEncounter as newEnc 
		join specialtyNonNewPatientEncounter as followupEnc using (anon_id),
		params
	where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND (params.followupMonths)
  	group by anon_id, specialtyEncounterId, specialtyEncounterDateTime
 ),


-- (8a) Look for any New Patient specialty visits (whether specialized treatment or not) that had a follow-up
specialtyEncounterFollowup AS
(
	select newEnc.*, min(nonNewSpecialtyEncounterId) AS firstFollowupEncounterId, min(nonNewSpecialtyEncounterDateTime) AS firstFollowupDateTime,
    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY) as daysUntilFollowup, 
    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH) as monthsUntilFollowup
	from specialtyNewPatientEncounter as newEnc 
		join specialtyNonNewPatientEncounter as followupEnc using (anon_id),
		params
	where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND (params.followupMonths)
  	group by anon_id, specialtyEncounterId, specialtyEncounterDateTime
 ),

-- (8b) New Patient specialty visits that did not have a follow-up within X months
specialtyNewEncounterNoFollowup AS 
(
	select anon_id, specialtyEncounterId, specialtyEncounterDateTime
	from specialtyNewPatientEncounter as newEnc 

	except distinct

	select anon_id, specialtyEncounterId, specialtyEncounterDateTime
	from specialtyEncounterFollowup
),

spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

-- Example result query for individual encounter rows
-- Once an encounter cohort of interest is defined, look to examples in encounterCohortDescription.sql to
--	describe the cohort (e.g., top diagnoses, medications, procedure orders, source department, etc.)
select *
from specialtyNewPatientEncounter
limit 100	