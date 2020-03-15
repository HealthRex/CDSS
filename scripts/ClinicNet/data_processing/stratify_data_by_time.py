# Takes HDF5 data files and remove items based on an item_date threshold

import pandas as pd
import numpy as np
import os
import gc
import sys, getopt
import multiprocessing

def remove_items(f):
        date_threshold = 1325376000000000000
        remove_greater = True
        
        data_s = pd.read_hdf(data_dir + "/" + f, 'data_s')
        data_x = pd.read_hdf(data_dir + "/" + f, 'data_x')
        data_y = pd.read_hdf(data_dir + "/" + f, 'data_y')
        data_s = data_s.reset_index(drop=True)
        data_x = data_x.reset_index(drop=True)
        data_y = data_y.reset_index(drop=True)
        
        rows_to_remove = None
        if remove_greater:
                rows_to_remove = list(data_s.loc[data_s.loc[:,"item_date"] >= date_threshold,:].index)
        else:
                rows_to_remove = list(data_s.loc[data_s.loc[:,"item_date"] < date_threshold,:].index)

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
                print('add_dates.py -i <data_directory> -d <patient_itemdate_mapping_file> [-p num_processes] [-h]')
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print('add_dates.py -i <data_directory> -d <patient_itemdate_mapping_file> [-p num_processes] [-h]')
                        print('')
                        print('This script performs processes data files (in HDF5 format), from <data_directory>, to add item_date timestamps based on an patient item to item date mapping file.')
                        print('The new data will be appended to existing data files in <data_directory>.')
                        print('One hdf5 file nees to be specified:')
                        print('1. <patient_itemdate_mapping_file>: data frame of patient items with columns being item_date (as nanoseconds since epoch) and patient_item_id')
                        print('Use num_processes to specify the number of processes to use for multiprocessing.')
                        sys.exit()
                elif opt == '-i':
                        data_dir = arg
                elif opt == '-p':
                        num_processes = int(arg)
                elif opt == '-d':
                        dates_dir = arg
        if len(argv) < 2 or data_dir == '' or dates_dir == '':
                print('add_dates.py -i <data_directory> -d <patient_itemdate_mapping_file> [-p num_processes] [-h]')
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
        pool.map(add_dates, files_list)

if __name__ == "__main__":
   main(sys.argv[1:])
