import sys
import numpy as np
import tensorflow as tf
import pandas as pd
import argparse
import h5py

sys.path.insert(0,'rnn_utils')
import utils
import load_and_format_data as lfd

def main(argv):

    parser = argparse.ArgumentParser(description='Command line parser for train_rnn.py ')
    parser.add_argument('--raw_data_dir',type=str,default='/home/ec2-user/cs230/scripts/matrix/final_data_031618_v2/',
                        help='path to the raw data from the healthrex database pull')
    parser.add_argument('--nfiles',type=int,default=1,
                        help='number of files to load, -1 if all')    
    parser.add_argument('--clean_data_dir',type=str,default='/home/ec2-user/cs230/scripts/DeepLearning/RNN/data_final/',
                        help='path to clean data output directory')
    parser.add_argument('--skip_clean_raw_data', dest='skip_clean_raw_data', action='store_true',
                        help='convert raw data to features/responses in one matrix')
    parser.add_argument('--skip_generate_sets',dest='skip_generate_sets',action='store_true',
                        help='generate train/dev/test sets')
    parser.add_argument('--rnn_data_path',type=str,default='rnn_data_',
                        help='name of clean rnn_data file')


    args = parser.parse_args()
    if args.skip_clean_raw_data is False: #Cleaning raw .txt data from database query
        lfd.clean_raw_data(args.raw_data_dir,nfiles=args.nfiles,data_out_dir=args.clean_data_dir)

    if args.skip_generate_sets is False: #Generate train/dev/test sets
        lfd.make_train_dev_test_v2(args.clean_data_dir,in_prefix=args.rnn_data_path,nfiles=args.nfiles)


    return



if __name__ == '__main__':
    main(sys.argv[1:])


