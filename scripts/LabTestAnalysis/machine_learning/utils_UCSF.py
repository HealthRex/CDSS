
# All utility code removed for refactoring
# Previous stable version saved in utils_UMich_backup20181021


import pandas as pd
from itertools import islice
import sqlite3
import LocalEnv
from medinfo.common.Util import log
import prepareData_NonSTRIDE as utils_general
import datetime
from collections import Counter

datetime_format = "%Y-%m-%dT%H:%M:%SZ"

def separate_demog_diagn_encnt(folder_path):
    file_name = 'demographics_and_diagnoses.tsv'
    # diagn: CSN, ICD10 (diagn time = Admission Datetime?! TODO)
    # demog: CSN, race, sex, Birth (time)
    # encnt: CSN, Admission Datetime
    df = pd.read_csv(folder_path + '/' + file_name, sep='\t')
    # print df.head()

    df_diagn = df[['CSN', 'Admission Datetime', 'ICD10']].copy()
    df_diagn = df_diagn.drop_duplicates()
    df_diagn.to_csv(folder_path + '/' + 'diagnoses.tsv', sep='\t')

    # A couple notes: our ethnic_grp column is only really useful
    # for hispanic versus not hispanic. The primary diagnosis is
    # marked by the "Principal Dx Used" text in the severity column.
    # TODO: Ethnic_Grp or Primary_Race?
    df_demog = df[['CSN', 'Gender', 'Primary_Race']].copy()
    df_demog = df_demog.drop_duplicates()
    df_demog.to_csv(folder_path + '/' + 'demographics.tsv', sep='\t')

    # TODO: it is important to differentiate 'Admission' and 'diagnose'
    # times in our model, even though there is only a couple' days diff
    df_encnt = df[['CSN', 'Admission Datetime']]
    df_encnt = df_encnt.drop_duplicates()
    df_encnt.to_csv(folder_path + '/' + 'encounters.tsv', sep='\t')

    df_pt_info = df[['CSN', 'Admission Datetime', 'Age']].copy()
    # print df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)).values
    df_pt_info['DOB'] = (df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)) \
        - df_pt_info['Age'].apply(lambda x: datetime.timedelta(days=x*365))).values
    df_pt_info = df_pt_info.drop_duplicates()
    df_pt_info[['CSN', 'DOB']].to_csv(folder_path + '/' + 'pt.info.tsv', sep='\t')
    return


def construct_result_in_range_yn(df):
    # baseline
    result_flag_list = df['result_flag'].apply(lambda x: 'N' if x == 'L' or x == 'H' or x == 'A' else 'Y').values.tolist()

    value_list = df['ord_num_value'].values.tolist()
    range_list = df['normal_range'].values.tolist()

    row, col = df.shape

    cnt_success = 0
    for i in range(row):
        try:
            n = float(str(value_list[i]))
            n1n2 = str(range_list[i]).split('-')
            assert len(n1n2) == 2
            n1, n2 = float(n1n2[0]), float(n1n2[1])

            if n1 <= n <= n2:
                result_flag_list[i] = 'Y'
            else:
                result_flag_list[i] = 'N'

            cnt_success += 1
        except:
            pass
    df['result_in_range_yn'] = pd.Series(result_flag_list).values
    # pd.testing.assert_series_equal(df['result_in_range_yn'], df_test['result_in_range_yn'])
    return df['result_in_range_yn']

def pd_process_labs(labs_df):
    labs_df = labs_df.rename(columns={
        'CSN': 'order_proc_id',
        'Order Time': 'order_time',  # TODO
        'Order Name': 'proc_code',
        'Component Name': 'base_name',
        'Result': 'ord_num_value',
        'Result Flag': 'result_flag',
        'discharge service': 'Team'
    })
    # print labs_df.columns
    # Decision: Hash the string type pat_id to long int to fit into CDSS pipeline
    labs_df['pat_id'] = labs_df['order_proc_id'].apply(lambda x: hash(x))

    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))

    labs_df['proc_code'] = labs_df['proc_code'].apply(lambda x: x.replace('/', '-'))
    labs_df['base_name'] = labs_df['base_name'].apply(lambda x: utils_general.filter_nonascii(x))
    # labs_df['base_name'] = labs_df['base_name'].apply(lambda x: utils_general.clean_basename(x))
    labs_df['base_name'] = labs_df['base_name'].apply(lambda x: x.replace('/','-'))

    # Decision: use 'COLLECTION_DATE' (result time) as 'order_time'
    labs_df['result_time'] = labs_df['order_time'].copy()

    # labs_df = labs_df[labs_df['base_name'].map(lambda x:str(x)!='*')]

    # Create redundant info to fit into CDSS pipeline
    # Counter({'NA': 4682, 'High': 1545, 'Low': 1341, 'High Panic': 60, 'Low Panic': 33, 'Abnormal': 19})
    labs_df['result_in_range_yn'] = labs_df['result_flag'].apply(lambda x: 'Y' if x=='NA' else 'N')

    # Counter({'Arterial': 198, 'Not specified': 155, 'Duplicate request, charge cancelled.': 152
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_general.filter_nondigits(x))

    labs_df.to_csv("labs_df.csv")
    return labs_df[['pat_id', 'order_proc_id', 'order_time', 'result_time',
                    'proc_code', 'base_name', 'ord_num_value', 'result_in_range_yn', 'result_flag', 'Team']]

def pd_process_pt_info(pt_info_df):
    pt_info_df = pt_info_df.rename(columns={'CSN':'order_proc_id','DOB':'Birth'})
    pt_info_df['pat_id'] = pt_info_df['order_proc_id'].apply(lambda x: hash(x))
    # pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: utils_general.remove_microsecs(x))
    return pt_info_df[['pat_id', 'Birth']]

def pd_process_encounters(encounters_df):
    encounters_df = encounters_df.rename(columns={'CSN':'order_proc_id','Admission Datetime':'AdmitDxDate'})
    encounters_df['pat_id'] = encounters_df['order_proc_id'].apply(lambda x: hash(x))
    # encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: utils_general.remove_microsecs(x))
    return encounters_df[['pat_id','order_proc_id','AdmitDxDate']]

def pd_process_diagnoses(diagnoses_df):
    diagnoses_df = diagnoses_df.rename(columns={'CSN':'order_proc_id','Admission Datetime':'diagnose_time','ICD10':'diagnose_code'})
    diagnoses_df['pat_id'] = diagnoses_df['order_proc_id'].apply(lambda x: hash(x))
    # diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: utils_general.remove_microsecs(x))

    return diagnoses_df[['pat_id','order_proc_id','diagnose_time','diagnose_code']]

def pd_process_demographics(demographics_df):
    demographics_df = demographics_df.rename(columns={'CSN':'order_proc_id',
                                                      'Gender':'GenderName',
                                                      'Primary_Race':'RaceName'
                                                      })
    demographics_df['pat_id'] = demographics_df['order_proc_id'].apply(lambda x: hash(x))

    demographics_df['GenderName'] = demographics_df['GenderName'].apply(lambda x: 'Unknown' if not x else x)
    demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: 'Unknown' if not x else x)
    return demographics_df[['pat_id', 'GenderName', 'RaceName']]

def pd_process_vitals(vitals_df):
    pass