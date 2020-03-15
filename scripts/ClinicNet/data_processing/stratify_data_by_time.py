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
        rows_to_keep = None
        if remove_greater:
                rows_to_keep = list(data_s.loc[data_s.loc[:,"item_date"] < date_threshold,:].index)
        else:
                rows_to_keep = list(data_s.loc[data_s.loc[:,"item_date"] >= date_threshold,:].index)
        data_s = data_s.loc[rows_to_keep,:]
        data_x = data_x.loc[rows_to_keep,:]
        data_y = data_y.loc[rows_to_keep,:]

        # Write output to file
        data_x.to_hdf(output_dir + "/" + f, key='data_x', mode='w', complevel=1)
        data_s.to_hdf(output_dir + "/" + f, key='data_s', complevel=1)
        data_y.to_hdf(output_dir + "/" + f, key='data_y', complevel=1)

        # Garbage collection
        del data_x
        del data_y
        del data_s
        gc.collect()

def main(argv):
        global files_list # Input directory (where the HDF5 files are stored)
        global data_dir
        global output_dir
        global date_threshold # Date timestamp threshold as nanoseconds since epoch
        global remove_greater # If true, removes rows with timestamp >= threshold. Otherwise, removes rows w/ timestamp < threshold.
        data_dir = ""
        output_dir = ""
        num_processes = 0
        date_threshold = 0
        remove_greater = False
        try:
                opts, args = getopt.getopt(argv,"hi:o:t:p:g")
        except getopt.GetoptError:
                print('stratify_data_by_time.py -i <data_directory> -o <output_dir> -t <timestamp> [-p num_processes] [-g] [-h]')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('stratify_data_by_time.py -i <data_directory> -o <output_dir> -t <timestamp> [-p num_processes] [-g] [-h]')
                        print('')
                        print('This script performs processes data files (in HDF5 format), from <data_directory>, to filter rows based on date nanoseconds-since-epoch timestamp <timestamp>.')
                        print('The new data will be outputed to data files in <output_dir>.')
                        print('Use -g to specify removal of rows with timestamp >= threshold; otherwise rows with timestamp < threshold will be removed.')
                        print('Use num_processes to specify the number of processes to use for multiprocessing.')
                        sys.exit()
                elif opt == '-i':
                        data_dir = arg
                elif opt == '-o':
                        output_dir = arg
                elif opt == '-t':
                        date_threshold = int(arg)
                elif opt == '-p':
                        num_processes = int(arg)
                elif opt == '-g':
                        remove_greater = True
        if len(argv) < 3 or data_dir == '' or output_dir == '' or date_threshold <= 0:
                print('stratify_data_by_time.py -i <data_directory> -o <output_dir> -t <timestamp> [-p num_processes] [-g] [-h]')
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
