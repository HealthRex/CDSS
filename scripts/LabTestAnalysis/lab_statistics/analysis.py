
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
import stats_database
from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline \
        import NON_PANEL_TESTS_WITH_GT_500_ORDERS, \
            UCSF_TOP_PANELS, UMICH_TOP_PANELS, \
            STRIDE_COMPONENT_TESTS_common, UMICH_TOP_COMPONENTS_common, UCSF_TOP_COMPONENTS_common
from scripts.LabTestAnalysis.machine_learning.ml_utils import map_lab
from scripts.LabTestAnalysis.machine_learning import LabNormalityLearner_Legacy as LNL

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

        self.labStats_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/lab_statistics')

        self.lab_descriptions = stats_utils.get_lab_descriptions(data_source=self.data_source, lab_type=self.lab_type)


    def plot_full_cartoon(self, lab='LABLDH', include_threshold_colors=True, inverse01=False):
        print 'Running plot_full_cartoon...'

        inverse_maker = '_inversed01' if inverse01 else ''

        statsByLab_folderpath = os.path.join(self.labStats_folderpath, self.dataset_foldername)
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

    def draw__Order_Intensities(self, labs,
                                scale=1., result_label=None, scale_method = 'normalize',
                                use_cached_fig_data=True,
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

        cached_result_foldername = os.path.join(self.labStats_folderpath, 'Fig2_Order_Intensities/')
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

                df_lab = stats_utils.get_queried_lab(lab, self.lab_type, time_limit=stats_utils.DEFAULT_TIMELIMIT)

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

        fig, ax = plt.subplots(figsize=(8, .3 + 5.7/20.*len(labs))) #5+ 3./20.*len(labs)
        # 8, 3.435 for guideline
        # 8, 6 for freq labs
        # 6 - 3.435 = 2.565
        # Size for saturation is 7, 2.565 ?
        print .3 + 5.7/20.*len(labs)

        if scale_method=='normalize':
            labs = sorted(labs, key=lambda x: lab2stats[x]['< 24 hrs'] / lab2stats[x]['total'], reverse=True)

        for i, lab in enumerate(labs[::-1]):

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
            plt.xlabel('Number of orders per 100 patient encounters', fontsize=14) #'Order number between 2014/07-2017/06'

        if include_legend:
            plt.legend(prop={'size': 12})
        else:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")
            pass
        # plt.xscale('log')

        plt.tight_layout()
        cached_result_folderpath = cached_result_foldername + 'Order_Intensities_%s_%s.png'%(self.lab_type,result_label)


        plt.savefig(cached_result_folderpath)
        plt.clf()

    def draw__Normality_Saturations(self, labs, max_repeat = 5, use_cached_fig_data=True):
        '''
        Drawing Figure 1 in the main text.

        :return:
        '''
        print 'draw__Normality_Saturations running...'

        print "Labs to be plot:", labs

        cached_result_foldername = os.path.join(self.labStats_folderpath, 'Fig2_Order_Intensities/')
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
            import pickle
            cur_cnt_folderpath = 'Normality_Saturations_Cnts'
            if not os.path.exists(cur_cnt_folderpath):
                os.mkdir(cur_cnt_folderpath)

            def save_obj(obj, path):
                with open(path, 'wb') as f:
                    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

            def load_obj(path):
                with open(path, 'rb') as f:
                    return pickle.load(f)

            for lab in labs:
                print 'Getting Normality Saturations for %s..' % lab

                cur_dict_name = "cur_dict_%s.pkl"%lab
                cur_dict_path = os.path.join(cur_cnt_folderpath, cur_dict_name)
                if not os.path.exists(cur_dict_path):
                    df_lab = stats_utils.get_queried_lab(lab, self.lab_type, time_limit=stats_utils.DEFAULT_TIMELIMIT)

                    if self.lab_type=='panel':
                        df_lab = df_lab[df_lab['order_status'] == 'Completed']

                    cur_dict = stats_utils.get_prevweek_normal__dict(df_lab, self.lab_type)

                    save_obj(cur_dict, cur_dict_path)
                else:
                    cur_dict = load_obj(cur_dict_path)

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
            #
            # print df_cnts
            # print df_fracs
            # quit()

            df_cnts.to_csv(cached_result_foldername + 'lab2cnt.csv', index=False)
            df_fracs.to_csv(cached_result_foldername + 'lab2frac.csv', index=False)

        print 'lab2cnt', lab2cnt
        print 'lab2frac', lab2frac

        fig, ax = plt.subplots(figsize=(6.5, 3.25)) #6, 4.5 # 7, 2.565 #6.5, 3.75

        #, '<', '>'
        marker_types = ('o', 'v', '^', '8', 's', 'P', '*', 'X', 'D', 'd')

        for k, lab in enumerate(labs):  # :

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
        plt.savefig(cached_result_foldername + 'Negative_Saturations_%s'%(self.lab_type))
        plt.clf()

    def draw__Diagnostic_Metrics(self, result_label='all_labs',
                                targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False,
                                 inverse01=False):
        '''
        Drawing Figure 3 in the main text.

        :return:
        '''
        labs = self.all_labs
        print 'draw__Diagnostic_Metrics for', labs, ' with label %s...'%result_label
        labs_stats_filepath = os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')

        df = pd.read_csv(labs_stats_filepath, keep_default_na=False)

        # df = df[df['fixTrainPPV'] == targeted_PPV]

        df = df[df['lab'].isin(labs)]

        cached_foldername = 'Fig3_Diagnostic_Metrics/'
        cached_folderpath = os.path.join(os.path.join(statsByLab_folderpath, cached_foldername))

        cached_tablename = 'Diagnostic_Metrics_%ss_PPV_%.2f__%s.csv'%(self.lab_type, targeted_PPV, result_label)
        cached_tablepath = os.path.join(cached_folderpath, cached_tablename)

        cached_figurename = 'Diagnostic_Metrics_%ss_PPV_%.2f_ind__%s.png'%(self.lab_type, targeted_PPV, result_label)
        cached_figurepath = os.path.join(cached_folderpath, cached_figurename)

        if not os.path.exists(cached_folderpath):
            os.mkdir(cached_folderpath)

        if os.path.exists(cached_tablepath) and use_cached_fig_data:
            # lab2stats = pickle.load(open(cached_result_path, 'r'))
            df_toplots = pd.read_csv(cached_tablepath, keep_default_na=False)
            # print df_toplots

        else:
            if self.data_source == 'Stanford':
                # if 'total_vol' not in df.columns.values.tolist():
                # Stanford data, scaled by vol
                df['total_vol'] = df['total_vol_20140701_20170701']

            elif self.data_source == 'UCSF':
                import stats_database
                if self.lab_type == 'panel':
                    ucsf_lab_cnt = dict(stats_database.UCSF_PANELS_AND_COUNTS)

                elif self.lab_type == 'component':
                    ucsf_lab_cnt = stats_database.UCSF_COMPONENT_TO_COUNT #dict(stats_database.UCSF_COMPONENTSS_AND_COUNTS)
                df['total_vol'] = df['lab'].apply(lambda x: ucsf_lab_cnt[x])
            elif self.data_source == 'UMich' and self.lab_type=='component' and result_label=='important_components':
                df = df[df['lab'].isin(stats_utils.umich_lab_cnt)]


                df['total_vol'] = df['lab'].apply(lambda x: stats_utils.umich_lab_cnt[x])
            else:
                df['total_vol'] = 1



            # TODO: use fractions in the original file!
            df['all_instance'] = df['TP'] + df['FP'] + df['TN'] + df['FN']

            for cnt_type in ['TP', 'FP', 'TN', 'FN']:
                df[cnt_type] = df[cnt_type]/df['all_instance']


            df['all_positive'] = df['TP'] + df['FP']

            # print df[['all_positive', 'total_vol']]
            df['predicted_normal_vol'] = df['all_positive'] * df['total_vol']

            if result_label == 'important_components':

                if self.data_source == 'UMich' or self.data_source == 'UCSF':
                    df['lab'] = df['lab'].apply(lambda x: map_lab(x, self.data_source, self.lab_type, map_type='from_src'))

                df = df[df['lab'].isin(stats_utils.get_important_labs('component'))]
                df['lab'] = pd.Categorical(
                    df['lab'],
                    categories=stats_utils.get_important_labs('component'),
                    ordered=True
                )
                df = df.sort_values('lab')
            elif self.data_source == 'UMich':
                pass
            else:
                df = df.sort_values('total_vol', ascending=False)

            df['all_negative'] = df['TN'] + df['FN']

            df['TN'] = -df['TN']
            df['all_negative'] = -df['all_negative']

            df_toshow = df.copy().drop_duplicates()

            self.lab_descriptions = stats_utils.get_lab_descriptions(data_source=self.data_source,#'Stanford',
                                                                     lab_type=self.lab_type)
            df_toshow['Lab Test'] = df_toshow['lab'].apply(lambda x:self.lab_descriptions.get(x,x))
            df_toshow['TN'] = -df_toshow['TN']

            df_toshow['Prev'] = df_toshow['TN'] + df_toshow['FP']
            df_toshow = df_toshow.rename(columns={
                'num_test_episodes':'Count',
                                                'TP':'TP',
                                                  'FP':'FP',
                                                  'TN':'TN',
                                                  'FN':'FN',
                                                  'sens':'sens',
                                                  'spec':'spec',
                                                  'LR_p':'LR+', 'LR_n':'LR-'})

            df_toshow['AUC'] = df_toshow['AUC'].apply(lambda x: '%.2f'%(x))

            print df_toshow['NPV']
            df_toshow['NPV'] = df_toshow['NPV'].apply(lambda x: stats_utils.convert_floatstr2percentage(x))

            numeric_cols = ['Prev', 'PPV', 'TP', 'FP', 'TN', 'FN', 'sens', 'spec']
            for numeric_col in numeric_cols:
                if df_toshow[numeric_col].dtype != type(0.1):
                    df_toshow[numeric_col] = df_toshow[numeric_col].apply(lambda x: stats_utils.convert_floatstr2percentage(x))
                else:
                    df_toshow[numeric_col] = df_toshow[numeric_col].apply(lambda x: stats_utils.convert_floatnum2percentage(x))

            df_toshow['LR+'] = df_toshow['LR+'].apply(lambda x: stats_utils.convert_floatstr2num(x))
            df_toshow['LR-'] = df_toshow['LR-'].apply(lambda x: stats_utils.convert_floatstr2num(x))

            df_toshow['Vol'] = (df_toshow['total_vol'] / float(stats_utils.NUM_DISTINCT_ENCS / 1000.)).apply(
                lambda x: int(round(x)))

            if self.data_source == 'Stanford' and self.lab_type=='panel':

                df_toshow.loc[df_toshow['Lab Test']=='Sodium', 'chargemaster'] = 219
                df_toshow.loc[df_toshow['Lab Test'] == 'Specific Gravity', 'medicare'] = 3.28
                df_toshow.loc[df_toshow['Lab Test'] == 'Sepsis Protocol Lactate', 'medicare'] = 11.87
                df_toshow.loc[df_toshow['Lab Test'] == 'LDH Total', 'medicare'] = 6.71
                df_toshow.loc[df_toshow['Lab Test'] == 'Lactate', 'medicare'] = 11.87
                df_toshow.loc[df_toshow['Lab Test'] == 'Urinalysis', 'medicare'] = 2.67
                df_toshow.loc[df_toshow['Lab Test'] == 'Calcium Ionized', 'medicare'] = 13.73
                df_toshow.loc[df_toshow['Lab Test'] == 'Heparin', 'medicare'] = 16.16

                # print df_toshow
                df_toshow = df_toshow.rename(columns={'medicare': 'Medicare', 'chargemaster': 'Chargemaster'})

                df_toshow['Medicare'] = df_toshow['Medicare'].apply(lambda x: '$%s' % x if x != '' else '-')
                df_toshow['Chargemaster'] = df_toshow['Chargemaster'].apply(lambda x: '$%s' % str(x) if x != '' else '-')

                cols_to_show = ['Lab Test', 'Vol', 'AUC'] \
                               + numeric_cols
                               #+ ['Medicare', 'Chargemaster'] #+ ['LR+', 'LR-'] \
                print df_toshow['Lab Test'].values.tolist()
                labs_to_show = ['Magnesium', 'Prothrombin Time', 'Phosphorus', 'Partial Thromboplastin Time',
                                'Lactate', 'Calcium Ionized', 'Potassium', 'Troponin I', 'LDH Total',
                                'Heparin', 'Urinalysis', # too few positives
                                'Blood Culture (Aerobic & Anaerobic)',
                                'Blood Culture (2 Aerobic)', 'Sodium', 'Lidocaine', 'Hematocrit', 'Urine Culture',
                                'Urinalysis With Microscopic', 'Uric Acid', 'Hemoglobin A1c'
                                ]
            else:
                cols_to_show = ['Lab Test', 'AUC'] + numeric_cols #+ ['LR+', 'LR-']

            if inverse01:
                df_toshow = df_toshow.rename(columns={'PPV': 'NPV',
                                                      'NPV': 'PPV',
                                                      'TP': 'TN',
                                                      'FP': 'FN',
                                                      'TN': 'TP',
                                                      'FN': 'FP',
                                                      'sens':'Spec',
                                                      'spec':'Sens',
                                                      'best_alg':'Best Alg',
                                                      'AUC':'C-stat',
                                                      'fixTrainPPV':'Target NPV'})

                rename_alg = {'xgb': 'xgboost', 'nn': 'neural-nets'}
                df_toshow['Best Alg'] = df_toshow['Best Alg'].apply(lambda x: rename_alg.get(x, x))
                if self.data_source == 'Stanford':
                    cols_to_show = ['Lab Test', 'Vol', 'Best Alg', 'C-stat', 'Prev', 'Target NPV', 'NPV', 'PPV', 'Sens', 'Spec', 'TN', 'FN', 'TP', 'FP'] #['Lab Test', 'Vol', 'C-stat', 'Prev', 'NPV', 'PPV', 'Sens', 'Spec', 'TN', 'FN', 'TP', 'FP']

                else:
                    cols_to_show = ['Lab Test', 'Best Alg', 'C-stat', 'Prev', 'Target NPV', 'NPV', 'PPV', 'Sens',
                                    'Spec', 'TN', 'FN', 'TP', 'FP']

            if self.data_source == 'Stanford':
                if self.lab_type == 'panel':
                    labs_to_show = ['LABMGN', 'LABPT', 'LABPHOS', 'LABPTT', 'LABLACWB', 'LABCAI', 'LABK',
                                    'LABTNI', 'LABLDH', 'LABBLC', 'LABNA', 'LABHCTX', 'LABURNC']
                    #['LABMGN', 'LABPHOS', 'LABBLC', 'LABBLC2', 'LABUA', 'LABUAPRN', 'LABLACWB', 'LABCAI'] # suggested by Jason Hom
                    df_toshow[df_toshow['lab'].isin(labs_to_show)][cols_to_show].to_csv(cached_tablepath.replace('.csv','_finalshow.csv'), index=False)
                else:
                    labs_to_show = ['WBC', 'HGB', 'NA', 'K', 'CR']
                    df_toshow[df_toshow['lab'].isin(labs_to_show)][cols_to_show].to_csv(
                        cached_tablepath.replace('.csv', '_finalshow.csv'), index=False)

            df_toshow[cols_to_show].iloc[:20].to_csv(cached_tablepath.replace('.csv','_toshow.csv'), index=False) #.sort_values('total_vol', ascending=False)

            if self.data_source == 'Stanford' and self.lab_type=='panel':
                cols_to_show += ['Medicare', 'Chargemaster']

            df_toshow[cols_to_show].to_csv(cached_tablepath.replace('.csv', '_full.csv'), index=False)

            df['all_positive_vol'] = df['all_positive'] * df['total_vol']
            df['true_positive_vol'] = df['TP'] * df['total_vol']
            df['all_negative_vol'] = df['all_negative'] * df['total_vol']
            df['true_negative_vol'] = df['TN'] * df['total_vol']

            df_toplots = df.iloc[:15]

            df_toplots[['lab',
                        'PPV', 'NPV', 'sens', 'spec', 'LR_p', 'LR_n',
                        'total_vol',
                       'all_positive_vol', 'true_positive_vol', 'all_negative_vol', 'true_negative_vol']]\
                        .to_csv(cached_tablepath, index=False, float_format='%.3f') # .sort_values('total_vol', ascending=False)\

        if not scale_by:
            scale = 1.
        elif scale_by=='pat':
            scale = float(stats_utils.NUM_DISTINCT_PATS/1000.)
        elif scale_by == 'enc':
            scale = float(stats_utils.NUM_DISTINCT_ENCS/1000.)
        elif scale_by == 'enc_ucsf':
            scale = float(stats_utils.NUM_DISTINCT_ENCS_UCSF/1000.)

        if self.data_source == 'Stanford' or self.data_source == 'UCSF' or self.data_source == 'UMich': #True: #self.lab_type == 'panel':
            df_toplots = df_toplots.iloc[::-1]
        else:
            df_toplots = df_toplots.iloc[::-1]

        for ind, df_toplot in enumerate([df_toplots.tail(38), df_toplots.head(38)]):

            if result_label == 'important_components':
                fig, ax = plt.subplots(figsize=(6, 9))
            else:
                fig, ax = plt.subplots(figsize=(10, 8))

            ax.barh(df_toplot['lab'], df_toplot['all_positive_vol'] / scale, color='orangered', alpha=1,
                    label='False Positive')
            ax.barh(df_toplot['lab'], df_toplot['true_positive_vol'] / scale, color='forestgreen', alpha=1,
                    label='True Positive')
            ax.barh(df_toplot['lab'], df_toplot['all_negative_vol'] / scale, color='gold', alpha=1,
                    label='False Negative')
            ax.barh(df_toplot['lab'], df_toplot['true_negative_vol'] / scale, color='royalblue', alpha=1,
                    label='True Negative')

            plt.yticks([])

            if result_label == 'important_components':
                plt.xlim([-8500, 6500])
                plt.xticks([-6000, -3000, 0, 3000, 6000])
                ax.set_xticklabels([6000, 3000, 0, 3000, 6000])

                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(True)
                ax.spines['left'].set_visible(False)
                pass
            else:
                for i, v in enumerate(df_toplot['all_positive_vol'] / scale):
                    cur_lab = df_toplot['lab'].values[i]
                    cur_description = self.lab_descriptions.get(cur_lab, cur_lab).replace(' - ', '/')

                    if self.data_source == 'UMich':
                        ax.text(v + 0.05, i - 0.2, cur_description, color='k', fontsize=14)
                    else:
                        if '\n' in cur_description:
                            ax.text(v + 50, i - 0.3, cur_description, color='k', fontsize=14)
                        else:
                            ax.text(v + 50, i - 0.1, cur_description, color='k', fontsize=14)

                if self.data_source == 'Stanford' and self.lab_type == 'panel':
                    plt.xlim([-2300, 2700])
                elif self.data_source == 'Stanford' and self.lab_type == 'component':
                    plt.xlim([-9000, 9000])
                elif self.data_source == 'UCSF' and self.lab_type == 'panel':
                    plt.xlim([-3200, 3200])
                elif self.data_source == 'UCSF' and self.lab_type == 'component':
                    plt.xlim([-6000, 6000])
                elif self.data_source == 'UMich' and self.lab_type == 'component':
                    # plt.xlim([-1.5, 1.5])
                    plt.xlim([-8000, 8000])

                if self.data_source == 'UCSF' or self.data_source == 'Stanford' or self.data_source == 'UMich':
                    plt.xlabel('Number of orders per 1000 patient encounters', fontsize=18) #, targeting at %.0f'%(targeted_PPV*100)+'% PPV'
                else:
                    plt.xlabel('Fraction of orders, targeting at %.0f' % (targeted_PPV * 100) + '% PPV',
                    fontsize=18)

            plt.tick_params('x', labelsize=24)


            plt.tight_layout()

            plt.savefig(cached_figurepath.replace('ind', 'ind_%i'%ind))

def main_transfer_model(curr_version, lab_type='component'):
    def statistic_analysis(lab, dataset_folder):
        from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score

        direct_comparisons = pd.read_csv(os.path.join(dataset_folder, 'direct_comparisons.csv'))
        # print direct_comparisons
        return roc_auc_score(direct_comparisons['actual'].values, direct_comparisons['predict'].values)

    all_sites = ['Stanford', 'UCSF', 'UMich']

    res_folderpath = 'data-transferring-component-%s/'%curr_version
    if not os.path.exists(res_folderpath):
        os.mkdir(res_folderpath)

    res_filepath = res_folderpath + 'all_transfers.csv'

    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
    ml_results_folderpath = os.path.join(main_folder, 'machine_learning')

    if os.path.exists(res_filepath):
        df_res = pd.read_csv(res_filepath, keep_default_na=False)

    else:

        labs = stats_utils.get_important_labs(lab_type='component')


        all_res_dicts = {}
        all_res_dicts['lab'] = labs

        diagonals = []
        off_diags = []

        columns = ['lab']
        for i in range(3): # Training sources
            for j in range(3): # Testing sources
                src = all_sites[i]
                dst = all_sites[j]


                '''
                '''
                ml_folder = ml_results_folderpath
                LNL.transfer_labs(src_dataset=src, dst_dataset=dst, lab_type=lab_type,
                                                  cur_version=curr_version)
                transfer_result_folderpath = ml_folder + '/data-%s-src-%s-dst-%s-%s/' \
                                             % (lab_type, src, dst, curr_version)
                cur_res = []
                for lab in labs:
                    direct_comparisons_folderpath = os.path.join(transfer_result_folderpath, lab)

                    if i!=j:
                        cur_AUC = statistic_analysis(lab=lab, dataset_folder=direct_comparisons_folderpath)
                        off_diags.append(cur_AUC)
                    else:
                        tmp_df = pd.read_csv('data-%s-component-10000-episodes-lastnormal' % src
                                        + '/' + 'summary-stats-bestalg-fixTrainPPV.csv', keep_default_na=False)
                        mapped_lab = map_lab(lab=lab, data_source=src, lab_type=lab_type)
                        cur_AUC = \
                            tmp_df[(tmp_df['lab'] == mapped_lab) & (tmp_df['fixTrainPPV'] == 0.95)]['AUC'].values[0]
                        diagonals.append(cur_AUC)
                    cur_res.append(cur_AUC)

                col = '%s -> %s' % (src, dst)
                all_res_dicts[col] = cur_res

                columns.append(col)
        import numpy as np
        print "diagonals avg:", np.mean(diagonals)
        print "off_diags avg:", np.mean(off_diags)

        df_res = pd.DataFrame.from_dict(all_res_dicts)

        descriptions = stats_utils.get_lab_descriptions(lab_type='component')
        df_res['lab'] = df_res['lab'].apply(lambda x:descriptions[x])
        df_res = df_res[columns]
        df_res.to_csv(res_filepath, index=False, float_format='%.2f')

    # TODO: move this stats part away
    import seaborn as sns; sns.set()
    import numpy as np
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(16, 12))
    col = 5
    for ind in range(df_res.shape[0]):
        cur_row = df_res.iloc[ind].values
        print cur_row
        cur_lab = cur_row[0]
        cur_aucs = cur_row[1:].astype(float).reshape(3,3)

        i, j = ind/col, ind%col
        plt.subplot2grid((3, col), (i, j))
        ax = sns.heatmap(cur_aucs, vmin=0, vmax=1, cbar=False, annot=True, cmap='ocean',
                         annot_kws={"size": 18},
                         xticklabels=['S', 'UC', 'UM'], yticklabels=['S', 'UC', 'UM'])
        plt.xlabel(cur_lab, fontsize=20)
        ax.xaxis.set_label_position('top')
        ax.xaxis.set_tick_params(labelsize=18)
        ax.yaxis.set_tick_params(labelsize=18)


    plt.tight_layout()
    fig.subplots_adjust(hspace=.5)

    plt.savefig(res_folderpath + 'transfer_heatmap.png')


    # statistic_analysis(lab='LABURIC', dataset_folder=os.path.join('data', 'LABURIC', 'transfer_Stanford_to_UCSF')) #'data-panel-Stanford-UCSF-10000-episodes'
    # apply_Stanford_to_UCSF(lab='LABURIC', lab_type='panel',
    #                        src_dataset_folderpath=os.path.join('data', 'LABURIC', 'wi last normality - Stanford'),
    #                        dst_dataset_folderpath=os.path.join('data', 'LABURIC', 'wi last normality - UCSF'),
    #                        output_folderpath=os.path.join('data', 'LABURIC', 'transfer_Stanford_to_UCSF'))

