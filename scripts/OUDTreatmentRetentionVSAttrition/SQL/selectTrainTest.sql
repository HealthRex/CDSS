with tempset as
(
  SELECT *
  FROM `mining-clinical-decisions.ivan_db.abstracted_data_v5_2022_08_10_label_threshold_180_obs_window_90_note_nlp_updated_2023-01-31` 
  where drug_era_start_date <= DATE '2020-11-07'
),

trainset as (
  SELECT *
  FROM `mining-clinical-decisions.ivan_db.abstracted_data_v5_2022_08_10_label_threshold_180_obs_window_90_note_nlp_updated_2023-01-31` 
  where person_id in (select distinct person_id from tempset)
),

testset as(
  SELECT *
  FROM `mining-clinical-decisions.ivan_db.abstracted_data_v5_2022_08_10_label_threshold_180_obs_window_90_note_nlp_updated_2023-01-31` 
  where person_id not in (select person_id from trainset)
)

select * from trainset