-- Create the test table with the same schema as the production table
CREATE OR REPLACE TABLE `mining-clinical-decisions.fateme_db.implied_suscept_test` (
  anon_id STRING,
  order_proc_id_coded INT64,
  organism STRING,
  antibiotic STRING,
  susceptibility STRING,
  implied_susceptibility STRING
);

-- Arrange: Set up test data
INSERT INTO `mining-clinical-decisions.fateme_db.implied_suscept_test` (anon_id, order_proc_id_coded, organism, antibiotic, susceptibility)
VALUES ('test_anon', 1, 'Pseudomonas aeruginosa', 'Cefazolin', 'Susceptible');

-- Act: Run the update query on the test data
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept_test`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%'
AND UPPER(antibiotic) = 'CEFAZOLIN';

-- Assert: Check that the update happened as expected
SELECT implied_susceptibility
FROM `mining-clinical-decisions.fateme_db.implied_suscept_test`
WHERE anon_id = 'test_anon' AND order_proc_id_coded = 1;

-- The test passes if the selected value is 'Resistant'
