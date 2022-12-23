-- Given patient encounter cohort queries defined using common table expressions (CTEs) 
-- 	(e.g., from specialtyReferralEncounterCohortDefintiions.sql),
--  generate item association description tables (e.g., diagnosis, medications, orders, source department)
--  comparing one cohort against another reference/baseline/comparator/control/denominator cohort.
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
		['E05.90'] as exampleCohortDiagnosis, -- Example for cohort of encounters below, look for visits for this diagnosis (Thyroid Nodule)
		10 as minPatientsForNonRareItems -- If an item has not been ordered for more than this number of patients, assume it is too rare to use/recommend
),


cohortEncounter AS
(	-- This is example placeholder of all NEW PATIENT encounters in any clinic that includes the exampleCohortDiagnosis
	-- Replace this with a specific cohort of interest, which can be constructed through a separate series of common table expressions
	-- E.g., See specialtyReferralEncounterCohortDefinitions.sql, copy in those CTE queries above, then
	--	replace the below with something like "select anon_id, encounterId, encounterDateTime from referringEncounter"
	-- %%% REPLACE BELOW WITH COHORT DEFINITION OF INTEREST %%% --
	select distinct
		enc.anon_id, 
		pat_enc_csn_id_coded as encounterId,
		appt_when_jittered as encounterDateTime
	from `shc_core_2021.encounter` as enc
		join shc_core_2021.diagnosis as dx on enc.pat_enc_csn_id_coded = dx.pat_enc_csn_id_jittered,
		params
	where visit_type like 'NEW PATIENT%' -- Naturally screens to only 'Office Visit' enc_type 
	and appt_status = 'Completed'
	and dx.icd10 in UNNEST(params.exampleCohortDiagnosis)
),
referenceEncounter AS
(	-- Example placeholder of all NEW PATIENT encounters in any clinic for any reason/diagnosis
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
--   designation of a cohorts of encounters of interest that can be modified above.
-- Can modify last result lines to extract reports of interest to describe the cohort
-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------

-- Collect total counts for the cohorts for use as denominators for percentages later
cohortEncounterCount AS
(
	select count(distinct anon_id) as nPatients, count(distinct encounterId) as nEncounters
	from cohortEncounter
),
referenceEncounterCount AS
(
	select count(distinct anon_id) as nPatients, count(distinct encounterId) as nEncounters
	from referenceEncounter
),


-------------------------------------------------------------
-- Most common diagnoses from encounters
cohortEncounterDiagnosis AS
(
	select 
		dx.icd9, dx.icd10, dx_name, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from cohortEncounter as cohortEnc 
	  join `shc_core_2021.diagnosis` as dx on cohortEnc.encounterId = dx.pat_enc_csn_id_jittered 
	group by dx.icd9, dx.icd10, dx_name
	order by count(*) desc
),
referenceEncounterDiagnosis AS
(
	select 
		dx.icd9, dx.icd10, dx_name, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from referenceEncounter as cohortEnc  -- Same query but replace with reference encounter group
	  join `shc_core_2021.diagnosis` as dx on cohortEnc.encounterId = dx.pat_enc_csn_id_jittered 
	group by dx.icd9, dx.icd10, dx_name
	order by count(*) desc
),
-- Join primary cohort and reference encounters diagnosis counts into a common table
cohortVsReferenceDiagnosisCount AS
(
	select 
		icd10 as itemId, dx_name as description,
		cohortItem.nPatients as nPatientscohortItem, cohortItem.nEncounters as nEncounterscohortItem, 
		cohortEncounterCount.nPatients as nPatientsCohortTotal, cohortEncounterCount.nEncounters as nEncountersCohortTotal,
		referenceItem.nPatients as nPatientsreferenceItem, referenceItem.nEncounters as nEncountersreferenceItem,
		referenceEncounterCount.nPatients as nPatientsReferenceTotal, referenceEncounterCount.nEncounters as nEncountersReferenceTotal
	from cohortEncounterDiagnosis as cohortItem
		left join referenceEncounterDiagnosis as referenceItem USING (icd9, icd10, dx_name), -- Left outer in case there are items that the reference group is missing
		cohortEncounterCount, referenceEncounterCount -- Append columns for total cohort and reference counts
),
-- Assemble count results above into more interpretable rates (e.g., support, prevalence, PPV, lift/interest, etc.)
cohortVsReferenceDiagnosisRate AS
(
	select 
		itemId, description,
		(nEncounterscohortItem / nEncountersCohortTotal) as cohortItemEncounterRate, -- Comparable to PPV / confidence / conditional probability of the order proc in an encounter, given the cohort of interest
		(nEncountersreferenceItem / nEncountersReferenceTotal) as referenceItemEncounterRate, -- Comparable to baseline prevalence ~ support
		(nEncounterscohortItem / nEncountersCohortTotal) / (nEncountersreferenceItem / nEncountersReferenceTotal) as cohortVsreferenceItemEncounterRate, -- AKA Lift / interest. Similar to Relative Risk
		-- To Do -- Add p-value / (negative log-p) value to further sort by significance of association to avoid spurious
		nEncountersCohortTotal, nEncountersReferenceTotal, 
		nPatientsCohortTotal, nPatientsReferenceTotal
	from cohortVsReferenceDiagnosisCount, params
	where nPatientscohortItem > params.minPatientsForNonRareItems
	and nPatientsreferenceItem > params.minPatientsForNonRareItems
	order by 
		nEncounterscohortItem desc, -- Sort by most commonly seen order procs for the primary cohort
		itemId, description
),



-------------------------------------------------------------
-- Most common order Proc from encounters
cohortEncounterProc AS
(
	select 
		op.proc_code, description, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	  from cohortEncounter as cohortEnc
	  join `shc_core_2021.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
	group by proc_code, description
	order by nEncounters desc
),
referenceEncounterProc AS
(
	select 
		op.proc_code, description, 
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	  from referenceEncounter as cohortEnc -- Same query, just use the referenceEncounter list instead of cohortEncounter
	  join `shc_core_2021.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
	group by proc_code, description
	order by nEncounters desc
),
-- Join primary cohort and reference encounters order proc counts into a common table
cohortVsReferenceProcCount AS
(
	select 
		proc_code as itemId, description,
		cohortItem.nPatients as nPatientscohortItem, cohortItem.nEncounters as nEncounterscohortItem, 
		cohortEncounterCount.nPatients as nPatientsCohortTotal, cohortEncounterCount.nEncounters as nEncountersCohortTotal,
		referenceItem.nPatients as nPatientsreferenceItem, referenceItem.nEncounters as nEncountersreferenceItem,
		referenceEncounterCount.nPatients as nPatientsReferenceTotal, referenceEncounterCount.nEncounters as nEncountersReferenceTotal
	from cohortEncounterProc as cohortItem
		left join referenceEncounterProc as referenceItem USING (proc_code, description), -- Left outer in case there are items that the reference group is missing
		cohortEncounterCount, referenceEncounterCount -- Append columns for total cohort and reference counts
),
-- Assemble count results above into more interpretable rates (e.g., support, prevalence, PPV, lift/interest, etc.)
cohortVsReferenceProcRate AS
(
	select 
		itemId, description,
		(nEncounterscohortItem / nEncountersCohortTotal) as cohortItemEncounterRate, -- Comparable to PPV / confidence / conditional probability of the order proc in an encounter, given the cohort of interest
		(nEncountersreferenceItem / nEncountersReferenceTotal) as referenceItemEncounterRate, -- Comparable to baseline prevalence ~ support
		(nEncounterscohortItem / nEncountersCohortTotal) / (nEncountersreferenceItem / nEncountersReferenceTotal) as cohortVsreferenceItemEncounterRate, -- AKA Lift / interest. Similar to Relative Risk
		-- To Do -- Add p-value / (negative log-p) value to further sort by significance of association to avoid spurious
		nEncountersCohortTotal, nEncountersReferenceTotal, 
		nPatientsCohortTotal, nPatientsReferenceTotal
	from cohortVsReferenceProcCount, params
	where nPatientscohortItem > params.minPatientsForNonRareItems
	and nPatientsreferenceItem > params.minPatientsForNonRareItems
	order by 
		nEncounterscohortItem desc, -- Sort by most commonly seen order procs for the primary cohort
		itemId, description
),



-------------------------------------------------------------
-- Most common medication orders from encounters
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
	order by nEncounters desc
),
referenceEncounterMed AS
(
	select 
		medication_id, med_description,
		count(distinct cohortEnc.anon_id) as nPatients, count(distinct cohortEnc.encounterId) as nEncounters
	from referenceEncounter as cohortEnc -- Same query, but just use different cohort
	  join `shc_core_2021.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded ,
	  params
	where order_class_c not in UNNEST(params.excludeMedOrderClass)
	group by medication_id, med_description
	order by nEncounters desc
),
-- Join primary cohort and reference encounters order med counts into a common table
cohortVsReferenceMedCount AS
(
	select 
		medication_id as itemId, med_description as description,
		cohortItem.nPatients as nPatientscohortItem, cohortItem.nEncounters as nEncountersCohortItem, 
		cohortEncounterCount.nPatients as nPatientsCohortTotal, cohortEncounterCount.nEncounters as nEncountersCohortTotal,
		referenceItem.nPatients as nPatientsReferenceItem, referenceItem.nEncounters as nEncountersReferenceItem,
		referenceEncounterCount.nPatients as nPatientsReferenceTotal, referenceEncounterCount.nEncounters as nEncountersReferenceTotal
	from cohortEncounterMed as cohortItem
		left join referenceEncounterMed as referenceItem USING (medication_id, med_description), -- Left outer in case there are items that the reference group is missing
		cohortEncounterCount, referenceEncounterCount -- Append columns for total cohort and reference counts
),
-- Assemble count results above into more interpretable rates (e.g., support, prevalence, PPV, lift/interest, etc.)
cohortVsReferenceMedRate AS
(
	select 
		itemId, description,
		(nEncountersCohortItem / nEncountersCohortTotal) as cohortItemEncounterRate, -- Comparable to PPV / confidence / conditional probability of the order proc in an encounter, given the cohort of interest
		(nEncountersReferenceItem / nEncountersReferenceTotal) as referenceItemEncounterRate, -- Comparable to baseline prevalence ~ support
		(nEncountersCohortItem / nEncountersCohortTotal) / (nEncountersReferenceItem / nEncountersReferenceTotal) as cohortVsreferenceItemEncounterRate, -- AKA Lift / interest. Similar to Relative Risk
		-- To Do -- Add p-value / (negative log-p) value to further sort by significance of association to avoid spurious
		nEncountersCohortTotal, nEncountersReferenceTotal, 
		nPatientsCohortTotal, nPatientsReferenceTotal
	from cohortVsReferenceMedCount, params
	where nPatientscohortItem > params.minPatientsForNonRareItems
	and nPatientsreferenceItem > params.minPatientsForNonRareItems
	order by 
		nEncountersCohortItem desc, -- Sort by most commonly seen order procs for the primary cohort
		itemId, description
),



spacer AS (select null as tempSpacer) -- Just put this here so don't have to worry about ending last named query above with a comma or not

----------------------------------------------------------------------------------------------
-- Replace or uncomment below with specific items to query to generate results of interest
----------------------------------------------------------------------------------------------

--select * from cohortVsReferenceDiagnosisRate
select * from cohortVsReferenceProcRate
--select * from cohortVsReferenceMedRate
limit 100
