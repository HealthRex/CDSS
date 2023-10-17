import pdb
import sys
import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
from datetime import datetime, timedelta
import csv
import models.ml_models as cl_ml
import pickle
from datetime import date

pdb.set_trace()

# ==== Statics including external model paths and other hyper-parameters
external_trained_lr_path = 'saved_classical_ml_models/external_lr_model.pkl'
external_trained_rf_path = 'saved_classical_ml_models/external_rf_model.pkl'
external_trained_xgb_path = 'saved_classical_ml_models/external_xgb_model.pkl'
external_test_data_path = 'feature_matrix/external_test_set.csv'
external_retention_cut_off = 180
external_non_feature_list = ['person_id', 'drug_exposure_start_DATE', 'TreatmentDuration', 'outcome']
external_min_treatment_duration = 2

# ethnicity_Hispanic_or_Latino
# ethnicity_Not_Reported
new_column_name = {'age_from_exposure_start_date': 'age_at_oud_dx'
					, 'gender_8532': 'gender_FEMALE'
					, 'race_8516': 'race_Black_or_African_American'
					, 'race_2000039200': 'race_Not_Reported'
					, 'race_2000039205': 'race_Other_race'}

test_date_th = '2017-01-01'
# ====

# Connect to the database
client = bigquery.Client('som-nero-phi-jonc101');
conn = dbapi.connect(client);
project_id = 'som-nero-phi-jonc101'
dataset_id = 'proj_nidactn_multisite_sf'


# Extract medical records for the external cohort.
# The SQL query first convert to standard concept IDs and then extract standard IDs for the cohort
extract_records_query = "".join([line for line in open("SQL/externalValidation_extractRecords.sql", "r")])
records = pd.read_sql_query(extract_records_query, conn)


# Create a pivot table to get multi-hot encoding of 'feature_concept_id'
pivot_df = records.pivot_table(index=['person_id'
							, 'drug_exposure_start_DATE']
							, columns='feature_concept_id'
							, aggfunc='size'
							, fill_value=0)

# Reset index to get 'person_id' and 'drug_exposure_start_DATE' as columns
pivot_df = pivot_df.reset_index()


# Merge columns to get 'TreatmentDuration' in the final result
feature_matrix = pd.merge(pivot_df, records[['person_id', 'drug_exposure_start_DATE', 'TreatmentDuration']].drop_duplicates(), 
                     on=['person_id', 'drug_exposure_start_DATE'], 
                     how='left')

# Extract demographics
extract_demogs_query = "".join([line for line in open("SQL/extractDemogs.sql", "r")])
demogs = pd.read_sql_query(extract_demogs_query, conn)

feature_matrix_with_demogs = feature_matrix.merge(demogs, on= ['person_id', 'drug_exposure_start_DATE'], how='left')
feature_matrix_with_demogs.rename(columns=new_column_name, inplace=True)


pdb.set_trace()
mapped_to_external_columns = [col.split('_')[1] if col.split('_')[0] == 'predictor' else col for col in feature_matrix_with_demogs.columns]

feature_matrix_with_demogs.columns = mapped_to_external_columns

# duplicated_columns = feature_matrix_with_demogs.columns[feature_matrix_with_demogs.columns.duplicated()]

randomCV_lr = pickle.load(open(external_trained_lr_path, 'rb'))    
best_model_lr = randomCV_lr.best_estimator_   
external_model_feature_names = best_model_lr.feature_names_in_ 


shared_columns = [col for col in external_model_feature_names if col in feature_matrix_with_demogs.columns]

missing_columns = [col for col in external_model_feature_names if col not in feature_matrix_with_demogs.columns]

