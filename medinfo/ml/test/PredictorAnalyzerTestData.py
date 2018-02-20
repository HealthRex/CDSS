#!/usr/bin/python
"""
Test input and output for predictor analysis.
"""

from numpy import array
import pandas as pd

MANUAL_PREDICTION_TEST_CASE = {
    'X': pd.DataFrame({
        'x1': [0.05, -1.67, 0.36, 1.97, -2.35, -1.51, 0.61, -0.92, -0.73, -0.25],
        'x2': [0.01, 0.17, 1.54, -0.09, 0.68, 0.39, 0.38, -2.77, -0.84, 1.31]
        }),
    'y_true': pd.DataFrame({'true':[1, 2, 3, 5, 8, 13, 21, 34, 55, 89]}),
    'y_predicted': pd.DataFrame({'predictions':[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}),
    'accuracy': 0.3,
    'report' : pd.DataFrame({
        'model': ['ListPredictor([ 1  2  3  4  5  6  7  8  9 10])'],
        'test_size': [10],
        'accuracy': [0.3]
    })
}
