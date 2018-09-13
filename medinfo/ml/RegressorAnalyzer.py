#!/usr/bin/python
"""
Class for analyzing the performance of a pre-trained Regressor.
"""

from pandas import DataFrame

from medinfo.ml.PredictorAnalyzer import PredictorAnalyzer
from sklearn.metrics import explained_variance_score, r2_score, mean_absolute_error, median_absolute_error

class RegressorAnalyzer(PredictorAnalyzer):
    ACCURACY_SCORE = 'accuracy'
    R2_SCORE = 'r2'
    MEDIAN_ABSOLUTE_ERROR_SCORE = 'median_absolute_error'
    MEAN_ABSOLUTE_ERROR_SCORE = 'mean_absolute_error'
    EXPLAINED_VARIANCE_SCORE = 'explained_variance'
    SUPPORTED_SCORES = [
        ACCURACY_SCORE, EXPLAINED_VARIANCE_SCORE, MEAN_ABSOLUTE_ERROR_SCORE,
        MEDIAN_ABSOLUTE_ERROR_SCORE, R2_SCORE
    ]

    def __init__(self, regressor, X_test, y_test):
        PredictorAnalyzer.__init__(self, regressor, X_test, y_test)

    def _score_accuracy(self):
        equality_df = (self._y_predicted[0] == self._y_test['true'])
        # If all false...return 0
        if 'True' not in equality_df.value_counts():
            return 0
        # if all true...return 1
        elif 'False' not in equality_df.value_counts():
            return 1.0
        else:
            equal_count = equality_df.value_counts()[True]
            unequal_count = equality_df.value_counts()[False]
            return (equal_count/(equal_count + unequal_count))

    def _score_r2(self):
        return r2_score(self._y_test, self._y_predicted)

    def _score_median_absolute_error(self):
        return median_absolute_error(self._y_test, self._y_predicted)

    def _score_mean_absolute_error(self):
        return mean_absolute_error(self._y_test, self._y_predicted)

    def _score_explained_variance(self):
        return explained_variance_score(self._y_test, self._y_predicted)

    def score(self, metric=None):
        if metric is None:
            metric = RegressorAnalyzer.MEAN_ABSOLUTE_ERROR_SCORE

        if metric not in RegressorAnalyzer.SUPPORTED_SCORES:
            raise ValueError('Score metric %s not supported.' % metric)

        if metric == RegressorAnalyzer.ACCURACY_SCORE:
            return self._score_accuracy()
        elif metric == RegressorAnalyzer.R2_SCORE:
            return self._score_r2()
        elif metric == RegressorAnalyzer.MEDIAN_ABSOLUTE_ERROR_SCORE:
            return self._score_median_absolute_error()
        elif metric == RegressorAnalyzer.MEAN_ABSOLUTE_ERROR_SCORE:
            return self._score_mean_absolute_error()
        elif metric == RegressorAnalyzer.EXPLAINED_VARIANCE_SCORE:
            return self._score_explained_variance()

    def build_report(self):
        # Report the following summary statistics:
        # * test size
        # * accuracy
        report_dict = {
            'model': [repr(self._predictor)],
            'test_size': [self._y_test.shape[0]]
        }
        for score_metric in RegressorAnalyzer.SUPPORTED_SCORES:
            score_value = self.score(metric=score_metric)
            report_dict.update({score_metric: score_value})

        return DataFrame(report_dict)

    def write_report(self, dest_path):
        column_names = ['model', 'test_size']
        column_names.extend(RegressorAnalyzer.SUPPORTED_SCORES)
        report = self.build_report()

        PredictorAnalyzer.write_report(self, report, dest_path, column_names)
