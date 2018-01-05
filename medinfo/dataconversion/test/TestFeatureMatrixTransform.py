#!/usr/bin/python

import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase, make_test_suite
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.dataconversion.test.FMTransformTestData import MANUAL_FM_TEST_CASE

class TestFeatureMatrixTransform(MedInfoTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(1, 1)
        pass

    def test_mean_data_imputation(self):
        fmt = FeatureMatrixTransform()

        # Impute data.
        input_matrix = MANUAL_FM_TEST_CASE['input']
        fmt.set_input_matrix(input_matrix)
        fmt.impute(feature="f2", strategy="mean")

        # Verify output.
        expected_matrix = MANUAL_FM_TEST_CASE['test_mean_data_imputation']
        actual_matrix = fmt.fetch_matrix()
        self.assertEqualList(expected_matrix, actual_matrix)

    def test_mode_data_imputation(self):
        pass

    def test_add_logarithm_feature(self):
        pass

    def test_remove_feature(self):
        pass

if __name__=="__main__":
    suite = make_test_suite(TestFeatureMatrixTransform)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
