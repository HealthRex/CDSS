/*
Sketch of queries against STARR-OMOP database to illustrate potential to 
find psychiatry related visits, their notes, and keywords/concepts
*/

/*
select cs.care_site_name, cs.care_site_source_value, count(vo.visit_occurrence_id) as nVisits
from 
    `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.visit_occurrence` as vo
        join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.care_site` as cs
            on vo.care_site_id = cs.care_site_id
where care_site_name like '%PSYCH%'
group by cs.care_site_name, cs.care_site_source_value
order by nVisits desc
*/

select c.*, *
from 
    `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.note_nlp` as nlp
    --`som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.visit_occurrence` as vo
        join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.concept` as c
            on nlp.note_nlp_source_concept_id = c.concept_id
where note_id = 124459672
limit 100



-- Find all notes from a "PSYCH" related clinic site, and find most common note NLP
--	source concepts (i.e., keywords) mentioned
select cs.care_site_name, EXTRACT(YEAR FROM vo.visit_start_date) as visitYear, c.concept_name, 
    count(distinct nlp.note_id) as nNotes, 
    count(distinct vo.visit_occurrence_id) as nVisits, 
    count(distinct vo.person_id) as nPatients
from 
    `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.visit_occurrence` as vo
        join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.care_site` as cs
            on vo.care_site_id = cs.care_site_id
        join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.note` as n
            using (visit_occurrence_id)
        join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.note_nlp` as nlp
            using (note_id)
        join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_1pcent_latest.concept` as c
            on nlp.note_nlp_source_concept_id = c.concept_id
where care_site_name like '%PSYCH%'
and nlp.term_exists = 'Y'
group by cs.care_site_name, visitYear, c.concept_name
order by nPatients desc
limit 100