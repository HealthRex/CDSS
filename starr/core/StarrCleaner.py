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

import numpy as np
import pandas as pd

from medinfo.common.Util import log
from starr.core.StarrLoader import StarrLoader

class StarrCleaner:
    RAW_TO_CLEAN_FILE_NAME_MAP = {
        'Chen_Demographics.csv.gz': 'starr_demographics_2008_2014.csv.gz',
        'Chen_Demographics_Yr6_8.csv.gz': 'starr_demographics_2014_2017.csv.gz',
        'Chen_Active_Meds_At_Admit.csv.gz': 'starr_active_meds_at_admit_2008_2014.csv.gz'
    }

    @staticmethod
    def build_clean_data_file(source_path, dest_path):
        # Force pandas to read certain fields as a given data type.
        data_types = {
            # Some patients lack birth_year, which causes the rest to get
            # cast to floats. To avoid this, cast to an object. Empty birth_year
            # is still modeled as pd.NaN.
            'BIRTH_YEAR': object,
            # 0_integer and 1_integer only encountered in test case.
            '0_integer': object,
            '1_INTEGER': object
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
            log.info('starr/data/[raw/%s] ==> [clean/%s]' % (raw_file, clean_file))
            raw_path = '/'.join([raw_data_dir, raw_file])
            clean_path = '/'.join([clean_data_dir, clean_file])
            StarrCleaner.build_clean_data_file(raw_path, clean_path)

if __name__ == '__main__':
    StarrCleaner.build_all_clean_data_files()