def main_full_analysis(figs_to_plot, curr_version, inverse01=False):

    '''
    :param curr_version:
    :param inverse01:
    :return:
    '''

    '''Figure 1'''
    if 1 in figs_to_plot:
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
    if 2 in figs_to_plot:
        scale = 1. / stats_utils.NUM_DISTINCT_ENCS * 100

        '''Figure 2.1'''
        labs_cnts_order_1day = stats_database.TOP_PANELS_AND_COUNTS_IN_1DAY[:20]
        labs_order_1day = [x[0] for x in labs_cnts_order_1day]
        plotter = Stats_Plotter(data_source='Stanford', lab_type='panel', curr_version=curr_version)
        plotter.draw__Order_Intensities(labs=labs_order_1day, result_label='labs_order_1day',
                                     scale=scale, use_cached_fig_data=True, scale_method='by_scale',
                                     include_legend=True)

        '''Figure 2.2'''
        # labs_guideline = ['LABESRP', 'LABALB', 'LABA1C', 'LABTSH', 'LABCRP', 'LABYCP', 'LABLIPS', 'LABAGALA', 'LABNTBNP']
        # plotter.draw__Order_Intensities(labs=labs_guideline, result_label='labs_guideline',
        #                              scale=scale, use_cached_fig_data=True, scale_method='normalize',  # normalize
        #                              include_legend=False)

        '''Figure 2.3'''
        # plotter = Stats_Plotter(data_source='Stanford', lab_type='component', curr_version=curr_version)
        # plotter.draw__Normality_Saturations(labs=['WBC', 'HGB', 'NA', 'K', 'CR'], use_cached_fig_data=True)

    if 3 in figs_to_plot:

        for data_source in ['Stanford', 'UCSF', 'UMich']: #'Stanford',
            for lab_type in ['component']:

                plotter = Stats_Plotter(data_source=data_source, lab_type=lab_type, curr_version=curr_version)

                '''
                Two steps: 
                lab2stats: Getting lab-wise stats tables under lab_statistics/dataset_folder/stats_by_lab_alg/..
                stats2summary: Aggregate all labs' stats under lab_statistics/dataset_folder/..
                '''
                plotter.draw__Diagnostic_Metrics(result_label="important_components",
                                                 targeted_PPV=0.95,
                                                 scale_by='enc',
                                                 use_cached_fig_data=False,
                                                 inverse01=inverse01)
    if 4 in figs_to_plot:
        main_transfer_model(curr_version)

    if 'SI' in figs_to_plot:
        pass


if __name__ == '__main__':
    curr_version = '10000-episodes-lastnormal'
    figs_to_plot = [4]
    main_full_analysis(figs_to_plot, curr_version=curr_version, inverse01=True)