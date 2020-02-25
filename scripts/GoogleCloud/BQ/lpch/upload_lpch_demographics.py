#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

# [2] "lpch_demographics_121119.csv"
# [1] "ANON_ID"                  "BIRTH_DATE_JITTERED"
# [3] "DEATH_DATE_JITTERED"      "GENDER"
# [5] "PRIMARY_RACE"             "ETHNICITY"
# [7] "MARITAL_STATUS"           "RELIGION"
# [9] "LANGUAGE"                 "INTRPTR_NEEDED_YN"
# [11] "INSURANCE_PAYOR_NAME"     "CUR_PCP_PROV_MAP_ID"
# [13] "RECENT_CONF_ENC_JITTERED" "RECENT_HT_IN_CMS"
# [15] "RECENT_WT_IN_KGS"         "BMI"
# [17] "CHARLSON_SCORE"           "N_HOSPITALIZATIONS"
# [19] "DAYS_IN_HOSPITAL"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_demographics_121119.csv'
csv_path = '/Users/jonc101/Downloads/lpch_demographics_121119.csv'

DATASET_NAME = 'lpch'
TABLE_NAME = 'demographics'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('BIRTH_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DEATH_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('GENDER', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRIMARY_RACE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ETHNICITY', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MARITAL_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RELIGION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LANGUAGE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('INTRPTR_NEEDED_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('INSURANCE_PAYOR_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CUR_PCP_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECENT_CONF_ENC_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECENT_HT_IN_CMS', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECENT_WT_IN_KGS', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BMI', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CHARLSON_SCORE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('N_HOSPITALIZATIONS', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DAYS_IN_HOSPITAL', 'INT64', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA =[bigquery.SchemaField('ANON_ID', 'STRING', 'REQUIRED', None, ()),
                      bigquery.SchemaField('BIRTH_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DEATH_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('GENDER', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRIMARY_RACE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ETHNICITY', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MARITAL_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RELIGION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LANGUAGE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('INTRPTR_NEEDED_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('INSURANCE_PAYOR_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CUR_PCP_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECENT_CONF_ENC_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECENT_HT_IN_CMS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RECENT_WT_IN_KGS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BMI', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CHARLSON_SCORE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('N_HOSPITALIZATIONS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DAYS_IN_HOSPITAL', 'STRING', 'NULLABLE', None, ())]



if __name__ == '__main__':
    logging.basicConfig()

    '''
    - removed heading and trailing lines in vim
    - added header line

    split every 2 mln lines:
    split -l 2000000 alert_history_012420.csv alert_history_012420_
    '''

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        bq_client.reconnect_client()
        bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                    schema=FINAL_TABLE_SCHEMA, skip_rows=1)

    print('Done')
    '''
    expecting 167,058,216 lines from original table
    '''

    '''
    Conversion script in SQL:
create or replace
table alert_2019.alert_history_20200124
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
from alert_2019.alert_history_20200124;
    '''
