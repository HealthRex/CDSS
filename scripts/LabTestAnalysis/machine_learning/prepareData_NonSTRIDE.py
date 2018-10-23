

import sqlite3
from itertools import islice
import pandas as pd
import LocalEnv
from medinfo.common.Util import log
import os
import numpy as np
import random, string

def filter_nonascii(any_str):
    return ''.join([i if ord(i) < 128 else ' ' for i in any_str])

def filter_nondigits(any_str):
    return ''.join([x for x in str(any_str) if x in '-.0123456789'])

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

def line_str2list(line_str, params_str2list):
    line_list = line_str.split(params_str2list['sep'])
    if params_str2list['skip_first_col']:
        line_list = line_list[1:]
    line_list = [x.strip() for x in line_list]
    if params_str2list['has_extra_quotes']:
        line_list = [x[1:-1] for x in line_list]
    return line_list

    # # Get rid of extra quotes
    # if skip_first_col:
    #     # get rid of meaningless first col index
    #     return [x.strip()[1:-1] for x in line_str.split('|')][1:]
    # else:
    #     return [x.strip()[1:-1] for x in line_str.split('|')]


def perturb_str(any_str, seed=None): #TODO: Doing seeding in the future
    str_len = len(any_str)
    ind_to_perturb = np.random.choice(str_len)
    chr_to_perturb = random.choice(string.letters + '-0123456789')
    any_str = any_str[:ind_to_perturb] + chr_to_perturb + any_str[ind_to_perturb+1:]
    return any_str

def perturb_a_file(raw_file_path, target_file_path, col_patid, my_dict):
    with open(raw_file_path) as fr:
        lines_raw = fr.readlines()
        fr.close()

    import os
    if not os.path.exists(target_file_path):
        fw = open(target_file_path,'w')
        fw.write(lines_raw[0]) # column name line
    else:
        fw = open(target_file_path,'a')
    for line_raw in lines_raw[1:]:
        line_as_list = line_str2list(line_raw)
        try:
            cur_pat_id = line_as_list[col_patid]
        except:
            # Handle cases where the line is empty
            continue

        perturbed_patid = my_dict[cur_pat_id]
        line_as_list[col_patid] = perturbed_patid # perturbing pat_id
        line_as_list = ["\"" + x + "\"" for x in line_as_list]
        line_perturbed = "|".join(line_as_list)
        line_perturbed += '\n'

        fw.write(line_perturbed)

# Both name lists have the same order!
def create_large_files(raw_data_files,raw_data_folderpath,
                       large_data_files,large_data_folderpath,
                       num_repeats=100,USE_CACHED_DB=True):
    import os
    if os.path.exists(large_data_folderpath + '/' + large_data_files[0]):
        if USE_CACHED_DB:
            log.info("Large files exist!")
            return
        else:
            for large_data_file in large_data_files:
                os.remove(large_data_folderpath + '/' + large_data_file)

    if 'labs' not in raw_data_files[0]:
        quit("Please place labs file as the beginning of raw_data_files!") # TODO: quit(int)?

    # query all_pat_ids from raw_data. Presumably small files, so should not be problem
    with open(raw_data_folderpath + '/' + raw_data_files[0]) as f:
        lines_lab = f.readlines()
        f.close()
    all_pat_ids = set([line_str2list(line)[1] for line in lines_lab[1:]]) #set([line.split('|')[1] for line in lines[1:]])

    # Each time, perturb pat_ids in a specific random way, and modify all tables accordingly...
    for _ in range(num_repeats):
        # Create a different perturbation rule each time
        my_dict = {}
        for pat_id in all_pat_ids:
            my_dict[pat_id] = perturb_str(pat_id)

        # For each perturbation, perturb all tables
        for ind in range(len(raw_data_files)):
            raw_file_path = raw_data_folderpath+'/'+raw_data_files[ind]
            target_file_path = large_data_folderpath+'/'+large_data_files[ind]
            perturb_a_file(raw_file_path, target_file_path, col_patid=1, my_dict=my_dict)

def lines2pd(lines_str, colnames, params_str2list):
    normal_num_cols = len(colnames)

    all_rows = []
    for line_str in lines_str:
        curr_row = line_str2list(line_str, params_str2list=params_str2list)

        if len(curr_row) < normal_num_cols/2: #
            # log.info('severely missing data when processing')
            continue
        all_rows.append(curr_row)

    data_df = pd.DataFrame(all_rows, columns=colnames)
    return data_df

