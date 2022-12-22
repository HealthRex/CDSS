-- Given patient encounter cohorts defined using common table expressions (CTEs),
--  generate description tables (e.g., top diagnosis, medications, orders, source department).
-- Instead of copy pasting this entire sequence, can replace the cohort CTE/query with the generic cohortEncounter identifier.
-- Provide a second encounter cohort using generic referenceEncounter identifier, so can report descriptive statistics
--	on the cohortEncounter relative to the referenceEncounter group. 
-- E.g., Look for top diagnoses in Endocrine clinic visits, relative to top diagnoses in all clinic visits 
--	(or all missed follow-up clinic visits or new vs. follow-up visits, etc.)
-- Can use the same cohortEnc for the referenceEnc if not doing any comparisons, then will just have a lot of ratios of 1:1

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
(	-- Default to just using the same as the cohortEncounter so no real comparisons
	-- Otherwise provide another reference / baseline / comparator / denominator cohort.
	-- %%% REPLACE BELOW WITH REFERENCE COHORT DEFINITION OF INTEREST %%% --
	select *
	from cohortEncounter
),

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

-- Med Order counts per Encounter
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


-- (5) Filter by only encounters including a diagnosis for XXX???

-- (6) Medications from cohort encounter Visits that are (rarely) ordered in reference cohort encounter (e.g., Primary Care)
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

-- Replace below with specific items to query to generate results of interest
select *
from cohortEncounterMed
limit 100
