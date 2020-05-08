#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS
import glob
from medinfo.db.bigquery import bigQueryUtil
import pandas as pd
from google.cloud import bigquery


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

file_match = glob.glob('/Users/jonc101/Downloads/shc/order_processed/sheet_*')
file_prefix = '/Users/jonc101/Downloads/shc/order_processed/sheet_'

CSV_FILE_PREFIX = file_prefix
file_prefix_list = []

for file in file_match:
	file_prefix_list.append(remove_prefix(file, file_prefix))
file_prefix_list = sorted(file_prefix_list)
print(file_prefix_list)






DATASET_NAME = 'shc_test'
TABLE_NAME = 'order_proc'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('order_proc_id_jittered', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('pat_enc_csn_id_jittered', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ordering_date_jittered', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_type_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_id', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_code', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('description', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('display_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('cpt_code', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_class_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('authrzing_prov_id', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERRING_PROV_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_PERF_PROV_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('abnormal_yn', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('lab_status_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_status_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('quantity', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('future_or_stand', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('standing_exp_date', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('standing_occurs', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('standing_orig_occur', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('radiology_sts_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_bgn_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_end_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_inst', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('prov_status_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('stand_interval', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('discrete_interval_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('instantiated_time', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_time', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('result_time', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_start_time', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('problem_list_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_ending_time', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('pat_class_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_date', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('chng_order_proc_id', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('last_stand_perf_dt', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('last_stand_perf_tm', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('parent_ce_order_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('initiated_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ordering_mode_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('duration', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('frequency', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('intervention', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('after_order_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('before_order_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('data_source', 'STRING', 'NULLABLE', None, ())]


# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions


if __name__ == '__main__':
    logging.basicConfig()
    bq_client = bigQueryUtil.BigQueryClient()
    bq_client.reconnect_client()
    for fn in (file_prefix_list):
         print('uploading {}'.format(fn))
         bq_client.reconnect_client()
         bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, CSV_FILE_PREFIX + fn,
                                             auto_detect_schema=False,
                                             schema=FINAL_TABLE_SCHEMA, skip_rows=1, append_to_table=True)

    print('Done')
