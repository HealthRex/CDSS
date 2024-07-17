WITH 
-- Set modifiable query parameters in one place here, so can abstract the subsequent queries structures below
-- Replace values to those of different cohorts of interest
-- https://stackoverflow.com/questions/29759628/setting-big-query-variables-like-mysql
-- https://medium.com/google-cloud/how-to-work-with-array-and-structs-in-bigquery-9c0a2ea584a6
params AS 
(
	select 
		['44']
			as specialtyDepIds, 	-- dep_map.specialty = 'Vascular' 

		['I73.9']	-- ICD 10 codes for Peripheral Artery Disease. Beware that this seems to capture Peripheral VASCULAR Disease, which is not entirely clear to be "arterial" and no venous disease
			as targetICD10, 

		[	'VSC03', 	-- VSC ARTERIAL EXAM/ABIS
			'VSC04', 	-- VSC GRAFT W ABIS ART DUP
			--'IMGCT0019',-- CT ABDOMEN ANGIOGRAPHY W AND WO IV CONTRAST -- This seems to NOT include legs, so couldn't diagnose PERIPHERAL artery disease based on this?
			'IMGCT0021'	-- CT ABDOMEN AORTA PELVIS RUNOFF LOWER EXTREMITIES BILATERAL ANGIOGRAPHY W AND WO IV CONTRAST
		]	-- Order_Proc.proc_code for imaging test that could diagnose Peripheral Artery Disease
			as workupProcCode,

		12	as followupMonths, -- Number of months to look back after a workup order to look for the target diagnosis code (note will also "look forward" up to 1 month, as allows same month)

		['3']	as excludeMedOrderClass -- 'Historical Med' class, doesn't represent a new prescription

),


-- Find all clinic visits for the referred specialty
specialtyPatientEncounter AS
(
	select enc.anon_id, enc.pat_enc_csn_id_coded as encounterId, enc.appt_when_jittered as encounterDateTime
	from `shc_core_2023.encounter` as enc 
		join `shc_core_2023.dep_map` as dep on enc.department_id = dep.department_id,
		params
	where dep.specialty_dep_c in UNNEST(params.specialtyDepIds)
	-- and visit_type like '%NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
	and appt_type in ('Office Visit','Appointment') -- Otherwise Telephone, Refill, Orders Only, etc.
	and appt_status = 'Completed'
	--and extract(YEAR from enc.appt_time_jittered) = params.cohortYear
),


-- Identify encounter table cohort for descriptive stats to follow
cohortEncounter AS
(
	select *
	from specialtyPatientEncounter
),

-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------
-- Should not need to edit much of anything below this line. Standard queries with parameters and 
--   designation of a cohort of encounters of interest that can be modified above.
-- Can modify last result lines to extract reports of interest to describe the cohort
-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------


-- Providers who have been at a specialty clinic visit
cohortEncounterProvider AS
(
  select prov.shc_prov_id as prov_map_id, prov_type, specialty_or_dept, 
    count(distinct cohortEnc.encounterId) as nEncounter, count(distinct cohortEnc.anon_id) as nPatient
  from cohortEncounter as cohortEnc
    join shc_core_2023.encounter as enc on (cohortEnc.encounterId = enc.pat_enc_csn_id_coded)
    join shc_core_2023.prov_map as prov on (enc.visit_prov_map_id = prov.shc_prov_id)
  where shc_prov_id like 'S%' -- Screen out 'T%' IDs which seem to refer to a RESOURCE or other non-human ID
  group by prov.shc_prov_id, prov_type, specialty_or_dept
  order by nEncounter desc
),

cohortEncounterDiagnosis AS
(
	select 
		dx.icd9, dx.icd10, dx_name, 
		count(*) as nDiagnosis, count(distinct cohortEnc.anon_id) as nPatient, count(distinct cohortEnc.encounterId) as nEncounter
	from cohortEncounter as cohortEnc 
	  join `shc_core_2023.diagnosis` as dx on cohortEnc.encounterId = dx.pat_enc_csn_id_jittered 
	group by dx.icd9, dx.icd10, dx_name
	order by count(*) desc
),

