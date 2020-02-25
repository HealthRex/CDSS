#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:


# [3] "lpch_diagnosis_101119.csv"
# [1] "ANON_ID"                   "LINE"
# [3] "PAT_ENC_CSN_ID_CODED"      "DX_ID"
# [5] "DX_NAME"                   "ICD9"
# [7] "ICD10"                     "START_DATE_JITTERED"
# [9] "NOTED_DATE_JITTERED"       "HX_DATE_OF_ENTRY_JITTERED"
# [11] "RESOLVED_DATE_JITTERED"    "END_DATE_JITTERED"
# [13] "PERF_PROV_MAP_ID"          "BILLING_PROV_MAP_ID"
# [15] "ENTRY_PROV_MAP_ID"         "DEPT_ID"
# [17] "PRIMARY"                   "CHRONIC"
# [19] "PRINCIPAL"                 "HOSPITAL_PL"
# [21] "PROBLEM_STATUS"            "ED"
# [23] "POA"                       "PRESENT_ON_ADM"
# [25] "SOURCE"                    "DATA_SOURCE"



os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_diagnosis_101119.csv'
csv_path = '/Users/jonc101/Downloads/lpch_diagnosis_101119.csv'

DATASET_NAME = 'lpch'
TABLE_NAME = 'diagnosis'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LINE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DX_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DX_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ICD9', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ICD10', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('START_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('NOTED_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HX_DATE_OF_ENTRY_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESOLVED_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('END_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PERF_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ENTRY_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DEPT_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRIMARY', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CHRONIC', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRINCIPAL', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HOSPITAL_PL', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROBLEM_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('POA', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRESENT_ON_ADM', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SOURCE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]

# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LINE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DX_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DX_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ICD9', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ICD10', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('START_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('NOTED_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HX_DATE_OF_ENTRY_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('RESOLVED_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('END_DATE_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PERF_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('BILLING_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ENTRY_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DEPT_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRIMARY', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CHRONIC', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRINCIPAL', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HOSPITAL_PL', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PROBLEM_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('POA', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRESENT_ON_ADM', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SOURCE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]



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

    #print('Done')
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
