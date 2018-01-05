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
    # Rather than defining custom strings, model these off of meaningful
    # nomenclature in scikit-learn or whatever ML utility is being used
    # to drive the implementation.
    DECISION_TREE = DecisionTreeClassifier
    LOGISTIC_REGRESSION = LogisticRegressionCV
    RANDOM_FOREST = RandomForestClassifier

    SUPPORTED_ALGORITHMS = [DECISION_TREE, LOGISTIC_REGRESSION]

    def __init__(self, algorithm=None):
        if algorithm is None:
            self._algorithm = SupervisedClassifier.LOGISTIC_REGRESSION
        elif algorithm not in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        else:
            self._algorithm = algorithm

    def algorithm(self):
        return self._algorithm

    def train(self, X, y):
        if self._algorithm == SupervisedClassifier.DECISION_TREE:
            self._train_decision_tree(X, y)
        elif self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            self._train_logistic_regression(X, y)

    def _train_decision_tree(self, X, y):
        self._model = DecisionTreeClassifier()
        self._model.fit(X, y)

    def _train_logistic_regression(self, X, y):
        self._model = LogisticRegressionCV(penalty='l1', solver='saga')
        self._model.fit(X, y)

    def _train_random_forest(self, X, y):
        self._model = RandomForestClassifier()
        self._model.fit(X, y)

    def predict(self, X):
        return self._model.predict(X)

    def accuracy(self, X, y):
        return self._model.score(X, y)
