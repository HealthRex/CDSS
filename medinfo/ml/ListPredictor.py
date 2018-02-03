#!/usr/bin/python
"""
Fake predictor meant purely for testing. It accepts a list of predictions
and just cycles through those predictions.
"""

from pandas import DataFrame
from numpy import array

from medinfo.ml.Predictor import Predictor

class ListPredictor(Predictor):
    def __init__(self, predictions):
        self._index = 0
        self._predictions = predictions
        self._num_predictions = len(self._predictions)

    def __repr__(self):
        return 'ListPredictor(%s)' % self._predictions.values

    __str__ = __repr__

    def predict(self, X):
        y_predicted = list()
        for row in X.iterrows():
            prediction = self._predictions[self._index]
            y_predicted.append(prediction)
            self._index = (self._index + 1) % self._num_predictions

        return DataFrame({'y_predicted': y_predicted})

    def predict_probability(self, X):
        return array([[0.5, 0.5]]*X.shape[0])
