#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

# [6] "lpch_mar_121319.csv"

# [1] "ANON_ID"                 "PAT_ENC_CSN_ID_CODED"
# [3] "ORDER_MED_ID_CODED"      "TAKEN_TIME_JITTERED"
# [5] "SCHEDULED_TIME_JITTERED" "MAR_TIME_SOURCE_C"
# [7] "MAR_ACTION_C"            "MAR_ACTION"
# [9] "SIG"                     "ROUTE_C"
# [11] "ROUTE"                   "REASON_C"
# [13] "REASON"                  "SITE_C"
# [15] "SITE"                    "INFUSION_RATE"
# [17] "MAR_INF_RATE_UNIT_C"     "MAR_INF_RATE_UNIT"
# [19] "DOSE_UNIT_C"             "DOSE_UNIT"
# [21] "MAR_DURATION"            "MAR_DURATION_UNIT_C"
# [23] "MAR_DURATION_UNIT"       "DATA_SOURCE"


# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_mar_121319.csv'
csv_path = '/Users/jonc101/Downloads/lpch_mar_121319.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'mar'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_MED_ID_CODED', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('TAKEN_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SCHEDULED_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_TIME_SOURCE_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_ACTION_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_ACTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIG', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ROUTE_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ROUTE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REASON_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REASON', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SITE_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SITE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('INFUSION_RATE', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_INF_RATE_UNIT_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_INF_RATE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_DURATION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_DURATION_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_DURATION_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('ORDER_MED_ID_CODED', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('TAKEN_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SCHEDULED_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_TIME_SOURCE_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_ACTION_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_ACTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIG', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ROUTE_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ROUTE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REASON_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REASON', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SITE_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SITE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('INFUSION_RATE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_INF_RATE_UNIT_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_INF_RATE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_DURATION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_DURATION_UNIT_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAR_DURATION_UNIT', 'STRING', 'NULLABLE', None, ()),
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
