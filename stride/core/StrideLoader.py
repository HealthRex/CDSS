#!/usr/bin/python
"""
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
import sys
import pandas as pd
import numpy as np
from optparse import OptionParser

from LocalEnv import BOX_STRIDE_FOLDER_ID, PATH_TO_CDSS, LOCAL_PROD_DB_PARAM
from medinfo.db import DBUtil
from medinfo.common.Util import log
from stride.rxnorm.RxNormClient import RxNormClient
from stride.core.StrideLoaderParams import TABLE_PREFIX, STRIDE_LOADER_PARAMS

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
    def fetch_psql_indices_dir():
        # CDSS/stride/indices/
        psql_dir = StrideLoader.fetch_psql_dir()
        return os.path.join(psql_dir, 'indices')

    @staticmethod
    def download_stride_data():
        data_dir = StrideLoader.fetch_data_dir()

        # Remote folder ID defined in LocalEnv.
        from stride.box.BoxClient import BoxClient  # Only import boxsdk if necessary (usually won't be)
        box = BoxClient()
        box.download_folder(BOX_STRIDE_FOLDER_ID, data_dir)

    @staticmethod
    def build_clean_csv_file(source_path, dest_path):
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
    def build_stride_psql_schemata():
        schemata_dir = StrideLoader.fetch_psql_schemata_dir()
        for params in STRIDE_LOADER_PARAMS.values():
            psql_table = params['psql_table'] % TABLE_PREFIX

            log.debug('loading %s schema...' % psql_table)

            # Open file, feed to DBUtil, and close file.
            schema_file_name = '.'.join([psql_table, 'schema.sql'])
            schema_file_path = os.path.join(schemata_dir, schema_file_name)
            schema_file = open(schema_file_path, 'r')
            DBUtil.runDBScript(schema_file)
            schema_file.close()

    @staticmethod
    def build_stride_psql_indices():
        indices_dir = StrideLoader.fetch_psql_indices_dir()
        for params in STRIDE_LOADER_PARAMS.values():
            psql_table = params['psql_table'] % TABLE_PREFIX

            # Open file, feed to DBUtil, and close file.
            indices_file_name = '.'.join([psql_table, 'indices.sql'])
            indices_file_path = os.path.join(indices_dir, indices_file_name)
            if os.path.exists(indices_file_path):
                log.debug('loading %s indices...' % psql_table)
                indices_file = open(indices_file_path, 'r')
                DBUtil.runDBScript(indices_file)
                indices_file.close()

    @staticmethod
    def clear_stride_psql_tables():
        log.info('Clearing stride psql tables...')
        for params in STRIDE_LOADER_PARAMS.values():
            psql_table = params['psql_table'] % TABLE_PREFIX
            log.debug('dropping table %s...' % psql_table)
            # load_stride_to_psql is not itempotent, so in case schema already
            # existed, clear table (avoid duplicate data).
            DBUtil.execute("DROP TABLE IF EXISTS %s CASCADE;" % psql_table)

    @staticmethod
    def process_stride_psql_db():
        # Unify labels in *_flowsheet. Can still recover distinctions
        # based on flo_meas_id.
        #   'Heart Rate' ==> 'Pulse'
        heart_rate_label_command = \
            """
            UPDATE
                %s_flowsheet
        	SET
                flowsheet_name = 'Pulse'
        	WHERE
                flowsheet_name = 'Heart Rate';
            """ % TABLE_PREFIX
        DBUtil.execute(heart_rate_label_command)
        #   'Urine Output' ==> 'Urine'
        urine_output_label_command = \
            """
            UPDATE
                %s_flowsheet
            SET
                flowsheet_name = 'Urine'
            WHERE
                flowsheet_name = 'Urine Output';
            """ % TABLE_PREFIX
        DBUtil.execute(urine_output_label_command)

        # Merge *_admit_vital and *_insurance into *_patient_encounter.
        # Insert newly merged records with negative IDs, then discard and
        # relabel old records.
        patient_encounter_merge_command = \
            """
            INSERT INTO
                %s_patient_encounter(
                    pat_enc_csn_id, pat_id,
                    payor_name, title,
                    bp_systolic, bp_diastolic,
                    temperature, pulse, respirations
                )
            SELECT
                -spe1.pat_enc_csn_id, pat_id,
                payor_name, title,
          	    max_BPS, max_BPD,
                max_temp, max_pulse, max_resp
            FROM
                (
                    SELECT
                        pat_enc_csn_id, pat_id, payor_name, title
                    FROM
                        %s_patient_encounter
                    WHERE
                        bp_systolic IS NULL
                ) AS spe1,
                (
                    SELECT
                        pat_enc_csn_id,
                        MAX(bp_systolic) as max_BPS,
                        MAX(bp_diastolic) as max_BPD,
                        MAX(temperature) as max_temp,
                        MAX(pulse) as max_pulse,
                        MAX(respirations) as max_resp
                    FROM
                        %s_patient_encounter
                    GROUP BY
                        pat_enc_csn_id
                ) spe2
            WHERE
                spe1.pat_enc_csn_id = spe2.pat_enc_csn_id;
            """ % (TABLE_PREFIX, TABLE_PREFIX, TABLE_PREFIX)
        DBUtil.execute(patient_encounter_merge_command)

        patient_encounter_cleanup_command = \
            """
            DELETE FROM
                %s_patient_encounter
            WHERE
                pat_enc_csn_id > 0;
            """ % TABLE_PREFIX
        DBUtil.execute(patient_encounter_cleanup_command)

        patient_encounter_cleanup_command = \
            """
            UPDATE
                %s_patient_encounter
            SET
                pat_enc_csn_id = -pat_enc_csn_id;
            """ % TABLE_PREFIX
        DBUtil.execute(patient_encounter_cleanup_command)

    @staticmethod
    def build_clean_csv_files():
        # Build paths to clean data files.
        raw_data_dir = StrideLoader.fetch_raw_data_dir()
        clean_data_dir = StrideLoader.fetch_clean_data_dir()
        for raw_file in sorted(STRIDE_LOADER_PARAMS.keys()):
            params = STRIDE_LOADER_PARAMS[raw_file]
            # Build clean data file path.
            clean_file = params['clean_file'] % TABLE_PREFIX
            raw_path = os.path.join(raw_data_dir, raw_file)
            clean_path = os.path.join(clean_data_dir, clean_file)
            log.debug('stride/data/[raw/%s] ==> [clean/%s]' % (raw_file, clean_file))
            # Building the clean file is the slowest part of setup, so only
            # do it if absolutely necessary. This means that users must be
            # aware of issues like a stale cache.
            if not os.path.exists(clean_path):
                StrideLoader.build_clean_csv_file(raw_path, clean_path)

    @staticmethod
    def load_stride_to_psql():
        # Build clean data files.
        StrideLoader.build_clean_csv_files()

        # Build psql schemata.
        StrideLoader.build_stride_psql_schemata()

        # Build paths to clean data files.
        clean_data_dir = StrideLoader.fetch_clean_data_dir()
        for raw_file in sorted(STRIDE_LOADER_PARAMS.keys()):
            params = STRIDE_LOADER_PARAMS[raw_file]

            # Build clean data file.
            clean_file = params['clean_file'] % TABLE_PREFIX
            log.info('loading %s...' % clean_file)
            clean_path = os.path.join(clean_data_dir, clean_file)

            # Uncompress data file.
            unzipped_clean_path = clean_path[:-3]
            with gzip.open(clean_path, 'rb') as f_in, open(unzipped_clean_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            # psql COPY data from clean files into DB.
            psql_table = params['psql_table'] % TABLE_PREFIX
            log.debug('stride/data/clean/%s ==> %s' % (clean_file, psql_table))
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

        # Run any one-off postprocessing transformations which all users
        # of the STRIDE database should receive. Defer any application-specific
        # transformations to other modules.
        StrideLoader.process_stride_psql_db()

        # Build indices.
        StrideLoader.build_stride_psql_indices()

    @staticmethod
    def backup_stride_psql_tables():
        pass

if __name__=='__main__':
    log.level = logging.DEBUG

    # Define options for command-line usage.
    usage_str = 'usage: %prog [options]\n'
    parser = OptionParser(usage=usage_str)
    parser.add_option('-s', '--schemata', dest='build_schemata',
                        action='store_true', default=False,
                        help='build STRIDE psql schemata')
    parser.add_option('-c', '--clean', dest='clean_csv_files',
                        action='store_true', default=False,
                        help='clean raw CSV and build clean CSV files')
    parser.add_option('-p', '--psql', dest='load_psql_data',
                        action='store_true', default=False,
                        help='load clean CSV data to psql database')
    parser.add_option('-b', '--backup_psql', dest='backup_psql_tables',
                        action='store_true', default=False,
                        help='backup psql tables to dump files')
    parser.add_option('-d', '--delete', dest='delete_stride',
                        action='store_true', default=False,
                        help='delete STRIDE tables')
    (options, args) = parser.parse_args(sys.argv[1:])

    # Handle command-line usage arguments.
    if options.build_schemata:
        StrideLoader.build_stride_psql_schemata()
    elif options.clean_csv_files:
        StrideLoader.build_clean_csv_files()
    elif options.load_psql_data:
        StrideLoader.load_stride_to_psql()
    elif options.backup_psql_tables:
        StrideLoader.backup_stride_psql_tables()
    elif options.delete_stride:
        StrideLoader.clear_stride_psql_tables()
