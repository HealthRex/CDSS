CREATE OR REPLACE TABLE `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.topnFeatures`
AS 

with attritionCohort AS 
(
    select *
    from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.drug_eras`
    where  CAST(drug_exposure_start_DATE AS DATE) < DATE('2021-01-01') 
    and TreatmentDuration < 180
    and TreatmentDuration >= 2
), 

retentionCohort AS 
(
    select *
    from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.drug_eras`
    where  CAST(drug_exposure_start_DATE AS DATE) < DATE('2021-01-01') 
    and TreatmentDuration >= 180
),

attritionConditions AS
(
  SELECT  A.person_id      
      , B.condition_start_DATE
      , B.condition_concept_id      
    FROM attritionCohort A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.condition_occurrence`  B
    ON A.person_id = B.person_id
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept`  C
    ON B.condition_concept_id = C.concept_id
    WHERE B.condition_start_DATE < CAST(A.drug_exposure_start_DATE AS DATE)
    and C.standard_concept = 'S'
),

attritionStatConditions AS
(
      SELECT condition_concept_id
      , count(distinct person_id) AS num_in_attrition
      , count(distinct person_id)/(select count(distinct person_id) from attritionConditions) as perc_in_attrition
      FROM attritionConditions
      GROUP BY condition_concept_id
), 

retentionConditions AS
(SELECT  A.person_id
      , B.condition_start_DATE
      , B.condition_concept_id
    FROM retentionCohort A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.condition_occurrence`  B
    ON A.person_id = B.person_id
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept`  C
    ON B.condition_concept_id = C.concept_id    
    WHERE B.condition_start_DATE <= CAST(A.drug_exposure_start_DATE AS DATE)
    AND C.standard_concept = 'S'
),

retentionStatConditions AS
(
      SELECT condition_concept_id
      , count(distinct person_id) AS num_in_retention
      , count(distinct person_id)/(select count(distinct person_id) from retentionConditions) as perc_in_retention
      FROM retentionConditions
      GROUP BY condition_concept_id
),

frequentConditions as 
(
      SELECT A.condition_concept_id as concept_id
      , 'condition' as feature_type
      , C.concept_name
      , A.num_in_attrition
      , A.perc_in_attrition
      , B.num_in_retention
      , B.perc_in_retention
      , (A.perc_in_attrition/B.perc_in_retention) as perc_in_attrition_TO_perc_in_retention
      FROM attritionStatConditions A
      JOIN retentionStatConditions B ON A.condition_concept_id = B.condition_concept_id
      JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` C ON A.condition_concept_id = C.concept_id
      WHERE A.condition_concept_id != 0
      AND A.perc_in_attrition >= 0.05
      AND B.perc_in_retention >= 0.05
      ORDER BY perc_in_attrition_TO_perc_in_retention DESC
), 

attritionProcedures AS
(
  SELECT  A.person_id      
      , B.procedure_DATE
      , B.procedure_concept_id      
    FROM attritionCohort A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.procedure_occurrence`  B
    ON A.person_id = B.person_id
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept`  C
    ON B.procedure_concept_id = C.concept_id    
    WHERE B.procedure_DATE < CAST(A.drug_exposure_start_DATE AS DATE)
    and C.standard_concept = 'S'
),

attritionStatProcedures AS
(
      SELECT procedure_concept_id
      , count(distinct person_id) AS num_in_attrition
      , count(distinct person_id)/(select count(distinct person_id) from attritionProcedures) as perc_in_attrition
      FROM attritionProcedures
      GROUP BY procedure_concept_id
), 

retentionProcedures AS
(SELECT  A.person_id
      , B.procedure_DATE
      , B.procedure_concept_id
    FROM retentionCohort A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.procedure_occurrence`  B
    ON A.person_id = B.person_id
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept`  C
    ON B.procedure_concept_id = C.concept_id    
    WHERE B.procedure_DATE < CAST(A.drug_exposure_start_DATE AS DATE)
    AND C.standard_concept = 'S'
),

retentionStatProcedures AS
(
      SELECT procedure_concept_id
      , count(distinct person_id) AS num_in_retention
      , count(distinct person_id)/(select count(distinct person_id) from retentionProcedures) as perc_in_retention
      FROM retentionProcedures
      GROUP BY procedure_concept_id
),

frequentProcedures as 
(
      SELECT A.procedure_concept_id as concept_id
      , 'procedure' as feature_type
      , C.concept_name
      , A.num_in_attrition
      , A.perc_in_attrition
      , B.num_in_retention
      , B.perc_in_retention
      , (A.perc_in_attrition/B.perc_in_retention) as perc_in_attrition_TO_perc_in_retention
      FROM attritionStatProcedures A
      JOIN retentionStatProcedures B ON A.procedure_concept_id = B.procedure_concept_id
      JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` C ON A.procedure_concept_id = C.concept_id
      WHERE A.procedure_concept_id != 0
      AND A.perc_in_attrition >= 0.05
      AND B.perc_in_retention >= 0.05
      ORDER BY perc_in_attrition_TO_perc_in_retention DESC
),

attritionDrugs AS
(
  SELECT  A.person_id      
      , B.drug_exposure_start_DATE
      , B.drug_concept_id      
    FROM attritionCohort A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure`  B
    ON A.person_id = B.person_id
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept`  C
    ON B.drug_concept_id = C.concept_id    
    WHERE B.drug_exposure_start_DATE < CAST(A.drug_exposure_start_DATE AS DATE)
    and C.standard_concept = 'S'
),

attritionStatDrugs AS
(
      SELECT drug_concept_id
      , count(distinct person_id) AS num_in_attrition
      , count(distinct person_id)/(select count(distinct person_id) from attritionDrugs) as perc_in_attrition
      FROM attritionDrugs
      GROUP BY drug_concept_id
), 

retentionDrugs AS
(SELECT  A.person_id
      , B.drug_exposure_start_DATE
      , B.drug_concept_id
    FROM retentionCohort A
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure`  B
    ON A.person_id = B.person_id
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept`  C
    ON B.drug_concept_id = C.concept_id    
    WHERE B.drug_exposure_start_DATE < CAST(A.drug_exposure_start_DATE AS DATE)
    AND C.standard_concept = 'S'
),


retentionStatDrugs AS
(
      SELECT drug_concept_id
      , count(distinct person_id) AS num_in_retention
      , count(distinct person_id)/(select count(distinct person_id) from retentionDrugs) as perc_in_retention
      FROM retentionDrugs
      GROUP BY drug_concept_id
),

frequentDrugs as 
(
      SELECT A.drug_concept_id as concept_id
      , 'drug' as feature_type
      , C.concept_name
      , A.num_in_attrition
      , A.perc_in_attrition
      , B.num_in_retention
      , B.perc_in_retention
      , (A.perc_in_attrition/B.perc_in_retention) as perc_in_attrition_TO_perc_in_retention
      FROM attritionStatDrugs A
      JOIN retentionStatDrugs B ON A.drug_concept_id = B.drug_concept_id
      JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` C ON A.drug_concept_id = C.concept_id
      WHERE A.drug_concept_id != 0
      AND A.perc_in_attrition >= 0.05
      AND B.perc_in_retention >= 0.05
      ORDER BY perc_in_attrition_TO_perc_in_retention DESC
), 

frequent_features_all as
(
      select *
      from frequentConditions
      union all
      select *
      from frequentProcedures
      union all
      select *
      from frequentDrugs
)

select * 
from frequent_features_all 
order by perc_in_attrition_TO_perc_in_retention DESC






