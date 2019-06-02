
import os
import stats_utils
import datetime
import collections
import pandas as pd
import numpy as np
import pickle

from medinfo.ml.SupervisedClassifier import SupervisedClassifier
from scripts.LabTestAnalysis.machine_learning.ml_utils import map_lab

pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import copy

from sklearn.metrics import roc_auc_score

import LocalEnv


DEFAULT_TIMELIMIT = stats_utils.DEFAULT_TIMELIMIT
#

main_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
stats_results_folderpath = os.path.join(main_folder, 'lab_statistics')
ml_results_folderpath = os.path.join(main_folder, 'machine_learning')

labs_old_stats_folder = os.path.join(stats_results_folderpath, 'data_summary_stats/')
labs_query_folder = os.path.join(stats_results_folderpath, 'query_lab_results/')

train_PPVs = (0.99, 0.95, 0.9, 0.8)

results_subfoldername = 'stats_by_lab_alg'
results_filename_template = '%s-stats-target-%s-%s.csv'
summary_filename_template = 'summary-stats-%s-%s.csv'


from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline \
        import NON_PANEL_TESTS_WITH_GT_500_ORDERS, \
    STRIDE_COMPONENT_TESTS, \
    UMICH_TOP_COMPONENTS, \
    UCSF_TOP_COMPONENTS, \
    UCSF_TOP_PANELS, UMICH_TOP_PANELS, \
STRIDE_COMPONENT_TESTS_common, UMICH_TOP_COMPONENTS_common, UCSF_TOP_COMPONENTS_common


