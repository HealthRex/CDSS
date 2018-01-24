#!/usr/bin/python

import unittest
from sklearn.model_selection import train_test_split

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from numpy import array

from SupervisedClassifierTestData import RANDOM_CLASSIFICATION_TEST_CASE

class TestSupervisedClassifier(MedInfoTestCase):
    def test_init(self):
        # Test unspecified algorithm.
        classifier = SupervisedClassifier([0, 1])
        self.assertEqual(classifier.algorithm(), \
            SupervisedClassifier.LOGISTIC_REGRESSION)

        # Test unsupported algorithm.
        with self.assertRaises(ValueError):
            SupervisedClassifier([0, 1], algorithm="foo")

        # Confirm specified algorithm selection.
        classifier = SupervisedClassifier([0, 1], algorithm=SupervisedClassifier.DECISION_TREE)
        self.assertEqual(classifier.algorithm(), SupervisedClassifier.DECISION_TREE)

    def test_predict(self):
        # Load data set.
        X = RANDOM_CLASSIFICATION_TEST_CASE["X"]
        y = RANDOM_CLASSIFICATION_TEST_CASE["y"]

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y)

        # Train logistic regression model.
        classifier = SupervisedClassifier([0, 1])
        classifier.train(X_train, y_train)

        # Test prediction values.
        y_predicted = classifier.predict(X_test)
        accuracy = classifier.compute_accuracy(X_test, y_test)
        self.assertTrue(accuracy > 0.5)

    def test_regress_and_round(self):
        # Load data set.
        X = RANDOM_CLASSIFICATION_TEST_CASE["X"]
        y = RANDOM_CLASSIFICATION_TEST_CASE["y"]

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y)

        # Train logistic regression model.
        decimalCoeffs = SupervisedClassifier([0, 1], algorithm=SupervisedClassifier.LOGISTIC_REGRESSION)
        decimalCoeffs.train(X_train, y_train)

        integerCoeffs = SupervisedClassifier([0, 1], algorithm=SupervisedClassifier.REGRESS_AND_ROUND)
        integerCoeffs.train(X_train, y_train)

        # Test coefficients.
        # TODO(sbala): Replace inline expectedCoefs with imported coefs from
        # SupervisedClassifierTestData. For some reason, the dictionary
        # instantation fails to include that data...
        # expectedCoefs = RANDOM_CLASSIFICATION_TEST_CASE["rounded_coefs"]
        beta_max = max([abs(c) for c in decimalCoeffs.coefs()])
        expectedCoefs = [round((3.0 * c) / beta_max) for c in decimalCoeffs.coefs()]
        actualCoefs = integerCoeffs.coefs()
        self.assertEqualList(expectedCoefs, actualCoefs)

        # Test performance.
        decimalAccuracy = decimalCoeffs.compute_accuracy(X_test, y_test)
        integerAccuracy = integerCoeffs.compute_accuracy(X_test, y_test)
        diff = abs(decimalAccuracy - integerAccuracy)
        self.assertTrue(diff < 0.05)

def suite():
    """
    Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test".
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSupervisedClassifier))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite())
