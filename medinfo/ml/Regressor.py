#!/usr/bin/python
"""
Generic class for linear and logistic regression.
"""

from numpy import array
from sklearn.linear_model import LassoCV
from sklearn.linear_model import LinearRegression

class Regressor:
    # Define string constants for all supported ML algorithms so that
    # clients can define which algorithm to call.
    # Rather than defining custom strings, model these off of meaningful
    # nomenclature in scikit-learn or whatever ML utility is being used
    # to drive the implementation.
    LASSO = 'lasso-regression'
    LINEAR_REGRESSION = 'linear-regression'
    REGRESS_AND_ROUND = 'regress-and-round'

    SUPPORTED_ALGORITHMS = [LASSO, LINEAR_REGRESSION, REGRESS_AND_ROUND]

    def __init__(self, algorithm=None):
        if algorithm is None:
            self._algorithm = Regressor.LASSO
        elif algorithm not in Regressor.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        else:
            self._algorithm = algorithm

    def algorithm(self):
        return self._algorithm

    def coefs(self):
        return self._model.coef_

    def train(self, X, y):
        if self._algorithm == Regressor.LASSO:
            self._train_lasso(X, y)
        elif self._algorithm == Regressor.LINEAR_REGRESSION:
            self._train_linear_regression(X, y)
        elif self._algorithm == Regressor.REGRESS_AND_ROUND:
            self._train_regress_and_round(X, y)

    def _train_lasso(self, X, y):
        self._model = LassoCV()
        self._model.fit(X, y)

    def _train_linear_regression(self, X, y):
        self._model = LinearRegression()
        self._model.fit(X, y)

    def _train_regress_and_round(self, X, y):
        self._train_lasso(X, y)
        self._model.coef_ = array([round(c) for c in self._model.coef_])

    def predict(self, X):
        return self._model.predict(X)

    def accuracy(self, X, y):
        return self._model.score(X, y)
