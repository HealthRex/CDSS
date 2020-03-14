# Takes HDF5 data files and add item_date timestamps based on a mapping file between patient_item_id and item_date

import pandas as pd
import numpy as np
import os
import sys, getopt
import multiprocessing

def add_dates(f):
	data_s = pd.read_hdf(data_dir + "/" + f, 'data_s')
	data_s = data_s.reset_index(drop=True)
	data_s = data_s.reset_index().merge(all_item_dates, on='patient_item_id', how='inner').set_index('index')
	del data_s.index.name
	# Write to output files:
	# data_x.to_hdf(output_dir + "/" + f, key='data_x', mode='w', complevel=1)
	# S1.to_hdf(output_dir + "/" + f, key='data_s', complevel=1)
	# S2.to_hdf(output_dir + "/" + f, key='data_y', complevel=1)
	print(f)
 
def main(argv):
	global files_list # Input directory (where the HDF5 files are stored)
	global data_dir
	global all_item_dates # Match patient item IDs to dates
	data_dir = ""
	dates_dir = ""
	all_item_dates = ""
	num_processes = 0
	try:
		opts, args = getopt.getopt(argv,"hi:d:p:")
	except getopt.GetoptError:
		print('make_order_set_responses.py -i <data_directory> -d <patient_itemdate_mapping_file> [-p num_processes] [-a] [-h]')
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
		elif opt == '-p':
			num_processes = int(arg)
		elif opt == '-d':
			dates_dir = arg
	if len(argv) < 4 or data_dir == '' or output_dir == '' or mapping_dir == '' or dates_dir == '':
		print('make_order_set_responses.py -i <data_directory> -o <output_dir> -m <patient_orderset_mapping_file> -d <patient_itemdate_mapping_file> [-p num_processes] [-a] [-h]')
		sys.exit(2)
	
	# Configure multiprocessing
	if num_processes == 0:
		num_processes = multiprocessing.cpu_count()-1
	print("Number of processes: " + str(num_processes))
	
	# Setup date time stamps
	all_item_dates = pd.read_hdf(dates_dir)
	
	# Iterate through data_dir to process the files
	files_list = os.listdir(data_dir)
	pool = multiprocessing.Pool(num_processes)
	pool.map(make_order_set_data, files_list)

if __name__ == "__main__":
   main(sys.argv[1:])
