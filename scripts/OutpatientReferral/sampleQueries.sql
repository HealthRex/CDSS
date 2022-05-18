-- (1) Find all (outpatient) encounter referral orders for specialty (Endocrinology)
	WITH 

	referringEncountersEndocrine2017 AS
	(
		select op.jc_uid, op.pat_enc_csn_id_coded as referringEncounterId, 
	      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
		from `starr_datalake2018.order_proc` as op 
		  join `starr_datalake2018.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
		where proc_id = 34378 -- proc_code = 'REF31' -- REFERRAL TO ENDOCRINE CLINIC -- Should be the same thing, but 2020 database update seems to be missing proc_code for many records
		and ordering_mode = 'Outpatient'
		and EXTRACT(YEAR from order_time_jittered) = 2017
		-- 5675 Records - Endocrine
		-- Sometimes the Referral Order Time is days later than the appointment contact date / appt_when 
		--  (Maybe entered later in follow-up), but usually the same 4730 times
		--  and DATETIME_TRUNC(enc.appt_when_jittered, DAY) = DATETIME_TRUNC(op.order_time_jittered, DAY)
		-- Many of the referring encounters are Telephone, Orders Only, BMT infusions, etc. encounters
		--  Is okay, is still the time of referral order entry, but should use more input context from time before this encounter too
	),
	referringEncountersHematology2017 AS
	(
		select op.jc_uid, op.pat_enc_csn_id_coded as referringEncounterId, 
	      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
		from `starr_datalake2018.order_proc` as op 
		  join `starr_datalake2018.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
		where proc_id = 34352 -- proc_code = 'REF18' -- REFERRAL TO HEMATOLOGY CLINIC -- Should be the same thing, but 2020 database update seems to be missing proc_code for many records
		and ordering_mode = 'Outpatient'
		and EXTRACT(YEAR from order_time_jittered) = 2017
		-- 2406 Records - Hematology
	),



	-- (1a) Find all (outpatient) encounters with referral orders for ANY specialty (use as reference baseline for relative risk estimates)


	-- (1b) Find clinic encounters from Primary Care specialities
	
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
	),


