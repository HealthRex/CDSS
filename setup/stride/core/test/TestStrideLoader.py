#!/usr/bin/env python
"""
Test suite for respective module in application package.
"""

import os
import unittest
import shutil
import gzip

from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from LocalEnv import PATH_TO_CDSS, TEST_RUNNER_VERBOSITY

from stride.core.StrideLoader import StrideLoader


class TestStrideLoader(MedInfoTestCase):
    def setUp(self):
        test_dir = '/'.join([PATH_TO_CDSS, 'setup', 'stride', 'core', 'test'])

        # gzip test_raw_data_file.csv
        raw_file_path = '/'.join([test_dir, 'test_raw_data_file.csv'])
        self.gz_raw_file_path = '.'.join([raw_file_path, 'gz'])
        with open(raw_file_path, 'rb') as f_in, gzip.open(self.gz_raw_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        # gzip test_clean_data_file.csv
        self.clean_file_path = '/'.join([test_dir, 'test_clean_data_file.csv'])
        self.gz_clean_file_path = '.'.join([self.clean_file_path, 'gz'])
        self.files_to_clean = [self.gz_raw_file_path, self.gz_clean_file_path]

    def tearDown(self):
        # Delete both gzip files.
        for file in self.files_to_clean:
            try:
                os.remove(file)
            except OSError:
                pass

    def test_build_clean_data_file(self):
        StrideLoader.build_clean_csv_file(self.gz_raw_file_path, self.gz_clean_file_path)
        with open(self.clean_file_path, 'rt') as f_expected, gzip.open(self.gz_clean_file_path, 'rt') as f_actual:
            content_expected = f_expected.read()
            content_actual = f_actual.read()
            self.assertEqual(content_expected, content_actual);

if __name__=='__main__':
    suite = make_test_suite(TestStrideLoader)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
