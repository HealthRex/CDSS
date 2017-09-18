Code Pipeline:

Matching
1. extractData_modified.py
From the stride database, extract potential covariates (lab tests, vital signs, demographic data)

2. /Users/jwang/Desktop/ClinicalDecisionMaker/scripts/SepsisICU/formatData.py
Format the *.tab files that are outputted by extractData into a single datatable

3. extract_age.py
extracts age data out of the stride database

4. clean_data.py
Reformat the single datatable outputted by formatData to include normalized_patient_id (since R modifies long numbers), age, income level, etc.

5. matching.Rmd
Cleans data, conducts propensity scoring using logistic regression, conducts patient matching, and assesses pre- and post-matching statistical differences (computes P-values); also prints out the matched normalized_ids for expert and everyone cohorts

6. remap_ids.py
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
*Make sure to set the database name in /Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db/Env.py

5. stratify.py
Separate patient ids into manageable chunks (i.e. files of 750 patient ids each)

6. run_association.sh
Apply AssociationAnalysis to each patient id file, training the specified database in Env.py

7. get_predictions.py
Using ItemRecommender.py, generate predictions on the trained database for a list of diagnoses; output predictions with associated statistics (PPV, OR, etc.)

Figures
1. matching_parse.py
Take the copy and pasted output from the matching.RMD pre- and post-matching analysis and format as a presentable csv table

2. plot_input.py
Generate an input file that can be used for the ROCPlot and PrecisionRecallPlot based on which predictions are found in the reference list

3. generate_plots.sh
Generate ROC and Precision-Recall curves for matched/unmatched and expert/everyone

Miscellaneous
1. extract_unmatched_patient_cohorts.py
Identify patients that fall under either expert (“Pamf”) or everyone (“Med Univ”) cohorts

2. extract_diagnosis_codes.py
Identify diagnosis ids in order of most common to least common
