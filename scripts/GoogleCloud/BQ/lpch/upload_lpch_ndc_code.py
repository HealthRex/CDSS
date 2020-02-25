#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

# [7] "lpch_ndc_code.csv"

# [1] "MEDICATION_ID"    "LINE"             "NDC_CODE"
# [4] "NDC_ID"           "NDC_FORMAT"       "RAW_11_DIGIT_NDC"
# [7] "MFG_LONG_NAME"    "MFG_CODE"         "PACKAGE_SIZE"
# [10] "MED_UNIT_C"       "UNIT"             "SIMPLE_GENERIC_C"
# [13] "SIMPLE_GENERIC"   "DATA_SOURCE"

# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_ndc_code.csv'
csv_path = '/Users/jonc101/Downloads/lpch_ndc_code.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'ndc_code'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('MEDICATION_ID', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('LINE', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('NDC_CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('NDC_ID', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('NDC_FORMAT', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RAW_11_DIGIT_NDC', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MFG_LONG_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MFG_CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PACKAGE_SIZE', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_UNIT_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIMPLE_GENERIC_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIMPLE_GENERIC', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('MEDICATION_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('LINE', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('NDC_CODE', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('NDC_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('NDC_FORMAT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RAW_11_DIGIT_NDC', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MFG_LONG_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MFG_CODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PACKAGE_SIZE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_UNIT_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIMPLE_GENERIC_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIMPLE_GENERIC', 'STRING', 'NULLABLE', None, ()),
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