--(2) Find all (New Patient) clinic visits for the referred specialty

	endocrineNewPatientEncounters2017_ AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
		and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
		-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017	-- >= So capture follow-up visits in 2018 as well
		-- 4796 records in 2017 (10650 for 2017 and after, largely including 2018)
	),
	hematologyNewPatientEncounters2017_ AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '14' -- dep.specialty like 'Hematology'
		and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
		-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017	-- >= So capture follow-up visits in 2018 as well
		-- 2895 records in 2017 (5,644 for 2017 and after)
	),


	-- (2a) Find all NON-New Patient clinic visits for the referred specialty
	endocrineNonNewPatientEncounters2017_ AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
		and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017
    	-- 20,489 non-NEW PATIENT specialty encounter visits in 2017
    ),
    hematologyNonNewPatientEncounters2017_ AS
	(
		select enc.jc_uid, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
		from `starr_datalake2018.encounter` as enc join `starr_datalake2018.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '14' -- dep.specialty like 'Hematol%'
		and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017
    	-- 23,203 non-NEW PATIENT specialty encounter visits in 2017
    ),


	-- (2b) Find all (New Patient) clinic visits for ANY specialty (use as reference baseline for relative risk estimates)

-- (3) Join to match referral orders to respective (first) patient visits within *6* months of referral

	endocrineReferralTimes2017 AS
	(
		select *, DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, DAY) as referralDelayDays
		from referringEncountersEndocrine2017 as refEnc join endocrineNewPatientEncounters2017_ as specEnc using (jc_uid)
		where DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, MONTH) BETWEEN 0 AND 11
		-- 2,640 referred New Patient visit within 6 months
		-- 2,898 referred New Patient visit within 12 months
			-- 67 days average, 66 days stdev, 44 days median (IQR 26-83)
	),
	hematologyReferralTimes2017 AS
	(
		select *, DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, DAY) as referralDelayDays
		from referringEncountersHematology2017 as refEnc join hematologyNewPatientEncounters2017_ as specEnc using (jc_uid)
		where DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, MONTH) BETWEEN 0 AND 11
		-- 1,204 referred New Patient visit within 6 months
		-- 1,238 referred New Patient visit within 12 months
			-- 42 days average, 45 days stdev, 34 days median (IQR 19-48)
	),

    -- Outer join to count how many with no follow-up visit at all
    -- Assess distribution of referral time by summarizing results in Excel


--(4) Find all (sorted by prevalence)
    -- Diagnoses from encounters in (1)
    endocrineReferralDiagnoses AS
    (
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referringEncountersEndocrine2017 as refEnc 
		  join `starr_datalake2018.diagnosis_code` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_coded 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
		-- 8,240 Distinct diagnosis codes, but long tail dominated by 512 Osteoporosis, 487 Thyroid Nodule, 424 Hypothyroid...
	),
    hematologyReferralDiagnoses AS
    (
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referringEncountersHematology2017 as refEnc 
		  join `starr_datalake2018.diagnosis_code` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_coded 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
		-- 5,257 Distinct diagnosis codes, but long tail dominated by 169 Anemia, 104 Thrombocytopenia, 92 Anemia, 90 Iron Def Anemia, 72 Leukocytosis...
	),
    
    -- Order Med from encounters in (2)
    endocrineNewEncounterMeds AS
    (
		select medication_id, med_description, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description
		order by count(*) desc
		-- 761 Distinct medication_id descriptions, but can likely boil down many based on active ingredient
		-- 242 OneTouch Verio Strip, 217 OneTouch Lancet, 185 Metformin, 164 Dexamethasone, 150 Alendronate
	),
	endocrineNewEncounterMedClass AS
	(
		select pharm_class_name, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by pharm_class_name
		order by count(*) desc
		-- 143 Distinct pharm_class_name types prescribed in the specialty visits
		-- 817 Insulins, 803 Thyroid Hormones, 660 Blood Sugar Diagnostics, 475 Diabetic Supplies, 462 Biguanide Anti-Diabetic, 398 Bone Resorption Inhibitors...
	),

    hematologyNewEncounterMeds AS
    (
		select medication_id, med_description, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description
		order by count(*) desc
		-- 304 Distinct medication_id descriptions
		-- 463 Ondansetron IV, 462 NS IV Bolus, 460 Diphenhydramine IV, 459 Methylprednisolone IV, 459 Epinephrine IV, 118 Acetaminophen, 112 Iron IV, ... 
		-- Looks like mostly chemotherapy pre-meds
	),
	hematologyNewEncounterMedClass AS
	(
		select pharm_class_name, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by pharm_class_name
		order by count(*) desc
		-- 112 Distinct pharm_class_name types prescribed in the specialty visits
		-- 593 Anti-Emetic, 521 Glucocorticoids, 484 Antihistamines, 459 Adrenergic Agent, 245 Saline Preparation, 206 Iron Replacement, ...
	),

	primaryCareMeds AS
	(
		select medication_id, med_description, count(*)
		from primaryCareEncounters2017 as primEnc
		  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by medication_id, med_description
		having count(*) >= 10
		order by count(*) desc
		-- 6416 Distinct medication_id descriptions in primary care, but can likely boil down many based on active ingredient
		-- 2108 Distinct medication_id descriptions in primary care that were ordered at least 10 times in 2017
	),
	primaryCareMedClass AS
	(
		select pharm_class_name, count(*)
		from primaryCareEncounters2017 as primEnc
		  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		group by pharm_class_name
		having count(*) >= 10
		order by count(*) desc
		-- 503 Distinct pharm_class_name types prescribed in the primary care visits
		-- 343 Distinct pharm_class_name types prescribed in the primary care visits that were ordered at least 10 times in 2017
	),



	-- Med Order counts per New Specialty Encounter
	endocrineNewPatientMedCount AS
	(
		select avg(nDistinctOrderMed) as avgDistinctOrderMed, max(nDistinctOrderMed) as maxDistinctOrderMed
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct om.medication_id) as nDistinctOrderMed
		  from endocrineNewPatientEncounters2017_ as specEnc
		    join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		  where order_class <> 'Historical Med'
		  group by specEnc.specialtyEncounterId 
		)
		-- 2.0 average distinct order_meds per specialty new visit, max 13
	),
	hematologyNewPatientMedCount AS
	(
		select avg(nDistinctOrderMed) as avgDistinctOrderMed, max(nDistinctOrderMed) as maxDistinctOrderMed
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct om.medication_id) as nDistinctOrderMed
		  from hematologyNewPatientEncounters2017_ as specEnc
		    join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		  where order_class <> 'Historical Med'
		  group by specEnc.specialtyEncounterId 
		)
		-- 3.1 average distinct order_meds per specialty new visit, max 43
	),


    -- Order Proc from encounters in (2)
    endocrineNewPatientProc AS
    (
		select op.proc_code, description, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		group by proc_code, description
		order by count(*) desc
		-- 954 Distinct proc_code descriptions
		-- 6,018 TSH, 4,655 T4, 2,841 25-OH VitD, ...
	),
	endocrineNewPatientProcCount AS
	(
		select avg(nDistinctOrderProcs) as avgDistinctOrderProcs, max(nDistinctOrderProcs) as maxDistinctOrderProcs
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct op.proc_code) as nDistinctOrderProcs
		  from endocrineNewPatientEncounters2017_ as specEnc
		    join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		  group by specEnc.specialtyEncounterId 
		)
		-- 5.3 average distinct order_procs per specialty new visit, max 38
	),

    hematologyNewPatientProc AS
    (
		select op.proc_code, description, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		group by proc_code, description
		order by count(*) desc
		-- 675 Distinct proc_code descriptions
		-- CMP, CBC w/ Diff, Ferritin, Retic Count, Type and Screen, Donor HTLV Ab, Transferrin Sat, ...
	),
	hematologyNewPatientProcCount AS
	(
		select avg(nDistinctOrderProcs) as avgDistinctOrderProcs, max(nDistinctOrderProcs) as maxDistinctOrderProcs
		from
		(
		  select specEnc.specialtyEncounterId, count(distinct op.proc_code) as nDistinctOrderProcs
		  from hematologyNewPatientEncounters2017_ as specEnc
		    join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		  group by specEnc.specialtyEncounterId 
		)
		-- 6.9 average distinct order_procs per specialty new visit, max 33
	),


-- (5) Filter (1) by only encouters including a diagnosis for XXX

-- (6) Medications from New Specialty Visits that are (rarely) ordered in Primary Care
	endocrineSpecificMeds AS
	(
		select medication_id, med_description, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		and medication_id not in
		(
			select medication_id
			from primaryCareEncounters2017 as primEnc
			  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
			where order_class <> 'Historical Med'
			group by medication_id
			having count(*) >= 10
		)
		group by medication_id, med_description
        order by count(*) desc
		-- 313 medications out of 761 medications ordered in New Specialty visits are rarely ordered in primary care
		-- Freestyle Libre Sensor, Freestyle Libre Reader, Zoledronic Acid IV, Thyrotropin IM, ..
	),
	hematologySpecificMeds AS
	(
		select medication_id, med_description, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
		and medication_id not in
		(
			select medication_id
			from primaryCareEncounters2017 as primEnc
			  join `starr_datalake2018.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
			where order_class <> 'Historical Med'
			group by medication_id
			having count(*) >= 10
		)
		group by medication_id, med_description
        order by count(*) desc
        -- 145 medications rarely ordered in primary care
        -- Epinephrine, Methylprednisolone IV, Iron IV, Filgrastim, Heparin IV, Mag oxide, KCL, ...
	),