all_algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

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




    def draw__Normality_Saturations(self, stats_folderpath, labs, max_repeat = 5, use_cached_fig_data=True):
        '''
        Drawing Figure 1 in the main text.

        :return:
        '''
        print 'draw__Normality_Saturations running...'

        print "Labs to be plot:", labs

        cached_result_foldername = os.path.join(stats_folderpath, 'Fig1_Normality_Saturations/')
        if not os.path.exists(cached_result_foldername):
            os.mkdir(cached_result_foldername)

        if os.path.exists(cached_result_foldername + 'lab2cnt.csv') and use_cached_fig_data:
            lab2cnt_pd = pd.read_csv(cached_result_foldername + 'lab2cnt.csv', keep_default_na=False)\
                .set_index('lab')
            lab2cnt_pd.columns = lab2cnt_pd.columns.astype(int)
            lab2cnt = lab2cnt_pd.to_dict(orient='index')

            lab2frac_pd = pd.read_csv(cached_result_foldername + 'lab2frac.csv', keep_default_na=False).set_index('lab')
            lab2frac_pd.columns = lab2frac_pd.columns.astype(int)
            lab2frac = lab2frac_pd.to_dict(orient='index')
        else:

            lab2cnt, lab2frac = {}, {}
            for lab in labs:
                print 'Getting Normality Saturations for %s..' % lab
                df_lab = stats_utils.get_queried_lab(lab, self.lab_type, time_limit=DEFAULT_TIMELIMIT)

                if self.lab_type=='panel':
                    df_lab = df_lab[df_lab['order_status'] == 'Completed']

                cur_dict = stats_utils.get_prevweek_normal__dict(df_lab, self.lab_type)

                normal_fractions = {}
                record_counts = {}
                for x in range(0, max_repeat + 1):
                    if x in cur_dict:
                        record_count = len(cur_dict[x])
                        normal_fraction = np.divide(sum(cur_dict[x]), float(record_count))
                    else:
                        record_count = 0
                        normal_fraction = float('nan')

                    record_counts[x] = record_count
                    normal_fractions[x] = (normal_fraction)
                lab2cnt[lab] = record_counts
                lab2frac[lab] = normal_fractions
            df_cnts = pd.DataFrame.from_dict(lab2cnt, orient='index').reset_index().rename(columns={'index': 'lab'})
            df_fracs = pd.DataFrame.from_dict(lab2frac, orient='index').reset_index().rename(columns={'index': 'lab'})

            df_cnts.to_csv(cached_result_foldername + 'lab2cnt.csv', index=False)
            df_fracs.to_csv(cached_result_foldername + 'lab2frac.csv', index=False)

        print 'lab2cnt', lab2cnt
        print 'lab2frac', lab2frac

        fig, ax = plt.subplots(figsize=(6.5, 3.25)) #6, 4.5 # 7, 2.565 #6.5, 3.75

        labs_to_plots = [labs[:20], labs[20:40], labs[40:60], labs[60:]]

        #, '<', '>'
        marker_types = ('o', 'v', '^', '8', 's', 'P', '*', 'X', 'D', 'd')

        for ind, labs_to_plot in enumerate(labs_to_plots):
            for k, lab in enumerate(labs_to_plot):  # :

                non_empty_inds = []
                for i in range(0,max_repeat+1):
                    if lab2frac[lab][i]=='':
                        break
                    non_empty_inds.append(i)
                y_s = [float(lab2frac[lab][i]) for i in non_empty_inds]
                print 'lab, y_s', lab, y_s
                plt.plot(non_empty_inds, y_s, '-'+marker_types[k], label=self.lab_descriptions[lab])
                # l2, = plt.scatter(non_empty_inds, y_s, marker=marker_types[k])
                # plt.plot(y_s[0], '-'+marker_types[k], color=l2.get_color(), markerfacecolor=l1.get_color(), label='My plots')

            plt.xticks(range(0, max_repeat + 1))
            plt.xlabel('Consecutive normal results in the past 7 days', fontsize=14)
            plt.tick_params('x', labelsize=15)  # 12
            plt.tick_params('y', labelsize=13)  # 10
            plt.ylabel("Normal rate", fontsize=14)
            plt.ylim([-0.05, 1.05])
            plt.legend(fontsize=13)
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")
            plt.tight_layout()
            plt.savefig(cached_result_foldername + 'Negative_Saturations_%s_%i'%(self.lab_type, ind))
            plt.clf()




    ######################################
    '''
    refactoring
    '''




    '''
    refactoring
    '''
    ######################################

    ######################################
    '''
    refactored
    '''

    def plot_order_intensities_barh(self, lab, time_since_last_order_binned, columns, scale,
                                    labeling=True, lab_ind=None):

        alphas = [1, 0.5, 0.2, 0.1]
        colors = ['black', 'blue', 'blue', 'blue']

        local_lab_descriptions = {
            'LABCBCD': 'CBC WITH\nDIFF',
            'LABPHOS': 'PHOSPHORUS\nSERUM/PLASMA',
            'LABA1C': 'HEMOGLOBIN\nA1C',
            'LABALB': 'ALBUMIN\nSERUM/PLASMA',
            'LABTSH': 'THYROID\nSIMULATING\nHORMONE',
            'LABESRP': 'SEDIMENTATION\nRATE (ESR)'
        }

        lab_descriptions = self.lab_descriptions

        pre_sum = 0
        pre_sums = []
        for key in columns:
            pre_sum += time_since_last_order_binned[key]
            pre_sums.append(pre_sum)

        for i in range(len(columns)-1,-1,-1):
            key = columns[i]
            pre_sum = pre_sums[i]

            lab_descriptions['LABTSH'] = 'TSH'
            lab_descriptions['LABESRP'] = 'Sedimentation Rate'
            lab_descriptions['LABCBCD'] = 'CBC w/ Diff'
            lab_descriptions['LABPTT'] = 'PTT'
            lab_descriptions['LABHEPAR'] = 'Heparin Activity Level'
            lab_descriptions['LABLIDOL'] = 'Lidocaine Level'
            lab_desciption = lab_descriptions.get(lab, lab)

            if labeling:
                plt.barh([lab_desciption], pre_sum, color=colors[i], alpha=alphas[i], label=key)
            else:
                plt.barh([lab_desciption], pre_sum, color=colors[i], alpha=alphas[i])

    def draw__Order_Intensities(self, stats_folderpath, labs,
                                scale=1., result_label=None, scale_method = 'normalize',
                                use_cached_fig_data=True, to_annotate_percentages=False,
                                include_legend=True):


        '''
        Drawing Figure 2 in the main text.

        :param self.lab_type:
        :return:
        '''

        '''
        Get labs
        '''
        print "Labs to be plot:", labs

        cached_result_foldername = os.path.join(stats_folderpath, 'Fig2_Order_Intensities/')
        if not os.path.exists(cached_result_foldername):
            os.mkdir(cached_result_foldername)
        cached_result_filename = 'Order_Intensities_%s_%s.csv'%(self.lab_type, result_label)
        cached_result_path = os.path.join(cached_result_foldername, cached_result_filename)

        '''
        Each lab 
            -> all its orders in 2014/07-2017/06 (implicit) 
            -> {time since last order:cnts} (cached)
            -> {0-1 days: cnt, 1-3 days: ...} 
            -> barh
        '''
        lab2stats = {}
        columns = ['< 24 hrs', '[24 hrs, 3 days)', '[3 days, 1 week)', '>= 1 week']

        if os.path.exists(cached_result_path) and use_cached_fig_data:
            lab2stats_pd = pd.read_csv(cached_result_path)
            lab2stats_pd = lab2stats_pd.rename(columns={'< 1 day':'< 24 hrs',
                                                        '1-3 days':'[24 hrs, 3 days)',
                                                        '3-7 days':'[3 days, 1 week)',
                                                        '> 7 days':'>= 1 week'})
            lab2stats = lab2stats_pd.set_index('lab').to_dict(orient='index')

        else:
            for lab in labs:
                print 'Getting Order Intensities of lab %s..'%lab

                df_lab = stats_utils.get_queried_lab(lab, self.lab_type, time_limit=DEFAULT_TIMELIMIT)

                dict_lab = stats_utils.get_floored_day_to_number_orders_cnts(lab, df_lab)

                day_counts = [0] * 4
                tot_cnt = 0
                for time, cnt in dict_lab.items():
                    if 0 <= time < 1:
                        day_counts[0] += cnt
                    elif 1 <= time < 3:
                        day_counts[1] += cnt
                    elif 3 <= time < 7:
                        day_counts[2] += cnt
                    elif time >= 7:
                        day_counts[3] += cnt
                    else:
                        print "time is out of range:", time
                    tot_cnt += cnt

                lab2stats[lab] = dict(zip(columns, day_counts))

            df_res = pd.DataFrame.from_dict(lab2stats, orient='index').reset_index().rename(columns={'index':'lab'})

            df_res.to_csv(cached_result_path, index=False)

        for lab, stats in lab2stats.items():
            stats['total'] = float(sum(stats.values()))

        labs_ordered = sorted(labs, key=lambda x: lab2stats[x]['< 24 hrs']/lab2stats[x]['total'], reverse=True) #< 24 hrs

        labs_toplots = [labs_ordered]

        for ind_toplot, labs_toplot in enumerate(labs_toplots):
            fig, ax = plt.subplots(figsize=(8, .3 + 5.7/20.*len(labs))) #5+ 3./20.*len(labs)
            # 8, 3.435 for guideline
            # 8, 6 for freq labs
            # 6 - 3.435 = 2.565
            # Size for saturation is 7, 2.565 ?
            print .3 + 5.7/20.*len(labs)
            for i, lab in enumerate(labs_toplot[::-1]):

                time_since_last_order_binned = lab2stats[lab]


                for time, cnt in time_since_last_order_binned.items():
                    if time == 'total':
                        continue
                    if scale_method == 'normalize':
                        time_since_last_order_binned[time] = cnt/time_since_last_order_binned['total']

                    elif scale_method == 'by_scale':
                        time_since_last_order_binned[time] = cnt*scale

                if i == 0:
                    self.plot_order_intensities_barh(lab, time_since_last_order_binned,
                                                     columns=columns,
                                                     labeling=True,
                                                     lab_ind=i,
                                                     scale=scale)
                else:
                    self.plot_order_intensities_barh(lab, time_since_last_order_binned,
                                                     columns=columns,
                                                     labeling=False,
                                                     lab_ind=i,
                                                     scale=scale)

            if scale_method == 'normalize':
                ax.set_xticklabels(['{:,.0%}'.format(x) for x in np.linspace(0,1,num=6)])
                plt.tick_params('x', labelsize=13)
                plt.tick_params('y', labelsize=11)
                plt.xlim([0,1])
            else:
                plt.tick_params('x', labelsize=15) #12
                plt.tick_params('y', labelsize=13) #10

            if result_label != 'labs_guideline':
                plt.xlabel('Number of orders per 1000 patient encounters', fontsize=14) #'Order number between 2014/07-2017/06'

            if include_legend:
                plt.legend(prop={'size': 12})
            else:
                ax.yaxis.tick_right()
                ax.yaxis.set_label_position("right")
                pass
            # plt.xscale('log')

            plt.tight_layout()
            cached_result_folderpath = cached_result_foldername + 'Order_Intensities_%s_%i_%s.png'%(self.lab_type,ind_toplot,result_label)

            if to_annotate_percentages:
                cached_result_folderpath.replace('.png', '_formal_1.png')
                # plt.xlim([0,5000])

            plt.savefig(cached_result_folderpath)
            plt.clf()


    def draw__stats_Curves(self, statsByLab_folderpath, labs, curve_type="ROC", algs=['random-forest'], result_label=None,
                           include_baseline=True, inverse01=False):
        result_foldername = 'Fig_stats_Curves'
        if result_label:
            result_foldername += '_' + result_label
        result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
        if not os.path.exists(result_folderpath):
            os.mkdir(result_folderpath)

        result_figname = '%s_%s_%s.png'%(self.data_source, self.lab_type, curve_type)
        result_figpath = os.path.join(result_folderpath, result_figname)

        result_tablename = '%s_%s_%s.csv'%(self.data_source, self.lab_type, curve_type)
        result_tablepath = os.path.join(result_folderpath, result_tablename)

        num_labs = len(labs)
        # fig, ax = plt.subplots(figsize=(12, 6))

        row, col, i_s, j_s = stats_utils.prepare_subfigs(num_labs, col=7) #7

        scores_base = []
        scores_best = []
        p_vals = []

        scores_diffs = {}

        lab_descriptions = stats_utils.get_lab_descriptions(lab_type=self.lab_type,
                                                            data_source=self.data_source,
                                                            line_break_at=18)
        for ind, lab in enumerate(labs):

            '''
            Getting p-values is slow
            '''

            xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best, p_val \
                = stats_utils.get_curve_onelab(lab,
                                               all_algs=algs,
                                               data_folder=statsByLab_folderpath.replace("lab_statistics", "machine_learning"),
                                               curve_type=curve_type,
                                               get_pval=False)
            # print lab, p_val
            scores_base.append(score_base)
            scores_best.append(score_best)
            p_vals.append(p_val)

            scores_diffs[lab] = score_best - score_base

            i, j = i_s[ind], j_s[ind]
            plt.subplot2grid((row, col), (i, j))

            dash_num = 20
            plt.plot(np.linspace(0, 1, num=dash_num), np.linspace(0, 1, num=dash_num), color='lightblue',
                     linestyle='--')

            if not inverse01:
                plt.plot(xVal_best, yVal_best, label='%0.2f' % (score_best), color='orange')
                if include_baseline:
                    plt.plot(xVal_base, yVal_base, label='%0.2f' % (score_base))
            else:
                plt.plot(1-yVal_best, 1-xVal_best, label='%0.2f' % (score_best), color='orange')
                if include_baseline:
                    plt.plot(1 - yVal_base, 1 - xVal_base, label='%0.2f' % (score_base))

            plt.xlim([0,1])
            plt.ylim([0,1])
            plt.xticks([])
            plt.yticks([])

            lab_descrip = lab_descriptions.get(lab, lab)
            if self.data_source == 'UCSF':
                lab_descrip = lab_descrip[:18] + '\n' + lab_descrip[18:]
            plt.xlabel(lab_descrip)
            plt.legend()


        plt.tight_layout()
        plt.savefig(result_figpath)

        measures = {'ROC': 'AUC (Area Under Curve)', 'PRC': 'APS (Average Precision Score)'}
        avg_base, avg_best = np.mean(scores_base), np.mean(scores_best)
        print "Average %s among %i labs: %.3f baseline, %.3f bestalg (an improvement of %.3f)." \
              % (measures[curve_type], len(scores_base), avg_base, avg_best, avg_best - avg_base)

        df_output_table = pd.DataFrame({'lab':labs,
                                        curve_type+' benchmark':scores_base,
                                        curve_type + ' ML model':scores_best,
                                        curve_type + ' p value':p_vals
                           })
        df_output_table['lab'] = df_output_table['lab'].apply(lambda x: self.lab_descriptions.get(x,x)) #
        df_output_table[curve_type + ' significance'] = df_output_table[curve_type + ' p value'].apply(lambda x: stats_utils.map_pval_significance(x))
        df_output_table[['lab',curve_type+' benchmark',curve_type + ' ML model',curve_type + ' p value',curve_type + ' significance']]\
            .to_csv(result_tablepath, index=False, float_format="%.2f")








    '''
    refactored
    '''
    ######################################




    def draw_histogram_transfer_modeling(self, src_dataset='Stanford', dst_dataset='UCSF', lab_type='panel'):
        print "Running draw_histogram_transfer_modeling..."

        from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import STRIDE_COMPONENT_TESTS

        ml_folder = ml_results_folderpath

        '''
        
        '''
        panels_stanford = ['LABMGN', 'LABK', 'LABNA', 'LABPHOS', 'LABURIC', 'LABTNI',
                           'LABPT', 'LABPTT', 'LABCAI', 'LABALB', 'LABTSH'
                ]

        if self.lab_type == 'panel':
            labs = panels_stanford
            from scripts.LabTestAnalysis.machine_learning.ml_utils import map_panel_from_Stanford_to_UCSF as map_lab
        else:
            labs = STRIDE_COMPONENT_TESTS
            from scripts.LabTestAnalysis.machine_learning.ml_utils import map_component_from_Stanford_to_UCSF as map_lab

        result_ml_foldername = 'data-Stanford-%s-%s-%s' % (dst_dataset, self.lab_type, self.curr_version)
        result_ml_folderpath = os.path.join(ml_folder, result_ml_foldername)
        if not os.path.exists(result_ml_folderpath):
            os.mkdir(result_ml_folderpath)

        result_figname = 'curves_model_transfering.png'
        result_figpath = os.path.join(result_ml_folderpath.replace('machine_learning', 'lab_statistics'), result_figname)

        dst_foldername = 'data-%s-%s-%s' % (dst_dataset, self.lab_type, self.curr_version)
        dst_folderpath = os.path.join(ml_folder, dst_foldername)

        # labs2curves = {}
        row, col, i_s, j_s = stats_utils.prepare_subfigs(num_figs=len(labs), col=6)

        for ind, lab in enumerate(labs):

            '''
            Model transfering
            '''
            xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best, p_val\
                    = stats_utils.get_curve_onelab(lab,
                                                   all_algs=all_algs,
                                                   data_folder=result_ml_folderpath,
                                                   curve_type='ROC',
                                                   get_pval=False,
                                                   get_baseline=False
                                                   )
            score_transfer = score_best
            xVal_transfer = xVal_best
            yVal_transfer = yVal_best

            '''
            Locally trained
            '''
            xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best, p_val \
                = stats_utils.get_curve_onelab(lab,
                                               all_algs=all_algs,
                                               data_folder=dst_folderpath,
                                               curve_type='ROC',
                                               get_pval=False,
                                               get_baseline=True
                                               )
            # labs2curves['xVal_bese_local'] = xVal_base
            # labs2curves['yVal_bese_local'] = yVal_base
            #
            # labs2curves['xVal_best_local'] = xVal_best
            # labs2curves['yVal_best_local'] = yVal_best

            i, j = i_s[ind], j_s[ind]
            print i,j
            plt.subplot2grid((row, col), (i, j))

            # plt.plot(xVal_base, yVal_base, label='%0.2f' % (score_base), color='blue')
            plt.plot(xVal_transfer, yVal_transfer, label='%0.2f' % (score_transfer), color='green')
            plt.plot(xVal_best, yVal_best, label='%0.2f' % (score_best), color='orange')
            plt.xlim([0, 1])
            plt.ylim([0, 1])
            plt.xticks([])
            plt.yticks([])
            plt.xlabel(self.lab_descriptions.get(lab, lab))
            plt.legend()

        plt.tight_layout()
        plt.savefig(result_figpath)

    def plot_full_cartoon(self, lab='LABLDH', include_threshold_colors=True, inverse01=False):
        print 'Running plot_full_cartoon...'

        inverse_maker = '_inversed01' if inverse01 else ''

        statsByLab_folderpath = '/Users/songxu/healthrex/CDSS/scripts/LabTestAnalysis/lab_statistics/data-%s-%s-%s/'%(self.data_source,self.lab_type,self.curr_version)
        ml_folderpath = statsByLab_folderpath.replace("lab_statistics", "machine_learning")

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
        plt.savefig(os.path.join(statsByLab_folderpath, 'ROC_%s%s.png'%(lab,inverse_maker)))

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
            plt.savefig(os.path.join(statsByLab_folderpath, 'cartoon_%s_thres%s.png' % (lab, inverse_maker)))
        else:
            plt.savefig(os.path.join(statsByLab_folderpath, 'cartoon_%s%s.png' % (lab, inverse_maker)))



    '''
    For each (train-)PPV wanted, each vital-day dataset
    Create a summary of all algs' performances on all labs
    '''

    def main_labs2stats(self, train_data_folderpath, ml_results_folderpath, stats_results_folderpath,
                        targeted_PPVs=train_PPVs, columns=None, thres_mode="fixTrainPPV",verbose=True):
        '''
        For each lab at each train_PPV,
        write all stats (e.g. roc_auc, PPV, total cnts) into csv file.

        Output table's columns for a Stanford panel:
        - lab
        - total_vol_20140701_20170701
        - num_train_episodes
        - num_train_patients
        - num_test_episodes
        - num_test_patients
        - alg
        - AUC
        - AUC_95%_CI
        - AUC_baseline (last_normality + train population mean)
        - fixTrainPPV
        - score_thres
        - TP
        - FP
        - TN
        - FN
        - sens
        - spec
        - LR_p
        - LR_n
        - PPV
        - NPV
        - medicare
        - chargemaster

        '''

        '''
        Chargemaster pricing. 
        
        For some reason, there is no entry for LABNA
        '''

        chargemaster_filepath = os.path.join(labs_old_stats_folder, 'labs_charges_volumes.csv')
        df_chargemaster = pd.read_csv(chargemaster_filepath)
        lab_to_chargemaster_median = dict(zip(df_chargemaster['name'], df_chargemaster['median_price']))
        lab_to_chargemaster_median['LABNA'] = 219.

        '''
        Medicare pricing. 
        '''
        lab_to_medicare = stats_utils.get_medicare_price_dict()

        for lab in self.all_labs:
            stats_results_filepath = os.path.join(stats_results_folderpath, 'stats_by_lab_alg', '%s.csv' % lab)
            if not os.path.exists(os.path.join(stats_results_folderpath, 'stats_by_lab_alg')):
                os.mkdir(os.path.join(stats_results_folderpath, 'stats_by_lab_alg'))
            if os.path.exists(stats_results_filepath):
                if verbose:
                    print "lab stats for %s exists!" % lab
                continue
            else:
                print "processing lab stats for %s" % lab


            df_lab2stats = pd.DataFrame(columns=columns) #
            '''
            lab, total_vol_20140701_20170701, medicare, chargemaster, 
            num_train_episodes, num_train_patients, num_test_episodes, num_test_patients, 
            AUC_baseline
            '''
            lab_vol = stats_utils.get_labvol(lab=lab,
                                             lab_type=self.lab_type,
                                             data_source=self.data_source,
                                             time_limit=DEFAULT_TIMELIMIT)

            chargemaster = lab_to_chargemaster_median.get(lab, float('nan'))
            medicare = lab_to_medicare.get(lab, float('nan'))

            num_train_episodes, num_train_patient, num_test_episodes, num_test_patient = \
                stats_utils.describe_lab_train_test_datasets(lab, train_data_folderpath)

            AUC_baseline = stats_utils.get_baseline2_auroc(os.path.join(train_data_folderpath, lab))

            lab_to_stats_meta = {}
            lab_to_stats_meta['lab'] = lab
            lab_to_stats_meta['total_vol_20140701_20170701'] = lab_vol
            lab_to_stats_meta['chargemaster'] = chargemaster
            lab_to_stats_meta['medicare'] = medicare
            lab_to_stats_meta['num_train_episodes'] = num_train_episodes
            lab_to_stats_meta['num_train_patient'] = num_train_patient
            lab_to_stats_meta['num_test_episodes'] = num_test_episodes
            lab_to_stats_meta['num_test_patient'] = num_test_patient
            lab_to_stats_meta['AUC_baseline'] = AUC_baseline

            for targeted_PPV in targeted_PPVs:
                lab_to_stats = copy.deepcopy(lab_to_stats_meta) #lab_to_stats_meta.copy()
                lab_to_stats['fixTrainPPV'] = targeted_PPV
                # try:
                #stats_results_filename = results_filename_template % (lab, thres_mode, str(targeted_PPV))


                for alg in all_algs:
                    lab_to_stats['alg'] = alg

                    df_direct_compare = pd.read_csv(
                        ml_results_folderpath + '/' + lab + '/' + alg + '/' + 'direct_comparisons.csv',
                        # '%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg),
                        keep_default_na=False)
                    actual_labels, predict_scores = df_direct_compare['actual'].values, df_direct_compare[
                        'predict'].values

                    lab_to_stats['AUC'] = stats_utils.get_safe(roc_auc_score, actual_labels, predict_scores)
                    AUROC_left, AUROC_right = stats_utils.bootstrap_CI(actual_labels, predict_scores, confident_lvl=0.95)
                    lab_to_stats['AUC_95%_CI'] = '[%f, %f]' % (AUROC_left, AUROC_right)

                    if thres_mode == 'fixTestPPV':
                        score_thres = stats_utils.pick_threshold(actual_labels, predict_scores,
                                                     target_PPV=targeted_PPV)  # TODO!
                    else:
                        df_direct_compare_train = pd.read_csv(
                            ml_results_folderpath + '/' + lab + '/' + alg + '/' + 'direct_comparisons_train.csv',
                            # '%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg),
                            keep_default_na=False)
                        actual_labels_train, predict_scores_train = df_direct_compare_train['actual'].values, \
                                                                    df_direct_compare_train['predict'].values
                        score_thres = stats_utils.pick_threshold(actual_labels_train, predict_scores_train,
                                                     target_PPV=targeted_PPV)

                    lab_to_stats['score_thres'] = score_thres

                    TP, FP, TN, FN, sens, spec, LR_p, LR_n, PPV, NPV = stats_utils.get_confusion_metrics(actual_labels,
                                                                                           predict_scores,
                                                                                           threshold=score_thres,
                                                                                           also_return_cnts=True)

                    lab_to_stats.update({
                        'TP': TP / float(num_test_episodes),
                        'FP': FP / float(num_test_episodes),
                        'TN': TN / float(num_test_episodes),
                        'FN': FN / float(num_test_episodes),
                        'sens': sens,
                        'spec': spec,
                        'LR_p': LR_p,
                        'LR_n': LR_n,
                        'PPV': PPV,
                        'NPV': NPV
                    })
                    df_lab2stats = df_lab2stats.append(lab_to_stats, ignore_index=True)

                df_lab2stats[columns].to_csv(stats_results_filepath, index=False)

    def main_stats2summary(self, targeted_PPVs=train_PPVs, columns=None, thres_mode="fixTrainPPV"):

        df_long = pd.DataFrame(columns=columns)

        columns_best_alg = [x if x != 'alg' else 'best_alg' for x in columns]
        df_best_alg = pd.DataFrame(columns=columns_best_alg)

        project_stats_folderpath = os.path.join(stats_results_folderpath, self.dataset_foldername)

        for lab in self.all_labs:
            # for targeted_PPV in targeted_PPVs:
            stats_results_filepath = os.path.join(project_stats_folderpath, 'stats_by_lab_alg', '%s.csv'%lab)

            df_lab = pd.read_csv(stats_results_filepath, keep_default_na=False)

            df_long = df_long.append(df_lab, ignore_index=True)

            idx_bestalgs = df_lab.groupby(['lab', 'fixTrainPPV'])['AUC'].transform(max) == df_lab['AUC']
            df_cur_bestalg = df_lab[idx_bestalgs]

            # df_cur_best_alg = df_lab.groupby(['lab', 'fixTrainPPV'])['AUC'].max()
            # df_cur_best_alg = pd.merge(df_cur_best_alg, df_lab, on=['lab', 'AUC'], how='left')

            df_cur_best_alg = df_cur_bestalg.rename(columns={'alg': 'best_alg'})
            df_best_alg = df_best_alg.append(df_cur_best_alg)

        # '''
        # TODO:!
        # '''
        # if self.lab_type=='panel' and self.data_source=='Stanford':
        #     df_chargemasters = pd.read_csv('data_summary_stats/labs_charges_volumes.csv', keep_default_na=False)
        #     df_chargemasters = df_chargemasters.rename(columns={'name':'lab', 'median_price':'chargemaster'})
        #     df_long = df_long.drop(['chargemaster'], axis=1)
        #     df_long = pd.merge(df_long, df_chargemasters[['lab', 'chargemaster']], on='lab', how='left')
        #
        #     df_best_alg = df_best_alg.drop(['chargemaster'], axis=1)
        #     df_best_alg = pd.merge(df_best_alg, df_chargemasters[['lab', 'chargemaster']], on='lab', how='left')

        summary_long_filename = 'summary-stats-%s-%s.csv' % ('allalgs', thres_mode)
        summary_long_filepath = os.path.join(project_stats_folderpath, summary_long_filename)

        for col in ['AUC', 'AUC_baseline', 'score_thres',
                 'TP', 'FP', 'TN', 'FN',
                 'sens', 'spec', 'LR_p', 'LR_n', 'PPV', 'NPV']:
            if df_long[col].dtype == df_long['lab'].dtype:
                df_long[col] = df_long[col].apply(lambda x: stats_utils.convert_floatstr2num(x))

        def handle_AUC_CI(astr):
            strs = astr.split('.')
            strs[1] = strs[1][:2] + strs[1][-3:]
            strs[2] = strs[2][:2] +strs[2][-1]
            return '.'.join(strs)

        df_long['AUC_95%_CI'] = df_long['AUC_95%_CI'].apply(lambda x: handle_AUC_CI(x))

        rename_alg = {'xgb':'xgboost', 'nn':'neural-nets'}
        df_long['alg'] = df_long['alg'].apply(lambda x: rename_alg.get(x,x))

        df_long[columns].to_csv(summary_long_filepath, index=False, float_format='%.2f')

        summary_best_filename = 'summary-stats-%s-%s.csv' % ('bestalg', thres_mode)
        summary_best_filepath = os.path.join(project_stats_folderpath, summary_best_filename)
        df_best_alg[columns_best_alg].to_csv(summary_best_filepath, index=False)

        # df_long[columns].to_csv(summary_filepath_template%('allalgs', thres_mode), index=False)
        # df_best_alg[columns_best_alg].to_csv(summary_filepath_template%('bestalg', thres_mode), index=False)

    def write_importantFeatures(self):
        stats_utils.output_feature_importances(self.all_labs,
                                               data_source=self.data_source,
                                               lab_type=self.lab_type,
                                               curr_version=self.curr_version)
        return

    def main_attachBaseline(self, targeted_PPVs, columns, thres_mode):
        '''

        Args:
            targeted_PPVs:
            columns:
            thres_mode:

        Returns:

        '''

        '''
        Load summary-stats-bestalg-fixTrainPPV.csv
        '''
        summary_best_filename = 'summary-stats-%s-%s.csv' % ('bestalg', thres_mode)
        summary_best_filepath = os.path.join(stats_results_folderpath, summary_best_filename)
        df_best_alg = pd.read_csv(summary_best_filepath, keep_default_na=False)
        # print df_best_alg.head()

        '''
        Get Baseline results for each lab
        '''

        print columns

    def main_basic_tables(self, train_data_folderpath, ml_results_folderpath, stats_results_folderpath, thres_mode="fixTrainPPV",
                          verbose=True):
        '''
        Performance on test set, by choosing a threshold whether from train or test.

        Args:
            lab_type:
            thres_mode:

        Returns:

        '''

        '''
        Shared columns
        '''
        columns = ['lab', 'total_vol_20140701_20170701', 'num_train_episodes', 'num_train_patient', 'num_test_episodes', 'num_test_patient']
        columns += ['alg', 'AUC', 'AUC_95%_CI', 'AUC_baseline']
        columns += [thres_mode]

        columns_statsMetrics = []
        columns_statsMetrics += ['score_thres', 'TP', 'FP', 'TN', 'FN']
        columns_statsMetrics += ['sens', 'spec', 'LR_p', 'LR_n', 'PPV', 'NPV']

        columns += columns_statsMetrics

        columns_STRIDE = columns[:]
        # columns_STRIDE += ['%s count'%x for x in DEFAULT_TIMEWINDOWS]

        columns_panels = columns_STRIDE[:] + ['medicare', 'chargemaster']  # ['min_price', 'max_price', 'mean_price', 'median_price']
        # 'min_volume_charge', 'max_volume_charge', 'mean_volume_charge', 'median_volume_charge'
        columns_components = columns_STRIDE[:]

        columns_UMichs = columns[:]

        if self.data_source == 'Stanford':
            if self.lab_type == 'panel':
                columns = columns_panels
            elif self.lab_type == 'component':
                columns = columns_components
        elif self.lab_type == 'UMich':
            columns = columns_UMichs

        self.main_labs2stats(train_data_folderpath=train_data_folderpath,
                        ml_results_folderpath=ml_results_folderpath,
                        stats_results_folderpath=stats_results_folderpath,
                        targeted_PPVs=train_PPVs,
                        columns=columns,
                        thres_mode=thres_mode,
                             verbose=verbose)

        self.main_stats2summary(targeted_PPVs=train_PPVs,
                           columns=columns,
                           thres_mode=thres_mode)

        # self.main_attachBaseline(targeted_PPVs=train_PPVs,
        #                     columns=[x + '_baseline' for x in columns_statsMetrics],
        #                     thres_mode=thres_mode)

    def main_generate_lab_statistics(self, verbose=True):
        print 'Generating lab-wise tables...'

        project_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
        train_data_folderpath = os.path.join(project_folder, 'machine_learning/',
                                             'data-%s-%s-%s' % (
                                             self.data_source, self.lab_type, self.curr_version)
                                             )
        ml_results_folderpath = os.path.join(project_folder, 'machine_learning/',
                                             # 'results-from-panels-10000-to-panels-5000-part-1'
                                             'data-%s-%s-%s' % (
                                             self.data_source, self.lab_type, self.curr_version)
                                             )

        stats_results_folderpath = ml_results_folderpath.replace('machine_learning', 'lab_statistics')

        if not os.path.exists(stats_results_folderpath):
            os.mkdir(stats_results_folderpath)

        self.main_basic_tables(train_data_folderpath=train_data_folderpath,
             ml_results_folderpath=ml_results_folderpath,
             stats_results_folderpath=stats_results_folderpath,
             thres_mode="fixTrainPPV",
                               verbose=verbose)

    def main_generate_stats_figures_tables(self, figs_to_plot, params={}, inverse01=False):
        print 'Generating figures and tables %s...' % str(figs_to_plot)

        '''
        scale by each 1000 patient encounter
        '''
        scale = 1. / stats_utils.NUM_DISTINCT_ENCS * 1000

        stats_folderpath = os.path.join(stats_utils.main_folder, 'lab_statistics/')
        ml_folderpath = os.path.join(stats_utils.main_folder, 'machine_learning')

        import LocalEnv
        statsByDataSet_foldername = 'data-%s-%s-%s' % (self.data_source, self.lab_type, self.curr_version)
        statsByDataSet_folderpath = os.path.join(stats_folderpath, statsByDataSet_foldername)
        if not os.path.exists(statsByDataSet_folderpath):
            os.mkdir(statsByDataSet_folderpath)

        labs_guideline_nested = stats_utils.get_guideline_maxorderfreq().values()
        labs_guideline = [lab for sublist in labs_guideline_nested for lab in sublist]
        labs_guideline = [x for x in labs_guideline if x!='LABCBCD' and x!='LABPHOS']
        labs_guideline += ['LABCRP', # C - REACTIVE PROTEIN
                           #'LABAFP', # ALPHA FETOPROTEIN, SERUM
                           'LABYCP', # C - PEPTIDE, SERUM
                           'LABLIPS', # LIPASE
                           # 'LABEP1', # ELECTROLYTE PANEL
                           'LABAGALA', # ASPERGILLUS GALACTOMANNAN
                           'LABNTBNP',
                           # 'LABPROCT'
                           #'LABYHISTS', # HISTOPLASMA AG, SERUM
                           #'LABSPIE', # PROTEIN IMMUNOFIX ELECTROPHORESIS, SERUM
                           #'LABUPIE' # URINE PROTEIN IMMUNOFIXATION ELECTROPHORESIS
                           ]

        labs_common_panels = ['LABMETB', 'LABCBCD']

        if 'Comparing_Components' in figs_to_plot:
            self.comparing_components(stats_folderpath)

        if 'Order_Intensities' in figs_to_plot:
            classic_labs = list(set(labs_common_panels + labs_guideline + stats_utils.get_important_labs()))

            import stats_database
            '''
            Choose 20 labs
            '''
            labs_cnts_order_1day = stats_database.TOP_PANELS_AND_COUNTS_IN_1DAY[:20]
            labs_order_1day = [x[0] for x in labs_cnts_order_1day]

            # lab_set, lab_label = labs_guideline, 'labs_guideline' # labs_guideline, 'labs_guideline'    labs_order_1day, 'labs_order_1day'

            self.draw__Order_Intensities(statsByDataSet_folderpath, labs=labs_guideline, result_label='labs_guideline',
                                    scale=scale, use_cached_fig_data=True, scale_method = 'normalize', #normalize
                                    to_annotate_percentages=False, include_legend=False)

            self.draw__Order_Intensities(statsByDataSet_folderpath, labs=labs_order_1day, result_label='labs_order_1day',
                                         scale=scale, use_cached_fig_data=True, scale_method = 'by_scale',
                                         to_annotate_percentages=False, include_legend=True)

        if 'Normality_Saturations' in figs_to_plot:
            labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels) - set(['LABTSH', 'LABLDH']))

            panels_saturations = ['LABPHOS', 'LABA1C', 'LABALB', 'LABTSH', 'LABESRP'] #'LABCBCD',

            components_saturations = ['WBC', 'HGB', 'NA', 'K', 'CR'] #, 'PLT'

            if self.lab_type=='panel':
                labs = panels_saturations
            else:
                labs = components_saturations
            print statsByDataSet_folderpath

            self.draw__Normality_Saturations(statsByDataSet_folderpath, labs=labs, use_cached_fig_data=True)

        if 'PPV_distribution' in figs_to_plot:
            # PPV_guideline(statsByDataSet_folderpath) #TODO
            self.get_best_calibrated_labs(statsByDataSet_folderpath, worst=False)

        if 'Savable_Fractions' in figs_to_plot:
            self.draw__Comparing_Savable_Fractions(statsByDataSet_folderpath, target_PPV=0.95, use_cache=True)

        if 'Comparing_PPVs' in figs_to_plot:
            self.draw__Comparing_PPVs(statsByDataSet_folderpath)

        if 'ROC' in figs_to_plot or 'PRC' in figs_to_plot:
            '''
            1. typical labs are for show in the main text
    
            2. all labs for putting in the Appendix
            '''
            typical_labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels))

            lab_set, set_label = self.all_labs, 'all_labs'  # typical_labs, 'typical_labs'

            if 'ROC' in figs_to_plot:
                top_improved_labs = ['LABBUN', 'LABUOSM', 'LABSTOBGD', 'LABPCCR', 'LABFE', 'LABCRP', 'LABPCTNI',
                                     'LABK', 'LABPLTS', 'LABPT', 'LABCDTPCR', 'LABALB', 'LABHIVWBL', 'LABPTEG',
                                     'LABESRP', 'LABUPREG', 'LABPROCT', 'LABPALB', 'LABCORT', 'LABPCCG4O', 'LABTRFS',
                                     'LABCSFTP', 'LABDIGL', 'LABNTBNP', 'LABURIC', 'LABHEPAR', 'LABMGN', 'LABLAC',
                                     'LABLIDOL', 'LABHCTX', 'LABPTT', 'LABCA', 'LABRETIC', 'LABSPLAC', 'LABTRIG']
                # lab_set, set_label = top_improved_labs, 'top_improved_labs'
                self.draw__stats_Curves(statsByDataSet_folderpath, lab_set, curve_type="ROC", algs=all_algs,
                                   result_label=set_label, inverse01=inverse01)
            if 'PRC' in figs_to_plot:
                self.draw__stats_Curves(statsByDataSet_folderpath, lab_set, curve_type="PRC", algs=all_algs,
                                   result_label=set_label, inverse01=inverse01)

            merge_ROC_PRC = False
            if merge_ROC_PRC:
                df_ROC = pd.read_csv(os.path.join(statsByDataSet_folderpath, 'Fig_stats_Curves_all_labs',
                                                  '%s_%s_ROC.csv' % (self.data_source, self.lab_type)), keep_default_na=False)
                df_PRC = pd.read_csv(os.path.join(statsByDataSet_folderpath, 'Fig_stats_Curves_all_labs',
                                                  '%s_%s_PRC.csv' % (self.data_source, self.lab_type)), keep_default_na=False)

                df_combined = pd.merge(df_ROC, df_PRC, on='lab', how='left')
                df_combined.pop('ROC p value')
                df_combined.pop('PRC p value')
                df_combined.to_csv(os.path.join(statsByDataSet_folderpath, 'Fig_stats_Curves_all_labs',
                                                '%s_%s_ROC_PRC.csv' % (self.data_source, self.lab_type)),
                                   index=False)

        if 'plot_cartoons' in figs_to_plot:
            self.plot_cartoons(os.path.join(ml_folderpath, statsByDataSet_foldername))

        if 'Diagnostic_Metrics' in figs_to_plot:
            top_panels_cnts = stats_utils.get_top_labs_and_cnts(lab_type=self.lab_type, top_k=20)
            top_panels = [x[0] for x in top_panels_cnts]
            panels = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels)) + ['LABK', 'LABNA', 'LABLIDOL'] #, 'LABCR', 'LABPTT', 'LABCAI'
            components = ['WBC', 'HGB', 'PLT', 'NA', 'K', 'CL', 'CR', 'BUN', 'CO2', 'CA',
                          'TP', 'ALB', 'ALKP', 'TBIL', 'AST', 'ALT', 'DBIL', 'IBIL', 'PHA']
            important_components = stats_utils.get_important_labs('component')

            result_label = params.get('Diagnostic_Metrics', 'all_labs')

            if self.data_source == 'Stanford':
                if self.lab_type == 'panel':
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label,
                                            targeted_PPV=0.95, scale_by='enc', use_cached_fig_data=False, inverse01=inverse01)
                else:
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label,
                                            targeted_PPV=0.95, scale_by='enc', use_cached_fig_data=False, inverse01=inverse01)
            elif self.data_source == 'UCSF':
                self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label,
                                        targeted_PPV=0.95, scale_by='enc_ucsf', use_cached_fig_data=False, inverse01=inverse01)

            elif self.data_source == 'UMich':
                if self.lab_type == 'component':
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label, #important_components
                                            targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False, inverse01=inverse01)
                else:
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs,
                                                 result_label=result_label,
                                                 targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False, inverse01=inverse01)

        if 'Predicted_Normal' in figs_to_plot:
            self.draw__predicted_normal_fractions(statsByLab_folderpath=statsByDataSet_folderpath, targeted_PPV=0.95)

        if 'Potential_Savings' in figs_to_plot:
            self.draw__Potential_Savings(statsByDataSet_folderpath, scale=scale, result_label='all_four',
                                    targeted_PPV=0.95, use_cached_fig_data=False, price_source='medicare')

        if 'Model_Transfering' in figs_to_plot:
            self.draw_histogram_transfer_modeling()

        if 'Full_Cartoon' in figs_to_plot:
            self.plot_full_cartoon(lab='LABLDH', include_threshold_colors=False, inverse01=True)
            self.plot_full_cartoon(lab='LABLDH', include_threshold_colors=True, inverse01=True)


        if 'write_importantFeatures' in figs_to_plot:
            self.write_importantFeatures()



