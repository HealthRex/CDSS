#!/usr/bin/python
"""
Generic class for linear and logistic regression.
"""

from sklearn.linear_model import LassoCV
from sklearn.linear_model import LinearRegression

class Regressor:
    # Define string constants for all supported ML algorithms so that
    # clients can define which algorithm to call.
    # Rather than defining custom strings, model these off of meaningful
    # nomenclature in scikit-learn or whatever ML utility is being used
    # to drive the implementation.
    LASSO = LassoCV
    LINEAR_REGRESSION = LinearRegression

    SUPPORTED_ALGORITHMS = [LASSO, LINEAR_REGRESSION]

    def __init__(self, algorithm=None):
        if algorithm is None:
            self._algorithm = Regressor.LASSO
        elif algorithm not in Regressor.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        else:
            self._algorithm = algorithm

    def algorithm(self):
        return self._algorithm

    def coef(self):
        return self._model.coef_

    def train(self, X, y):
        if self._algorithm == Regressor.LASSO:
            self._train_lasso(X, y)
        elif self._algorithm == Regressor.LINEAR_REGRESSION:
            self._train_linear_regression(X, y)

    def _train_lasso(self, X, y):
        self._model = LassoCV()
        self._model.fit(X, y)

    def _train_linear_regression(self, X, y):
        self._model = LinearRegression()
        self._model.fit(X, y)

    def predict(self, X):
        return self._model.predict(X)
