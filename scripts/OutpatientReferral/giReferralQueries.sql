-- (1) Find all (outpatient) encounter referral orders for specialty (Gastroenterology)
	WITH 

	referringEncounter AS
	(
		select op.anon_id, op.pat_enc_csn_id_coded as referringEncounterId, 
	      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
		from `shc_core_2021.order_proc` as op 
		  join `shc_core_2021.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
		where proc_id = 34380 -- %%% proc_code = 'REF32' -- REFERRAL TO GASTROENTEROLOGY -- Should be the same thing, but database update seems to be missing proc_code for many records
		and ordering_mode = 'Outpatient'
		and EXTRACT(YEAR from order_time_jittered) = 2020 -- %%% Restrict to one year for simplicity (thoughy maybe anomalous Covid year)
		-- Related REF32A (GI UHA), REF516 (Peds GI), REF132 (GI-External) skipping here, as restricting to internal adult referrals for now
	),

	-- (1a) Find all (outpatient) encounters with referral orders for ANY specialty (use as reference baseline for relative risk estimates)

	-- (1b) Find clinic encounters from Primary Care specialities
	
	primaryCareEncounter AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as primaryEncounterId, enc.appt_when_jittered as primaryEncounterDateTime, 
      		dep.specialty_dep_c, dep.specialty
		from `shc_core_2021.encounter` as enc join `shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c in ('9','17','125','2527') -- dep.specialty in 'Family Medicine','Internal Medicine','Primary Care','Express Care'
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) = 2020	-- %%% Restrict to one year for now
	),

--(2) Find all (New Patient) clinic visits for the referred specialty

	specialtyNewPatientEncounter AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
		from `shc_core_2021.encounter` as enc join `shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '10' -- dep.specialty = 'Gastroenterology' %%% Specific specialty eval for now
		and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
		-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2020	-- %%% Restrict start year, but use >= So capture follow-up visits as well
	),

	-- (2a) Find all NON-New Patient clinic visits for the referred specialty
	specialtyNonNewPatientEncounter AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
		from `shc_core_2021.encounter` as enc join `shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '10' -- dep.specialty = 'Gastroenterology' %%% Specific specialty eval for now
		and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2020 -- %% Restrict start year
    ),

	-- (2b) Find all (New Patient) clinic visits for ANY specialty (use as reference baseline for relative risk estimates)

-- (3) Join to match referral orders to respective (first) patient visits within X months of referral

	referralSpecialtyEncounterTime AS
	(
		select *, DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, DAY) as referralDelayDays
		from referringEncounter as refEnc join specialtyNewPatientEncounter as specEnc using (anon_id)
		where DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, MONTH) BETWEEN 0 AND 11 -- %%% Follow-up time
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


--(4) Find all (sorted by prevalence)
    -- Diagnoses from encounters in (1)
    referralDiagnosis AS
    (
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referringEncounter as refEnc 
		  join `shc_core_2021.diagnosis` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_jittered 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
	),
    
    -- Order Med from encounters in (2)
    specialtyNewEncounterMeds AS
    (
		select medication_id, med_description, count(*)
		from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		group by medication_id, med_description
		order by count(*) desc
	),
	specialtyNewEncounterMedClass AS
	(
		select pharm_class_name, count(*)
		from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		group by pharm_class_name
		order by count(*) desc
	),


	-- Med Order counts per New Specialty Encounter
	specialtyNewPatientMedCount AS
	(
		select avg(nDistinctOrderMed) as avgDistinctOrderMed, max(nDistinctOrderMed) as maxDistinctOrderMed
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct om.medication_id) as nDistinctOrderMed
		  from specialtyNewPatientEncounter as specEnc
		    join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		  where order_class_c <> 3 -- 'Historical Med'
		  group by specEnc.specialtyEncounterId 
		)
	),


    -- Order Proc from encounters in (2)
    specialtyNewPatientProc AS
    (
		select op.proc_code, description, count(*)
		from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		group by proc_code, description
		order by count(*) desc
	),
	specialtyNewPatientProcCount AS
	(
		select avg(nDistinctOrderProcs) as avgDistinctOrderProcs, max(nDistinctOrderProcs) as maxDistinctOrderProcs
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct op.proc_code) as nDistinctOrderProcs
		  from specialtyNewPatientEncounter as specEnc
		    join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		  group by specEnc.specialtyEncounterId 
		)
	),


-- (5) Filter (1) by only encounters including a diagnosis for XXX

