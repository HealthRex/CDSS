'''
1. num_features: Read frequency files for medications, diagnosis and procedure select top-n features. 
2. For each patient in medication file:
	a. Read their medication
	b. Iterate through their timestamps.
	c. Form a m by n matrix where m is the number of timestamps and n is the top-n features
3 Repeat step 2 for diagnosis and procedure

'''
import utils.create_stationary as sta
import argparse
import os
import pdb
import sys
import logging


# pdb.set_trace()
sys.path.append(os.getcwd())
parser = argparse.ArgumentParser()

parser.add_argument("--logging_milestone", type=int, default=1000)    
# logging.basicConfig(format='Date-Time : %(asctime)s : Line No. : %(lineno)d - %(message)s', level = logging.INFO, filename = 'log/logfile_create_stationary.log', filemode = 'a')


parser.add_argument("--top_n_med", type=int, default=100)    
parser.add_argument("--top_n_proc", type=int, default=100)    
parser.add_argument("--top_n_ccs", type=int, default=100)    
parser.add_argument("--top_n_lab", type=int, default=100)    


parser.add_argument("--diagnosis_file_path", type=str, default='intermediate_files/diagnosis_codes.csv')    
parser.add_argument("--medication_file_path", type=str, default='intermediate_files/medication_codes.csv')    
parser.add_argument("--procedure_file_path", type=str, default='intermediate_files/procedure_codes.csv')    
parser.add_argument("--lab_file_path", type=str, default='intermediate_files/lab_codes.csv')    
parser.add_argument("--demographic_file_path", type=str, default='intermediate_files/metadata.csv')    


parser.add_argument("--ccs_frequencies_mci_path", type=str, default='intermediate_files/ccs_frequencies.csv')    
parser.add_argument("--pharm_class_frequencies_mci_path", type=str, default='intermediate_files/pharm_class_frequencies.csv')    
parser.add_argument("--procedure_id_frequencies_mci_path", type=str, default='intermediate_files/procedure_id_frequencies.csv')    
parser.add_argument("--lab_id_frequencies_mci_path", type=str, default='intermediate_files/labs_id_frequencies.csv')    


sta.create_stationary(parser.parse_args().diagnosis_file_path
						,parser.parse_args().medication_file_path
						,parser.parse_args().procedure_file_path
						,parser.parse_args().lab_file_path
						,parser.parse_args().demographic_file_path
						,parser.parse_args().ccs_frequencies_mci_path
						,parser.parse_args().pharm_class_frequencies_mci_path
						,parser.parse_args().procedure_id_frequencies_mci_path
						,parser.parse_args().lab_id_frequencies_mci_path
						,parser.parse_args().top_n_ccs							 
						,parser.parse_args().top_n_med
						,parser.parse_args().top_n_proc
						,parser.parse_args().top_n_lab							 
						,parser.parse_args().logging_milestone
						)

