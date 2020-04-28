# This script generates batch assignments (randomly) from data
# The batch assignments (in pickle file format) will be used by make_batches.py

import numpy as np
import pandas as pd
import math
import os
import tables
import pickle
import gzip
import random
import sys, getopt

# Function to generate random batches
def get_shuffled_batches(data_dir, batch_size, num_data_rows):
	files_list = os.listdir(data_dir)
	files_list.sort()
	data_x = None
	if batch_size is None:
		batch_size = num_data_rows

	data_map = {} # Keys are file names; values are row numbers
	data_rows_remaining = num_data_rows
	total_rows_read = 0 # Keep track of the total number of rows we have read so far
	while data_rows_remaining > 0:
		total_data_rows = 0 # Keep track of the total number of rows in our dataset
		for f in files_list:
			store = pd.HDFStore(data_dir + "/" + f, mode='r')
			nrows = store.get_storer('data_x').shape[0]
			total_data_rows += nrows
			batch_update = [] # The data row numbers in the new batch to add on
			if f in list(data_map.keys()): 
				batch_update = list(set(random.sample(list(range(nrows)), nrows)) - set(data_map[f]))
			else:
				data_map[f] = []
				batch_update = list(set(random.sample(list(range(nrows)), nrows)))
			random.shuffle(batch_update)
			batch_update_length = min(batch_size,len(batch_update))
			batch_update_length = min(batch_update_length, data_rows_remaining)
			data_map[f].extend(batch_update[0:batch_update_length])
			data_rows_remaining -= batch_update_length
			total_rows_read += batch_update_length
			store.close()
		if total_rows_read == total_data_rows: # In the event that we have already read all the rows
			data_rows_remaining = 0
			num_data_rows = total_rows_read
			if batch_size > num_data_rows:
				batch_size = num_data_rows
			break
            
	print("Read {} data rows in {} files".format(num_data_rows, len(files_list)))

	# Turn the data_map into a list of tuples 
	data_map_list = []
	for k,v in data_map.items():
		s = [(k,r) for r in v]
		if len(s) > 0:
			data_map_list.extend(s)
            
	random.shuffle(data_map_list)

	# Now, create some batches: 
	num_batches = int(math.ceil(float(num_data_rows) / batch_size)) # How many batches to have
	num_rows_remaining = int(num_data_rows % batch_size) # How many rows in the last batch if it's not a perfect division by batch_size
	padding = int(batch_size - num_rows_remaining) # The "padding" to add to make divisible by batch_size
	batches = np.array_split(data_map_list + [None for i in range(padding)], num_batches) # Do batch assignments
	batches[num_batches-1] = batches[num_batches-1][:-padding] # Get rid of the padding now
	batch_dicts = [] # Convert the batches into a list of dicts where keys are the files and values are the row numbers
	for i in range(num_batches):
		curr_batch = {}
		for k, v in batches[i]:
			curr_batch.setdefault(k, []).append(v)
		batch_dicts.append(curr_batch)

	print("Created {} batches of size {}".format(len(batch_dicts), batch_size))

	return batch_dicts

def main(argv):
	# Read in command line arguments:
	input_dir = ''
	output_file = ''
	num_rows = 100000000000
	batch_size = 0
	try:
		opts, args = getopt.getopt(argv,"hi:o:b:n:")
	except getopt.GetoptError:
		print('prep_batches.py -i <data_directory> -o <output_file> -b <batch_size> [-n num_rows] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('prep_batches.py -i <data_directory> -o <output_file> -b <batch_size> [-n num_rows] [-h]')
			print('')
			print('This script prepares randomly shuffled batch assignments from the data stored in the files in <data_directory>.')
			print('The size of each batch is given by <batch_size>; larger batch sizes means fewer batches and small batch sizes means more batches.')
			print('The output, <output_file>, is a pickle file containing the batch assignments. This pickle file will be used by make_batches.py.')
			print('Batch assignments is a list of dicts; each element (dict) of the list is a batch.')
			print('The keys of each dict are the files of the batch and the values are the row numbers for given files of the batch.')
			print('We can specify that num_rows of data in our dataset be used.')
			print('Note that the shuffling done is completely random -- the entire dataset is shuffled, not just individual files within the dataset.')
			print('Therefore, this script will take a long time to run, and will consume a lot of memory.')
			print('Rather than making all the batches at once, we can specify a range of batches to make per run.')
			print('This is done via <index_to_begin> and <index_to_end>, where we can supply the indices of the batches to start and end at.')
			sys.exit()
                elif opt == '-b':
                        batch_size = int(arg)
		elif opt == '-n':
			num_rows = int(arg)
		elif opt == '-i':
			input_dir = arg
		elif opt == '-o':
			output_file = arg
	if len(argv) < 3 or batch_size == 0 or input_dir == '' or output_file == '':
		print('prep_batches.py -i <data_directory> -o <output_file> -b <batch_size> [-n num_rows] [-h]')
		sys.exit(2)

	# Get our shuffled batch assignments and write them to the pickle file
	shuffled_batches = get_shuffled_batches(input_dir, batch_size, num_rows)
	outfile = gzip.open(output_file,'wb', compresslevel=1)
	pickle.dump(shuffled_batches,outfile)
	outfile.close()

if __name__ == "__main__":
   main(sys.argv[1:])
   
