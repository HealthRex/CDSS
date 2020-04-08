#!/usr/bin/python
"""
Utility class for generating clinical prediction rules for condition mortality.
"""

import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d

from ConditionMortalityMatrix import ConditionMortalityMatrix
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.ml.FeatureSelector import FeatureSelector
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

class ConditionMortalityPredictor:
    def __init__(self, condition, num_patients, icd_list=None, use_cache=None):
        self._condition = condition
        self._num_patients = num_patients
        self._icd_list = icd_list

        self._FEATURES_TO_REMOVE = [
            'index_time',
            'death_date', 'Death.post',
            'Death.postTimeDays', 'Birth.pre',
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
        self._eliminated_features = list()

        self._build_cmm_names()
        if use_cache is None:
            self._build_raw_feature_matrix()
        print('Processing raw feature matrix...')
        self._process_raw_feature_matrix()
        print('Training predictor...')
        self._train_predictor()
        print('Testing predictor...')
        self._test_predictor()

    def _build_cmm_names(self):
        slugified_condition = "-".join(self._condition.split())
        self._build_cmm_name_raw(slugified_condition, self._num_patients)
        self._build_cmm_name_processed(slugified_condition, self._num_patients)

    def _build_cmm_name_raw(self, slugified_condition, num_patients):
        template = '%s-mortality-matrix-%d-pat-raw.tab'
        self._cmm_name_raw = template % (slugified_condition, num_patients)

    def _build_cmm_name_processed(self, slugified_condition, num_patients):
        template = '%s-mortality-matrix-%d-pat-processed.tab'
        self._cmm_name_processed = template % (slugified_condition, num_patients)

    def _build_raw_feature_matrix(self):
        self._cmm = ConditionMortalityMatrix(self._condition, \
            self._num_patients, self._cmm_name_raw, self._icd_list)

    def _process_raw_feature_matrix(self):
        # Read raw CMM.
        self._fm_io = FeatureMatrixIO()
        print('Reading raw matrix...')
        self._cmm_raw = self._fm_io.read_file_to_data_frame(self._cmm_name_raw)

        # Add and remove features to _cmm_processed.
        self._fmt = FeatureMatrixTransform()
        self._fmt.set_input_matrix(self._cmm_raw)
        print('Adding features...')
        self._add_features()
        print('Imputing data...')
        self._impute_data()
        self._remove_features()
        self._fmt.drop_duplicate_rows()
        self._cmm_processed = self._fmt.fetch_matrix()

        # Divide _cmm_processed into training and test data.
        # This must happen before feature selection so that we don't
        # accidentally learn information from the test data.
        self._train_test_split()
        print('Selecting features...')
        self._select_features()

        # Write output to new matrix.
        train = self._y_train.join(self._X_train)
        test = self._y_test.join(self._X_test)
        self._cmm_processed = train.append(test)

        header = self._build_processed_matrix_header()

        self._fm_io.write_data_frame_to_file(self._cmm_processed, self._cmm_name_processed, header)

    def _build_processed_matrix_header(self):
        # FeatureMatrixFactory and FeatureMatrixIO expect a list of strings.
        # Each comment below represents the line in the comment.
        header = list()

        # <file_name.tab>
        file_name = self._cmm_name_processed
        header.append(file_name)
        # Created: <timestamp>
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        header.append('Created: %s' % timestamp)
        # Source: __name__
        header.append('Source: %s' % __name__)
        # Command: ConditionMortalityMatrix()
        if self._icd_list:
            command = 'ConditionMortalityPredictor(%s, %s, %s)' % \
                (self._condition, self._num_patients, self._icd_list)
        else:
            command = 'ConditionMortalityPredictor(%s, %s)' % \
                (self._condition, self._num_patients)
        header.append('Command: %s' % command)
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
        # This matrix is the result of the following processing steps on the raw matrix:
        line = 'This matrix is the result of the following processing steps on the raw matrix:'
        header.append(line)
        #   (1) Imputing missing values with the mean value of each column.
        line = '  (1) Imputing missing values with the mean value of each column.'
        header.append(line)
        #   (2) Manually removing low-information features:
        line = '  (2) Manually removing low-information features:'
        header.append(line)
        #       ___
        line = '      %s' % str(self._FEATURES_TO_REMOVE)
        header.append(line)
        #   (3) Algorithmically selecting the top 100 features via recursive feature elimination.
        line = '  (3) Algorithmically selecting the top 100 features via recursive feature elimination.'
        header.append(line)
        #       The following features were eliminated.
        line = '      The following features were eliminated:'
        header.append(line)
        # List all features with rank >100.
        line = '        %s' % str(self._eliminated_features)
        header.append(line)
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
        #   [clinical_item] fields may have the following suffixes:
        header.append('  [clinical_item] fields may have the following suffixes:')
        #       ___.pre - how many times has this occurred before order_time?
        header.append('    ___.pre - how many times has this occurred before order_time?')
        #       ___.pre.Xd - how many times has this occurred within X days before index_time?
        header.append('    ___.pre.Xd - how many times has this occurred within X days before index_time?')
        #       ___.preTimeDays - how many days before order_time was last occurrence?
        header.append('    ___.preTimeDays - how many days before order_time was last occurrence?')
        #
        header.append('')
        #   [flowsheet] and [lab_result] fields may have the following suffixes:
        header.append('  [flowsheet] and [lab_result] fields may have the following suffixes:')
        #       ___.X_Y.count - # of result values between X and Y days of index_time.
        header.append('    ___.X_Y.count - # of result values between X and Y days of index_time.')
        #       ___.X_Y.countInRange - # of result values in normal range.
        header.append('    ___.X_Y.countInRange - # of result values in normal range.')
        #       ___.X_Y.min - minimum result value.
        header.append('    ___.X_Y.min - minimum result value.')
        #       ___.X_Y.max - maximum result value.
        header.append('    ___.X_Y.max - maximum result value.')
        #       ___.X_Y.median - median result value.
        header.append('    ___.X_Y.median - median result value.')
        #       ___.X_Y.std - standard deviation of result values.
        header.append('    ___.X_Y.std - standard deviation of result values.')
        #       ___.X_Y.first - first result value.
        header.append('    ___.X_Y.first - first result value.')
        #       ___.X_Y.last - last result value.
        header.append('    ___.X_Y.last - last result value.')
        #       ___.X_Y.diff - difference between penultimate and proximate values.
        header.append('    ___.X_Y.diff - difference between penultimate and proximate values.')
        #       ___.X_Y.slope - slope between penultimate and proximate values.
        header.append('    ___.X_Y.slope - slope between penultimate and proximate values.')
        #       ___.X_Y.proximate - closest result value to order_time.
        header.append('    ___.X_Y.proximate - closest result value to order_time.')
        #       ___.X_Y.firstTimeDays - time between first and order_time.
        header.append('    ___.X_Y.firstTimeDays - time between first and order_time.')
        #       ___.X_Y.lastTimeDays - time between last and order_time.
        header.append('    ___.X_Y.lastTimeDays - time between last and order_time.')
        #       ___.X_Y.proximateTimeDays - time between proximate and order_time.
        header.append('    ___.X_Y.proximateTimeDays - time between proximate and order_time.')

        return header

    def _train_predictor(self):
        self._predictor = SupervisedClassifier(algorithm=SupervisedClassifier.REGRESS_AND_ROUND)
        self._predictor.train(self._X_train, column_or_1d(self._y_train))

    def _train_test_split(self):
        y = pd.DataFrame(self._cmm_processed.pop('I(0<=Death.postTimeDays<=28)'))
        # Without this line, sklearn complains about the format of y.
        # "DataConversionWarning: A column-vector y was passed when a 1d array
        #   was expected. Please change the shape of y to (n_samples, ), for
        #   example using ravel()."
        # Note that this turns y into a numpy array, so need to cast back.
        # y = y.values.ravel()
        X = self._cmm_processed
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(X, y, shuffle=False)

    def _impute_data(self):
        # Impute missing values with mean value.
        for feature in self._cmm_raw.columns.values:
            if feature in self._FEATURES_TO_REMOVE:
                continue
            # If all values are null, just remove the feature.
            # Otherwise, imputation will fail (there's no mean value),
            # and sklearn will ragequit.
            if self._cmm_raw[feature].isnull().all():
                self._fmt.remove_feature(feature)
                self._eliminated_features.append(feature)
            # Only try to impute if some of the values are null.
            elif self._cmm_raw[feature].isnull().any():
                # TODO(sbala): Impute all time features with non-mean value.
                self._fmt.impute(feature)

    def _add_features(self):
        # Add threshold feature indicating whether death date
        # is within 28 days of index time.
        self._fmt.add_threshold_feature('Death.postTimeDays', lower_bound=0, upper_bound=28)

    def _remove_features(self):
        # Prune obviously unhelpful fields.
        # In theory, FeatureSelector should be able to prune these, but no
        # reason not to help it out a little bit.
        for feature in self._FEATURES_TO_REMOVE:
            self._fmt.remove_feature(feature)

    def _select_features(self):
        # Use FeatureSelector to prune all but 100 variables.
        fs = FeatureSelector(algorithm=FeatureSelector.RECURSIVE_ELIMINATION, \
            problem=FeatureSelector.CLASSIFICATION)

        fs.set_input_matrix(self._X_train, column_or_1d(self._y_train))
        num_features_to_select = int(0.01*len(self._X_train.columns.values))
        fs.select(k=num_features_to_select)

        # Enumerate eliminated features pre-transformation.
        self._feature_ranks = fs.compute_ranks()
        for i in range(len(self._feature_ranks)):
            if self._feature_ranks[i] > num_features_to_select:
                self._eliminated_features.append(self._X_train.columns[i])

        self._X_train = fs.transform_matrix(self._X_train)
        self._X_test = fs.transform_matrix(self._X_test)

    def _test_predictor(self):
        self._accuracy = self._predictor.compute_accuracy(self._X_test, self._y_test)

    def predict(self, X):
        return self._predictor.predict(X)

    def summarize(self):
        summary_lines = list()

        # Condition: condition
        condition = self._condition
        line = 'Condition: %s' % condition
        summary_lines.append(line)

        # Algorithm: SupervisedClassifier(algorithm)
        algorithm = 'SupervisedClassifier(REGRESS_AND_ROUND)'
        line = 'Algorithm: %s' % algorithm
        summary_lines.append(line)

        # Train/Test Size: training_size, test_size
        training_size = self._X_train.shape[0]
        test_size = self._X_test.shape[0]
        line = 'Train/Test Size: %s/%s' % (training_size, test_size)
        summary_lines.append(line)

        # Model: sig_features
        coefs = self._predictor.coefs()
        cols = self._X_train.columns
        sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
        linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
        line = 'Model: logistic(%s)' % linear_model
        summary_lines.append(line)

        # Baseline Episode Mortality: episode_mortality
        counts = self._y_test[self._y_test.columns[0]].value_counts()
        line = 'Baseline Episode Mortality: %s/%s' % (counts[1], test_size)
        summary_lines.append(line)

        # AUC: auc
        auc = self._predictor.compute_roc_auc(self._X_test, self._y_test)
        line = 'AUC: %s' % auc
        summary_lines.append(line)
        # Accuracy: accuracy
        line = 'Accuracy: %s' % self._accuracy
        summary_lines.append(line)

        return '\n'.join(summary_lines)

if __name__=="__main__":
    conditions = ['pneumonia', 'tuberculosis', 'meningitis', 'influenza',
        'nephritis', 'diabetes'
        # 'tetanus' – there aren't any tetanus mortality events.
        ]
    for condition in conditions:
        predictor = ConditionMortalityPredictor(condition, 1000)
        print(condition.summarize())
