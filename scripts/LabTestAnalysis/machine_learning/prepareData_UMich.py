

import sqlite3

import pandas as pd
import LocalEnv
import utils_UMich

import os

def prepare_database(raw_data_files, raw_data_folderpath, db_name, fold_enlarge_data=1): #TODO: UMich.db also put here?

    if fold_enlarge_data != 1:
        # large_data_folderpath = LocalEnv.PATH_TO_CDSS + '/' + 'scripts/LabTestAnalysis/machine_learning' + '/' + large_data_foldername
        large_data_folderpath = raw_data_folderpath + '/' + 'enlarged_data_by_%s_fold'%str(fold_enlarge_data)

        if not os.path.exists(large_data_folderpath):
            os.mkdir(large_data_folderpath)
        #TODO: by default, the first one should be labs
        large_data_files = [x.replace('sample','large') for x in raw_data_files]
        # Same file names, different folders
        utils_UMich.create_large_files(raw_data_files,raw_data_folderpath,
                                       large_data_files,large_data_folderpath,
                                                     num_repeats=fold_enlarge_data)
        data_files = large_data_files
        data_folderpath = large_data_folderpath
    else:
        data_files = raw_data_files
        data_folderpath = raw_data_folderpath

    if os.path.exists(data_folderpath + '/' + db_name):
        print db_name + "exists!"
        return

    for data_file in data_files:
        utils_UMich.raw2db(data_file, data_folderpath, db_name=db_name, build_index_patid=True)


if __name__ == '__main__':

    to_create_large_files = True

    rawdata_foldername = 'raw_data_UMich'

    raw_data_files = ['labs.sample.txt',
                    'pt.info.sample.txt',
                    'encounters.sample.txt',
                    'demographics.sample.txt',
                    'diagnoses.sample.txt']
    raw_data_folderpath = LocalEnv.PATH_TO_CDSS + '/scripts/LabTestAnalysis/machine_learning/' + rawdata_foldername

    db_name = LocalEnv.LOCAL_PROD_DB_PARAM["DSN"]

    prepare_database(raw_data_files, raw_data_folderpath, db_name, fold_enlarge_data=1)





