#!/usr/bin/python
"""
Pipeline class for managing end to end training, testing,
and analysis of LabNormality prediction.
"""

import inspect
import os
from pandas import DataFrame
import logging

from medinfo.common.Util import log
from medinfo.ml.FeatureSelector import FeatureSelector
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.ml.SupervisedLearningPipeline import SupervisedLearningPipeline
from scripts.LabTestAnalysis.machine_learning.dataExtraction.LabNormalityMatrix import LabNormalityMatrix

class LabNormalityPredictionPipeline(SupervisedLearningPipeline):
    def __init__(self, lab_panel, num_episodes, use_cache=None):
        SupervisedLearningPipeline.__init__(self, lab_panel, num_episodes, use_cache)

        self._build_raw_feature_matrix()
        self._build_processed_feature_matrix()
        self._train_and_analyze_predictors()

    def _build_raw_matrix_path(self):
        template = '%s-normality-matrix-%d-episodes-raw.tab'
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_matrix_path(self, template, \
            pipeline_file_name)

    def _build_raw_feature_matrix(self):
        raw_matrix_path = self._build_raw_matrix_path()
        matrix_class = LabNormalityMatrix
        SupervisedLearningPipeline._build_raw_feature_matrix(self, matrix_class, \
            raw_matrix_path)

    def _build_processed_matrix_path(self):
        template = '%s-normality-matrix-%d-episodes-processed.tab'
        pipeline_file_path = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_matrix_path(self, template, \
            pipeline_file_path)

    def _build_processed_feature_matrix(self):
        # Define parameters for processing steps.
        params = {}
        raw_matrix_path = self._build_raw_matrix_path()
        processed_matrix_path = self._build_processed_matrix_path()
        features_to_add = {}
        imputation_strategies = {}

        features_to_remove = [
            'pat_id', 'order_time', 'order_proc_id',
            'proc_code', 'abnormal_panel',
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
            'RaceUnknown.preTimeDays'
        ]
        outcome_label = 'all_components_normal'
        selection_problem = FeatureSelector.CLASSIFICATION
        selection_algorithm = FeatureSelector.RECURSIVE_ELIMINATION
        percent_features_to_select = 0.05
        matrix_class = LabNormalityMatrix
        pipeline_file_path = inspect.getfile(inspect.currentframe())
        data_overview = [
            # Overview:
            'Overview',
            # The outcome label is ___.
            'The outcome label is %s.' % outcome_label,
            # %s is a boolean indicator which summarizes whether all components
            '%s is a boolean indicator which summarizes whether all components ' % outcome_label,
            # in the lab panel order represented by a given row are normal.
            'in the lab panel order represented by a given row are normal.',
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

        # Bundle parameters into single object to be unpacked in SLP.
        params['raw_matrix_path'] = raw_matrix_path
        params['processed_matrix_path'] = processed_matrix_path
        params['features_to_add'] = features_to_add
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

    def _train_and_analyze_predictors(self):
        problem = SupervisedLearningPipeline.CLASSIFICATION
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        data_dir = SupervisedLearningPipeline._fetch_data_dir_path(self, pipeline_file_name)
        meta_report = None
        fm_io = FeatureMatrixIO()
        for algorithm in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            SupervisedLearningPipeline._train_predictor(self, problem, algorithm, [0, 1])
            pipeline_prefix = '%s-normality-prediction-%s' % (self._var, algorithm)
            dest_dir = '/'.join([data_dir, algorithm])
            # If dest_dir does not exist, make it.
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            SupervisedLearningPipeline._analyze_predictor(self, dest_dir, pipeline_prefix)
            if meta_report is None:
                meta_report = fm_io.read_file_to_data_frame('/'.join([dest_dir, '%s-report.tab' % pipeline_prefix]))
            else:
                algorithm_report = fm_io.read_file_to_data_frame('/'.join([dest_dir, '%s-report.tab' % pipeline_prefix]))
                log.debug('algorithm_report: %s' % algorithm_report)
                meta_report = meta_report.append(algorithm_report)

        header = ['LabNormalityPredictionPipeline("%s", 10000)' % self._var]
        fm_io.write_data_frame_to_file(meta_report, \
            '/'.join([data_dir, '%s-normality-prediction-report.tab' % self._var]), \
            header)

if __name__ == '__main__':
    log.level = logging.DEBUG
    LAB_PANELS = [
        # 'LABA1C', 
        'LABLAC', 'LABMB', 'LABMETB', 'LABMETC'
        # "LABA1C", "LABABG", "LABBLC", "LABBLC2", "LABCAI",
        # "LABCBCD", "LABCBCO", "LABHFP", "LABLAC", "LABMB",
        # "LABMETB", "LABMETC", "LABMGN", "LABNTBNP", "LABPCG3",
        # "LABPCTNI", "LABPHOS", "LABPOCGLU", "LABPT", "LABPTT",
        # "LABROMRS", "LABTNI", "LABTYPSNI", "LABUA", "LABUAPRN",
        # "LABURNC", "LABVANPRL", "LABVBG"
    ]
    for panel in LAB_PANELS:
        LabNormalityPredictionPipeline(panel, 10000, use_cache=True)
