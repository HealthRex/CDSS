# Antibiotic Susceptibility Inference

This directory contains the SQL scripts used for inferring antibiotic susceptibility in cases where the susceptibility is not reported or is null.

## How to Use

1. Run the `antibiotic_susceptibility_inference.sql` script to apply the susceptibility rules to your data. This script will update the `implied_susceptibility` field based on the specified rules for each organism-antibiotic pair where the susceptibility has not been reported.

2. After running the main script, execute `antibiotic_susceptibility_tests.sql` to verify that the data has been updated correctly. The test scripts will perform checks to ensure that:
   - Only rows with null or non-reported susceptibility have been updated with an implied susceptibility.
   - The correct number of rows are marked as 'Resistant' or 'Susceptible' for each organism-antibiotic pair as per the inference rules.
   - No rows with reported susceptibility have been altered by the inference process.

## Unit Tests

The unit tests are designed to verify the accuracy and integrity of the susceptibility inference process. They include checks for:

- Ensuring that rows with null susceptibility are correctly inferred and updated to 'Resistant' or 'Susceptible' where applicable, according to the rules set in the inference script.
- Confirming that rows with an existing susceptibility report are not modified by the inference script.

Please refer to the comments within `antibiotic_susceptibility_tests.sql` for detailed explanations on what each test case verifies and how it should be interpreted.

Remember to update the test data and scenarios in `antibiotic_susceptibility_tests.sql` to match the logic implemented in your main inference script, including handling of non-reported susceptibilities.
