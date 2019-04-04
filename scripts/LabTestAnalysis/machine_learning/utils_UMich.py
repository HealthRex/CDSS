import pandas as pd
from itertools import islice
import sqlite3
import LocalEnv
from medinfo.common.Util import log

test_mode = False


def filter_nondigits(any_str):
    return ''.join([x for x in str(any_str) if x in '.0123456789'])

def filter_range(any_str): # contains sth like range a-b
    nums = any_str.strip().split('-')
    try:
        return (float(nums[0]) + float(nums[1])) / 2.
    except:
        return any_str

def remove_microsecs(any_str):
    try:
        return any_str.split('.')[0]
    except:
        return any_str

def line_str2list(line_str):
    # Get rid of extra quotes
    # if test_mode:
    #     if skip_first_col:
    #         # get rid of meaningless first col index
    #         return [x.strip()[1:-1] for x in line_str.split('|')][1:]
    #     else:
    #         return [x.strip()[1:-1] for x in line_str.split('|')]
    # else:
    return [x.strip() for x in line_str.split('\t')]

import numpy as np
import random, string

def perturb_str(any_str, seed=None): #TODO: Doing seeding in the future
    str_len = len(any_str)
    ind_to_perturb = np.random.choice(str_len)
    chr_to_perturb = random.choice(string.letters + '-0123456789')
    any_str = any_str[:ind_to_perturb] + chr_to_perturb + any_str[ind_to_perturb + 1:]
    return any_str

def perturb_a_file(raw_file_path, target_file_path, col_patid, my_dict):
    with open(raw_file_path) as fr:
        lines_raw = fr.readlines()
        fr.close()

    import os
    if not os.path.exists(target_file_path):
        fw = open(target_file_path, 'w')
        fw.write(lines_raw[0])  # column name line
    else:
        fw = open(target_file_path, 'a')
    for line_raw in lines_raw[1:]:
        line_as_list = line_str2list(line_raw)
        try:
            cur_pat_id = line_as_list[col_patid]
        except:
            # Handle cases where the line is empty
            continue

        perturbed_patid = my_dict[cur_pat_id]
        line_as_list[col_patid] = perturbed_patid  # perturbing pat_id
        line_as_list = ["\"" + x + "\"" for x in line_as_list]
        line_perturbed = "|".join(line_as_list)
        line_perturbed += '\n'

        fw.write(line_perturbed)

# Both name lists have the same order!
def create_large_files(raw_data_files, raw_data_folderpath,
                       large_data_files, large_data_folderpath, num_repeats=100, USE_CACHED_DB=True):
    import os
    if os.path.exists(large_data_folderpath + '/' + large_data_files[0]):
        if USE_CACHED_DB:
            log.info("Large files exist!")
            return
        else:
            for large_data_file in large_data_files:
                os.remove(large_data_folderpath + '/' + large_data_file)

    if 'labs' not in raw_data_files[0]:
        quit("Please place labs file as the beginning of raw_data_files!")  # TODO: quit(int)?

    # query all_pat_ids from raw_data. Presumably small files, so should not be problem
    with open(raw_data_folderpath + '/' + raw_data_files[0]) as f:
        lines_lab = f.readlines()
        f.close()
    all_pat_ids = set(
        [line_str2list(line)[1] for line in lines_lab[1:]])  # set([line.split('|')[1] for line in lines[1:]])

    # Each time, perturb pat_ids in a specific random way, and modify all tables accordingly...
    for _ in range(num_repeats):
        # Create a different perturbation rule each time
        my_dict = {}
        for pat_id in all_pat_ids:
            my_dict[pat_id] = perturb_str(pat_id)

        # For each perturbation, perturb all tables
        for ind in range(len(raw_data_files)):
            raw_file_path = raw_data_folderpath + '/' + raw_data_files[ind]
            target_file_path = large_data_folderpath + '/' + large_data_files[ind]
            perturb_a_file(raw_file_path, target_file_path, col_patid=1, my_dict=my_dict)


def lines2pd(lines_str, colnames):
    normal_num_cols = len(colnames)

    all_rows = []
    for line_str in lines_str:
        curr_row = line_str2list(line_str) #, skip_first_col=True

        if len(curr_row) < normal_num_cols / 2:  #
            # log.info('severely missing data when processing')
            continue
        all_rows.append(curr_row)

    data_df = pd.DataFrame(all_rows, columns=colnames)
    return data_df