def prepare_database(raw_data_files, raw_data_folderpath, db_name, data_source,
                     fold_enlarge_data=1, USE_CACHED_DB=False):

    if os.path.exists(os.path.join(raw_data_folderpath, db_name)):
        if USE_CACHED_DB:
            log.info(db_name + " already exists!")
            return
        else:
            os.remove(os.path.join(raw_data_folderpath, db_name))

    ## Have to handle UCSF by converting:
    # Input: demographics_and_diagnoses:
    # Output: demographics, diagnoses

    if fold_enlarge_data != 1: # TODO: fix for UCSF, perturbing stuff etc.
        large_data_folderpath = raw_data_folderpath + '/' + 'enlarged_data_by_%s_fold'%str(fold_enlarge_data)

        if not os.path.exists(large_data_folderpath):
            os.mkdir(large_data_folderpath)

        large_data_files = [x.replace('sample','large') for x in raw_data_files]
        # Same file names, different folders
        create_large_files(raw_data_files,raw_data_folderpath,
                                       large_data_files,large_data_folderpath,
                                                     num_repeats=fold_enlarge_data, USE_CACHED_DB=USE_CACHED_DB)
        data_files = large_data_files
        data_folderpath = large_data_folderpath
    else:
        data_files = raw_data_files
        data_folderpath = raw_data_folderpath

    for data_file in data_files:
        raw2db(data_file, data_folderpath, db_path=raw_data_folderpath,
               db_name=db_name, build_index_patid=True, data_source=data_source)


def pd2db(data_df, db_path, table_name, db_name, data_source):
    conn = sqlite3.connect(db_path + '/' + db_name)

    if data_source == 'UMich':
        import utils_UMich as utils_specs
    elif data_source == 'UCSF':
        import utils_UCSF as utils_specs

    if table_name == "labs":  #
        data_df = utils_specs.pd_process_labs(data_df)
    elif table_name == "pt_info":
        data_df = utils_specs.pd_process_pt_info(data_df)
    elif table_name == "encounters":
        data_df = utils_specs.pd_process_encounters(data_df)
    elif table_name == "demographics":
        data_df = utils_specs.pd_process_demographics(data_df)
    elif table_name == "diagnoses":
        data_df = utils_specs.pd_process_diagnoses(data_df)
    elif table_name == 'vitals':
        data_df = utils_specs.pd_process_vitals(data_df)
    else:
        print table_name + " does not exist!"

    data_df.to_sql(table_name, conn, if_exists="append")

def preprocess_files(data_source, raw_data_folderpath):
    if data_source == 'UCSF':
        import utils_UCSF as utils_specs
        utils_specs.separate_demog_diagn_encnt(raw_data_folderpath)
    else:
        pass

# Chunk mechanism, should be general for any outside data
def raw2db(data_file, data_folderpath, db_path, db_name,
           data_source, build_index_patid=True):
    chunk_size = 10000  # num of rows

    print 'Now writing %s into database...' % data_file  #

    if data_source == 'UMich':
        table_name = data_file.replace(".txt", "")
        table_name = table_name.replace(".sample", "")
        table_name = table_name.replace(".large", "")
        table_name = table_name.replace('.', '_')  # pt.info
    elif data_source == 'UCSF':
        table_name = data_file.replace(".tsv", "")  # TODO:UCSF
        table_name = table_name.replace("_deident", "")
        table_name = table_name.replace('.', '_')

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
                colnames = line_str2list(next_n_lines_str[0], params_str2list)
                # print colnames
                data_df = lines2pd(next_n_lines_str[1:], colnames, params_str2list)
                is_first_chunk = False
            else:  ## make each chunk into pandas
                data_df = lines2pd(next_n_lines_str, colnames, params_str2list)

            ## append each pandas to db tables
            pd2db(data_df, db_path=db_path, db_name=db_name, table_name=table_name, data_source=data_source)
            ##
    if build_index_patid:
        conn = sqlite3.connect(db_path + '/' + db_name)
        build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);" % (table_name, table_name, 'pat_id')
        # print build_index_query
        conn.execute(build_index_query)