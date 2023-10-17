with stanfordData as (
  select distinct 
        person_id
        , drug_exposure_start_DATE
        , TreatmentDuration
  from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.trainset` 
  union all
  select distinct 
        person_id
        , drug_exposure_start_DATE
        , TreatmentDuration
  from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.testset`
), 

standardizedHolmuskConcepts as (
  select distinct 
        A.concept_id
        , A.Variable_type
        , A.concept_id as holmuskConceptID
        , B.concept_id_2 as standardizedConceptID
  from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.holmusk_significant_variables` A
  join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept_relationship` B
  on A.concept_id = CAST(B.concept_id_1 AS STRING)
  where B.relationship_id = 'Maps to'
),

diagRecords as (
  select distinct 
          B.person_id
        , B.drug_exposure_start_DATE
        , B.TreatmentDuration
        , CONCAT('predictor_', C.holmuskConceptID, '_', A.condition_concept_id) as feature_concept_id
  from `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.condition_occurrence` A
  join stanfordData B on A.person_id = B.person_id
  join standardizedHolmuskConcepts C on A.condition_concept_id = C.standardizedConceptID
  where 
    A.condition_concept_id in (select distinct standardizedConceptID from standardizedHolmuskConcepts where Variable_type = 'diagnosis')
  and 
  A.condition_start_DATE <= B.drug_exposure_start_DATE
),

procRecords as (
  select distinct 
          B.person_id
        , B.drug_exposure_start_DATE
        , B.TreatmentDuration
        , CONCAT('predictor_', C.holmuskConceptID, '_', A.procedure_concept_id) as feature_concept_id
  from `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.procedure_occurrence` A
  join stanfordData B on A.person_id = B.person_id
  join standardizedHolmuskConcepts C on A.procedure_concept_id = C.standardizedConceptID
  where 
    A.procedure_concept_id in (select distinct standardizedConceptID from standardizedHolmuskConcepts where Variable_type = 'procedure')
  and 
  A.procedure_DATE <= B.drug_exposure_start_DATE
), 

drugRecords as (
  select distinct 
          B.person_id
        , B.drug_exposure_start_DATE
        , B.TreatmentDuration
        , CONCAT('predictor_', C.holmuskConceptID, '_',A.drug_concept_id) as feature_concept_id
  from `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure` A
  join stanfordData B on A.person_id = B.person_id
  join standardizedHolmuskConcepts C on A.drug_concept_id = C.standardizedConceptID
  where 
    A.drug_concept_id in (select distinct standardizedConceptID from standardizedHolmuskConcepts where Variable_type = 'prescription')
  and 
  A.drug_exposure_start_DATE <= B.drug_exposure_start_DATE
),

allRecords as
(select distinct *
from diagRecords
union all
select distinct *
from drugRecords
union all
select distinct * 
from procRecords)


select *
from allRecords
order by person_id

