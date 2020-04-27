# Gets statistics for the dataset
# Computes mean and standard deviations for each feature, as well as build a covariance matrix
# Additionally, for each response variable, the frequency (i.e. percent) of it being a non-zero value is computed

import numpy as np
import pandas as pd
import os
import tables
import gc
import multiprocessing
import tempfile
import random
import gzip
import _pickle as cPickle # Must use python 3!!
import sys, getopt

# Below are the functions for calculating the average and variances, as well as y frequencies
# Note: NAs are considered as zeros

# Worker function to be pooled for calculating averages
def get_average_worker(f):
	print(f)
	data_x = pd.read_hdf(data_dir + "/" + f, 'data_x', mode='r')
	data_x = data_x.fillna(0)
	data_x = data_x.astype(np.float64) # More accuracy for float point arithmetic
	cols_to_transform = data_x.columns
	if not (exclude_cols_transformation is None):
		cols_to_transform = data_x.columns.difference(exclude_cols_transformation)
	if not (transformation is None):
		data_x[cols_to_transform] = transformation(data_x[cols_to_transform])
	current_N = data_x.shape[0]
	current_sum = data_x.sum(axis=0, skipna=True)
	fd, path = tempfile.mkstemp()
	try:
		with os.fdopen(fd, 'wb') as tmp:
			cPickle.dump((current_sum, current_N), tmp, protocol=4) # protocol=4 avoids OverflowError: cannot serialize a bytes object larger than 4 GiB
	except:
		os.remove(path)
		raise
	del data_x
	gc.collect()
	return path

def get_average(num_processes=1, num_files=None):
	files_list = os.listdir(data_dir)
	random.shuffle(files_list)
	if not (num_files is None):
		files_list = files_list[0:num_files]
	running_sum = None
	running_N = 0
	# Multiprocess pool (returns a bunch of temp files):
	pool = multiprocessing.Pool(num_processes)
	tmp_files = pool.map(get_average_worker, files_list)
	# Iterate through tmp_files:
	for f in tmp_files:
		try:
			with open(f, 'rb') as fp:
				pickle_data = cPickle.load(fp)
				current_sum = pickle_data[0]
				running_N += pickle_data[1]
				if running_sum is None:
					running_sum = current_sum
				else:
					running_sum = running_sum.add(current_sum)
		except:
			os.remove(f)
			raise
		os.remove(f) # Remove the temporary file
	return (running_sum / float(running_N))

# Worker function to be pooled for calculating covariance matrix
def get_covar_worker(files_list):
	running_sum_squared_diff = np.float64(0.0)
	running_N = 0
	for f in files_list:
		print(f)
		data_x = pd.read_hdf(data_dir + "/" + f, 'data_x', mode='r')
		data_x = data_x.fillna(0)
		data_x = data_x.astype(np.float64) # More accuracy for float point arithmetic
		cols_to_transform = data_x.columns
		if not (exclude_cols_transformation is None):
			cols_to_transform = data_x.columns.difference(exclude_cols_transformation)
		if not (transformation is None):
			data_x[cols_to_transform] = transformation(data_x[cols_to_transform])
		current_N = data_x.shape[0]
		current_sum_squared_diff = np.transpose(np.matrix(data_x))*np.matrix(data_x)
		running_N += current_N
		running_sum_squared_diff += current_sum_squared_diff
		del data_x
		del current_sum_squared_diff
		gc.collect()
	# Create temporary file to store our data
	fd, path = tempfile.mkstemp()
	try:
		with gzip.open(path, 'wb', compresslevel=1) as tmp:
			cPickle.dump((running_sum_squared_diff, running_N), tmp, protocol=4) # Again, we need protocol=4
	except:
		os.remove(path)
		raise
	return path

def get_covar(num_processes=1, num_files=None):
	files_list = os.listdir(data_dir)
	random.shuffle(files_list)
	if not (num_files is None):
		files_list = files_list[0:num_files]
	running_sum_squared_diff = np.float64(0.0)
	running_N = 0
	# Multiprocess pool (returns a bunch of temp files):
	pool = multiprocessing.Pool(num_processes)
	# We'll divide the task up into num_processes (rather than number of files since each temp file created will be huge)
	tmp_files = pool.map(get_covar_worker, np.array_split(files_list, num_processes))
	# Iterate through tmp_files:
	for f in tmp_files:
		try:
			with gzip.open(f, 'rb', compresslevel=1) as fp: ##
				pickle_data = cPickle.load(fp)
				current_sum_squared_diff = pickle_data[0]
				running_N += pickle_data[1]
				running_sum_squared_diff += current_sum_squared_diff
		except:
			os.remove(f)
			raise
		os.remove(f) # Remove the temporary file
	running_N -= 1 # Bessel's correction
	return (running_sum_squared_diff / float(running_N))

# Note: Not parallelized
def get_stddev(num_files=None):
	files_list = os.listdir(data_dir)
	random.shuffle(files_list)
	if not (num_files is None):
		files_list = files_list[0:num_files]
	running_sum_squared_diff = None
	running_N = 0
	for f in files_list:
		print(f)
		data_x = pd.read_hdf(data_dir + "/" + f, 'data_x', mode='r')
		data_x = data_x.fillna(0)
		cols_to_transform = data_x.columns
		if not (exclude_cols_transformation is None):
			cols_to_transform = data_x.columns.difference(exclude_cols_transformation)
		if not (transformation is None):
			data_x[cols_to_transform] = transformation(data_x[cols_to_transform])
		running_N += data_x.shape[0]
		data_x -= average
		data_x = data_x**2
		current_sum_squared_diff = data_x.sum(axis=0, skipna=True)
		if running_sum_squared_diff is None:
			running_sum_squared_diff = current_sum_squared_diff
		else:
			running_sum_squared_diff = running_sum_squared_diff.add(current_sum_squared_diff)
		del data_x
		gc.collect()
	running_N -= 1 # Bessel's correction
	return (running_sum_squared_diff / float(running_N))**(0.5)

