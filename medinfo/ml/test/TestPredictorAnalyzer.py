#!/usr/bin/python
"""
Test suite for PredictorAnalyzer.
"""

import filecmp
import os
from pandas.util.testing import assert_frame_equal
from pandas import DataFrame
import logging
import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from medinfo.common.Util import log
from medinfo.ml.Predictor import Predictor
from medinfo.ml.PredictorAnalyzer import PredictorAnalyzer
from medinfo.ml.ListPredictor import ListPredictor
from PredictorAnalyzerTestData import MANUAL_PREDICTION_TEST_CASE

class TestPredictorAnalyzer(MedInfoTestCase):
    def setUp(self):
        log.level = logging.ERROR
        # Fetch data.
        X_test = MANUAL_PREDICTION_TEST_CASE['X']
        y_test = MANUAL_PREDICTION_TEST_CASE['y_true']
        y_predicted = MANUAL_PREDICTION_TEST_CASE['y_predicted']

        # Initialize predictor and analyzer.
        self._predictor = ListPredictor(y_predicted['predictions'])
        self._analyzer = PredictorAnalyzer(self._predictor, X_test, y_test)

    def tearDown(self):
        # Clean up the actual report file.
        try:
            test_dir = os.path.dirname(os.path.abspath(__file__))
            actual_report_name = 'actual-list-predictor.report'
            actual_report_path = '/'.join([test_dir, actual_report_name])
            os.remove(actual_report_path)
        except OSError:
            pass

    def test_score_accuracy(self):
        # Compute accuracy.
        expected_accuracy = MANUAL_PREDICTION_TEST_CASE['accuracy']
        actual_accuracy = self._analyzer.score(metric=PredictorAnalyzer.ACCURACY_SCORE)

        # Assert values are correct.
        self.assertEqual(expected_accuracy, actual_accuracy)

    def test_score_accuracy_ci(self):
        # Compute accuracy.
        expected_accuracy = MANUAL_PREDICTION_TEST_CASE['accuracy']
        expected_lower_ci = MANUAL_PREDICTION_TEST_CASE['ci_lower_bound']
        expected_upper_ci = MANUAL_PREDICTION_TEST_CASE['ci_upper_bound']
        actual_accuracy, lower_ci, upper_ci = self._analyzer.score(metric=PredictorAnalyzer.ACCURACY_SCORE, ci=0.9, n_bootstrap_iter=100)

        # Assert values are correct.
        self.assertEqual(expected_accuracy, actual_accuracy)
        self.assertEqual(expected_lower_ci, lower_ci)
        self.assertEqual(expected_upper_ci, upper_ci)

    def test_build_report(self):
        # Build report.
        expected_report = MANUAL_PREDICTION_TEST_CASE['report']
        actual_report = self._analyzer.build_report()

        # Assert values are correct.
        assert_frame_equal(expected_report, actual_report)

        # Build paths for expected and actual report.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        expected_report_name = 'expected-list-predictor.report'
        actual_report_name = 'actual-list-predictor.report'
        expected_report_path = '/'.join([test_dir, expected_report_name])
        actual_report_path = '/'.join([test_dir, actual_report_name])

        # Write the report.

        self._analyzer.write_report(actual_report, actual_report_path)

        # Assert files equal.
        self.assertTrue(filecmp.cmp(expected_report_path, actual_report_path))

if __name__=='__main__':
    suite = make_test_suite(TestPredictorAnalyzer)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
