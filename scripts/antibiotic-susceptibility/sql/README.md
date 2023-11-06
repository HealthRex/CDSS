# Antibiotic Susceptibility Inference

This directory contains the SQL scripts used for inferring antibiotic susceptibility.

## How to Use

Run the `antibiotic_susceptibility_inference.sql` script to apply the susceptibility rules to your data.

After running the main script, execute `antibiotic_susceptibility_tests.sql` to verify that the data has been updated correctly. The tests will check for the correct number of rows updated for each condition and ensure that no unexpected changes have been made.

## Unit Tests

The unit tests are designed to verify that:
- The correct number of rows are marked as 'Resistant' for each organism-antibiotic pair.
- No rows are incorrectly updated.


Please refer to the comments within `antibiotic_susceptibility_tests.sql` for details on what each test verifies.
