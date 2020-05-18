# Takes HDF5 data files and remove items based on an item_date threshold

import pandas as pd
import numpy as np
import os
import gc
import sys, getopt
import multiprocessing

def remove_items(f):        
        # Read in data
        data_s = pd.read_hdf(data_dir + "/" + f, 'data_s')
        data_x = pd.read_hdf(data_dir + "/" + f, 'data_x')
        data_y = pd.read_hdf(data_dir + "/" + f, 'data_y')
        data_s = data_s.reset_index(drop=True)
        data_x = data_x.reset_index(drop=True)
        data_y = data_y.reset_index(drop=True)
        
        # Remove data rows based on date threshold
        rows_to_keep1 = list(data_s.loc[data_s.loc[:,"item_date"] >= date_threshold1,:].index)
        rows_to_keep2 = list(data_s.loc[data_s.loc[:,"item_date"] < date_threshold2,:].index)
        rows_to_keep = list(set(rows_to_keep1) & set(rows_to_keep2)) # Intersection
        data_s = data_s.loc[rows_to_keep,:]
        data_x = data_x.loc[rows_to_keep,:]
        data_y = data_y.loc[rows_to_keep,:]

        # Write output to file
        data_x.to_hdf(output_dir + "/" + f, key='data_x', mode='w', complevel=1)
        data_s.to_hdf(output_dir + "/" + f, key='data_s', complevel=1)
        data_y.to_hdf(output_dir + "/" + f, key='data_y', complevel=1)
        print(f)

        # Garbage collection
        del data_x
        del data_y
        del data_s
        gc.collect()

def main(argv):
        global files_list # Input directory (where the HDF5 files are stored)
        global data_dir
        global output_dir
        global date_threshold1 # Date timestamp threshold #1 as nanoseconds since epoch
        global date_threshold2 # Date timestamp threshold #2 as nanoseconds since epoch
        global remove_greater # If true, removes rows with timestamp >= threshold. Otherwise, removes rows w/ timestamp < threshold.
        data_dir = ""
        output_dir = ""
        num_processes = 0
        date_threshold1 = -1
        date_threshold2 = -1
        try:
                opts, args = getopt.getopt(argv,"hi:o:l:g:p:")
        except getopt.GetoptError:
                print('stratify_data_by_time.py -i <data_directory> -o <output_dir> -l <timestamp1> -g <timestamp2> [-p num_processes] [-h]')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('stratify_data_by_time.py -i <data_directory> -o <output_dir> -l <timestamp1> -g <timestamp2> [-p num_processes] [-h]')
                        print('')
                        print('This script performs processes data files (in HDF5 format), from <data_directory>, to select rows based between date nanoseconds-since-epoch timestamps <timestamp1> and <timestamp2>.')
                        print('Timestamp <timestamp1> must be less than <timestamp2>.')
                        print('The new data will be outputed to data files in <output_dir>.')
                        print('Use num_processes to specify the number of processes to use for multiprocessing.')
                        sys.exit()
                elif opt == '-i':
                        data_dir = arg
                elif opt == '-o':
                        output_dir = arg
                elif opt == '-l':
                        date_threshold1 = int(arg)
                elif opt == '-g':
                        date_threshold2 = int(arg)
                elif opt == '-p':
                        num_processes = int(arg)
        if len(argv) < 4 or data_dir == '' or output_dir == '' or date_threshold1 < 0 or date_threshold2 < 0 or date_threshold1 >= date_threshold2:
                print('stratify_data_by_time.py -i <data_directory> -o <output_dir> -l <timestamp1> -g <timestamp2> [-p num_processes] [-h]')
                sys.exit(2)

        # Configure multiprocessing
        if num_processes == 0:
                num_processes = multiprocessing.cpu_count()-1
        print("Number of processes: " + str(num_processes))

        # Iterate through data_dir to process the files
        files_list = os.listdir(data_dir)
        pool = multiprocessing.Pool(num_processes)
        pool.map(remove_items, files_list)

if __name__ == "__main__":
   main(sys.argv[1:])
