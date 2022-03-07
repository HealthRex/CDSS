-- (1) Find all (outpatient) encounter referral orders for specialty (Endocrinology)
	WITH 

	referringEncountersEndocrine2017 AS
	(
		select op.anon_id, op.pat_enc_csn_id_coded as referringEncounterId, 
	      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
		from `som-nero-phi-jonc101.shc_core_2021.order_proc` as op 
		  join `som-nero-phi-jonc101.shc_core_2021.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
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
		select op.anon_id, op.pat_enc_csn_id_coded as referringEncounterId, 
	      enc.appt_when_jittered as referringApptDateTime, op.order_time_jittered as referralOrderDateTime
		from `som-nero-phi-jonc101.shc_core_2021.order_proc` as op 
		  join `som-nero-phi-jonc101.shc_core_2021.encounter` as enc on op.pat_enc_csn_id_coded = enc.pat_enc_csn_id_coded 
		where proc_id = 34352 -- proc_code = 'REF18' -- REFERRAL TO HEMATOLOGY CLINIC -- Should be the same thing, but 2020 database update seems to be missing proc_code for many records
		and ordering_mode = 'Outpatient'
		and EXTRACT(YEAR from order_time_jittered) = 2017
		-- 2406 Records - Hematology
	),



	-- (1a) Find all (outpatient) encounters with referral orders for ANY specialty (use as reference baseline for relative risk estimates)


	-- (1b) Find clinic encounters from Primary Care specialities
	
	primaryCareEncounters2017 AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as primaryEncounterId, enc.appt_when_jittered as primaryEncounterDateTime, 
      		dep.specialty_dep_c, dep.specialty
		from `som-nero-phi-jonc101.shc_core_2021.encounter` as enc join `som-nero-phi-jonc101.shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c in ('9','17','125','2527') -- dep.specialty in 'Family Medicine','Internal Medicine','Primary Care','Express Care'
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) = 2017	-- >= So capture follow-up visits in 2018 as well
		-- 420,964 records in 2017
	),


