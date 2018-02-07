#!/usr/bin/python

import unittest
from pandas import DataFrame
from sklearn.model_selection import train_test_split

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from numpy import array

from SupervisedLearningTestData import RANDOM_CLASSIFICATION_TEST_CASE

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

    def _assert_equal_hyperparams(self, expected_hyperparams, actual_hyperparams):
        for key in expected_hyperparams.keys():
            expected = expected_hyperparams[key]
            actual = actual_hyperparams[key]
            if key == 'cv':
                # StratifiedKFold objects with identical arguments do not
                # compute as equal.
                self.assertEqual(expected.n_splits, actual.n_splits)
                self.assertEqual(expected.random_state, actual.random_state)
                self.assertEqual(expected.shuffle, actual.shuffle)
            elif key == 'scoring':
                # _ThresholdScorer objects with identical arguments do not
                # compute as equal.
                self.assertEqual(type(expected), type(actual))
            else:
                self.assertEqual(expected, actual)

    def test_train_and_predict(self):
        # Load data set.
        X = DataFrame(RANDOM_CLASSIFICATION_TEST_CASE['X'], columns = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10'])
        y = DataFrame(RANDOM_CLASSIFICATION_TEST_CASE['y'])
        random_state = RANDOM_CLASSIFICATION_TEST_CASE['random_state']
        expected_y_pred_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['y_predicted']
        expected_hyperparams_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['hyperparams']
        expected_params_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['params']

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y, \
                                            random_state=random_state)

        # Iterate through SUPPORTED_ALGORITHMS.
        for algorithm in [SupervisedClassifier.LOGISTIC_REGRESSION]:
            # Train model.
            classifier = SupervisedClassifier([0, 1], algorithm=algorithm, \
                                                random_state=random_state)
            classifier.train(X_train, y_train)

            # Test hyperparameters.
            expected_hyperparams = expected_hyperparams_by_algorithm[algorithm]
            actual_hyperparams = classifier.hyperparams()
            self._assert_equal_hyperparams(expected_hyperparams, actual_hyperparams)

            # Test model parameters.
            expected_params = expected_params_by_algorithm[algorithm]
            actual_params = classifier.params()
            self.assertEqualDict(expected_params, actual_params)

            # Test prediction values.
            expected_y_pred = expected_y_pred_by_algorithm[algorithm]
            actual_y_pred = classifier.predict(X_test)
            self.assertEqualList(expected_y_pred, actual_y_pred)

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
