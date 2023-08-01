import pdb
import sys
import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
from datetime import datetime, timedelta
import csv



test_person_id = 30959303
data_train = pd.read_csv('feature_matrix/train_set.csv') 
data_test = pd.read_csv('feature_matrix/test_set.csv')

if len(data_train[data_train['person_id']==test_person_id])>0:
  data_point = data_train[data_train['person_id']==test_person_id]
elif len(data_test[data_test['person_id']==test_person_id])>0:
  data_point = data_test[data_test['person_id']==test_person_id]
else:
  print('data point doesnt exist')
  pdb.set_trace()


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

# Check if train and test overlap
overlap = any(value in data_train.person_id.unique() for value in data_test.person_id.unique())

if overlap == True:
  print('Warning: train and test sets have overlapping cases.')
  pdb.set_trace

client = bigquery.Client('som-nero-phi-jonc101');
conn = dbapi.connect(client);

query_string = '''
  SELECT distinct B.concept_name , A.*
  FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure` A
  JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` B on A.drug_concept_id = B.concept_id
  where B.concept_name like '%buprenorphine%naloxone%'
  and A.person_id = ''' +str(test_person_id)+ '''  order by person_id, A.drug_exposure_start_date
'''

exposures = pd.read_sql_query(query_string, conn)
exposures.to_csv('Sanity Check/'+str(test_person_id)+'_exposures.csv', index=False)

drug_eras = form_drug_eras(exposures, 30)
drug_eras_df = pd.DataFrame(data=drug_eras, columns=['person_id', 'drug_exposure_start_DATE', 'drug_exposure_end_DATE', 'TreatmentDuration'])
drug_eras_df.to_csv('Sanity Check/'+str(test_person_id)+'_eras.csv', index=False)

# Extract conditions
condition_features = pd.read_sql_query("SELECT distinct cast(string_field_1 as INT64) as feature_concept_id FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'diagnosis'", conn)
common_features_conds = list(set([str(x) for x in condition_features.feature_concept_id.values.tolist()]).intersection(data_point.columns.values.tolist()))

drug_features = pd.read_sql_query("SELECT distinct cast(string_field_1 as INT64) as feature_concept_id FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'drug'", conn)
common_features_drugs = list(set([str(x) for x in drug_features.feature_concept_id.values.tolist()]).intersection(data_point.columns.values.tolist()))

proc_features = pd.read_sql_query("SELECT distinct cast(string_field_1 as INT64) as feature_concept_id FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'procedure'", conn)
common_features_procs = list(set([str(x) for x in proc_features.feature_concept_id.values.tolist()]).intersection(data_point.columns.values.tolist()))


query_string = '''
  SELECT  distinct 
        condition_start_DATE as observation_date
      , condition_concept_id as feature_concept_id  
    FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.condition_occurrence`  
    WHERE person_id = ''' +str(test_person_id)+ ''' 
    AND condition_concept_id IN 
      (SELECT distinct cast(string_field_1 as INT64) FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'diagnosis')
'''
conditions = pd.read_sql_query(query_string, conn)


query_string = '''
  SELECT  distinct 
        drug_exposure_start_DATE as observation_date
      , drug_concept_id as feature_concept_id  
    FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.drug_exposure` 
    WHERE person_id = ''' +str(test_person_id)+ ''' 
    AND drug_concept_id IN 
      (SELECT distinct cast(string_field_1 as INT64) FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'drug')
'''
drugs = pd.read_sql_query(query_string, conn)


query_string = '''
  SELECT  distinct 
        procedure_DATE as observation_date
      , procedure_concept_id as feature_concept_id  
    FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.procedure_occurrence`
    WHERE person_id = ''' +str(test_person_id)+ ''' 
    AND procedure_concept_id IN 
      (SELECT distinct cast(string_field_1 as INT64) FROM `som-nero-phi-jonc101.proj_nida_ctn_sf.moud_feature_matrix_Ivan` where string_field_2 = 'procedure')
'''
procedures = pd.read_sql_query(query_string, conn)

query_string = "SELECT  * FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.person` WHERE person_id = " + str(test_person_id)
demographics = pd.read_sql_query(query_string, conn)
demographics.to_csv('Sanity Check/'+str(test_person_id)+'_demographics.csv', index=False)

# pdb.set_trace()

# start date: '2021-07-24'
# person_id: 30021837
for i in range(len(data_point)):

  current_row = data_point.iloc[i]
  current_start = current_row['drug_exposure_start_DATE']
  look_back = datetime.strptime(current_start, '%Y-%m-%d').date() - pd.Timedelta(days=90)

  print('Checking patient {} row {}'.format(current_row['person_id'], i))

  current_conds_occ = conditions[(conditions['observation_date'] <= datetime.strptime(current_start, '%Y-%m-%d').date()) & (conditions['observation_date']>= look_back)]['feature_concept_id'].values.tolist()
  current_conds_occ = [str(x) for x in current_conds_occ]  
  current_row_conditions = current_row.loc[common_features_conds]
  non_zeros = current_row_conditions[current_row_conditions > 0].index.values.tolist()

  if set(current_conds_occ) == set(non_zeros):
    print('conditions matched!')
  else:
    print('There is a mismatch!')
    pdb.set_trace()

  current_drugs_occ = drugs[(drugs['observation_date'] <= datetime.strptime(current_start, '%Y-%m-%d').date()) & (drugs['observation_date']>= look_back)]['feature_concept_id'].values.tolist()
  current_drugs_occ = [str(x) for x in current_drugs_occ]
  current_row_drugs = current_row.loc[common_features_drugs]
  non_zeros = current_row_drugs[current_row_drugs > 0].index.values.tolist()

  if set(current_drugs_occ) == set(non_zeros):
    print('drugs matched!')
  else:
    print('There is a mismatch!')
    pdb.set_trace()

  current_procs_occ = procedures[(procedures['observation_date'] <= datetime.strptime(current_start, '%Y-%m-%d').date()) & (procedures['observation_date']>= look_back)]['feature_concept_id'].values.tolist()
  current_procs_occ = [str(x) for x in current_procs_occ]
  current_row_procs = current_row.loc[common_features_procs]
  non_zeros = current_row_procs[current_row_procs > 0].index.values.tolist()

  if set(current_procs_occ) == set(non_zeros):
    print('procedures matched!')
  else:
    print('There is a mismatch!')
    pdb.set_trace()

print('Successfully tested the data for the queried patient.')