def get_freq_y():
	files_list = os.listdir(data_dir)
	files_list.sort()
	running_sum = None
	running_N = 0
	for f in files_list:
		print(f)
		data_y = pd.read_hdf(data_dir + "/" + f, 'data_y', mode='r')
		data_y = data_y.clip(upper=1) # Change all numbers greater than 1 to 1's
		data_y = data_y.fillna(0)
		data_y = data_y.astype(int) # More accuracy (don't want to add up floats)
		running_N += data_y.shape[0]
		current_sum = data_y.sum(axis=0, skipna=True)
		if running_sum is None:
			running_sum = current_sum
		else:
			running_sum = running_sum.add(current_sum)
		del data_y
		gc.collect()
	return (running_sum / float(running_N))

def main(argv):
	# How to transform our data (i.e. log2(x+1)):
	global transformation
	transformation = lambda x: np.log2(x+1)

	# Output file names:
	output_avg_stddev_filename = "avg_stddev.hdf5" # name of the output file for avg and std dev
	output_covar_filename = "covar.hdf5" # name of the output file for covariance matrix
	output_freq_y_filename = "freq_y.hdf5" # name of the output file for y frequencies

	# Read in command line arguments:
	global data_dir
	data_dir = ''
	output_dir = ''
	global exclude_cols_transformation
	exclude_cols_transformation = None
	num_processes = 0
	skipcov = False
	num_files = None
	try:
		opts, args = getopt.getopt(argv,"hi:o:x:p:t:n:s")
	except getopt.GetoptError:
		print('compute_stats.py -i <data_directory> -o <output_directory> [-x features_to_exclude] [-p num_processes] [-t temp_dir] [-n num_files] [-s] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('compute_stats.py -i <data_directory> -o <output_directory> [-x features_to_exclude] [-p num_processes] [-t temp_dir] [-n num_files] [-s] [-h]')
			print('')
			print('This script computes the mean, covariance, and standard deviation of all features. All data is log2(x+1)-transformed except those in features_to_exclude.')
			print('Additionally, for each response variable, the frequency (i.e. percent) of it being a non-zero value is computed.')
			print('As a result, three output files will be generated: avg_stddev.hdf5, covar.hdf5, and freq_y.hdf5')
			print('The input files are read from the directory <data_directory>')
			print('For features_to_exclude, supply feature names separated by commas.')
			print('Use num_processes to specify the number of processes to use for multiprocessing.')
			print('Use temp_dir to specify a different temp folder than the default.')
			print('Use num_files to limit how many files in the directory to read from (for computation tractability purposes); the data between files should all be shuffled beforehand.')
			print('Specify the -s option to skip computation of the covariance matrix')
			sys.exit()
		elif opt == '-x':
			exclude_cols_transformation = arg.split(',')
		elif opt == '-i':
			data_dir = arg
		elif opt == '-o':
			output_dir = arg
		elif opt == '-p':
                        num_processes = int(arg)
		elif opt == '-t':
                        tempfile.tempdir = arg # Change default temp directory
		elif opt == '-n':
			num_files = int(arg)
		elif opt == '-s':
			skipcov = True
	if len(argv) < 2 or data_dir == '' or output_dir == '':
                print('compute_stats.py -i <data_directory> -o <output_directory> [-x features_to_exclude] [-p num_processes] [-t temp_dir] [-n num_files] [-s] [-h]')
                sys.exit(2)

	# Configure multiprocessing
	if num_processes == 0:
		num_processes = multiprocessing.cpu_count()-1
	print("Number of processes: " + str(num_processes))

	# Get the average
	output_file = output_dir + "/" + output_avg_stddev_filename
	#avg = get_average(num_processes, num_files)
	#avg.to_hdf(output_file, key='avg', mode='w')
	avg = pd.read_hdf(output_file, key='avg')
	global average
	average = avg
	print("FINISHED AVERAGE")
	if not skipcov:
		# Get the covariance matrix
		output_file = output_dir + "/" + output_covar_filename
		covar = get_covar(num_processes, num_files)
		covar_df = pd.DataFrame(covar, columns=list(avg.keys()), index=list(avg.keys())) # Convert to dataframe
		covar_df.to_hdf(output_file, key='covar', mode='w', complevel=1) # We'll use some compression for this large matrix
		del covar_df # Free up memory
		print("FINISHED COVARIANCE")
		# Get the standard deviation
		output_file = output_dir + "/" + output_avg_stddev_filename
		stt = pd.Series(np.diagonal(covar)**0.5, index=list(avg.keys())) # No attribute columns
		stt.to_hdf(output_file, key='sd')
		print("FINISHED STANDARD DEVIATION")
	else:
		# Calculate SD without the covariance matrix
		stt = get_stddev(num_files)
		output_file = output_dir + "/" + output_avg_stddev_filename
		stt.to_hdf(output_file, key='sd')
	# Get the frequencies
	output_file = output_dir + "/" + output_freq_y_filename
	freq_y = get_freq_y() # Response variable files are small so no need for multiprocessing
	freq_y.to_hdf(output_file, key='freq_y', mode='w')
	print("FINISHED FREQUENCIES")

if __name__ == "__main__":
   main(sys.argv[1:])

