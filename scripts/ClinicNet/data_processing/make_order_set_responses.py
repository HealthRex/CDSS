import pandas as pd
import numpy as np
import os
import gc
import sys, getopt
import multiprocessing

#python data_processing/make_order_set_responses.py -i data/hdf5/dev2/ -o data/hdf5/dev2_order_set/ -m ./queried/patient_item_id_to_order_set_ID_matches.hdf5 -d ./queried/patientitemid_itemdate.hdf5 

def make_order_set_data(f):
	data_s = pd.read_hdf(data_dir + "/" + f, 'data_s')
	data_s = data_s.reset_index(drop=True)
	num_rows = len(data_s.index)
	data_s = data_s.merge(all_item_dates, on='patient_item_id', how='inner')
	assert num_rows == len(data_s.index)
	num_cols = len(data_s.columns)
	# Remove all patients who have no order sets:
	data_s = data_s[data_s['patient_id'].isin(list(mapping.keys()))]
	patients = list(data_s['patient_id'].unique()) # list of patient IDs
	# Set up order set columns:
	for ordersetID in all_ordersetIDs:
		feature_name = 'orderset_' + str(ordersetID) + '.post.1d'
		data_s[feature_name] = 0
	# Fill in order set columns:
	final_patient_items = [] # Final list of patient items to retain when writing out data frame
	for patient in patients: # Iterate through patient IDs
		print(f + " - Going through patient: " + str(patient))
		patient_items = data_s.loc[data_s['patient_id'] == patient,'patient_item_id']
		order_set_data = mapping[patient] # Order set data for current patient
		for patient_item in patient_items: # Iterate through patient item IDs
			atLeastOneOrderSetUsed = False # At least one order set within next 24 hours
			for index, row in order_set_data.iterrows(): # Iterate through order set usage
				feature_name = 'orderset_' + str(row['external_id']) + '.post.1d'
				item_time = data_s.loc[data_s['patient_item_id'] == patient_item,'item_date']
				assert len(item_time) == 1
				item_time = item_time.iloc[0]
				timeDiffSeconds = (row['item_date'] - item_time) / 1000000000
				if timeDiffSeconds >= 0 and timeDiffSeconds <= 24*60*60:
					data_s.loc[data_s['patient_item_id'] == patient_item,feature_name] += 1
					atLeastOneOrderSetUsed = True
			if atLeastOneOrderSetUsed or retain_all:
				final_patient_items.append(patient_item)
	# Prepare data frames for writing to output files:
	data_x = pd.read_hdf(data_dir + "/" + f, 'data_x')
	data_x = data_x.reset_index(drop=True)
	data_s = data_s[data_s['patient_item_id'].isin(final_patient_items)]
	data_x = data_x.loc[data_x.index.isin(data_s.index),:]
	assert len(data_x.index) == len(data_s.index)
	S1 = data_s.iloc[:,:num_cols] #TODO (not five)
	S2 = data_s.iloc[:,num_cols:]
	# Write to output files:
	data_x.to_hdf(output_dir + "/" + f, key='data_x', mode='w', complevel=1)
	S1.to_hdf(output_dir + "/" + f, key='data_s', complevel=1)
	S2.to_hdf(output_dir + "/" + f, key='data_y', complevel=1)
	print(f + " - " + str(len(final_patient_items)) + " out of " + str(num_rows) + " items retained among " + str(len(patients)) + " patients")
	# Garbage collection:
	del data_x
	del data_s
	gc.collect()
    
def main(argv):
	global files_list # Input directory (where the HDF5 files are stored)
	global data_dir
	global output_dir
	global mapping # Dict mapping from patient ID to data frame containing order set information for that patient
	global all_ordersetIDs # List of all order set IDs that will become response variables
	global all_item_dates # Match patient item IDs to dates
	global retain_all # Match patient item IDs to dates
	data_dir = ""
	output_dir = ""
	mapping_dir = ""
	dates_dir = ""
	all_item_dates = ""
	num_processes = 0
	retain_all = False
	try:
		opts, args = getopt.getopt(argv,"hi:o:m:d:p:a")
	except getopt.GetoptError:
		print('make_order_set_responses.py -i <data_directory> -o <output_dir> -m <patient_orderset_mapping_file> -d <patient_itemdate_mapping_file> [-p num_processes] [-a] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('make_order_set_responses.py -i <data_directory> -o <output_dir> -m <patient_orderset_mapping_file> -d <patient_itemdate_mapping_file> -p <num_processes> [-a] [-h]')
			print('')
			print('This script performs processes data files (in HDF5 format), from <data_directory>, to give post-one-day order set usages.')
			print('Only the data rows that have at least one post-one-day order set usage are retained unless the flag -a is used in which case all data rows will be retained.')
			print('The new data will be stored in <output_directory>.')
			print('Two hdf5 files need to be specified:')
			print('1. <patient_orderset_mapping_file>: data frame of order set items with columns being patient_id, patient_item_id, external_id (the order set ID), and item_date (the order set item date as nanoseconds since epoch).')
			print('2. <patient_itemdate_mapping_file>: data frame of patient items with columns being item_date (as nanoseconds since epoch) and patient_item_id')
			print('Use num_processes to specify the number of processes to use for multiprocessing.')
			sys.exit()
		elif opt == '-i':
			data_dir = arg
		elif opt == '-o':
			output_dir = arg
		elif opt == '-p':
			num_processes = int(arg)
		elif opt == '-a':
			retain_all = True
		elif opt == '-m':
			mapping_dir = arg
		elif opt == '-d':
			dates_dir = arg
	if len(argv) < 4 or data_dir == '' or output_dir == '' or mapping_dir == '' or dates_dir == '':
		print('make_order_set_responses.py -i <data_directory> -o <output_dir> -m <patient_orderset_mapping_file> -d <patient_itemdate_mapping_file> [-p num_processes] [-a] [-h]')
		sys.exit(2)
	
	# Configure multiprocessing
	if num_processes == 0:
		num_processes = multiprocessing.cpu_count()-1
	print("Number of processes: " + str(num_processes))
	
	# Setup mappings
	mapping = pd.read_hdf(mapping_dir)
	mapping = mapping.sort_values(by='item_date')
	mapping = mapping.drop_duplicates()
	all_ordersetIDs = list(mapping['external_id'].unique())
	all_ordersetIDs.sort()
	mapping = dict(tuple(mapping.groupby('patient_id')))
	all_item_dates = pd.read_hdf(dates_dir)
	print("Total order sets: {}".format(len(all_ordersetIDs)))
	
	# Iterate through data_dir to process the files
	files_list = os.listdir(data_dir)
	pool = multiprocessing.Pool(num_processes)
	pool.map(make_order_set_data, files_list)

if __name__ == "__main__":
   main(sys.argv[1:])
