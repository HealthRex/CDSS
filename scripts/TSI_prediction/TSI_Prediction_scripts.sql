TSI Prediction


--
-- Count of labs with TSI/TRAB
SELECT lab_name, count(lab_name) FROM `som-nero-phi-jonc101.starr_datalake2018.lab_result` 
      WHERE lab_name IN ('Thyroid-Stimulating Immunoglob, Serum', 'Thyroid Stim Immunoglobulin', 'Thyroid Stimulating Immunoglobulins', 'Thyroid Stim Immuno', 'Thyrotropin Receptor Ab, Serum', 'TSH Receptor Ab', 'Thyrotropin Receptor Ab', 'TSH Receptor Antibody' )
     -- AND lab_name NOT IN ('Thyroid Peroxidase Abs', 'Thyroid Peroxidase (TPO) Antibody', 'Anti-Thyroid Peroxidase IgG', 'Thyroid Ab')
GROUP BY lab_name 