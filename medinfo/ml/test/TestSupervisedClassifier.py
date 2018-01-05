#!/usr/bin/python

import unittest
from sklearn.model_selection import train_test_split

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

from SupervisedClassifierTestData import RANDOM_CLASSIFICATION_TEST_CASE

class TestSupervisedClassifier(MedInfoTestCase):
    def test_init(self):
        # Test unspecified algorithm.
        classifier = SupervisedClassifier()
        self.assertEqual(classifier.algorithm(), \
            SupervisedClassifier.LOGISTIC_REGRESSION)

        # Test unsupported algorithm.
        with self.assertRaises(ValueError):
            SupervisedClassifier(algorithm="foo")

        # Confirm specified algorithm selection.
        classifier = SupervisedClassifier(algorithm=SupervisedClassifier.DECISION_TREE)
        self.assertEqual(classifier.algorithm(), SupervisedClassifier.DECISION_TREE)

    def test_predict(self):
        # Load data set.
        X = RANDOM_CLASSIFICATION_TEST_CASE["X"]
        y = RANDOM_CLASSIFICATION_TEST_CASE["y"]

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y)

        # Train logistic regression model.
        classifier = SupervisedClassifier()
        classifier.train(X_train, y_train)

        # Test prediction values.
        y_predicted = classifier.predict(X_test)
        accuracy = classifier.accuracy(X_test, y_test)
        self.assertTrue(accuracy > 0.5)

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
