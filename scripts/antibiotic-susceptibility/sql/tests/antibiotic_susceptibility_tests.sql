-- Create the test table with the same schema as the production table
CREATE OR REPLACE TABLE `mining-clinical-decisions.fateme_db.implied_suscept_test` (
  anon_id STRING,
  order_proc_id_coded INT64,
  organism STRING,
  antibiotic STRING,
  susceptibility STRING,
  implied_susceptibility STRING
);

-- Arrange: Set up test data for reported susceptibility
INSERT INTO `mining-clinical-decisions.fateme_db.implied_suscept_test` (anon_id, order_proc_id_coded, organism, antibiotic, susceptibility)
VALUES ('test_reported', 1, 'Pseudomonas aeruginosa', 'Cefazolin', 'Susceptible');

-- Arrange: Set up test data for non-reported susceptibility
INSERT INTO `mining-clinical-decisions.fateme_db.implied_suscept_test` (anon_id, order_proc_id_coded, organism, antibiotic, susceptibility)
VALUES ('test_non_reported', 2, 'Pseudomonas aeruginosa', 'Cefazolin', NULL);

-- Act: Run the update query on the test data for non-reported susceptibility
UPDATE `mining-clinical-decisions.fateme_db.implied_suscept_test`
SET implied_susceptibility = 'Resistant'
WHERE UPPER(organism) LIKE '%PSEUDOMONAS%'
AND UPPER(antibiotic) = 'CEFAZOLIN'
AND (susceptibility IS NULL OR susceptibility = '');

-- Assert: Check that the update happened as expected for non-reported susceptibility
SELECT implied_susceptibility
FROM `mining-clinical-decisions.fateme_db.implied_suscept_test`
WHERE anon_id = 'test_non_reported' AND order_proc_id_coded = 2;

-- The test passes if the selected value for non-reported susceptibility is 'Resistant'

-- Assert: Check that the update did not affect reported susceptibility
SELECT implied_susceptibility
FROM `mining-clinical-decisions.fateme_db.implied_suscept_test`
WHERE anon_id = 'test_reported' AND order_proc_id_coded = 1;

-- The test passes if the selected value for reported susceptibility remains NULL
