import pdb
import sys
import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
from datetime import datetime, timedelta
import csv

# pdb.set_trace()
train_data_date = pd.to_datetime('2021-01-01').date()

client = bigquery.Client('som-nero-phi-jonc101');
conn = dbapi.connect(client);

query_string = '''SELECT * FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_feature_matrix_conditions`'''
feature_matrix_conditions = pd.read_sql_query(query_string, conn)

query_string = '''SELECT * FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_feature_matrix_drugs`'''
feature_matrix_drugs = pd.read_sql_query(query_string, conn)

query_string = '''SELECT * FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_feature_matrix_procedures`'''
feature_matrix_procedures = pd.read_sql_query(query_string, conn)

query_string = '''SELECT * FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.cohort_v2_demographics`'''
feature_matrix_demographics = pd.read_sql_query(query_string, conn)
feature_matrix_demographics = feature_matrix_demographics.drop(['drug_exposure_end_DATE'], axis=1)

feature_matrix = feature_matrix_conditions.merge(feature_matrix_drugs, on=['person_id', 'drug_exposure_start_DATE'], how='outer').merge(feature_matrix_procedures, on=['person_id', 'drug_exposure_start_DATE'], how='outer')

feature_matrix = feature_matrix.merge(feature_matrix_demographics, on=['person_id', 'drug_exposure_start_DATE'], how='left')

data_train = feature_matrix[feature_matrix['drug_exposure_start_DATE'] < train_data_date]
data_test = feature_matrix[feature_matrix['drug_exposure_start_DATE'] >= train_data_date]

for id_value in data_train['person_id']:
    matching_rows = data_test[data_test['person_id'] == id_value]
    data_test = data_test.drop(matching_rows.index)
    data_train = data_train.append(matching_rows)

# np.intersect1d(data_train['person_id'], data_test['person_id'])
# pdb.set_trace()
data_train = data_train.reset_index(drop=True)
data_train = data_train.fillna(0)
data_test = data_test.reset_index(drop=True)
data_test = data_test.fillna(0)

data_train.to_csv('feature_matrix/train_set.csv', index=False)

data_test.to_csv('feature_matrix/test_set.csv', index=False)