cohortEncounterSourceDepartment AS
(
	select 
		specialty_dep_c, specialty, department_id, dept_abbreviation, department_name, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from cohortEncounter as cohortEnc 
		join shc_core_2023.encounter as enc on (cohortEnc.encounterId = enc.pat_enc_csn_id_coded)
		join shc_core_2023.dep_map as dep using (department_id)
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
	  join `shc_core_2023.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
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
	    join `shc_core_2023.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
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
	  join `shc_core_2023.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
	group by proc_code, description
	order by count(*) desc
),

-- Number of distinct Orders per Encounter
cohortEncounterProcCount AS
(
	select avg(nDistinctOrderProcs) as avgDistinctOrderProcs, max(nDistinctOrderProcs) as maxDistinctOrderProcs
	from
	(
	  select cohortEnc.encounterId, count(distinct op.proc_code) as nDistinctOrderProcs
	  from cohortEncounter as cohortEnc
	    join `shc_core_2023.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
	  group by cohortEnc.encounterId 
	)
),

-- Procedure from encounters (more likely completed/billed for procedures, as opposed to orders)
cohortEncounterProcedure AS
(
	select 
		px_id, code, description, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	  from cohortEncounter as cohortEnc
	  join `shc_core_2023.procedure` as proc on cohortEnc.encounterId = proc.pat_enc_csn_id_coded 
	group by px_id, code, description
	order by count(*) desc
),




---------------------------------------------------------------
--------- Specific Queries of Interest ------------------------
---------------------------------------------------------------


-- Isolate entries of the specific diagnosis codes of interest, 
-- 	but only if it was entered by one of the providers attached to the cohort encounters of interest
specificDiagnosisFromCohortEncounterProvider AS
(
	select 
		dx.icd9, dx.icd10, dx_name, 
		dx.anon_id, dx.pat_enc_csn_id_jittered as encounterId, start_date_jittered as dxDate 
	from cohortEncounterProvider as cohortEncProv 
	  join `shc_core_2023.diagnosis` as dx on 
	  	( CONCAT('S', cohortEncProv.prov_map_id) = dx.perf_prov_map_id), -- Diagnosis table adds an extra S prefix on provider IDs
	  	params
	where dx.icd10 in UNNEST(params.targetICD10)
),

-- Further isolate those specific diagnosis entries by cohort encounter providers
--	that occurred within X time AFTER one of the key workup procedure orders
specificDiagnosisAfterWorkupFromCohortEncounterProvider AS
(
	select 
		dx.icd9, dx.icd10, dx_name, 
		dx.anon_id, dx.encounterId, dx.dxDate,
		max(op.order_time_jittered) as lastWorkupOrderDate
	from specificDiagnosisFromCohortEncounterProvider as dx
	  join `shc_core_2023.order_proc` as op on (dx.anon_id = op.anon_id)
	  , params
	where op.proc_code in UNNEST(params.workupProcCode)
		and DATETIME_DIFF(dx.dxDate, op.order_time_jittered, MONTH) 
			BETWEEN 0 AND (params.followupMonths-1) -- Follow-up time
			-- Checking within MONTH resolution means the order could have happened AFTER the diagnosis date, 
			-- 	if it happened within the same (zero difference) month
	group by 
		dx.icd9, dx.icd10, dx_name, 
		dx.anon_id, dx.encounterId, dx.dxDate
),




-- Reidentify the diagnosis dates
reidentifySpecificDiagnosisAfterWorkupFromCohortEncounterProvider AS
(
	select 
		mrn, 
		icd10, dx_name,
		DATETIME_SUB(dxDate, INTERVAL jitter DAY) as realDxDate,
		DATETIME_SUB(lastWorkupOrderDate, INTERVAL jitter DAY) as realLastWorkupOrderDate,
	from 
		specificDiagnosisAfterWorkupFromCohortEncounterProvider as targetDx
		join `som-nero-phi-jonc101-secure.starr_map.shc_map_2023` using (anon_id)
),

-- specificDiagnosesPerYear AS
(
	select EXTRACT(YEAR from realDxDate) as realDxYear, count(distinct mrn)
	from reidentifySpecificDiagnosisAfterWorkupFromCohortEncounterProvider
	group by realDxYear
	order by realDxYear desc
),

spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

-------------------------------------------------------------------------------------------------
-- Replace or uncomment below with specific items to query to generate results of interest
-------------------------------------------------------------------------------------------------

-- select * from cohortEncounter
-- select * from cohortEncounterProvider
-- select * from cohortEncounterDiagnosis
-- select * from cohortEncounterSourceDepartment
-- select * from cohortEncounterMed
-- select * from cohortEncounterMedCount
-- select * from cohortEncounterProc
-- select * from cohortEncounterProcCount
-- select * from cohortEncounterProcedure
-- select * from cohortSpecificMeds
-- select * from cohortSpecificProc

-- select * from specificDiagnosisFromCohortEncounterProvider
-- select * from specificDiagnosisAfterWorkupFromCohortEncounterProvider


limit 1000




