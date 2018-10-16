
import pandas as pd
from itertools import islice
import sqlite3
import LocalEnv

def filter_nondigits(any_str):
    return ''.join([x for x in str(any_str) if x in '.0123456789'])

def filter_range(any_str): # contains sth like range a-b
    nums = any_str.strip().split('-')
    try:
        return (float(nums[0])+float(nums[1]))/2.
    except:
        return any_str

def remove_microsecs(any_str):
    try:
        return any_str.split('.')[0]
    except:
        return any_str

def line_str2list(line_str, skip_first_col=False):
    # Get rid of extra quotes
    if skip_first_col:
        # get rid of meaningless first col index
        return [x.strip()[1:-1] for x in line_str.split('|')][1:]
    else:
        return [x.strip()[1:-1] for x in line_str.split('|')]

import numpy as np
import random, string

def perturb_str(any_str, seed=None): #TODO: seeding
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
            # print 'raw_file:', raw_file
            # print 'line_as_list:', line_as_list
            # print 'col_patid:', col_patid
            continue

        perturbed_patid = my_dict[cur_pat_id]
        line_as_list[col_patid] = perturbed_patid # perturbing pat_id
        line_as_list = ["\"" + x + "\"" for x in line_as_list]
        line_perturbed = "|".join(line_as_list)
        line_perturbed += '\n'

        fw.write(line_perturbed)

#TODO: enforce both name lists have the same order
def create_large_files(raw_data_files,raw_data_folderpath,
                       large_data_files,large_data_folderpath,num_repeats=100):
    import os
    if os.path.exists(large_data_folderpath + '/' + large_data_files[0]):
        print "Large files exist!"
        return

    if 'labs' not in raw_data_files[0]:
        quit("Please place labs file as the beginning of raw_data_files!") # TODO: quit(int)?

    # query all_pat_ids from raw_data. Presumably small files, so should not be problem
    with open(raw_data_folderpath + '/' + raw_data_files[0]) as f:
        lines_lab = f.readlines()
        f.close()
    all_pat_ids = set([line_str2list(line)[1] for line in lines_lab[1:]]) #set([line.split('|')[1] for line in lines[1:]])
    # print 'all_pat_ids:', all_pat_ids

    # Each time, make pat_ids into dict, and modify all tables...
    for _ in range(num_repeats):
        # create perturbation dictionary
        my_dict = {}
        for pat_id in all_pat_ids:
            my_dict[pat_id] = perturb_str(pat_id)

        # perturb the lab table
        for ind in range(len(raw_data_files)):
            raw_file_path = raw_data_folderpath+'/'+raw_data_files[ind]
            target_file_path = large_data_folderpath+'/'+large_data_files[ind]
            perturb_a_file(raw_file_path, target_file_path, col_patid=1, my_dict=my_dict)

def lines2pd(lines_str, colnames):

    # colnames = [x.strip() for x in lines[0].split('|')]
    # Get rid of extra quotes
    # colnames = [x[1:-1] for x in colnames] #TODO: second chunk does not have colnames!
    normal_num_cols = len(colnames)

    all_rows = []
    for line_str in lines_str:
        # curr_row = [x.strip() for x in line.split('|')]
        # curr_row = curr_row[1:]
        # curr_row = [x[1:-1] for x in curr_row]
        curr_row = line_str2list(line_str, skip_first_col=True)

        if len(curr_row) < normal_num_cols/2: #
            # print 'severely missing data when processing ' + filename_txt
            continue
        all_rows.append(curr_row)

    data_df = pd.DataFrame(all_rows, columns=colnames)
    return data_df

