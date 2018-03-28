#!/usr/bin/python
"""
Given data in /LabTestAnalysis/machine_learning/data/, build report tables.
"""

import ast
import inspect
import os
import numpy as np
import pandas
from pandas import DataFrame, read_csv, Series
import sys

from medinfo.common.Util import log
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

class LabNormalityReport:
    def __init__(self):
        self._fm_io = FeatureMatrixIO()
        pass

    @staticmethod
    def fetch_components_in_panel(lab_panel):
        # Doing a single query results in a sequential scan through
        # stride_order_results. To avoid this, break up the query in two.
        # First, get all the order_proc_ids for proc_code.
        query = SQLQuery()
        query.addSelect('order_proc_id')
        query.addFrom('stride_order_proc')
        query.addWhereIn('proc_code', [lab_panel])
        query.addGroupBy('order_proc_id')
        results = DBUtil.execute(query)
        lab_order_ids = [row[0] for row in results]

        # Second, get all base_names from those orders.
        query = SQLQuery()
        query.addSelect('base_name')
        query.addFrom('stride_order_results')
        query.addWhereIn('order_proc_id', lab_order_ids)
        query.addGroupBy('base_name')
        results = DBUtil.execute(query)
        components = [row[0] for row in results]

        return components

    @staticmethod
    def fetch_data_dir_path():
        # e.g. report_dir = CDSS/scripts/LabTestAnalysis/data
        data_dir = LabNormalityReport.fetch_report_dir_path()
        report_dir_list = data_dir.split('/')[:-1]
        report_dir_list.extend(['machine_learning', 'data'])

        report_dir = '/'.join(report_dir_list)
        return report_dir

    @staticmethod
    def fetch_report_dir_path():
        # e.g. data_dir = CDSS/scripts/LabTestAnalysis/report
        file_name = inspect.getfile(inspect.currentframe())
        data_dir = os.path.dirname(os.path.abspath(file_name))
        return data_dir

    @staticmethod
    def fetch_lab_panels():
        # Treat LabNormalityPredictionPipeline as the source of truth for
        # defining which algorithms to analyze. Infer list from data dir.
        data_dir = LabNormalityReport.fetch_data_dir_path()
        labs = os.listdir(data_dir)
        # OSX automatically creates .DS_Store files.
        if '.DS_Store' in labs:
            labs.remove('.DS_Store')
        labs.remove('LABNONGYN')
        return sorted(labs)

    @staticmethod
    def read_lab_meta_report(lab_panel):
        fm_io = FeatureMatrixIO()
        data_dir = LabNormalityReport.fetch_data_dir_path()
        meta_report_path = data_dir + '/%s/%s-normality-prediction-report.tab' % (lab_panel, lab_panel)
        if os.path.exists(meta_report_path):
            meta_report = fm_io.read_file_to_data_frame(meta_report_path)
            return meta_report
        else:
            # IF meta_report does not exist, fetch the data on class counts.
            algorithm = SupervisedClassifier.REGRESS_AND_ROUND
            report_path = data_dir + '/%s/%s/%s-normality-prediction-report.tab' % (lab_panel, algorithm, lab_panel)
            algorithm_report = fm_io.read_file_to_data_frame(report_path)
            return algorithm_report

    @staticmethod
    def fetch_best_predictor(lab_panel):
        meta_report = LabNormalityReport.read_lab_meta_report(lab_panel)
        # Check for whether 0 classifiers were able to successfully train.
        if 'error' in meta_report.columns.values:
            # On the fly, interpret failure as a new "classifier".
            meta_report = meta_report.loc[0]
            train_value_counts = ast.literal_eval('%s' % meta_report['y_train.value_counts()'])
            test_value_counts = ast.literal_eval('%s' % meta_report['y_test.value_counts()'])

            max_value = np.max(train_value_counts.values())
            common_label = [k for k, v in train_value_counts.iteritems() if v == max_value][0]
            test_size = np.sum(test_value_counts.values())
            counts = meta_report['y_test.value_counts()']
            accuracy = test_value_counts[common_label] / test_size
            recall = 1.0 if common_label == 1 else 0.0
            percent_predictably_positive = 0.0
            precision = (test_value_counts[1] / test_size) if common_label == 1 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall)
            average_precision = precision
            precision_at_10_percent = precision
            k_99 = 1.0 if precision >= 0.99 else 0.0
            k_95 = 1.0 if precision >= 0.95 else 0.0
            k_90 =1.0 if precision >= 0.90 else 0.0
            roc_auc = None
            hyperparams = None

            best_predictor = DataFrame({
                'model': ['CONSTANT(label=%s)' % common_label],
                'test_size': [test_size],
                'y_test.value_counts()': [counts],
                'accuracy': [accuracy],
                'recall': [recall],
                'precision': [precision],
                'f1': [f1],
                'average_precision': [average_precision],
                'percent_predictably_positive': [percent_predictably_positive],
                'precision_at_10_percent': [precision_at_10_percent],
                'k(precision=0.99)': [k_99],
                'k(precision=0.95)': [k_95],
                'k(precision=0.90)': [k_90],
                'roc_auc': [roc_auc],
                'hyperparams': [hyperparams]
            })

            return best_predictor

        # Note that there might be multiple values with the same max value.
        best_predictor = meta_report.loc[meta_report['percent_predictably_positive'] == meta_report['percent_predictably_positive'].max()]
        num_predictors = len(best_predictor.index)

        # Break ties based on roc_auc.
        if num_predictors != 1:
            best_predictor = meta_report.loc[meta_report['roc_auc'] == meta_report['roc_auc'].max()]
            num_predictors = len(best_predictor.index)

        # Break ties based on k(0.99).
        if num_predictors != 1:
            best_predictor = meta_report.loc[meta_report['k(precision=0.99)'] == meta_report['k(precision=0.99)'].max()]
            num_predictors = len(best_predictor.index)

        # Break ties on accuracy.
        if num_predictors != 1:
            best_predictor = meta_report.loc[meta_report['accuracy'] == meta_report['accuracy'].max()]
            num_predictors = len(best_predictor.index)

        # If still tied, return first.
        best_predictor = best_predictor.iloc[0]

        return best_predictor

    @staticmethod
    def fetch_summary_stats_dir():
        report_dir = LabNormalityReport.fetch_report_dir_path()
        stats_dir_list = report_dir.split('/')[:-1]
        stats_dir_list.extend(['lab_statistics', 'data_summary_stats'])
        stats_dir = '/'.join(stats_dir_list)

        return stats_dir

    @staticmethod
    def fetch_lab_panel_summary_stats(lab_panel):
        stats_dir = LabNormalityReport.fetch_summary_stats_dir()
        panel_stats_path = '/'.join([stats_dir, 'labs_charges_volumes.csv'])
        panel_stats = read_csv(panel_stats_path)
        panel_index = panel_stats.index[panel_stats['name'] == lab_panel].tolist()[0]
        panel_row = panel_stats.loc[panel_index]

        return panel_row

    @staticmethod
    def fetch_median_charge(lab_panel):
        if lab_panel == 'LABNA':
            return '0.50'
        panel_row = LabNormalityReport.fetch_lab_panel_summary_stats(lab_panel)

        return '{:.2f}'.format(panel_row['median_price'])

    @staticmethod
    def fetch_description(lab_panel):
        if lab_panel == 'LABNA':
            return 'NA'

        panel_row = LabNormalityReport.fetch_lab_panel_summary_stats(lab_panel)

        return panel_row['description']

    @staticmethod
    def fetch_volume(lab_panel):
        if lab_panel == 'LABNA':
            return 10

        panel_row = LabNormalityReport.fetch_lab_panel_summary_stats(lab_panel)

        return panel_row['count']

    @staticmethod
    def build_lab_performance_summary_table():
        # Include the following fields:
        # * lab_panel
        # * description
        # * median_charge
        # * volume
        # * median_charge_volume ($)
        # * best_algorithm
        # * k(precision=0.99) (%)
        # * k(precision=0.95) (%)
        # * k(precision=0.90) (%)
        # * median_savings(precision=0.99) ($)
        # * median_savings(precision=0.95) ($)
        # * median_savings(precision=0.90) ($)
        lab_summary = DataFrame()
        lab_panels = LabNormalityReport.fetch_lab_panels()
        for lab_panel in lab_panels:
            print lab_panel
            best_predictor = LabNormalityReport.fetch_best_predictor(lab_panel)
            description = LabNormalityReport.fetch_description(lab_panel)
            median_charge = LabNormalityReport.fetch_median_charge(lab_panel)
            counts = best_predictor['y_test.value_counts()']
            volume = LabNormalityReport.fetch_volume(lab_panel)
            median_charge_volume = float(median_charge) * float(volume)
            roc_auc = best_predictor['roc_auc']
            best_model = best_predictor['model']
            percent_predictably_positive = float(best_predictor['percent_predictably_positive'])
            k_99 = float(best_predictor['k(precision=0.99)'])
            k_95 = float(best_predictor['k(precision=0.95)'])
            k_90 = float(best_predictor['k(precision=0.90)'])
            # components = LabNormalityReport.fetch_components_in_panel(lab_panel)
            row = DataFrame({
                'lab_panel': [lab_panel],
                'description': [description],
                # 'num_components': [len(components)],
                'counts': [counts],
                'median_charge': [median_charge],
                'volume': [volume],
                'median_charge_volume ($)': ['{:.2f}'.format(median_charge_volume)],
                'best_model': [best_model],
                'roc_auc': [roc_auc],
                'percent_predictably_positive': [percent_predictably_positive],
                'k(precision=0.99)': [k_99],
                'k(precision=0.95)': [k_95],
                'k(precision=0.90)': [k_90],
                'median_savings(precision=0.99) ($)': ['{:.2f}'.format(k_99 * median_charge_volume)],
                'median_savings(precision=0.95) ($)': ['{:.2f}'.format(k_95 * median_charge_volume)],
                'median_savings(precision=0.90) ($)': ['{:.2f}'.format(k_90 * median_charge_volume)]
            })
            lab_summary = lab_summary.append(row.loc[0], ignore_index=True)

        return DataFrame(lab_summary, columns=['lab_panel', 'description', 'counts', 'num_components', 'median_charge', 'volume', 'median_charge_volume ($)',
                    'best_model', 'roc_auc', 'percent_predictably_positive', 'k(precision=0.99)', 'k(precision=0.95)', 'k(precision=0.90)',
                    'median_savings(precision=0.99) ($)', 'median_savings(precision=0.95) ($)', 'median_savings(precision=0.90) ($)'])

    @staticmethod
    def fetch_algorithm_performance(lab_panel, algorithm):
        meta_report = LabNormalityReport.read_lab_meta_report(lab_panel)

        # Because all the bifurcated classifiers contain the algorithm
        # string for the base classifier, we need to use two masks to generate
        # the right mask.
        if 'cross-validation' in algorithm:
            algorithm = algorithm.strip('-cross-validation')
        if 'model' not in meta_report.columns.values:
            return meta_report
        non_bifurcated_mask = meta_report['model'].str.contains(algorithm.upper().replace('-','_'))
        bifurcated_mask = meta_report['model'].str.contains(('bifurcated-' + algorithm).upper().replace('-','_'))
        if 'bifurcated' in algorithm:
            combined_mask = non_bifurcated_mask
        else:
            combined_mask = non_bifurcated_mask & ~bifurcated_mask

        algorithm_report = meta_report[combined_mask]

        return algorithm_report

    @staticmethod
    def build_algorithm_performance_summary(algorithm):
        models = DataFrame()
        lab_panels = LabNormalityReport.fetch_lab_panels()
        best_count = 0
        for lab_panel in lab_panels:
            algorithm_report = LabNormalityReport.fetch_algorithm_performance(lab_panel, algorithm)
            if 'model' not in algorithm_report.columns.values or algorithm_report.empty:
                continue
            models = models.append(algorithm_report, ignore_index=True)
            best_algorithm = LabNormalityReport.fetch_best_predictor(lab_panel)
            # best_algorithm.reset_index(inplace=True)
            algorithm_report.reset_index()
            if algorithm_report.iloc[0].equals(best_algorithm):
                best_count += 1
            algorithm_report['lab_panel'] = lab_panel

        min_k_99 = models['percent_predictably_positive'].min()
        median_k_99 = models['percent_predictably_positive'].median()
        max_k_99 = models['percent_predictably_positive'].max()
        min_roc_auc = models['roc_auc'].min()
        median_roc_auc = models['roc_auc'].median()
        max_roc_auc = models['roc_auc'].max()
        algorithm_summary = DataFrame({
            'algorithm': [algorithm],
            'best_predictor_count': [best_count],
            'min(k(0.99))': [min_k_99],
            'median(k(0.99))': [median_k_99],
            'max(k(0.99))': [max_k_99],
            'min(roc_auc)': [min_roc_auc],
            'median(roc_auc)': [median_roc_auc],
            'max(roc_auc)': [max_roc_auc]
        }, columns=['algorithm', 'best_predictor_count', 'min(k(0.99))',
                    'median(k(0.99))', 'max(k(0.99))', 'min(roc_auc)',
                    'median(roc_auc)','max(roc_auc)'])

        return algorithm_summary

    @staticmethod
    def build_algorithm_performance_summary_table():
        algorithms_to_test = list()
        algorithms_to_test.extend(SupervisedClassifier.SUPPORTED_ALGORITHMS)
        for algorithm in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            algorithms_to_test.append('bifurcated-%s' % algorithm)

        summary = DataFrame()
        for algorithm in algorithms_to_test:
            algorithm_summary = LabNormalityReport.build_algorithm_performance_summary(algorithm)
            summary = summary.append(algorithm_summary, ignore_index=True)

        return summary

if __name__ == '__main__':
    fm_io = FeatureMatrixIO()
    # summary_table = LabNormalityReport.build_lab_performance_summary_table()
    # fm_io.write_data_frame_to_file(summary_table, 'lab-performance-summary.tab')
    summary = LabNormalityReport.build_algorithm_performance_summary_table()
    fm_io.write_data_frame_to_file(summary, 'algorithm-performance-summary.tab')
