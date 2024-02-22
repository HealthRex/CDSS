-- table 1 for mci is
with fetureMatrix as(
  select * 
  from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.train_set_sep4_2023`
  union all
  select *
  from `som-nero-phi-jonc101.proj_NIDACTN_SF_V2.test_set_sep4_2023`
),

-- select count(*) 
-- from fetureMatrix
-- where TreatmentDuration >=2
-- and TreatmentDuration >= 180

retention_person_demog as
(
select person_id
      , age_from_exposure_start_date as age_at_study_entry
      , gender_8507
      , gender_8532
      , if (race_2000039200 > 0, 1, 0) as race_2000039200
      , if (race_2000039201 > 0, 1, 0) as race_2000039201
      , if (race_2000039205 > 0, 1, 0) as race_2000039205
      , if (race_2000039206 > 0, 1, 0) as race_2000039206
      , if (race_2000039207 > 0, 1, 0) as race_2000039207
      , if (race_2000039211 > 0, 1, 0) as race_2000039211
      , if (race_2000039212 > 0, 1, 0) as race_2000039212
      , if (race_8515 > 0, 1, 0) as race_8515
      , if (race_8516 > 0, 1, 0) as race_8516
      , if (race_8527 > 0, 1, 0) as race_8527
      , if (race_8557 > 0, 1, 0) as race_8557
      , if (race_8657 > 0, 1, 0) as race_8657
from fetureMatrix
where TreatmentDuration >= 180
and age_from_exposure_start_date is not null
and (gender_8507 != 0 or gender_8532 !=0)
and (race_2000039200 != 0 or race_2000039201 != 0 or race_2000039205 != 0 or race_2000039206 != 0 or race_2000039207 != 0 or race_2000039211 != 0 or race_2000039212 != 0 or race_8515 != 0 or race_8516 != 0 or race_8527 != 0 or race_8557 != 0 or race_8657 != 0)
),

retention_demog_stats as
(
select 
        avg(age_at_study_entry) as age_at_study_entry_avg
      , min(age_at_study_entry) as age_at_study_entry_min
      , max(age_at_study_entry) as age_at_study_entry_max
      , APPROX_QUANTILES(age_at_study_entry, 100)[OFFSET(25)] as age_at_study_entry_25percent
      , APPROX_QUANTILES(age_at_study_entry, 100)[OFFSET(50)] as age_at_study_entry_50percent
      , APPROX_QUANTILES(age_at_study_entry, 100)[OFFSET(75)] as age_at_study_entry_75percent
      , (APPROX_QUANTILES(age_at_study_entry, 100)[OFFSET(75)]) - (APPROX_QUANTILES(age_at_study_entry, 100)[OFFSET(25)]) as IQR
      , (select count(*) from retention_person_demog where gender_8507 = 1) as num_gender_8507
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where gender_8507 = 1) as perc_gender_8507
      , (select count(*) from retention_person_demog where gender_8532 = 1) as num_gender_8532
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where gender_8532 = 1) as perc_gender_8532      

      , (select count(*) from retention_person_demog where   race_2000039200 = 1) as num_race_2000039200
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039200 = 1) as perc_race_2000039200

      , (select count(*) from retention_person_demog where   race_2000039201 = 1) as num_race_2000039201
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039201 = 1) as perc_race_2000039201

      , (select count(*) from retention_person_demog where   race_2000039205 = 1) as num_race_2000039205
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039205 = 1) as perc_race_2000039205

      , (select count(*) from retention_person_demog where   race_2000039206 = 1) as num_race_2000039206
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039206 = 1) as perc_race_2000039206

      , (select count(*) from retention_person_demog where   race_2000039207 = 1) as num_race_2000039207
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039207 = 1) as perc_race_2000039207

      , (select count(*) from retention_person_demog where   race_2000039211 = 1) as num_race_2000039211
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039211 = 1) as perc_race_2000039211

      , (select count(*) from retention_person_demog where   race_2000039212 = 1) as num_race_2000039212
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_2000039212 = 1) as perc_race_2000039212

      , (select count(*) from retention_person_demog where   race_8515 = 1) as num_race_8515
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_8515 = 1) as perc_race_8515

      , (select count(*) from retention_person_demog where   race_8516 = 1) as num_race_8516
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_8516 = 1) as perc_race_8516

      , (select count(*) from retention_person_demog where   race_8527 = 1) as num_race_8527
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_8527 = 1) as perc_race_8527

      , (select count(*) from retention_person_demog where   race_8557 = 1) as num_race_8557
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_8557 = 1) as perc_race_8557

      , (select count(*) from retention_person_demog where   race_8657 = 1) as num_race_8657
      , (select count(*)/(select count(*) from retention_person_demog) from retention_person_demog where race_8657 = 1) as perc_race_8657

from retention_person_demog
)

select 'retention' as class
      , A.*
from retention_demog_stats A

