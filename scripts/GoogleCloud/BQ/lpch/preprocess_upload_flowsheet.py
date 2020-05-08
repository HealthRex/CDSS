import os
import glob
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery
import pandas as pd
from os import listdir
from os.path import isfile, join

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

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

file_match = glob.glob('/Users/jonc101/Documents/lpch_auto/flowsheets/flowsheet2012/flowsheet_*')
file_prefix = '/Users/jonc101/Documents/lpch_auto/flowsheets/flowsheet2012/flowsheet_'
CSV_FILE_PREFIX = file_prefix
file_prefix_list = []

for file in file_match:
	file_prefix_list.append(remove_prefix(file, file_prefix))
file_prefix_list = sorted(file_prefix_list)
print(file_prefix_list)


DATASET_NAME = 'lpch'
TABLE_NAME = 'flowsheet'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('INPATIENT_DATA_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('LINE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('TEMPLATE', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ROW_DISP_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MEAS_VALUE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECORDED_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ENTRY_USER_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

def load_table(csv_path):
    bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                schema=FINAL_TABLE_SCHEMA, skip_rows=1, append_to_table = True)


if __name__ == '__main__':
  logging.basicConfig()
  #upload = input('Upload? ("y"/"n"): ')
  bq_client = bigQueryUtil.BigQueryClient()
  print('uploading {}aa'.format(CSV_FILE_PREFIX))

  load_table(CSV_FILE_PREFIX + 'aa')
  file_prefix_list.remove('aa')

  for fn in (file_prefix_list):
      print('uploading {}'.format(fn))
      bq_client.reconnect_client()
      bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, CSV_FILE_PREFIX + fn,
                                          auto_detect_schema=False,
                                          schema=FINAL_TABLE_SCHEMA, skip_rows=1, append_to_table=True)
      print('uploaded {}'.format(fn))
