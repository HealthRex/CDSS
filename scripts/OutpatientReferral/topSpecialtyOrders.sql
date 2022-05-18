	WITH 

	-- Find all (New Patient) clinic visits (with info on specialty)
	newPatientEncounter AS
	(
		select enc.anon_id, enc.pat_enc_csn_id_coded, 
			dep.specialty_dep_c, dep.specialty, -- Groups different clinics into specialty groupings. E.g,. dep.specialty_dep_c = '7' -- dep.specialty like 'Endocrin%'
			enc.appt_when_jittered as encounterDateTime, extract(YEAR from enc.appt_time_jittered) as encounterYear
		from `som-nero-phi-jonc101.shc_core_2021.encounter` as enc 
		    join `som-nero-phi-jonc101.shc_core_2021.dep_map` as dep on enc.department_id = dep.department_id 
		where visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
		-- and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
		and appt_status = 'Completed'
		and extract(YEAR from enc.appt_time_jittered) = 2019	-- Avoid 2020 for now to avoid weird Covid patterns
	),

    -- Find all diagnoses associated with new patient encounters
    newPatientEncounterDiagnosis AS
    (
		select newEnc.*, dx.icd9, dx.icd10, dx_name
		from newPatientEncounter as newEnc 
		    join `som-nero-phi-jonc101.shc_core_2021.diagnosis` as dx on newEnc.pat_enc_csn_id_coded = dx.pat_enc_csn_id_jittered 
	),
    -- Order Med from encounters
    newPatientEncounterMed AS
    (
		select newEnc.*, medication_id, med_description, pharm_class_name
		from newPatientEncounter as newEnc 
		  join `som-nero-phi-jonc101.shc_core_2021.order_med` as om on newEnc.pat_enc_csn_id_coded = om.pat_enc_csn_id_coded 
		where order_class_c <> 3 -- 'Historical Med'
	),
    -- Order Proc from encounters
    newPatientEncounterProc AS
    (
		select newEnc.*, op.proc_code, op.description
		from newPatientEncounter as newEnc 
		  join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on newEnc.pat_enc_csn_id_coded = op.pat_enc_csn_id_coded 
	),
	-- Encounter * Diagnosis * Order Proc (will have redundancies, because one encounter can have multiple diagnoses, so later need to count unique by encounter or patient ID)
	newPatientEncounterDiagnosisProc AS
	(
		select newEnc.*, 
			dx.icd9, dx.icd10, dx_name, 
			op.proc_code, op.description
		from newPatientEncounter as newEnc 
		    join `som-nero-phi-jonc101.shc_core_2021.diagnosis` as dx on newEnc.pat_enc_csn_id_coded = dx.pat_enc_csn_id_jittered 
		  	join `som-nero-phi-jonc101.shc_core_2021.order_proc` as op on newEnc.pat_enc_csn_id_coded = op.pat_enc_csn_id_coded 
	),

	-- Start accumulating counts by different strata
	newPatientEncounterCount AS -- For baseline prevalence numbers, get total patient encounter counts of any type
	(
		select
			count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
		from newPatientEncounter
	),

	topSpecialty AS
	(
		select 
			specialty_dep_c, specialty, 
			count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
		from newPatientEncounter
		group by
			specialty_dep_c, specialty
		order by nEncounters desc
	),
	topDiagnosisPerSpecialty AS
	(
		select 
			specialty_dep_c, specialty, 
			icd9, icd10, dx_name, 
			count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
		from newPatientEncounterDiagnosis
		group by
			specialty_dep_c, specialty, 
			icd9, icd10, dx_name
		order by nEncounters desc
	),

	-- Break down (proc) order prevalence by different strata. Start with across all New Patient visits, any specialty, any diagnosis
	topProc AS 
	(
		select
			proc_code, description,
			count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
    	from newPatientEncounterProc
		group by
			proc_code, description
		order by nEncounters desc
	),
	topProcPerSpecialty AS
	(
		select
			specialty_dep_c, specialty,
			proc_code, description,
			count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
    	from newPatientEncounterProc
		group by
			specialty_dep_c, specialty,
			proc_code, description
		order by nEncounters desc
	),
	topProcPerSpecialtyDiagnosis AS
	(
		select
			specialty_dep_c, specialty,
			icd9, icd10, dx_name, 
			proc_code, description,
			count(distinct anon_id) as nPatients, count(distinct pat_enc_csn_id_coded) as nEncounters
    	from newPatientEncounterDiagnosisProc
		group by
			specialty_dep_c, specialty,
			icd9, icd10, dx_name, 
			proc_code, description
		order by nEncounters desc
	),

	-- Compare proc order rate per specialty-diagnosis vs. overall most common rate
	procCountsPerSpecialtyDiagnosis AS
	(
		select
			specialty_dep_c, specialty,
			icd9, icd10, dx_name, 
			proc_code, description,
			newEncCount.nPatients as nPatientsAny, newEncCount.nEncounters as nEncountersAny,
			ts.nPatients as nPatientsPerSpecialty, ts.nEncounters as nEncountersPerSpecialty,			
			tds.nPatients as nPatientsPerSpecialtyDiagnosis, tds.nEncounters as nEncountersPerSpecialtyDiagnosis,
			tp.nPatients as nPatientsProcPerAny, tp.nEncounters as nEncountersProcPerAny,
			tpsd.nPatients as nPatientsProcPerSpecialtyDiagnosis, tpsd.nEncounters as nEncountersProcPerSpecialtyDiagnosis
		from 
			topProcPerSpecialtyDiagnosis as tpsd join 
			topProc as tp using (proc_code, description) join
			topDiagnosisPerSpecialty as tds using (specialty_dep_c, specialty, icd9, icd10, dx_name) join
			topSpecialty as ts using (specialty_dep_c, specialty),
			newPatientEncounterCount as newEncCount 	-- Last one is not a joint, since no criteria. Should be a single count row product against all
	),
	procOrderRatePerSpecialtyDiagnosis AS
	(
		select
			specialty_dep_c, specialty,
			icd9, icd10, dx_name, 
			proc_code, description,

			(nEncountersProcPerSpecialtyDiagnosis / nEncountersPerSpecialtyDiagnosis) AS procRatePerSpecialtyDiagnosis,	-- AKA Confidence / PPV / Conditional Prevalence
			(nEncountersProcPerAny / nEncountersAny) AS procRatePerAny, -- AKA Baseline Prevalence ~ Support
			(nEncountersProcPerSpecialtyDiagnosis / nEncountersPerSpecialtyDiagnosis) / (nEncountersProcPerAny / nEncountersAny) AS procRateLiftPerSpecialtyDiagnosisVsAny,	-- AKA Lift / Interest (similar to relative risk)
			-- To Do -- Add p-value / (negative log-p) value to further sort by significance of association to avoid spurious

			nPatientsAny, nEncountersAny,
			nPatientsPerSpecialty, nEncountersPerSpecialty,			
			nPatientsPerSpecialtyDiagnosis, nEncountersPerSpecialtyDiagnosis,
			nPatientsProcPerAny, nEncountersProcPerAny,
			nPatientsProcPerSpecialtyDiagnosis, nEncountersProcPerSpecialtyDiagnosis,

		from procCountsPerSpecialtyDiagnosis
		where nPatientsProcPerSpecialtyDiagnosis > 10 -- Ignore small cases by only looking at items that are ordered for more than 10 different patients
		order by
			nEncountersPerSpecialty desc, specialty,	-- Sort by most common specialty type first
			nEncountersPerSpecialtyDiagnosis desc, icd10, dx_name,	-- Then sort by most common diagnosis per specialty
			procRatePerSpecialtyDiagnosis desc  -- Then sort by most common proc orders per specialty-diagnosis
	),
	spacer AS (select * from newPatientEncounter limit 10)

    select * 
    from procOrderRatePerSpecialtyDiagnosis
    limit 1000
	

