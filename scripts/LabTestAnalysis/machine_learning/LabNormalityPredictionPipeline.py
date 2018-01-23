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
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_matrix_path(self, template, \
            pipeline_file_name)

    def _process_raw_feature_matrix(self):
        # Buid paths for matrix files.
        raw_matrix_path = self._build_raw_matrix_path()
        processed_matrix_path = self._build_processed_matrix_path()

        # If processed matrix exists, and the client has not requested to flush
        # the cache, just use the matrix that already exists and return.
        if os.path.exists(processed_matrix_path) and not self._flush_cache:
            pass
        else:
            # Read raw matrix.
            fm_io = FeatureMatrixIO()
            raw_matrix = fm_io.read_file_to_data_frame(raw_matrix_path)

            # Initialize FMT.
            fmt = FeatureMatrixTransform()
            fmt.set_input_matrix(raw_matrix)

            # Add features.
            FEATURES_TO_ADD = {}
            SupervisedLearningPipeline._add_features(self, fmt, features_to_add)

            # Impute data and remove features.
            IMPUTATION_STRATEGIES = {}
            FEATURES_TO_REMOVE = [
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
            SupervisedLearningPipeline._impute_data(self, fmt, raw_matrix, \
                IMPUTATION_STRATEGIES, FEATURES_TO_REMOVE)
            SupervisedLearningPipeline._remove_features(self, fmt, \
                FEATURES_TO_REMOVE)
            fmt.drop_duplicate_rows()

            processed_matrix = fmt.fetch_matrix()

            # Divide processed_matrix into training and test data.
            # This must happen before feature selection so that we don't
            # accidentally learn information from the test data.
            self._train_test_split(processed_matrix)
            self._select_features()

            # Write processed matrix to new file.
            self._build_processed_feature_matrix()

    def _build_processed_feature_matrix(self):
        processed_matrix_path = self._build_processed_matrix_path()
        SupervisedLearningPipeline._build_processed_feature_matrix(self, processed_matrix_path)

    def _train_test_split(self, processed_matrix):
        outcome_label = 'all_components_normal'
        SupervisedLearningPipeline._train_test_split(self, processed_matrix, \
            outcome_label)

    def _select_features(self):
        problem = FeatureSelector.CLASSIFICATION
        algorithm = FeatureSelector.RECURSIVE_ELIMINATION
        # Use FeatureSelector to prune all but 1% of variables.
        percent = 0.01
        SupervisedLearningPipeline._select_features(self, problem, percent, algorithm)

    def _train_predictor():
        pass

    def _test_predictor():
        pass

    def _analyze_predictor():
        pass

    def _summarize_pipeline():
        pass

if __name__ == '__main__':
    lnpp = LabNormalityPredictionPipeline('LABMETB', 10)
