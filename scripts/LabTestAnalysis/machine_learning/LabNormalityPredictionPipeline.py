#!/usr/bin/python
"""
Pipeline class for managing end to end training, testing,
and analysis of LabNormality prediction.
"""

import inspect
import os

from medinfo.ml.SupervisedLearningPipeline import SupervisedLearningPipeline
from scripts.LabTestAnalysis.machine_learning.dataExtraction.LabNormalityMatrix import LabNormalityMatrix

class LabNormalityPredictionPipeline(SupervisedLearningPipeline):
    def __init__(self, lab_panel, num_episodes, use_cache=None):
        SupervisedLearningPipeline.__init__(self, lab_panel, num_episodes, use_cache)

        # Parse arguments.
        self._lab_panel = lab_panel
        self._num_episodes = num_episodes
        # Determine whether the cache should be flushed or used
        # at each successive step in the pipeline.
        self._flush_cache = True if use_cache is None else False

        self._build_raw_feature_matrix()

        pass

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
        template = '%s-normality-matrix-%d-epi-processed.tab'
        pipeline_file_path = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_matrix_path(self, template, \
            pipeline_file_path)

    def _build_processed_feature_matrix(self):
        # Buid paths for matrix files.
        raw_matrix_path = self._build_raw_matrix_path()
        processed_matrix_path = self._build_processed_matrix_path()

        # Define parameters for processing steps.
        params = {}
        features_to_add = {}
        imputation_strategies = {}
        features_to_remove = [
            'index_time', 'Birth.pre',
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
        percent_features_to_select = 0.01
        matrix_class = LabNormalityMatrix
        pipeline_file_name = inspect.getfile(inspect.currentframe())

        # Bundle parameters into single object to be unpacked in SLP.
        params['features_to_add'] = features_to_add
        params['imputation_strategies'] = imputation_strategies
        params['features_to_remove'] = features_to_remove
        params['outcome_label'] = outcome_label
        params['selection_problem'] = selection_problem
        params['selection_algorithm'] = selection_algorithm
        params['percent_features_to_select'] = percent_features_to_select
        params['matrix_class'] = matrix_class
        params['pipeline_file_path'] = pipeline_file_path

        # Defer processing logic to SupervisedLearningPipeline.
        SupervisedLearningPipeline._build_processed_feature_matrix(self, params)

    def _train_predictor():
        pass

    def _test_predictor():
        pass

    def _analyze_predictor():
        pass

    def _summarize_pipeline():
        pass

if __name__ == '__main__':
    print inspect.getfile(inspect.currentframe())
    # lnpp = LabNormalityPredictionPipeline('LABMETB', 10)
