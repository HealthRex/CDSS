#!/usr/bin/python
"""
Abstract class for analyzing the performance of a pre-trained predictor
on a set of test data.
"""

import pandas as pd

class PredictorAnalyzer:
    ACCURACY_SCORE = 'accuracy'
    def __init__(self, predictor, X_test, y_test):
        self._predictor = predictor
        # In theory we could let the client pass X_test and y_test into each
        # individual scoring function, but that might encourage them to keep
        # testing constantly, turning the test cases into training cases.
        self._X_test = X_test
        self._y_test = y_test
        self._y_predicted = self._predictor.predict(self._X_test)

    def _score_accuracy(self):
        # sklearn has a built-in function to compute this. However,
        # to avoid requiring all non-sklearn-based predictors to implement
        # all of their own scoring functions, we'll take the unusual step
        # of re-implementing here, given the computation is fairly simple.
        true_vals = self._y_test.iloc[:,0]
        predicted_vals = self._y_predicted.iloc[:,0]
        # Create new series comparing first column of each DataFrame.
        accuracy = (true_vals == predicted_vals)

        return accuracy.value_counts(normalize=True)[True]

    def score(self, metric=None):
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

    def write_report(self, dest_path):
        report = self.build_report()
        report.to_csv(dest_path, sep='\t', index=False, \
            columns=['model', 'test_size', 'accuracy'])
