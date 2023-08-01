import pdb
import sys
import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
from datetime import datetime, timedelta
import csv

# Hyper-parameters
train_test_threshold_date = '2021-01-01'
drug_exposure_max_gap = 30

def form_drug_eras(exposures
				, max_gap):
	'''
	This function combine drug exposures and create a drug era
	'''
	drug_eras = []
	exposures_grouped = exposures.groupby(by='person_id')
	for group_name, group_data in exposures_grouped:		
		combined_exposures = []
		start = group_data.iloc[0]['drug_exposure_start_DATE']
		end = group_data.iloc[0]['drug_exposure_end_DATE']
		trt_dur = (end - start).days
		current_combined_exposures = {'id': group_name, 's_date': start, 'e_date': end, 'trt_dur': trt_dur}
		i=1
		while i < len(group_data):
			# If current start time is less than 30 days from previous end date, combine the exposures
			if (group_data.iloc[i]['drug_exposure_start_DATE'] <= end + timedelta(days=max_gap)):
				end = max(end, group_data.iloc[i]['drug_exposure_end_DATE'])  
				trt_dur = (end - start).days
				current_combined_exposures['e_date'] = end
				current_combined_exposures['trt_dur'] = trt_dur
			else:
				# current exposure if at least 30 days apart from previous exposure
				combined_exposures.append([group_name, current_combined_exposures['s_date'], current_combined_exposures['e_date'], current_combined_exposures['trt_dur']])								
				start = group_data.iloc[i]['drug_exposure_start_DATE']
				end = group_data.iloc[i]['drug_exposure_end_DATE']
				trt_dur = (end - start).days
				current_combined_exposures['s_date'] = start
				current_combined_exposures['e_date'] = end
				current_combined_exposures['trt_dur'] = trt_dur				
			i +=1
		
		combined_exposures.append([group_name, current_combined_exposures['s_date'], current_combined_exposures['e_date'], current_combined_exposures['trt_dur']])
		# pdb.set_trace()
		drug_eras.extend(combined_exposures)
	return drug_eras

# pdb.set_trace()

# Connect to the database
client = bigquery.Client('som-nero-phi-jonc101');
conn = dbapi.connect(client);

project_id = 'som-nero-phi-jonc101'
dataset_id = 'proj_nidactn_multisite_sf'

query_string = '''
  	SELECT distinct B.concept_name , A.*
  	FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure` A
  	JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` B on A.drug_concept_id = B.concept_id
  	where B.concept_name like '%buprenorphine%naloxone%'
  	order by person_id, A.drug_exposure_start_date
'''
# Read all drug BUP exposures
exposures = pd.read_sql_query(query_string, conn)
exposures = exposures.sort_values(by=['person_id', 'drug_exposure_start_DATE'])

# Form drug eras by combining drug exposures with less than 30 days gap
drug_eras = form_drug_eras(exposures, drug_exposure_max_gap)
drug_eras_df = pd.DataFrame(data=drug_eras, columns=['person_id', 'drug_exposure_start_DATE', 'drug_exposure_end_DATE', 'TreatmentDuration'])
drug_eras_df['drug_exposure_start_DATE'] = drug_eras_df['drug_exposure_start_DATE'].astype(str).str.encode('utf-8')
drug_eras_df['drug_exposure_end_DATE'] = drug_eras_df['drug_exposure_end_DATE'].astype(str).str.encode('utf-8')

# Uploda drug eras into BigQuery
drug_eras_df.to_gbq(destination_table=f"{project_id}.{dataset_id}.{'drug_eras'}", project_id=project_id, if_exists="replace")

# Extract medical records for the cohort
extract_records_query = "".join([line for line in open("SQL/extractRecords.sql", "r")])
records = pd.read_sql_query(extract_records_query, conn)


# Create a pivot table to get multi-hot encoding of 'feature_concept_id'
pivot_df = records.pivot_table(index=['person_id', 'drug_exposure_start_DATE'], 
                           columns='feature_concept_id', 
                           aggfunc='size', 
                           fill_value=0)

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

# pdb.set_trace()
# Devide to train and test set
trainset = feature_matrix_with_demogs[feature_matrix_with_demogs['drug_exposure_start_DATE'] < pd.to_datetime(train_test_threshold_date)]
testset = feature_matrix_with_demogs[feature_matrix_with_demogs['drug_exposure_start_DATE'] >= pd.to_datetime(train_test_threshold_date)]

overlapping_rows_inTest = testset[testset['person_id'].isin(trainset['person_id'])]
testset = testset[~testset['person_id'].isin(trainset['person_id'])]
trainset = pd.concat([trainset, overlapping_rows_inTest])
trainset.reset_index(drop=True, inplace=True)

overlapping_data = trainset[trainset['person_id'].isin(testset['person_id'])]['person_id'].unique()

# Write train and test sets to disk
trainset.to_csv('feature_matrix/train_set.csv', index=False)
testset.to_csv('feature_matrix/test_set.csv', index=False)

