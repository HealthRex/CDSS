
# All utility code removed for refactoring
# Previous stable version saved in utils_UMich_backup20181021


import pandas as pd
from itertools import islice
import sqlite3
import LocalEnv
from medinfo.common.Util import log
import prepareData_NonSTRIDE as utils_general


def line_str2list(line_str, skip_first_col=False, test_mode=False):

    if test_mode:
        '''
        In the sample data, there is extra quotes, redundant indices,
        and | as the separator.
        '''
        if skip_first_col:
            # get rid of meaningless first col index
            return [x.strip()[1:-1] for x in line_str.split('|')][1:]
        else:
            return [x.strip()[1:-1] for x in line_str.split('|')]
    else:
        return [x.strip() for x in line_str.split('\t')]

def preprocess_files(raw_data_folderpath, data_files):
    '''
    Sample files are in a non-ideal format with separator | and extra quotes
    Preprocess to be in consistent form as raw data on the UMich site.

    Args:
        raw_data_folderpath:
        data_files:

    Returns:

    '''
    print raw_data_folderpath, data_files
    for data_file in data_files:
        data_filepath = raw_data_folderpath + '/' + data_file
        with open(data_filepath, 'r') as lines_read:
            with open(data_filepath.replace('.sample', ''), 'w') as out_file:
                for i, linestr in enumerate(lines_read):
                    if i == 0:
                        line = line_str2list(linestr, skip_first_col=False, test_mode=True)
                    else:
                        line = line_str2list(linestr, skip_first_col=True, test_mode=True)

                    out_file.write('\t'.join(line) + '\n')

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

def pd_process_labs(labs_df, time_min=None):
    labs_df = labs_df.rename(columns={'PatientID':'pat_id',
               'EncounterID':'order_proc_id',
               'COLLECTION_DATE':'result_time',
               'ORDER_CODE': 'proc_code',
               'RESULT_CODE': 'base_name',
               'VALUE':'ord_num_value',
               'RANGE':'normal_range',
               'HILONORMAL_FLAG': 'result_flag'
                })

    if time_min:
        labs_df = labs_df[labs_df['result_time'] > time_min]

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


    return {'labs':labs_df[['pat_id', 'order_proc_id','order_time','result_time',
                       'proc_code','base_name','ord_num_value','result_in_range_yn','result_flag']]}

def pd_process_pt_info(pt_info_df):
    pt_info_df = pt_info_df.rename(columns={'PatientID':'pat_id','DOB':'Birth'})
    pt_info_df['pat_id'] = pt_info_df['pat_id'].apply(lambda x: hash(x))
    pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: utils_general.remove_microsecs(x))
    return {'pt_info':pt_info_df[['pat_id', 'Birth']]}

def pd_process_encounters(encounters_df, time_min=None, outpatient=False):
    encounters_df = encounters_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','AdmitDate':'AdmitDxDate'})
    if time_min:
        encounters_df = encounters_df[encounters_df['AdmitDxDate'] > time_min]
    if not outpatient:
        encounters_df = encounters_df[encounters_df['PatientClassCode'] != 'Outpatient']
    encounters_df['pat_id'] = encounters_df['pat_id'].apply(lambda x: hash(x))
    encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: utils_general.remove_microsecs(x))
    return {'encounters':encounters_df[['pat_id','order_proc_id','AdmitDxDate']]}

def pd_process_diagnoses(diagnoses_df, time_min=None):
    diagnoses_df = diagnoses_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','ActivityDate':'diagnose_time','TermCodeMapped':'diagnose_code'})
    if time_min:
        diagnoses_df = diagnoses_df[diagnoses_df['diagnose_time'] > time_min]
    diagnoses_df['pat_id'] = diagnoses_df['pat_id'].apply(lambda x: hash(x))
    diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: utils_general.remove_microsecs(x))

    return {'diagnoses':diagnoses_df[['pat_id','order_proc_id','diagnose_time','diagnose_code']]}

def pd_process_demographics(demographics_df):
    demographics_df = demographics_df.rename(columns={'PatientID':'pat_id'})
    demographics_df['pat_id'] = demographics_df['pat_id'].apply(lambda x: hash(x))

    demographics_df['GenderName'] = demographics_df['GenderName'].apply(lambda x: 'Unknown' if not x else x)
    demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: 'Unknown' if not x else x)
    demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: x.replace("/", "-"))
    return {'demographics':demographics_df[['pat_id', 'GenderName', 'RaceName']]}
