
# All utility code removed for refactoring
# Previous stable version saved in utils_UMich_backup20181021


import pandas as pd
from itertools import islice
import sqlite3
import LocalEnv
from medinfo.common.Util import log
import prepareData_NonSTRIDE as utils_general

def separate_demog_diagn_encnt(filepath):
    # diagn: CSN, ICD10 (diagn time = Admission Datetime?! TODO)
    # demog: CSN, race, sex, Birth (time)
    # encnt: CSN, Admission Datetime
    df = pd.read_csv(filepath, sep='\t')
    # print df.head()

    df_diagn = df[['CSN', 'Admission Datetime', 'ICD10']].copy()
    df_diagn.to_csv('diagnoses.tsv', sep='\t')

    # A couple notes: our ethnic_grp column is only really useful
    # for hispanic versus not hispanic. The primary diagnosis is
    # marked by the "Principal Dx Used" text in the severity column.
    # TODO: Ethnic_Grp or Primary_Race?
    df_demog = df[['CSN', 'Gender', 'Admission Datetime', 'Age']].copy()
    df_demog.to_csv('demographics.tsv', sep='\t')

    # TODO: it is important to differentiate 'Admission' and 'diagnose'
    # times in our model, even though there is only a couple' days diff
    df_encnt = df[['CSN', 'Admission Datetime']]
    df_encnt.to_csv('encounters.tsv', sep='\t')

    pass


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
    labs_df = labs_df.rename(columns={'PatientID':'pat_id',
               'EncounterID':'order_proc_id',
               'COLLECTION_DATE':'result_time',
               'ORDER_CODE': 'proc_code',
               'RESULT_CODE': 'base_name',
               'VALUE':'ord_num_value',
               'RANGE':'normal_range',
               'HILONORMAL_FLAG': 'result_flag'
                })

    # Hash the string type pat_id to long int to fit into CDSS pipeline
    labs_df['pat_id'] = labs_df['pat_id'].apply(lambda x: hash(x))

    # Decision: use 'COLLECTION_DATE' (result time) as 'order_time'
    labs_df['order_time'] = labs_df['result_time'].copy()

    labs_df = labs_df[labs_df['base_name'].map(lambda x:str(x)!='*')]

    # Create redundant info to fit into CDSS pipeline
    labs_df['result_in_range_yn'] = construct_result_in_range_yn(labs_df[['ord_num_value', 'normal_range', 'result_flag']])

    # Decision: use (a+b)/2 for the "a-b" range case
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_general.filter_range(x) if '-' in x else x)
    # Decision: use "0.1", "60" to handles cases like "<0.1", ">60" cases
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_general.filter_nondigits(x))

    # Make 00:00:00.0000000000 (hr;min;sec) into 00:00:00 to allow CDSS parse later
    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: utils_general.remove_microsecs(x))
    labs_df['result_time'] = labs_df['result_time'].apply(lambda x: utils_general.remove_microsecs(x))

    return labs_df[['pat_id', 'order_proc_id','order_time','result_time',
                       'proc_code','base_name','ord_num_value','result_in_range_yn','result_flag']]

def pd_process_pt_info(pt_info_df):
    pt_info_df = pt_info_df.rename(columns={'PatientID':'pat_id','DOB':'Birth'})
    pt_info_df['pat_id'] = pt_info_df['pat_id'].apply(lambda x: hash(x))
    pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: utils_general.remove_microsecs(x))
    return pt_info_df[['pat_id', 'Birth']]

def pd_process_encounters(encounters_df):
    encounters_df = encounters_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','AdmitDate':'AdmitDxDate'})
    encounters_df['pat_id'] = encounters_df['pat_id'].apply(lambda x: hash(x))
    encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: utils_general.remove_microsecs(x))
    return encounters_df[['pat_id','order_proc_id','AdmitDxDate']]

def pd_process_diagnoses(diagnoses_df):
    diagnoses_df = diagnoses_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','ActivityDate':'diagnose_time','TermCodeMapped':'diagnose_code'})
    diagnoses_df['pat_id'] = diagnoses_df['pat_id'].apply(lambda x: hash(x))
    diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: utils_general.remove_microsecs(x))

    return diagnoses_df[['pat_id','order_proc_id','diagnose_time','diagnose_code']]

def pd_process_demographics(demographics_df):
    demographics_df = demographics_df.rename(columns={'PatientID':'pat_id'})
    demographics_df['pat_id'] = demographics_df['pat_id'].apply(lambda x: hash(x))

    demographics_df['GenderName'] = demographics_df['GenderName'].apply(lambda x: 'Unknown' if not x else x)
    demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: 'Unknown' if not x else x)
    return demographics_df[['pat_id', 'GenderName', 'RaceName']]