-- Procedures in specialty care that are rarely encountered in primary care
	endocrineSpecificProc AS
	(
		select proc_id, proc_code, description, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where proc_id not in
		(
			select proc_id
			from primaryCareEncounters2017 as primEnc
			  join `starr_datalake2018.order_proc` as op on primEnc.primaryEncounterId = op.pat_enc_csn_id_coded 
			group by proc_id
			having count(*) >= 10
		)
		group by proc_id, proc_code, description
        order by count(*) desc
		-- 368 procedures ordered in endocrine rarely done in primary care
		-- Endo Echo Head and Neck, FNA, Chromogranin A, NM Thyroid Whole Body, ...
	),
	hematologySpecificProc AS
	(
		select proc_id, proc_code, description, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where proc_id not in
		(
			select proc_id
			from primaryCareEncounters2017 as primEnc
			  join `starr_datalake2018.order_proc` as op on primEnc.primaryEncounterId = op.pat_enc_csn_id_coded 
			group by proc_id
			having count(*) >= 10
		)
		group by proc_id, proc_code, description
        order by count(*) desc
        -- 296 proc rarely ordered by primary care
        -- Donor virus testing, HLA order, ... doesn't look like much a primary care could not order. Just rare as cancer specific.
	),



--(7) New (Endocrine) specialty encounters in 2017 that do NOT include a specialty only procedure (e.g., biopsy, injection)

