import os
import glob
import os
import logging
import itertools
import string
import  numpy  as np
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery
import pandas as pd
from os import listdir
from os.path import isfile, join
import re


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def count_alphabet(input_row):
    d = []
    for i in  string.ascii_lowercase:
        d.append(input_row.count(i))
    return sum(d)

def non_numeric_sub(string):
    return re.sub("[^0-9.-]", "", string)


file_match = glob.glob('/Users/jonc101/Documents/lpch_auto/flowsheets/flowsheet2012/flowsheet_*')
file_prefix = '/Users/jonc101/Documents/lpch_auto/flowsheets/flowsheet2012/flowsheet_'

file_prefix_list = []

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

for file in file_match:
	file_prefix_list.append(remove_prefix(file, file_prefix))
file_prefix_list = sorted(file_prefix_list)
print(file_prefix_list)

for file in file_prefix_list:
    print('-----------------')
    print('reading file in:')
    print('-----------------')
    print(file_prefix + file)
    print('-----------------')
    if file == 'aa':

        c  = pd.read_csv(file_prefix + file, sep='\t')
        c['meas_value'] = c['meas_value'].apply(str)
        c['meas_value'] = c['meas_value'].apply(non_numeric_sub)
        c['entry_user_id'] = c['entry_user_id'].apply(str)
        c['entry_user_id'] = c['entry_user_id'].apply(non_numeric_sub)
        # remove potential numbers:
        c['meas_length'] = c['meas_value'].apply(len)
        c[(c.meas_length < 10)]
        c = c.drop('meas_length',1)
        c.to_csv(file_prefix + file, encoding='utf-8', index=False)


    else:
        c  = pd.read_csv(file_prefix + file, sep='\t',header = None)
        c[5] = c[5].apply(str)
        c[5] = c[5].apply(non_numeric_sub)
        c[7] = c[7].apply(str)
        c[7] = c[7].apply(non_numeric_sub)
        # remove potential numbers:
        c['meas_length'] = c[5].apply(len)
        c[(c.meas_length < 10)]
        c = c.drop('meas_length',1)
        c.to_csv(file_prefix + file, encoding='utf-8', index=False)
    print('-----------------')
    print('processed file')
    print('-----------------')
    print(file_prefix + file)
    print('-----------------')
