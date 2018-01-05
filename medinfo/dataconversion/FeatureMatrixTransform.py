#!/usr/bin/python
"""
Module for transforming the values within an existing feature matrix.
"""

import pandas as pd

from sklearn.preprocessing import Imputer

class FeatureMatrixTransform():
    IMPUTE_STRATEGY_MEAN = 'mean'
    IMPUTE_STRATEGY_MEDIAN = 'median'
    IMPUTE_STRATEGY_MODE = 'most-frequent'

    def __init__(self):
        self._matrix = None

        # Use sklearn and pandas to do most of the work.
        self._imputer = Imputer()


    def set_input_matrix(self, matrix):
        if type(matrix) != pd.core.frame.DataFrame:
            raise ValueError('Input matrix must be pandas DataFrame.')

        self._matrix = matrix

    def impute(self, feature=None, strategy=None):
        if self._matrix is None:
            raise ValueError('Must call set_input_matrix() before impute().')

        # If user does not specify which feature to impute, impute values
        # for all columns in the matrix.
        if feature is None:
            feature = 'all-features'

        # If an imputation strategy is not specified, default to mean.
        if strategy is None:
            strategy = FeatureMatrixTransform.IMPUTE_STRATEGY_MEAN

        self._impute_single_feature(feature=feature, strategy=strategy)

    def fetch_matrix(self):
        return self._matrix

    def _impute_single_feature(self, feature, strategy):
        if strategy == FeatureMatrixTransform.IMPUTE_STRATEGY_MEAN:
            self._matrix[feature] =  self._matrix[feature].fillna(self._matrix[feature].mean(0))

        pass