endocrineNewPatientNonSpecializedEncounters2017 AS
(
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from endocrineNewPatientEncounters2017_ as specEnc
	where extract(YEAR FROM specialtyEncounterDateTime) = 2017
 
    except distinct
    
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where op.proc_code in 
    ('210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250') -- Injections, biopsies, etc. that would not be expected to be done by generalist
    -- 4,479 New Patient encounters in 2017 out of 4,796 New Patient encounters

    except distinct 

	select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
    and om.medication_id in (90538, 2364, 25122, 199672, 210386, 199615, 86468, 199672, 210913, 126553, 94690, 115097, 7785, 541179, 2243, 84544, 115097, 2364, 213399)
    -- 4,389 New Patient specialty encounters in 2017 that don't include an order for an (injectable) med or procedure that can likely only occur in specialty clinic
),

endocrineNewPatientNoMedsOrProcsEncounters2017 AS
(
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from endocrineNewPatientEncounters2017_ as specEnc
  	where extract(YEAR FROM specialtyEncounterDateTime) = 2017

    except distinct
    
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where op.proc_code in 
    ('210976536', 'EIA004', '210910022', 'PATH9', 'PATH9', 'INJ190835', 'IMGNM0014', '210995251', 'IMGUSBT', 'IMGUS0033', 'IMGNM0015', '21090897', '210999358', 'INJJ0897.UHA', '210999091', '2109J0834', '230976942.UHA', '210992250') -- Injections, biopsies, etc. that would not be expected to be done by generalist
    -- 4,479 New Patient encounters in 2017 out of 4,796 New Patient encounters

    except distinct 

	select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class <> 'Historical Med'
    -- 2,874 New Patient specialty encounters in 2017 that only include non-specialized procedure orders (mostly labs, imaging, referrals). Not even any oral med / treatment prescriptions
),


