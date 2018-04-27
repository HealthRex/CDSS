#!/usr/bin/python

from pandas.util.testing import assert_frame_equal
from scipy.stats import powerlaw
import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase, make_test_suite
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.dataconversion.test.FMTransformTestData import MANUAL_FM_TEST_CASE

class TestFeatureMatrixTransform(MedInfoTestCase):
    def setUp(self):
        self.fmt = FeatureMatrixTransform()
        input_matrix = MANUAL_FM_TEST_CASE['input']
        self.fmt.set_input_matrix(input_matrix)

    def tearDown(self):
        pass

    def test_mean_data_imputation(self):
        # Impute data.
        self.fmt.impute(feature="f2", strategy=FeatureMatrixTransform.IMPUTE_STRATEGY_MEAN)

        # Verify output.
        expected_matrix = MANUAL_FM_TEST_CASE['test_mean_data_imputation']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_mode_data_imputation_single_feature(self):
        # Impute single feature.
        self.fmt.impute(feature='f4', strategy=FeatureMatrixTransform.IMPUTE_STRATEGY_MODE)

        # Verify single feature imputation.
        expected_matrix = MANUAL_FM_TEST_CASE['test_mode_data_imputation_single_feature']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_mode_data_imputation_all_features(self):
        # Impute all features.
        self.fmt.impute(strategy=FeatureMatrixTransform.IMPUTE_STRATEGY_MODE)

        # Verify all feature imputation.
        expected_matrix = MANUAL_FM_TEST_CASE['test_mode_data_imputation_all_features']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_add_logarithm_feature(self):
        # Impute mean(f2) and add ln(f2) feature.
        self.fmt.impute(feature="f2")
        self.fmt.add_logarithm_feature('f2')

        # Hack: pandas automatically sorts the columns of a DataFrame on
        # init. To make the test data match our intended behavior, need to
        # rearrange the columns here so that ln(f2) follows f2.
        expected_matrix = MANUAL_FM_TEST_CASE['test_add_logarithm_feature']
        cols = list(expected_matrix.columns)
        cols.insert(2, cols.pop(5))
        expected_matrix = expected_matrix[cols]

        # Verify feature addition.
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_remove_feature(self):
        # Remove f2.
        self.fmt.remove_feature('f2')

        # Verify feature removal.
        expected_matrix = MANUAL_FM_TEST_CASE['test_remove_feature']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_add_indicator_feature(self):
        # Add indicator feature.
        self.fmt.add_indicator_feature('f2')

        # Hack: pandas automatically sorts the columns of a DataFrame on
        # init. To make the test data match our intended behavior, need to
        # rearrange the columns here so that ln(f2) follows f2.
        expected_matrix = MANUAL_FM_TEST_CASE['test_add_indicator_feature']
        cols = list(expected_matrix.columns)
        cols.insert(2, cols.pop(0))
        expected_matrix = expected_matrix[cols]

        # Verify feature addition.
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_add_threshold_feature(self):
        # Add threshold feature.
        self.fmt.add_threshold_feature('f2', upper_bound=3.5)

        # Hack: pandas automatically sorts the columns of a DataFrame on
        # init. To make the test data match our intended behavior, need to
        # rearrange the columns here so that I(f2<=3.5) follows f2.
        expected_matrix = MANUAL_FM_TEST_CASE['test_add_threshold_feature']
        cols = list(expected_matrix.columns)
        cols.insert(2, cols.pop(0))
        expected_matrix = expected_matrix[cols]

        # Verify feature addition.
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_add_change_interval_feature(self):
        # Add change feature.
        self.fmt.add_change_feature('interval', 0.5, 'patient_id', 'f2')

        expected_matrix = MANUAL_FM_TEST_CASE['test_add_change_interval_feature']
        cols = list(expected_matrix.columns)
        cols.insert(2, cols.pop(0))
        expected_matrix = expected_matrix[cols]

        # Verify feature addition.
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_add_change_percent_feature(self):
        # Add change feature.
        self.fmt.add_change_feature('percent', 0.35, 'patient_id', 'f2')

        expected_matrix = MANUAL_FM_TEST_CASE['test_add_change_percent_feature']
        cols = list(expected_matrix.columns)
        cols.insert(2, cols.pop(0))
        expected_matrix = expected_matrix[cols]

        # Verify feature addition.
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_zero_data_imputation(self):
        # Impute zero(f2).
        self.fmt.impute(feature="f2", strategy=FeatureMatrixTransform.IMPUTE_STRATEGY_ZERO)

        # Verify feature addition.
        expected_matrix = MANUAL_FM_TEST_CASE['test_zero_data_imputation']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def test_median_data_imputation(self):
        # Impute median(f2).
        self.fmt.impute(feature="f2", strategy=FeatureMatrixTransform.IMPUTE_STRATEGY_MEDIAN)

        # Verify feature addition.
        expected_matrix = MANUAL_FM_TEST_CASE['test_median_data_imputation']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

    def _power_law_dist(self):
        return powerlaw.rvs(1.66, random_state=2)

    def test_distrbution_data_imputation(self):
        # Impute distribution(f2).
        self.fmt.impute(feature="f2", distribution=self._power_law_dist, \
            strategy=FeatureMatrixTransform.IMPUTE_STRATEGY_DISTRIBUTION)

        # Verify feature addition.
        expected_matrix = MANUAL_FM_TEST_CASE['test_distribution_data_imputation']
        actual_matrix = self.fmt.fetch_matrix()
        assert_frame_equal(expected_matrix, actual_matrix)

if __name__=="__main__":
    suite = make_test_suite(TestFeatureMatrixTransform)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
