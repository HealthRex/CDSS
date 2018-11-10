#!/usr/bin/python
"""
Abstract class for an end-to-end pipeline which builds a raw feature matrix,
processes the raw matrix, trains a predictor on the processed matrix,
tests the predictor's performance, and summarizes its analysis.

SubClasses will be expected to override the following functions:
* __init__()
* _build_raw_matrix_path()
* _build_raw_feature_matrix()
* _build_processed_matrix_path()
* _build_processed_feature_matrix()
* _add_features()
* _remove_features()
* _select_features()
* summarize()
"""

import datetime
import inspect
import os
import pandas as pd
import sys

from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d

from medinfo.common.Util import log
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.ml.FeatureSelector import FeatureSelector
from medinfo.ml.BifurcatedSupervisedClassifier import BifurcatedSupervisedClassifier
from medinfo.ml.Regressor import Regressor
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.ml.ClassifierAnalyzer import ClassifierAnalyzer


class SupervisedLearningPipeline:
    CLASSIFICATION = 'classification'
    REGRESSION = 'regression'

    def __init__(self, variable, num_data_points, use_cache=None, random_state=None,
                 isLabPanel=True, timeLimit=None, holdOut=False,
                 isLabNormalityPredictionPipeline=False):
        # Process arguments.
        self._var = variable
        self._num_rows = num_data_points
        self._flush_cache = True if use_cache is None else False

        self._raw_matrix = None
        self._processed_matrix = None
        self._predictor = None
        self._eliminated_features = list()
        self._removed_features = list()
        self._added_features = list()
        self._random_state = random_state

        self._isLabNormalityPredictionPipeline = isLabNormalityPredictionPipeline
        self._isLabPanel = isLabPanel
        self._timeLimit = timeLimit
        self._holdOut = holdOut

    def predictor(self):
        return self._predictor

    def _build_model_dump_path(self, file_name_template, pipeline_module_path):
        # Build model file name.
        slugified_var = '-'.join(self._var.split())
        model_dump_name = file_name_template % (slugified_var)

        # Build path.
        data_dir = self._fetch_data_dir_path(pipeline_module_path)
        model_dump_path = '/'.join([data_dir, model_dump_name])

        return model_dump_path

    def _build_raw_matrix_path(self, file_name_template, pipeline_module_file):
        # Build raw matrix file name.
        slugified_var = '-'.join(self._var.split())
        raw_matrix_name = file_name_template % (slugified_var, self._num_rows)

        # Build path.
        data_dir = self._fetch_data_dir_path(pipeline_module_file)
        raw_matrix_path = '/'.join([data_dir, raw_matrix_name])

        return raw_matrix_path

    def _build_matrix_path(self, file_name_template, pipeline_module_path):
        # Build matrix file name.
        slugified_var = '-'.join(self._var.split())
        matrix_name = file_name_template % (slugified_var, self._num_rows)

        # Build path.
        data_dir = self._fetch_data_dir_path(pipeline_module_path)
        matrix_path = '/'.join([data_dir, matrix_name])

        return matrix_path

    def _fetch_data_dir_path(self, pipeline_module_path):
        # e.g. app_dir = CDSS/scripts/LabTestAnalysis/machine_learning
        app_dir = os.path.dirname(os.path.abspath(pipeline_module_path))

        # e.g. data_dir = CDSS/scripts/LabTestAnalysis/machine_learning/data
        parent_dir_list = app_dir.split('/')
        parent_dir_list.append('data')
        parent_dir_list.append(self._var)
        data_dir = '/'.join(parent_dir_list)

        # If data_dir does not exist, make it.
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        return data_dir

    def _build_raw_feature_matrix(self, matrix_class, raw_matrix_path, params=None):
        # If raw matrix exists, and client has not requested to flush the cache,
        # just use the matrix that already exists and return.
        if params is None:
            self._raw_matrix_params = {}
        else:
            self._raw_matrix_params = params
        if os.path.exists(raw_matrix_path) and not self._flush_cache:
            if self._isLabNormalityPredictionPipeline and not self._holdOut:
                fm_io = FeatureMatrixIO()
                matrix = fm_io.read_file_to_data_frame(raw_matrix_path)
                self.used_patient_set = set(matrix['pat_id'].values)
            pass
        else:
            # Each matrix class may have a custom set of parameters which should
            # be passed on directly to matrix_class, but we expect them to have
            # at least 1 primary variables and # of rows.
            # Ensure that random_state is [-1, 1]
            random_state = float(self._random_state)/float(sys.maxint)
            if self._isLabNormalityPredictionPipeline:
                matrix = matrix_class(self._var, self._num_rows, random_state=random_state,
                                  isLabPanel=self._isLabPanel, timeLimit=self._timeLimit,
                                      notUsePatIds=self.notUsePatIds)
                if not self._holdOut:
                    self.used_patient_set = matrix.patients
            else:
                matrix = matrix_class(self._var, self._num_rows, random_state=random_state)
            matrix.write_matrix(raw_matrix_path)

    def _build_processed_feature_matrix_sx(self, params):
        # params is a dict defining the details of how the raw feature matrix
        # should be transformed into the processed matrix. Given the sequence
        # of steps will be identical across all pipelines, sbala decided to
        # pack all the variability into this dict. It's not ideal because the
        # dict has 10+ values, but that seems better than forcing all pipelines
        # to reproduce the logic of the processing steps.
        # Principle: Minimize overridden function calls.
        #   params['features_to_add'] = features_to_add
        #   params['features_to_filter_on'] (optional) = features_to_filter_on
        #   params['imputation_strategies'] = imputation_strategies
        #   params['features_to_remove'] = features_to_remove
        #   params['outcome_label'] = outcome_label
        #   params['selection_problem'] = selection_problem
        #   params['selection_algorithm'] = selection_algorithm
        #   params['percent_features_to_select'] = percent_features_to_select
        #   params['matrix_class'] = matrix_class
        #   params['pipeline_file_path'] = pipeline_file_path
        #   TODO(sbala): Determine which fields should have defaults.
        fm_io = FeatureMatrixIO()
        log.debug('params: %s' % params)
        # If processed matrix exists, and the client has not requested to flush
        # the cache, just use the matrix that already exists and return.
        processed_matrix_path = params['processed_matrix_path']
        if os.path.exists(processed_matrix_path) and not self._flush_cache:
            # Assume feature selection already happened, but we still need
            # to split the data into training and test data.
            processed_matrix = fm_io.read_file_to_data_frame(processed_matrix_path)
            '''
            Make sure the order of rows is consistent before splitting
            '''
            processed_matrix.sort_index(inplace=True)
            self._train_test_split(processed_matrix, params['outcome_label']) #TODO sxu: when reloading, no pat_id
        else:
            # Read raw matrix.
            raw_matrix = fm_io.read_file_to_data_frame(params['raw_matrix_path'])
            # Initialize FMT.

            # Divide processed_matrix into training and test data.
            # This must happen before feature selection so that we don't
            # accidentally learn information from the test data.

            # TODO: work on this...
            self._train_test_split(raw_matrix, params['outcome_label'])

            fmt = FeatureMatrixTransform()
            train_df = self._X_train.join(self._y_train)
            fmt.set_input_matrix(train_df)

            # Add features.
            self._add_features(fmt, params['features_to_add'])

            # Remove features.
            self._remove_features(fmt, params['features_to_remove'])
            # Filter on features
            if 'features_to_filter_on' in params:
                self._filter_on_features(fmt, params['features_to_filter_on'])

            # HACK: When read_csv encounters duplicate columns, it deduplicates
            # them by appending '.1, ..., .N' to the column names.
            # In future versions of pandas, simply pass mangle_dupe_cols=True
            # to read_csv, but not ready as of pandas 0.22.0.
            for feature in raw_matrix.columns.values:
                if feature[-2:] == ".1":
                    fmt.remove_feature(feature)
                    self._removed_features.append(feature)

            # Impute data.
            self._impute_data(fmt, train_df, params['imputation_strategies'])

            # In case any all-null features were created in preprocessing,
            # drop them now so feature selection will work
            fmt.drop_null_features()

            # Build interim matrix.
            train_df = fmt.fetch_matrix()

            self._y_train = pd.DataFrame(train_df.pop(params['outcome_label']))
            self._X_train = train_df

            '''
            Select X_test columns according to processed X_train
            '''
            self._X_test = self._X_test[self._X_train.columns]
            '''
            Impute data according to the same strategy when training
            '''
            for feat in self._X_test.columns:
                self._X_test[feat] = self._X_test[feat].fillna(self.feat2imputed_dict[feat])

            self._select_features(params['selection_problem'],
                params['percent_features_to_select'],
                params['selection_algorithm'],
                params['features_to_keep'])

            train = self._y_train.join(self._X_train)
            test = self._y_test.join(self._X_test)

            processed_matrix = train.append(test)
            '''
            Need to recover the order of rows before writing into disk
            '''
            processed_matrix.sort_index(inplace=True)

            # Write output to new matrix file.
            header = self._build_processed_matrix_header(params)
            fm_io.write_data_frame_to_file(processed_matrix, \
                processed_matrix_path, header)

        '''
        For testing the model on the holdout set, should remember features 
        to select from the raw matrix of the holdout data. 
        '''
        if self._isLabNormalityPredictionPipeline:
            final_features = processed_matrix.columns.values
            if not self.feat2imputed_dict:
                '''
                The dict was not created during imputation. 
                Probably because the processed matrix was loaded from previous session. 
                Take the 'best guess' for the imputed value as the most common one in
                any column. 
                '''
                for feat in final_features:
                    most_freq_val = processed_matrix[feat].value_counts().idxmax()
                    self.feat2imputed_dict[feat] = most_freq_val

            curr_keys = self.feat2imputed_dict.keys()

            '''
            Only need to impute the selected features for the holdOut set. 
            '''
            for one_key in curr_keys:
                if one_key not in final_features:
                    self.feat2imputed_dict.pop(one_key)

    def _build_processed_feature_matrix(self, params):
        # params is a dict defining the details of how the raw feature matrix
        # should be transformed into the processed matrix. Given the sequence
        # of steps will be identical across all pipelines, sbala decided to
        # pack all the variability into this dict. It's not ideal because the
        # dict has 10+ values, but that seems better than forcing all pipelines
        # to reproduce the logic of the processing steps.
        # Principle: Minimize overridden function calls.
        #   params['features_to_add'] = features_to_add
        #   params['features_to_filter_on'] (optional) = features_to_filter_on
        #   params['imputation_strategies'] = imputation_strategies
        #   params['features_to_remove'] = features_to_remove
        #   params['outcome_label'] = outcome_label
        #   params['selection_problem'] = selection_problem
        #   params['selection_algorithm'] = selection_algorithm
        #   params['percent_features_to_select'] = percent_features_to_select
        #   params['matrix_class'] = matrix_class
        #   params['pipeline_file_path'] = pipeline_file_path
        #   TODO(sbala): Determine which fields should have defaults.
        fm_io = FeatureMatrixIO()
        log.debug('params: %s' % params)
        # If processed matrix exists, and the client has not requested to flush
        # the cache, just use the matrix that already exists and return.
        processed_matrix_path = params['processed_matrix_path']
        if os.path.exists(processed_matrix_path) and not self._flush_cache:
            # Assume feature selection already happened, but we still need
            # to split the data into training and test data.
            processed_matrix = fm_io.read_file_to_data_frame(processed_matrix_path)
            self._train_test_split(processed_matrix, params['outcome_label'])
        else:
            # Read raw matrix.
            raw_matrix = fm_io.read_file_to_data_frame(params['raw_matrix_path'])
            # Initialize FMT.
            fmt = FeatureMatrixTransform()
            fmt.set_input_matrix(raw_matrix)

            # Add features.
            self._add_features(fmt, params['features_to_add'])
            # Remove features.
            self._remove_features(fmt, params['features_to_remove'])
            # Filter on features
            if 'features_to_filter_on' in params:
                self._filter_on_features(fmt, params['features_to_filter_on'])

            # HACK: When read_csv encounters duplicate columns, it deduplicates
            # them by appending '.1, ..., .N' to the column names.
            # In future versions of pandas, simply pass mangle_dupe_cols=True
            # to read_csv, but not ready as of pandas 0.22.0.
            for feature in raw_matrix.columns.values:
                if feature[-2:] == ".1":
                    fmt.remove_feature(feature)
                    self._removed_features.append(feature)

            # Impute data.
            self._impute_data(fmt, raw_matrix, params['imputation_strategies'])

            # In case any all-null features were created in preprocessing,
            # drop them now so feature selection will work
            fmt.drop_null_features()

            # Build interim matrix.
            processed_matrix = fmt.fetch_matrix()

            # Divide processed_matrix into training and test data.
            # This must happen before feature selection so that we don't
            # accidentally learn information from the test data.
            self._train_test_split(processed_matrix, params['outcome_label'])

            self._select_features(params['selection_problem'],
                params['percent_features_to_select'],
                params['selection_algorithm'],
                params['features_to_keep'])

            train = self._y_train.join(self._X_train)
            test = self._y_test.join(self._X_test)
            processed_matrix = train.append(test)

            # Write output to new matrix file.
            header = self._build_processed_matrix_header(params)
            fm_io.write_data_frame_to_file(processed_matrix, \
                processed_matrix_path, header)

        '''
        For testing the model on the holdout set, should remember features 
        to select from the raw matrix of the holdout data. 
        '''
        if self._isLabNormalityPredictionPipeline:
            final_features = processed_matrix.columns.values
            if not self.feat2imputed_dict:
                '''
                The dict was not created during imputation. 
                Probably because the processed matrix was loaded from previous session. 
                Take the 'best guess' for the imputed value as the most common one in
                any column. 
                '''
                for feat in final_features:
                    most_freq_val = processed_matrix[feat].value_counts().idxmax()
                    self.feat2imputed_dict[feat] = most_freq_val

            curr_keys = self.feat2imputed_dict.keys()

            '''
            Only need to impute the selected features for the holdOut set. 
            '''
            for one_key in curr_keys:
                if one_key not in final_features:
                    self.feat2imputed_dict.pop(one_key)

    def _add_features(self, fmt, features_to_add):
        # Expected format for features_to_add:
        # {
        #   'threshold': [{arg1, arg2, etc.}, ...]
        #   'indicator': [{arg1, arg2, etc.}, ...]
        #   'logarithm': [{arg1, arg2, etc.}, ...]
        # }
        indicator_features = features_to_add.get('indicator')
        threshold_features = features_to_add.get('threshold')
        logarithm_features = features_to_add.get('logarithm')
        change_features = features_to_add.get('change')

        if indicator_features:
            for feature in indicator_features:
                base_feature = feature.get('base_feature')
                boolean_indicator = feature.get('boolean_indicator')
                added_feature = fmt.add_indicator_feature(base_feature, boolean_indicator)
                self._added_features.append(added_feature)

        if threshold_features:
            for feature in threshold_features:
                base_feature = feature.get('base_feature')
                lower_bound= feature.get('lower_bound')
                upper_bound = feature.get('upper_bound')
                added_feature = fmt.add_threshold_feature(base_feature, lower_bound, upper_bound)
                self._added_features.append(added_feature)

        if logarithm_features:
            for feature in logarithm_features:
                base_feature = feature.get('base_feature')
                logarithm = feature.get('logarithm')
                added_feature = fmt.add_threshold_feature(base_feature, logarithm)
                self._added_features.append(added_feature)

        # TODO (raikens): right now, unchanged_yn is the only allowable name for a
        # change feature, which means at most one change_feature can be added
        if change_features:
            if len(change_features) > 1:
                 raise ValueError("Adding multiple \'change\' type features is not yet supported")

            for feature in change_features:
                feature_old = feature.get('feature_old')
                feature_new = feature.get('feature_new')
                method = feature.get('method')
                param = feature.get('param')
                added_feature = fmt.add_change_feature(method, param, feature_old, feature_new)
                self._added_features.append(added_feature)

                # sd method discards 300 rows for measuring sd
                if method == 'sd':
                    self._num_rows = self._num_rows - 300

        log.debug('self._added_features: %s' % self._added_features)

    def _impute_data(self, fmt, raw_matrix, imputation_strategies):
        for feature in raw_matrix.columns.values:
            if feature in self._removed_features:
                continue
            # If all values are null, just remove the feature.
            # Otherwise, imputation will fail (there's no mean value),
            # and sklearn will ragequit.
            if raw_matrix[feature].isnull().all():
                fmt.remove_feature(feature)
                self._removed_features.append(feature)
            # Only try to impute if some of the values are null.
            elif raw_matrix[feature].isnull().any():
                # If an imputation strategy is specified, follow it.
                if imputation_strategies.get(feature):
                    strategy = imputation_strategies.get(feature)
                    fmt.impute(feature, strategy)
                else:
                    # TODO(sbala): Impute all time features with non-mean value.
                    imputed_value = fmt.impute(feature)
                    if self._isLabNormalityPredictionPipeline:
                        self.feat2imputed_dict[feature] = imputed_value
            else:
                '''
                If there is no need to impute, still keep the mean value, in case test data 
                need imputation
                TODO sxu: take care of the case of non-mean imputation strategy
                '''
                if self._isLabNormalityPredictionPipeline:
                    imputed_value = fmt.impute(feature)
                    self.feat2imputed_dict[feature] = imputed_value

    def _remove_features(self, fmt, features_to_remove):
        # Prune manually identified features (meant for obviously unhelpful).
        # In theory, FeatureSelector should be able to prune these, but no
        # reason not to help it out a little bit.
        for feature in features_to_remove:
            fmt.remove_feature(feature)
            self._removed_features.append(feature)

        log.debug('self._removed_features: %s' % self._removed_features)

    def _filter_on_features(self, fmt, features_to_filter_on):
        # Filter out rows with unwanted value for given feature
        for filter_feature in features_to_filter_on:
            feature = filter_feature.get('feature')
            value = filter_feature.get('value')
            self._num_rows = fmt.filter_on_feature(feature, value)
            log.debug('Removed rows where %s equals \'%s\'; %d rows remain.' % (feature, str(value), self._num_rows))

    '''
    Strategy 1: split by pat_id, no overlapping between train/test
    '''
    def _train_test_split_sx1(self, processed_matrix, outcome_label):
        log.debug('outcome_label: %s' % outcome_label)
        all_pat_ids = list(set(processed_matrix['pat_id'].values))
        train_pat_ids, test_pat_ids = train_test_split(all_pat_ids, random_state=self._random_state)

        train_matrix = processed_matrix[processed_matrix['pat_id'].isin(train_pat_ids)].copy()
        self._y_train = pd.DataFrame(train_matrix.pop(outcome_label))
        self._X_train = train_matrix

        test_matrix = processed_matrix[processed_matrix['pat_id'].isin(test_pat_ids)].copy()
        self._y_test = pd.DataFrame(test_matrix.pop(outcome_label))
        self._X_test = test_matrix

    def _train_test_split(self, processed_matrix, outcome_label):
        log.debug('outcome_label: %s' % outcome_label)
        y = pd.DataFrame(processed_matrix.pop(outcome_label))
        X = processed_matrix
        log.debug('X.columns: %s' % X.columns)
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(X, y, random_state=self._random_state)

    def _select_features(self, problem, percent_features_to_select, algorithm, features_to_keep=None):
        # Initialize FeatureSelector.
        fs = FeatureSelector(problem=problem, algorithm=algorithm, random_state=self._random_state)
        fs.set_input_matrix(self._X_train, column_or_1d(self._y_train))
        num_features_to_select = int(percent_features_to_select*len(self._X_train.columns.values))

        # Parse features_to_keep.
        if features_to_keep is None:
            features_to_keep = []

        # Select features.
        fs.select(k=num_features_to_select)

        # Enumerate eliminated features pre-transformation.
        feature_ranks = fs.compute_ranks()
        for i in range(len(feature_ranks)):
            if feature_ranks[i] > num_features_to_select:
                # If in features_to_keep, pretend it wasn't eliminated.
                if self._X_train.columns[i] not in features_to_keep:
                    self._eliminated_features.append(self._X_train.columns[i])

        # Hack: rather than making FeatureSelector handle the concept of
        # kept features, just copy the data here and add it back to the
        # transformed matrices.
        # Rather than looping, do this individually so that we can skip if
        # transformed X already has the feature.
        for feature in features_to_keep:
            kept_X_train_feature = self._X_train[[feature]].copy()
            log.debug('kept_X_train_feature.shape: %s' % str(kept_X_train_feature.shape))
            self._X_train = fs.transform_matrix(self._X_train)
            if feature not in self._X_train:
                self._X_train = self._X_train.merge(kept_X_train_feature, left_index=True, right_index=True)

            kept_X_test_feature = self._X_test[[feature]].copy()
            log.debug('kept_X_test_feature.shape: %s' % str(kept_X_test_feature.shape))
            self._X_test = fs.transform_matrix(self._X_test)
            if feature not in self._X_test:
                self._X_test = self._X_test.merge(kept_X_test_feature, left_index=True, right_index=True)

        if not features_to_keep:
        # Even if there is no feature to keep, still need to
        # perform transform_matrix to drop most low-rank features
            self._X_train = fs.transform_matrix(self._X_train)
            self._X_test = fs.transform_matrix(self._X_test)

    def _build_processed_matrix_header(self, params):
        # FeatureMatrixFactory and FeatureMatrixIO expect a list of strings.
        # Each comment below represents the line in the comment.
        header = list()

        processed_matrix_path = params['processed_matrix_path']
        pipeline_file_path = params['pipeline_file_path']
        raw_matrix_name = params['raw_matrix_path'].split('/')[-1]
        file_summary = self._build_file_summary(processed_matrix_path, \
            pipeline_file_path, raw_matrix_name)
        header.extend(file_summary)
        header.append('')
        data_overview = params['data_overview']
        header.extend(data_overview)
        header.append('')
        processing_summary = self._build_processing_steps_summary()
        header.extend(processing_summary)

        return header

    def _build_file_summary(self, processed_matrix_path, pipeline_file_path, raw_matrix_name):
        summary = list()

        # <file_name.tab>
        matrix_file_name = processed_matrix_path.split('/')[-1]
        summary.append(matrix_file_name)
        # Created: <timestamp>
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        summary.append('Created: %s' % timestamp)
        # Source: __name__
        module_name = pipeline_file_path.split('/')[-1]
        summary.append('Source: %s' % module_name)
        # Command: Pipeline()
        class_name = module_name.split('.')[0]
        args = [self._var, str(self._num_rows)]
        for key, value in self._raw_matrix_params:
            args.append('%s=%s' % (key, value))
        command = '%s(%s)' % (class_name, ', '.join(args))
        summary.append('Command: %s' % command)
        # Number of Observations
        summary.append('Number of Episodes: %s' % self._num_rows)
        summary.append('')
        # Overview:
        summary.append('Overview:')
        # This file is a processed version of ___.
        line = 'This file is a post-processed version of %s.' % raw_matrix_name
        summary.append(line)

        return summary

    def _build_processing_steps_summary(self):
        summary = []

        # This matrix is the result of the following processing steps on the raw matrix:
        line = 'This matrix is the result of the following processing steps on the raw matrix:'
        summary.append(line)
        #   * Adding the following features.
        line = '  * Adding the following features:'
        summary.append(line)
        #   *   ___
        for feature in self._added_features:
            line = '      %s' % feature
            summary.append(line)
        #   * Imputing missing values with the mean value of each column.
        line = '  * Imputing missing values with the mean value of each column.'
        summary.append(line)
        #   (2) Manually removing low-information features:
        line = '  * Manually removing low-information features:'
        summary.append(line)
        #       ___
        line = '      %s' % str(self._removed_features)
        summary.append(line)
        #   (3) Algorithmically selecting the top 100 features via recursive feature elimination.
        line = '  * Algorithmically selecting the top 100 features via recursive feature elimination.'
        summary.append(line)
        #       The following features were eliminated.
        line = '      The following features were eliminated:'
        summary.append(line)
        # List all features with rank >100.
        line = '        %s' % str(self._eliminated_features)
        summary.append(line)

        return summary

    def _train_predictor(self, problem, classes=None, hyperparams=None):
        if problem == SupervisedLearningPipeline.CLASSIFICATION:
            if 'bifurcated' in hyperparams['algorithm']:
                learning_class = BifurcatedSupervisedClassifier
                # Strip 'bifurcated-' from algorithm for SupervisedClassifier.
                hyperparams['algorithm'] = '-'.join(hyperparams['algorithm'].split('-')[1:])
            else:
                learning_class = SupervisedClassifier

            self._predictor = learning_class(classes, hyperparams)
        elif problem == SupervisedLearningPipeline.REGRESSION:
            learning_class = Regressor
            self._predictor = learning_class(algorithm=algorithm)
        status = self._predictor.train(self._X_train, column_or_1d(self._y_train))

        return status

    def _analyze_predictor(self, dest_dir, pipeline_prefix):
        analyzer = ClassifierAnalyzer(self._predictor, self._X_test, self._y_test)

        # Build names for output plots and report.
        direct_comparisons_name = '%s-direct-compare-results.csv' % pipeline_prefix
        precision_at_k_plot_name = '%s-precision-at-k-plot.png' % pipeline_prefix
        precision_recall_plot_name = '%s-precision-recall-plot.png' % pipeline_prefix
        roc_plot_name = '%s-roc-plot.png' % pipeline_prefix
        report_name = '%s-report.tab' % pipeline_prefix

        # Build paths.
        direct_comparisons_path = '/'.join([dest_dir, direct_comparisons_name])
        log.debug('direct_comparisons_path: %s' % direct_comparisons_path)
        precision_at_k_plot_path = '/'.join([dest_dir, precision_at_k_plot_name])
        log.debug('precision_at_k_plot_path: %s' % precision_at_k_plot_path)
        precision_recall_plot_path = '/'.join([dest_dir, precision_recall_plot_name])
        log.debug('precision_recall_plot_path: %s' % precision_recall_plot_path)
        roc_plot_path = '/'.join([dest_dir, roc_plot_name])
        log.debug('roc_plot_path: %s' % roc_plot_path)
        report_path = '/'.join([dest_dir, report_name])
        log.debug('report_path: %s' % report_path)

        # Build plot titles.
        roc_plot_title = 'ROC (%s)' % pipeline_prefix
        precision_recall_plot_title = 'Precision-Recall (%s)' % pipeline_prefix
        precision_at_k_plot_title = 'Precision @K (%s)' % pipeline_prefix

        # Write output.
        analyzer.output_direct_comparisons(direct_comparisons_path)
        analyzer.plot_roc_curve(roc_plot_title, roc_plot_path)
        analyzer.plot_precision_recall_curve(precision_recall_plot_title, precision_recall_plot_path)
        analyzer.plot_precision_at_k_curve(precision_at_k_plot_title, precision_at_k_plot_path)
        analyzer.write_report(report_path, ci=0.95)


    # sx
    def _analyze_predictor_traindata(self, dest_dir, pipeline_prefix):
        analyzer = ClassifierAnalyzer(self._predictor, self._X_train, self._y_train)
        train_label = 'traindata'

        # Build names for output plots and report.
        direct_comparisons_name = '%s-direct-compare-results-%s.csv' % (pipeline_prefix, train_label)
        precision_at_k_plot_name = '%s-precision-at-k-plot-%s.png' % (pipeline_prefix, train_label)
        precision_recall_plot_name = '%s-precision-recall-plot-%s.png' % (pipeline_prefix, train_label)
        roc_plot_name = '%s-roc-plot-%s.png' % (pipeline_prefix, train_label)
        report_name = '%s-report-%s.tab' % (pipeline_prefix, train_label)

        # Build paths.
        direct_comparisons_path = '/'.join([dest_dir, direct_comparisons_name])
        log.debug('direct_comparisons_path: %s' % direct_comparisons_path)
        precision_at_k_plot_path = '/'.join([dest_dir, precision_at_k_plot_name])
        log.debug('precision_at_k_plot_path: %s' % precision_at_k_plot_path)
        precision_recall_plot_path = '/'.join([dest_dir, precision_recall_plot_name])
        log.debug('precision_recall_plot_path: %s' % precision_recall_plot_path)
        roc_plot_path = '/'.join([dest_dir, roc_plot_name])
        log.debug('roc_plot_path: %s' % roc_plot_path)
        report_path = '/'.join([dest_dir, report_name])
        log.debug('report_path: %s' % report_path)

        # Build plot titles.
        roc_plot_title = 'ROC (%s)' % pipeline_prefix
        precision_recall_plot_title = 'Precision-Recall (%s)' % pipeline_prefix
        precision_at_k_plot_title = 'Precision @K (%s)' % pipeline_prefix

        # Write output.
        analyzer.output_direct_comparisons(direct_comparisons_path)
        # analyzer.plot_roc_curve(roc_plot_title, roc_plot_path)
        # analyzer.plot_precision_recall_curve(precision_recall_plot_title, precision_recall_plot_path)
        # analyzer.plot_precision_at_k_curve(precision_at_k_plot_title, precision_at_k_plot_path)
        # analyzer.write_report(report_path, ci=0.95)


    def _analyze_predictor_holdoutset(self, dest_dir, pipeline_prefix):
        slugified_var = '-'.join(self._var.split())
        holdout_path = dest_dir + '/../' + '%s-normality-matrix-%d-episodes-processed-holdout.tab'%(slugified_var, self._num_rows)
        fm_io = FeatureMatrixIO()
        processed_matrix = fm_io.read_file_to_data_frame(holdout_path)
        if self._isLabPanel:
            y_holdout = pd.DataFrame(processed_matrix.pop('all_components_normal'))
        else:
            y_holdout = pd.DataFrame(processed_matrix.pop('component_normal'))
        X_holdout = processed_matrix
        analyzer = ClassifierAnalyzer(self._predictor, X_holdout, y_holdout)
        train_label = 'holdoutset'

        # Build names for output plots and report.
        direct_comparisons_name = '%s-direct-compare-results-%s.csv' % (pipeline_prefix, train_label)
        precision_at_k_plot_name = '%s-precision-at-k-plot-%s.png' % (pipeline_prefix, train_label)
        precision_recall_plot_name = '%s-precision-recall-plot-%s.png' % (pipeline_prefix, train_label)
        roc_plot_name = '%s-roc-plot-%s.png' % (pipeline_prefix, train_label)
        report_name = '%s-report-%s.tab' % (pipeline_prefix, train_label)

        # Build paths.
        direct_comparisons_path = '/'.join([dest_dir, direct_comparisons_name])
        log.debug('direct_comparisons_path: %s' % direct_comparisons_path)
        precision_at_k_plot_path = '/'.join([dest_dir, precision_at_k_plot_name])
        log.debug('precision_at_k_plot_path: %s' % precision_at_k_plot_path)
        precision_recall_plot_path = '/'.join([dest_dir, precision_recall_plot_name])
        log.debug('precision_recall_plot_path: %s' % precision_recall_plot_path)
        roc_plot_path = '/'.join([dest_dir, roc_plot_name])
        log.debug('roc_plot_path: %s' % roc_plot_path)
        report_path = '/'.join([dest_dir, report_name])
        log.debug('report_path: %s' % report_path)

        # Build plot titles.
        roc_plot_title = 'ROC (%s)' % pipeline_prefix
        precision_recall_plot_title = 'Precision-Recall (%s)' % pipeline_prefix
        precision_at_k_plot_title = 'Precision @K (%s)' % pipeline_prefix

        # Write output.
        analyzer.output_direct_comparisons(direct_comparisons_path)
        analyzer.plot_roc_curve(roc_plot_title, roc_plot_path)
        analyzer.plot_precision_recall_curve(precision_recall_plot_title, precision_recall_plot_path)
        analyzer.plot_precision_at_k_curve(precision_at_k_plot_title, precision_at_k_plot_path)
        analyzer.write_report(report_path, ci=0.95)
