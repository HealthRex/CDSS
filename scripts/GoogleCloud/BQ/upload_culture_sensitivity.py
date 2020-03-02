#!/usr/bin/env python2

import os
import logging
import itertools
import string
import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

CSV_FILE = 'c:\\=== WORK ===\\=== Stanford ===\\csv_uploads\\culture_sensitivity_021320.csv'
DATASET_NAME = 'test_dataset'
TABLE_NAME = 'culture_sensitivity'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('rit_uid', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('order_proc_id_coded', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('line', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('order_time_jittered', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('result_time_jittered', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sens_obs_inst_tm_jittered', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sens_anl_inst_tm_jittered', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('description', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sens_organism_sid', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('organism', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('antibiotic', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('suscept', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sensitivity_value', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sensitivity_units', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sens_status_c', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('sens_ref_range', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('antibio_lnc_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('specimen_source', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('specimen_type', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('source', 'STRING', 'NULLABLE', None, ()),
                      ]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('rit_uid', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('order_proc_id_coded_s', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('line_s', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('order_time_jittered', 'DATETIME', 'NULLABLE', None, ()),
                       bigquery.SchemaField('result_time_jittered', 'DATETIME', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sens_obs_inst_tm_jittered', 'DATETIME', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sens_anl_inst_tm_jittered', 'DATETIME', 'NULLABLE', None, ()),
                       bigquery.SchemaField('description', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sens_organism_sid', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('organism', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('antibiotic', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('suscept', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sensitivity_value', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sensitivity_units', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sens_status_c_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('sens_ref_range', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('antibio_lnc_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('specimen_source', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('specimen_type', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('source', 'STRING', 'NULLABLE', None, ()),
                       ]


def load_alert_table(csv_path):
    assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'

    bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                schema=UPLOAD_TABLE_SCHEMA, skip_rows=1)


if __name__ == '__main__':
    logging.basicConfig()

    '''
    No preprocessing necessary
    '''

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        print('uploading {}'.format(CSV_FILE))
        load_alert_table(CSV_FILE)

    print('Done')

    '''
    expecting 2,110,392 lines from original table
    '''

    '''
    Conversion script in SQL:
create or replace 
table test_dataset.culture_sensitivity
as
select * except(
    order_proc_id_coded_s,
    line_s,
    sens_status_c_s,
    antibio_lnc_id_s
),
case when order_proc_id_coded_s = '' then NULL else cast(order_proc_id_coded_s as INT64) end as order_proc_id_coded,
case when line_s = '' then NULL else cast(line_s as INT64) end as line,
case when sens_status_c_s = '' then NULL else cast(sens_status_c_s as INT64) end as sens_status_c,
case when antibio_lnc_id_s = '' then NULL else cast(antibio_lnc_id_s as INT64) end as antibio_lnc_id,
timestamp(order_time_jittered, 'America/Los_Angeles') as order_time_jittered_utc,
timestamp(result_time_jittered, 'America/Los_Angeles') as result_time_jittered_utc,
timestamp(sens_obs_inst_tm_jittered, 'America/Los_Angeles') as sens_obs_inst_tm_jittered_utc,
timestamp(sens_anl_inst_tm_jittered, 'America/Los_Angeles') as sens_anl_inst_tm_jittered_utc
from test_dataset.culture_sensitivity;
    '''