hematologyNewPatientNonSpecializedEncounters2017 AS
(
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from hematologyNewPatientEncounters2017_ as specEnc
	where extract(YEAR FROM specialtyEncounterDateTime) = 2017
	-- 2,895 New Patient Encounters in 2017
 
    except distinct
    
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from hematologyNewPatientEncounters2017_ as specEnc
		join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
	where op.proc_code in 
    	('LABBBPRBC','11500201','PATH16','11500202','PATH9','LABBBPPLT','NUR14606A','NUR14606B','NUR744','210936589') -- Blood transfusion, FNA, etc. that would not be expected to be done by generalist
    -- 2,877 New Patient encounters in 2017 without the above procedure orders

    except distinct 

	select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
	from hematologyNewPatientEncounters2017_ as specEnc
		join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
	where order_class <> 'Historical Med'	-- Exclude IV and chemotherapy related meds that a primary care would be unlikely to order
    and om.medication_id in (213662,209509,226945,112594,126580,540302,211084,540301,540304,221562,85848,112593,230620,230501,10467,200346,206390,213297,96471,126580,10236,540145,122481,85848,540763,236322,205661,213978,94592,210518,221636,10236,540145,122481,85848,540763,236322,205661,213978,94592,210518,221636,213980,13531,237602,237606,205208,232098,213297,7319,114723,242838,114723,210379,80845,199389,210527,9062,77372,7319,115220,115220,127401,231363,10537,228717,9063,110888,7319,23204,115378,236322,94592,202044,7319,206291,237603,95354,126404,114814,88720,28921,31915,10248,3708,211638,36089,31025,870,23210,381,117152,80504,237599,237601,29481,5510,126917,121514,8679,209037,19292,7319,221638,242528,77867,127400,201699,212878,127420,91568,13733,119134,10000,2331,2364,203466,28871,237600,96053,21102,212882,110889,4871,2364,10177,127420,209888,91375,28870,9605,209878,43483,95803,234674,89428,239975,80845,4454,112403,542067,31916,112597,242207,1965,2131,241649,15861,231412,10531)
    -- 2,732 New Patient specialty encounters in 2017 that don't include an order for an (injectable) med or procedure that can likely only occur in specialty clinic
),

hematologyNewPatientNoMedsOrProcsEncounters2017 AS
(
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from hematologyNewPatientEncounters2017_ as specEnc
	where extract(YEAR FROM specialtyEncounterDateTime) = 2017
	-- 2,895 New Patient Encounters in 2017
 
    except distinct
    
    select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime 
	from hematologyNewPatientEncounters2017_ as specEnc
		join `starr_datalake2018.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
	where op.proc_code in 
    	('LABBBPRBC','11500201','PATH16','11500202','PATH9','LABBBPPLT','NUR14606A','NUR14606B','NUR744','210936589') -- Blood transfusion, FNA, etc. that would not be expected to be done by generalist
    -- 2,877 New Patient encounters in 2017 without the above procedure orders

    except distinct 

	select specEnc.jc_uid, specEnc.specialtyEncounterId, specEnc.specialtyEncounterDateTime
	from hematologyNewPatientEncounters2017_ as specEnc
		join `starr_datalake2018.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
	where order_class <> 'Historical Med'	-- Exclude IV and chemotherapy related meds that a primary care would be unlikely to order
    -- 2,594 New Patient specialty encounters in 2017 that don't include an order for ANY meds, and not specialty specific procedurs
),

-- (8) Join to find New Patient specialty visits that did not include specialized treatment and are followed by another visit
  	-- Implies that the actions in the New Patient visit could have been done before hand and then 
  	--	the follow-up could have happened immediately, eliminating the need for the extra follow-up visit
  	endocrineNonSpecialEncounterFollowup2017 AS
  	(
		select newEnc.*, min(nonNewSpecialtyEncounterId) AS firstFollowupEncounterId, min(nonNewSpecialtyEncounterDateTime) AS firstFollowupDateTime,
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY) as daysUntilFollowup, 
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH) as monthsUntilFollowup
		from endocrineNewPatientNoMedsOrProcsEncounters2017 as newEnc join endocrineNonNewPatientEncounters2017_ as followupEnc using (jc_uid)
		where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND 11
	  	group by jc_uid, specialtyEncounterId, specialtyEncounterDateTime
	  	-- 1,167 New Patient to follow-up specialty encounters within 6 months
	  	-- 1,451 New Patient to follow-up specialty encounters within 12 months
	  	-- Means >1,000 didn't follow-up in specialty clinic at all within 12 months, 
	  	--	implying many of those New Patient visits weren't even necessary
	  	-- Follow-up: Average 96 days, StdDev 85 days
	 ),

  	hematologyNonSpecialEncounterFollowup2017 AS
  	(
		select newEnc.*, min(nonNewSpecialtyEncounterId) AS firstFollowupEncounterId, min(nonNewSpecialtyEncounterDateTime) AS firstFollowupDateTime,
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, DAY) as daysUntilFollowup, 
	    	DATETIME_DIFF(min(followupEnc.nonNewSpecialtyEncounterDateTime), newEnc.specialtyEncounterDateTime, MONTH) as monthsUntilFollowup
		from hematologyNewPatientNoMedsOrProcsEncounters2017 as newEnc join hematologyNonNewPatientEncounters2017_ as followupEnc using (jc_uid)
		where DATETIME_DIFF(followupEnc.nonNewSpecialtyEncounterDateTime, newEnc.specialtyEncounterDateTime, MONTH) BETWEEN 0 AND 11
	  	group by jc_uid, specialtyEncounterId, specialtyEncounterDateTime
	  	-- 1,075 New Patient to follow-up specialty encounters within 6 months
	  	-- 1,279 New Patient to follow-up specialty encounters within 12 months
	  	-- Means >1,000 didn't follow-up in specialty clinic at all within 12 months, 
	  	--	implying many of those New Patient visits weren't even necessary
	  	-- Follow-up: Average 84 days, StdDev 74 days
	 ),

