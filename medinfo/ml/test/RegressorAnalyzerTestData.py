#!/usr/bin/python
"""
Test input and output for regressor analysis.
"""

import pandas as pd
from numpy import array

# x, y, coef = sklearn.datasets.make_regression(n_samples=10, n_features=2)
RANDOM_REGRESSION_TEST_CASE = {
    'X': pd.DataFrame({
        'x1': [0.0506969, -1.67110936, 0.36348042, 1.9794256, -2.3583237,
            -1.51876327, 0.61071492, -0.92222904, -0.7306277, -0.25001944],
        'x2': [0.01719597, 0.1764346, 1.54603964, -0.09592507, 0.68128352,
            0.39048658, 0.3859871, -2.77311639, -0.8455577, 1.3107445]
    }),
    'y_true': pd.DataFrame({
        'true': [   4.72776063, -141.67945344,   61.00264029,  169.97305673,
           -191.70661982, -124.37875255,   60.35967648, -132.87637078,
            -79.52298865,    3.2722214 ]
    }),
    'y_predicted': pd.DataFrame({
        'predicted': [4.686657, -140.363148, 60.634069, 168.408025,
            -189.871451, -123.194396, 59.855238, -132.000909, -78.899579, 3.402474]
    }),
    'coef': [86.79316541, 19.05192056],
    'coef_predicted': [86, 19],
    'accuracy': 0,
    'r2': 0.9999114854982919,
    'median_absolute_error': 0.74943603999999908,
    'mean_absolute_error': 0.8444099799999979,
    'explained_variance': 0.99992171249797723,
    'report': pd.DataFrame({
        'model': ['LinearPredictor([86, 19])'],
        'test_size': [10],
        'accuracy': [0],
        'explained_variance': [0.99992171249797723],
        'mean_absolute_error': [0.8444099799999979],
        'median_absolute_error': [0.74943603999999908],
        'r2': [0.9999114854982919],
    })
}
