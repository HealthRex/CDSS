#!/usr/bin/env python2

import os
import logging
import itertools
import string
import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

CSV_FILE_PREFIX = '/path/to/jc_alerts_orders_120619_head_tail_removed_reformatted_quotes_escaped_'
DATASET_NAME = 'alert_2019'
TABLE_NAME = 'alerts_orders'
TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                bigquery.SchemaField('alt_id_coded', 'INT64', 'REQUIRED', None, ()),
                bigquery.SchemaField('order_id_coded', 'INT64', 'NULLABLE', None, ()),
                bigquery.SchemaField('alt_csn_id_coded', 'INT64', 'REQUIRED', None, ()),
                bigquery.SchemaField('line', 'INT64', 'REQUIRED', None, ()),
                bigquery.SchemaField('med_alerts_actn_c', 'INT64', 'NULLABLE', None, ()),
                bigquery.SchemaField('med_alerts_actn_c_name', 'STRING', 'NULLABLE', None, ()),
                bigquery.SchemaField('medication_id', 'INT64', 'NULLABLE', None, ()),
                bigquery.SchemaField('medication_name', 'STRING', 'NULLABLE', None, ())]


def load_alert_table(csv_path):
    assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'

    bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                schema=TABLE_SCHEMA, skip_rows=0)


if __name__ == '__main__':
    logging.basicConfig()

    '''
    CSV remove SQL commands head and tail:
    tail -n +3 jc_alerts_orders_120619.csv | head -n -1 > jc_alerts_orders_120619_head_tail_removed.csv
    
    CSV check line nums are as expected:
    wc -l jc_alerts_orders_120619_head_tail_removed.csv
    
    CSV cleanup command:
    cat jc_alerts_orders_120619_head_tail_removed.csv | sed -e 's/^\(".*"\),"\(.*\)","\(.*\)","\(.*\)","\(.*\)","\(.*\)",\(".*"\),"\(.*\)",\(".*"\)$/\1,\2,\3,\4,\5,\6,\7,\8,\9/g' > jc_alerts_orders_120619_head_tail_removed_reformatted.csv
    
    CSV escape quotes command:
    cat jc_alerts_orders_120619_head_tail_removed_reformatted.csv | sed 's/\([^",]\)"\([^",]\)/\1""\2/g' > jc_alerts_orders_120619_head_tail_removed_reformatted_quotes_escaped.csv
     
    file needs to be split:
    split -l 2000000 jc_<TABLE_NAME>_reformatted.csv jc_<TABLE_NAME>_reformatted_

    example of above:
    split -l 2000000 jc_alerts_orders_120619_head_tail_removed_reformatted_quotes_escaped.csv jc_alerts_orders_120619_head_tail_removed_reformatted_quotes_escaped_
    '''
    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        print('uploading {}aa'.format(CSV_FILE_PREFIX))
        load_alert_table(CSV_FILE_PREFIX + 'aa')
        for fn in ([x + y for x, y in itertools.product('a', string.ascii_lowercase[1:])] +
                   [x + y for x, y in itertools.product('b', string.ascii_lowercase)] +
                   [x + y for x, y in itertools.product('c', string.ascii_lowercase[:2])]):
            print('uploading {}'.format(CSV_FILE_PREFIX + fn))
            bq_client.reconnect_client()
            bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, CSV_FILE_PREFIX + fn,
                                        auto_detect_schema=False,
                                        schema=None, skip_rows=0, append_to_table=True)

    print('Done')

    '''
    expecting 107,202,804 lines from original table
    '''
