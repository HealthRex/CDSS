#!/usr/bin/env python2

import os
import csv
import pandas as pd
import logging
from datetime import datetime, timedelta
import pytz
import itertools
import string

import LocalEnv
from medinfo.dataconversion.Util import log
from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

class LoadAlert:

    @staticmethod
    def add_zone_to_timestamp_col(csv_in_path, csv_out_path, timezone_diff='-07'):
        '''
        pandas method has some caveats, didn't end up using
        '''
        df = pd.read_csv(csv_in_path)
        df[' update_date_jittered'] = df[' update_date_jittered'].apply(lambda x: x + timezone_diff)
        df.to_csv(csv_out_path, index=False, sep=',')

    @staticmethod
    def add_offset_to_timestamp_col(csv_in_path, csv_out_path, timezone_diff=8):

        with open(csv_in_path, 'rb') as csv_in, open(csv_out_path, 'wb') as csv_out:
            next(csv_in)
            next(csv_in)    # skip first 2 rows
            writer = csv.writer(csv_out, lineterminator='\n')
            reader = csv.reader(csv_in)
            for row in reader:
                orig_ts = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                #new_ts = orig_ts + timedelta(hours=timezone_diff)
                new_ts = orig_ts.astimezone(pytz.utc)
                row.append(row[3])
                row[3] = new_ts.strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(row)


    @staticmethod
    def load_alert_table(csv_path):
        bq_client = bigQueryUtil.BigQueryClient()
        assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'

        schema = [ bigquery.SchemaField('anon_id',              'STRING', 'REQUIRED', None, ()),
                   bigquery.SchemaField('alt_id_jittered',      'INT64', 'REQUIRED', None, ()),
                   bigquery.SchemaField('pat_csn_jittered',     'INT64', 'NULLABLE', None, ()),
                   bigquery.SchemaField('update_date_jittered', 'TIMESTAMP', 'REQUIRED', None, ()),
                   bigquery.SchemaField('alert_desc',           'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('general_alt_type_c',   'INT64', 'NULLABLE', None, ()),
                   bigquery.SchemaField('general_alert_name',   'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('general_alert_title',  'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('general_alert_abbr',   'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('med_alert_type_c',     'INT64', 'NULLABLE', None, ()),
                   bigquery.SchemaField('med_alert_name',       'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('med_alert_title',      'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('med_alert_abbr',       'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('immun_id',             'INT64', 'NULLABLE', None, ()),
                   bigquery.SchemaField('immun_name',           'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('immun_abbreviation',   'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('immun_type',           'STRING', 'NULLABLE', None, ()),
                   bigquery.SchemaField('bpa_locator_id',       'INT64', 'NULLABLE', None, ()),
                   bigquery.SchemaField('local_update_date_jittered','DATETIME', 'REQUIRED', None, ())]

        bq_client.load_csv_to_table('alert_2019', 'alert', csv_path, auto_detect_schema=False, \
                              schema=schema, skip_rows=0)


if __name__ == '__main__':
    logging.basicConfig()

    #csv_in_path = input('Enter csv in path: ')
    #csv_out_path = input('Enter csv out path: ')
    #LoadAlert.add_offset_to_timestamp_col(csv_in_path, csv_out_path)

    '''
    needed to split file instead
    split -l 2000000 jc_alerts_mod.csv jc_alerts_mod_
    '''
    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        print('uploading jc_alerts_mod_aa')
        LoadAlert.load_alert_table('/Users/starli/Downloads/jc_alerts_mod_aa')
        for fn in ([x+y for x,y in itertools.product('a', string.ascii_lowercase[1:])] +
                   [x+y for x,y in itertools.product('b', string.ascii_lowercase)] +
                   [x+y for x,y in itertools.product('c', string.ascii_lowercase[:11])]):
            print('uploading jc_alerts_mod_%s' % (fn))
            bq_client.reconnect_client()
            bq_client.load_csv_to_table('alert_2019', 'alert', '/Users/starli/Downloads/jc_alerts_mod_' + fn, \
                                        auto_detect_schema=False, \
                                        schema=None, skip_rows=0, append_to_table=True)
    print('Done')

    '''
    expecting 62,364,707 lines from original table
    '''


