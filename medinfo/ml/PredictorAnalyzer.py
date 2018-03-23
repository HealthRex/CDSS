#!/usr/bin/python
"""
Abstract class for analyzing the performance of a pre-trained predictor
on a set of test data.
"""

import pandas as pd
from sklearn.utils.validation import column_or_1d
from sklearn.metrics import accuracy_score

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

    def _score_accuracy(self, ci=None):
        return accuracy_score(self._y_test, self._y_predicted)

    def score(self, metric=None, ci=None):
        # ci defines confidence interval as float.
        # Also defines whether score returns score or (-ci, score, +ci)
        if metric is None:
            metric = PredictorAnalyzer.ACCURACY_SCORE

        if metric == PredictorAnalyzer.ACCURACY_SCORE:
            return self._score_accuracy()
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