-- (9) New Patient specialty encouners where had a particular lab abnormality beforehand (to estimate power calculations)
    /*
	endocrinePriorAbnormalTSH AS
	(
		select specNewEnc.*, ord_num_value, DATETIME_DIFF(specNewEnc.specialtyEncounterDateTime, res.result_time_jittered, MONTH) as labToEncMonths
		from `starr_datalake2018.lab_result` as res
		   join endocrineNewPatientEncounters2017_ as specNewEnc
		        on res.rit_uid = specNewEnc.jc_uid 
		where base_name = 'TSH'
		and ord_num_value <0.5
		and EXTRACT(YEAR from specNewEnc.specialtyEncounterDateTime) = 2017
		and DATETIME_DIFF(specNewEnc.specialtyEncounterDateTime, res.result_time_jittered, MONTH) BETWEEN 0 AND 11
		-- 805 Endocrine New Patient visits in 2017 with low TSH in prior year
	),

	endocrinePriorAbnormalCalcium AS
	(
		select specNewEnc.*, ord_num_value, DATETIME_DIFF(specNewEnc.specialtyEncounterDateTime, res.result_time_jittered, MONTH) as labToEncMonths
		from `starr_datalake2018.lab_result` as res
		   join specialtyNewPatientEncounters2017 as specNewEnc
		        on res.rit_uid = specNewEnc.jc_uid 
		where base_name = 'CA'
		and ord_num_value > 11.5
		and EXTRACT(YEAR from specNewEnc.specialtyEncounterDateTime) = 2017
		and DATETIME_DIFF(specNewEnc.specialtyEncounterDateTime, res.result_time_jittered, MONTH) BETWEEN 0 AND 11
		-- 73 Endocrine New Patient visits in 2017 with high CA in prior year
	),

	hematologyPriorAbnormalPlt AS
	(
		select specNewEnc.*, ord_num_value, DATETIME_DIFF(specNewEnc.specialtyEncounterDateTime, res.result_time_jittered, MONTH) as labToEncMonths
		from `starr_datalake2018.lab_result` as res
		   join hematologyNewPatientEncounters2017 as specNewEnc
		        on res.rit_uid = specNewEnc.jc_uid 
		where base_name = 'PLT'
		and ord_num_value < 30
		and EXTRACT(YEAR from specNewEnc.specialtyEncounterDateTime) = 2017
		and DATETIME_DIFF(specNewEnc.specialtyEncounterDateTime, res.result_time_jittered, MONTH) BETWEEN 0 AND 11
		-- 2784 Hematology New Patient visits in 2017 with low PLT in prior year
		--	(But this is likely capturing a lot of MDS, leukemia, etc., not just isolated thrombocytopenia)
	),
	*/
	spacer AS (select * from primaryCareEncounters2017)
	