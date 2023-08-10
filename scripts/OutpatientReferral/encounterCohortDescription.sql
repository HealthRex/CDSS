-- Given patient encounter cohort queries defined using common table expressions (CTEs) 
-- 	(e.g., from specialtyReferralEncounterCohortDefintiions.sql),
--  generate description tables (e.g., top diagnosis, medications, orders, source department).
-- Instead of copy pasting this entire sequence, can replace the cohort CTE/query with the generic cohortEncounter identifier.
-- E.g., Look for top diagnoses in Endocrine clinic visits
--	(or all missed follow-up clinic visits or new vs. follow-up visits, etc.)

WITH 
-- Set modifiable query parameters in one place here, so can abstract the subsequent queries structures below
-- Replace values to those of different cohorts of interest
-- https://stackoverflow.com/questions/29759628/setting-big-query-variables-like-mysql
-- https://medium.com/google-cloud/how-to-work-with-array-and-structs-in-bigquery-9c0a2ea584a6
params AS 
(
	select 
		[3]	as excludeMedOrderClass, -- 'Historical Med' class, doesn't represent a new prescription
		10 as minPatientsForNonRareItems -- If an item has not been ordered for more than this number of patients, assume it is too rare to use/recommend
),

cohortEncounter AS
(	-- This is a sample placeholder of all NEW PATIENT encounters in any clinic
	-- Replace this with a specific cohort of interest, which can be constructed through a separate series of common table expressions
	-- E.g., See specialtyReferralEncounterCohortDefinitions.sql, copy in those CTE queries above, then
	--	replace the below with something like "select anon_id, encounterId, encounterDateTime from referringEncounter"
	-- %%% REPLACE BELOW WITH COHORT DEFINITION OF INTEREST %%% --
	select 
		anon_id, 
		pat_enc_csn_id_coded as encounterId,
		appt_when_jittered as encounterDateTime
	from `shc_core_2021.encounter` as enc
	where visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
	and appt_status = 'Completed'
),

referenceEncounter AS
(	-- Example placeholder of all NEW PATIENT encounters in any clinic for any reason/diagnosis
	-- Used as a comparison/baseline reference group to compare the above cohort of interest against 
	-- %%% REPLACE BELOW WITH REFERENCE COHORT DEFINITION OF INTEREST %%% --
	select distinct
		anon_id, 
		pat_enc_csn_id_coded as encounterId,
		appt_when_jittered as encounterDateTime
	from `shc_core_2021.encounter` as enc
	where visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
	and appt_status = 'Completed'
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
	  join `shc_core_2021.diagnosis` as dx on cohortEnc.encounterId = dx.pat_enc_csn_id_jittered 
	group by dx.icd9, dx.icd10, dx_name
	order by count(*) desc
),

cohortEncounterSourceDepartment AS
(
	select 
		specialty_dep_c, specialty, department_id, dept_abbreviation, department_name, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from cohortEncounter as cohortEnc 
		join shc_core_2021.encounter as enc on (cohortEnc.encounterId = enc.pat_enc_csn_id_coded)
		join shc_core_2021.dep_map as dep using (department_id)
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
	  join `shc_core_2021.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
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
	    join `shc_core_2021.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
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
	  join `shc_core_2021.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
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
	    join `shc_core_2021.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
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
	  join `shc_core_2021.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
	  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
	and medication_id not in
	(
		select medication_id
		from referenceEncounter as refEnc
		  join `shc_core_2021.order_med` as om on refEnc.encounterId = om.pat_enc_csn_id_coded ,
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
	  join `shc_core_2021.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded ,
	  params
	where proc_id not in
	(
		select proc_id
		from referenceEncounter as refEnc
		  join `shc_core_2021.order_proc` as op on refEnc.encounterId = op.pat_enc_csn_id_coded 
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

-- select * from cohortEncounter
-- select * from cohortEncounterDiagnosis
-- select * from cohortEncounterSourceDepartment
select * from cohortEncounterMed
-- select * from cohortEncounterMedCount
-- select * from cohortEncounterProc
-- select * from cohortEncounterProcCount
-- select * from cohortSpecificMeds
-- select * from cohortSpecificProc

limit 100
