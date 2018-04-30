#!/usr/bin/python
"""
Simple wrapper around BoxClient for downloading STARR data from Box.
"""

import inspect
import os

from LocalEnv import BOX_STARR_FOLDER_ID, PATH_TO_CDSS
from starr.box.BoxClient import BoxClient
from medinfo.db import DBUtil

class StarrLoader:
    @staticmethod
    def fetch_starr_dir():
        # CDSS/starr/
        return PATH_TO_CDSS + 'starr/'

    @staticmethod
    def fetch_core_dir():
        # CDSS/core/
        return PATH_TO_CDSS + 'core/'

    @staticmethod
    def fetch_data_dir():
        # CDSS/starr/data/
        starr_dir = StarrLoader.fetch_starr_dir()
        return starr_dir + 'data/'

    @staticmethod
    def fetch_clean_data_dir():
        data_dir = StarrLoader.fetch_data_dir()
        return data_dir + 'clean/'

    @staticmethod
    def fetch_raw_data_dir():
        data_dir = StarrLoader.fetch_data_dir()
        return data_dir + 'raw/'

    @staticmethod
    def fetch_psql_dir():
        # CDSS/starr/data/
        starr_dir = StarrLoader.fetch_starr_dir()
        return starr_dir + 'psql/'

    @staticmethod
    def fetch_schemata_dir():
        # CDSS/starr/schemata/
        psql_dir = StarrLoader.fetch_psql_dir()
        return psql_dir + 'schemata/'

    @staticmethod
    def download_starr_data():
        data_dir = StarrLoader.fetch_data_dir()

        # Remote folder ID defined in LocalEnv.
        box = BoxClient()
        box.download_folder(BOX_STARR_FOLDER_ID, data_dir)

    @staticmethod
    def build_starr_psql_schemata():
        schemata_dir = StarrLoader.fetch_schemata_dir()
        schema_file_names = os.listdir(schemata_dir)
        # Iterate through all __.sql schema files.
        for schema_file_name in schema_file_names:
            # Ignore '.', '..', and any other miscellaneous files.
            if '.sql' not in schema_file_name:
                continue

            # Open file, feed to DBUtil, and close file.
            schema_file_path = schemata_dir + schema_file_name
            schema_file = open(schema_file_path, 'r')
            DBUtil.runDBScript(schema_file)
            schema_file.close()

    @staticmethod
    def load_stride_patient_data():
        # Build paths to raw data files.
        data_dir = StarrLoader.fetch_data_dir()
        raw_data_dir = data_dir + 'raw/'
        # Patient demographic data is split between two files covering
        # 2008-2014 and 2014-2017, respectively.
        demographics_2008_2014_file_name = 'Chen_Demographics.csv.gz'
        demographics_2014_2017_file_name = 'Chen_Demographics_Yr6_8.csv.gz'
        demographics_2008_2014_file_path = raw_data_dir + demographics_2008_2014_file_name
        demographics_2014_2017_file_path = raw_data_dir + demographics_2014_2017_file_name

        # psql COPY data from raw files into stride_patient.
        DBUtil.copy_csv_file_to_table(demographics_2008_2014_file_path, 'stride_patient')

if __name__=='__main__':
    StarrLoader.download_starr_data()
    # StarrLoader.build_starr_psql_schemata()
    # StarrLoader.load_stride_patient_data()
