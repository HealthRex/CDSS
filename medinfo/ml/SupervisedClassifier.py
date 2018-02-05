#!/usr/bin/python
"""
Generic module for supervised machine learning classification.
"""

from sklearn.linear_model import LogisticRegressionCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, make_scorer

class SupervisedClassifier:
    # Define string constants for all supported ML algorithms so that
    # clients can define which algorithm to call.
    DECISION_TREE = 'decision-tree'
    LOGISTIC_REGRESSION = 'l1-logistic-regression-cross-validation'
    RANDOM_FOREST = 'random-forest'
    REGRESS_AND_ROUND = 'regress-and-round'

    SUPPORTED_ALGORITHMS = [DECISION_TREE, LOGISTIC_REGRESSION, RANDOM_FOREST, \
        REGRESS_AND_ROUND]

    def __init__(self, classes, algorithm=None):
        if algorithm is None:
            self._algorithm = SupervisedClassifier.LOGISTIC_REGRESSION
        elif algorithm not in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        else:
            self._algorithm = algorithm
        self._classes = classes

    def __repr__(self):
        if self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            coefs = self.coefs()
            cols = self._features
            sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
            linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
            return 'L1_REGRESSION(%s)' % linear_model
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            coefs = self.coefs()
            cols = self._features
            sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
            linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
            return 'L1_REGRESS_AND_ROUND(%s)' % linear_model
        else:
            return 'SupervisedClassifier(%s, %s)' % (self._classes, self._algorithm)

    __str__ = __repr__

    def algorithm(self):
        return self._algorithm

    def classes(self):
        return self._classes

    def coefs(self):
        return self._model.coef_[0]

    def train(self, X, y, coef_max=None):
        self._features = X.columns
        if self._algorithm == SupervisedClassifier.DECISION_TREE:
            self._train_decision_tree(X, y)
        elif self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            self._train_logistic_regression(X, y)
        elif self._algorithm == SupervisedClassifier.RANDOM_FOREST:
            self._train_random_forest(X, y)
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            self._train_regress_and_round(X, y, coef_max=coef_max)

    def _train_decision_tree(self, X, y):
        self._model = DecisionTreeClassifier()
        self._model.fit(X, y)

    def _train_logistic_regression(self, X, y):
        # Note: SAGA is only guaranteed to converge quickly if the various
        # dimensions are normalized, which will generally not be the case.
        # score -- by default, LogisticRegressionCV uses accuracy. However,
        # many medinfo learning applications will be unbalanced classification
        # problems, so use roc_auc_score instead.
        # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
        scorer = make_scorer(roc_auc_score, needs_threshold=True)
        self._model = LogisticRegressionCV(penalty='l1', solver='saga', \
            max_iter=10000, scoring=scorer)
        self._model.fit(X, y)

    def _train_random_forest(self, X, y):
        self._model = RandomForestClassifier()
        self._model.fit(X, y)

    def _train_regress_and_round(self, X, y, coef_max=None):
        self._train_logistic_regression(X, y)

        if coef_max is None:
            # This is the optimal M value from Jung et al.
            # The choice here is completely arbitrary, but we need something.
            # https://arxiv.org/abs/1702.04690
            coef_max = 3

        # Based on Jung et al. https://arxiv.org/abs/1702.04690
        # w_j = round((M * beta_j) / (max_i|beta_i|))
        # coef_max = M = max rounded coefficient value
        # beta_max = max_i|beta_i| = largest unrounded regression coefficient
        beta_max = max([abs(c) for c in self._model.coef_[0]])
        self._model.coef_[0] = [round((coef_max * c) / (beta_max)) for c in self._model.coef_[0]]

    def predict(self, X):
        return self._model.predict(X)

    def predict_probability(self, X):
        return self._model.predict_proba(X)

    def compute_accuracy(self, X, y):
        return self._model.score(X, y)

    def compute_roc_auc(self, X, y):
        y_predicted = self.predict_probability(X)
        return roc_auc_score(y, y_predicted[:,1])
