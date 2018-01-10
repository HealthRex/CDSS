#!/usr/bin/python

from sklearn.feature_selection import f_classif, f_regression, SelectKBest

from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform

class FeatureSelector:
    SELECT_K_BEST = 'select_K_best'
    REMOVE_HIGH_VARIANCE = 'remove_high_variance'
    SUPPORTED_ALGORITHMS = [SELECT_K_BEST]

    REGRESSION = 'regression'
    CLASSIFICATION = 'classification'
    SUPPORTED_PROBLEMS = [REGRESSION, CLASSIFICATION]

    def __init__(self, algorithm=None, problem=None):
        # Specify feature selection algorithm.
        if algorithm is None:
            algorithm = FeatureSelector.REMOVE_HIGH_VARIANCE
        elif algorithm not in FeatureSelector.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        self._algorithm = algorithm

        # Specify regression vs. classification problem.
        if problem is None:
            problem = 'classification'
        elif problem not in FeatureSelector.SUPPORTED_PROBLEMS:
            raise ValueError('Problem %s not supported.' % problem)
        self._problem = problem

        # Use a FeatureMatrixTransform for actually generating output matrix.
        self._fmt = FeatureMatrixTransform()
        self._selector = None

        pass

    def set_input_matrix(self, X, y):
        self._input_X = X
        self._input_y = y
        pass

    def select(self, k=None):
        if self._algorithm == FeatureSelector.SELECT_K_BEST:
            if k is None:
                raise ValueError('Must specify value for k.')
            self._select_K_best(k)

        self._selector.fit(self._input_X, self._input_y)

    def compute_ranks(self):
        if self._algorithm == FeatureSelector.SELECT_K_BEST:
            scores = self._selector.scores_
            sorted_scores = sorted(scores, reverse=True)
            ranks = [sorted_scores.index(i) + 1 for i in scores]

        return ranks

    def transform_matrix(self):
        pass

    def _remove_high_variance(self):
        pass

    def _select_K_best(self, k):
        if self._problem == FeatureSelector.CLASSIFICATION:
            score = f_classif
        else:
            score = f_regression

        self._selector = SelectKBest(score, k)

    def _select_percentile(self):
        pass

    def _eliminate_recursively(self):
        pass

    def _select_recursively(self):
        pass
