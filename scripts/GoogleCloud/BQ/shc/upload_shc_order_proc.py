#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:



# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_order_med_121319.csv'
csv_path = '/Users/jonc101/Downloads/lpch_order_med_121319.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'order_med'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('order_proc_id_jittered', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('pat_enc_csn_id_jittered', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('order_type_name', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_id', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_code', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('description', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('display_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('cpt_code', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_class_name', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('authrzing_prov_id', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERRING_PROV_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_PERF_PROV_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('abnormal_yn', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('lab_status_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_status_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('quantity', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('future_or_stand', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('standing_exp_date', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('standing_occurs', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('standing_orig_occur', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('radiology_sts_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_bgn_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_end_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_inst', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('prov_status_name', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('stand_interval', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('discrete_interval_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('instantiated_time', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('order_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('result_time', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_start_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('problem_list_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_ending_time', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('pat_class_name', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('proc_date', 'FLOAT64', 'NULLABLE', None, ()),
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
                      bigquery.SchemaField('before_order_id', 'STRING', 'NULLABLE', None, ())]


# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions


if __name__ == '__main__':
    logging.basicConfig()

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        bq_client.reconnect_client()
        bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                    schema=FINAL_TABLE_SCHEMA, skip_rows=1)

    print('Done')
