
import sqlite3
from itertools import islice
import pandas as pd
import LocalEnv
if LocalEnv.DATASET_SOURCE_NAME == 'UMich':
    import utils_UMich as utils_NonSTRIDE
elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
    import utils_UCSF as utils_NonSTRIDE

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


class DB_Preparor:
    def __init__(self, raw_data_files, raw_data_folderpath,
                       db_name,
                       fold_enlarge_data,
                       USE_CACHED_DB,
                       data_source = 'UMich',
                       time_min='2015-01-01',
                       test_mode=False):

        self.data_source = 'UMich'
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
            # large_data_folderpath = raw_data_folderpath + '/' + 'enlarged_data_by_%s_fold'%str(fold_enlarge_data)
            #
            # if not os.path.exists(large_data_folderpath):
            #     os.mkdir(large_data_folderpath)
            #
            # large_data_files = [x.replace('sample','large') for x in raw_data_files]
            # # Same file names, different folders
            # create_large_files(raw_data_files,raw_data_folderpath,
            #                                large_data_files,large_data_folderpath,
            #                                              num_repeats=fold_enlarge_data, USE_CACHED_DB=USE_CACHED_DB)
            # data_files = large_data_files
            # data_folderpath = large_data_folderpath
        else:
            data_files = raw_data_files
            data_folderpath = raw_data_folderpath

        for data_file in data_files:
            self.raw2db(data_file, data_folderpath, db_path=raw_data_folderpath,
                   db_name=db_name, build_index_patid=True, data_source=data_source)





    # def perturb_str(any_str, seed=None):
    #     if seed:
    #         np.random.seed(seed)
    #     str_len = len(any_str)
    #     ind_to_perturb = np.random.choice(str_len)
    #     chr_to_perturb = random.choice(string.letters + '-0123456789')
    #     any_str = any_str[:ind_to_perturb] + chr_to_perturb + any_str[ind_to_perturb+1:]
    #     return any_str
    #
    # def perturb_a_file(raw_file_path, target_file_path, col_patid, perturb_dict, params_str2list):
    #     with open(raw_file_path) as fr:
    #         lines_raw = fr.readlines()
    #         fr.close()
    #
    #     import os
    #     if not os.path.exists(target_file_path):
    #         fw = open(target_file_path,'w')
    #         fw.write(lines_raw[0]) # column name line
    #     else:
    #         fw = open(target_file_path,'a')
    #     for line_raw in lines_raw[1:]:
    #         # print 'line_raw:', len(line_raw.split('\t'))
    #         line_as_list = utils_NonSTRIDE.line_str2list(line_raw, params_str2list)
    #         try:
    #             cur_pat_id = line_as_list[col_patid]
    #         except:
    #             # Handle cases where the line is empty
    #             continue
    #
    #         perturbed_patid = perturb_dict[cur_pat_id]
    #         line_as_list[col_patid] = perturbed_patid # perturbing pat_id
    #
    #         if params_str2list['has_extra_quotes']:
    #             line_as_list = ["\"" + x + "\"" for x in line_as_list]
    #
    #         line_perturbed = params_str2list['sep'].join(line_as_list) #first col won't be a problem
    #
    #         line_perturbed += '\n'
    #
    #         fw.write(line_perturbed)

    # Both name lists have the same order!

    # def create_large_files(raw_data_files,raw_data_folderpath,
    #                        large_data_files,large_data_folderpath,
    #                        num_repeats=100,USE_CACHED_DB=True):
    #     import os
    #     if os.path.exists(large_data_folderpath + '/' + large_data_files[0]):
    #         if USE_CACHED_DB:
    #             log.info("Large files exist!")
    #             return
    #         else:
    #             # for large_data_file in large_data_files:
    #             for one_file in os.listdir(large_data_folderpath):
    #                 os.remove(large_data_folderpath + '/' + one_file)
    #
    #     if 'labs' not in raw_data_files[0]:
    #         log.debug("Please place labs file as the beginning of raw_data_files!")
    #         quit()
    #
    #     params_str2list = {}
    #     if LocalEnv.DATASET_SOURCE_NAME == 'UMich':
    #         col_patid = 1
    #
    #         params_str2list['sep'] = '|'
    #         params_str2list['has_extra_quotes'] = True
    #         params_str2list['skip_first_col'] = True
    #     elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
    #         col_patid = 0
    #
    #         params_str2list['sep'] = '\t'
    #         params_str2list['has_extra_quotes'] = False
    #         params_str2list['skip_first_col'] = False
    #
    #     # query all_pat_ids from raw_data. Presumably small files, so should not be problem
    #     with open(raw_data_folderpath + '/' + raw_data_files[0]) as f:
    #         lines_lab = f.readlines()
    #         f.close()
    #
    #     all_pat_ids = set([utils_NonSTRIDE.line_str2list(line,params_str2list=params_str2list)[col_patid] for line in lines_lab[1:]]) # skip the first row as columns
    #
    #     # Each time, perturb pat_ids in a specific random way, and modify all tables accordingly...
    #     for _ in range(num_repeats):
    #         # Create a different perturbation rule each time
    #         perturb_dict = {}
    #         for pat_id in all_pat_ids:
    #             perturb_dict[pat_id] = perturb_str(pat_id)
    #
    #         # For each perturbation, perturb all tables
    #         for ind in range(len(raw_data_files)):
    #             raw_file_path = raw_data_folderpath+'/'+raw_data_files[ind]
    #             target_file_path = large_data_folderpath+'/'+large_data_files[ind]
    #             perturb_a_file(raw_file_path, target_file_path, col_patid=col_patid,
    #                            perturb_dict=perturb_dict, params_str2list=params_str2list)

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
            curr_row = utils_NonSTRIDE.line_str2list(line_str, skip_first_col=True,
                                                     test_mode=self.test_mode)
                                                     # params_str2list=params_str2list)
            if len(curr_row) < normal_num_cols/2: #
                # log.info('severely missing data when processing')
                continue
            all_rows.append(curr_row)

        data_df = pd.DataFrame(all_rows, columns=colnames)
        return data_df


    def pd2db(self, data_df, df_name, db_path, db_name, data_source):
        conn = sqlite3.connect(db_path + '/' + db_name)

        if data_source == 'UMich':
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
                print df_name + " does not exist for UMich!"

        elif data_source == 'UCSF':

            if df_name == "labs":  #
                tab2df_dict = utils_NonSTRIDE.pd_process_labs(data_df)
            elif df_name == "demographics_and_diagnoses":
                tab2df_dict = utils_NonSTRIDE.pd_process_demogdiagn(data_df)
            elif df_name == 'vitals':
                tab2df_dict = utils_NonSTRIDE.pd_process_vitals(data_df)
            else:
                print df_name + " does not exist for UCSF!"

        for table_name in tab2df_dict.keys():
            tab2df_dict[table_name].to_sql(table_name, conn, if_exists="append")

        return tab2df_dict.keys()

    def preprocess_files(self, data_source, raw_data_folderpath):
        if data_source == 'UCSF':
            import utils_UCSF as utils_specs
            utils_specs.separate_demog_diagn_encnt(raw_data_folderpath)
            utils_specs.separate_labs_team(raw_data_folderpath)
        else:
            pass

    # Chunk mechanism, should be general for any outside data
    def raw2db(self, data_file, data_folderpath, db_path, db_name,
           data_source, build_index_patid=True):
        chunk_size = 100000  # num of rows

        print 'Now writing %s into database...' % data_file  #

        generated_tables = []

        with open(data_folderpath + '/' + data_file) as f:
            is_first_chunk = True
            while True:
                # a chunk of rows
                next_n_lines_str = list(islice(f, chunk_size))
                if not next_n_lines_str:
                    break

                params_str2list = {}
                if data_source == 'UMich':
                    params_str2list['sep'] = '|'
                    params_str2list['has_extra_quotes'] = True
                    params_str2list['skip_first_col'] = True
                elif data_source == 'UCSF':
                    params_str2list['sep'] = '\t'
                    params_str2list['has_extra_quotes'] = False
                    params_str2list['skip_first_col'] = False

                if is_first_chunk:
                    colnames = utils_NonSTRIDE.line_str2list(next_n_lines_str[0],
                                                             test_mode=self.test_mode)
                                                             # , params_str2list, is_column=True)
                    data_df = self.lines2pd(next_n_lines_str[1:], colnames)
                                       #, params_str2list)
                    is_first_chunk = False
                else:  ## make each chunk into pandas
                    data_df = self.lines2pd(next_n_lines_str, colnames)
                                       # params_str2list)

                ## append each pandas to db tables
                if data_source == 'UMich':
                    df_name = data_file.replace(".txt", "")
                    df_name = df_name.replace(".sample", "")
                    df_name = df_name.replace(".test", "")
                    df_name = df_name.replace(".large", "")
                    df_name = df_name.replace('.', '_')  # pt.info
                elif data_source == 'UCSF':
                    df_name = data_file.replace(".tsv", "")  #
                    df_name = df_name.replace("_deident", "")
                    df_name = df_name.replace('.', '_')
                generated_tables += self.pd2db(data_df, df_name=df_name, db_path=db_path, db_name=db_name, data_source=data_source)
                ##

        if build_index_patid:
            conn = sqlite3.connect(db_path + '/' + db_name)

            for generated_table in generated_tables:
                build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);" % (generated_table, generated_table, 'pat_id')
                # print build_index_query
                conn.execute(build_index_query)