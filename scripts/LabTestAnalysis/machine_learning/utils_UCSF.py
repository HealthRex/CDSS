
# All utility code removed for refactoring
# Previous stable version saved in utils_UMich_backup20181021


import pandas as pd
pd.set_option('display.width', 300)
from itertools import islice
import sqlite3
import LocalEnv
from medinfo.common.Util import log
import prepareData_NonSTRIDE as utils_general
import datetime
from collections import Counter

datetime_format = "%Y-%m-%dT%H:%M:%SZ"
RUNNING_MODE = 'TEST' #TODO

import dask.dataframe as dd
# def separate_demog_diagn_encnt(folder_path): # TODO: Do this by pieces...
#     file_name = 'demographics_and_diagnoses.tsv' # TODO: dangerous here
#     # diagn: CSN, ICD10 (diagn time = Admission Datetime?! TODO)
#     # demog: CSN, race, sex, Birth (time)
#     # encnt: CSN, Admission Datetime
#     df = dd.read_csv(folder_path + '/' + file_name, sep='\t')
#     # print df.head()
#
#     df_diagn = df.ix[df['present_on_admit']=='Yes',
#                   ['CSN', 'Admission Datetime', 'ICD10']].copy() # TODO: succeed?
#     df_diagn = df_diagn.drop_duplicates()
#     df_diagn.to_csv(folder_path + '/' + 'diagnoses-*.tsv', sep='\t')
#
#     # A couple notes: our ethnic_grp column is only really useful
#     # for hispanic versus not hispanic. The primary diagnosis is
#     # marked by the "Principal Dx Used" text in the severity column.
#     # TODO: Ethnic_Grp or Primary_Race?
#     df_demog = df[['CSN', 'Gender', 'Primary_Race']].copy()
#     df_demog = df_demog.drop_duplicates()
#     if RUNNING_MODE == 'TEST':
#         df_demog['Gender'] = df_demog['Gender'].apply(lambda x: 'Male')
#     df_demog.to_csv(folder_path + '/' + 'demographics-*.tsv', sep='\t')
#
#     # TODO: it is important to differentiate 'Admission' and 'diagnose'
#     # times in our model, even though there is only a couple' days diff
#     df_encnt = df[['CSN', 'Admission Datetime']]
#     df_encnt = df_encnt.drop_duplicates()
#     df_encnt.to_csv(folder_path + '/' + 'encounters-*.tsv', sep='\t')
#
#     df_pt_info = df[['CSN', 'Admission Datetime', 'Age']].copy()
#     # print df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)).values
#
#
#     if RUNNING_MODE=='TEST':
#         df_pt_info['DOB'] = df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime(year=1900,month=1,day=1))
#     else:
#         df_pt_info['DOB'] = (df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)) \
#             - df_pt_info['Age'].apply(lambda x: datetime.timedelta(days=x*365))).values
#     df_pt_info = df_pt_info.drop_duplicates()
#     df_pt_info[['CSN', 'DOB']].to_csv(folder_path + '/' + 'pt.info-*.tsv', sep='\t')
#
#     return

# def separate_labs_team(folder_path): # TODO: Do this by pieces...
#     file_name = 'labs_deident.tsv'
#     df = dd.read_csv(folder_path + '/' + file_name, sep='\t')
#     df_team = df[['CSN','Order Time','discharge service']] #: 'Team'
#     df_team = df_team.drop_duplicates()
#     df_team.to_csv(folder_path + '/' + 'treatment_team-*.tsv', sep='\t')
#
#     df_labs = df[['CSN','Order Time','Order Name','Order Proc ID','BASE_NAME','Result','Result Flag']]
#     df_labs.to_csv(folder_path + '/' + 'labs-*.tsv', sep='\t')

