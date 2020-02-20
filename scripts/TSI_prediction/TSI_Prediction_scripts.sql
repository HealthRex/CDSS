TSI Prediction


--
-- Count of labs with TSI/TRAB
SELECT lab_name, count(lab_name) FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` 
      WHERE lab_name IN ('Thyroid-Stimulating Immunoglob, Serum', 'Thyroid Stim Immunoglobulin', 'Thyroid Stimulating Immunoglobulins', 'Thyroid Stim Immuno', 'Thyrotropin Receptor Ab, Serum', 'TSH Receptor Ab', 'Thyrotropin Receptor Ab', 'TSH Receptor Antibody' )
     -- AND lab_name NOT IN ('Thyroid Peroxidase Abs', 'Thyroid Peroxidase (TPO) Antibody', 'Anti-Thyroid Peroxidase IgG', 'Thyroid Ab') -- antibodies related to hypothyroidism
GROUP BY lab_name 

-- 
-- Patients with TSI/TRAB
-- TRAB max is 1.75, TSI cutoff is 1.3/139. "High" means high but "Null" doesn't mean in range necessarily
-- TimeToResult is the difference between when the test was ordered and when it resulted
-- Average time to result is 4.33 days
SELECT rit_uid, pat_enc_csn_id_coded, lab_name, ord_num_value, reference_low, reference_high, result_in_range_yn, result_flag, ordering_mode, taken_time_jittered, result_time_jittered, DATE_DIFF(DATE(result_time_jittered), DATE(taken_time_jittered), DAY) as TimeToResult  FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` 
      WHERE lab_name IN ('Thyroid-Stimulating Immunoglob, Serum', 'Thyroid Stim Immunoglobulin', 'Thyroid Stimulating Immunoglobulins', 'Thyroid Stim Immuno', 'Thyrotropin Receptor Ab, Serum', 'TSH Receptor Ab', 'Thyrotropin Receptor Ab', 'TSH Receptor Antibody' )
      AND ord_num_value < 9999999

