CREATE OR REPLACE TABLE `som-nero-phi-jonc101.proj_nidactn_multisite_sf.records`
AS 

WITH cohort_condition AS
(
  SELECT  distinct A.person_id  
      , 'condition' as feature_type
      , PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE) as drug_exposure_start_DATE        
      , B.condition_start_DATE as observation_date
      , B.visit_occurrence_id
      , B.condition_concept_id as feature_concept_id  
      , A.TreatmentDuration
    FROM `som-nero-phi-jonc101.proj_nidactn_multisite_sf.drug_eras` A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.condition_occurrence`  B
    ON A.person_id = B.person_id
    WHERE B.condition_start_DATE <= PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE)  
    AND DATE_DIFF(PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE)  , B.condition_start_DATE, DAY) <= 90
    AND B.condition_concept_id IN 
      (SELECT distinct cast(string_field_1 as INT64) FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'diagnosis')
),


cohort_procedure AS
(
  SELECT  distinct A.person_id  
      , 'procedure' as feature_type
      , PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE) as drug_exposure_start_DATE            
      , B.procedure_DATE as observation_date
      , B.visit_occurrence_id
      , B.procedure_concept_id as feature_concept_id  
      , A.TreatmentDuration     
    FROM `som-nero-phi-jonc101.proj_nidactn_multisite_sf.drug_eras` A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.procedure_occurrence`  B
    ON A.person_id = B.person_id
    WHERE B.procedure_DATE <= PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE)  
    AND DATE_DIFF(PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE)  , B.procedure_DATE, DAY) <= 90    
    AND B.procedure_concept_id IN 
    (SELECT distinct cast(string_field_1 as INT64) FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'procedure')
),


cohort_drug AS
(
  SELECT  distinct A.person_id  
      , 'drug' as feature_type
      , PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE) as drug_exposure_start_DATE            
      , B.drug_exposure_start_DATE as observation_date
      , B.visit_occurrence_id
      , B.drug_concept_id as feature_concept_id  
      , A.TreatmentDuration     
    FROM `som-nero-phi-jonc101.proj_nidactn_multisite_sf.drug_eras` A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure`  B
    ON A.person_id = B.person_id
    WHERE B.drug_exposure_start_DATE <= PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE)  
    AND DATE_DIFF(PARSE_DATE('%Y-%m-%d', A.drug_exposure_start_DATE)  , B.drug_exposure_start_DATE, DAY) <= 90    
    AND B.drug_concept_id IN 
       (SELECT distinct cast(string_field_1 as INT64) FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'drug')
),

all_records as
(
select *
from cohort_condition
union all
select *
from cohort_procedure
union all
select *
from cohort_drug)

SELECT * FROM all_records 