def pd_process_demogdiagn(df):
    file_name = 'demographics_and_diagnoses.tsv'  # TODO: dangerous here
    # diagn: CSN, ICD10 (diagn time = Admission Datetime?! TODO)
    # demog: CSN, race, sex, Birth (time)
    # encnt: CSN, Admission Datetime
    tab2df_dict = {}

    df_diagn = df.ix[df['present_on_admit'] == 'Yes',
                     ['CSN', 'Admission Datetime', 'ICD10']].copy()  # TODO: succeed?
    df_diagn = df_diagn.drop_duplicates()
    df_diagn = df_diagn.rename(
        columns={'CSN': 'order_proc_id', 'Admission Datetime': 'diagnose_time', 'ICD10': 'diagnose_code'})
    df_diagn['pat_id'] = df_diagn['order_proc_id'].apply(lambda x: hash(x))
    tab2df_dict['diagnoses'] = df_diagn[['pat_id', 'order_proc_id', 'diagnose_time', 'diagnose_code']]

    # diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: utils_general.remove_microsecs(x))

    # A couple notes: our ethnic_grp column is only really useful
    # for hispanic versus not hispanic. The primary diagnosis is
    # marked by the "Principal Dx Used" text in the severity column.
    # TODO: Ethnic_Grp or Primary_Race?
    df_demog = df[['CSN', 'Gender', 'Primary_Race']].copy()
    df_demog = df_demog.drop_duplicates()
    if RUNNING_MODE == 'TEST':
        df_demog['Gender'] = df_demog['Gender'].apply(lambda x: 'Male')

    df_demog = df_demog.rename(columns={'Gender': 'GenderName',
                                        'Primary_Race': 'RaceName'
                                        })
    df_demog['pat_id'] = df_demog['CSN'].apply(lambda x: hash(x))

    df_demog['GenderName'] = df_demog['GenderName'].apply(lambda x: 'Unknown' if not x else x)
    df_demog['RaceName'] = df_demog['RaceName'].apply(lambda x: 'Unknown' if not x else x)

    tab2df_dict['demographics'] = df_demog[['pat_id', 'GenderName', 'RaceName']]


    # TODO: it is important to differentiate 'Admission' and 'diagnose'
    # times in our model, even though there is only a couple' days diff
    df_encnt = df[['CSN', 'Admission Datetime']].copy()
    df_encnt = df_encnt.drop_duplicates()

    df_encnt = df_encnt.rename(columns={'CSN': 'order_proc_id', 'Admission Datetime': 'AdmitDxDate'})
    df_encnt['pat_id'] = df_encnt['order_proc_id'].apply(lambda x: hash(x))
    # encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: utils_general.remove_microsecs(x))
    tab2df_dict['encounters'] = df_encnt[['pat_id', 'order_proc_id', 'AdmitDxDate']]

    df_pt_info = df[['CSN', 'Admission Datetime', 'Age']].copy()
    # print df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)).values

    df_pt_info['pat_id'] = df_pt_info['CSN'].apply(lambda x: hash(x))
    # pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: utils_general.remove_microsecs(x))
    if RUNNING_MODE == 'TEST':
        df_pt_info['Birth'] = df_pt_info['Admission Datetime'].apply(
            lambda x: datetime.datetime(year=1900, month=1, day=1))
    else:
        df_pt_info['Birth'] = (
                    df_pt_info['Admission Datetime'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)) \
                    - df_pt_info['Age'].apply(lambda x: datetime.timedelta(days=x * 365))).values
    df_pt_info = df_pt_info.drop_duplicates()
    tab2df_dict['pt_info'] = df_pt_info[['pat_id', 'Birth']]

    return tab2df_dict


def pd_process_labs(df): # labs and teams
    team_df = df[['CSN', 'Order Time', 'Order Proc ID', 'discharge service']].copy()  #: 'Team'
    team_df = team_df.rename(columns={
        'CSN':'pat_id',
        'Order Time': 'order_time',
        'Order Proc ID':'order_proc_id',
        'discharge service':'treatment_team'
    })
    team_df = team_df.drop_duplicates()
    # df_team.to_csv(folder_path + '/' + 'treatment_team-*.tsv', sep='\t')

    labs_df = df[['CSN', 'Order Time', 'Order Name', 'Order Proc ID', 'BASE_NAME', 'Result', 'Result Flag']].copy()
    labs_df = labs_df.rename(columns={
        'CSN': 'pat_id',
        'Order Time': 'order_time',  # TODO
        'Order Name': 'proc_code',
        'Order Proc ID': 'order_proc_id',
        'BASE_NAME': 'base_name',
        'Result': 'ord_num_value',
        'Result Flag': 'result_flag'  # TODO: check later
    })
    labs_df['pat_id'] = labs_df['pat_id'].apply(lambda x: hash(x))

    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))

    labs_df['proc_code'] = labs_df['proc_code'].apply(lambda x: x.replace('/', '-'))
    labs_df['result_time'] = labs_df['order_time'].copy()
    labs_df['result_in_range_yn'] = labs_df['result_flag'].apply(lambda x: 'Y' if x == 'NA' else 'N')

    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_general.filter_nondigits(x))

    # labs_df.to_csv("labs_df.csv")
    labs_df = labs_df[['pat_id', 'order_proc_id', 'order_time', 'result_time',
                    'proc_code', 'base_name', 'ord_num_value', 'result_in_range_yn', 'result_flag']]
    tab2df_dict = {}
    tab2df_dict['team'] = team_df
    tab2df_dict['labs'] = labs_df
    return tab2df_dict