# Write the list of strings to the .csv file
with open('Random Files/missing_columns.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for string in missing_columns:
        csv_writer.writerow([string])

pdb.set_trace()

for col in missing_columns:
    feature_matrix_with_demogs[col] = 0

pdb.set_trace()

# feature_matrix_with_demogs.columns = feature_matrix_with_demogs.columns.astype(str)
feature_matrix_with_demogs_clean = feature_matrix_with_demogs[external_model_feature_names]


duplicated_columns = feature_matrix_with_demogs_clean.columns[feature_matrix_with_demogs_clean.columns.duplicated()]


feature_matrix_with_demogs_clean = feature_matrix_with_demogs_clean.loc[:, ~feature_matrix_with_demogs_clean.columns.duplicated()]

feature_matrix_with_demogs_clean['person_id'] = feature_matrix_with_demogs['person_id']
feature_matrix_with_demogs_clean['drug_exposure_start_DATE'] = feature_matrix_with_demogs['drug_exposure_start_DATE']
feature_matrix_with_demogs_clean['TreatmentDuration'] = feature_matrix_with_demogs['TreatmentDuration']
# feature_matrix_with_demogs_clean['outcome'] = feature_matrix_with_demogs['outcome']

feature_matrix_with_demogs_clean = feature_matrix_with_demogs_clean.loc[feature_matrix_with_demogs_clean['drug_exposure_start_DATE'] >= pd.to_datetime(test_date_th)]




feature_matrix_with_demogs_columns = feature_matrix_with_demogs.columns.values.tolist()

# feature_matrix_with_demogs_columns = 


external_feature_query = " select distinct * from `som-nero-phi-jonc101.proj_nidactn_multisite_sf.holmusk_significant_variables`"
external_site_features_standard = pd.read_sql_query(external_feature_query, conn)



# Read and standardize variables/features that the external site has used to train their models.
external_feature_query = '''
  		select distinct 
        	A.Variable_type
        	, A.concept_id as holmuskConceptID
        	, B.concept_id_2 as standardizedConceptID
  		from `som-nero-phi-jonc101.proj_nidactn_multisite_sf.holmusk_significant_variables` A
  		join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept_relationship` B
  		on A.concept_id = B.concept_id_1
  		where B.relationship_id = 'Maps to' 
  '''
# external_site_features_standard includes a mapping between external concept IDs to equivalent standard concept IDs
external_site_features_standard = pd.read_sql_query(external_feature_query, conn)


# Find all variables that exist in external site dictionary but missing in our data
missing_variables = external_site_features_standard[~external_site_features_standard['standardizedConceptID'].isin(pivot_df.columns.tolist())]['standardizedConceptID'].tolist()

# Add missing variables to our data. Set the values to 0
for var in missing_variables:
    pivot_df[var] = 0

pdb.set_trace()
non_mapable_features = []
# Iterate over feature matrix columns
for i in range(feature_matrix_with_demogs.shape[1]):
	current_standard_feature = feature_matrix_with_demogs.columns.values[i]
	# If the feature name exist in the dictionary, map it back to Holmusk feature name
	if  current_standard_feature in external_site_features_standard["standardizedConceptID"].values.tolist():
		map_temp = external_site_features_standard[external_site_features_standard['standardizedConceptID']==current_standard_feature]
		if len(map_temp)==1:
			# pdb.set_trace()
			# print('Warning: there are multiple matching')
			feature_matrix_with_demogs.columns.values[i] = map_temp['holmuskConceptID'].iloc[0]
	
	else:
		non_mapable_features.append(current_standard_feature)

pdb.set_trace()

randomCV_lr = pickle.load(open(external_trained_lr_path, 'rb'))    
best_model_lr = randomCV_lr.best_estimator_   
external_model_feature_names = best_model_lr.feature_names_in_ 

feature_matrix_column_names = [str(x) for x in feature_matrix_with_demogs.columns.values.tolist()]

#	Convert external model feature names to standard concept IDs
filtered_columns = [col for col in external_model_feature_names if col in feature_matrix_column_names]

missing_columns = [col for col in external_model_feature_names if col not in feature_matrix_column_names]

for col in missing_columns:
    feature_matrix_with_demogs[col] = 0

pdb.set_trace()
feature_matrix_with_demogs.columns = feature_matrix_with_demogs.columns.astype(str)
feature_matrix_with_demogs_clean = feature_matrix_with_demogs[external_model_feature_names]
feature_matrix_with_demogs_clean = feature_matrix_with_demogs_clean.loc[:, ~feature_matrix_with_demogs_clean.columns.duplicated()]

feature_matrix_with_demogs_clean['person_id'] = feature_matrix_with_demogs['person_id']
feature_matrix_with_demogs_clean['drug_exposure_start_DATE'] = feature_matrix_with_demogs['drug_exposure_start_DATE']
feature_matrix_with_demogs_clean['TreatmentDuration'] = feature_matrix_with_demogs['TreatmentDuration']
# feature_matrix_with_demogs_clean['outcome'] = feature_matrix_with_demogs['outcome']

feature_matrix_with_demogs_clean = feature_matrix_with_demogs_clean.loc[feature_matrix_with_demogs_clean['drug_exposure_start_DATE'] >= pd.to_datetime(test_date_th)]


# Save feature matrix
feature_matrix_with_demogs_clean.to_csv(external_test_data_path, index=False)



# Load external model
cl_ml.test_with_imb(external_trained_rf_path
                    , external_trained_lr_path
                    , external_trained_xgb_path
                    , external_test_data_path
                    , external_retention_cut_off
                    , external_non_feature_list
                    , external_min_treatment_duration
                    , 'external_testing'
                    )
