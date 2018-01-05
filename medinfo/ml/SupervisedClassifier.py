#!/usr/bin/python
"""
Generic module for supervised machine learning classification.
"""

from sklearn.linear_model import LogisticRegressionCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

class SupervisedClassifier:
    # Define string constants for all supported ML algorithms so that
    # clients can define which algorithm to call.
    DECISION_TREE = 'decision-tree'
    LOGISTIC_REGRESSION = 'l1-logistic-regression-cross-validation'
    RANDOM_FOREST = 'random-forest'
    REGRESS_AND_ROUND = 'regress-and-round'

    SUPPORTED_ALGORITHMS = [DECISION_TREE, LOGISTIC_REGRESSION, RANDOM_FOREST, \
        REGRESS_AND_ROUND]

    def __init__(self, algorithm=None):
        if algorithm is None:
            self._algorithm = SupervisedClassifier.LOGISTIC_REGRESSION
        elif algorithm not in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        else:
            self._algorithm = algorithm

    def algorithm(self):
        return self._algorithm

    def coefs(self):
        return self._model.coef_[0]

    def train(self, X, y):
        if self._algorithm == SupervisedClassifier.DECISION_TREE:
            self._train_decision_tree(X, y)
        elif self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            self._train_logistic_regression(X, y)
        elif self._algorithm == SupervisedClassifier.RANDOM_FOREST:
            self._train_random_forest(X, y)
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            self._train_regress_and_round(X, y)

    def _train_decision_tree(self, X, y):
        self._model = DecisionTreeClassifier()
        self._model.fit(X, y)

    def _train_logistic_regression(self, X, y):
        self._model = LogisticRegressionCV(penalty='l1', solver='saga')
        self._model.fit(X, y)

    def _train_random_forest(self, X, y):
        self._model = RandomForestClassifier()
        self._model.fit(X, y)

    def _train_regress_and_round(self, X, y):
        self._train_logistic_regression(X, y)
        self._model.coef_[0] = [round(c) for c in self._model.coef_[0]]

    def predict(self, X):
        return self._model.predict(X)

    def accuracy(self, X, y):
        return self._model.score(X, y)
