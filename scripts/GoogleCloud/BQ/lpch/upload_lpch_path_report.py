#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:


# $lpch_path_report_meta.csv
# [1] "ANON_ID"                   "PAT_ENC_CSN_ID_CODED"
# [3] "ORDER_ID_CODED"            "PROC_CODE"
# [5] "DESCRIPTION"               "ORDERING_DATE_JITTERING"
# [7] "PROC_START_TIME_JITTERING" "PROC_END_TIME_JITTERING"
# [9] "RESULT_TIME_JITTERING"     "ANON_ACCESSION_NUMBER"
# [11] "AUTHRZING_PROV_MAP_ID"     "RPT_PRELIM_PROV_MAP_ID"
# [13] "RPT_FINAL_PROV_MAP_ID"     "BILLING_PROV_MAP_ID"
# [15] "REFERRING_PROV_MAP_ID"     "PROC_PERF_PROV_MAP_ID"
# [17] "LAB_STATUS_C"              "LAB_STATUS"
# [19] "ORDER_STATUS_C"            "ORDER_STATUS"
# [21] "DATA_SOURCE"

# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_path_report_meta.csv'
csv_path = '/Users/jonc101/Downloads/lpch_path_report_meta.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'path_report'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PROC_CODE', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_DATE_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_START_TIME_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_END_TIME_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_TIME_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ANON_ACCESSION_NUMBER', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AUTHRZING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RPT_PRELIM_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RPT_FINAL_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERRING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_PERF_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LAB_STATUS_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LAB_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA =[bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_ID_CODED', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PROC_CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_DATE_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_START_TIME_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_END_TIME_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_TIME_JITTERING', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ANON_ACCESSION_NUMBER', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AUTHRZING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RPT_PRELIM_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RPT_FINAL_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERRING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_PERF_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LAB_STATUS_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LAB_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS', 'STRING', 'NULLABLE', None, ()),
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
