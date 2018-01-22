#!/usr/bin/python
"""
Pipeline class for managing end to end training, testing,
and analysis of LabNormality prediction.
"""

import inspect
import os

class LabNormalityPredictionPipeline:
    def __init__(self, lab_panel, outcome_label, num_episodes, flush_cache=None):
        self._raw_matrix = None
        self._processed_matrix = None
        self._predictor = None

        self._eliminated_features = list()

        # Parse arguments.
        self._lab_panel = lab_panel
        self._outcome_label = outcome_label
        self._num_episodes = num_episodes
        # Determine whether the cache should be flushed or used
        # at each successive step in the pipeline.
        self._flush_cache = True if flush_cache is None else False

        # If raw feature matrix does not exist, build it.
        self._build_raw_feature_matrix()

        pass

    def _build_raw_matrix_name(self):
        slugified_lab_panel = '-'.join(self._lab_panel.split())
        template = '%s-normality-matrix-%d-epi-raw.tab'
        raw_matrix_name = template % (slugified_lab_panel, self._num_episodes)
        return raw_matrix_name

    def _fetch_data_dir_path(self):
        # app_dir = CDSS/scripts/LabTestAnalysis/machine_learning
        app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # data_dir = CDSS/scripts/LabTestAnalysis/data
        lab_analysis_dir_list = app_dir.split('/')[:-1]
        lab_analysis_dir_list.append('data')
        data_dir = '/'.join(lab_analysis_dir_list)
        return data_dir

    def _build_raw_feature_matrix(self):
        # Build path for raw matrix file.
        data_dir = self._fetch_data_dir_path()
        raw_matrix_name = self._build_raw_matrix_name()
        raw_matrix_path = '/'.join([data_dir, raw_matrix_name])

        # If raw matrix exists, and client has not requested to flush the cache,
        # just use the matrix that already exists and return.
        if os.path.exists(raw_matrix_path) and not self._flush_cache:
            continue
        else:
            lnm = LabNormalityMatrix(self._lab_panel, self._num_episodes)
            lnm.write_matrix(raw_matrix_path)

    def _build_processed_matrix_name(self):
        slugified_lab_panel = '_'.join(self._lab_panel.split())
        template = '%s-normality-matrix-%d-epi-processed.tab'
        processed_matrix_name = template % (slugified_lab_panel, self._num_episodes)
        return processed_matrix_name

    def _process_raw_feature_matrix(self):
        # Buid path for matrix files.
        data_dir = self._fetch_data_dir_path()
        raw_matrix_name = self._build_raw_matrix_name()
        processed_matrix_name = self._build_processed_matrix_name()
        processed_matrix_path = '/'.join([data_dir, processed_matrix_name])

        # If processed matrix exists, and the client has not requested to flush
        # the cache, just use the matrix that already exists and return.
        if os.path.exists(processed_matrix_path) and not self._flush_cache:
            continue
        else:
            # Read raw matrix.
            fm_io = FeatureMatrixIO()
            raw_matrix = fm_io.read_file_to_data_frame(raw_matrix_name)

            # Add and remove features to processed matrix.
            fmt = FeatureMatrixTransform()
            fmt.set_input_matrix(raw_matrix)
            self._add_features(fmt)
            self._remove_features(fmt)
            fmt.drop_duplicate_rows()
            processed_matrix = fmt.fetch_matrix()

            # Divide processed_matrix into training and test data.
            # This must happen before feature selection so that we don't
            # accidentally learn information from the test data.
            self._train_test_split()
            self._select_features()
        pass

    def _add_features(self, fmt):
        pass

    def _remove_features(self, fmt):
        self._LOW_SIGNAL_FEATURES = [
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
        for feature in LOW_SIGNAL_FEATURES:
            fmt.remove_feature(feature)

    def _train_test_split(self, processed_matrix):
        y = pd.DataFrame(processed_matrix.pop(self._outcome_label))
        X = processed_matrix
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(X, y, shuffle=False)

    def _select_features(self, problem, num_features_to_select):
        # Use FeatureSelector to prune all but 1% of variables.
        fs = FeatureSelector(algorithm=FeatureSelector.RECURSIVE_ELIMINATION, \
            problem=problem)

        fs.set_input_matrix(self._X_train, column_or_1d(self._y_train))
        fs.select(k=num_features_to_select)

        # Enumerate eliminated features pre-transformation.
        self._feature_ranks = fs.compute_ranks()
        for i in range(len(self._feature_ranks)):
            if self._feature_ranks[i] > num_features_to_select:
                self._eliminated_features.append(self._X_train.columns[i])

        self._X_train = fs.transform_matrix(self._X_train)
        self._X_test = fs.transform_matrix(self._X_test)

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
