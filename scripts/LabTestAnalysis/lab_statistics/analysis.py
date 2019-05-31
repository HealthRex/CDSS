
import stats_utils

import os

import pandas as pd
import numpy as np
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import LocalEnv

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline \
        import NON_PANEL_TESTS_WITH_GT_500_ORDERS, \
            UCSF_TOP_PANELS, UMICH_TOP_PANELS, \
            STRIDE_COMPONENT_TESTS_common, UMICH_TOP_COMPONENTS_common, UCSF_TOP_COMPONENTS_common

class Stats_Plotter():
    def __init__(self, data_source='Stanford', lab_type='panel', curr_version='10000-episodes'):
        self.data_source = data_source
        self.lab_type = lab_type

        if data_source == 'Stanford' and lab_type == 'panel':
            self.all_labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS  #
        elif data_source == 'Stanford' and lab_type == 'component':
            self.all_labs = STRIDE_COMPONENT_TESTS_common#
        elif data_source == 'UMich' and lab_type == 'panel':
            self.all_labs = UMICH_TOP_PANELS
        elif data_source == 'UMich' and lab_type == 'component':
            self.all_labs = UMICH_TOP_COMPONENTS_common#
        elif data_source == 'UCSF' and lab_type == 'component':
            self.all_labs = UCSF_TOP_COMPONENTS_common #
        elif data_source == 'UCSF' and lab_type == 'panel':
            self.all_labs = UCSF_TOP_PANELS

        self.curr_version = curr_version

        self.dataset_foldername = 'data-%s-%s-%s'%(data_source, lab_type, curr_version)

        self.lab_descriptions = stats_utils.get_lab_descriptions(data_source=self.data_source, lab_type=self.lab_type)


    def plot_full_cartoon(self, lab='LABLDH', include_threshold_colors=True, inverse01=False):
        print 'Running plot_full_cartoon...'

        inverse_maker = '_inversed01' if inverse01 else ''

        statsByLab_folderpath = '/Users/songxu/healthrex/CDSS/scripts/LabTestAnalysis/lab_statistics/data-%s-%s-%s/'%(self.data_source,self.lab_type,self.curr_version)
        ml_folderpath = statsByLab_folderpath.replace("lab_statistics", "machine_learning")

        result_folderpath = os.path.join(statsByLab_folderpath, '../', 'Fig1_cartoon')
        if not os.path.exists(result_folderpath):
            os.mkdir(result_folderpath)

        xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best, p_val \
            = stats_utils.get_curve_onelab(lab,
                                           all_algs=['random-forest'],
                                           data_folder=ml_folderpath,
                                           curve_type='ROC',
                                           get_pval=False)

        score_thres = 0.756

        plt.figure(figsize=(5, 4))
        # plt.plot(xVal_base, yVal_base, label='baseline model, %0.2f' % (score_base), linewidth=2)
        '''Representative ROC of LABLDH'''
        if not inverse01:
            plt.plot(xVal_best, yVal_best, color='orange', linewidth=2) #, label='random forest', AUROC=%0.2f  % (score_best)
        else:
            plt.plot(1-yVal_best, 1-xVal_best, color='orange', linewidth=2)

        if include_threshold_colors:
            df_directcompare_rf = pd.read_csv(os.path.join(ml_folderpath, lab, 'random-forest', 'direct_comparisons.csv'))
            actual_labels = df_directcompare_rf['actual'].values
            predict_probas = df_directcompare_rf['predict'].values

            sensitivity, specificity, LR_p, LR_n, PPV, NPV = stats_utils.get_confusion_metrics(actual_labels, predict_probas, score_thres, also_return_cnts=False)
            print "sensitivity", sensitivity
            print "specificity", specificity
            print "score_thres", score_thres

            '''The POINT of PPV=0.95'''
            if not inverse01:
                plt.scatter(1-specificity, sensitivity, s=50, color='orange')
            else:
                plt.scatter(1-sensitivity, specificity, s=50, color='orange')

            '''Reference line of AUC=0.5'''
            dash_num = 20
            # plt.plot([1-specificity]*dash_num, np.linspace(0,1,num=dash_num), 'k--')
            plt.plot(np.linspace(0,1,num=dash_num),np.linspace(0,1,num=dash_num), color='lightblue', linestyle='--')

        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.xticks([])
        plt.yticks([])
        plt.ylabel('Sensitivity', fontsize=16) #lab_descriptions.get(lab, lab)
        plt.xlabel('1-Specificity', fontsize=16)
        # plt.legend(fontsize=12)
        plt.savefig(os.path.join(result_folderpath, 'ROC_%s%s.png'%(lab,inverse_maker)))

        plt.clf()

        df = pd.read_csv(ml_folderpath + "/%s/baseline_comparisons.csv"
                         % (lab), keep_default_na=False)
        scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
        scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

        plot_baseline = False
        if plot_baseline:
            plt.figure(figsize=(5, 4))


            plt.hist(scores_actual_0, bins=30, alpha=0.8, color='b', label="Abnormal")
            plt.hist(scores_actual_1, bins=30, alpha=0.8, color='g', label="Normal")
            plt.xlim([0, 1])
            plt.ylim([0, 500])
            plt.xticks([])
            plt.yticks([])
            # plt.xlabel(lab_descriptions[lab] + 'auroc=%.2f' % auc)
            # plt.xlabel('baseline', fontsize=16)
            plt.xlabel('Score, baseline', fontsize=16)
            plt.ylabel('num of orders', fontsize=16)
            plt.legend(fontsize=12)
            plt.savefig(os.path.join(statsByLab_folderpath, 'cartoon_baseline_%s.png'%lab))
            plt.clf()

        plt.figure(figsize=(5, 4))
        alg = 'random-forest'
        df = pd.read_csv(ml_folderpath + "/%s/%s/direct_comparisons.csv"
                         % (lab, alg), keep_default_na=False)


        df1 = pd.read_csv(ml_folderpath + "/%s/%s/%s-normality-prediction-%s-report.tab"
                          % (lab, alg, lab, alg), sep='\t', keep_default_na=False)
        auc = df1['roc_auc'].values[0]


        if include_threshold_colors:


            scores_actual_trueNega = df.ix[(df['actual']==0) & (df['predict']<score_thres), 'predict'].values
            scores_actual_falsPosi = df.ix[(df['actual'] == 0) & (df['predict'] >= score_thres), 'predict'].values

            scores_actual_falsNega = df.ix[(df['actual'] == 1) & (df['predict'] < score_thres), 'predict'].values
            scores_actual_truePosi = df.ix[(df['actual'] == 1) & (df['predict'] >= score_thres), 'predict'].values

            if not inverse01:
                plt.hist(scores_actual_trueNega, bins=22, alpha=0.8, color='royalblue', label="true negatives")
                plt.hist(scores_actual_falsNega, bins=22, alpha=0.8, color='gold', label="false negatives")
                plt.hist(scores_actual_truePosi, bins=7, alpha=0.8, color='forestgreen', label="true positives")
                plt.hist(scores_actual_falsPosi, bins=7, alpha=0.8, color='orangered', label="false positives")

                plt.plot([score_thres] * dash_num, np.linspace(0, 800, num=dash_num), 'k--')
            else:
                plt.hist(1-scores_actual_trueNega, bins=22, alpha=0.8, color='royalblue', label="true positives")
                plt.hist(1-scores_actual_falsNega, bins=22, alpha=0.8, color='gold', label="false positives")
                plt.hist(1-scores_actual_truePosi, bins=7, alpha=0.8, color='forestgreen', label="true negatives")
                plt.hist(1-scores_actual_falsPosi, bins=7, alpha=0.8, color='orangered', label="false negatives")

                plt.plot([1-score_thres] * dash_num, np.linspace(0, 800, num=dash_num), 'k--')



            plt.legend(loc=(0.45,0.6), fontsize=12)

        else:

            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            if not inverse01:
                plt.hist(scores_actual_0, bins=30, alpha=0.8, color='gray', label="Abnormal") #gray red
                plt.hist(scores_actual_1, bins=30, alpha=0.8, color='black', label="Normal") #black green
            else:
                plt.hist(1-scores_actual_0, bins=30, alpha=0.8, color='gray', label="Positive")
                plt.hist(1-scores_actual_1, bins=30, alpha=0.8, color='black', label="Negative")

            plt.legend(fontsize=12)

        plt.xlim([0, 1])
        plt.ylim([0, 800])
        plt.xticks([])
        plt.yticks([])
        # plt.xlabel(lab_descriptions[lab])
        # plt.xlabel('random forest', fontsize=16)
        plt.xlabel('Score', fontsize=16)
        plt.ylabel('Number of orders', fontsize=16)

        if include_threshold_colors:
            plt.savefig(os.path.join(result_folderpath, 'cartoon_%s_thres%s.png' % (lab, inverse_maker)))
        else:
            plt.savefig(os.path.join(result_folderpath, 'cartoon_%s%s.png' % (lab, inverse_maker)))

