#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:


# [4] "lpch_drg_code.csv"
# [1] "ANON_ID"              "PAT_ENC_CSN_ID_CODED" "DRG_MPI_CODE"
# [4] "DRG_NAME"             "DRG_WEIGHT"           "DATA_SOURCE"


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_drg_code.csv'
csv_path = '/Users/jonc101/Downloads/lpch_drg_code.csv'

DATASET_NAME = 'lpch'
TABLE_NAME = 'drg_code'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('DRG_MPI_CODE', 'INT64', 'NULLABLE', None, ()),
                       bigquery.SchemaField('DRG_NAME', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('DRG_WEIGHT', 'FLOAT64', 'NULLABLE', None, ()),
                       bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions

# [1] "ANON_ID"              "PAT_ENC_CSN_ID_CODED" "DRG_MPI_CODE"
# [4] "DRG_NAME"             "DRG_WEIGHT"           "DATA_SOURCE"

UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('DRG_MPI_CODE', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('DRG_NAME', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('DRG_WEIGHT', 'STRING', 'NULLABLE', None, ()),
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
