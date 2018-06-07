#!/usr/bin/python
"""
Given data in /LabTestAnalysis/machine_learning/data/, build report tables.
"""

import ast
import inspect
import os
import matplotlib
import matplotlib.pyplot as plt
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
    PROC_CODE_TO_LABEL = {
        'LABUSPG': 'Urine Specific Gravity',
        'LABLIDOL': 'Lidocaine',
        'LABURIC': 'Uric Acid',
        'LABSPLAC': 'Lactate (Sepsis Protocol)',
        'LABCMVQT': 'Cytomegalovirus DNA',
        'LABAFBC': 'AFB Culture, Respiratory',
        'LABCSFC': 'CSF Culture',
        'LABHIVWBL': 'HIV Antibody',
        'LABCSFGL': 'CSF Glucose',
        'LABAFBD': 'AFB Culture, Non-Respiratory',
        'LABPLTS': 'Platelet Count',
        'LABLACWB': 'Lactate (Whole Blood)',
        'LABUAPRN': 'Urinalysis, Culture Screen',
        'LABROMRS': 'MRSA Screen',
        'LABMB': 'Creatine Kinase-Muscle/Brain',
        'LABLAC': 'Lactate',
        'LABTYPSNI': 'Type and Screen',
        'LABBLC2': 'Blood Culture (2 Aerobic)',
        'LABTNI': 'Troponin I',
        'LABMGN': 'Magnesium',
        'LABUPREG': 'Pregnancy (Urine)',
        'LABBLCSTK': 'Blood Culture (1st, Phlebotomy)',
        'LABBLCTIP': 'Blood Culture (2nd, Catheter)',
        'LABCK': 'Creatine Kinase',
        'LABHEPAR': 'Heparin Activity Level',
        'LABGRAM': 'Gram Stain',
        'LABK': 'Potassium',
        'LABFCUL': 'Fungal Culture',
        'LABFIB': 'Fibrinogen',
        'LABTRIG': 'Triglycerides',
        'LABFLDC': 'Fluid Culture and Gram Stain',
        'LABANER': 'Anaerobic Culture',
        'LABCAI': 'Ionized Calcium',
        'LABBLC': 'Blood Culture (Aerobic & Anaerobic)',
        'LABPCG3': 'i-STAT G3+',
        'LABA1C': 'Hemoglobin A1c',
        'LABABG': 'Arterial Blood Gases',
        'LABALB': 'Albumin',
        'LABB12': 'Vitamin B12',
        'LABBXTG': 'Biopsy / Tissue Culture & Gram Stain',
        'LABCBCO': 'CBC',
        'LABCBCD': 'CBC with Differential',
        'LABCDTPCR': 'C. Diff. Toxin B Gene PCR',
        'LABCRP': 'C-Reactive Protein',
        'LABCSFTP': 'Cerebrospinal Fluid Total Protein',
        'LABESRP': 'Erythrocyte Sedimentation Rate',
        'LABFE': 'Iron',
        'LABFER': 'Ferritin',
        'LABFT4': 'Free T4',
        'LABNH3': 'Ammonia',
        'LABNTBNP': 'NT-proBNP',
        'LABPALB': 'Prealbumin',
        'LABPCCR': 'i-STAT Creatinine',
        'LABPCTNI': 'i-STAT Troponin I',
        'LABPHOS': 'Phosphorous',
        'LABPOCGLU': 'Glucose by Meter',
        'LABRESP': 'Respiratory Culture',
        'LABRETIC': 'Reticulocyte Count',
        'LABSTOBGD': 'Stool Guaiac',
        'LABTRFS': 'Transferrin Saturation',
        'LABTSH': 'Thyroid-Stimulating Hormone',
        'LABUA': 'Microscopic Urinalysis',
        'LABUOSM': 'Urine Osmolality',
        'LABUCR': 'Urine Creatinine',
        'LABURNA': 'Urine Sodium',
        'LABURNC': 'Urine Culture',
        'LABVANPRL': 'Vancomycin Trough Level',
        'LABVBG': 'Venous Blood Gases',
        'LABHAP': 'Haptoglobin',
        'LABHCTX': 'Hematocrit',
        'LABHFP': 'Hepatic Function Panel A',
        'LABLDH': 'Total LDH',
        'LABLIPS': 'Lipase',
        'LABMETB': 'Basic Metabolic Panel',
        'LABMETC': 'Comprehensive Metabolic Panel',
        'LABNA': 'Sodium',
        'LABDIGL': 'Digoxin',
        'LABCA': 'Calcium',
        'LABBUN': 'Blood Urea Nitrogen',
        'LABFOL': 'Folic Acid',
        'LABPT': 'Prothrombin Time',
        'LABPTT': 'Partial Thromboplastin Time',
        'LABHBSAG': 'Hepatitis B Surface Antigen',
        'LABOSM': 'Osmolality',
        'LABPCCG4O': 'i-STAT CG4 (Other)',
        'LABPROCT': 'Procalcitonin',
        'LABPTEG': 'Perioperative Thromboelastography',
        'LABRESPG': 'Respiratory Culture and Gram Stain',
        'LABSTLCX': 'Stool Culture',
        'LABCORT': 'Cortisol'
    }

    def __init__(self):
        self._fm_io = FeatureMatrixIO()

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
        if 'LABNONGYN' in labs:
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
            test_normal_count = ast.literal_eval(counts)[1.0]
            try:
                test_abnormal_count = ast.literal_eval(counts)[0.0]
            except:
                test_abnormal_count = 0
            accuracy = test_value_counts[common_label] / test_size
            recall = 1.0 if common_label == 1 else 0.0
            percent_predictably_positive = 0.0
            ppp_lower_ci = 0.0
            ppp_upper_ci = 1.0
            precision = (test_value_counts[1] / test_size) if common_label == 1 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall)
            average_precision = precision
            precision_at_10_percent = precision
            roc_auc = None
            roc_auc_lower_ci = None
            roc_auc_upper_ci = None
            hyperparams = None

            best_predictor = DataFrame({
                'model': ['CONSTANT(label=%s)' % common_label],
                'test_size': [test_size],
                'counts': counts,
                'test_normal_count': [test_normal_count],
                'test_abnormal_count': [test_abnormal_count],
                'accuracy': [accuracy],
                'recall': [recall],
                'precision': [precision],
                'f1': [f1],
                'average_precision': [average_precision],
                'percent_predictably_positive': [percent_predictably_positive],
                'percent_predictably_positive_0.95_lower_ci': [ppp_lower_ci],
                'percent_predictably_positive_0.95_upper_ci': [ppp_upper_ci],
                'precision_at_10_percent': [precision_at_10_percent],
                'roc_auc': [roc_auc],
                'roc_auc_0.95_lower_ci': [roc_auc_lower_ci],
                'roc_auc_0.95_upper_ci': [roc_auc_upper_ci],
                'hyperparams': [hyperparams]
            })

            return best_predictor.iloc[0]

        # Note that there might be multiple values with the same max value.
        best_predictor = meta_report.loc[meta_report['percent_predictably_positive_0.95_lower_ci'].astype('float') == meta_report['percent_predictably_positive_0.95_lower_ci'].astype('float').max()]
        num_predictors = len(best_predictor.index)

        # Break ties based on roc_auc.
        if num_predictors != 1:
            best_predictor = best_predictor.loc[best_predictor['percent_predictably_positive'].astype('float') == best_predictor['percent_predictably_positive'].astype('float').max()]
            num_predictors = len(best_predictor.index)

        # Break ties based on roc_auc.
        if num_predictors != 1:
            best_predictor = best_predictor.loc[best_predictor['roc_auc'].astype('float') == best_predictor['roc_auc'].astype('float').max()]
            num_predictors = len(best_predictor.index)

        # Break ties on accuracy.
        if num_predictors != 1:
            best_predictor = best_predictor.loc[best_predictor['accuracy'].astype('float') == best_predictor['accuracy'].astype('float').max()]
            num_predictors = len(best_predictor.index)

        # If still tied, return first.
        best_predictor = best_predictor.iloc[0]
        counts = best_predictor['y_test.value_counts()']
        test_normal_count = ast.literal_eval(counts)[1.0]
        test_abnormal_count = ast.literal_eval(counts)[0.0]
        best_predictor['test_normal_count'] = test_normal_count
        best_predictor['test_abnormal_count'] = test_abnormal_count

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
        # * percent_predictably_positive
        # * predicatble_charge_volume ($)
        lab_summary = DataFrame()
        lab_panels = LabNormalityReport.fetch_lab_panels()
        for lab_panel in lab_panels:
            best_predictor = LabNormalityReport.fetch_best_predictor(lab_panel)
            description = LabNormalityReport.fetch_description(lab_panel)
            median_charge = LabNormalityReport.fetch_median_charge(lab_panel)
            # counts = best_predictor['y_test.value_counts()']
            test_normal_count = best_predictor['test_normal_count']
            test_abnormal_count = best_predictor['test_abnormal_count']
            volume = LabNormalityReport.fetch_volume(lab_panel)
            median_charge_volume = float(median_charge) * float(volume)
            roc_auc = best_predictor['roc_auc']
            roc_auc_lower_ci = best_predictor['roc_auc_0.95_lower_ci']
            roc_auc_upper_ci = best_predictor['roc_auc_0.95_upper_ci']
            best_model = best_predictor['model']
            ppp = float(best_predictor['percent_predictably_positive'])
            ppp_lower_ci = best_predictor['percent_predictably_positive_0.95_lower_ci']
            ppp_upper_ci = best_predictor['percent_predictably_positive_0.95_upper_ci']
            # components = LabNormalityReport.fetch_components_in_panel(lab_panel)
            row = DataFrame({
                'lab_panel': [lab_panel],
                'description': [description],
                'test_normal_count': test_normal_count,
                'test_abnormal_count': test_abnormal_count,
                'median_charge': [median_charge],
                'volume': [volume],
                'median_charge_volume ($)': ['{:.2f}'.format(median_charge_volume)],
                'best_model': [best_model],
                'roc_auc': [roc_auc],
                'roc_auc_0.95_lower_ci': [roc_auc_lower_ci],
                'roc_auc_0.95_upper_ci': [roc_auc_upper_ci],
                'percent_predictably_positive': [ppp],
                'percent_predictably_positive_0.95_lower_ci': [ppp_lower_ci],
                'percent_predictably_positive_0.95_upper_ci': [ppp_upper_ci],
                'predictable_charge_volume ($)': ['{:.2f}'.format(ppp * median_charge_volume)],
            })
            lab_summary = lab_summary.append(row.loc[0], ignore_index=True)

        return DataFrame(lab_summary, columns=['lab_panel', 'description', 'test_normal_count', 'test_abnormal_count', 'median_charge', 'volume', 'median_charge_volume ($)',
                    'best_model', 'roc_auc', 'roc_auc_0.95_lower_ci', 'roc_auc_0.95_upper_ci',
                    'percent_predictably_positive', 'percent_predictably_positive_0.95_lower_ci',
                    'percent_predictably_positive_0.95_upper_ci', 'predictable_charge_volume ($)'])

    @staticmethod
    def build_lab_performance_report():
        lab_summary = LabNormalityReport.build_lab_performance_summary_table()


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
            if algorithm_report.iloc[0]['model'] == best_algorithm['model']:
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
            'min(predictability@0.99)': [min_k_99],
            'median(predictability@0.99)': [median_k_99],
            'max(predictability@0.99)': [max_k_99],
            'min(roc_auc)': [min_roc_auc],
            'median(roc_auc)': [median_roc_auc],
            'max(roc_auc)': [max_roc_auc]
        }, columns=['algorithm', 'best_predictor_count', 'min(predictability@0.99)',
                    'median(predictability@0.99)', 'max(predictability@0.99)', 'min(roc_auc)',
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

    @staticmethod
    def fetch_predictable_and_expensive_labs(all=None):
        labs = LabNormalityReport.build_lab_performance_summary_table()
        if all:
            predictable_labs = labs
        else:
            predictable_labs = labs.loc[labs['percent_predictably_positive'] >= 0.1]
        # labs = pandas.concat([predictable_labs,expensive_labs]).drop_duplicates().reset_index(drop=True)
        labs = predictable_labs
        labs['normal_rate'] = labs['test_normal_count'] / (labs['test_normal_count'] + labs['test_abnormal_count'])
        labs['abnormal_rate'] = labs['test_abnormal_count'] / (labs['test_normal_count'] + labs['test_abnormal_count'])
        labs['annual_median_charge_volume ($)'] = labs['median_charge_volume ($)'].astype('float') / 6.0
        labs['label'] = None
        labs.set_index('lab_panel', drop=False, inplace=True)

        # Add labels.
        for proc_code, label in LabNormalityReport.PROC_CODE_TO_LABEL.iteritems():
            if proc_code in labs['lab_panel'].values:
                labs.at[proc_code, 'label'] = label

        return labs

    @staticmethod
    def plot_predictable_and_expensive_charges():
        labs = LabNormalityReport.fetch_predictable_and_expensive_labs()
        # Build dataframe.
        charges = DataFrame()
        charges['label'] = labs['label']
        charges['normal, predictable'] = labs['percent_predictably_positive'] * labs['annual_median_charge_volume ($)'].astype('float')
        charges['normal, unpredictable'] = labs['normal_rate'] * labs['annual_median_charge_volume ($)'].astype('float') - charges['normal, predictable']
        charges['abnormal'] = labs['abnormal_rate'] * labs['annual_median_charge_volume ($)'].astype('float')
        charges['total'] = labs['annual_median_charge_volume ($)'].astype('float')
        charges.sort_values('normal, predictable', inplace=True)

        matplotlib.rcParams.update({'font.family': 'serif'})
        matplotlib.rcParams.update({'font.sans-serif': ['Helvetica', 'Arial', 'Tahoma']})
        matplotlib.rcParams.update({'font.serif': ['Times New Roman', 'Times', 'Palatino']})
        figure = plt.figure()
        title = "Lab test annual predictable charge volume"
        axes = charges[['label', 'normal, predictable', 'normal, unpredictable', 'abnormal']].plot(kind='barh', \
                    stacked=True, color=['#4caf50', '#448aff', '#f44336'], \
                    width=0.85, title=title, linewidth=0.5, edgecolor='#ffffff', \
                    logx=False)

        axes.set_ylabel("")
        axes.set_yticklabels(charges['label'])
        axes.set_xlabel("Annual Charge Volume ($, millions)")
        # axes.set_xticklabels(['0', '0', '5', '10', '15', '20', '25'])
        axes.set_xticklabels(['0', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        # for p in axes.patches:
        #     axes.annotate(str(p.get_width()), (p.get_width() * 1.005, p.get_y() * 1.005))

        plt.tight_layout()
        plt.savefig('predictable-and-expensive-charges.png', dpi=144)

    @staticmethod
    def build_lab_predictability_summary_report(all=None):
        labs = LabNormalityReport.fetch_predictable_and_expensive_labs(all)

        labs['normality'] = labs['normal_rate'].astype('float').map('{:.1%}'.format)
        labs['predictability@0.99'] = labs['percent_predictably_positive'].astype('float').map('{:.1%}'.format)
        labs['predictability@0.99[-0.95]'] = labs['percent_predictably_positive_0.95_lower_ci'].astype('float').map('{:.1%}'.format)
        labs['predictability@0.99[+0.95]'] = labs['percent_predictably_positive_0.95_upper_ci'].astype('float').map('{:.1%}'.format)
        labs['predictable_CV'] = (labs['percent_predictably_positive'].astype('float') * labs['annual_median_charge_volume ($)'].astype('float') / 1000).map('${:,.0f}'.format)
        labs['predictable_CV[-0.95]'] = (labs['percent_predictably_positive_0.95_lower_ci'].astype('float') * labs['annual_median_charge_volume ($)'].astype('float') / 1000).map('${:,.0f}'.format)
        labs['predictable_CV[+0.95]'] = (labs['percent_predictably_positive_0.95_upper_ci'].astype('float') * labs['annual_median_charge_volume ($)'].astype('float') / 1000).map('${:,.0f}'.format)

        summary = DataFrame()
        summary['lab'] = labs['label']
        summary['charge'] = labs['median_charge'].astype('float').map('${:,.0f}'.format)
        summary['volume'] = labs['volume'].floordiv(6).astype('float').map('{:,.0f}'.format)
        summary['normal rate'] = labs['normality']
        summary['predictability@0.99'] = labs['predictability@0.99'] + ' [' + \
            labs['predictability@0.99[-0.95]'] + ', ' + \
            labs['predictability@0.99[+0.95]'] + ']'
        summary['predictable CV ($1,000s)'] = labs['predictable_CV'] + ' [' + \
            labs['predictable_CV[-0.95]'] + ', ' + \
            labs['predictable_CV[+0.95]'] + ']'

        return summary


if __name__ == '__main__':
    fm_io = FeatureMatrixIO()
    summary_table = LabNormalityReport.build_lab_performance_summary_table()
    fm_io.write_data_frame_to_file(summary_table, 'lab-performance-summary.tab')
    summary = LabNormalityReport.build_algorithm_performance_summary_table()
    fm_io.write_data_frame_to_file(summary, 'algorithm-performance-summary.tab')
    LabNormalityReport.plot_predictable_and_expensive_charges()
    summary = LabNormalityReport.build_lab_predictability_summary_report()
    fm_io.write_data_frame_to_file(summary, 'predictable-labs.tab')
    summary = LabNormalityReport.build_lab_predictability_summary_report(all=True)
    fm_io.write_data_frame_to_file(summary, 'all-labs.tab')
