#!/usr/bin/python
"""
Utility class for analyzing the performance of a pre-trained classifier
on a set of test data.
"""

import matplotlib.pyplot as plt
from matplotlib import rcParams
from pandas import DataFrame

from sklearn.metrics import recall_score, precision_score, f1_score
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.metrics import precision_recall_curve, roc_curve

from medinfo.ml.PredictorAnalyzer import PredictorAnalyzer

class ClassifierAnalyzer(PredictorAnalyzer):
    ACCURACY_SCORE = 'accuracy'
    RECALL_SCORE = 'recall'
    PRECISION_SCORE = 'precision'
    F1_SCORE = 'f1'
    AVERAGE_PRECISION_SCORE = 'average_precision'
    ROC_AUC_SCORE = 'roc_auc'
    SUPPORTED_SCORES = [ACCURACY_SCORE, RECALL_SCORE, PRECISION_SCORE,
                        F1_SCORE, AVERAGE_PRECISION_SCORE, ROC_AUC_SCORE]

    def __init__(self, classifier, X_test, y_test):
        # TODO(sbala): Make this API more flexible, so that it can work
        # with multi-label classifiers or binary classifiers whose
        # positive label != 1.
        PredictorAnalyzer.__init__(self, classifier, X_test, y_test)
        self._y_pred_prob = classifier.predict_probability(X_test)[:,1]

    def _score_accuracy(self):
        return PredictorAnalyzer._score_accuracy(self)

    def _score_recall(self):
        return recall_score(self._y_test, self._y_predicted)

    def _score_precision(self):
        return precision_score(self._y_test, self._y_predicted)

    def _score_f1(self):
        return f1_score(self._y_test, self._y_predicted)

    def _score_average_precision(self):
        return average_precision_score(self._y_test, self._y_pred_prob)

    def _score_roc_auc(self):
        return roc_auc_score(self._y_test, self._y_pred_prob)

    def score(self, metric=None):
        if metric is None:
            metric = ClassifierAnalyzer.ACCURACY_SCORE

        if metric not in ClassifierAnalyzer.SUPPORTED_SCORES:
            raise ValueError('Score metric %s not supported.' % metric)

        if metric == ClassifierAnalyzer.ACCURACY_SCORE:
            return self._score_accuracy()
        elif metric == ClassifierAnalyzer.RECALL_SCORE:
            return self._score_recall()
        elif metric == ClassifierAnalyzer.PRECISION_SCORE:
            return self._score_precision()
        elif metric == ClassifierAnalyzer.F1_SCORE:
            return self._score_f1()
        elif metric == ClassifierAnalyzer.AVERAGE_PRECISION_SCORE:
            return self._score_average_precision()
        elif metric == ClassifierAnalyzer.ROC_AUC_SCORE:
            return self._score_roc_auc()

    def compute_precision_recall_curve(self):
        return precision_recall_curve(self._y_test, self._y_pred_prob)

    def plot_precision_recall_curve(self, title, dest_path):
        # Compute inputs.
        precisions, recalls, thresholds = self.compute_precision_recall_curve()
        average_precision = self._score_average_precision()

        # Set figure settings.
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'Tahoma']

        # Make plot.
        plt.step(recalls, precisions, color='b', alpha=0.2, where='post')
        plt.fill_between(recalls, precisions, step='post', alpha=0.2, color='b')

        # Label axes.
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])

        # Set title.
        plt.title('{0}: AP={1:0.2f}'.format(title, average_precision))

        # Save figure.
        plt.savefig(dest_path)

    def compute_roc_curve(self):
        return roc_curve(self._y_test, self._y_pred_prob)

    def plot_roc_curve(self, title, dest_path):
        # Compute inputs.
        fprs, tprs, thresholds = self.compute_roc_curve()
        roc_auc = self._score_roc_auc()

        # Set figure settings.
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'Tahoma']

        # Make plot.
        plt.figure()
        plt.plot(fprs, tprs, color='darkorange', lw=2)
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')

        # Label axes.
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')

        # Set title.
        plt.title('%s (AUC = %s)' % (title, roc_auc))

        # Save figure.
        plt.savefig(dest_path)

    def build_report(self):
        column_names = ['model', 'test_size']
        column_names.extend(ClassifierAnalyzer.SUPPORTED_SCORES)
        report_dict = {
            'model': [repr(self._predictor)],
            'test_size': [self._y_test.shape[0]]
        }

        for score_metric in ClassifierAnalyzer.SUPPORTED_SCORES:
            score_value = self.score(metric=score_metric)
            report_dict.update({score_metric: score_value})

        return DataFrame(report_dict, columns=column_names)

    def write_report(self, dest_path):
        column_names = ['model', 'test_size']
        column_names.extend(ClassifierAnalyzer.SUPPORTED_SCORES)
        report = self.build_report()

        PredictorAnalyzer.write_report(self, report, dest_path, column_names)
