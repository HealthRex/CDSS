-- Test query for common note concepts mentioned in ER visits, organized by primary diagnosis
-- May need further debugging, as counts seem small (even for 1% sample, most common diagnosis is Chest Pain with 161 patients, would be ~16,100 in total dataset?)

WITH 
emergencyRoomVisitPrimaryDiagnoses AS
(
	select 
		co.condition_source_value, cc.concept_name as condition_concept_name, 
		count(distinct vo.visit_occurrence_id) as nVisits,
		count(distinct vo.person_id) as nPatients
	from 
			`som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.visit_occurrence` as vo
				join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.condition_occurrence` as co
					using (visit_occurrence_id)
				join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.concept` as cc
						on co.condition_concept_id = cc.concept_id
	where 
		vo.visit_concept_id = 9203 -- Emergency Room Visit
		and condition_concept_id <> 0 -- Lots of 0 values
		and condition_status_concept_id = 32902	-- Primary Diagnosis
	group by
		co.condition_source_value, cc.concept_name
	having
		nPatients > 10	 -- Avoid rare items
	order by
		nPatients desc
),
emergencyRoomVisitPrimaryDiagnosesNoteConcepts AS
(
	select 
		erDx.condition_source_value, erDx.condition_concept_name,
		erDx.nVisits as nVisitsPerERDx, erDx.nPatients as nPatientsPerERDx,
		nc.concept_name as note_concept_name, --nc.domain_id,
		count(distinct vo.visit_occurrence_id) as nVisits,
		count(distinct vo.person_id) as nPatients
	from 
			`som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.visit_occurrence` as vo
				join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.condition_occurrence` as co
					using (visit_occurrence_id)
				join emergencyRoomVisitPrimaryDiagnoses as erDx	-- Join this separately so can get patient/visit counts per diagnosis as well as per note concept
						on co.condition_source_value = erDx.condition_source_value
				join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.note` as n
						using (visit_occurrence_id)
				join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.note_nlp` as nlp
						using (note_id)
				join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.concept` as nc
						on nlp.note_nlp_source_concept_id = nc.concept_id
	where 
		vo.visit_concept_id = 9203 -- Emergency Room Visit
		and condition_concept_id <> 0 -- Lots of 0 values
		and condition_status_concept_id = 32902	-- Primary Diagnosis
		and note_type_concept_id = 44814646	-- ED Provider Notes
		--and term_exists = 'Y'	-- Interested in relevant info, so negated presence also suggests relevant
	group by
		erDx.condition_source_value, erDx.condition_concept_name,
		erDx.nVisits, erDx.nPatients,
		nc.concept_name--, nc.domain_id
	having
		nPatients > nPatientsPerERDx / 2 -- Only look for things that occur in at least half of cases for now
	order by
		nVisitsPerERDx desc,
		nVisits desc
)

select *
from emergencyRoomVisitPrimaryDiagnosesNoteConcepts

