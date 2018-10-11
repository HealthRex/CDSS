

import sqlite3
from itertools import islice
import pandas as pd
import utils_UMich

import LocalEnv
db_name = LocalEnv.LOCAL_PROD_DB_PARAM["DSN"]

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
        curr_row = utils_UMich.line_str2list(line_str, skip_first_col=True)

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
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_UMich.filter_range(x) if '-' in x else x)
    # print labs_df.ix[[74,261,319,509], 'ord_num_value']
    # quit()
    labs_df['ord_num_value'] = labs_df['ord_num_value'].apply(lambda x: utils_UMich.filter_nondigits(x))

    # Make 00:00:00.0000000000 (hr;min;sec) into 00:00:00 to allow CDSS parse later
    labs_df['order_time'] = labs_df['order_time'].apply(lambda x: utils_UMich.remove_microsecs(x))
    labs_df['result_time'] = labs_df['result_time'].apply(lambda x: utils_UMich.remove_microsecs(x))

    labs_df.to_csv("labs_df.csv")


    return labs_df[['pat_id', 'order_proc_id','order_time','result_time',
                       'proc_code','base_name','ord_num_value','result_in_range_yn','result_flag']]

def pd_process_pt_info(pt_info_df): # TODO
    pt_info_df = pt_info_df.rename(columns={'PatientID':'pat_id','DOB':'Birth'})
    pt_info_df['pat_id'] = pt_info_df['pat_id'].apply(lambda x: hash(x))
    pt_info_df['Birth'] = pt_info_df['Birth'].apply(lambda x: utils_UMich.remove_microsecs(x))
    return pt_info_df[['pat_id', 'Birth']]

def pd_process_encounters(encounters_df):
    encounters_df = encounters_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','AdmitDate':'AdmitDxDate'})
    encounters_df['pat_id'] = encounters_df['pat_id'].apply(lambda x: hash(x))
    encounters_df['AdmitDxDate'] = encounters_df['AdmitDxDate'].apply(lambda x: utils_UMich.remove_microsecs(x))
    return encounters_df[['pat_id','order_proc_id','AdmitDxDate']]

def pd_process_diagnoses(diagnoses_df): # TODO
    diagnoses_df = diagnoses_df.rename(columns={'PatientID':'pat_id','EncounterID':'order_proc_id','ActivityDate':'diagnose_time','TermCodeMapped':'diagnose_code'})
    diagnoses_df['pat_id'] = diagnoses_df['pat_id'].apply(lambda x: hash(x))
    diagnoses_df['diagnose_time'] = diagnoses_df['diagnose_time'].apply(lambda x: utils_UMich.remove_microsecs(x))

    return diagnoses_df[['pat_id','order_proc_id','diagnose_time','diagnose_code']]

def pd_process_demographics(demographics_df):
    demographics_df = demographics_df.rename(columns={'PatientID':'pat_id'})
    demographics_df['pat_id'] = demographics_df['pat_id'].apply(lambda x: hash(x))
    return demographics_df[['pat_id', 'GenderName', 'RaceName']]

def pd2db(data_df, table_name):
    conn = sqlite3.connect(db_name)

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



def raw2db(txtpath, build_index_patid=True):
    chunk_size = 1000 # num of rows

    filename_txt = txtpath.split('/')[-1]
    print 'Now processing ' + filename_txt # TODO: modify this by useful info...

    table_name = filename_txt.replace(".sample.txt", "") #TODO
    table_name = table_name.replace('.','_')
    with open(txtpath) as f:
        is_first_chunk = True
        while True:
            # a chunk of rows
            next_n_lines_str = list(islice(f, chunk_size))
            if not next_n_lines_str:
                break

            if is_first_chunk:
                colnames = utils_UMich.line_str2list(next_n_lines_str[0])
                # print colnames
                data_df = lines2pd(next_n_lines_str[1:], colnames)
                is_first_chunk = False
            else:## make each chunk into pandas
                data_df = lines2pd(next_n_lines_str, colnames)

            ## append each pandas to db tables
            pd2db(data_df, table_name=table_name)
            ##
    if build_index_patid:
        conn = sqlite3.connect(db_name)
        build_index_query = "CREATE INDEX IF NOT EXISTS index_for_%s ON %s (%s);"%(table_name,table_name,'pat_id')
        # print build_index_query
        conn.execute(build_index_query)

def prepare_database(data_folder_path): #TODO: UMich.db also put here?
    import os
    if os.path.exists(db_name):
        print db_name + "exists!"
        return
    raw_txtpaths = ['labs.sample.txt',
                 'pt.info.sample.txt',
                 'encounters.sample.txt',
                 'demographics.sample.txt',
                 'diagnoses.sample.txt']
    raw_txtpaths  = [data_folder_path+x for x in raw_txtpaths]

    for txtpath in raw_txtpaths:
        raw2db(txtpath, build_index_patid=True)


if __name__ == '__main__':
    prepare_database(data_folder_path='raw_data_UMich/')





