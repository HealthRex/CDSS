#!/usr/bin/python

import unittest
from sklearn.model_selection import train_test_split

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase
from SupervisedClassifierTestData import RANDOM_REGRESSION_TEST_CASE
from medinfo.ml.Regressor import Regressor

class TestRegressor(MedInfoTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        # Test unspecified algorithm.
        regressor = Regressor()
        self.assertEqual(regressor.algorithm(), Regressor.LASSO)

        # Test unsupported algorithm.
        with self.assertRaises(ValueError):
            Regressor(algorithm="foo")

        # Confirm specified algorithm selection.
        regressor = Regressor(algorithm=Regressor.LINEAR_REGRESSION)
        self.assertEqual(regressor.algorithm(), Regressor.LINEAR_REGRESSION)

    def test_train(self):
        # Load data set.
        X = RANDOM_REGRESSION_TEST_CASE["X"]
        y = RANDOM_REGRESSION_TEST_CASE["y"]

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y)

        # Train logistic regression model.
        regressor = Regressor(algorithm=Regressor.LASSO)
        regressor.train(X_train, y_train)

        # Test value of coefficients.
        expected_coef = RANDOM_REGRESSION_TEST_CASE["coef"]
        actual_coef = regressor.coef()
        for expected, actual in zip(expected_coef, actual_coef):
            if expected == 0:
                self.assertTrue(actual < 0.01)
            else:
                error = (expected - actual)/expected
                self.assertTrue(abs(error) < 0.01)

    def test_predict(self):
        # Load data set.
        X = RANDOM_REGRESSION_TEST_CASE["X"]
        y = RANDOM_REGRESSION_TEST_CASE["y"]

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y)

        # Train logistic regression model.
        regressor = Regressor(algorithm=Regressor.LINEAR_REGRESSION)
        regressor.train(X_train, y_train)

        # Test prediction values.
        y_predicted = regressor.predict(X_test)
        for actual, predicted in zip(y_test, y_predicted):
            if actual == 0:
                self.assertTrue(predicted < 0.01)
            else:
                error = (actual - predicted)/actual
                self.assertTrue(abs(error) < 0.01)

def suite():
    """
    Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test".
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegressor))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite())
