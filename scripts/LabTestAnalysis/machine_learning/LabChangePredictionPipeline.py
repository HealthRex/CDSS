#!/usr/bin/python
"""
Pipeline class for managing end to end training, testing,
and analysis of LabChange prediction.
"""

import inspect
import os
from pandas import DataFrame, Series
from sklearn.externals import joblib
import logging

from medinfo.common.Util import log
from medinfo.ml.FeatureSelector import FeatureSelector
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.ml.BifurcatedSupervisedClassifier import BifurcatedSupervisedClassifier
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.ml.SupervisedLearningPipeline import SupervisedLearningPipeline
from scripts.LabTestAnalysis.machine_learning.dataExtraction.LabChangeMatrix import LabChangeMatrix

class LabChangePredictionPipeline(SupervisedLearningPipeline):
    def __init__(self, change_params, lab_panel, num_episodes, use_cache=None):
        SupervisedLearningPipeline.__init__(self, lab_panel, num_episodes, use_cache)
        self._change_params = (change_params)
        log.debug('change_params: %s' % self._change_params)

        self._build_raw_feature_matrix()
        self._build_processed_feature_matrix()
        self._train_and_analyze_predictors()

    def _build_model_dump_path(self, algorithm):
        template = '%s' + '-change-%s-model.pkl' % algorithm
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_model_dump_path(self, template, \
            pipeline_file_name)

    def _build_raw_matrix_path(self):
        template = '%s-change-matrix-%d-episodes-raw.tab'
        pipeline_file_name = inspect.getfile(inspect.currentframe())

        return '/Users/raikens/Documents/research/HealthRex/Data/LabChangeMatrices/LABCK-panel-10000-episodes-values-18234.0-sec_prev_measurement.tab'

    def _build_raw_feature_matrix(self):
        raw_matrix_path = self._build_raw_matrix_path()
        matrix_class = LabChangeMatrix
        SupervisedLearningPipeline._build_raw_feature_matrix(self, matrix_class, \
            raw_matrix_path)

    def _build_processed_matrix_path(self, raw_matrix_path):
        template = '%s-change-matrix-%d-episodes-processed.tab'
        pipeline_file_path = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_matrix_path(self, template, \
            pipeline_file_path)

    def _build_processed_feature_matrix(self):
        # Define parameters for processing steps.
        params = {}
        #TODO (raikens): set to use cache??
        raw_matrix_path = self._build_raw_matrix_path()
        processed_matrix_path = self._build_processed_matrix_path(raw_matrix_path)

        log.debug('params: %s' % params)

        features_to_add = {'change': [self._change_params]}
        imputation_strategies = {
        }

        features_to_remove = [
            'pat_id', 'order_time', 'order_proc_id', 'ord_num_value',
            'proc_code', 'abnormal_panel', 'all_components_normal',
            'num_normal_components', 'Birth.pre',
            'Male.preTimeDays', 'Female.preTimeDays',
            'RaceWhiteHispanicLatino.preTimeDays',
            'RaceWhiteNonHispanicLatino.preTimeDays',
            'RaceHispanicLatino.preTimeDays',
            'RaceAsian.preTimeDays',
            'RaceBlack.preTimeDays',
            'RacePacificIslander.preTimeDays',
            'RaceNativeAmerican.preTimeDays',
            'RaceOther.preTimeDays',
            'RaceUnknown.preTimeDays',
            'Death.post',
            'Death.postTimeDays',
            'num_components'
        ]
        features_to_keep = [
            # Keep the # of times it's been ordered in past, even if low info.
            '%s.pre' % self._var
        ]
        outcome_label = 'change_yn'
        selection_problem = FeatureSelector.CLASSIFICATION
        selection_algorithm = FeatureSelector.RECURSIVE_ELIMINATION
        percent_features_to_select = 0.05
        matrix_class = LabChangeMatrix
        pipeline_file_path = inspect.getfile(inspect.currentframe())
        data_overview = [
            # Overview:
            'Overview',
            # The outcome label is ___.
            'The outcome label is %s.' % outcome_label,
            # %s is a boolean indicator which summarizes whether all components
            '%s is a boolean indicator which summarizes whether the lab test ' % outcome_label,
            # in the lab panel order represented by a given row are normal.
            'result has changed compared to the previous measurement.',
            # Each row represents a unique lab panel order.
            'Each row represents a unique lab panel order.',
            # Each row contains fields summarizing the patient's demographics,
            "Each row contains fields summarizing the patient's demographics",
            # inpatient admit date, prior vitals, and prior lab results.
            'inpatient admit date, prior vitals, and prior lab results.',
            # Most cells in matrix represent a count statistic for an event's
            "Most cells in matrix represent a count statistic for an event's",
            # occurrence or a difference between an event's time and index_time.
            "occurrence or a difference between an event's time and index_time.",
        ]

        # Bundle parameters into single object
        params['raw_matrix_path'] = raw_matrix_path
        params['processed_matrix_path'] = processed_matrix_path
        params['features_to_add'] = features_to_add
        params['features_to_keep'] = features_to_keep
        params['imputation_strategies'] = imputation_strategies
        params['features_to_remove'] = features_to_remove
        params['outcome_label'] = outcome_label
        params['selection_problem'] = selection_problem
        params['selection_algorithm'] = selection_algorithm
        params['percent_features_to_select'] = percent_features_to_select
        params['matrix_class'] = matrix_class
        params['pipeline_file_path'] = pipeline_file_path
        params['data_overview'] = data_overview

        # Defer processing logic to SupervisedLearningPipeline.
        SupervisedLearningPipeline._build_processed_feature_matrix(self, params)

    def _fetch_data_dir_path(self, pipeline_module_path):
        # e.g. app_dir = CDSS/scripts/LabTestAnalysis/machine_learning
        app_dir = os.path.dirname(os.path.abspath(pipeline_module_path))

        # e.g. data_dir = CDSS/scripts/LabTestAnalysis/machine_learning/data
        parent_dir_list = app_dir.split('/')
        parent_dir_list.append('data')

        # make subdirectory based on lab test name and change defs
        # e.g. data_dir =  CDSS/scripts/LabTestAnalysis/machine_learning/data/LABCK/change_interval_05
        parent_dir_list.append(self._var)
        paramstr = str(self._change_params['param']).replace('.','')
        change_def = 'change_%s_%s' % (self._change_params['method'], paramstr)
        parent_dir_list.append(change_def)
        data_dir = '/'.join(parent_dir_list)

        # If data_dir does not exist, make it.
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        return data_dir

    def _train_and_analyze_predictors(self):
        log.info('Training and analyzing predictors...')
        problem = SupervisedLearningPipeline.CLASSIFICATION
        meta_report = None
        fm_io = FeatureMatrixIO()

        # Build paths for output.
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        data_dir = self._fetch_data_dir_path(pipeline_file_name)

        # Test BifurcatedSupervisedClassifier and SupervisedClassifier.
        algorithms_to_test = list()
        algorithms_to_test.extend(SupervisedClassifier.SUPPORTED_ALGORITHMS)
        for algorithm in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            pass # TODO:(raikens) something in the BifurcatedSupervisedClassifier pipeline is crashing
            #algorithms_to_test.append('bifurcated-%s' % algorithm)
        log.debug('algorithms_to_test: %s' % algorithms_to_test)

        # Train and analyse algorithms.
        for algorithm in algorithms_to_test:
            log.info('Training and analyzing %s...' % algorithm)
            # If report_dir does not exist, make it.
            report_dir = '/'.join([data_dir, algorithm])
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            log.debug('report_dir: %s' % report_dir)

            # Define hyperparams.
            hyperparams = {}
            hyperparams['algorithm'] = algorithm
            hyperparams['hyperparam_strategy'] = SupervisedClassifier.EXHAUSTIVE_SEARCH
            hyperparams['max_iter'] = 1024

            # If bifurcated algorithm, define bifurcator.
            if 'bifurcated' in algorithm:
                # bifrucator = LAB.pre == 0
                hyperparams['bifurcator'] = '%s.pre' % self._var
                hyperparams['bifurcation_strategy'] = BifurcatedSupervisedClassifier.EQUAL
                hyperparams['bifurcation_value'] = 0
                hyperparams['bifurcated'] = True

            # Train classifier.
            predictor_path = self._build_model_dump_path(algorithm)
            if os.path.exists(predictor_path) and 'bifurcated' not in algorithm:
                log.debug('Loading model from disk...')
                # TODO(sbala): Fix loblib.load so that it works for bifurcated
                # supervised classifiers.
                self._predictor = joblib.load(predictor_path)
                self._features = self._X_train.columns
                status = SupervisedClassifier.TRAINED
            else:
                status = SupervisedLearningPipeline._train_predictor(self, problem, [0, 1], hyperparams)

            # If failed to train, write an error report.
            y_train_counts = self._y_train[self._y_train.columns[0]].value_counts()
            y_test_counts = self._y_test[self._y_test.columns[0]].value_counts()
            if status == SupervisedClassifier.INSUFFICIENT_SAMPLES:
                # Skip all analysis and reporting.
                # This will be true for all algorithms, so just return.
                # Build error report.
                algorithm_report = DataFrame(
                    {
                    'lab_panel': [self._var],
                    'algorithm': [algorithm],
                    'error': [status],
                    'y_train.value_counts()': [y_train_counts.to_dict()],
                    'y_test.value_counts()': [y_test_counts.to_dict()]
                    },
                    columns=[
                        'lab_panel', 'algorithm', 'error',
                        'y_train.value_counts()', 'y_test.value_counts()'
                    ]
                )
                header = ['LabChangePredictionPipeline("%s", 10000)' % self._var]
                # Write error report.
                fm_io.write_data_frame_to_file(algorithm_report, \
                    '/'.join([report_dir, '%s-change-prediction-report.tab' % (self._var)]), \
                    header)
            # If successfully trained, append to a meta report.
            elif status == SupervisedClassifier.TRAINED:
                pipeline_prefix = '%s-change-prediction-%s' % (self._var, algorithm)
                SupervisedLearningPipeline._analyze_predictor(self, report_dir, pipeline_prefix)
                if meta_report is None:
                    meta_report = fm_io.read_file_to_data_frame('/'.join([report_dir, '%s-report.tab' % pipeline_prefix]))
                else:
                    algorithm_report = fm_io.read_file_to_data_frame('/'.join([report_dir, '%s-report.tab' % pipeline_prefix]))
                    log.debug('algorithm_report: %s' % algorithm_report)
                    meta_report = meta_report.append(algorithm_report)
                # Write predictor to disk.
                predictor = SupervisedLearningPipeline.predictor(self)
                predictor_path = self._build_model_dump_path(algorithm)
                joblib.dump(predictor, predictor_path)

        # After building per-algorithm reports, write to meta report.
        # Note that if there were insufficient samples to build any of the
        # algorithms, then meta_report will still be None.
        if meta_report is not None:
            header = ['LabChangePredictionPipeline("%s", 7183)' % self._var]
            fm_io.write_data_frame_to_file(meta_report, \
                '/'.join([data_dir, '%s-change-prediction-report.tab' % self._var]), header)

if __name__ == '__main__':
    log.level = logging.DEBUG
    labs_to_test = ['LABCK']
    change_params = {}
    change_params['method'] = 'percent'
    change_params['param'] = 0.15
    change_params['feature_old'] = 'CK.-14_0.last'
    change_params['feature_new'] = 'ord_num_value'

    #params_to_test = [0.5, 0.25, 0.15, 0.10, 0.05]
    params_to_test = [0.10, 0.05]

    for panel in labs_to_test:
        for param in params_to_test:
            LabChangePredictionPipeline(change_params, panel, 7183, use_cache=True)
