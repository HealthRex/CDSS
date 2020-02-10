#!/usr/bin/env python2

import os
import logging
import itertools
import string
import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

CSV_FILE_PREFIX = '/path/to/alt_drug_allergy_020320_'
DATASET_NAME = 'alert_2019'
TABLE_NAME = 'alt_drug_allergy'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('alt_id_jittered', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('alt_csn_id_jittered', 'INT64', 'REQUIRED', None, ()),
                      bigquery.SchemaField('medication_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('allergen_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('allergy_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('drug_intrct_lvl_c', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('cm_ct_owner_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('inact_ingre_ind_yn', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('inact_review_yn', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('alert_root_aller_id', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('alert_med_class_id', 'INT64', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('anon_id', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('alt_id_jittered_s', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('alt_csn_id_jittered_s', 'STRING', 'REQUIRED', None, ()),
                       bigquery.SchemaField('medication_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('allergen_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('allergy_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('drug_intrct_lvl_c_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('cm_ct_owner_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('inact_ingre_ind_yn', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('inact_review_yn', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('alert_root_aller_id_s', 'STRING', 'NULLABLE', None, ()),
                       bigquery.SchemaField('alert_med_class_id_s', 'STRING', 'NULLABLE', None, ())]


def load_alert_table(csv_path):
    assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'

    bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                schema=UPLOAD_TABLE_SCHEMA, skip_rows=1)


if __name__ == '__main__':
    logging.basicConfig()

    '''
    - removed trailing line in vim
    
    split every 2 mln lines:
    split -l 2000000 alt_drug_allergy_020320.csv alt_drug_allergy_020320_
    '''

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        print('uploading {}aa'.format(CSV_FILE_PREFIX))
        load_alert_table(CSV_FILE_PREFIX + 'aa')
        for fn in ([x + y for x, y in itertools.product('a', string.ascii_lowercase[1:8])]):
            print('uploading {}'.format(CSV_FILE_PREFIX + fn))
            bq_client.reconnect_client()
            bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, CSV_FILE_PREFIX + fn,
                                        auto_detect_schema=False,
                                        schema=None, skip_rows=0, append_to_table=True)

    print('Done')

    '''
    expecting 15,734,195 lines from original table
    '''

    '''
    Conversion script in SQL:
create or replace 
table alert_2019.alt_drug_allergy
as
select * except(
    alt_id_jittered_s,
    alt_csn_id_jittered_s,
    medication_id_s,
    allergen_id_s,
    allergy_id_s,
    drug_intrct_lvl_c_s,
    cm_ct_owner_id_s,
    alert_root_aller_id_s,
    alert_med_class_id_s
),
case when alt_id_jittered_s = '' then NULL else cast(alt_id_jittered_s as INT64) end as alt_id_jittered,
case when alt_csn_id_jittered_s = '' then NULL else cast(alt_csn_id_jittered_s as INT64) end as alt_csn_id_jittered,
case when medication_id_s = '' then NULL else cast(medication_id_s as INT64) end as medication_id,
case when allergen_id_s = '' then NULL else cast(allergen_id_s as INT64) end as allergen_id,
case when allergy_id_s = '' then NULL else cast(allergy_id_s as INT64) end as allergy_id,
case when drug_intrct_lvl_c_s = '' then NULL else cast(drug_intrct_lvl_c_s as INT64) end as drug_intrct_lvl_c,
case when cm_ct_owner_id_s = '' then NULL else cast(cm_ct_owner_id_s as INT64) end as cm_ct_owner_id,
case when alert_root_aller_id_s = '' then NULL else cast(alert_root_aller_id_s as INT64) end as alert_root_aller_id,
case when alert_med_class_id_s = '' then NULL else cast(alert_med_class_id_s as INT64) end as alert_med_class_id
from alert_2019.alt_drug_allergy;
    '''
