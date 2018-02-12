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

from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d

from medinfo.common.Util import log
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.ml.FeatureSelector import FeatureSelector
from medinfo.ml.Regressor import Regressor
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.ml.ClassifierAnalyzer import ClassifierAnalyzer


class SupervisedLearningPipeline:
    CLASSIFICATION = 'classification'
    REGRESSION = 'regression'

    def __init__(self, variable, num_data_points, use_cache=None):
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
            pass
        else:
            # Each matrix class may have a custom set of parameters which should
            # be passed on directly to matrix_class, but we expect them to have
            # at least 1 primary variables and # of rows.
            matrix = matrix_class(self._var, self._num_rows)
            matrix.write_matrix(raw_matrix_path)

    def _build_processed_feature_matrix(self, params):
        # params is a dict defining the details of how the raw feature matrix
        # should be transformed into the processed matrix. Given the sequence
        # of steps will be identical across all pipelines, sbala decided to
        # pack all the variability into this dict. It's not ideal because the
        # dict has 10+ values, but that seems better than forcing all pipelines
        # to reproduce the logic of the processing steps.
        # Principle: Minimize overridden function calls.
        #   params['features_to_add'] = features_to_add
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
            # Impute data.
            self._impute_data(fmt, raw_matrix, params['imputation_strategies'])
            # Remove duplicate data.
            fmt.drop_duplicate_rows()

            # Build interim matrix.
            processed_matrix = fmt.fetch_matrix()

            # Divide processed_matrix into training and test data.
            # This must happen before feature selection so that we don't
            # accidentally learn information from the test data.
            self._train_test_split(processed_matrix, params['outcome_label'])
            self._select_features(params['selection_problem'],
                params['percent_features_to_select'],
                params['selection_algorithm'])
            train = self._y_train.join(self._X_train)
            test = self._y_test.join(self._X_test)
            processed_matrix = train.append(test)

            # Write output to new matrix file.
            header = self._build_processed_matrix_header(params)
            fm_io.write_data_frame_to_file(processed_matrix, \
                processed_matrix_path, header)

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
                    fmt.impute(feature)

    def _remove_features(self, fmt, features_to_remove):
        # Prune manually identified features (meant for obviously unhelpful).
        # In theory, FeatureSelector should be able to prune these, but no
        # reason not to help it out a little bit.
        for feature in features_to_remove:
            fmt.remove_feature(feature)
            self._removed_features.append(feature)

    def _train_test_split(self, processed_matrix, outcome_label):
        log.debug('outcome_label: %s' % outcome_label)
        y = pd.DataFrame(processed_matrix.pop(outcome_label))
        X = processed_matrix
        log.debug('X.columns: %s' % X.columns)
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(X, y)

    def _select_features(self, problem, percent_features_to_select, algorithm):
        # Initialize FeatureSelector.
        fs = FeatureSelector(problem=problem, algorithm=algorithm)
        fs.set_input_matrix(self._X_train, column_or_1d(self._y_train))
        num_features_to_select = int(percent_features_to_select*len(self._X_train.columns.values))

        # Select features.
        fs.select(k=num_features_to_select)

        # Enumerate eliminated features pre-transformation.
        feature_ranks = fs.compute_ranks()
        for i in range(len(feature_ranks)):
            if feature_ranks[i] > num_features_to_select:
                self._eliminated_features.append(self._X_train.columns[i])

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
        #
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

    def _train_predictor(self, problem, algorithm=None, classes=None):
        if problem == SupervisedLearningPipeline.CLASSIFICATION:
            learning_class = SupervisedClassifier
            hyperparams = {'algorithm': algorithm}
            self._predictor = learning_class(classes, hyperparams)
        elif problem == SupervisedLearningPipeline.REGRESSION:
            learning_class = Regressor
            self._predictor = learning_class(algorithm=algorithm)
        self._predictor.train(self._X_train, column_or_1d(self._y_train))

    def _analyze_predictor(self, dest_dir, pipeline_prefix):
        analyzer = ClassifierAnalyzer(self._predictor, self._X_test, self._y_test)

        # Build names for output plots and report.
        precision_at_k_plot_name = '%s-precision-at-k-plot.png' % pipeline_prefix
        precision_recall_plot_name = '%s-precision-recall-plot.png' % pipeline_prefix
        roc_plot_name = '%s-roc-plot.png' % pipeline_prefix
        report_name = '%s.report' % pipeline_prefix

        # Build paths.
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
        analyzer.plot_roc_curve(roc_plot_title, roc_plot_path)
        analyzer.plot_precision_recall_curve(precision_recall_plot_title, precision_recall_plot_path)
        analyzer.plot_precision_at_k_curve(precision_at_k_plot_title, precision_at_k_plot_path)
        analyzer.write_report(report_path)
