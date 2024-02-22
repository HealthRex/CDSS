
select distinct 
      F.person_id
                  , PARSE_DATE('%Y-%m-%d', F.drug_exposure_start_DATE) as drug_exposure_start_DATE
      , DATE_DIFF(PARSE_DATE('%Y-%m-%d', F.drug_exposure_start_DATE) , extract(date from P.birth_DATETIME), year) as age_from_exposure_start_date
      
      , case
            when P.gender_concept_id = 8532 then 1
            else 0
            end
      as gender_8532
      , case
            when P.gender_concept_id = 8507 then 1
            else 0
            end
      as gender_8507
      
      , case
            when P.race_concept_id = 2000039212 then 1
            else 0
            end
      as race_2000039212
      , case
            when P.race_concept_id = 8515 then 1
            else 0
            end
      as race_8515            
      , case
            when P.race_concept_id = 2000039205 then 1
            else 0
            end
      as race_2000039205
      , case
            when P.race_concept_id = 8527 then 1
            else 0
            end
      as race_8527
      , case
            when P.race_concept_id = 2000039200 then 1
            else 0
            end
      as race_2000039200
      , case
            when P.race_concept_id = 2000039207 then 1
            else 0
            end
      as race_2000039207
      , case
            when P.race_concept_id = 8516 then 1
            else 0
            end
      as race_8516
      , case
            when P.race_concept_id = 8657 then 1
            else 0
            end
      as race_8657
      , case
            when P.race_concept_id = 8557 then 1
            else 0
            end
      as race_8557
      , case
            when P.race_concept_id = 2000039206 then 1
            else 0
            end
      as race_2000039206
      , case
            when P.race_concept_id = 2000039211 then 1
            else 0
            end
      as race_2000039211
      , case
            when P.race_concept_id = 2000039201 then 1
            else 0
            end
      as race_2000039201                                                                        
from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.drug_eras` F
join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.person` P on F.person_id = P.person_id