def pd_process_labs_(labs_df):
    labs_df = labs_df.rename(columns={
        'CSN': 'pat_id',
        'Order Time': 'order_time',  # TODO
        'Order Name': 'proc_code',
        'Order Proc ID':'order_proc_id',
        'BASE_NAME': 'base_name',
        'Result': 'ord_num_value',
        'Result Flag': 'result_flag' #TODO: check later
    })
    # print labs_df.columns
    # Decision: Hash the string type pat_id to long int to fit into CDSS pipeline
    labs_df['pat_id'] = labs_df['pat_id'].apply(lambda x: hash(x))

    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))

    labs_df['proc_code'] = labs_df['proc_code'].apply(lambda x: x.replace('/', '-'))
    # labs_df['base_name'] = labs_df['base_name'].apply(lambda x: utils_general.filter_nonascii(x))
    # labs_df['base_name'] = labs_df['base_name'].apply(lambda x: utils_general.clean_basename(x))
    # labs_df['base_name'] = labs_df['base_name'].apply(lambda x: x.replace('/','-'))

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
                    'proc_code', 'base_name', 'ord_num_value', 'result_in_range_yn', 'result_flag']]

# def pd_process_pt_info(pt_info_df):
#     pt_info_df = pt_info_df.rename(columns={'CSN':'pat_id','DOB':'Birth'})
#     pt_info_df['pat_id'] = pt_info_df['pat_id'].apply(lambda x: hash(x))
#     # pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: utils_general.remove_microsecs(x))
#     return pt_info_df[['pat_id', 'Birth']]

# def pd_process_encounters(encounters_df):
#     encounters_df = encounters_df.rename(columns={'CSN':'order_proc_id','Admission Datetime':'AdmitDxDate'})
#     encounters_df['pat_id'] = encounters_df['order_proc_id'].apply(lambda x: hash(x))
#     # encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: utils_general.remove_microsecs(x))
#     return encounters_df[['pat_id','order_proc_id','AdmitDxDate']]

# def pd_process_diagnoses(diagnoses_df):
#     diagnoses_df = diagnoses_df.rename(columns={'CSN':'order_proc_id','Admission Datetime':'diagnose_time','ICD10':'diagnose_code'})
#     diagnoses_df['pat_id'] = diagnoses_df['order_proc_id'].apply(lambda x: hash(x))
#     # diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: utils_general.remove_microsecs(x))
#
#     return diagnoses_df[['pat_id','order_proc_id','diagnose_time','diagnose_code']]

# def pd_process_demographics(demographics_df):
#     demographics_df = demographics_df.rename(columns={'CSN':'order_proc_id',
#                                                       'Gender':'GenderName',
#                                                       'Primary_Race':'RaceName'
#                                                       })
#     demographics_df['pat_id'] = demographics_df['order_proc_id'].apply(lambda x: hash(x))
#
#     demographics_df['GenderName'] = demographics_df['GenderName'].apply(lambda x: 'Unknown' if not x else x)
#     demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: 'Unknown' if not x else x)
#     return demographics_df[['pat_id', 'GenderName', 'RaceName']]

def pd_process_vitals(vitals_df):
    #TODO: be careful of very large df operation...
    #TODO: is separate_demo... easy in memory?
    # Transform the whole table...
    # VS record time --> shifted_record_dt_tm
    #
    tab2df_dict = {}
    vitals_df = vitals_df.rename(columns={'CSN':'flo_meas_id',
                                          'VS record time':'shifted_record_dt_tm',
                                          'SBP':'flowsheet_value_SBP',
                                          'DBP':'flowsheet_value_DBP',
                                          'FiO2 (%)':'flowsheet_value_FiO2',
                                          'Pulse': 'flowsheet_value_Pulse',
                                          'Resp': 'flowsheet_value_Resp',
                                          'Temp': 'flowsheet_value_Temp',
                                          'o2flow': 'flowsheet_value_o2flow'
                                          })
    vitals_df['pat_id'] = vitals_df['flo_meas_id'].apply(lambda x: hash(x))

    vitals_df_long = pd.wide_to_long(vitals_df, stubnames='flowsheet_value',
                          i=['pat_id', 'flo_meas_id', 'shifted_record_dt_tm'],
                          j='flowsheet_name', sep='_', suffix='\w')
    vitals_df_long = vitals_df_long.reset_index()
    vitals_df_long = vitals_df_long.drop(vitals_df_long[vitals_df_long.flowsheet_value=='NA'].index)

    tab2df_dict['vitals'] = vitals_df_long
    return tab2df_dict