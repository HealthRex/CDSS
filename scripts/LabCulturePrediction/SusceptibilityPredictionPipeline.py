#!/usr/bin/python
"""
Pipeline class for managing end to end training, testing,
and analysis of Antibiotic Suseptibiltiy prediction.
"""

import argparse
import inspect
import os
import pandas as pd
from pandas import DataFrame, Series
from sklearn.externals import joblib
from sklearn.metrics import make_scorer, average_precision_score
import logging

from medinfo.common.Util import log
from medinfo.ml.FeatureSelector import FeatureSelector
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.ml.BifurcatedSupervisedClassifier import BifurcatedSupervisedClassifier
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.ml.SupervisedLearningPipeline import SupervisedLearningPipeline
from LabCultureMatrix import LabCultureMatrix

class SusceptibilityPredictionPipeline(SupervisedLearningPipeline):
    def __init__(self, lab_panel, drug, num_episodes, use_cache=None, random_state=None):
        SupervisedLearningPipeline.__init__(self, lab_panel, num_episodes, use_cache, random_state)

        self.drug = drug
        self._build_raw_feature_matrix()
        self._build_processed_feature_matrix()
        self._train_and_analyze_predictors()

    def _build_model_dump_path(self, algorithm):
        template = '%s' + '-normality-%s-model.pkl' % algorithm
        pipeline_file_name = inspect.getfile(inspect.currentframe())

        slugified_var = '-'.join(self._var.split())
        model_dump_name = template % (slugified_var)

        # Build path.
        data_dir = self._fetch_data_dir_path(pipeline_file_name)
        model_dump_path = '/'.join([data_dir, self.drug, model_dump_name])

        return model_dump_path


    def _build_raw_matrix_path(self):
        template = '%s-normality-matrix-%d-episodes-raw.tab'
        pipeline_file_name = inspect.getfile(inspect.currentframe())

        slugified_var = '-'.join(self._var.split())
        raw_matrix_name = template % (slugified_var, self._num_rows)

        data_dir = self._fetch_data_dir_path(pipeline_file_name)
        drug_path = '/'.join([data_dir, self.drug])
        if not os.path.exists(drug_path):
            os.makedirs(drug_path)
        raw_matrix_path = '/'.join([data_dir, self.drug, raw_matrix_name])

        return raw_matrix_path

    def _build_composite_raw_matrix_path(self):
        template = '%s-normality-matrix-%d-episodes-raw.tab'
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        return SupervisedLearningPipeline._build_matrix_path(self, template, \
            pipeline_file_name)
   
    def _build_raw_feature_matrix(self):
        # This pipeline should only be run AFTER raw LabCultureMatrix has been
        # created. To build our raw feature matrix, we load the labculture matrix
        # into memory and filter down to rows where the antibiotic
        # we care about was tested. 
        raw_matrix_path = self._build_raw_matrix_path()
        self._raw_matrix_params = {}
        if os.path.exists(raw_matrix_path):
            pass
        else:
            # Assert LabCultureMatrix already built
            composite_raw_matrix_path = self._build_composite_raw_matrix_path()
            assert os.path.exists(composite_raw_matrix_path)

            # Load in LabCultureMatrix, filter on susceptibiliy tested column
            comp_raw_matrix = pd.read_csv(composite_raw_matrix_path, sep='\t')
            outcome_tested = '%s_tested' % self.drug
            raw_matrix = comp_raw_matrix[comp_raw_matrix[outcome_tested] == 1]
            
            # Write Filtered Matrix to raw matrix path
            raw_matix_path = self._build_raw_matrix_path()
            raw_matrix.to_csv(raw_matrix_path, sep='\t', index=False)


    def _build_processed_matrix_path(self):
        template = '%s-normality-matrix-%d-episodes-processed.tab'
        pipeline_file_path = inspect.getfile(inspect.currentframe())

        slugified_var = '-'.join(self._var.split())
        processed_matrix_name = template % (slugified_var, self._num_rows)

        # Build Path
        data_dir = self._fetch_data_dir_path(pipeline_file_path)
        processed_matrix_path = '/'.join([data_dir, self.drug, processed_matrix_name])

        return processed_matrix_path

    def _build_processed_feature_matrix(self):
        # Define parameters for processing steps.
        params = {}
        raw_matrix_path = self._build_raw_matrix_path()
        processed_matrix_path = self._build_processed_matrix_path()
        features_to_add = {}
        imputation_strategies = {
        }

        features_to_remove = [
            'pat_id', 'shifted_order_time',
            'proc_code', 'abnormal_panel', 'Birth.pre',
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
            'escherichia_coli',
            "organism_name",
            "staphylococcus_aureus",
            "enterococcus_species", 
            "klebsiella_pneumoniae",
            "pseudomonas_aeruginosa", 
            "coag_negative_staphylococcus", 
            "enterococcus_faecalis", 
            "proteus_mirabilis", 
            "candida_albicans"
        ]

        antibiotic_flags = ['trimethoprim_sulfamethoxazole', 'vancomycin',
                            'penicillin', 'levofloxacin',
                            'clindamycin', 'ceftriaxone',
                            'erythromycin', 'ampicillin',
                            'meropenem', 'ciprofloxacin',
                            'cefepime', 'aztreonam',
                            'ampicillin_sulbactam', 'piperacillin_tazobactam',
                            'linezolid', 'oxacillin',
                            'cefazolin', 'daptomycin'
        ]


        features_to_remove += ['%s_susc' % flag for flag in antibiotic_flags if flag != self.drug]
        features_to_remove += ['%s_tested' % flag for flag in antibiotic_flags]

        features_to_keep = [
            # Keep the # of times it's been ordered in past, even if low info.
            '%s.pre' % '-'.join(self._var.split())
        ]
        outcome_label = '%s_susc' % self.drug
        selection_problem = FeatureSelector.CLASSIFICATION
        selection_algorithm = FeatureSelector.RECURSIVE_ELIMINATION
        percent_features_to_select = 0.05
        matrix_class = LabCultureMatrix
        pipeline_file_path = inspect.getfile(inspect.currentframe())
        random_state = self._random_state
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
        params['random_state'] = random_state

        # Defer processing logic to SupervisedLearningPipeline.
        SupervisedLearningPipeline._build_processed_feature_matrix(self, params)


    def _train_and_analyze_predictors(self):
        log.info('Training and analyzing predictors...')
        problem = SupervisedLearningPipeline.CLASSIFICATION
        meta_report = None
        fm_io = FeatureMatrixIO()

        # Build paths for output.
        pipeline_file_name = inspect.getfile(inspect.currentframe())
        data_dir = SupervisedLearningPipeline._fetch_data_dir_path(self, pipeline_file_name)

        # Test BifurcatedSupervisedClassifier and SupervisedClassifier.
        algorithms_to_test = list()
        algorithms_to_test.extend(SupervisedClassifier.SUPPORTED_ALGORITHMS)
        # for algorithm in SupervisedClassifier.SUPPORTED_ALGORITHMS:
        #     algorithms_to_test.append('bifurcated-%s' % algorithm)
        log.debug('algorithms_to_test: %s' % algorithms_to_test)

        # Train and analyse algorithms.
        for algorithm in algorithms_to_test:
            log.info('Training and analyzing %s...' % algorithm)
            # If report_dir does not exist, make it.
            report_dir = '/'.join([data_dir, self.drug, algorithm])
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            # Define hyperparams.
            hyperparams = {}
            hyperparams['algorithm'] = algorithm
            hyperparams['hyperparam_strategy'] = SupervisedClassifier.EXHAUSTIVE_SEARCH
            hyperparams['max_iter'] = 1024
            hyperparams['random_state'] = self._random_state

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
                header = ['LabCulturePredictionPipeline("%s", 1000000)' % self._var]
                # Write error report.
                fm_io.write_data_frame_to_file(algorithm_report, \
                    '/'.join([report_dir, '%s-normality-prediction-report.tab' % (self._var)]), \
                    header)
            # If successfully trained, append to a meta report.
            elif status == SupervisedClassifier.TRAINED:
                pipeline_prefix = '%s-normality-prediction-%s' % (self._var, algorithm)
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
            header = ['LabCulturePredictionPipeline("%s", 1000000)' % self._var]
            fm_io.write_data_frame_to_file(meta_report, \
                '/'.join([data_dir, '%s-normality-prediction-report.tab' % self._var]), header)




        
if __name__ == '__main__':
    log.level = logging.DEBUG
    parser = argparse.ArgumentParser()
    parser.add_argument('-antibiotic_name', required=True)
    args = parser.parse_args()

    panel = "LABBLC LABBLC2"
    SusceptibilityPredictionPipeline(panel, args.antibiotic_name, 1000000, use_cache=True, random_state=123456789)

