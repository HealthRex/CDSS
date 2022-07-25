import pdb
import pandas as pd
import itertools
import math
import collections
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import csv 
from google.cloud.bigquery import dbapi
from google.cloud import bigquery

logging.basicConfig(format='Date-Time : %(asctime)s : Line No. : %(lineno)d - %(message)s', level = logging.INFO, filename = 'log/logfile_create_stationary.log', filemode = 'a')

def blind_data(patient_id
				,line_med_splited
				, line_diag_splited
				, line_proc_splited
				, line_lab_splited
				, current_patient_demog
				, blind_period
				, admit_date):
	# if patient_id == 'JC2872558':
	# 	pdb.set_trace()
	line_meds_blinded = []
	line_diags_blinded = []
	line_procs_blinded = []
	line_lab_blinded = []

	if (line_med_splited != [] and line_diag_splited != [] and line_proc_splited != []):
		first_record_date = min(datetime.strptime(line_med_splited[0][0], '%Y-%m-%d'), datetime.strptime(line_diag_splited[0][0][:10], '%Y-%m-%d'), datetime.strptime(line_proc_splited[0][0][:10], '%Y-%m-%d'))
		last_record_date = max(datetime.strptime(line_med_splited[-1][0], '%Y-%m-%d'), datetime.strptime(line_diag_splited[-1][0][:10], '%Y-%m-%d'), datetime.strptime(line_proc_splited[-1][0][:10], '%Y-%m-%d'))
	elif (line_med_splited != [] and line_diag_splited != [] and line_proc_splited == []):
		first_record_date = min(datetime.strptime(line_med_splited[0][0], '%Y-%m-%d'), datetime.strptime(line_diag_splited[0][0][:10], '%Y-%m-%d'))
		last_record_date = max(datetime.strptime(line_med_splited[-1][0], '%Y-%m-%d'), datetime.strptime(line_diag_splited[-1][0][:10], '%Y-%m-%d'))
	elif (line_med_splited == [] and line_diag_splited != [] and line_proc_splited != []):
		first_record_date = min(datetime.strptime(line_proc_splited[0][0], '%Y-%m-%d'), datetime.strptime(line_diag_splited[0][0][:10], '%Y-%m-%d'))
		last_record_date = max(datetime.strptime(line_proc_splited[-1][0], '%Y-%m-%d'), datetime.strptime(line_diag_splited[-1][0][:10], '%Y-%m-%d'))	
	elif (line_med_splited == [] and line_diag_splited != [] and line_proc_splited == []):
		# pdb.set_trace()
		first_record_date = datetime.strptime(line_diag_splited[0][0][:10], '%Y-%m-%d')
		last_record_date = datetime.strptime(line_diag_splited[-1][0][:10], '%Y-%m-%d')
	else:
		pdb.set_trace()
	# pdb.set_trace()	

	idx_date = admit_date + relativedelta(days= blind_period)

	for i in range(len(line_med_splited)):
		current_date = datetime.strptime(line_med_splited[i][0][:10], '%Y-%m-%d').date() 		
		current_date_to_idx_date = (idx_date - current_date).days
		if (current_date_to_idx_date >=0):
			line_meds_blinded.append(line_med_splited[i])
	# pdb.set_trace()		
	for i in range(len(line_diag_splited)):
		current_date = datetime.strptime(line_diag_splited[i][0][:10], '%Y-%m-%d').date() 		
		current_date_to_idx_date = (idx_date - current_date).days
		if (current_date_to_idx_date >=0):
			line_diags_blinded.append(line_diag_splited[i])
	# pdb.set_trace()		
	for i in range(len(line_proc_splited)):
		current_date = datetime.strptime(line_proc_splited[i][0][:10], '%Y-%m-%d').date() 		
		current_date_to_idx_date = (idx_date - current_date).days
		if (current_date_to_idx_date >=0):
			line_procs_blinded.append(line_proc_splited[i])
	# pdb.set_trace()	
	for i in range(len(line_lab_splited)):
		if line_lab_splited[i][0] == None:
			break
		current_date = datetime.strptime(line_lab_splited[i][0][:10], '%Y-%m-%d').date() 		
		current_date_to_idx_date = (idx_date - current_date).days
		if (current_date_to_idx_date >=0):
			line_lab_blinded.append(line_lab_splited[i])

	# if patient_id == 'JC2872558':
	# 	pdb.set_trace()

	return line_meds_blinded, line_diags_blinded, line_procs_blinded, line_lab_blinded	

