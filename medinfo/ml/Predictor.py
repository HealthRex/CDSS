#!/usr/bin/python
"""
Abstract class for predictor, which can predict outcomes, summarize its logic,
and be fed to a PredictorAnalyzer for analysis of its performance.

Predictor may be arbitrarily simple (always return 0) or complex (CNN).
The Predictor API is based on the common API provided by sklearn.
"""

import pandas as pd

class Predictor:
    def __repr__(self):
        return 'Predictor()'
        
    __str__ = __repr__

    def predict(self, X):
        y_predicted = list()
        for row in X.iterrows():
            y_predicted.append(True)

        return pd.DataFrame({'y_predicted': y_predicted})
