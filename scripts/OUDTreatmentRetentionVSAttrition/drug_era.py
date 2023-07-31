import pdb
import sys
import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
from datetime import datetime, timedelta
import csv


client = bigquery.Client('som-nero-phi-jonc101');
conn = dbapi.connect(client);

query_string = '''
  SELECT distinct B.concept_name , A.*
  FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_2022_08_10.drug_exposure` A
  JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_2022_08_10.concept` B on A.drug_concept_id = B.concept_id
  where B.concept_name like '%buprenorphine%naloxone%'
  order by person_id, A.drug_exposure_start_date
'''
exposures = pd.read_sql_query(query_string, conn)
exposures = exposures.sort_values(by=['person_id', 'drug_exposure_start_DATE'])

exposures_grouped = exposures.groupby(by='person_id')

# pdb.set_trace()
with open('feature_matrix/cohort_v2_drug_eras.csv', 'w', newline='') as exp_file:
	exp_file.write('person_id,drug_exposure_start_DATE,drug_exposure_end_DATE,TreatmentDuration\n')
	writer = csv.writer(exp_file)
	for group_name, group_data in exposures_grouped:		
		combined_exposures = []
		start = group_data.iloc[0]['drug_exposure_start_DATE']
		end = group_data.iloc[0]['drug_exposure_end_DATE']
		trt_dur = (end - start).days
		current_combined_exposures = {'id': group_name, 's_date': start, 'e_date': end, 'trt_dur': trt_dur}
		i=1
		while i < len(group_data):
			if (group_data.iloc[i]['drug_exposure_start_DATE'] <= end + timedelta(days=30)):
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
		# pdb.set_trace()
		combined_exposures.append([group_name, current_combined_exposures['s_date'], current_combined_exposures['e_date'], current_combined_exposures['trt_dur']])
		writer.writerows(combined_exposures)

