#!/usr/bin/python

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LassoCV
from sklearn.feature_selection import f_classif, f_regression, RFE, RFECV, SelectKBest, SelectPercentile

from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform

class FeatureSelector:
    SELECT_K_BEST = 'select_K_best'
    SELECT_PERCENTILE = 'select_percentile'
    REMOVE_HIGH_VARIANCE = 'remove_high_variance'
    RECURSIVE_ELIMINATION = 'eliminate_recursively'
    SUPPORTED_ALGORITHMS = [SELECT_K_BEST, SELECT_PERCENTILE, RECURSIVE_ELIMINATION]

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

    def select(self, k=None, percentile=None):
        if self._algorithm == FeatureSelector.SELECT_K_BEST:
            if k is None:
                raise ValueError('Must specify value for k.')
            self._select_K_best(k)
        elif self._algorithm == FeatureSelector.SELECT_PERCENTILE:
            if percentile is None:
                raise ValueError('Must specify value for percentile.')
            self._select_percentile(percentile)
        elif self._algorithm == FeatureSelector.RECURSIVE_ELIMINATION:
            self._eliminate_recursively(k)

        self._selector.fit(self._input_X, self._input_y)

    def compute_ranks(self):
        if self._algorithm == FeatureSelector.SELECT_K_BEST:
            scores = self._selector.scores_
            sorted_scores = sorted(scores, reverse=True)
            ranks = [sorted_scores.index(i) + 1 for i in scores]
        elif self._algorithm == FeatureSelector.SELECT_PERCENTILE:
            scores = self._selector.scores_
            sorted_scores = sorted(scores, reverse=True)
            ranks = [sorted_scores.index(i) + 1 for i in scores]
        elif self._algorithm == FeatureSelector.RECURSIVE_ELIMINATION:
            n_selected = self._selector.n_features_
            support = self._selector.support_
            ranking = self._selector.ranking_
            # RFE and RFECV do not provide feature scores. Instead, they
            # provide a list of features which have been selected (support)
            # and an ascending list indicating when each other feature was
            # eliminated. Use these two to construct feature ranks, though
            # acknowledge that RFE and RFECV do not actually distinguish between
            # the weights of selected features.
            ranks = [0]*len(support)
            selected_count = 0
            for i in range(len(ranking)):
                if support[i]:
                    # All selected features in ranking receive rank 1, so need
                    # to iterate through list and add incrementing values so
                    # that features ranked 1, 1, 1, become 1, 2, 3.
                    ranks[i] = ranking[i] + selected_count
                    selected_count += 1
                else:
                    # Even if there are 5 selected features, the 6th feature
                    # in ranking is given rank 2, so add (n_selected - 1).
                    ranks[i] = ranking[i] + (n_selected - 1)

        return ranks

    def transform_matrix(self, X):
        if type(X) == pd.DataFrame:
            # Try to preserve labels.
            columns = X.columns
            old_index = X.index
            labels = [columns[x] for x in self._selector.get_support(indices=True)]
            return pd.DataFrame(self._selector.transform(X), columns=labels, index=old_index)
        else:
            return self._selector.transform(X)

    def _remove_high_variance(self):
        pass

    def _select_K_best(self, k):
        if self._problem == FeatureSelector.CLASSIFICATION:
            score = f_classif
        else:
            score = f_regression

        self._selector = SelectKBest(score, k)

    def _select_percentile(self, percentile):
        # Algorithm is conservative. Defaults to keeping features if
        # percentile specifies a value that corresponds to a floating number
        # of features. For example, if percentile=18 on a 20-feature matrix
        # implies keeping 3.6 features. In that case, keeps 4 features.
        if self._problem == FeatureSelector.CLASSIFICATION:
            score = f_classif
        else:
            score = f_regression

        self._selector = SelectPercentile(score, percentile)

    def _eliminate_recursively(self, k=None):
        if self._problem == FeatureSelector.CLASSIFICATION:
            estimator = RandomForestClassifier()
        else:
            estimator = LassoCV()
        # If k is not specified, then use RFECV to automatically decide on
        # optimal number of features. If specified, then use RFE.
        if k is None:
            self._selector = RFECV(estimator)
        else:
            self._selector = RFE(estimator, n_features_to_select=k)

    def _select_recursively(self):
        pass