def construct_result_in_range_yn(df):
    # baseline
    result_flag_list = df['result_flag'].apply(
        lambda x: 'N' if x == 'L' or x == 'H' or x == 'A' else 'Y').values.tolist()

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

from medinfo.db import DBUtil
if test_mode:
    time_min = '1900-01-01'
else:
    time_min = '2015-01-01'


def pd_process_labs(labs_df, order_proc_ids_to_include=None):
    # print labs_df.columns
    labs_df = labs_df.rename(columns={'PatientID': 'pat_id',
                                      'EncounterID': 'order_proc_id',
                                      'COLLECTION_DATE': 'result_time',
                                      'ORDER_CODE': 'proc_code',
                                      'RESULT_CODE': 'base_name',
                                      'VALUE': 'ord_num_value',
                                      'RANGE': 'normal_range',
                                      'HILONORMAL_FLAG': 'result_flag'
                                      }
                             )
    if order_proc_ids_to_include and not test_mode: # for including only inpatients
        labs_df = labs_df[labs_df['order_proc_id'].isin(order_proc_ids_to_include)]

    labs_df = labs_df[labs_df['result_time'] > time_min]  # DBUtil.datetime()
    # labs_df = labs_df[labs_df[]]

    # Hash the string type pat_id to long int to fit into CDSS pipeline
    labs_df['pat_id'] = labs_df['pat_id'].apply(lambda x: hash(x))

    # Decision: use 'COLLECTION_DATE' (result time) as 'order_time'
    labs_df['order_time'] = labs_df['result_time'].copy()

    labs_df = labs_df[labs_df['base_name'].map(lambda x: str(x) != '*')]

    if labs_df.shape[0] == 0:
        labs_df = pd.DataFrame(columns=['pat_id', 'order_proc_id', 'order_time', 'result_time',
                                        'proc_code', 'base_name', 'ord_num_value', 'result_in_range_yn', 'result_flag'])
        # labs_df['result_in_range_yn'] = labs_df['result_flag']

    else:

        # Create redundant info to fit into CDSS pipeline
        labs_df['result_in_range_yn'] = construct_result_in_range_yn(
            labs_df[['ord_num_value', 'normal_range', 'result_flag']])

        # Decision: use (a+b)/2 for the "a-b" range case
        labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: filter_range(x) if '-' in x else x)
        # Decision: use "0.1", "60" to handles cases like "<0.1", ">60" cases
        labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: filter_nondigits(x))

        # Make 00:00:00.0000000000 (hr;min;sec) into 00:00:00 to allow CDSS parse later
        labs_df['order_time'] = labs_df['order_time'].apply(lambda x: remove_microsecs(x))
        labs_df['result_time'] = labs_df['result_time'].apply(lambda x: remove_microsecs(x))

    return labs_df[['pat_id', 'order_proc_id', 'order_time', 'result_time',
                    'proc_code', 'base_name', 'ord_num_value', 'result_in_range_yn', 'result_flag']]

def pd_process_pt_info(pt_info_df):
    pt_info_df = pt_info_df.rename(columns={'PatientID': 'pat_id', 'DOB': 'Birth'})
    pt_info_df['pat_id'] = pt_info_df['pat_id'].apply(lambda x: hash(x))
    pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: remove_microsecs(x))
    return pt_info_df[['pat_id', 'Birth']]

def pd_process_encounters(encounters_df):
    encounters_df = encounters_df.rename(
        columns={'PatientID': 'pat_id', 'EncounterID': 'order_proc_id', 'AdmitDate': 'AdmitDxDate'})
    encounters_df = encounters_df[
        (encounters_df['AdmitDxDate'] > time_min) & (encounters_df['PatientClassCode'] != 'Outpatient')]

    encounters_df['pat_id'] = encounters_df['pat_id'].apply(lambda x: hash(x))
    encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: remove_microsecs(x))
    return encounters_df[['pat_id', 'order_proc_id', 'AdmitDxDate']]


