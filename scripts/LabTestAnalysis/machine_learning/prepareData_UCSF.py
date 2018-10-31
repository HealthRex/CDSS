
import sqlite3
from itertools import islice
import pandas as pd
import utils_UCSF
pd.set_option('display.width', 300)
import datetime

import LocalEnv
db_name = LocalEnv.LOCAL_PROD_DB_PARAM["DSN"]

datetime_format = "%Y-%m-%dT%H:%M:%SZ"

# TODO: build index simultaneously
def pd_process_labs(labs_df):
    # print labs_df.columns
    labs_df = labs_df.rename(columns={
               'CSN':'order_proc_id',
               'Order Time':'order_time', # TODO
               'Order Name': 'proc_code',
               'Component Name': 'base_name',
               'Result':'ord_num_value',
               'Result Flag': 'result_flag',
                'discharge service':'Team'
                })
    # print labs_df.columns

    # Hash the string type pat_id to long int to fit into CDSS pipeline
    labs_df['pat_id'] = labs_df['order_proc_id'].apply(lambda x: hash(x))

    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))

    labs_df['base_name'] = labs_df['base_name'].apply(lambda x: utils_UCSF.filter_nonascii(x))
    labs_df['base_name'] = labs_df['base_name'].apply(lambda x: utils_UCSF.clean_basename(x))

    # TODO,decision: use 'COLLECTION_DATE' (result time) as 'order_time'
    labs_df['result_time'] = labs_df['order_time'].copy()

    # labs_df = labs_df[labs_df['base_name'].map(lambda x:str(x)!='*')]

    # Create redundant info to fit into CDSS pipeline
    labs_df['result_in_range_yn'] = labs_df['result_flag'].apply(lambda x: 'N' if x=='Low' or x=='High' else 'Y')
    #TODO: High Panic, Abnormal!

    # TODO,decision: use "0.1", "60" to handles cases like "<0.1", ">60" cases
    # TODO: maybe add a column to indicate that?
    # import re
    # range_pattern = re.compile("\d-\d")
    # print labs_df.ix[labs_df['ord_num_value'].map(lambda x: range_pattern.match(x)), 'ord_num_value']
    # quit()
    # TODO: not very robust for the "a-b" range case
    # print labs_df.ix[labs_df['ord_num_value'].map(lambda x:'-' in x), 'ord_num_value']
    # labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_UCSF.filter_range(x) if '-' in x else x)
    # print labs_df.ix[[74,261,319,509], 'ord_num_value']
    # quit()

    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_UCSF.filter_nondigits(x))

    labs_df.to_csv("labs_df.csv")
    return labs_df[['pat_id', 'order_proc_id','order_time','result_time',
                       'proc_code','base_name','ord_num_value','result_in_range_yn','result_flag','Team']]

def pd_process_vitals(vitals_df):
    vitals_df = vitals_df.rename(columns={
        'CSN': 'order_proc_id',
        'VS record time': 'vitals_time',  # TODO
    })
    vitals_df['pat_id'] = vitals_df['order_proc_id'].apply(lambda x: hash(x))
    vitals_df['vitals_time'] = vitals_df['vitals_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))
    return vitals_df[['pat_id','order_proc_id','vitals_time','SBP','DBP','FiO2 (%)','Pulse','Resp','Temp','o2flow']]

def pd_process_demographics_and_diagnoses(dd_df):
    dd_df = dd_df.rename(columns={
        'CSN': 'order_proc_id',
        'Admission Datetime': 'AdmitDxDate', # TODO: what is "Entry into hospital"?
        'ICD10': 'diagnose_code', # TODO: ICD10! also, has "co_morbidity" and "severity_of_dx" columns that can be potentially useful
        'Age': 'Age',
        'Gender':'GenderName',
        'Primary_Race':'RaceName'
    })
    dd_df['pat_id'] = dd_df['order_proc_id'].apply(lambda x: hash(x))
    dd_df['AdmitDxDate'] = dd_df['AdmitDxDate'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))
    return dd_df[['pat_id', 'AdmitDxDate', 'diagnose_code', 'Age', 'GenderName', 'RaceName']]

def pd2db(data_df, table_name):
    conn = sqlite3.connect('UCSF.db')

    if table_name == "labs": # TODO: ".sample!"
        data_df = pd_process_labs(data_df)
    elif table_name == "vitals":
        data_df = pd_process_vitals(data_df)
    elif table_name == "demographics_and_diagnoses":
        data_df = pd_process_demographics_and_diagnoses(data_df)
    else:
        print table_name + " does not exist!"

    data_df.to_sql(table_name, conn, if_exists="append")

def raw2db(txtpath, build_index_patid=True):
    chunk_size = 1000 # num of rows

    filename_txt = txtpath.split('/')[-1]
    print filename_txt

    table_name = filename_txt.replace("_deident", "")
    table_name = table_name.replace(".tsv", "")
    table_name = table_name.replace('.','_')

    for chunk in pd.read_csv(txtpath, chunksize=chunk_size, sep='\t'):
        # print chunk.shape
        pd2db(chunk, table_name=table_name)
    # with open(txtpath) as f:
    #     is_first_chunk = True
    #     while True:
    #         # a chunk of rows
    #         next_n_lines_str = list(islice(f, chunk_size))
    #         if not next_n_lines_str:
    #             break
    #
    #         if is_first_chunk:
    #             colnames = next_n_lines_str[0] #utils_UCSF.line_str2list(next_n_lines_str[0])
    #             print colnames
    #             data_df = lines2pd(next_n_lines_str[1:], colnames)
    #             is_first_chunk = False
    #         else:## make each chunk into pandas
    #             data_df = lines2pd(next_n_lines_str, colnames)
    #
    #         ## append each pandas to db tables
    #         pd2db(data_df, table_name=table_name)
            ##
    conn = sqlite3.connect('UCSF.db')
    build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);"%(table_name,table_name,'pat_id')
    print build_index_query
    conn.execute(build_index_query)

def prepare_database(data_folder_path):
    raw_txtpaths = ['labs_deident.tsv',
                    'demographics_and_diagnoses.tsv',
                    'vitals_deident.tsv'
                    ]
    raw_txtpaths  = [data_folder_path + x for x in raw_txtpaths]

    for txtpath in raw_txtpaths:
        raw2db(txtpath, build_index_patid=True)


if __name__ == '__main__':
    data_folder_path = LocalEnv.PATH_TO_CDSS + '/' + 'scripts/LabTestAnalysis/machine_learning/raw_data_UCSF/'
    prepare_database(data_folder_path)