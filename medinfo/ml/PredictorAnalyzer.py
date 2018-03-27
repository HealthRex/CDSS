#!/usr/bin/python
"""
Abstract class for analyzing the performance of a pre-trained predictor
on a set of test data.
"""

import pandas as pd
from sklearn.utils.validation import column_or_1d
from sklearn.metrics import accuracy_score
import numpy as np

from medinfo.common.Util import log

class PredictorAnalyzer:
    ACCURACY_SCORE = 'accuracy'
    def __init__(self, predictor, X_test, y_test):
        self._predictor = predictor
        # In theory we could let the client pass X_test and y_test into each
        # individual scoring function, but that might encourage them to keep
        # testing constantly, turning the test cases into training cases.
        self._X_test = X_test
        self._y_test = y_test.reset_index(drop=True)
        log.debug('y_true[0].value_counts(): %s' % self._y_test[self._y_test.columns.values[0]].value_counts())
        # Cast to DataFrame to ease subsequent analysis, even though sklearn
        # by default just outputs an ndarray.
        self._y_predicted = pd.DataFrame(self._predictor.predict(self._X_test))
        log.debug('y_predicted[0].value_counts(): %s' % self._y_predicted[self._y_predicted.columns.values[0]].value_counts())

    def _score_accuracy(self, ci=None, n_bootstrap_iter=None):
        sample_accuracy = accuracy_score(self._y_test, self._y_predicted)
        log.debug('y_test: %s' % self._y_test)
        if ci:
            if n_bootstrap_iter is None:
                n_bootstrap_iter = 100
            # For consistency of results, seed random number generator with
            # fixed number.
            rng = np.random.RandomState(n_bootstrap_iter)
            # Use bootstrap to compute cis.
            bootstrap_scores = list()
            for i in range(0, n_bootstrap_iter):
                # Sample y_test and y_pred with replacement.
                indices = rng.randint(0, len(self._y_predicted) - 1, len(self._y_predicted))
                sample_y_test = np.array(self._y_test)[indices]
                sample_y_pred = np.array(self._y_predicted)[indices]
                log.debug('sample_y_pred: %s' % sample_y_pred)
                if len(np.unique(sample_y_test)) < 2:
                    # We need at least one positive and one negative sample for ROC AUC
                    # to be defined: reject the sample
                    continue
                score = accuracy_score(sample_y_test, sample_y_pred)
                bootstrap_scores.append(score)

            # Sort bootstrap scores to get CIs.
            bootstrap_scores.sort()
            sorted_scores = np.array(bootstrap_scores)
            # May not be equal to n_bootstrap_iter if some samples were rejected
            num_bootstraps = len(sorted_scores)
            log.debug('sorted_scores: %s' % sorted_scores)

            ci_lower_bound_float = (1.0 - ci) / 2
            ci_lower_bound = sorted_scores[int(ci_lower_bound_float * num_bootstraps)]
            ci_upper_bound_float = ci + ci_lower_bound_float
            ci_upper_bound = sorted_scores[int(ci_upper_bound_float * num_bootstraps)]

            return sample_accuracy, ci_lower_bound, ci_upper_bound
        else:
            return sample_accuracy

    def score(self, metric=None, ci=None, n_bootstrap_iter=None):
        # ci defines confidence interval as float.
        # Also defines whether score returns score or (-ci, score, +ci)
        if metric is None:
            metric = PredictorAnalyzer.ACCURACY_SCORE

        if metric == PredictorAnalyzer.ACCURACY_SCORE:
            return self._score_accuracy(ci, n_bootstrap_iter)
        else:
            raise ValueError('Score metric %s not supported.' % metric)

    def build_report(self):
        # Report the following summary statistics:
        # * test size
        # * accuracy
        accuracy = self._score_accuracy()
        test_size = self._y_test.shape[0]
        report = pd.DataFrame({
            'model': [repr(self._predictor)],
            'test_size': [test_size],
            'accuracy': [accuracy]
        })

        return report

    def write_report(self, report, dest_path, column_names=None):
        if column_names is None:
            column_names = ['model', 'test_size', 'accuracy']
        report.to_csv(dest_path, sep='\t', index=False, columns=column_names,
            float_format='%.5f')