def main_full_analysis(curr_version, inverse01=False):

    '''
    :param curr_version:
    :param inverse01:
    :return:
    '''

    '''Figure 1'''
    plotter = Stats_Plotter(data_source='Stanford', lab_type='panel', curr_version=curr_version)
    # plotter.main_generate_lab_statistics(verbose=False)
    plotter.plot_full_cartoon(lab='LABLDH', include_threshold_colors=False, inverse01=inverse01)
    plotter.plot_full_cartoon(lab='LABLDH', include_threshold_colors=True, inverse01=inverse01)
    #

    '''Figure 2: 
    Stanford Panel Order_Intensities, 
    Stanford Component Order_Intensities, 
    Stanford Component Normality_Saturations.
    '''

    for data_source in ['Stanford', 'UCSF', 'UMich']: #'Stanford',
        for lab_type in ['panel', 'component']:

            plotter = Stats_Plotter(data_source=data_source, lab_type=lab_type, curr_version=curr_version)

            '''
            Two steps: 
            lab2stats: Getting lab-wise stats tables under lab_statistics/dataset_folder/stats_by_lab_alg/..
            stats2summary: Aggregate all labs' stats under lab_statistics/dataset_folder/..
            '''
            # plotter.main_generate_lab_statistics(verbose=False)



if __name__ == '__main__':
    curr_version = '10000-episodes-lastnormal'

    main_full_analysis(curr_version=curr_version, inverse01=True)