#!/usr/bin/python
"""
Simple wrapper around BoxClient for downloading STRIDE data from Box.

Class for extracting, transforming, and loading raw STRIDE files as delivered by
Stanford into a proper format that can be analyzed (psql, R, etc).

All knowledge about the oddities of the STRIDE dataset should be confined
to this file. It will try to solve a number of problems, including:
* Inconsistencies in column names (e.g. pat_id vs. pat_anon_id)
* Inconsistencies in using quotes (e.g. pat_id vs. "pat_id" for headers)
* Inconsistencies in capitalization
* Quotes which prevent logical data types (e.g. "1980" vs. 1980 for timestamps)
"""

import inspect
import logging
import os
import gzip
import shutil
import pandas as pd
import numpy as np

from LocalEnv import BOX_STRIDE_FOLDER_ID, PATH_TO_CDSS, LOCAL_PROD_DB_PARAM
from stride.box.BoxClient import BoxClient
from medinfo.db import DBUtil
from medinfo.common.Util import log
from stride.rxnorm.RxNormClient import RxNormClient
from stride.core.StrideLoaderParams import STRIDE_LOADER_PARAMS

class StrideLoader:
    @staticmethod
    def fetch_stride_dir():
        # CDSS/stride/
        return os.path.join(PATH_TO_CDSS, 'stride')

    @staticmethod
    def fetch_core_dir():
        # CDSS/core/
        return os.path.join(PATH_TO_CDSS, 'core')

    @staticmethod
    def fetch_data_dir():
        # CDSS/stride/data/
        stride_dir = StrideLoader.fetch_stride_dir()
        return os.path.join(stride_dir, 'data')

    @staticmethod
    def fetch_clean_data_dir():
        data_dir = StrideLoader.fetch_data_dir()
        return os.path.join(data_dir, 'clean')

    @staticmethod
    def fetch_raw_data_dir():
        data_dir = StrideLoader.fetch_data_dir()
        return os.path.join(data_dir, 'raw')

    @staticmethod
    def fetch_psql_dir():
        # CDSS/stride/data/
        stride_dir = StrideLoader.fetch_stride_dir()
        return os.path.join(stride_dir, 'psql')

    @staticmethod
    def fetch_psql_schemata_dir():
        # CDSS/stride/schemata/
        psql_dir = StrideLoader.fetch_psql_dir()
        return os.path.join(psql_dir, 'schemata')

    @staticmethod
    def download_stride_data():
        data_dir = StrideLoader.fetch_data_dir()

        # Remote folder ID defined in LocalEnv.
        box = BoxClient()
        box.download_folder(BOX_STRIDE_FOLDER_ID, data_dir)

    @staticmethod
    def build_clean_data_file(source_path, dest_path):
        # Force pandas to read certain fields as an object.
        # This both makes read_csv faster and reduces parsing errors.
        # Fields that look like integers should be read as objects so that
        # missing data doesn't force pandas to read as a float.
        # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
        raw_data = pd.read_csv(source_path, compression='gzip', \
                                dtype=object, skipinitialspace=True,
                                error_bad_lines=False, warn_bad_lines=True)

        # Make header column all lowercase.
        raw_data.columns = [column.lower() for column in raw_data.columns]

        # Make custom patches to the data values. Any parsing errors should
        # be fixed offline, but any data oddities should be fixed here.
        raw_file_name = os.path.split(source_path)[-1]
        # If generating a *_mapped_meds file, append active_ingredient.
        if 'Chen_Mapped_Meds' in raw_file_name:
            rxnorm = RxNormClient()
            name_function = rxnorm.fetch_name_by_rxcui
            raw_data['active_ingredient'] = raw_data['rxcui'].map(name_function)
        elif 'fio2' in raw_file_name:
            # TODO(sbala): Find a way to capture the PEEP value in our schema.
            # FiO2 is sometimes recorded as a FiO2/PEEP value, which cannot
            # be stored as a floating point number. Given <5% of values include
            # a PEEP value (Positive End Expiratory-Pressure), it's OK to lose
            # this information. e.g. "0.50/8-10" ==> "0.50"
            float_value = raw_data['flowsheet_value'].str.split('/', \
                                                                expand=True)[0]
            raw_data['flowsheet_value'] = float_value


        # Write to csv.
        raw_data.to_csv(path_or_buf=dest_path, compression='gzip', index=False)

    @staticmethod
    def build_starr_psql_schemata():
        schemata_dir = StarrLoader.fetch_psql_schemata_dir()
        for params in STARR_LOADER_PARAMS.values():
            psql_table = params['psql_table']

            log.debug('loading %s schema...' % psql_table)

            # Open file, feed to DBUtil, and close file.
            schema_file_name = '.'.join([psql_table, 'schema.sql'])
            schema_file_path = os.path.join(schemata_dir, schema_file_name)
            schema_file = open(schema_file_path, 'r')
            DBUtil.runDBScript(schema_file)
            schema_file.close()

    @staticmethod
    def clear_starr_psql_tables():
        log.info('Clearing starr psql tables...')
        for params in STARR_LOADER_PARAMS.values():
            psql_table = params['psql_table']
            log.debug('dropping table %s...' % psql_table)
            # load_starr_to_psql is not itempotent, so in case schema already
            # existed, clear table (avoid duplicate data).
            # existence_query = "SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename = '%s')"
            # table_exists = DBUtil.execute(existence_query % psql_table)[0][0]
            # if table_exists:
            #     DBUtil.execute("DELETE FROM %s;" % psql_table)
            DBUtil.execute("DROP TABLE IF EXISTS %s CASCADE;" % psql_table)

    @staticmethod
    def load_starr_to_psql():
        # Clear any old data.
        StarrLoader.clear_starr_psql_tables()
        # Build schemata.
        StarrLoader.build_starr_psql_schemata()

        # Build paths to clean data files.
        raw_data_dir = StarrLoader.fetch_raw_data_dir()
        clean_data_dir = StarrLoader.fetch_clean_data_dir()
        for raw_file in sorted(STARR_LOADER_PARAMS.keys()):
            params = STARR_LOADER_PARAMS[raw_file]

            # Build clean data file.
            clean_file = params['clean_file']
            log.info('loading %s...' % clean_file)
            raw_path = os.path.join(raw_data_dir, raw_file)
            clean_path = os.path.join(clean_data_dir, clean_file)
            log.debug('starr/data/[raw/%s] ==> [clean/%s]' % (raw_file, clean_file))
            # Building the clean file is the slowest part of setup, so only
            # do it if absolutely necessary. This means that users must be
            # aware of issues like a stale cache.
            if not os.path.exists(clean_path):
                StarrLoader.build_clean_data_file(raw_path, clean_path)

            # Uncompress data file.
            unzipped_clean_path = clean_path[:-3]
            with gzip.open(clean_path, 'rb') as f_in, open(unzipped_clean_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            # psql COPY data from clean files into DB.
            psql_table = params['psql_table']
            log.debug('starr/data/clean/%s ==> %s' % (clean_file, psql_table))
            # In some cases, two files going to the same table will have
            # non-identical column names. Pass these explicitly so that
            # psql knows which columns to try to fill from file.
            # Strip the newline character.
            with open(unzipped_clean_path, 'r') as f_in:
                columns = f_in.readline()[:-1]
            command = "COPY %s (%s) FROM '%s' WITH (FORMAT csv, HEADER);" % (psql_table, columns, unzipped_clean_path)
            DBUtil.execute(command)

            # Delete unzipped_clean_path.
            os.remove(unzipped_clean_path)

        # Build starr_patient_encounter based on starr_admit_vital
        # and stride_insurance.
        starr_patient_encounter_query = \
            """
            SELECT
                si.pat_id, si.pat_enc_csn_id,
                payor_name, title,
                bp_systolic, bp_diastolic,
                temperature, pulse, respirations
            INTO TABLE
                stride_patient_encounter
            FROM
                stride_insurance AS si
            JOIN
                stride_admit_vital AS sav
            ON
                si.pat_enc_csn_id=sav.pat_enc_csn_id;
            """
        DBUtil.execute(starr_patient_encounter_query)

if __name__=='__main__':
    # StarrLoader.download_starr_data()
    log.level = logging.INFO
    StarrLoader.load_starr_to_psql()
