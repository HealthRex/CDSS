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

import inspect
import os

from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d

class SupervisedLearningPipeline:
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

        # e.g. data_dir = CDSS/scripts/LabTestAnalysis/data
        parent_dir_list = app_dir.split('/')[:-1]
        parent_dir_list.append('data')
        data_dir = '/'.join(parent_dir_list)

        # If data_dir does not exist, make it.
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        return data_dir

    def _build_raw_feature_matrix(self, matrix_class, raw_matrix_path):
        # If raw matrix exists, and client has not requested to flush the cache,
        # just use the matrix that already exists and return.
        if os.path.exists(raw_matrix_path) and not self._flush_cache:
            pass
        else:
            matrix = matrix_class(self._lab_panel, self._num_episodes)
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
        
        # If processed matrix exists, and the client has not requested to flush
        # the cache, just use the matrix that already exists and return.
        if os.path.exists(processed_matrix_path) and not self._flush_cache:
            pass
        else:
            # Read raw matrix.
            fm_io = FeatureMatrixIO()
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
            # TODO(sbala): Pipe the necessary data into
            # _build_processed_matrix_header, and modularize.
            header = self._build_processed_matrix_header(params)
            fm_io.write_data_frame_to_file(processed_matrix, \
                params['processed_matrix_path'], header)

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
                fm.remove_feature(feature)
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
        y = pd.DataFrame(processed_matrix.pop(outcome_label))
        X = processed_matrix
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

    def _build_processed_matrix_header(self, processed_matrix_path):
        # FeatureMatrixFactory and FeatureMatrixIO expect a list of strings.
        # Each comment below represents the line in the comment.
        header = list()

        file_summary = self._build_file_summary()
        #
        header.append('')
        # Overview:
        header.append('Overview:')
        # This file is a processed version of ___.
        line = 'This file is a post-processed version of %s.' % self._cmm_name_raw
        header.append(line)
        # The outcome label is ___, which is a boolean indicator
        line = 'The outcome label is I(0<=Death.postTimeDays<=28), which is a boolean indicator'
        header.append(line)
        # for whether the patient given by pat_id passed away within 28 days
        line = 'for whether the patient given by pat_id passed away within 28 days'
        header.append(line)
        # of the time index represented by a given row.
        line = 'of the time index represented by a given row.'
        header.append(line)

        processing_summary = self._build_processing_steps_summary()

        #
        line = ''
        header.append(line)
        # Each row represents a decision point (proxied by clinical order).
        line = 'Each row represents a decision point (proxied by clinical order).'
        header.append(line)
        # Each row contains fields summarizing the patient's demographics,
        line = "Each row contains fields summarizing the patient's demographics"
        header.append(line)
        # inpatient admit date, prior vitals, and prior lab results.
        line = 'inpatient admit date, prior vitals, and prior lab results.'
        header.append(line)
        # Most cells in matrix represent a count statistic for an event's
        line = "Most cells in matrix represent a count statistic for an event's"
        header.append(line)
        # occurrence or a difference between an event's time and index_time.
        line = "occurrence or a difference between an event's time and index_time."
        header.append(line)
        #
        header.append('')
        # Fields:
        header.append('Fields:')
        #   pat_id - ID # for patient in the STRIDE data set.
        header.append('  pat_id - ID # for patient in the STRIDE data set.')
        #   index_time - time at which clinical decision was made.
        header.append('  index_time - time at which clinical decision was made.')
        #   death_date - if patient died, date on which they died.
        header.append('  death_date - if patient died, date on which they died.')
        #   AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.
        header.append('  AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.')
        #   Birth.preTimeDays - patient's age in days.
        header.append("  Birth.preTimeDays - patient's age in days.")
        #   [Male|Female].pre - is patient male/female (binary)?
        header.append('  [Male|Female].pre - is patient male/female (binary)?')
        #   [RaceX].pre - is patient race [X]?
        header.append('  [RaceX].pre - is patient race [X]?')
        #   Team.[specialty].[clinical_item] - specialist added to treatment team.
        header.append('  Team.[specialty].[clinical_item] - specialist added to treatment team.')
        #   Comorbidity.[disease].[clinical_item] - disease added to problem list.
        header.append('  Comorbidity.[disease].[clinical_item] - disease added to problem list.')
        #   ___.[flowsheet] - measurements for flowsheet biometrics.
        header.append('  ___.[flowsheet] - measurements for flowsheet biometrics.')
        #       Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,
        header.append('    Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,')
        #           Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.
        header.append('      Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.')
        #   ___.[lab_result] - lab component results.
        header.append('  ___.[lab_result] - lab component results.')
        #       Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,
        header.append('    Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,')
        #           CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,
        header.append('      CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,')
        #           PHV, PO2V, PCO2V
        header.append('      PHV, PO2V, PCO2V')
        #
        header.append('')
        #
        header.append('')

        lab_field_summary = self._build_flowsheet_and_lab_results_field_summary()

        return header

    def _build_file_summary(self, processed_matrix_path, pipeline_file_path):
        summary = list()

        # <file_name.tab>
        matrix_file_name = processed_matrix_path.split('/')[-1]
        header.append(matrix_file_name)
        # Created: <timestamp>
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        header.append('Created: %s' % timestamp)
        # Source: __name__
        header.append('Source: %s' % pipeline_file_path.split('/')[-1])
        # Command: Pipeline()
        if self._icd_list:
            command = 'ConditionMortalityPredictor(%s, %s, %s)' % \
                (self._condition, self._num_patients, self._icd_list)
        else:
            command = 'ConditionMortalityPredictor(%s, %s)' % \
                (self._condition, self._num_patients)
        header.append('Command: %s' % command)

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

    def _build_clinical_item_field_description(self):
        description = list()
        #   [clinical_item] fields may have the following suffixes:
        description.append('  [clinical_item] fields may have the following suffixes:')
        #       ___.pre - how many times has this occurred before order_time?
        description.append('    ___.pre - how many times has this occurred before order_time?')
        #       ___.pre.Xd - how many times has this occurred within X days before index_time?
        description.append('    ___.pre.Xd - how many times has this occurred within X days before index_time?')
        #       ___.preTimeDays - how many days before order_time was last occurrence?
        description.append('    ___.preTimeDays - how many days before order_time was last occurrence?')

        return description

    def _build_flowsheet_and_lab_results_field_description(self):
        description = list()
        #   [flowsheet] and [lab_result] fields may have the following suffixes:
        description.append('  [flowsheet] and [lab_result] fields may have the following suffixes:')
        #       ___.X_Y.count - # of result values between X and Y days of index_time.
        description.append('    ___.X_Y.count - # of result values between X and Y days of index_time.')
        #       ___.X_Y.countInRange - # of result values in normal range.
        description.append('    ___.X_Y.countInRange - # of result values in normal range.')
        #       ___.X_Y.min - minimum result value.
        description.append('    ___.X_Y.min - minimum result value.')
        #       ___.X_Y.max - maximum result value.
        description.append('    ___.X_Y.max - maximum result value.')
        #       ___.X_Y.median - median result value.
        description.append('    ___.X_Y.median - median result value.')
        #       ___.X_Y.std - standard deviation of result values.
        description.append('    ___.X_Y.std - standard deviation of result values.')
        #       ___.X_Y.first - first result value.
        description.append('    ___.X_Y.first - first result value.')
        #       ___.X_Y.last - last result value.
        description.append('    ___.X_Y.last - last result value.')
        #       ___.X_Y.diff - difference between penultimate and proximate values.
        description.append('    ___.X_Y.diff - difference between penultimate and proximate values.')
        #       ___.X_Y.slope - slope between penultimate and proximate values.
        description.append('    ___.X_Y.slope - slope between penultimate and proximate values.')
        #       ___.X_Y.proximate - closest result value to order_time.
        description.append('    ___.X_Y.proximate - closest result value to order_time.')
        #       ___.X_Y.firstTimeDays - time between first and order_time.
        description.append('    ___.X_Y.firstTimeDays - time between first and order_time.')
        #       ___.X_Y.lastTimeDays - time between last and order_time.
        description.append('    ___.X_Y.lastTimeDays - time between last and order_time.')
        #       ___.X_Y.proximateTimeDays - time between proximate and order_time.
        description.append('    ___.X_Y.proximateTimeDays - time between proximate and order_time.')

        return description


    def summarize():
        pass
