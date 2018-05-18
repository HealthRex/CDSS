#!/usr/bin/python
"""
Test suite for RegressorAnalyzer.
"""

import filecmp
import os
from pandas import DataFrame, Series
from pandas.util.testing import assert_frame_equal
import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from medinfo.ml.Regressor import Regressor
from medinfo.ml.RegressorAnalyzer import RegressorAnalyzer
from RegressorAnalyzerTestData import RANDOM_REGRESSION_TEST_CASE

# Use a simple Regressor instead of a true Regressor so that the predictions
# are non-random, and we can validate the output.
class LinearPredictor(Regressor):
    def __repr__(self):
        return 'LinearPredictor(%s)' % self._coefs

    __str__ = __repr__

    def __init__(self, coefs):
        self._coefs = coefs

    def predict(self, X):
        predictions = X.dot(self._coefs)
        return DataFrame(predictions)

class TestRegressorAnalyzer(MedInfoTestCase):
    def setUp(self):
        coef_predicted = RANDOM_REGRESSION_TEST_CASE['coef_predicted']
        self._regressor = LinearPredictor(coef_predicted)
        X_test = RANDOM_REGRESSION_TEST_CASE['X']
        y_test = RANDOM_REGRESSION_TEST_CASE['y_true']
        self._analyzer = RegressorAnalyzer(self._regressor, X_test, y_test)

    def tearDown(self):
        # Clean up the actual report file.
        try:
            test_dir = os.path.dirname(os.path.abspath(__file__))
            actual_report_name = 'actual-linear-predictor.report'
            actual_report_path = '/'.join([test_dir, actual_report_name])
            os.remove(actual_report_path)
        except OSError:
            pass

    def test_score_accuracy(self):
        # Compute accuracy.
        expected_accuracy = RANDOM_REGRESSION_TEST_CASE['accuracy']
        actual_accuracy = self._analyzer.score()

        self.assertEqual(expected_accuracy, actual_accuracy)

    def test_score_r2(self):
        # Compute r2.
        expected_r2 = RANDOM_REGRESSION_TEST_CASE['r2']
        actual_r2 = self._analyzer.score(metric=RegressorAnalyzer.R2_SCORE)

        self.assertEqual(expected_r2, actual_r2)

    def test_score_median_absolute_error(self):
        # Compute median_absolute_error.
        expected_median_error = RANDOM_REGRESSION_TEST_CASE['median_absolute_error']
        actual_median_error = self._analyzer.score(metric=RegressorAnalyzer.MEDIAN_ABSOLUTE_ERROR_SCORE)

        self.assertEqual(expected_median_error, actual_median_error)

    def test_score_mean_absolute_error(self):
        # Compute mean_absolute_error.
        expected_mean_absolute_error = RANDOM_REGRESSION_TEST_CASE['mean_absolute_error']
        actual_mean_absolute_error = self._analyzer.score(metric=RegressorAnalyzer.MEAN_ABSOLUTE_ERROR_SCORE)

        self.assertEqual(expected_mean_absolute_error, actual_mean_absolute_error)

    def test_score_explained_variance(self):
        # Compute explained_variance.
        expected_explained_variance = RANDOM_REGRESSION_TEST_CASE['explained_variance']
        actual_explained_variance = self._analyzer.score(metric=RegressorAnalyzer.EXPLAINED_VARIANCE_SCORE)

        self.assertEqual(expected_explained_variance, actual_explained_variance)

    def test_build_report(self):
        # Build report.
        expected_report = RANDOM_REGRESSION_TEST_CASE['report']
        actual_report = self._analyzer.build_report()

        # Assert values are correct.
        assert_frame_equal(expected_report, actual_report)

        # Build paths for expected and actual report.
        test_dir = os.path.dirname(os.path.abspath(__file__))
        expected_report_name = 'expected-linear-predictor.report'
        actual_report_name = 'actual-linear-predictor.report'
        expected_report_path = '/'.join([test_dir, expected_report_name])
        actual_report_path = '/'.join([test_dir, actual_report_name])

        # Write the report.
        self._analyzer.write_report(actual_report_path)

        # Assert files equal.
        self.assertTrue(filecmp.cmp(expected_report_path, actual_report_path))

if __name__ == '__main__':
    suite = make_test_suite(TestRegressorAnalyzer)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