--(2) Find all (New Patient) clinic visits for the referred specialty

	endocrineNewPatientEncounters2017_ AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
		from `som-nero-phi-jonc101.shc_core_2021.encounter` as enc join `som-nero-phi-jonc101.shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
		and visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
		-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017	-- >= So capture follow-up visits in 2018 as well
		-- 4796 records in 2017 (10650 for 2017 and after, largely including 2018)
	),
	hematologyNewPatientEncounters2017_ AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as specialtyEncounterId, enc.appt_when_jittered as specialtyEncounterDateTime
		from `som-nero-phi-jonc101.shc_core_2021.encounter` as enc join `som-nero-phi-jonc101.shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
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
		select enc.anon_id, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
		from `som-nero-phi-jonc101.shc_core_2021.encounter` as enc join `som-nero-phi-jonc101.shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
		and visit_type not like 'NEW PATIENT%' -- Wide list of different 'ESTABLISHED PATIENT...,' 'RETURN PATIENT...,' 'THYROID BIOPSY,' etc.
		and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc. (20,489 out 21,817 are Office Visit / Appointment)
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) >= 2017
    	-- 20,489 non-NEW PATIENT specialty encounter visits in 2017
    ),
    hematologyNonNewPatientEncounters2017_ AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded as nonNewSpecialtyEncounterId, enc.appt_when_jittered as nonNewSpecialtyEncounterDateTime
		from `som-nero-phi-jonc101.shc_core_2021.encounter` as enc join `som-nero-phi-jonc101.shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
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
		from referringEncountersEndocrine2017 as refEnc join endocrineNewPatientEncounters2017_ as specEnc using (anon_id)
		where DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, MONTH) BETWEEN 0 AND 11
		-- 2,640 referred New Patient visit within 6 months
		-- 2,898 referred New Patient visit within 12 months
			-- 67 days average, 66 days stdev, 44 days median (IQR 26-83)
	),
	hematologyReferralTimes2017 AS
	(
		select *, DATETIME_DIFF(specEnc.specialtyEncounterDateTime, refEnc.referralOrderDateTime, DAY) as referralDelayDays
		from referringEncountersHematology2017 as refEnc join hematologyNewPatientEncounters2017_ as specEnc using (anon_id)
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
		  join `som-nero-phi-jonc101.shc_core_2021.diagnosis` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_jittered 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
		-- 8,240 Distinct diagnosis codes, but long tail dominated by 512 Osteoporosis, 487 Thyroid Nodule, 424 Hypothyroid...
	),
    hematologyReferralDiagnoses AS
    (
		select dx.icd9, dx.icd10, dx_name, count(*)
		from referringEncountersHematology2017 as refEnc 
		  join `som-nero-phi-jonc101.shc_core_2021.diagnosis` as dx on refEnc.referringEncounterId = dx.pat_enc_csn_id_jittered 
		group by dx.icd9, dx.icd10, dx_name
		order by count(*) desc
		-- 5,257 Distinct diagnosis codes, but long tail dominated by 169 Anemia, 104 Thrombocytopenia, 92 Anemia, 90 Iron Def Anemia, 72 Leukocytosis...
	),
    
    -- Order Med from encounters in (2)
    endocrineNewEncounterMeds AS
    (
		select medication_id, med_description, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		group by medication_id, med_description
		order by count(*) desc
		-- 761 Distinct medication_id descriptions, but can likely boil down many based on active ingredient
		-- 242 OneTouch Verio Strip, 217 OneTouch Lancet, 185 Metformin, 164 Dexamethasone, 150 Alendronate
	),
	endocrineNewEncounterMedClass AS
	(
		select pharm_class_name, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		group by pharm_class_name
		order by count(*) desc
		-- 143 Distinct pharm_class_name types prescribed in the specialty visits
		-- 817 Insulins, 803 Thyroid Hormones, 660 Blood Sugar Diagnostics, 475 Diabetic Supplies, 462 Biguanide Anti-Diabetic, 398 Bone Resorption Inhibitors...
	),

    hematologyNewEncounterMeds AS
    (
		select medication_id, med_description, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
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
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		group by pharm_class_name
		order by count(*) desc
		-- 112 Distinct pharm_class_name types prescribed in the specialty visits
		-- 593 Anti-Emetic, 521 Glucocorticoids, 484 Antihistamines, 459 Adrenergic Agent, 245 Saline Preparation, 206 Iron Replacement, ...
	),

	primaryCareMeds AS
	(
		select medication_id, med_description, count(*)
		from primaryCareEncounters2017 as primEnc
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
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
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
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
		    join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		  where order_class_c <> 3 -- 'Historical Med'
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
		    join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		  where order_class_c <> 3 -- 'Historical Med'
		  group by specEnc.specialtyEncounterId 
		)
		-- 3.1 average distinct order_meds per specialty new visit, max 43
	),


    -- Order Proc from encounters in (2)
    endocrineNewPatientProc AS
    (
		select op.proc_code, description, count(*)
		from endocrineNewPatientEncounters2017_ as specEnc
		  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
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
		    join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		  group by specEnc.specialtyEncounterId 
		)
		-- 5.3 average distinct order_procs per specialty new visit, max 38
	),

    hematologyNewPatientProc AS
    (
		select op.proc_code, description, count(*)
		from hematologyNewPatientEncounters2017_ as specEnc
		  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
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
		    join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
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
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		and medication_id not in
		(
			select medication_id
			from primaryCareEncounters2017 as primEnc
			  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
			where order_class_c <> 3 -- 'Historical Med'
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
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on specEnc.specialtyEncounterId = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
		and medication_id not in
		(
			select medication_id
			from primaryCareEncounters2017 as primEnc
			  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on primEnc.primaryEncounterId = om.pat_enc_csn_id_coded 
			where order_class_c <> 3 -- 'Historical Med'
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
		  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where proc_id not in
		(
			select proc_id
			from primaryCareEncounters2017 as primEnc
			  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on primEnc.primaryEncounterId = op.pat_enc_csn_id_coded 
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
		  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on specEnc.specialtyEncounterId = op.pat_enc_csn_id_coded 
		where proc_id not in
		(
			select proc_id
			from primaryCareEncounters2017 as primEnc
			  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on primEnc.primaryEncounterId = op.pat_enc_csn_id_coded 
			group by proc_id
			having count(*) >= 10
		)
		group by proc_id, proc_code, description
        order by count(*) desc
        -- 296 proc rarely ordered by primary care
        -- Donor virus testing, HLA order, ... doesn't look like much a primary care could not order. Just rare as cancer specific.
	),


	spacer AS (select * from primaryCareEncounters2017)

    select * 
    from endocrineNewPatientProc
	

