#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

# [5] "lpch_lab_result_121219.csv"
# [1] "ANON_ID"                "PAT_ENC_CSN_ID_CODED"
# [3] "ORDER_ID_CODED"         "ORDER_TIME_JITTERED"
# [5] "TAKEN_TIME_JITTERED"    "RESULT_TIME_JITTERED"
# [7] "COMPONENT_ID"           "LINE"
# [9] "ORDER_TYPE"             "PROC_CODE"
# [11] "GROUP_LAB_NAME"         "LAB_NAME"
# [13] "BASE_NAME"              "ORD_VALUE"
# [15] "ORD_NUM_VALUE"          "REFERENCE_LOW"
# [17] "REFERENCE_HIGH"         "REFERENCE_UNIT"
# [19] "RESULT_IN_RANGE_YN"     "RESULT_FLAG"
# [21] "AUTH_PROV_MAP_ID"       "ORDERING_MODE"
# [23] "EXTENDED_VALUE_COMMENT" "EXTENDED_COMP_COMMENT"
# [25] "DATA_SOURCE"

# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'

# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_lab_result_121219.csv'
csv_path = '/Users/jonc101/Downloads/lpch_lab_result_121219.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'lab_result'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('TAKEN_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('COMPONENT_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LINE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_TYPE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('GROUP_LAB_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LAB_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BASE_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORD_VALUE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORD_NUM_VALUE', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERENCE_LOW', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERENCE_HIGH', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERENCE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_IN_RANGE_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_FLAG', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AUTH_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_MODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('EXTENDED_VALUE_COMMENT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('EXTENDED_COMP_COMMENT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('TAKEN_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('COMPONENT_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LINE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_TYPE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROC_CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('GROUP_LAB_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LAB_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BASE_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORD_VALUE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORD_NUM_VALUE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERENCE_LOW', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERENCE_HIGH', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFERENCE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_IN_RANGE_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESULT_FLAG', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AUTH_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_MODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('EXTENDED_VALUE_COMMENT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('EXTENDED_COMP_COMMENT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

if __name__ == '__main__':
    logging.basicConfig()
    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        bq_client.reconnect_client()
        bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                    schema=FINAL_TABLE_SCHEMA, skip_rows=1)

    #print('Done')