def pd_process_diagnoses(diagnoses_df):
    diagnoses_df = diagnoses_df.rename(
        columns={'PatientID': 'pat_id', 'EncounterID': 'order_proc_id', 'ActivityDate': 'diagnose_time',
                 'TermCodeMapped': 'diagnose_code'})

    diagnoses_df = diagnoses_df[diagnoses_df['diagnose_time'] > time_min]

    '''
    For ICD9, map the whole code
    For ICD10, only map the prefix
    '''
    diagnoses_df['diagnose_code'] = diagnoses_df[['diagnose_code', 'Lexicon']].apply(
        lambda x: x['diagnose_code'].split('.')[0] if x['Lexicon']=='ICD10' else x['diagnose_code'], axis=1)# )

    diagnoses_df['pat_id'] = diagnoses_df['pat_id'].apply(lambda x: hash(x))
    diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: remove_microsecs(x))

    return diagnoses_df[['pat_id', 'order_proc_id', 'diagnose_time', 'diagnose_code']]


def pd_process_demographics(demographics_df):
    demographics_df = demographics_df.rename(columns={'PatientID': 'pat_id'})
    demographics_df['pat_id'] = demographics_df['pat_id'].apply(lambda x: hash(x))

    demographics_df['GenderName'] = demographics_df['GenderName'].apply(lambda x: 'Unknown' if not x else x)
    demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: 'Unknown' if not x else x)
    demographics_df['RaceName'] = demographics_df['RaceName'].apply(lambda x: x.replace("/", "-"))
    return demographics_df[['pat_id', 'GenderName', 'RaceName']]

def pd2db(data_df, db_path, table_name, db_name, order_proc_ids_to_include=None):
    conn = sqlite3.connect(db_path + '/' + db_name)

    if table_name == "labs":  #
        data_df = pd_process_labs(data_df, order_proc_ids_to_include)
    elif table_name == "pt_info":
        data_df = pd_process_pt_info(data_df)
    elif table_name == "encounters":
        data_df = pd_process_encounters(data_df)
    elif table_name == "demographics":
        data_df = pd_process_demographics(data_df)
    elif table_name == "diagnoses":
        data_df = pd_process_diagnoses(data_df)
    else:
        print table_name + " does not exist!"

    data_df.to_sql(table_name, conn, if_exists="append")

    if table_name == 'encounters':
        return data_df['order_proc_id'].values.tolist()

def raw2db(data_file, data_folderpath, db_path, db_name, build_index_patid=True, collected_included_order_proc_ids=None):
    chunk_size = 100000  # num of rows

    print 'Now writing %s into database...' % data_file  #

    table_name = data_file.replace(".txt", "")
    table_name = table_name.replace(".sample", "")
    table_name = table_name.replace(".large", "")
    table_name = table_name.replace('.', '_')  # pt.info

    if table_name == 'encounters':
        all_included_order_proc_ids = []

    with open(data_folderpath + '/' + data_file) as f:
        is_first_chunk = True
        while True:
            # a chunk of rows
            next_n_lines_str = list(islice(f, chunk_size))
            if not next_n_lines_str:
                break

            if is_first_chunk:
                colnames = line_str2list(next_n_lines_str[0])
                # print colnames
                data_df = lines2pd(next_n_lines_str[1:], colnames)
                is_first_chunk = False
            else:  ## make each chunk into pandas
                data_df = lines2pd(next_n_lines_str, colnames)

            ## append each pandas to db tables
            if table_name == 'encounters':
                cur_included_order_proc_ids = pd2db(data_df, db_path=db_path, db_name=db_name, table_name=table_name)
                all_included_order_proc_ids += cur_included_order_proc_ids
            elif table_name == 'labs':
                pd2db(data_df, db_path=db_path, db_name=db_name, table_name=table_name,
                      order_proc_ids_to_include=collected_included_order_proc_ids)
            else:
                pd2db(data_df, db_path=db_path, db_name=db_name, table_name=table_name)
            ##
    if build_index_patid:
        conn = sqlite3.connect(db_path + '/' + db_name)
        build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);" % (table_name, table_name, 'pat_id')
        # print build_index_query
        conn.execute(build_index_query)

    if table_name == 'encounters':
        return set(all_included_order_proc_ids)