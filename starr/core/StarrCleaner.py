#!/usr/bin/python
"""
Class for cleaning raw STARR files as delivered by Stanford into a proper
format that can be piped into any CSV parser.

All knowledge about the oddities of the STARR dataset should be confined
to this file. It will try to solve a number of problems, including:
* Inconsistencies in column names (e.g. pat_id vs. pat_anon_id)
* Inconsistencies in using quotes (e.g. pat_id vs. "pat_id" for headers)
* Inconsistencies in capitalization
* Quotes which prevent logical data types (e.g. "1980" vs. 1980 for timestamps)
"""

import logging
import numpy as np
import pandas as pd

from medinfo.common.Util import log
from starr.core.StarrLoader import StarrLoader

class StarrCleaner:
    RAW_TO_CLEAN_FILE_NAME_MAP = {
        'Chen_Demographics.csv.gz': 'starr_demographics_2008_2014.csv.gz',
        'Chen_Demographics_Yr6_8.csv.gz': 'starr_demographics_2014_2017.csv.gz',
        'Chen_Active_Meds_At_Admit.csv.gz': 'starr_admit_meds_2008_2014.csv.gz',
        'Chen_Admit_Vitals.csv.gz': 'starr_admit_vitals_2008_2014.csv.gz',
        'Chen_Clinical_Notes_Yr1.csv.gz': 'starr_clinical_notes_year_1.csv.gz',
        'Chen_Clinical_Notes_Yr2.csv.gz': 'starr_clinical_notes_year_2.csv.gz',
        'Chen_Clinical_Notes_Yr3.csv.gz': 'starr_clinical_notes_year_3.csv.gz',
        'Chen_Clinical_Notes_Yr4.csv.gz': 'starr_clinical_notes_year_4.csv.gz',
        'Chen_Clinical_Notes_Yr5.csv.gz': 'starr_clinical_notes_year_5.csv.gz',
        'Chen_Clinical_Notes_Yr6.csv.gz': 'starr_clinical_notes_year_6.csv.gz',
        'Chen_Clinical_Notes_Yr7.csv.gz': 'starr_clinical_notes_year_7.csv.gz',
        'Chen_Clinical_Notes_Yr8.csv.gz': 'starr_clinical_notes_year_8.csv.gz',
    }

    @staticmethod
    def build_clean_data_file(source_path, dest_path):
        source_file = source_path.split('/')[-1]
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
            'BP_DIASTOLIC': int,
            'BP_SYSTOLIC': int,
            'CONTACT_DATE': object,
            'COSIGNER_NAME': object,
            'DEATH_DATE': object,
            'DEPARTMENT': object,
            'DESCRIPTION': object,
            'ETHNICITY': object,
            'GENDER': object,
            'HOSPITAL_SERVICE': object,
            'MEDICATION_ID': object,
            'NOTE_DATE': object,
            'NOTE_TYPE': object,
            'PAT_ANON_ID': object,
            'PAT_ID': object,
            'PAT_ENC_CSN_ID': object,
            'PHARM_CLASS': object,
            'PHARM_SUBCLASS': object,
            'PROVIDER_TYPE': object,
            'PULSE': int,
            'RACE': object,
            'RESPIRATIONS': int,
            'SPECIALTY': object,
            'STATUS': object,
            'TEMPERATURE': float,
            'THERA_CLASS': object,
        }

        raw_data = pd.read_csv(source_path, compression='gzip', \
                                dtype=data_types, skipinitialspace=True)
        # Make header column all lowercase.
        raw_data.columns = [column.lower() for column in raw_data.columns]

        # Write to csv.
        raw_data.to_csv(path_or_buf=dest_path, compression='gzip', \
                            index=False)

    @staticmethod
    def build_all_clean_data_files():
        raw_data_dir = StarrLoader.fetch_raw_data_dir()
        clean_data_dir = StarrLoader.fetch_clean_data_dir()
        for raw_file, clean_file in StarrCleaner.RAW_TO_CLEAN_FILE_NAME_MAP.iteritems():
            log.debug('starr/data/[raw/%s] ==> [clean/%s]' % (raw_file, clean_file))
            raw_path = '/'.join([raw_data_dir, raw_file])
            clean_path = '/'.join([clean_data_dir, clean_file])
            StarrCleaner.build_clean_data_file(raw_path, clean_path)

if __name__ == '__main__':
    log.level = logging.DEBUG
    StarrCleaner.build_all_clean_data_files()
