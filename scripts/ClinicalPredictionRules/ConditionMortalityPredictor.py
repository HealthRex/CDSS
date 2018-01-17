#!/usr/bin/python
"""
Utility class for generating clinical prediction rules for condition mortality.
"""

from ConditionMortalityMatrix import ConditionMortalityMatrix
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform

class ConditionMortalityPredictor:
    def __init__(self, condition, num_patients, icd_list=None, flush_cache=None):
        self._condition = condition
        self._num_patients = num_patients
        self._icd_list = icd_list

        # self._cpp = ClinicalPredictionRule(condition)

        self._build_raw_feature_matrix()

        # If flush_cache is True, don't cache midpoint results.
        pass

    def _build_cmm_names(self):
        slugified_condition = "-".join(self._condition.split())
        self._build_cmm_name_raw(slugified_condition, self._num_patients)
        self._build_cmm_name_processed(slugified_condition, self._num_patients)

    def _build_cmm_name_raw(self, slugified_condition, num_patients):
        template = '%s-mortality-matrix-%d-pat-raw.tab'
        self._cmm_name_raw = template % (condition, num_patients)

    def _build_cmm_name_processed(self, slugified_condition, num_patients):
        template = '%s-mortality-matrix-%d-pat-processed.tab'
        self._cmm_name_processed = template % (condition, num_patients)

    def _build_raw_feature_matrix(self):
        self._build_cmm_names()
        self._cmm = ConditionMortalityMatrix(self._condition, \
            self._num_patients, self._icd_list)
        self._cmm.write_matrix(self._cmm_name_raw)

    def _process_raw_feature_matrix(self):
        # Read raw CMM.
        self._fm_io = FeatureMatrixIO()
        self._cmm_raw = self._fm_io.read_file_to_data_frame(self._cmm_name_raw)

        # Prune obviously unhelpful fields.
        # In theory, FeatureSelector should be able to prune these, but no
        # reason not to help it out a little bit.
        self._fmt = FeatureMatrixTransform()
        self._fmt.set_input_matrix(self._cmm_raw)
        # Remove Birth.pre (just says 'Was person born?')
        self._fmt.remove_feature('Birth.pre')
        # Remove Race.preTimeDays (just says 'When was person born?')
        self._fmt.remove_feature('RaceWhiteHispanicLatino.preTimeDays')
        self._fmt.remove_feature('RaceWhiteNonHispanicLatino.preTimeDays')
        self._fmt.remove_feature('RaceHispanicLatino.preTimeDays')
        self._fmt.remove_feature('RaceBlack.preTimeDays')
        self._fmt.remove_feature('RaceAsian.preTimeDays')
        self._fmt.remove_feature('RacePacificIslander.preTimeDays')
        self._fmt.remove_feature('RaceNativeAmerican.preTimeDays')
        self._fmt.remove_feature('RaceOther.preTimeDays')
        self._fmt.remove_feature('RaceUnknown.preTimeDays')
        # Remove Sex.preTimeDays (just says 'When was person born?')
        self._fmt.remove_feature('Male.preTimeDays')
        self._fmt.remove_feature('Female.preTimeDays')

        # Impute missing values.
        # [clinical_item].preTimeDays and .postTimeDays default to None.
        # Should impute a high value so that learning treats this event as
        # so distant as to no longer be relevant.
        # Set to 500 years, or 182,500 days.
        FIVE_HUNDRED_YEARS = 182500
        for feature in self._cmm_raw.columns.values:
            if '.preTimeDays' in feature:
                self._fmt.impute(feature, distribution=lambda x: -1*FIVE_HUNDRED_YEARS, \
                    strategy=FEATURE_MATRIX_TRANSFORM.IMPUTE_STRATEGY_DISTRIBUTION)
            elif '.postTimeDays' in feature:
                self._fmt.impute(feature, distribution=lambda x: FIVE_HUNDRED_YEARS, \
                    strategy=FEATURE_MATRIX_TRANSFORM.IMPUTE_STRATEGY_DISTRIBUTION)
        self._fmt.impute(feature='')feature=None, strategy=None, distribution=None

        # Convert non-numeric values to numeric values.
        # Use feature selection to prune 90% of variables.
        pass

    def _build_processed_matrix_header(self):
        pass

    def _train_test_split(self):
        pass

    def _train_predictor(self):
        pass

    def _test_predictor(self):
        pass

    def predict(self):
        pass

    def summarize(self):
        pass

if __name__=="__main__":
    pneumonia = ConditionMortalityPredictor('pneumonia', 10)
