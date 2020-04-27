#!/usr/bin/python
"""
Test suite for FeatureMatrixIO.
"""

import filecmp
import inspect
import os
from pandas import read_csv
from pandas.testing import assert_frame_equal
import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.dataconversion.test.FeatureMatrixIOTestData import MANUAL_TEST_CASE

class TestFeatureMatrixIO(MedInfoTestCase):
    def setUp(self):
        # Set up temp files.
        self._no_header_temp_file_path = '_no_header_temp_file_path'
        self._with_header_temp_file_path = '_with_header_temp_file_path'
        self._stripped_header_file_path = '_stripped_header_file_path'

    def tearDown(self):
        # Clean up temp files.
        temp_files = [
            self._no_header_temp_file_path,
            self._with_header_temp_file_path,
            self._stripped_header_file_path
        ]
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass

    def test_strip_header(self):
        # Initialize FeatureMatrixIO.
        fm_io = FeatureMatrixIO()

        # Build paths for test files.
        app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        no_header_file_name = 'test-matrix-no-header.tab'
        with_header_file_name = 'test-matrix-with-header.tab'
        no_header_file_path = os.path.join(app_dir, no_header_file_name)
        with_header_file_path = os.path.join(app_dir, with_header_file_name)

        # Strip header.
        matrix_with_header = fm_io.read_file_to_data_frame(with_header_file_path)
        self._stripped_header_file_path = fm_io.strip_header(with_header_file_path)

        # Validate matrix data.
        expected_matrix = MANUAL_TEST_CASE['matrix_no_header']
        actual_matrix = fm_io.read_file_to_data_frame(self._stripped_header_file_path, \
            datetime_col_index=1)
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_read_file_to_data_frame(self):
        # Initialize FeatureMatrixIO.
        fm_io = FeatureMatrixIO()

        # Build paths for test files.
        app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        no_header_file_name = 'test-matrix-no-header.tab'
        with_header_file_name = 'test-matrix-with-header.tab'
        no_header_file_path = os.path.join(app_dir, no_header_file_name)
        with_header_file_path = os.path.join(app_dir, with_header_file_name)

        # Read files into data frames.
        matrix_stripped_header = fm_io.read_file_to_data_frame(with_header_file_path)
        matrix_no_header = fm_io.read_file_to_data_frame(no_header_file_path)

        # Verify that FeatureMatrixIO correctly stripped the header.
        expected_matrix = MANUAL_TEST_CASE['matrix_no_header']
        assert_frame_equal(expected_matrix, matrix_stripped_header)
        assert_frame_equal(expected_matrix, matrix_no_header)

    def test_write_data_frame_to_file(self):
        # Initialize FeatureMatrixIO.
        fm_io = FeatureMatrixIO()

        # Build paths for test files.
        app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        no_header_file_name = 'test-matrix-no-header.tab'
        with_header_file_name = 'test-matrix-with-header.tab'
        no_header_file_path = os.path.join(app_dir, no_header_file_name)
        with_header_file_path = os.path.join(app_dir, with_header_file_name)

        # Read data frames from test files.
        matrix_no_header = MANUAL_TEST_CASE['matrix_no_header']
        matrix_header = MANUAL_TEST_CASE['custom_header']

        # Write data frame without header.
        no_header_temp_file_name = 'no-header-temp-file.tab'
        self._no_header_temp_file_path = os.path.join(app_dir, no_header_temp_file_name)
        fm_io.write_data_frame_to_file(matrix_no_header, self._no_header_temp_file_path)

        # Write data frame with header.
        with_header_temp_file_name = 'header-temp-file.tab'
        self._with_header_temp_file_path = os.path.join(app_dir, with_header_temp_file_name)
        fm_io.write_data_frame_to_file(matrix_no_header, self._with_header_temp_file_path, matrix_header)

        # Validate output files.
        self.assertTrue(filecmp.cmp(no_header_file_path, self._no_header_temp_file_path))
        self.assertTrue(filecmp.cmp(with_header_file_path, self._with_header_temp_file_path))

if __name__=="__main__":
    suite = make_test_suite(TestFeatureMatrixIO)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
