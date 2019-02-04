#!/usr/bin/python
"""
Module for transforming the values within an existing feature matrix.
"""

import numpy as np
import pandas as pd

from scipy.stats import norm
from sklearn.preprocessing import Imputer
from Util import log
from math import isnan

class FeatureMatrixTransform:
    IMPUTE_STRATEGY_MEAN = 'mean'
    IMPUTE_STRATEGY_MEDIAN = 'median'
    IMPUTE_STRATEGY_MODE = 'most-frequent'
    IMPUTE_STRATEGY_ZERO = 'zero'
    IMPUTE_STRATEGY_DISTRIBUTION = 'distribution'

    LOG_BASE_10 = 'log-base-10'
    LOG_BASE_E = 'log-base-e'

    ALL_FEATURES = 'all-features'

    def __init__(self):
        self._matrix = None

    def set_input_matrix(self, matrix):
        if type(matrix) != pd.core.frame.DataFrame:
            raise ValueError('Input matrix must be pandas DataFrame.')

        self._matrix = pd.DataFrame.copy(matrix)

    def fetch_matrix(self):
        return self._matrix

    def impute(self, feature=None, strategy=None, distribution=None):
        if self._matrix is None:
            raise ValueError('Must call set_input_matrix() before impute().')
        # If user does not specify which feature to impute, impute values
        # for all columns in the matrix.
        if feature is None:
            feature = FeatureMatrixTransform.ALL_FEATURES

        # If an imputation strategy is not specified, default to mean.
        if strategy is None:
            strategy = FeatureMatrixTransform.IMPUTE_STRATEGY_MEAN

        # If distribution is not specified, default to norm.
        if distribution is None:
            distribution = norm.rvs

        # TODO sxu: modify other modules to also return stuff
        if feature == FeatureMatrixTransform.ALL_FEATURES:
            self._impute_all_features(strategy, distribution=distribution)
        else:
            return self._impute_single_feature(feature, strategy, distribution=distribution)

    def do_impute_sx(self, matrix, means):
        '''
        sxu new implementation

        Input: train_df, but does not change it
        Output: dictionary {order_proc_id: {feature: imputation value}}
        '''
        import datetime
        # TODO: alert: changes row order and indices of matrix!

        datetime_format = "%Y-%m-%d %H:%M:%S"

        matrix_sorted = matrix.sort_values(['pat_id', 'order_time']).reset_index()
        count_time_suffixs = ['preTimeDays', 'postTimeDays']  # TODO: postTimeDays should really not appear!
        stats_numeric_suffixs = ['min', 'max', 'median', 'mean', 'std', 'first', 'last', 'diff', 'slope',
                                 'proximate']
        stats_time_suffixs = ['firstTimeDays', 'lastTimeDays', 'proximateTimeDays']

        impute_train = {}

        nega_inf_days = -1000000
        for i in range(0, matrix_sorted.shape[0]):
            cur_episode_id = matrix_sorted.ix[i, 'order_proc_id']
            impute_train[cur_episode_id] = {}
            for column in matrix_sorted.columns.values.tolist():
                '''
                Value not missing
                '''
                if matrix_sorted.ix[i, column] == matrix_sorted.ix[i, column]:
                    continue

                '''
                Value missing
                '''
                column_tail = column.split('.')[-1].strip()

                if column in means:
                    popu_mean = means[column]  # TODO: pre-compute with dict

                if column_tail in stats_numeric_suffixs:
                    '''
                    impute with the previous episode if available; otherwise population mean
                    '''
                    if i == 0 or (matrix_sorted.ix[i, 'pat_id'] != matrix_sorted.ix[i - 1, 'pat_id']) or (
                            matrix_sorted.ix[i - 1, column] != matrix_sorted.ix[i - 1, column]):
                        matrix_sorted.ix[i, column] = popu_mean  # impute_train[cur_episode_id][column] = popu_mean
                    else:
                        matrix_sorted.ix[i, column] = matrix_sorted.ix[
                            i - 1, column]  # impute_train[cur_episode_id][column] = train_df_sorted.ix[i-1, column]

                elif column_tail in stats_time_suffixs:
                    '''
                    use the previous + time difference if available; otherwise -infinite
                    '''
                    if i == 0 or (matrix_sorted.ix[i, 'pat_id'] != matrix_sorted.ix[i - 1, 'pat_id']) or (
                            matrix_sorted.ix[i - 1, column] != matrix_sorted.ix[i - 1, column]):
                        # impute_train[cur_episode_id][column] = nega_inf_days
                        matrix_sorted.ix[i, column] = nega_inf_days
                    else:
                        day_diff = (datetime.datetime.strptime(matrix_sorted.ix[i, 'order_time'], datetime_format) -
                                    datetime.datetime.strptime(matrix_sorted.ix[i - 1, 'order_time'],
                                                               datetime_format)).days
                        # impute_train[cur_episode_id][column] = train_df_sorted.ix[i-1, column] - day_diff # TODO!

                        matrix_sorted.ix[i, column] = matrix_sorted.ix[i - 1, column] - day_diff

                elif column_tail in count_time_suffixs:
                    '''
                    -infinite
                    '''
                    # impute_train[cur_episode_id][column] = nega_inf_days
                    matrix_sorted.ix[i, column] = nega_inf_days

                else:
                    '''
                    In all other cases, just use mean to impute
                    '''
                    matrix_sorted.ix[i, column] = popu_mean
                    pass

        return matrix_sorted.set_index('index')

    def _impute_all_features(self, strategy, distribution=None):
        for column in self._matrix:
            self._impute_single_feature(column, strategy, distribution=distribution)

    # TODO sxu: modify other modules to also return stuff
    def _impute_single_feature(self, feature, strategy, distribution=None):
        if strategy == FeatureMatrixTransform.IMPUTE_STRATEGY_MEAN:
            self._matrix[feature] =  self._matrix[feature].fillna(self._matrix[feature].mean(0))
            return self._matrix[feature].mean(0)
        elif strategy == FeatureMatrixTransform.IMPUTE_STRATEGY_MODE:
            self._matrix[feature] = self._matrix[feature].fillna(self._matrix[feature].mode().iloc[0])
        elif strategy == FeatureMatrixTransform.IMPUTE_STRATEGY_ZERO:
            self._matrix[feature] = self._matrix[feature].fillna(0.0)
        elif strategy == FeatureMatrixTransform.IMPUTE_STRATEGY_MEDIAN:
            self._matrix[feature] = self._matrix[feature].fillna(self._matrix[feature].median())
        elif strategy == FeatureMatrixTransform.IMPUTE_STRATEGY_DISTRIBUTION:
            self._matrix[feature] = self._matrix[feature].apply(lambda x: distribution() if pd.isnull(x) else x)

    def drop_null_features(self):
        for feature in self._matrix.columns.values:
            if self._matrix[feature].isnull().all():
                self.remove_feature(feature)

    def remove_feature(self, feature):
        try:
            del self._matrix[feature]
        except KeyError:
            log.info('Cannot remove non-existent feature "%s".' % feature)

    def filter_on_feature(self, feature, value):
        # remove rows where feature == value
        if pd.isnull(value): # nan is not comparable, so need different syntax
            rows_to_remove = self._matrix[pd.isnull(self._matrix[feature])].index
        else:
            try:
                rows_to_remove = self._matrix[self._matrix[feature] == value].index
            except TypeError:
                log.info('Cannot filter %s on %s; types are not comparable.' % (feature, str(value)))
                return

        self._matrix.drop(rows_to_remove, inplace = True)
        self._matrix.reset_index(drop=True, inplace = True)

        # return number of rows remaining
        return self._matrix.shape[0]

    def add_logarithm_feature(self, base_feature, logarithm=None):
        if logarithm is None:
            logarithm = FeatureMatrixTransform.LOG_BASE_E

        col_index = self._matrix.columns.get_loc(base_feature)

        if logarithm == FeatureMatrixTransform.LOG_BASE_E:
            log_feature = 'ln(' + base_feature + ')'
            new_col = self._matrix[base_feature].apply(np.log)
            self._matrix.insert(col_index + 1, log_feature, new_col)
        elif logarithm == FeatureMatrixTransform.LOG_BASE_10:
            log_feature = 'log10(' + base_feature + ')'
            new_col = self._matrix[base_feature].apply(np.log10)
            self._matrix.insert(col_index, log_feature, new_col)

        return log_feature

    def add_indicator_feature(self, base_feature, boolean_indicator=None):
        # boolean: determines whether to add True/False labels or 1/0
        if boolean_indicator is None or boolean_indicator is False:
            indicator = self._numeric_indicator
        else:
            indicator = self._boolean_indicator

        col_index = self._matrix.columns.get_loc(base_feature)
        indicator_feature = 'I(' + base_feature + ')'
        new_col = self._matrix[base_feature].apply(indicator)
        self._matrix.insert(col_index + 1, indicator_feature, new_col)

        return indicator_feature

    def add_threshold_feature(self, base_feature, lower_bound=None, upper_bound=None):
        # Add feature which indicates whether base_feature is >= lower_bound
        # and <= upper_bound.
        if lower_bound is None and upper_bound is None:
            raise ValueError('Must specify either lower_bound or upper_bound.')
        elif lower_bound is None:
            # base_feature <= upper_bound
            threshold_feature = 'I(%s<=%s)' % (base_feature, upper_bound)
            indicator = lambda x: 1 if x <= upper_bound else 0
        elif upper_bound is None:
            # base_feature >= lower_bound
            threshold_feature = 'I(%s>=%s)' % (base_feature, lower_bound)
            indicator = lambda x: 1 if x >= lower_bound else 0
        else:
            # lower_bound <= base_feature <= upper_bound
            threshold_feature = 'I(%s<=%s<=%s)' % (lower_bound, base_feature, upper_bound)
            indicator = lambda x: 1 if x <= upper_bound and x >= lower_bound else 0

        col_index = self._matrix.columns.get_loc(base_feature)
        new_col = self._matrix[base_feature].apply(indicator)
        self._matrix.insert(col_index + 1, threshold_feature, new_col)

        return threshold_feature

    def drop_duplicate_rows(self):
        self._matrix.drop_duplicates(inplace=True)

    def remove_low_signal_features(self):
        # Prune obviously unhelpful fields.
        # in theory, FeatureSelector should be able to prune these
        # automatically, but no harm in helping out given it has to sift
        # through ~3000 features.
        LOW_SIGNAL_FEATURES = [
            'index_time',
            'Birth.pre', 'Death.post'
            'Male.preTimeDays', 'Female.preTimeDays',
            'RaceWhiteHispanicLatino.preTimeDays',
            'RaceWhiteNonHispanicLatino.preTimeDays',
            'RaceHispanicLatino.preTimeDays',
            'RaceAsian.preTimeDays',
            'RaceBlack.preTimeDays',
            'RacePacificIslander.preTimeDays',
            'RaceNativeAmerican.preTimeDays',
            'RaceOther.preTimeDays',
            'RaceUnknown.preTimeDays'
            ]
        for feature in LOW_SIGNAL_FEATURES:
            self.remove_feature(feature)

    def _numeric_indicator(self, value):
        return 1 if pd.notnull(value) else 0

    def _boolean_indicator(self, value):
        return pd.notnull(value)

    def add_change_feature(self, method, param, feature_old, feature_new):
        # Add column unchanged_yn describing whether feature_new is 'unchanged'
        # relative to feature_old

        if method == "percent":
            change_col = self._matrix.apply(self._percent_change, \
            args=(feature_old, feature_new, param), axis = 1)
        elif method == "interval":
            change_col = self._matrix.apply(self._interval_change, \
            args=(feature_old, feature_new, param), axis = 1)
        elif method == "sd": #TODO (raikens): finish this
            k = 300 #TODO (raikens): make this user-specified
            n = self._matrix.shape[0]
            if (n <= k):
                raise ValueError("Not enough data to estimate sd")

            # estimate sd from sample and drop sample rows
            sample_rows = np.random.choice(n, k, replace = False)
            sd = np.std(self._matrix.loc[sample_rows, feature_new], ddof = 1)
            self._matrix.drop(sample_rows, inplace = True)
            self._matrix.reset_index(drop=True, inplace = True)
            margin = param*sd

            change_col = self._matrix.apply(self._interval_change, \
            args=(feature_old, feature_new, margin), axis = 1)

        else:
            raise ValueError("Must specify a supported method for change calculation")

        # add new column to matrix
        # TODO (raikens): since new column is always "unchange_yn," only one
        # change feature can be added.
        col_index = self._matrix.columns.get_loc(feature_new)
        self._matrix.insert(col_index + 1, "unchanged_yn", change_col)
        return "unchanged_yn"

    def _is_numeric(self, x):
        try:
            float(x)
            return (not isnan(x))
        except ValueError:
            return False

    def _percent_change(self, row, feature_old, feature_new, param):
        # Return 1 if new value has changed by more than <param> percent
        # of old value, else return 0.
        # If either old or new value is missing, returns 9999999.
        if not (self._is_numeric(row[feature_old]) and self._is_numeric(row[feature_new])):
            return 9999999
        elif row[feature_old] == 0.0:
            return 1
        else:
            return int(abs(1.0-float(row[feature_new])/float(row[feature_old])) < param)

    def _interval_change(self, row, feature_old, feature_new, param):
        # Return 1 if new value has changed by more than <param> from old value,
        # else return 0.
        # If either old or new value is missing, returns 9999999.
        if not (self._is_numeric(row[feature_old]) and self._is_numeric(row[feature_new])):
            return 9999999
        else:
            return int(abs(float(row[feature_new])-float(row[feature_old])) < param)
