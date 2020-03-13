#!/usr/bin/env python2

import os
import logging
import itertools
import string
import pandas as pd
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-2c5b.json'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='[/PATH/TO/JSON]'.json'

#CSV_FILE_PREFIX = '/Users/jonc101/Downloads/ahrq_ccs4.csv'

DATASET_NAME = 'ahrq'
TABLE_NAME = 'ahrq_diag_codes'

csv_path = '/Users/jonc101/Downloads/ahrq_diag_save.csv'

#'ICD10'
#'ICD10_string'
#'CCSR_CATEGORY_1'
#'CCSR_CATEGORY_2'
#'ICD_10_CODE_Description'
#'Category_Description'
#'Category_1_Description'
#'Category_2_Description'

FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ICD10', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('ICD10_string', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('CCSR_CATEGORY_1', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('CCSR_CATEGORY_2', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('ICD_10_CODE_Description', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('Category_Description', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('Category_1_Description', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('Category_2_Description', 'STRING', 'NULLABLE', None, ())]

if __name__ == '__main__':
    logging.basicConfig()

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        bq_client.reconnect_client()
        bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                    schema=FINAL_TABLE_SCHEMA,
                                    skip_rows=1)
    print('Done')

'''
ahrq = pd.read_csv('/Users/jonc101/Downloads/ahrq_icd10_diagnosis.csv')
ahrq['ICD10_string'] = ahrq["'ICD-10-CM CODE'"]
ahrq['ICD10_string'] = ahrq['ICD10_string'].str.replace("'", '')
ahrq_col2 =  []
num_rows = len(ahrq)
for row in range(0,num_rows):
    ahrq_col2.append(ahrq['ICD10_string'][row][0:3] + '.' + ahrq['ICD10_string'][row][3:])
ahrq['ICD10'] = ahrq_col2
ahrq['CCSR_CATEGORY_1'] = ahrq["'CCSR CATEGORY 1'"].str.replace("'", '')
ahrq['CCSR_CATEGORY_2'] = ahrq["'CCSR CATEGORY 2'"].str.replace("'", '')
ahrq['ICD_10_CODE_Description'] = ahrq["'ICD-10-CM CODE DESCRIPTION'"]
ahrq['Category_Description'] = ahrq["'Default CCSR CATEGORY DESCRIPTION'"]
ahrq['Category_1_Description'] = ahrq["'CCSR CATEGORY 1 DESCRIPTION'"]
ahrq['Category_2_Description'] = ahrq["'CCSR CATEGORY 2 DESCRIPTION'"]
ahrq_save = ahrq[['ICD10',
                  'ICD10_string',
                  'CCSR_CATEGORY_1',
                  'CCSR_CATEGORY_2',
                  'ICD_10_CODE_Description',
                  'Category_Description',
                  'Category_1_Description',
                  'Category_2_Description']]


csv_path = '/Users/jonc101/Downloads/ahrq_icd10_diagnosis.csv'
'''
