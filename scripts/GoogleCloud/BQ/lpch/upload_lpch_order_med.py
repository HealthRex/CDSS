#!/usr/bin/env python2

import os
import logging
import itertools
import string
#import LocalEnv     # used for setting GOOGLE_APPLICATION_CREDENTIALS

from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery

# files names:

# [8] "lpch_order_med_121319.csv"
# [1] "ANON_ID"                 "PAT_ENC_CSN_ID_CODED"
# [3] "ORDER_MED_ID_CODED"      "ORDER_TIME_JITTERED"
# [5] "START_TIME_JITTERED"     "END_TIME_JITTERED"
# [7] "MEDICATION_ID"           "MED_DESCRIPTION"
# [9] "AMB_MED_DISP_NAME"       "ORDER_CLASS_C"
# [11] "ORDER_CLASS"             "ORDERING_MODE_C"
# [13] "ORDERING_MODE"           "SIG"
# [15] "QUANTITY"                "REFILLS"
# [17] "PRESC_PROV_MAP_ID"       "AUTHR_PROV_MAP_ID"
# [19] "MED_ROUTE_C"             "MED_ROUTE"
# [21] "DISCON_TIME_JITTERED"    "CHNG_ORDER_MED_ID_CODED"
# [23] "HV_DISCR_FREQ_ID"        "FREQ_NAME"
# [25] "FREQ_DISPLAY_NAME"       "FREQ_TYPE"
# [27] "NUMBER_OF_TIMES"         "TIME_UNIT"
# [29] "PRN_YN"                  "FREQ_PERIOD"
# [31] "HV_DISCRETE_DOSE"        "HV_DOSE_UNIT_C"
# [33] "HV_DOSE_UNIT"            "ORDER_STATUS_C"
# [35] "ORDER_STATUS"            "MIN_DISCRETE_DOSE"
# [37] "MAX_DISCRETE_DOSE"       "DOSE_UNIT_C"
# [39] "DOSE_UNIT"               "LASTDOSE"
# [41] "SERV_AREA_ID"            "EQUIP_STATUS_YN"
# [43] "PHARM_CLASS_NAME"        "THERA_CLASS_NAME"
# [45] "PHARM_CLASS_ABBR"        "THERA_CLASS_ABBR"
# [47] "IS_ADMINISTERED"         "DATA_SOURCE"


# /Users/jonc101/Downloads/
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/Users/jonc101/Downloads/Mining Clinical Decisions-58be3d782c5b.json'


# /Users/jonc101/Downloads/
CSV_FILE_PREFIX = '/Users/jonc101/Downloads/lpch_order_med_121319.csv'
csv_path = '/Users/jonc101/Downloads/lpch_order_med_121319.csv'
DATASET_NAME = 'lpch'
TABLE_NAME = 'order_med'
FINAL_TABLE_SCHEMA = [bigquery.SchemaField('ANON_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_MED_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('START_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('END_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MEDICATION_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AMB_MED_DISP_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_CLASS_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_CLASS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_MODE_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_MODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIG', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('QUANTITY', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFILLS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRESC_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AUTHR_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_ROUTE_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_ROUTE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DISCON_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CHNG_ORDER_MED_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DISCR_FREQ_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_DISPLAY_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_TYPE', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('NUMBER_OF_TIMES', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('TIME_UNIT', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRN_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_PERIOD', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DISCRETE_DOSE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DOSE_UNIT_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DOSE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS_C', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MIN_DISCRETE_DOSE', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAX_DISCRETE_DOSE', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT_C', 'FLOAT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LASTDOSE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SERV_AREA_ID', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('EQUIP_STATUS_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PHARM_CLASS_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('THERA_CLASS_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PHARM_CLASS_ABBR', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('THERA_CLASS_ABBR', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('IS_ADMINISTERED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]


# Final schema is what we want at the end, however, regexp used to process the csv can't handle matching more than 9 fragments (\1 - \9).
# So upload everything as string and process in bigquery - this will take care of string to int and datetime to date conversions
UPLOAD_TABLE_SCHEMA =[bigquery.SchemaField('ANON_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PAT_ENC_CSN_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_MED_ID_CODED', 'INT64', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('START_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('END_TIME_JITTERED', 'DATETIME', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MEDICATION_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_DESCRIPTION', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AMB_MED_DISP_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_CLASS_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_CLASS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_MODE_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDERING_MODE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SIG', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('QUANTITY', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('REFILLS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRESC_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('AUTHR_PROV_MAP_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_ROUTE_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MED_ROUTE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DISCON_TIME_JITTERED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('CHNG_ORDER_MED_ID_CODED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DISCR_FREQ_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_DISPLAY_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_TYPE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('NUMBER_OF_TIMES', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('TIME_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PRN_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('FREQ_PERIOD', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DISCRETE_DOSE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DOSE_UNIT_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('HV_DOSE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('ORDER_STATUS', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MIN_DISCRETE_DOSE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('MAX_DISCRETE_DOSE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT_C', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DOSE_UNIT', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('LASTDOSE', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('SERV_AREA_ID', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('EQUIP_STATUS_YN', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PHARM_CLASS_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('THERA_CLASS_NAME', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('PHARM_CLASS_ABBR', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('THERA_CLASS_ABBR', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('IS_ADMINISTERED', 'STRING', 'NULLABLE', None, ()),
                      bigquery.SchemaField('DATA_SOURCE', 'STRING', 'NULLABLE', None, ())]


if __name__ == '__main__':
    logging.basicConfig()

    upload = input('Upload? ("y"/"n"): ')
    bq_client = bigQueryUtil.BigQueryClient()
    if upload == 'Y' or upload == 'y':
        bq_client.reconnect_client()
        bq_client.load_csv_to_table(DATASET_NAME, TABLE_NAME, csv_path, auto_detect_schema=False,
                                    schema=FINAL_TABLE_SCHEMA, skip_rows=1)

    print('Done')
