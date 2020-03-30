#!/usr/bin/env python2

import os
import credentials
import logging
import itertools
import string
from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery
# Construct a BigQuery client object.


bq_client = bigQueryUtil.BigQueryClient()
dataset_id = "ahrq_ccsr"

if __name__ == '__main__':
    logging.basicConfig()

    create_table = input('Create Table? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if create_table == 'Y' or create_table == 'y':
        bq_client.reconnect_client()
        bq_client.create_new_dataset(dataset_id)
    print('data set run finished')
