# Performs univariate feature selection by removing low or zero variance features
# Also removes features that we specify to be removed

import pandas as pd
import numpy as np
import tables
import os
import multiprocessing
import gc
import sys, getopt

def feature_selection_worker(fname):
	print(fname)
	data_x = pd.read_hdf(data_dir + "/" + fname, 'data_x', mode='r')
	data_x = data_x.drop(features_to_remove, axis=1)
	data_y = pd.read_hdf(data_dir + "/" + fname, 'data_y', mode='r')
	data_s = None
	try:
		data_s = pd.read_hdf(data_dir + "/" + fname, 'data_s', mode='r')
	except KeyError:
		data_s = None
	data_x.to_hdf(output_dir + "/" + fname, 'data_x', complevel=1, mode='w')
	data_y.to_hdf(output_dir + "/" + fname, 'data_y', complevel=1)
	if not (data_s is None):
		data_s.to_hdf(output_dir + "/" + fname, 'data_s', complevel=1)
		del data_s
	del data_x
	del data_y
	gc.collect()

def data_remove_features(num_processes=1):
	files_list = os.listdir(data_dir)
	print("Feature selection data files in " + data_dir + " and outputting them to " + output_dir)
	pool = multiprocessing.Pool(num_processes)
	pool.map(feature_selection_worker, files_list)

def identify_lowvar_features(std_dev, std_dev_threshold):
	features = list(std_dev.keys())
	zero_var = list(set(range(0, len(std_dev))) - set(list(np.nonzero(std_dev > std_dev_threshold)[0])))
	return list(std_dev[zero_var].keys()).tolist()

def main(argv):
	# Read in command line arguments:
	global output_dir
	global features_to_remove
	global data_dir
	data_dir = ''
	stats_dir = ''
	output_dir = ''
	manually_remove = None
	num_processes = 0
	std_dev_threshold = np.float64(0.0)
	try:
		opts, args = getopt.getopt(argv,"hi:o:s:t:r:p:")
	except getopt.GetoptError:
		print('feature_selection.py -i <data_directory> -o <output_directory> -s <stats_dir> [-t threshold] [-r features_to_remove] [-p num_processes] [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('feature_selection.py -i <data_directory> -o <output_directory> -s <stats_dir> [-t threshold] [-r features_to_remove] [-p num_processes] [-h]')
			print('')
			print('This script performs feature selection to remove near zero variance features, defined by standard deviation threshold, and features specified by a comma-delimited list in features_to_remove.')
			print('The new data with the features removed will be stored in <output_directory>.')
			print('Additionally, two files in <stats_dir> (from which we get averages and standard deviations) will be created: avg_stddev_featureselected.hdf5 and covar_featureselected.hdf5')
			print('The input files are read from the directory <data_directory>')
			print('Use num_processes to specify the number of processes to use for multiprocessing.')
			sys.exit()
		elif opt == '-r':
			manually_remove = arg.split(',')
		elif opt == '-i':
			data_dir = arg
		elif opt == '-o':
			output_dir = arg
		elif opt == '-p':
			num_processes = int(arg)
		elif opt == '-t':
			std_dev_threshold = np.float64(arg)
		elif opt == '-s':
			stats_dir = arg
	if len(argv) < 3 or data_dir == '' or output_dir == '' or stats_dir == '':
		print('feature_selection.py -i <data_directory> -o <output_directory> -s <stats_dir> [-t threshold] [-r features_to_remove] [-p num_processes] [-h]')
		sys.exit(2)

	# Configure multiprocessing
	if num_processes == 0:
		num_processes = multiprocessing.cpu_count()-1
	print("Number of processes: " + str(num_processes))

	# Curating features to be removed
	std_dev = pd.read_hdf(stats_dir + "/" + "avg_stddev.hdf5", 'sd')
	lowvar_features = identify_lowvar_features(std_dev, std_dev_threshold)
	features_to_remove = lowvar_features + manually_remove
	features_to_remove = list(set(features_to_remove) & set(list(std_dev.keys()).tolist())) # Remove manually_remove elements that aren't also in std_dev
	print("{} features out of {} to be removed (SD threshold: {})".format(len(features_to_remove), len(list(std_dev.keys()).tolist()), std_dev_threshold))

	# Processing the data to remove selected features
	data_remove_features(num_processes)

	# Getting the feature-selected version of the statistics and outputting them
	print("Done with data files; now creating new statistics files")
	std_dev = std_dev[~std_dev.index.isin(features_to_remove)]
	avg = pd.read_hdf(stats_dir + "/" + "avg_stddev.hdf5", 'avg')
	avg = avg[~avg.index.isin(features_to_remove)]
	covar = pd.read_hdf(stats_dir + "/" + "covar.hdf5", 'covar')
	covar = covar.drop(features_to_remove, axis=1)
	covar = covar.drop(features_to_remove, axis=0)
	avg.to_hdf(stats_dir + "/" + "avg_stddev_featureselected.hdf5", 'avg', mode='w')
	std_dev.to_hdf(stats_dir + "/" + "avg_stddev_featureselected.hdf5", 'sd')
	covar.to_hdf(stats_dir + "/" + "covar_featureselected.hdf5", 'covar', mode='w', complevel=1)

if __name__ == "__main__":
   main(sys.argv[1:])
