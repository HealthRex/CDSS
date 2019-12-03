#!/usr/bin/env python2

import os
import logging
import itertools
import string
import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

CSV_FILE_PREFIX = '/path/to/jc_alert_history_reformatted_missed_contact_dates_fixed_'
DATASET_NAME = 'alert_2019'
TABLE_NAME = 'alert_history'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('alt_id_jittered', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('alt_csn_id_coded', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('alt_status_c', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('alt_status_c_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('was_shown_c', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('was_shown_c_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('bpa_trgr_action_c', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('bpa_trgr_action_c_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('shown_place_c', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('shown_place_c_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('contact_date', 'DATE', 'NULLABLE', None, ()),
                      bigquery.SchemaField('alt_action_inst', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('user_id', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('patient_dep_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('department_name', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('alt_group_info', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('alt_id_jittered_s', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('alt_csn_id_coded_s', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('alt_status_c_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('alt_status_c_name', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('was_shown_c_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('was_shown_c_name', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('bpa_trgr_action_c_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('bpa_trgr_action_c_name', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('shown_place_c_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('shown_place_c_name', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('contact_date_time', 'DATETIME', 'NULLABLE', None, ()),
                       bigquery.SchemaField('alt_action_inst', 'DATETIME', 'NULLABLE', None, ()),
                       bigquery.SchemaField('user_id', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('patient_dep_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('department_name', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('alt_group_info', 'STRING', 'NULLABLE', None, ())]


def load_alert_table(csv_path):
    assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'

    bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                schema=UPLOAD_TABLE_SCHEMA, skip_rows=1)


if __name__ == '__main__':
    logging.basicConfig()

    '''
    CSV dates are in MM-DD-YYYY format, but bigquery requires YYYY-MM-DD:
    cat jc_alert_history.csv | sed -e 's/\(.*\)\([0-9][0-9]\)-\([0-9][0-9]\)-\([0-9]\{4\}\)\(.*\)\([0-9][0-9]\)-\([0-9][0-9]\)-\([0-9]\{4\}\)\(.*\)/\1\4-\2-\3\5\8-\6-\7\9/g' > jc_alert_history_reformatted.csv
    
    CSV contact_date only rows conversion:
    cat jc_alert_history_reformatted.csv | sed -e 's/^\(.*\)\([0-9][0-9]\)-\([0-9][0-9]\)-\([0-9]\{4\}\)\(.*\)$/\1\4-\2-\3\5/g' > jc_alert_history_reformatted_missed_contact_dates_fixed.csv
    
    split every 2 mln lines:
    split -l 2000000 jc_alert_history_reformatted_missed_contact_dates_fixed.csv jc_alert_history_reformatted_missed_contact_dates_fixed_
    
    
    Remove last line:
    tail -n +1 jc_alert_history_reformatted_missed_contact_dates_fixed_df | head -n -1 > jc_alert_history_reformatted_missed_contact_dates_fixed_df2 
    '''

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        print('uploading {}aa'.format(CSV_FILE_PREFIX))
        load_alert_table(CSV_FILE_PREFIX + 'aa')
        for fn in ([x + y for x, y in itertools.product('a', string.ascii_lowercase[1:])] +
                   [x + y for x, y in itertools.product('b', string.ascii_lowercase)] +
                   [x + y for x, y in itertools.product('c', string.ascii_lowercase)] +
                   [x + y for x, y in itertools.product('d', string.ascii_lowercase[:6])]):
            print('uploading {}'.format(CSV_FILE_PREFIX + fn))
            bq_client.reconnect_client()
            bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, CSV_FILE_PREFIX + fn,
                                        auto_detect_schema=False,
                                        schema=None, skip_rows=0, append_to_table=True)

    print('Done')

    '''
    expecting 167,059,744 lines from original table
    '''

    '''
    Conversion script in SQL:
create or replace 
table alert_2019.alert_history
as
select * except(
    alt_id_jittered_s,
    alt_csn_id_coded_s,
    alt_status_c_s,
    was_shown_c_s,
    bpa_trgr_action_c_s,
    shown_place_c_s,
    patient_dep_id_s,
    contact_date_time
),
case when alt_id_jittered_s = '' then NULL else cast(alt_id_jittered_s as INT64) end as alt_id_jittered,
case when alt_csn_id_coded_s = '' then NULL else cast(alt_csn_id_coded_s as INT64) end as alt_csn_id_coded,
case when alt_status_c_s = '' then NULL else cast(alt_status_c_s as INT64) end as alt_status_c,
case when was_shown_c_s = '' then NULL else cast(was_shown_c_s as INT64) end as was_shown_c,
case when bpa_trgr_action_c_s = '' then NULL else cast(bpa_trgr_action_c_s as INT64) end as bpa_trgr_action_c,
case when shown_place_c_s = '' then NULL else cast(shown_place_c_s as INT64) end as shown_place_c,
case when patient_dep_id_s = '' then NULL else cast(patient_dep_id_s as INT64) end as patient_dep_id,
cast(contact_date_time as DATE) as contact_date,
timestamp(alt_action_inst, 'America/Los_Angeles') as alt_action_inst_utc
from alert_2019.alert_history;
    '''