def create_stationary_ccs(patient_id, line_diag_splited, frequent_ccs_dict):
	# pdb.set_trace()
	epsil = 2.220446049250313e-16
	round_num_digit = 5
	for i in range(len(line_diag_splited)):
		# if line_diag_splited[i][0]
		for j in range(1, len(line_diag_splited[i])): 
			if (line_diag_splited[i][j] in frequent_ccs_dict):           
				frequent_ccs_dict[ line_diag_splited[i][j]] = 1
			else:
				continue  
				print('test') 
	# pdb.set_trace()
	frequent_ccs_dict_sorted = dict(collections.OrderedDict(sorted(frequent_ccs_dict.items())))    
	# num_records = len(line_diag_splited)
	# if (num_records > 1):
	# 	frequent_ccs_dict_sorted = {k: np.round(v / (math.log(num_records, 2)+ epsil), round_num_digit) for k, v in frequent_ccs_dict_sorted.items()}
	# else:
	# frequent_ccs_dict_sorted = {k: np.round(v , round_num_digit) for k, v in frequent_ccs_dict_sorted.items()}        
	# pdb.set_trace()
	return frequent_ccs_dict_sorted


def create_stationary_med(line_med_splited, frequent_meds_dict):
	# pdb.set_trace()
	epsil = 2.220446049250313e-16
	round_num_digit = 5
	for i in range(len(line_med_splited)):
		# if line_med_splited[i][0]
		for j in range(1, len(line_med_splited[i])): 
			if (line_med_splited[i][j] in frequent_meds_dict):           
				frequent_meds_dict[ line_med_splited[i][j]] = 1
			else:
				continue  
				print('test') 
	# pdb.set_trace()
	frequent_meds_dict_sorted = dict(collections.OrderedDict(sorted(frequent_meds_dict.items())))    
	# num_records = len(line_med_splited)
	# if (num_records > 1):
	# 	frequent_meds_dict_sorted = {k: np.round(v / (math.log(num_records, 2)+ epsil), round_num_digit) for k, v in frequent_meds_dict_sorted.items()}
	# else:
	# 	frequent_meds_dict_sorted = {k: np.round(v , round_num_digit) for k, v in frequent_meds_dict_sorted.items()}        
	# pdb.set_trace()
	return frequent_meds_dict_sorted

def create_stationary_proc(patient_id, line_proc_splited, frequent_procs_dict):
	# pdb.set_trace()
	epsil = 2.220446049250313e-16
	round_num_digit = 5
	for i in range(len(line_proc_splited)):
		# if line_proc_splited[i][0]
		for j in range(1, len(line_proc_splited[i])): 
			if (line_proc_splited[i][j] in frequent_procs_dict):           
				frequent_procs_dict[ line_proc_splited[i][j]] = 1
			else:
				continue  
				print('test') 
	# pdb.set_trace()
	# if patient_id == 'JCcb6601':
	# 	pdb.set_trace()		
	frequent_procs_dict_sorted = dict(collections.OrderedDict(sorted(frequent_procs_dict.items())))    
	# num_records = len(line_proc_splited)
	# if (num_records > 1):
	# 	frequent_procs_dict_sorted = {k: np.round(v / (math.log(num_records, 2)+ epsil), round_num_digit) for k, v in frequent_procs_dict_sorted.items()}
	# else:
	# 	frequent_procs_dict_sorted = {k: np.round(v , round_num_digit) for k, v in frequent_procs_dict_sorted.items()}        
	# pdb.set_trace()
	return frequent_procs_dict_sorted


def create_stationary_lab(patient_id, line_lab_splited, frequent_lab_dict):
	# pdb.set_trace()
	epsil = 2.220446049250313e-16
	round_num_digit = 5
	for i in range(len(line_lab_splited)):
		# if line_proc_splited[i][0]
		for j in range(1, len(line_lab_splited[i])): 
			if (line_lab_splited[i][j] in frequent_lab_dict):           
				frequent_lab_dict[ line_lab_splited[i][j]] = 1
			else:
				continue  
				print('test') 
	frequent_labs_dict_sorted = dict(collections.OrderedDict(sorted(frequent_lab_dict.items())))    
	
	# num_records = len(line_lab_splited)
	
	# if (num_records > 1):
	# 	frequent_labs_dict_sorted = {k: np.round(v / (math.log(num_records, 2)+ epsil), round_num_digit) for k, v in frequent_labs_dict_sorted.items()}
	# else:
	# 	frequent_labs_dict_sorted = {k: np.round(v , round_num_digit) for k, v in frequent_labs_dict_sorted.items()}        
	# # pdb.set_trace()
	return frequent_labs_dict_sorted