def get_AUC_transfer_labs(src_dataset='Stanford', dst_dataset='UCSF', lab_type='panel', curr_version='10000-episodes'):
    if lab_type == 'panel':
        labs = ['LABURIC']
        # from scripts.LabTestAnalysis.machine_learning.ml_utils import map_panel_from_Stanford_to_UCSF as map_lab
    else:
        from scripts.LabTestAnalysis.lab_statistics import stats_utils
        labs = stats_utils.get_important_labs(lab_type=lab_type) #STRIDE_COMPONENT_TESTS
        # from scripts.LabTestAnalysis.machine_learning.ml_utils import map_component_from_Stanford_to_UCSF as map_lab

    transfer_result_folderpath = 'data-%s-src-%s-dst-%s-%s/'%(lab_type,src_dataset,dst_dataset, curr_version)
    if not os.path.exists(transfer_result_folderpath):
        os.mkdir(transfer_result_folderpath)

    res = []

    for lab in labs:
        direct_comparisons_folderpath = os.path.join(transfer_result_folderpath, lab)

        cur_AUC = statistic_analysis(lab=lab, dataset_folder=direct_comparisons_folderpath)

        res.append(cur_AUC)
    return res




def main_full_analysis(curr_version, inverse01=False):
    for data_source in ['Stanford', 'UCSF', 'UMich']: #'Stanford',
        for lab_type in ['panel', 'component']:

            plotter = Stats_Plotter(data_source=data_source, lab_type=lab_type, curr_version=curr_version)

            '''
            Two steps: 
            lab2stats: Getting lab-wise stats tables under lab_statistics/dataset_folder/stats_by_lab_alg/..
            stats2summary: Aggregate all labs' stats under lab_statistics/dataset_folder/..
            '''
            plotter.main_generate_lab_statistics(verbose=False)

            if data_source=='Stanford' and lab_type=='panel':
                plotter.main_generate_stats_figures_tables(figs_to_plot=[#'Full_Cartoon', # Figure 1
                                                                         #'Order_Intensities', # Figure 2
                                                                        'Diagnostic_Metrics', # Table 1 & SI Table
                                                                        # 'ROC',  # SI Figure
                                                                        #  'write_importantFeatures' # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'},
                    inverse01=inverse01) # TODO ['top_15', 'all_labs']

            elif data_source=='Stanford' and lab_type=='component':
                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                        'Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         # 'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'important_components'},
                    inverse01=inverse01)  # TODO ['common_components', 'all_labs']
                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                        # 'Normality_Saturations',
                                                                          'Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         # 'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'},
                                                           inverse01=inverse01)

            elif data_source=='UMich' and lab_type=='panel':
                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                        'Diagnostic_Metrics',  # SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         # 'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'},
                    inverse01=inverse01)  # TODO

            elif data_source=='UMich' and lab_type=='component':
                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                          'Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         # 'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'important_components'},
                                                           inverse01=inverse01)  # TODO

                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                        'Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         #'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'},
                                                           inverse01=inverse01)  # TODO

            elif data_source=='UCSF' and lab_type=='panel':
                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                        'Diagnostic_Metrics',  # SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         # 'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'},
                    inverse01=inverse01)  # TODO

            elif data_source=='UCSF' and lab_type=='component':
                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                         'Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         # 'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'important_components'},
                                                           inverse01=inverse01)  # TODO

                plotter.main_generate_stats_figures_tables(figs_to_plot=[
                                                                        'Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         # 'ROC',  # SI Figure
                                                                         #'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'},
                                                           inverse01=inverse01)  # TODO

    main_transfer_model(curr_version)


def main_one_analysis(curr_version):
    # list_of_figuretables = [
    #     'ROC', 'PRC',
    #     'Normality_Saturations',  # Normal rate saturates to 100% as number of consecutive normals accumulate.
    #     'Order_Intensities',  # Volumes of repeated test
    #     'plot_cartoons',  # all cartoons
    #     'write_importantFeatures',
    #
    #     'Diagnostic_Metrics',  # After picking a threshold
    #     'Potential_Savings',  # After scaled by chargemaster/medicare
    #
    #     'Model_Transfering',  #
    #     'Comparing_Components',  #
    # ]

    main_figuretables = [
        'LDH_cartoons', # main Figure 1
        'common_repeated_labs', # main Figure 2
        'panel_diagnostics_table', # main Table 1
        'component_compare_figure',  # main Figure 3
        'component_cross_site_aucs', # main Figure 4
    ]


    '''
    Params
    '''

    params = {
        'Diagnostic_Metrics': ['all_labs', 'important_components']
    }

    plotter = Stats_Plotter(data_source="Stanford",
                            lab_type='panel',
                            curr_version=curr_version)
    plotter.compare_algs(alg1='random-forest', alg2='xgb')

    # if 'LDH_cartoons' in main_figuretables:
    #     plotter.plot_full_cartoon(lab='LABLDH', include_threshold_colors=False)

    quit()


if __name__ == '__main__':
    curr_version = '10000-episodes-lastnormal'

    # main_one_analysis(curr_version=curr_version)
    main_full_analysis(curr_version=curr_version, inverse01=True)
