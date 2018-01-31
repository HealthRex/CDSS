#!/usr/bin/python
"""
Test input and output for predictor analysis.
"""

from numpy import array
import pandas as pd

MANUAL_MULTILABEL_CLASSIFICATION_TEST_CASE = {
    'y': pd.DataFrame({
        'y_true': [],
        'y_predicted': [],
        'y_score': []
    })
}

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

# x, y, coef = sklearn.datasets.make_regression(n_samples=10, n_features=2)
RANDOM_REGRESSION_TEST_CASE = {
    'X': array([[ 0.0506969 ,  0.01719597],
       [-1.67110936,  0.1764346 ],
       [ 0.36348042,  1.54603964],
       [ 1.9794256 , -0.09592507],
       [-2.3583237 ,  0.68128352],
       [-1.51876327,  0.39048658],
       [ 0.61071492,  0.3859871 ],
       [-0.92222904, -2.77311639],
       [-0.7306277 , -0.8455577 ],
       [-0.25001944,  1.3107445 ]]),
    'y_true': array([   4.72776063, -141.67945344,   61.00264029,  169.97305673,
       -191.70661982, -124.37875255,   60.35967648, -132.87637078,
        -79.52298865,    3.2722214 ]),
    'y_predicted': array([4.72776063, -141, 61, 169.97305673,
        -191, -124, 60.35967648, -132,
        -79, 3.2722214]),
    'coef': array([ 86.79316541,  19.05192056])
}