-- (6) Medications from New Specialty Visits that are (rarely) ordered in Primary Care
	specialtySpecificMeds AS
	(
		select medication_id, med_description, count(*)
		from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		and medication_id not in
		(
			select medication_id
			from primaryCareEncounter as primEnc
			  join `shc_core_2021.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
			where order_class_c <> 3 -- 'Historical Med'
			group by medication_id
			having count(*) >= 10
		)
		group by medication_id, med_description
        order by count(*) desc
		-- 313 medications out of 761 medications ordered in New Specialty visits are rarely ordered in primary care
		-- Freestyle Libre Sensor, Freestyle Libre Reader, Zoledronic Acid IV, Thyrotropin IM, ..
	),

-- Procedures in specialty care that are rarely encountered in primary care
	specialtySpecificProc AS
	(
		select proc_id, proc_code, description, count(*)
		from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where proc_id not in
		(
			select proc_id
			from primaryCareEncounter as primEnc
			  join `shc_core_2021.order_proc` as op on primEnc.primaryEncounterId = op.pat_enc_csn_id_coded 
			group by proc_id
			having count(*) >= 10
		)
		group by proc_id, proc_code, description
        order by count(*) desc
		-- 368 procedures ordered in specialty rarely done in primary care
		-- Endo Echo Head and Neck, FNA, Chromogranin A, NM Thyroid Whole Body, ...
	),


--(7) New (specialty) specialty encounters that do NOT include a specialty only procedure (e.g., biopsy, injection)

specialtyNewPatientNonSpecializedEncounter AS
(
    select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc
	where extract(YEAR FROM specialtyEncounterDateTime) = 2020 -- %%% Restrict to specific year
 
    except distinct
    
    select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
	where op.proc_code in -- %%% List needs further customization for each specialty
    ('210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250') -- Injections, biopsies, etc. that would not be expected to be done by generalist

    except distinct 

	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
	from specialtyNewPatientEncounter as specEnc
		  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
	where order_class_c <> 3 -- 'Historical Med' 
	and om.medication_id in -- %% List needs customization for each specialty
	(90538, 2364, 25122, 199672, 210386, 199615, 86468, 199672, 210913, 126553, 94690, 115097, 7785, 541179, 2243, 84544, 115097, 2364, 213399)
),

specialtyNewPatientNoMedsOrProcsEncounter AS
(
    select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc
  	where extract(YEAR FROM specialtyEncounterDateTime) = 2020 -- %%% Restrict to specific year

    except distinct
    
    select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from specialtyNewPatientEncounter as specEnc
	  join `shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
	where op.proc_code in -- %% Custom exclusion list per specialty
    ('210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250') -- Injections, biopsies, etc. that would not be expected to be done by generalist

    except distinct 

	select specEnc.anon_id, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
	from specialtyNewPatientEncounter as specEnc
	  join `shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
	where order_class_c <> 3 -- 'Historical Med'
),



-- (8) Join to find New Patient specialty visits that did not include specialized treatment and are followed by another visit
  	-- Implies that the actions in the New Patient visit could have been done before hand and then 
  	--	the follow-up could have happened immediately, eliminating the need for the extra follow-up visit
  	specialtyNonSpecialEncounterFollowup AS
  	(
		select newEnc.*, min(nonNewSpecialtyEncounterId) AS firstFollowupEncounterId, min(nonNewSpecialtyEncounterDateTime) AS firstFollowupDateTime,
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY) as daysUntilFollowup, 
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH) as monthsUntilFollowup
		from specialtyNewPatientNoMedsOrProcsEncounter as newEnc join specialtyNonNewPatientEncounter as followupEnc using (anon_id)
		where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND 11 -- %%% Follow-up time
	  	group by anon_id, specialtyEncounterId, specialtyEncounterDateTime
	 ),


  	-- (8a) Look for any New Patient specialty visits (whether specialized treatment or not) that had a follow-up
  	specialtyEncounterFollowup AS
  	(
		select newEnc.*, min(nonNewSpecialtyEncounterId) AS firstFollowupEncounterId, min(nonNewSpecialtyEncounterDateTime) AS firstFollowupDateTime,
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY) as daysUntilFollowup, 
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH) as monthsUntilFollowup
		from specialtyNewPatientEncounter as newEnc join specialtyNonNewPatientEncounter as followupEnc using (anon_id)
		where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND 11 -- %%% Follow-up time
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


-- Top Dx, Departments for different cohorts

    referralDiagnosisX AS
    (
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referringEncounter as refEnc 
		  join `shc_core_2021.diagnosis` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_jittered 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
	),
    referralLostFollowupDiagnosis AS
    (
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referralEncounterLostFollowup as refEnc 
		  join `shc_core_2021.diagnosis` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_jittered 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
	),





	spacer AS (select * from primaryCareEncounter)
	

select *
from referralLostFollowupDiagnosis
limit 100	