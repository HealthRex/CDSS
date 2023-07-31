-- cohort_v2_records_conditions
select person_id, drug_exposure_start_DATE, feature_concept_id
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_records` where feature_type = 'condition'

--cohort_v2_distinct_condition_ids
select distinct cast(string_field_1 as INT64) as concept_id
from  `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan`
where string_field_2 = 'diagnosis'

-- cohort_v2_feature_matrix_conditions
execute immediate (select '''
select * from som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_records_conditions
pivot (count(*) condition for feature_concept_id in (''' || string_agg('' || concept_id, ',' order by concept_id) || "))"
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_distinct_condition_ids`
)


--cohort_v2_records_drugs
select person_id, drug_exposure_start_DATE, feature_concept_id
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_records` where feature_type = 'drug'

--cohort_v2_distinct_drug_ids
select distinct cast(string_field_1 as INT64) as concept_id
from  `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan`
where string_field_2 = 'drug'

--cohort_v2_feature_matrix_drugs
execute immediate (select '''
select * from som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_records_drugs
pivot (count(*) drug for feature_concept_id in (''' || string_agg('' || concept_id, ',' order by concept_id) || "))"
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_distinct_drug_ids`
)


--cohort_v2_records_procedures
select person_id, drug_exposure_start_DATE, feature_concept_id
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_records` where feature_type = 'procedure'

--cohort_v2_distinct_procedure_ids
select distinct cast(string_field_1 as INT64) as concept_id
from  `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan`
where string_field_2 = 'procedure'

--cohort_v2_feature_matrix_procedures
execute immediate (select '''
select * from som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_records_procedures
pivot (count(*) procedure for feature_concept_id in (''' || string_agg('' || concept_id, ',' order by concept_id) || "))"
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_distinct_procedure_ids`
)


select F.*
      , DATE_DIFF(F.drug_exposure_start_DATE , extract(date from P.birth_DATETIME), year) as age_from_exposure_start_date
      
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
from `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_drug_eras` F
join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_2022_08_10.person` P on F.person_id = P.person_id


