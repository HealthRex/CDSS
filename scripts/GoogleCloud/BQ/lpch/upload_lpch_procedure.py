#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:


# $lpch_procedure_101219.csv
# [1] "ANON_ID"                "LINE"
# [3] "PAT_ENC_CSN_ID_CODED"   "PX_ID"
# [5] "CODE"                   "DESCRIPTION"
# [7] "CODE_TYPE"              "START_DATE_JITTERED"
# [9] "PROC_DATE_JITTERED"     "ADM_DATE_TIME_JITTERED"
# [11] "PERF_PROV_MAP_ID"       "BILLING_PROV_MAP_ID"
# [13] "ENTRY_PROV_MAP_ID"      "DEP_MAP_ID"
# [15] "SOURCE"                 "DATA_SOURCE"


# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_procedure_101219.csv'
csv_path = '/Users/jonc101/Downloads/lpch_procedure_101219.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'procedure'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('LINE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PX_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CODE_TYPE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('START_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ADM_DATE_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PERF_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ENTRY_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DEP_MAP_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SOURCE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('LINE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PX_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CODE_TYPE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('START_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ADM_DATE_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PERF_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ENTRY_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DEP_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SOURCE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

if __name__ == '__main__':
    logging.basicConfig()
    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        bq_client.reconnect_client()
        bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                    schema=FINAL_TABLE_SCHEMA, skip_rows=1)

    print('Done')
