#!/usr/bin/python

import logging
from pandas import DataFrame
from sklearn.model_selection import train_test_split
import sys
import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import MedInfoTestCase, make_test_suite
from medinfo.common.Util import log
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.ml.BifurcatedSupervisedClassifier import BifurcatedSupervisedClassifier
from numpy import array
from SupervisedLearningTestData import RANDOM_CLASSIFICATION_TEST_CASE

class TestBifurcatedSupervisedClassifier(MedInfoTestCase):
    def setUp(self):
        log.level = logging.INFO

    def tearDown(self):
        pass

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
        X = DataFrame(RANDOM_CLASSIFICATION_TEST_CASE['X'], \
                        columns = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', \
                                    'x8', 'x9', 'x10'])
        y = DataFrame(RANDOM_CLASSIFICATION_TEST_CASE['y'])
        random_state = RANDOM_CLASSIFICATION_TEST_CASE['random_state']
        expected_y_pred_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['y_predicted']
        expected_str_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['str']
        expected_hyperparams_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['hyperparams']
        expected_params_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['params']
        expected_descriptions_by_algorithm = RANDOM_CLASSIFICATION_TEST_CASE['description']

        # Generate train/test split.
        X_train, X_test, y_train, y_test = train_test_split(X, y, \
                                            random_state=random_state)

        # Initialize classifier.
        hyperparams = {}
        hyperparams['bifurcator'] = 'x3'
        hyperparams['bifurcation_strategy'] = BifurcatedSupervisedClassifier.LTE
        hyperparams['bifurcation_value'] = 0.5
        hyperparams['random_state'] = 123456789
        hyperparams['algorithm'] = SupervisedClassifier.REGRESS_AND_ROUND

        # Use algorithm as key for test results.
        algorithm = 'bifurcated'
        self._bsc = BifurcatedSupervisedClassifier([0, 1], hyperparams)

        # Train.
        self._bsc.train(X_train, y_train)

        # Test hyperparams.
        expected_hyperparams = expected_hyperparams_by_algorithm[algorithm]
        actual_hyperparams = self._bsc.hyperparams()
        self._assert_equal_hyperparams(expected_hyperparams['model_true'], actual_hyperparams['model_true'])
        self._assert_equal_hyperparams(expected_hyperparams['model_false'], actual_hyperparams['model_false'])

        # Test params.
        expected_params = expected_params_by_algorithm[algorithm]
        actual_params = self._bsc.params()
        self.assertEqual(expected_params, actual_params)

        # Test str.
        expected_str = expected_str_by_algorithm[algorithm]
        actual_str = str(self._bsc)
        self.assertEqual(expected_str, actual_str)

        # Test description.
        expected_description = expected_descriptions_by_algorithm[algorithm]
        actual_description = self._bsc.description()
        self.assertEqual(expected_description, actual_description)

        # Test predictions.
        expected_y_pred = expected_y_pred_by_algorithm[algorithm]
        actual_y_pred = self._bsc.predict(X_test)
        self.assertEqualList(expected_y_pred, actual_y_pred)

if __name__ == '__main__':
    suite = make_test_suite(TestBifurcatedSupervisedClassifier)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
