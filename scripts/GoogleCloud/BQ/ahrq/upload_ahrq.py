#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
#CSV_FILE_PREFIX = '/Users/jonc101/Downloads/ahrq_ccs4.csv'
csv_path = '/Users/jonc101/Downloads/ahrq_ccs4.csv'

DATASET_NAME = 'ahrq'
TABLE_NAME = 'ahrq_codes'

 # 'icd_10',
 # 'ccs_category',
 # 'icd_code_description',
 # 'ccs_category_description',
 # 'multi_ccs_lvl_1',
 # 'multi_ccs_lvl_1_label',
 # 'multi_ccs_lvl_2',
 # 'multi_ccs_lvl_2_label')

FINAL_TABLE_SCHEMA = [bigquery.SchemaField('CODE', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('ccs_category', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('ccs_category_description', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('multi_ccs_lvl_1', 'INT64', 'NULLABLE', None, ()),
                       bigquery.SchemaField('multi_ccs_lvl_1_label', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('CODE_TYPE', 'STRING', 'NULLABLE', None, ())]                       
                       #bigquery.SchemaField('multi_ccs_lvl_2', 'FLOAT64', 'NULLABLE', None, ()),
                       #bigquery.SchemaField('multi_ccs_lvl_2_label', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions


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

RSCRIPT TO CLEAN DATA FOR REFERENCE

library(dplyr)

# change directory
setwd('~/Downloads/')
ccs <- read.csv('ccs_pr_icd10pcs_2020_1/ccs_pr_icd10pcs_2020_1.csv')

# function to remove commas
remove_comma <- function(x){
  return(gsub("," ," ",x))
}

ccs_colnames <- c('CODE',
  'ccs_category',
  'DESCRIPTION',
  'ccs_category_description',
  'multi_ccs_lvl_1',
  'multi_ccs_lvl_1_label',
  'multi_ccs_lvl_2',
  'multi_ccs_lvl_2_label')

colnames(ccs) <- ccs_colnames

ccs2 <- ccs %>% select(CODE, ccs_category, DESCRIPTION, ccs_category_description,
                       multi_ccs_lvl_1, multi_ccs_lvl_1_label)

ccs3 <- sapply(ccs2, remove_comma)
#colnames(ccs) <- ccs_colnames
write.csv(ccs3,'ahrq_ccs4.csv')

'''
