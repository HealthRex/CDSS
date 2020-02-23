(1) Find all (outpatient) encounter referral orders for specialty (Endocrinology)
	WITH 
	referringEncounters2017 AS
	(
		select op.jc_uid, op.pat_enc_csn_id_coded as referringEncounterId, 
	      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
		from `starr_datalake2018.order_proc` as op 
		  join `starr_datalake2018.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
		where proc_code = 'REF31' -- REFERRAL TO ENDOCRINE CLINIC (internal)
		and ordering_mode = 'Outpatient'
		and EXTRACT(YEAR from order_time_jittered) = 2017
		-- 5675 Records
		-- Sometimes the Referral Order Time is days later than the appointment contact date / appt_when 
		--  (Maybe entered later in follow-up), but usually the same 4730 times
		--  and DATETIME_TRUNC(enc.appt_when_jittered, DAY) = DATETIME_TRUNC(op.order_time_jittered, DAY)
		-- Many of the referring encounters are Telephone, Orders Only, BMT infusions, etc. encounters
		--  Is okay, is still the time of referral order entry, but should use more input context from time before this encounter too
	)

	(1a) Find all (outpatient) encounters with referral orders for ANY specialty (use as reference baseline for relative risk estimates)


	(1b) Find clinic encounters from Primary Care specialities
	WITH
	primaryCareEncounters2017 AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as primaryEncounterId, enc.appt_when_jittered as primaryEncounterDateTime, 
      		dep.specialty_dep_c, dep.specialty
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c in ('9','17','125','2527') -- dep.specialty in 'Family Medicine','Internal Medicine','Primary Care','Express Care'
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) = 2017	-- >= So capture follow-up visits in 2018 as well
		-- 420,964 records in 2017
	)


(2) Find all (New Patient) clinic visits for the referred specialty
	WITH
	specialtyNewPatientEncounters2017_ AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
		and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
		-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017	-- >= So capture follow-up visits in 2018 as well
		-- 4796 records in 2017 (10650 for 2017 and after, largely including 2018)
	)

	(2a) Find all NON-New Patient clinic visits for the referred specialty
	WITH
	specialtyNonNewPatientEncounters2017_ AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
		and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017
    	-- 20,489 non-NEW PATIENT specialty encounter visits in 2017
    )

	(2b) Find all (New Patient) clinic visits for ANY specialty (use as reference baseline for relative risk estimates)

(3) Join to match referral orders to respective (first) patient visits within *6* months of referral

	select *, DATETIME_DIFF(specEnc.specialtyEncDateTime, refEnc.referringEncDateTime, MONTH)
	from referringEncounters as refEnc join specialtyNewPatientEncounters as specEnc using (jc_uid)
	where DATETIME_DIFF(specEnc.specialtyEncDateTime, refEnc.referringEncDateTime, MONTH) BETWEEN 0 AND 5
	-- 2636 referred New Patient visit within 6 months
	-- 2899 referred New Patient visit within 12 months

    - Outer join to count how many with no follow-up visit at all
    - Assess distribution of referral time
(4) Find all (sorted by prevalence)
    - Diagnoses from encounters in (1)
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referringEncounters as refEnc 
		  join `starr_datalake2018.diagnosis_code` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_coded 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
		-- 8240 Distinct diagnosis codes, but long tail dominated by head with 512 Osteoporosis, 487 Thyroid Nodule...
    
    - Order Med	from encounters in (2)
		select medication_id, med_description, count(*)
		from specialtyNewPatientEncounters as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description
		order by count(*) desc
		-- 761 Distinct medication_id descriptions, but can likely boil down many based on active ingredient

		select pharm_class_name, count(*)
		from specialtyNewPatientEncounters as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by pharm_class_name
		order by count(*) desc
		-- 143 Distinct pharm_class_name types prescribed in the specialty visits


		select avg(nDistinctOrderMed) as avgDistinctOrderMed, max(nDistinctOrderMed) as maxDistinctOrderMed
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct om.medication_id) as nDistinctOrderMed
		  from specialtyNewPatientEncounters as specEnc
		    join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		  where order_class <> 'Historical Med'
		  group by specEnc.specialtyEncounterId 
		)
		-- 2.0 average distinct order_meds per specialty new visit, max 13



		select medication_id, med_description, count(*)
		from primaryCareEncounters2017 as primEnc
		  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description
		having count(*) >= 10
		order by count(*) desc
		-- 6416 Distinct medication_id descriptions in primary care, but can likely boil down many based on active ingredient
		-- 2108 Distinct medication_id descriptions in primary care that were ordered at least 10 times in 2017

		select pharm_class_name, count(*)
		from primaryCareEncounters2017 as primEnc
		  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by pharm_class_name
		having count(*) >= 10
		order by count(*) desc
		-- 503 Distinct pharm_class_name types prescribed in the primary care visits
		-- 343 Distinct pharm_class_name types prescribed in the primary care visits that were ordered at least 10 times in 2017


    - Order Proc from encounters in (2)
		select op.proc_code, description, count(*)
		from specialtyNewPatientEncounters as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		group by proc_code, description
		order by count(*) desc
		-- 954 Distinct proc_code descriptions

		select avg(nDistinctOrderProcs) as avgDistinctOrderProcs, max(nDistinctOrderProcs) as maxDistinctOrderProcs
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct op.proc_code) as nDistinctOrderProcs
		  from specialtyNewPatientEncounters as specEnc
		    join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		  group by specEnc.specialtyEncounterId 
		)
		-- 5.3 average distinct order_procs per specialty new visit, max 38



(5) Filter (1) by only encouters including a diagnosis for XXX










(6) Medications from New Specialty Visits that are (rarely) ordered in Primary Care
		select medication_id, med_description
		from specialtyNewPatientEncounters2017 as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description

    	except distinct

		select medication_id, med_description
		from primaryCareEncounters2017 as primEnc
		  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description
		having count(*) >= 10
		-- 183 medications out of 761 medications ordered in New Specialty visits


(7) New (Endocrine) specialty encounters in 2017 that do NOT include a specialty only procedure (e.g., biopsy, injection)

specialtyNewPatientNonSpecializedEncounters2017 AS
(
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
		from specialtyNewPatientEncounters2017 as specEnc
 
    except distinct
    
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
		from specialtyNewPatientEncounters2017 as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where op.proc_code in 
    ('210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250') -- Injections, biopsies, etc. that would not be expected to be done by generalist
    -- 4,479 New Patient encounters in 2017 out of 4,796 New Patient encounters

    except distinct 

	select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
		from specialtyNewPatientEncounters2017 as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
    and om.medication_id in (90538, 2364, 25122, 199672, 210386, 199615, 86468, 199672, 210913, 126553, 94690, 115097, 7785, 541179, 2243, 84544, 115097, 2364, 213399)
    -- 4,389 New Patient specialty encounters in 2017 that don't include an order for an (injectable) med or procedure that can likely only occur in specialty clinic
),

specialtyNewPatientNoMedsOrProcsEncounters2017 AS
(
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
		from specialtyNewPatientEncounters2017 as specEnc
 
    except distinct
    
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
		from specialtyNewPatientEncounters2017 as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where op.proc_code in 
    ('210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250') -- Injections, biopsies, etc. that would not be expected to be done by generalist
    -- 4,479 New Patient encounters in 2017 out of 4,796 New Patient encounters

    except distinct 

	select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
		from specialtyNewPatientEncounters2017 as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
    -- 2,874 New Patient specialty encounters in 2017 that only include non-specialized procedure orders (mostly labs, imaging, referrals). Not even any oral med / treatment prescriptions
)


(8) Join to find New Patient specialty visits that did not include specialized treatment and are followed by another visit
  	-- Implies that the actions in the New Patient visit could have been done before hand and then 
  	--	the follow-up could have happened immediately, eliminating the need for the extra follow-up visit

	select newEnc.*, min(nonNewSpecialtyEncounterId), min(nonNewSpecialtyEncounterDateTime),
    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY), 
    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH)
	from specialtyNewPatientNoMedsOrProcsEncounters2017 as newEnc join specialtyNonNewPatientEncounters2017_ as followupEnc using (jc_uid)
	where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND 11
  	group by jc_uid, specialtyEncounterId, specialtyEncounterDateTime
  	-- 1,167 New Patient to follow-up specialty encounters within 6 months
  	-- 1,451 New Patient to follow-up specialty encounters within 12 months
  	-- Means >1,000 didn't follow-up in specialty clinic at all within 12 months, 
  	--	implying many of those New Patient visits weren't even necessary
  	-- Follow-up: Average 96 days, StdDev 85 days