def pd_process_labs(labs_df):
    labs_df = labs_df.rename(columns={'PatientID':'pat_id',
               'EncounterID':'order_proc_id',
               'COLLECTION_DATE':'result_time', # TODO
               'ORDER_CODE': 'proc_code',
               'RESULT_CODE': 'base_name',
               'VALUE':'ord_num_value',
               'HILONORMAL_FLAG': 'result_flag'
                })

    # Hash the string type pat_id to long int to fit into CDSS pipeline
    labs_df['pat_id'] = labs_df['pat_id'].apply(lambda x: hash(x))

    # TODO,decision: use 'COLLECTION_DATE' (result time) as 'order_time'
    labs_df['order_time'] = labs_df['result_time'].copy()

    labs_df = labs_df[labs_df['base_name'].map(lambda x:str(x)!='*')]

    # Create redundant info to fit into CDSS pipeline
    labs_df['result_in_range_yn'] = labs_df['result_flag'].apply(lambda x: 'N' if x=='L' or x=='H' or x=='A' else 'Y')

    # TODO,decision: use "0.1", "60" to handles cases like "<0.1", ">60" cases
    # TODO: maybe add a column to indicate that?
    # import re
    # range_pattern = re.compile("\d-\d")
    # print labs_df.ix[labs_df['ord_num_value'].map(lambda x: range_pattern.match(x)), 'ord_num_value']
    # quit()
    # TODO: not very robust for the "a-b" range case
    # print labs_df.ix[labs_df['ord_num_value'].map(lambda x:'-' in x), 'ord_num_value']
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: filter_range(x) if '-' in x else x)
    # print labs_df.ix[[74,261,319,509], 'ord_num_value']
    # quit()
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: filter_nondigits(x))

    # Make 00:00:00.0000000000 (hr;min;sec) into 00:00:00 to allow CDSS parse later
    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: remove_microsecs(x))
    labs_df['result_time'] = labs_df['result_time'].apply(lambda x: remove_microsecs(x))

    labs_df.to_csv("labs_df.csv")


    return labs_df[['pat_id', 'order_proc_id','order_time','result_time',
                       'proc_code','base_name','ord_num_value','result_in_range_yn','result_flag']]

def pd_process_pt_info(pt_info_df): # TODO
    pt_info_df = pt_info_df.rename(columns={'PatientID':'pat_id','DOB':'Birth'})
    pt_info_df['pat_id'] = pt_info_df['pat_id'].apply(lambda x: hash(x))
    pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: remove_microsecs(x))
    return pt_info_df[['pat_id', 'Birth']]

def pd_process_encounters(encounters_df):
    encounters_df = encounters_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','AdmitDate':'AdmitDxDate'})
    encounters_df['pat_id'] = encounters_df['pat_id'].apply(lambda x: hash(x))
    encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: remove_microsecs(x))
    return encounters_df[['pat_id','order_proc_id','AdmitDxDate']]

def pd_process_diagnoses(diagnoses_df): # TODO
    diagnoses_df = diagnoses_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','ActivityDate':'diagnose_time','TermCodeMapped':'diagnose_code'})
    diagnoses_df['pat_id'] = diagnoses_df['pat_id'].apply(lambda x: hash(x))
    diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: remove_microsecs(x))

    return diagnoses_df[['pat_id','order_proc_id','diagnose_time','diagnose_code']]

def pd_process_demographics(demographics_df):
    demographics_df = demographics_df.rename(columns={'PatientID':'pat_id'})
    demographics_df['pat_id'] = demographics_df['pat_id'].apply(lambda x: hash(x))
    return demographics_df[['pat_id', 'GenderName', 'RaceName']]

def pd2db(data_df, db_path, table_name, db_name):
    conn = sqlite3.connect(db_path + '/' + db_name)

    if table_name == "labs": # TODO: ".sample!"
        data_df = pd_process_labs(data_df)
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
    
def raw2db(data_file, data_folderpath, db_path, db_name, build_index_patid=True):
    chunk_size = 1000 # num of rows

    print 'Now processing ' + data_file # TODO: modify this by useful info...

    table_name = data_file.replace(".txt", "") #TODO
    table_name = table_name.replace(".sample","")
    table_name = table_name.replace(".large", "")
    table_name = table_name.replace('.','_') #pt.info
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
            else:## make each chunk into pandas
                data_df = lines2pd(next_n_lines_str, colnames)

            ## append each pandas to db tables
            pd2db(data_df, db_path=db_path, db_name=db_name, table_name=table_name)
            ##
    if build_index_patid:
        conn = sqlite3.connect(db_path + '/' + db_name)
        build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);"%(table_name,table_name,'pat_id')
        # print build_index_query
        conn.execute(build_index_query)