# This script turns the data (stored in tab-delimited plaintext files) into HDF5 format

import numpy as np
import pandas as pd
import os
import tables
import random
import re
import multiprocessing
import sys, getopt

# Function: loading in the data and making it into HDF5
# Everything is stored with as the float32 data type
## (Therefore, any non-numerical columns need to not be present in columns_line_exclude_responses)
def load_in_data(files_list):
	global columns_line, columns_line_exclude_responses, hdf5_dir, files_dir
	rand_identifier = random.randint(1,9999999)
	hdf5_file = hdf5_dir + '/{}.h5'.format(rand_identifier)
	data_x = None
	data_y = None
	for i in range(len(files_list)):
		f = files_list[i]
		if i%10==0:
			print(str(i) + ": " + f) # Which iteration we're currently on
		subdata = pd.read_table(files_dir + "/" + f, sep = '\t', header=None, names=columns_line, usecols=columns_line_exclude_responses, dtype='float32', na_values='None')
		colNames_y = subdata.columns[subdata.columns.str.contains(pat = '.post.1d')] 
		colNames_x = subdata.columns[~subdata.columns.str.contains(pat = '.post.1d')] 
		if data_x is None:
			data_x = subdata.loc[:,colNames_x]
		else:
			data_x = data_x.append(subdata.loc[:,colNames_x])
		if data_y is None:
			data_y = subdata.loc[:,colNames_y]
		else:
			data_y = data_y.append(subdata.loc[:,colNames_y])            
	data_x.to_hdf(hdf5_file, key='data_x', mode='w', complevel=1)
	data_y.to_hdf(hdf5_file, key='data_y', mode='a', complevel=1)

def main(argv):
	# Read in command line arguments:
	input_dir = ''
	columns_file=''
	output_dir = ''
	num_split = 1
	relevant_response_columns_file = ''
	exclude_cols = []
	num_processes = 0
	try:
		opts, args = getopt.getopt(argv,"hi:c:o:n:r:e:p:")
	except getopt.GetoptError:
		print('make_hdf5.py -i <data_directory> -c <columns_file> -o <output_directory> [-n num_split] [-r response_var_file] [-e exclude_features] [-p num_processes] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
	                print('make_hdf5.py -i <data_directory> -c <columns_file> -o <output_directory> [-n num_split] [-r response_var_file] [-e exclude_features] [-p num_processes] [-h]')
			print('')
			print('This script converts the data (stored in tab-delimited plaintext files in <data_directory>) into HDF5 files which will be stored in <output_directory>')
			print('We specify a tab-delimited file, <columns_file>, containing the column names of each column in the tab-delimited plaintext data files')
			print('The number of HDF5 files produced is dictated by num_split, which denotes how many chunks the data will be split into')
			print('As we process the data in chunks, we can use multiple processors by specifying num_processes')
			print('We can specify a response_var_file which is a tab-separated-values file containing a column named clinical_item_id, which has all the clinical item ID numbers we want to retain in the final HDF5 files for the response variable')
			print('Important: Because the data frame stored in the HDF5 file will be float32 format, it is necessary to get rid of features that are non-numerical')
			print('To get rid of certain features, specify exclude_features as the feature names separated by commas')
			print('Each HDF5 file produced will receive a random numerical ID for its filename.')
			sys.exit()
                elif opt == '-p':
                        num_processes = int(arg)
                elif opt == '-r':
                        relevant_response_columns_file = arg
                elif opt == '-e':
                        exclude_cols = arg.split(',')
		elif opt == '-n':
			num_split = int(arg)
		elif opt == '-i':
			input_dir = arg
		elif opt == '-o':
			output_dir = arg
                elif opt == '-c':
                        columns_file = arg
	if len(argv) < 3 or columns_file == '' or input_dir == '' or output_dir == '':
                print('make_hdf5.py -i <data_directory> -c <columns_file> -o <output_directory> [-n num_split] [-r response_var_file] [-e exclude_features] [-p num_processes] [-h]')
		sys.exit(2)

	# Set up globals (since multiprocessing.Pool(...) doesn't handle multiple arguments)
	global columns_line, columns_line_exclude_responses, hdf5_dir, files_dir
	files_dir = input_dir
	hdf5_dir = output_dir

	# Load the columns	
	columns_line = []
	with open(columns_file) as f:
		columns_line = f.readline().split("\t")

	# Process response columns to get a list of response columns to be removed
	response_cols = pd.read_csv(relevant_response_columns_file, sep="\t")
	response_cols = response_cols.loc[:,"clinical_item_id"]
	response_cols = response_cols.values
	response_cols = map(lambda x: "clinitem_{}.post.1d".format(x), response_cols)
	r = re.compile("(.*\.post\.1d$)")
	all_response_cols = list(filter(r.match, columns_line))
	response_cols_to_remove = list(set(all_response_cols) - set(response_cols))

	# Get a list of colummns that will make it into the final HDF5 file
	columns_line_exclude_responses = list(set(columns_line) - set(response_cols_to_remove))
	columns_line_exclude_responses = list(set(columns_line_exclude_responses) - set(exclude_cols))  # also exclude exclude_cols columns

	# Process the data into HDF5 files
        files_list = os.listdir(files_dir)
	if num_processes == 0:
		num_processes = multiprocessing.cpu_count()-1
	if num_processes > num_split: # In case we have more processors than we actually need
		num_processes = num_split
	print("Using " + str(num_processes) + " processes for processing " + str(len(files_list)) + " files divided into " + str(num_split) + " chunks")
	pool = multiprocessing.Pool(num_processes)
	p = pool.map(load_in_data, np.array_split(files_list, num_split))
	print("FINISHED")

if __name__ == "__main__":
   main(sys.argv[1:])
