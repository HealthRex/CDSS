# This script takes data files and shuffles them into batches (which have been determined previously)

import pandas as pd
import os
import tables
import pickle
import gzip
import gc
import sys, getopt

# Function to write batches of dataset to files
def write_shuffled_batches(data_dir, output_dir, batch_dicts, index_begin=None, index_end=None):
	files_list = os.listdir(data_dir)
	files_list.sort()
	num_batches = len(batch_dicts)
	if index_begin is None:
		index_begin = 0
	if index_end is None:
		index_end = 0
	if index_end > num_batches:
		index_end = num_batches
	batch_data_x = [None for i in range(num_batches)] # Stores our final data frames (x)
	batch_data_y = [None for i in range(num_batches)] # Stores our final data frames (y)
	batch_data_s = [None for i in range(num_batches)] # Stores our final data frames (s)
	for f in files_list:
		print(f)
		data_x = pd.read_hdf(data_dir + "/" + f, 'data_x', mode='r')
		data_y = pd.read_hdf(data_dir + "/" + f, 'data_y', mode='r')
		data_s = None
		try:
			data_s = pd.read_hdf(data_dir + "/" + f, 'data_s', mode='r')
		except KeyError:
			data_s = None
		for i in range(index_begin,index_end):
			if f in list(batch_dicts[i].keys()):
				if batch_data_x[i] is None:
					batch_data_x[i] = data_x.iloc[batch_dicts[i][f]]
				else:
					batch_data_x[i] = batch_data_x[i].append(data_x.iloc[batch_dicts[i][f]])
				if batch_data_y[i] is None:
					batch_data_y[i] = data_y.iloc[batch_dicts[i][f]]
				else:
					batch_data_y[i] = batch_data_y[i].append(data_y.iloc[batch_dicts[i][f]])
				if batch_data_s[i] is None and not (data_s is None):
					batch_data_s[i] = data_s.iloc[batch_dicts[i][f]]
				elif not (data_s is None):
					batch_data_s[i] = batch_data_s[i].append(data_s.iloc[batch_dicts[i][f]])
		# Free up some memory:
		del data_x
		del data_y
		del data_s
		gc.collect()
	for i in range(index_begin,index_end):
		print("Writing batch {} to file".format(i))
		hdf5_file = output_dir + "/" + str(i) + ".h5"
		batch_data_x[i].to_hdf(hdf5_file, key='data_x', mode='w', complevel=1)
		batch_data_y[i].to_hdf(hdf5_file, key='data_y', mode='a', complevel=1)
		if not (all(v is None for v in batch_data_s)):
			batch_data_s[i].to_hdf(hdf5_file, key='data_s', mode='a', complevel=1)


def main(argv):
	# Read in command line arguments:
	pickle_shuffle_file = ''
	input_dir = ''
	output_dir = ''
	begin_index=None
	end_index=None
	try:
		opts, args = getopt.getopt(argv,"hs:d:i:o:b:e:")
	except getopt.GetoptError:
		print('make_batches.py -s <shuffle_pickle_file> -i <directory_of_data_to_shuffle> -o <output_directory> [-b index_to_begin] [-e index_to_end] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('make_batches.py -s <shuffle_pickle_file> -i <directory_of_data_to_shuffle> -o <output_directory> [-b index_to_begin] [-e index_to_end] [-h]')
			print('')
			print('This script shuffles the data stored in the files in <directory_of_data_to_shuffle>.')
			print('The shuffling is done in accordance to the batches supplied in the <shuffle_pickle_file> file.')
			print('Each output file will be a batch of data, and will be stored in <output_directory>')
			print('We need to look through all data files to find the data rows associated with each batch.')
			print('Therefore, this script will take a long time to run, and will consume a lot of memory.')
			print('Rather than making all the batches at once, we can specify a range of batches to make per run.')
			print('This is done via <index_to_begin> and <index_to_end>, where we can supply the indices of the batches to start and end at.')
			sys.exit()
		elif opt == '-s':
			pickle_shuffle_file = arg
                elif opt == '-b':
                        begin_index = int(arg)
                elif opt == '-e':
                        end_index = int(arg)
		elif opt == '-i':
			input_dir = arg
		elif opt == '-o':
			output_dir = arg
        if len(argv) < 3 or pickle_shuffle_file == '' or input_dir == '' or output_dir == '':
                print('make_batches.py -s <shuffle_pickle_file> -i <directory_of_data_to_shuffle> -o <output_directory> [-b index_to_begin] [-e index_to_end] [-h]')
                sys.exit(2)

	# Read the shuffling from the gzip-compressed pickle file
	infile = gzip.open(pickle_shuffle_file,'rb', compresslevel=1)
	shuffled_batches = pickle.load(infile)
	infile.close()

	# Finally, time to write the batches to files
	write_shuffled_batches(input_dir, output_dir, shuffled_batches, begin_index, end_index)

if __name__ == "__main__":
   main(sys.argv[1:])