def create_stationary(diagnosis_file_path
					, medication_file_path
					, procedure_file_path
					, lab_file_path
					, demographic_file_path
					, ccs_frequencies_mci_path
					, pharm_class_frequencies_mci_path
					, procedure_id_frequencies_mci_path
					, lab_id_frequencies_mci_path
					, top_n_ccs							 
					, top_n_med
					, top_n_proc
					, top_n_lab
					, logging_milestone		
					):
	# pdb.set_trace()
	blind_period = 1
	client_name ="som-nero-phi-jonc101-secure"
	query_string = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered` A ORDER BY A.anon_id"
	client = bigquery.Client(client_name); 
	conn = dbapi.connect(client);
	cursor = conn.cursor();
	costUB_with_anonid_filtered = pd.read_sql_query(query_string, conn); 


	lab_data = pd.read_csv(lab_file_path, header=None, sep='\n', skiprows=1)
	lab_data = lab_data[0].str.split(',', expand=True)

	print('Reading demographic data ...')
	demographic_data = pd.read_csv(demographic_file_path)
	demographic_data = pd.get_dummies(demographic_data, columns=['sex', 'canonical_race', 'canonical_ethnicity'])

	
	# Rread frequent ICD codes
	# pdb.set_trace()
	print('Check out dtype=str')
	print('Reading frequent codes and selecting top features')
	frequent_ccs = pd.read_csv(ccs_frequencies_mci_path)
	frequent_ccs.columns=frequent_ccs.columns.str.strip()
	frequent_ccs = frequent_ccs.sort_values('num patient', ascending=False)
	frequent_ccs_top_n = frequent_ccs['Code'].values[:top_n_ccs].tolist()


	frequent_meds = pd.read_csv(pharm_class_frequencies_mci_path)
	frequent_meds.columns=frequent_meds.columns.str.strip()
	frequent_meds = frequent_meds.sort_values('num patient', ascending=False)
	frequent_meds_top_n = frequent_meds['Code'].values[:top_n_med].tolist()

	frequent_procs = pd.read_csv(procedure_id_frequencies_mci_path)
	frequent_procs.columns = frequent_procs.columns.str.strip()
	frequent_procs = frequent_procs.sort_values('num patient', ascending=False)	
	frequent_procs_top_n = frequent_procs['Code'].values[:top_n_proc].tolist()

	frequent_labs = pd.read_csv(lab_id_frequencies_mci_path)
	frequent_labs.columns = frequent_labs.columns.str.strip()
	frequent_labs = frequent_labs.sort_values('num patient', ascending=False)	
	frequent_labs_top_n = frequent_labs['Code'].values[:top_n_proc].tolist()


	# pdb.set_trace()
	frequent_ccs_dict = {}
	for i in range(len(frequent_ccs_top_n)):
		frequent_ccs_dict[frequent_ccs_top_n[i]] = 0 
	frequent_ccs_dict = dict(collections.OrderedDict(sorted(frequent_ccs_dict.items())))    

	frequent_meds_dict = {}
	for i in range(len(frequent_meds_top_n)):
		frequent_meds_dict[str(frequent_meds_top_n[i])] = 0 
	frequent_meds_dict = dict(collections.OrderedDict(sorted(frequent_meds_dict.items())))    

	frequent_procs_dict = {}
	for i in range(len(frequent_procs_top_n)):
		frequent_procs_dict[str(frequent_procs_top_n[i])] = 0 
	frequent_procs_dict = dict(collections.OrderedDict(sorted(frequent_procs_dict.items())))    

	frequent_labs_dict = {}
	for i in range(len(frequent_labs_top_n)):
		frequent_labs_dict[str(frequent_labs_top_n[i])] = 0 
	frequent_labs_dict = dict(collections.OrderedDict(sorted(frequent_labs_dict.items())))    


	# pdb.set_trace()
	with open(diagnosis_file_path) as diag_file, open(medication_file_path) as med_file, open(procedure_file_path) as proc_file, open('stationary_data/stationary_dataset.csv', 'w') as stationary_file, open('intermediate_files/elig_patients.csv', 'w') as elig_patients_file, open('intermediate_files/unelig_patients.csv', 'w') as unelig_patients_file:
		header_diag = next(diag_file)
		header_med = next(med_file)
		header_proc = next(proc_file)

		elig_patients_file.write('eligible_patients_ids\n')
		unelig_patients_file.write('uneligible_patients_ids\n')

		stationary_file.write('patient_id, age')
		stationary_file.write(',')  

		stationary_file.write(','.join('DEMOG_' + str(x) for x in demographic_data.columns[2:]))
		stationary_file.write(',')  


		stationary_file.write(','.join('DIAG_' + str(x) for x in [*frequent_ccs_dict.keys()]))
		stationary_file.write(',')

		stationary_file.write(','.join('MED_' + str(x) for x in [*frequent_meds_dict.keys()]))
		stationary_file.write(',')  

		stationary_file.write(','.join('PROC_' + str(x) for x in [*frequent_procs_dict.keys()]))
		stationary_file.write(',') 

		stationary_file.write(','.join('LAB_' + str(x) for x in [*frequent_labs_dict.keys()]))  
		stationary_file.write(',')
				
		stationary_file.write('Cost_Direct, Cost_Indirect, Cost_Total')
		stationary_file.write('\n')       
		line_counter = 0
		
		# pdb.set_trace()
		
		previous_id = '0'
		read_med = True
		read_proc = True

		# num_lines_in_diag = sum(1 for line in diag_file)
		for line in diag_file:
			line_counter+=1
			if line_counter %100 ==0:
				print('Processing line {} in the diagnosis table.'.format(line_counter))
			# print(line_counter)
			line_diag = line.replace('\n','').split(',')
			line_diag_splited = [list(y) for x, y in itertools.groupby(line_diag[1:], lambda z: z == 'EOV') if not x]    
	
			# line_med = meds_data[ meds_data[0] == line_diag[0]]
			if read_med == True:
				line_med = med_file.readline().replace('\n','').split(',')
				line_med_splited = [list(y) for x, y in itertools.groupby(line_med[1:], lambda z: z == 'EOV') if not x]    

			if read_proc == True:	
				line_proc = proc_file.readline().replace('\n','').split(',')
				line_proc_splited = [list(y) for x, y in itertools.groupby(line_proc[1:], lambda z: z == 'EOV') if not x]    
			
			current_id = line_diag[0]
			if previous_id>current_id:
				pdb.set_trace()
				print('Previous ID larger')
			previous_id = current_id
			
			# logging.info('ID in diagnosis record is {}. Id in medication record is {}. ID in procedure record is {}.'.format(line_diag[0], line_med[0], line_proc[0]))

			if not (line_diag[0] == line_med[0] == line_proc[0]):
				# pdb.set_trace()
				logging.info('========================================================')
				logging.info('Patients dont match')
				logging.info('========================================================')

			if line_diag[0] == line_med[0]:
				logging.info('line_diag[0] == line_med[0]: {} and {}. therefore read_med=True.'.format(line_diag[0], line_med[0]))
				line_med_splited = [list(y) for x, y in itertools.groupby(line_med[1:], lambda z: z == 'EOV') if not x]    
				read_med = True
			elif line_diag[0] < line_med[0]:
				# pdb.set_trace()
				logging.info('line_diag[0] < line_med[0]: {} and {}'.format(line_diag[0], line_med[0]))
				line_med_splited = []
				logging.info('Setting line_med_splited=[] and read_med = False')
				read_med = False
			elif line_diag[0] > line_med[0]:
				logging.info('line_diag[0] > line_med[0]: {} and {}'.format(line_diag[0], line_med[0]))
				logging.info('start reading lines from med while line_med[0] < line_diag[0]')
				while line_med[0] < line_diag[0]:
					line_med = med_file.readline().replace('\n','').split(',')
					line_med_splited = [list(y) for x, y in itertools.groupby(line_med[1:], lambda z: z == 'EOV') if not x]    
					logging.info('Read line_med[0]: {}'.format(line_med[0]))
					if line_med == ['']:
						line_med_splited = []
						# pdb.set_trace()
						break					
				# pdb.set_trace()
				if line_med[0] == line_diag[0]:
					logging.info('line_med[0] == line_diag[0] and therefore read_med = True')
					read_med = True
				else:
					logging.info('line_med[0] != line_diag[0] and therefore read_med = False')
					read_med = False	

			if line_diag[0] == line_proc[0]:
				logging.info('line_diag[0] == line_proc[0]: {} and {}. therefore read_proc=True.'.format(line_diag[0], line_proc[0]))				
				line_proc_splited = [list(y) for x, y in itertools.groupby(line_proc[1:], lambda z: z == 'EOV') if not x]    
				read_proc = True
			elif line_diag[0] < line_proc[0]:
				logging.info('line_diag[0] < line_proc[0]: {} and {}'.format(line_diag[0], line_proc[0]))
				line_proc_splited = []
				logging.info('Setting line_proc_splited=[] and read_proc = False')
				read_proc = False
			elif line_diag[0] > line_proc[0]:
				logging.info('line_diag[0] > line_proc[0]: {} and {}'.format(line_diag[0], line_proc[0]))
				logging.info('start reading lines from proc while line_proc[0] < line_diag[0]')
				while line_proc[0] < line_diag[0]:
					line_proc = proc_file.readline().replace('\n','').split(',')
					line_proc_splited = [list(y) for x, y in itertools.groupby(line_proc[1:], lambda z: z == 'EOV') if not x]    
					logging.info('Read line_proc[0]: {}'.format(line_proc[0]))
					if line_proc == ['']:
						line_proc_splited = []
						# pdb.set_trace()
						break					
				# pdb.set_trace()
				if line_proc[0] == line_diag[0]:
					logging.info('line_proc[0] == line_diag[0] and therefore read_proc = True')
					read_proc = True
				else:
					logging.info('line_med[0] != line_proc[0] and therefore read_proc = False')
					read_proc = False	



			# pdb.set_trace()

			if len(line_diag_splited)==0:
				diag_id = 'NA'
			else:
				diag_id = line_diag[0]

			if len(line_med_splited)==0:
				med_id = 'NA'
			else:
				med_id = line_med[0]

			if len(line_proc_splited)==0:
				proc_id = 'NA'
			else:
				proc_id = line_proc[0]
			
			logging.info('line_diag[0], line_med[0], line_proc[0]: {}, {}, {}'.format(diag_id, med_id, proc_id))

			# pdb.set_trace()
			current_costUB = costUB_with_anonid_filtered[costUB_with_anonid_filtered['anon_id']==line_diag[0]]
			if len(current_costUB)<1:
				pdb.set_trace()
			# elif len(current_costUB) > 1:
			# 	pdb.set_trace()	
			current_patient_demog = demographic_data[demographic_data['anon_id']==line_diag[0]]

			if current_patient_demog.empty:
				pdb.set_trace()
				print('Demographic data is missing ...')
				continue
				
			for idx, row in  current_costUB.iterrows():
				admit_date = row['AdmitDate']
				dis_date = row['DischargeDate']
				dir_cost = row['Cost_Direct']
				ind_cost = row['Cost_Indirect']
				tot_cost = row['Cost_Total']
				# idx_date = admit_date + relativedelta(days= 1)

				lab_line = lab_data [lab_data.iloc[:,0]==line_diag[0]]
				if len(lab_line) == 1 :					
					lab_line_splited = [list(y) for x, y in itertools.groupby(lab_line.values.tolist()[0][1:], lambda z: z == 'EOV') if not x]    
					# pdb.set_trace()	
					temp_merg = [lab_line_splited[0][0][:10]] + lab_line_splited[0][1:]
					prev_time = lab_line_splited[0][0][:10]
					lab_line_splited_synced = []	
					for mrg_idx in range(1, len(lab_line_splited)):
						if lab_line_splited[mrg_idx][0] == None:
						   lab_line_splited_synced.append(lab_line_splited[mrg_idx])
						   continue						   
						if lab_line_splited[mrg_idx][0][:10] == prev_time:
							temp_merg = temp_merg + lab_line_splited[mrg_idx][1:]														
						else:
						    lab_line_splited_synced.append([temp_merg[0]] + list(set(temp_merg[1:])))
						    temp_merg = [lab_line_splited[mrg_idx][0][:10]] + lab_line_splited[mrg_idx][1:]
						prev_time = lab_line_splited[mrg_idx][0][:10]    
					# pdb.set_trace()	    	
				elif len(lab_line) == 0 :
					lab_line_splited=[]
				else:
					pdb.set_trace()	
					print('Error')	
				# pdb.set_trace()
	
				
				line_med_blinded, line_diag_blinded, line_proc_blinded, line_lab_blinded = blind_data(line_med[0]
																						, line_med_splited
																						, line_diag_splited
																						, line_proc_splited
																						, lab_line_splited_synced
																						, current_patient_demog
																						, blind_period
																						, admit_date)


				frequent_ccs_dict = dict.fromkeys(frequent_ccs_dict, 0)    
				frequent_meds_dict = dict.fromkeys(frequent_meds_dict, 0)    
				frequent_procs_dict = dict.fromkeys(frequent_procs_dict, 0)    
				frequent_labs_dict = dict.fromkeys(frequent_labs_dict, 0)    

				if len(line_diag_blinded)==0 and len(line_med_blinded)==0 and len(line_proc_blinded)==0 and len(line_lab_blinded)==0:
					unelig_patients_file.write(line_diag[0])
					unelig_patients_file.write('\n')
					continue
				if len(line_diag_blinded)>0 or len(line_med_blinded)>0 or len(line_proc_blinded)>0 or len(line_lab_blinded)>0:
					# pdb.set_trace() 
					elig_patients_file.write(line_diag[0])
					elig_patients_file.write('\n')
				# pdb.set_trace()
				stationary_ccs_vect = create_stationary_ccs(line_diag[0], line_diag_blinded, frequent_ccs_dict)		
				stationary_med_vect = create_stationary_med(line_med_blinded, frequent_meds_dict)					
				stationary_proc_vect = create_stationary_proc(line_diag[0], line_proc_blinded, frequent_procs_dict)		
				stationary_lab_vect = create_stationary_lab(line_diag[0], line_lab_blinded, frequent_labs_dict)		

							
				# pdb.set_trace()
				# if line_med[0] == 'JC2a00006' or line_diag[0] == 'JC2a00006':
				# 	pdb.set_trace()	
				current_patient_age = int(admit_date.year)-int(current_patient_demog['bdate'].values[0].split('-')[0])

				sex_columns = [x for x in current_patient_demog.columns if 'sex_' in x]
				race_columns = [x for x in current_patient_demog.columns if 'canonical_race_' in x]
				ethnicity_columns = [x for x in current_patient_demog.columns if 'canonical_ethnicity_' in x]

				

				stationary_file.write((line_diag[0]))
				stationary_file.write(',')

				stationary_file.write(str(current_patient_age))
				stationary_file.write(',')
				stationary_file.write(','.join(map(repr, current_patient_demog[sex_columns].values.tolist()[0])))
				stationary_file.write(',')
				stationary_file.write(','.join(map(repr, current_patient_demog[race_columns].values.tolist()[0])))
				stationary_file.write(',')
				stationary_file.write(','.join(map(repr, current_patient_demog[ethnicity_columns].values.tolist()[0])))
				stationary_file.write(',')


				# pdb.set_trace()
				stationary_file.write(','.join(map(repr, list(stationary_ccs_vect.values()))))
				stationary_file.write(',')
				stationary_file.write(','.join(map(repr, list(stationary_med_vect.values()))))
				stationary_file.write(',')
				stationary_file.write(','.join(map(repr, list(stationary_proc_vect.values()))))
				stationary_file.write(',')
				stationary_file.write(','.join(map(repr, list(stationary_lab_vect.values()))))
				stationary_file.write(',')	

				stationary_file.write(str(dir_cost))
				stationary_file.write(',')	
				stationary_file.write(str(ind_cost))
				stationary_file.write(',')		
				stationary_file.write(str(tot_cost))						
				stationary_file.write('\n')            
	logging.info('Finished creating stationary data')
	logging.info('***********************************************************************')			
	logging.info('***********************************************************************')			
	logging.info('***********************************************************************')			
	logging.info('***********************************************************************')			
	logging.info('***********************************************************************')							
