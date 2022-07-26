import os
import pandas as pd
import pdb
from google.cloud import bigquery
from google.cloud.bigquery import dbapi

def extract_desc(features, med_desc, diag_desc, proc_desc, lab_desc):
	features.columns = ['code', 'score']
	features = features.sort_values(by='score', ascending=False)
	codes_descriptions = []
	# pdb.set_trace()
	for idx, row in features.iterrows():
		if row['code'].split('_')[0] == 'DIAG':
			current_diag_code = row['code'].split('_')[1]
			current_diag_desc = diag_desc[diag_desc['CCSR_CATEGORY_1']==current_diag_code]
			temp_list = current_diag_desc.values.tolist()
			codes_descriptions.extend([['Diagnosis']+x+[row['score']] for x in temp_list])

		elif row['code'].split('_')[0] == 'MED':
			current_med_code = row['code'].split('_')[1]
			current_med_desc = med_desc[med_desc['pharm_class_abbr']==current_med_code]
			temp_list = current_med_desc.values.tolist()
			codes_descriptions.extend([['Medication']+x+[row['score']] for x in temp_list])

		elif row['code'].split('_')[0] == 'PROC':
			current_proc_code = row['code'].split('_')[1]				
			current_proc_desc = proc_desc[proc_desc['proc_id']==int(current_proc_code)]		
			temp_list = current_proc_desc.values.tolist()
			codes_descriptions.extend([['Pocedure']+x+[row['score']] for x in temp_list])

		elif row['code'].split('_')[0] == 'LAB':	
			current_lab_code = row['code'].split('_')[1]				
			current_lab_desc = lab_desc[lab_desc['base_name']==current_lab_code]		
			temp_list = current_lab_desc.values.tolist()
			codes_descriptions.extend([['Lab result']+x+[row['score']] for x in temp_list])

	# pdb.set_trace()
	codes_descriptions_df = pd.DataFrame(codes_descriptions, columns=['Table', 'Code', 'Description', 'num_patient', 'Score'])
	return codes_descriptions_df

def extract_desc_for_stat(features, med_desc, diag_desc, proc_desc, lab_desc):
	codes_descriptions = []
	# pdb.set_trace()
	for i in range(len(features)):
		current_feature = features[i]
		if current_feature.split('_')[0] == 'DIAG':
			current_diag_code = current_feature.split('_')[1]
			current_diag_desc = diag_desc[diag_desc['CCSR_CATEGORY_1']==current_diag_code]
			temp_list = current_diag_desc.values.tolist()
			codes_descriptions.extend([['Diagnosis']+x for x in temp_list])

		elif current_feature.split('_')[0] == 'MED':
			current_med_code = current_feature.split('_')[1]
			current_med_desc = med_desc[med_desc['pharm_class_abbr']==current_med_code]
			temp_list = current_med_desc.values.tolist()
			codes_descriptions.extend([['Medication']+x for x in temp_list])

		elif current_feature.split('_')[0] == 'PROC':
			current_proc_code = current_feature.split('_')[1]				
			current_proc_desc = proc_desc[proc_desc['proc_id']==int(current_proc_code)]		
			temp_list = current_proc_desc.values.tolist()
			codes_descriptions.extend([['Pocedure']+x for x in temp_list])

		elif current_feature.split('_')[0] == 'LAB':	
			# pdb.set_trace()
			current_lab_code = current_feature.split('_')[1]				
			current_lab_desc = lab_desc[lab_desc['base_name']==current_lab_code]		
			temp_list = current_lab_desc.values.tolist()
			
			temp_list = [['Lab result']+x for x in temp_list]
			lab_result = current_feature.split('_')[-1]
			for i in range(len(temp_list)):
				temp_list[i][0] =  temp_list[i][0] + '_' + lab_result
			# pdb.set_trace()	
			codes_descriptions.extend(temp_list)

	# pdb.set_trace()
	codes_descriptions_df = pd.DataFrame(codes_descriptions, columns=['Table', 'Code', 'Description', 'num_patient'])
	return codes_descriptions_df


freq_med_desc = 'SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.medication_description`'
freq_diag_desc = 'SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.diagnosis_description`'
freq_proc_desc = 'SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.procedure_description`'
freq_lab_desc = 'SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.lab_description`'

client_name ="som-nero-phi-jonc101-secure"
client = bigquery.Client(client_name); 
conn = dbapi.connect(client);
cursor = conn.cursor();
med_desc = pd.read_sql_query(freq_med_desc, conn); 
diag_desc = pd.read_sql_query(freq_diag_desc, conn); 
proc_desc = pd.read_sql_query(freq_proc_desc, conn); 
lab_desc = pd.read_sql_query(freq_lab_desc, conn); 


stationary_data_sample = pd.read_csv('stationary_data/stationary_dataset.csv', nrows=200)
stationary_data_sample.columns = stationary_data_sample.columns.str.strip()
features_to_remove=['patient_id', 'age', 'DEMOG_sex_Female', 'DEMOG_sex_Male', 'DEMOG_sex_Unknown', \
'DEMOG_canonical_race_Asian', 'DEMOG_canonical_race_Black', 'DEMOG_canonical_race_Native American', \
'DEMOG_canonical_race_Other', 'DEMOG_canonical_race_Pacific Islander', 'DEMOG_canonical_race_Unknown', \
'DEMOG_canonical_race_White', 'DEMOG_canonical_ethnicity_Hispanic/Latino', \
'DEMOG_canonical_ethnicity_Non-Hispanic', 'DEMOG_canonical_ethnicity_Unknown', \
'Cost_Direct', 'Cost_Indirect', 'Cost_Total']
# pdb.set_trace()
stationary_data_columns = stationary_data_sample.loc[:, ~stationary_data_sample.columns.isin(features_to_remove)].columns.tolist()
stationary_data_columns_desc = extract_desc_for_stat(stationary_data_columns, med_desc, diag_desc, proc_desc, lab_desc)
stationary_data_columns_desc.to_csv('stationary_data/stationary_dataset_feature_description.csv', index=False)



path_to_features = 'results/feature_scores_reg.csv'
features = pd.read_csv(path_to_features)
features_desc = extract_desc(features, med_desc, diag_desc, proc_desc, lab_desc)
features_desc.to_csv(path_to_features[:-4]+'_'+'descriptions.csv', index=False)

path_to_features = 'results/feature_scores_mir.csv'
features = pd.read_csv(path_to_features)
features_desc = extract_desc(features, med_desc, diag_desc, proc_desc, lab_desc)
features_desc.to_csv(path_to_features[:-4]+'_'+'descriptions.csv', index=False)


print('Test')



