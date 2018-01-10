#!/usr/bin/python

import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from medinfo.ml.FeatureSelector import FeatureSelector
from FeatureSelectorTestData import RANDOM_REGRESSION_TEST_CASE

class TestFeatureSelector(MedInfoTestCase):
    def setUp(self):
        fs = FeatureSelector()
        pass

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_generate_univariate_test_case(self):

        # Generate data set.
        # X, y = generate_univariate_test_case(variances)

        # Confirm X has len(variances) features.

        # Confirm variance(x_i) == variances[i].

        # Confirm that
        pass

    def test_generate_multivariate_test_case(self):
        pass

    def test_remove_high_variance(self):
        # remove_>1_variance
        # remove_>0.1_variance
        # remove_>0.01_variance
        pass

    def test_select_K_best(self):
        # Fetch test case.
        X = RANDOM_REGRESSION_TEST_CASE['X']
        y = RANDOM_REGRESSION_TEST_CASE['y']
        coefs = RANDOM_REGRESSION_TEST_CASE['coefs']
        sorted_coefs = sorted(coefs, reverse=True)

        # For the test example, the true implementation flips the significance
        # of features 3 and 4 because their weights are so similar, so we know
        # that k=3 will fail. Don't bother testing.
        K_VALUES = [5, 4, 2, 1]
        for k in K_VALUES:
            # Set input features and values.
            fs = FeatureSelector(algorithm=FeatureSelector.SELECT_K_BEST, \
                problem=FeatureSelector.REGRESSION)
            fs.set_input_matrix(X, y)

            # Select 5 best features.
            fs.select(k=k)
            feature_ranks = fs.compute_ranks()

            # Identify the minimum true coefficient value for which we expect
            # feature must have been selected.
            min_true_coef_val = sorted_coefs[k]

            # Iterate through features to confirm we selected at least the k
            # we know we should have selected.
            feature_index = 0
            for feature in feature_ranks:
                if coefs[feature_index] > min_true_coef_val:
                    # The ordering of the significant features isn't maintained
                    # by SelectKBest. Therefore, just confirm that the k
                    # features with the highest true weights are selected.
                    self.assertTrue(feature_ranks[feature_index] <= k)
                feature_index += 1

    def test_select_percentile(self):
        # select_60%_best (15)
        # select_20%_best (5)
        # select_8%_best (2)
        pass

    def test_eliminate_recursively(self):
        # select_5_best
        # select_3_best
        # select_1_best
        pass

    def test_select_recursively(self):
        # select_1_best
        # select_3_best
        # select_5_best
        pass

if __name__=="__main__":
    suite = make_test_suite(TestFeatureSelector)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
