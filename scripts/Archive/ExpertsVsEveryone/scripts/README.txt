Code Pipeline:

Matching
1. /Users/jwang/Desktop/ClinicalDecisionMaker/scripts/SepsisICU/extractData_modified.py
From the stride database, extract potential covariates (lab tests, vital signs, demographic data)

2. /Users/jwang/Desktop/ClinicalDecisionMaker/scripts/SepsisICU/formatData.py
Format the *.tab files that are outputted by extractData into a single datatable

3. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/test/extract_age.py:
extracts age data out of the stride database

4. /Users/jwang/Desktop/Patient Matching/clean_data.py
Reformat the single datatable outputted by formatData to include normalized_patient_id (since R modifies long numbers), age, income level, etc.

5. /Users/jwang/Desktop/Patient Matching/matching.Rmd
Cleans data, conducts propensity scoring using logistic regression, conducts patient matching, and assesses pre- and post-matching statistical differences (computes P-values); also prints out the matched normalized_ids for expert and everyone cohorts

6. /Users/jwang/Desktop/Patient Matching/remap_ids.py
Takes the output of matching.Rmd and maps the normalized ids to the original patient ids found in the database

Training
1. createdb [name]
Create a new empty database

2. psql -f medinfo/db/definition/cpoeStats.sql -U jwang198 medinfo_*
Load in the schema of medinfo

3. /Users/jwang/Desktop/RawData/restoreCPOETables_*.sh
Loads in medinfo data

4. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/cpoe/ResetModel.py
Clears out the clinical_item_assocations and residual data so that the new database is fresh for training

5. Set the database name to clean in /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/Env.py

6. /Users/jwang/Desktop/Results/stratify.py
Separate patient ids into manageable chunks (i.e. files of 750 patient ids each)

7. /Users/jwang/Desktop/Results/train_associations.sh
Apply AssociationAnalysis to each patient id file, training the specified database in Env.py

8. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/test/get_predictions.py
Using ItemRecommender.py, generate predictions on the trained database for a list of diagnoses; output predictions with associated statistics (PPV, OR, etc.)

Figures
1. /Users/jwang/Desktop/Figures/matching_parse.py
Take the copy and pasted output from the matching.RMD pre- and post-matching analysis and format as a presentable csv table

2. /Users/jwang/Desktop/Results/generate_plot_input_part1.py
First part of generating an input file that can be used for the ROCPlot and PrecisionRecallPlot
Outer join on expert and everyone-predictions to create a unified score file

3. /Users/jwang/Desktop/Results/generate_plot_input_part2.py
Adds two columns: orderset (binary) and reference outcome (binary) to the unified score column

4. /Users/jwang/Desktop/Results/generate_roc_plots.sh
Generate ROC plots for matched/unmatched and expert/everyone

5. /Users/jwang/Desktop/Results/generate_pr_curves.sh
Generate Precision-Recall curves for matched/unmatched and expert/everyone

6. /Users/jwang/Desktop/Results/generate_rbo_input.py
Generates formatted input file for use in rank_bias_overlap.sh

7. /Users/jwang/Desktop/Results/rank_bias_overlap.sh
Compute rank bias overlap between expert and everyone prediction lists

Miscellaneous
1. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/test/extract_unmatched_patient_cohorts.py
Identify patients that fall under either expert (“Pamf”) or everyone (“Med Univ”) cohorts

2. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/test/extract_diagnosis_codes.py
Identify diagnosis ids in order of most common to least common

3. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/test/get_references_or_ordersets.py
Extract reference lists or order sets from medinfo database to use for evaluation

4. /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/test/number_clinical_items.py
Count number of clinical items associated with a list of patient ids
