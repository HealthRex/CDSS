#!/usr/bin/python
"""
Simple wrapper around BoxClient for downloading STARR data from Box.

Class for extracting, transforming, and loading raw STARR files as delivered by
Stanford into a proper format that can be analyzed (psql, R, etc).

All knowledge about the oddities of the STARR dataset should be confined
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

from LocalEnv import BOX_STARR_FOLDER_ID, PATH_TO_CDSS, LOCAL_PROD_DB_PARAM
from starr.box.BoxClient import BoxClient
from medinfo.db import DBUtil
from medinfo.common.Util import log

class StarrLoader:
    STARR_FILE_PARAMS = {
        'Chen_Demographics.csv.gz': {
            'clean_file': 'starr_demographics_2008_2014.csv.gz',
            'psql_table': 'starr_patient'
        },
        'Chen_Demographics_Yr6_8.csv.gz': {
            'clean_file': 'starr_demographics_2014_2017.csv.gz',
            'psql_table': 'starr_patient'
        },
        'Chen_Active_Meds_At_Admit.csv.gz': {
            'clean_file': 'starr_admit_meds_2008_2014.csv.gz',
            'psql_table': 'starr_admit_med'
        },
        'Chen_Admit_Vitals.csv.gz': {
            'clean_file': 'starr_admit_vitals_2008_2014.csv.gz',
            'psql_table': 'starr_admit_vital'
        },
        'Chen_Clinical_Notes_Yr1.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_1.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr2.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_2.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr3.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_3.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr4.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_4.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr5.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_5.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr6.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_6.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr7.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_7.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr8.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_8.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_DX_List_5Yr.csv.gz': {
            'clean_file': 'starr_dx_2008_2014.csv.gz',
            'psql_table': 'starr_dx'
        },
        'Chen_Dx_List_Yrs6_8.csv.gz': {
            'clean_file': 'starr_dx_2014_2017.csv.gz',
            'psql_table': 'starr_dx'
        },
        'Chen_Insurance_Info_5Yr.csv.gz': {
            'clean_file': 'starr_insurance_2008_2014.csv.gz',
            'psql_table': 'starr_insurance'
        },
        'Chen_Insurance_Info_Yrs6_8.csv.gz': {
            'clean_file': 'starr_insurance_2014_2017.csv.gz',
            'psql_table': 'starr_insurance'
        },
        'Chen_Mapped_Meds_5Yr.csv.gz': {
            'clean_file': 'starr_medication_2008_2014.csv.gz',
            'psql_table': 'starr_medication'
        },
        'Chen_Mapped_Meds_Yrs6_8.patchHeader.csv.gz': {
            'clean_file': 'starr_medication_2014_2017.csv.gz',
            'psql_table': 'starr_medication'
        },
        'Chen_MedicationID_to_MPI.csv.gz': {
            'clean_file': 'starr_medication_mpi.csv.gz',
            'psql_table': 'starr_medication_mpi'
        }
    }

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
    def fetch_psql_schemata_dir():
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
    def build_clean_data_file(source_path, dest_path):
        # Force pandas to read certain fields as a given data type.
        # This both makes read_csv faster and reduces parsing errors.
        # Fields that look like integers should be read as objects so that
        # missing data doesn't force pandas to read as a float.
        # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
        data_types = {
            # 0_integer and 1_integer only encountered in test cases.
            '0_integer': object,
            '1_INTEGER': object,
            'AUTHOR_NAME': object,
            'BIRTH_YEAR': object,
            'BP_DIASTOLIC': object,
            'BP_SYSTOLIC': object,
            'CONTACT_DATE': object,
            'COSIGNER_NAME': object,
            'data_source': object,
            'DEATH_DATE': object,
            'DEPARTMENT': object,
            'DESCRIPTION': object,
            'dx_icd9_code': object,
            'dx_icd9_code_list': object,
            'ETHNICITY': object,
            'GENDER': object,
            'GENERIC_NAME': object,
            'HOSPITAL_SERVICE': object,
            'MEDICATION_ID': object,
            'MED_NAME': object,
            'MPI_ID_VAL': object,
            'NAME': object,
            'NOTE_DATE': object,
            'noted_date': object,
            'NOTE_TYPE': object,
            'PAT_ANON_ID': object,
            'pat_id': object,
            'PAT_ID': object,
            'pat_enc_csn_id': object,
            'PAT_ENC_CSN_ID': object,
            'PAYOR_NAME': object,
            'PHARM_CLASS': object,
            'PHARM_SUBCLASS': object,
            'PROVIDER_TYPE': object,
            'PULSE': object,
            'RACE': object,
            'resolved_date': object,
            'RESPIRATIONS': object,
            'RXCUI': object,
            'SPECIALTY': object,
            'STATUS': object,
            'TEMPERATURE': float,
            'THERA_CLASS': object,
            'TITLE': object
        }

        raw_data = pd.read_csv(source_path, compression='gzip', \
                                dtype=data_types, skipinitialspace=True)
        # Make header column all lowercase.
        raw_data.columns = [column.lower() for column in raw_data.columns]

        # Write to csv.
        raw_data.to_csv(path_or_buf=dest_path, compression='gzip', \
                            index=False)

    @staticmethod
    def build_starr_psql_schemata():
        schemata_dir = StarrLoader.fetch_psql_schemata_dir()
        for params in StarrLoader.STARR_FILE_PARAMS.values():
            psql_table = params['psql_table']

            # Open file, feed to DBUtil, and close file.
            schema_file_name = '.'.join([psql_table, 'sql'])
            schema_file_path = schemata_dir + schema_file_name
            schema_file = open(schema_file_path, 'r')
            DBUtil.runDBScript(schema_file)
            schema_file.close()

    @staticmethod
    def clear_starr_psql_tables():
        for params in StarrLoader.STARR_FILE_PARAMS.values():
            psql_table = params['psql_table']
            # load_starr_to_psql is not itempotent, so in case schema already
            # existed, clear table (avoid duplicate data).
            DBUtil.execute("DELETE FROM %s;" % psql_table)

    @staticmethod
    def load_starr_to_psql():
        # Build schemata.
        StarrLoader.build_starr_psql_schemata()
        # Clear any old data.
        StarrLoader.clear_starr_psql_tables()

        # Build paths to clean data files.
        raw_data_dir = StarrLoader.fetch_raw_data_dir()
        clean_data_dir = StarrLoader.fetch_clean_data_dir()
        for raw_file in sorted(StarrLoader.STARR_FILE_PARAMS.keys()):
            params = StarrLoader.STARR_FILE_PARAMS[raw_file]

            # Build clean data file.
            clean_file = params['clean_file']
            log.info('loading %s...' % clean_file)
            raw_path = '/'.join([raw_data_dir, raw_file])
            clean_path = '/'.join([clean_data_dir, clean_file])
            log.debug('starr/data/[raw/%s] ==> [clean/%s]' % (raw_file, clean_file))
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

if __name__=='__main__':
    # StarrLoader.download_starr_data()
    log.level = logging.INFO
    StarrLoader.load_starr_to_psql()
