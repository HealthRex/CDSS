
import sqlite3
from itertools import islice
import pandas as pd
import LocalEnv
if LocalEnv.DATASET_SOURCE_NAME == 'UMich':
    from . import utils_UMich as utils_NonSTRIDE
elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
    from . import utils_UCSF as utils_NonSTRIDE

from medinfo.common.Util import log
import os
import numpy as np
import random, string


def filter_range(any_str):  # contains sth like range a-b
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

def filter_nonascii(any_str):
    return ''.join([i if ord(i) < 128 else ' ' for i in any_str])

def filter_nondigits(any_str):
    return ''.join([x for x in str(any_str) if x in '-.0123456789'])

def preprocess_files(raw_data_folderpath, data_files=None):
    if LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
        from . import utils_UCSF as utils_specs
        utils_specs.separate_demog_diagn_encnt(raw_data_folderpath)
        utils_specs.separate_labs_team(raw_data_folderpath)
    else:
        from . import utils_UMich
        utils_UMich.preprocess_files(raw_data_folderpath, data_files)

class DB_Preparor:
    def __init__(self, raw_data_files, raw_data_folderpath,
                       db_name,
                       fold_enlarge_data,
                       USE_CACHED_DB,
                       time_min='2015-01-01',
                       test_mode=False):

        self.num_repeats = fold_enlarge_data
        self.time_min = time_min
        self.test_mode = test_mode

        if os.path.exists(os.path.join(raw_data_folderpath, db_name)):
            if USE_CACHED_DB:
                log.info(db_name + " already exists!")
                return
            else:
                os.remove(os.path.join(raw_data_folderpath, db_name))

        ## Have to handle UCSF by converting:
        # Input: demographics_and_diagnoses:
        # Output: demographics, diagnoses

        # TODO: don't do logic in __init__ function

        if fold_enlarge_data != 1:  # TODO: fix for UCSF, perturbing stuff etc.
            '''
            For now, use this very simple enlarging strategy
            '''
            data_files = []
            for raw_file in raw_data_files:
                self.enlarge_a_file(os.path.join(raw_data_folderpath, raw_file), num_repeats=self.num_repeats)
                data_files.append(raw_file.replace(".sample",".test"))
            data_folderpath = raw_data_folderpath

        else:
            data_files = raw_data_files
            data_folderpath = raw_data_folderpath

        for data_file in data_files:
            print('Started processing %s...' % data_file)
            if LocalEnv.DATASET_SOURCE_NAME == 'UMich':
                if 'encounters' in data_file:
                    all_included_order_proc_ids = utils_NonSTRIDE.raw2db(data_file, data_folderpath,
                                                                     db_path=raw_data_folderpath, db_name=db_name,
                                                                     build_index_patid=True)
                elif 'labs' in data_file:
                    utils_NonSTRIDE.raw2db(data_file, data_folderpath, db_path=raw_data_folderpath, db_name=db_name,
                                       build_index_patid=True,
                                       collected_included_order_proc_ids=all_included_order_proc_ids)
                else:
                    utils_NonSTRIDE.raw2db(data_file, data_folderpath, db_path=raw_data_folderpath, db_name=db_name,
                                       build_index_patid=True)
            else:
                self.raw2db(data_file, data_folderpath, db_path=raw_data_folderpath,
                       db_name=db_name, build_index_patid=True)


    def enlarge_a_file(self, filename, num_repeats=10):

        fr = open(filename, 'r')
        lines_fr = fr.readlines()
        rows = len(lines_fr) - 1

        fw = open(filename.replace(".sample", ".test"), 'w')
        fw.write(lines_fr[0])
        ind = 0
        for i in range(num_repeats):
            for line in lines_fr[1:]:
                # print line.split('|')[1][1:-1]
                line_list = line.split('|')
                try:
                    line_list[1] = '\"%d\"' % ind
                except:
                    continue
                new_line = "|".join(line_list)

                fw.write(new_line)
                ind += 1

    def lines2pd(self, lines_str, colnames):
             # , params_str2list):
        normal_num_cols = len(colnames)

        all_rows = []
        for line_str in lines_str:
            curr_row = utils_NonSTRIDE.line_str2list(line_str, #skip_first_col=True,
                                                     test_mode=False)
                                                     # params_str2list=params_str2list)
            if len(curr_row) < normal_num_cols/2: #
                # log.info('severely missing data when processing')
                continue
            all_rows.append(curr_row)

        data_df = pd.DataFrame(all_rows, columns=colnames)
        return data_df


    def pd2db(self, data_df, df_name, db_path, db_name):
        conn = sqlite3.connect(db_path + '/' + db_name)

        if LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            if df_name == "labs":  #
                tab2df_dict = utils_NonSTRIDE.pd_process_labs(data_df)
            elif df_name == "pt_info":
                tab2df_dict = utils_NonSTRIDE.pd_process_pt_info(data_df)
            elif df_name == "encounters":
                tab2df_dict = utils_NonSTRIDE.pd_process_encounters(data_df)
            elif df_name == "demographics":
                tab2df_dict = utils_NonSTRIDE.pd_process_demographics(data_df)
            elif df_name == "diagnoses":
                tab2df_dict = utils_NonSTRIDE.pd_process_diagnoses(data_df)
            else:
                print(df_name + " does not exist for UMich!")

        elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':

            if df_name == "labs":  #
                tab2df_dict = utils_NonSTRIDE.pd_process_labs(data_df)
            elif df_name == "demographics_and_diagnoses":
                tab2df_dict = utils_NonSTRIDE.pd_process_demogdiagn(data_df)
            elif df_name == 'vitals':
                tab2df_dict = utils_NonSTRIDE.pd_process_vitals(data_df)
            else:
                print(df_name + " does not exist for UCSF!")

        for table_name in list(tab2df_dict.keys()):
            tab2df_dict[table_name].to_sql(table_name, conn, if_exists="append")

            if self.test_mode:
                tab2df_dict[table_name].to_csv('raw_data_UCSF/' + table_name + '.csv')

        return list(tab2df_dict.keys())

    # Chunk mechanism, should be general for any outside data
    def raw2db(self, data_file, data_folderpath, db_path, db_name,
           build_index_patid=True):
        chunk_size = 100000  # num of rows

        print('Now writing %s into database...' % data_file)  #

        generated_tables = []

        with open(data_folderpath + '/' + data_file) as f:
            is_first_chunk = True
            while True:
                # a chunk of rows
                next_n_lines_str = list(islice(f, chunk_size))
                if not next_n_lines_str:
                    break

                if is_first_chunk:
                    colnames = utils_NonSTRIDE.line_str2list(next_n_lines_str[0],
                                                             test_mode=False)
                    data_df = self.lines2pd(next_n_lines_str[1:], colnames)
                                       #, params_str2list)
                    is_first_chunk = False
                else:  ## make each chunk into pandas
                    data_df = self.lines2pd(next_n_lines_str, colnames)
                                       # params_str2list)

                ## append each pandas to db tables
                if LocalEnv.DATASET_SOURCE_NAME == 'UMich':
                    df_name = data_file.replace(".txt", "")
                    df_name = df_name.replace(".sample", "")
                    df_name = df_name.replace(".test", "")
                    df_name = df_name.replace(".large", "")
                    df_name = df_name.replace('.', '_')  # pt.info
                elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
                    df_name = data_file.replace(".tsv", "")  #
                    df_name = df_name.replace("_deident", "")
                    df_name = df_name.replace('.', '_')

                generated_tables += self.pd2db(data_df, df_name=df_name, db_path=db_path, db_name=db_name)
                ##

        if build_index_patid:
            conn = sqlite3.connect(db_path + '/' + db_name)

            for generated_table in generated_tables:
                build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);" % (generated_table, generated_table, 'pat_id')
                log.info(build_index_query)
                # print build_index_query
                conn.execute(build_index_query)