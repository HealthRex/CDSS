# Gets statistics for the dataset
# Computes mean and standard deviations for each feature
# Additionally, for each response variable, the frequency (i.e. percent) of it being a non-zero value is computed

import numpy as np
import pandas as pd
import os
import tables
import gc
import sys, getopt

# Below are the functions for calculating the average and standard deviations, as well as y frequencies
# Note: NAs are considered as zeros

def get_average(data_dir, transformation=None, exclude_cols_transformation=None):
	files_list = os.listdir(data_dir)
	files_list.sort()
	running_sum = None
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
		current_sum = data_x.sum(axis=0, skipna=True)
		if running_sum is None:
			running_sum = current_sum
		else:
			running_sum = running_sum.add(current_sum)
		del data_x
		gc.collect()
	return (running_sum / float(running_N))

def get_stddev(data_dir, average, transformation=None, exclude_cols_transformation=None):
	files_list = os.listdir(data_dir)
	files_list.sort()
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

def get_freq_y(data_dir):
	files_list = os.listdir(data_dir)
	files_list.sort()
	running_sum = None
	running_N = 0
	for f in files_list:
		print(f)
		data_y = pd.read_hdf(data_dir + "/" + f, 'data_y', mode='r')
		data_y = data_y.clip(upper=1) # Change all numbers greater than 1 to 1's
		running_N += data_y.shape[0]
		current_sum = data_y.sum(axis=0, skipna = True)
		if running_sum is None:
			running_sum = current_sum
		else:
			running_sum = running_sum.add(current_sum)
                del data_y
                gc.collect()
	return (running_sum / float(running_N))

def main(argv):
	# How to transform our data (i.e. log2(x+1)):
	transformation_function = lambda x: np.log2(x+1)

	# Output file names:
	output_avg_stddev_filename = "avg_stddev.hdf5" # name of the output file for avg and std dev
	output_freq_y_filename = "freq_y.hdf5" # name of the output file for y frequencies

	# Read in command line arguments:
	input_dir = ''
	output_dir = ''
	exclude_cols_transformation = None
	try:
		opts, args = getopt.getopt(argv,"hi:o:x:")
	except getopt.GetoptError:
		print('compute_stats.py -i <data_directory> -o <output_directory> [-x features_to_exclude] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
                	print('compute_stats.py -i <data_directory> -o <output_directory> [-x features_to_exclude] [-h]')
			print('')
			print('This script computes the mean and standard deviation of all features, except those in features_to_exclude.')
			print('Additionally, for each response variable, the frequency (i.e. percent) of it being a non-zero value is computed.')
			print('As a result, two output files will be generated: avg_stddev.hdf5 and freq_y.hdf5')
			print('The input files are read from the directory <data_directory>')
			print('For features_to_exclude, supply feature names separated by commas.')
			sys.exit()
		elif opt == '-x':
			exclude_cols_transformation = arg.split(',')
		elif opt == '-i':
			input_dir = arg
		elif opt == '-o':
			output_dir = arg
        if len(argv) < 2 or input_dir == '' or output_dir == '':
                print('compute_stats.py -i <data_directory> -o <output_directory> [-x features_to_exclude] [-h]')
                sys.exit(2)

	# Get the average
	output_file = output_dir + "/" + output_avg_stddev_filename
	avg = get_average(input_dir, transformation_function, exclude_cols_transformation)
	avg.to_hdf(output_file, key='avg', mode='w')
	print("FINISHED AVERAGE")
	# Get the standard deviation
	stt = get_stddev(input_dir, avg, transformation_function, exclude_cols_transformation)
	stt.to_hdf(output_file, key='sd')
	print("FINISHED STANDARD DEVIATION")
	# Get the frequencies
        output_file = output_dir + "/" + output_freq_y_filename
	freq_y = get_freq_y(input_dir)
	freq_y.to_hdf(output_file, key='freq_y', mode='w')

if __name__ == "__main__":
   main(sys.argv[1:])
   
