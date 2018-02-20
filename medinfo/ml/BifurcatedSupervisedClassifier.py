#!/usr/bin/python
"""
Ensemble supervised classifier which uses a binary condition on a specific
feature to determine which of two classifiers it should use.
"""

import pandas as pd
from pandas import DataFrame

from medinfo.common.Util import log
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

class BifurcatedSupervisedClassifier:
    EQUAL = '=='
    LTE = '<='
    GTE = '>='
    SUPPORTED_BIFURCATION_STRATEGIES = [EQUAL, GTE, LTE]
    def __init__(self, classes, hyperparams):
        if hyperparams['bifurcation_strategy'] not in BifurcatedSupervisedClassifier.SUPPORTED_BIFURCATION_STRATEGIES:
            raise ValueError('Bifurcation strategy %s not supported.' % hyperparams['bifurcation_strategy'])

        self._classes = classes
        self._hyperparams = hyperparams

        self._sc_true = SupervisedClassifier(classes, hyperparams)
        self._sc_false = SupervisedClassifier(classes, hyperparams)

    def __repr__(self):
        bs = self._build_bifurcation_str()
        classes_str = str(self._classes)
        hyperparams_str = "hyperparams={'algorithm': %s, 'bifurcator': %s, 'bifurcation_strategy': %s, 'bifurcation_threshold': %s, 'random_state': %s}" % (self._hyperparams['algorithm'],
                                self._hyperparams['bifurcator'],
                                self._hyperparams['bifurcation_strategy'],
                                self._hyperparams['bifurcation_value'],
                                self._hyperparams['random_state'])
        s = "BifurcatedSupervisedClassifier(%s, %s)" % (classes_str, hyperparams_str)
        return s

    __str__ = __repr__

    def _build_bifurcation_str(self):
        args = (
                self._hyperparams['bifurcator'],
                self._hyperparams['bifurcation_strategy'],
                self._hyperparams['bifurcation_value']
                )
        return '%s %s %s' % args

    def fetch_bifurcation_masks(self, X):
        if self._hyperparams['bifurcation_strategy'] is BifurcatedSupervisedClassifier.EQUAL:
            true_mask = X[self._hyperparams['bifurcator']] == self._hyperparams['bifurcation_value']
            false_mask = X[self._hyperparams['bifurcator']] != self._hyperparams['bifurcation_value']
        elif self._hyperparams['bifurcation_strategy'] is BifurcatedSupervisedClassifier.LTE:
            true_mask = X[self._hyperparams['bifurcator']] <= self._hyperparams['bifurcation_value']
            false_mask = X[self._hyperparams['bifurcator']] > self._hyperparams['bifurcation_value']
        elif self._hyperparams['bifurcation_strategy'] is BifurcatedSupervisedClassifier.GTE:
            true_mask = X[self._hyperparams['bifurcator']] >= self._hyperparams['bifurcation_value']
            false_mask = X[self._hyperparams['bifurcator']] < self._hyperparams['bifurcation_value']

        log.debug('true_mask: %s' % true_mask)
        return true_mask, false_mask

    def description(self):
        args = (
                self._build_bifurcation_str(),
                self._sc_true.description(),
                self._sc_false.description()
                )
        return 'BifurcatedSupervisedClassifier(%s, true=%s, false=%s)' % args

    def hyperparams(self):
        hyperparams = {
            'model_true': self._sc_true.hyperparams(),
            'model_false': self._sc_false.hyperparams()
        }
        return hyperparams

    def params(self):
        params = {
            'bifurcator': self._hyperparams['bifurcator'],
            'bifurcation_strategy': self._hyperparams['bifurcation_strategy'],
            'bifurcation_value': self._hyperparams['bifurcation_value'],
            'model_true': self._sc_true.description(),
            'model_false': self._sc_false.description()
        }
        return params

    def train(self, X_train, y_train):
        true_mask, false_mask = self.fetch_bifurcation_masks(X_train)

        # Train sc_true.
        X_train_true = X_train[true_mask]
        y_train_true = y_train[true_mask]
        self._sc_true.train(X_train_true, y_train_true)

        # Train sc_true.
        X_train_false = X_train[false_mask]
        y_train_false = y_train[false_mask]
        self._sc_false.train(X_train_false, y_train_false)

    def _stitch_disjoint_row(self, row):
        if pd.isnull(row['y_pred_true']):
            val = row['y_pred_false']
        else:
            val = row['y_pred_true']
        return val

    def _predict_label_or_probability(self, X_test, probability=None):
        true_mask, false_mask = self.fetch_bifurcation_masks(X_test)

        # Predict X_test_true.
        X_test_true = X_test[true_mask]
        if probability:
            y_pred_true = self._sc_true.predict_probability(X_test_true)
        else:
            y_pred_true = self._sc_true.predict(X_test_true)
        log.debug('y_pred_true: %s' % y_pred_true)

        # Predict X_test_false.
        X_test_false = X_test[false_mask]
        if probability:
            y_pred_false = self._sc_false.predict_probability(X_test_false)
        else:
            y_pred_false = self._sc_false.predict(X_test_false)
        log.debug('y_pred_false: %s' % y_pred_false)

        # Stitch results.
        y_pred_true_df = DataFrame(y_pred_true, index=X_test_true.index, \
                                    columns=['y_pred_true'])
        log.debug('y_pred_true_df: %s' % y_pred_true_df)
        y_pred_false_df = DataFrame(y_pred_false, index=X_test_false.index, \
                                    columns=['y_pred_false'])
        log.debug('y_pred_false_df: %s' % y_pred_false_df)
        true_mask_df = DataFrame(true_mask)
        mask_plus_true = true_mask_df.merge(y_pred_true_df, how='left', \
                                            left_index=True, right_index=True)
        mask_plus_true_plus_false = mask_plus_true.merge(y_pred_false_df, \
                                how='left', left_index=True, right_index=True)
        mask_plus_true_plus_false['y_pred'] = mask_plus_true_plus_false.apply(self._stitch_disjoint_row, axis=1)
        log.debug('mask_plus_false: %s' % mask_plus_true_plus_false)
        y_pred = mask_plus_true_plus_false['y_pred'].values

        return y_pred

    def predict(self, X_test):
        return self._predict_label_or_probability(X_test)

    def predict_probability(self, X_test):
        return self._predict_label_or_probability(X_test, probability=True)
