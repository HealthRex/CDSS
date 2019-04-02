
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

import LocalEnv


# # labs_ml_folder = stats_utils.labs_ml_folder
# # labs_stats_folder = stats_utils.labs_stats_folder
#
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


# all_panels = NON_PANEL_TESTS_WITH_GT_500_ORDERS
# all_components = STRIDE_COMPONENT_TESTS
# all_UMichs = UMICH_TOP_COMPONENTS
# all_UCSF = UCSF_TOP_COMPONENTS
all_algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

class Stats_Plotter():
    def __init__(self, data_source='Stanford', lab_type='panel', curr_version='10000-episodes'):
        self.data_source = data_source
        self.lab_type = lab_type

        if data_source == 'Stanford' and lab_type == 'panel':
            self.all_labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS  # [x[0] for x in labs_and_cnts]
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
                else:
                    # df_lab = df_lab[df_lab['order_status'] == 'Completed']
                    pass

                cur_dict = stats_utils.get_prevweek_normal__dict(df_lab, self.lab_type)
                # lab2stats[lab] = cur_dict

                # cur_dict = lab2stats[lab]


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
            plt.xlabel('Consecutive normal tests in the past 7 days', fontsize=14)
            plt.tick_params('x', labelsize=15)  # 12
            plt.tick_params('y', labelsize=13)  # 10
            plt.ylabel("Normal rate", fontsize=14)
            plt.ylim([-0.05, 1.05])
            plt.legend(fontsize=13)
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")
            plt.tight_layout()
            plt.savefig(cached_result_foldername + 'Normality_Saturations_%s_%i'%(self.lab_type, ind))
            plt.clf()


    def draw__Potential_Savings(self, statsByLab_folderpath, scale=None, targeted_PPV=0.95,
                                result_label='',use_cached_fig_data=False,price_source='medicare'):
        '''
        Drawing Figure 4 in the main text.

        :return:
        '''

        df = pd.read_csv(os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv'),
                         keep_default_na=False)
        df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]
        df = df.drop_duplicates()

        # labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=50)
        # df = df[df['lab'].isin(all_labs)] #[x[0] for x in labs_and_cnts]

        result_foldername = 'Fig4_Potential_Savings/'
        result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
        if not os.path.exists(result_folderpath):
            os.mkdir(result_folderpath)

        '''
        Hierarchy:
        
        '''

        fig_filename = 'Potential_Savings_PPV_%.2f_%s_%s.png'%(targeted_PPV, result_label, price_source)
        fig_path = os.path.join(result_folderpath, fig_filename)
        data_filename = 'Potential_Savings_%.2f_%s_%s.csv'%(targeted_PPV, result_label, price_source)
        data_path = os.path.join(result_folderpath, data_filename)

        if os.path.exists(data_path) and use_cached_fig_data:
            df = pd.read_csv(data_path, keep_default_na=False)

        else:
            # df = df[df['lab'] != 'LABNA']  # TODO: fix LABNA's price here

            df = df[df[price_source] != '']
            df[price_source] = df[price_source].astype(float)

            df['TP_cost'] = df['true_positive'] * df['total_cnt'] * df[price_source]
            df['FP_cost'] = df['false_positive'] * df['total_cnt'] * df[price_source]
            df['FN_cost'] = df['false_negative'] * df['total_cnt'] * df[price_source]
            df['TN_cost'] = df['true_negative'] * df['total_cnt'] * df[price_source]
            df['total_cost'] = df['TP_cost'] + df['FP_cost'] + df['FN_cost'] + df['TN_cost']

            df = df[['lab', 'TP_cost', 'FP_cost', 'FN_cost', 'TN_cost', 'total_cost']]

            df = df.sort_values('TP_cost')
            df.to_csv(data_path, index=False)

        # print df.shape
        print 'Total saved money:', (df['TP_cost']).sum() * 66440./1000/3
        df = df.iloc[-20:]
        # print df.shape
        # quit()

        # unit, scale = 'million', 10.**6


        # if not scale_by:
        #     scale = 1.
        # elif scale_by == 'pat':
        #     scale = float(stats_utils.NUM_DISTINCT_PATS)
        # elif scale_by == 'enc':
        #     scale = float(stats_utils.NUM_DISTINCT_ENCS)

        df['TP_cost'] = df['TP_cost'] * scale
        df['FP_cost'] = df['FP_cost'] * scale
        df['FN_cost'] = df['FN_cost'] * scale
        df['TN_cost'] = df['TN_cost'] * scale
        df['total_cost'] = df['total_cost'] * scale

        # df['total_cost'] = df['TP_cost'] + df['FP_cost']
        # lab_descriptions['LABBLC'] = 'BLOOD CULTURE (AEROBIC & ANAEROBIC)'
        # lab_descriptions['LABBLC2'] = 'BLOOD CULTURE (2 AEROBIC)'

        df['lab_description'] = df['lab'].apply(
            lambda x: self.lab_descriptions[x])

        # '''
        # Top cost volume labs (with a medicare price)
        # '''
        # labs_to_show = ['LABMGN', 'LABBLC', 'LABBLC2', 'LABLIDOL', 'LABK', 'LABNA', 'LABPHOS', 'LABTNI',
        #                 'LABPROCT', 'LABURIC', 'LABLAC', 'LABUSPG', 'LABHBSAG',
        #                 'LABLIPS', 'LABUOSM', 'LABANER', 'LABCK', 'LABPLTS',
        #                 'LABB12', 'LABTNI',
        #                 #'LABUPREG','LABALB',
        #                 #'LABMB', 'LABURNC', 'LABTRIG'
        #                 # 'LABUOSM', 'LABA1C'
        #                 ]
        # df = df[df['lab'].isin(labs_to_show)]

        '''
        Cost per 1000 pat enc, translate to annual cost
        '''
        df['Annual TP cost'] = df['TP_cost'] * stats_utils.NUM_DISTINCT_ENCS /3. /1000.
        df[['lab_description', 'Annual TP cost']].sort_values('Annual TP cost', ascending=False).to_csv(os.path.join(result_folderpath, 'info_column.csv'), index=False, float_format='%.0f')

        # fig, ax = plt.subplots(figsize=(8, 6))
        fig, ax = plt.subplots(figsize=(10, 6)) # LABBLC has too long name!
        ax.barh(df['lab_description'], df['total_cost'],
                color='royalblue', alpha=1, label='true negative')  # 'True Positive@0.95 train_PPV'

        ax.barh(df['lab_description'], df['TP_cost']+df['FN_cost']+df['FP_cost'],
                color='orangered', alpha=1, label='false positive')

        ax.barh(df['lab_description'], df['TP_cost'] + df['FN_cost'],
                color='gold', alpha=1, label='false negative')

        ax.barh(df['lab_description'], df['TP_cost'],
                color='forestgreen', alpha=1, label='true positive')

        ax.set_xticklabels(['0', '$5,000', '$10,000', '$15,000', '$20,000', '$25,000', '$30,000', '$35,000'])

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(12)

        plt.xlabel('Medicare fee per 1000 patient encounters', fontsize=14) # 'Total Amount (in %s) in 2014.07-2017.06, targeting PPV=%.2f'%(unit, targeted_PPV)
        # plt.xticks(range(0, 15001, 5000))
        # plt.xlim([0,20000])


        plt.tight_layout()
        plt.savefig(fig_path)

        plt.show()







    ######################################
    '''
    refactoring
    '''

    def draw__Diagnostic_Metrics(self, statsByLab_folderpath, labs, result_label='all_labs',
                                targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False):
        '''
        Drawing Figure 3 in the main text.

        :return:
        '''
        print 'draw__Diagnostic_Metrics for', labs, ' with label %s...'%result_label
        # df = pd.read_csv('data_performance_stats/best-alg-%s-summary-fix-trainPPV.csv' % self.lab_type,
        #                  keep_default_na=False)
        labs_stats_filepath = os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')

        df = pd.read_csv(labs_stats_filepath, keep_default_na=False)

        df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]

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
                df['total_vol'] = df['total_cnt']

            elif self.data_source == 'UCSF':
                import stats_database
                if self.lab_type == 'panel':
                    ucsf_lab_cnt = dict(stats_database.UCSF_PANELS_AND_COUNTS)

                elif self.lab_type == 'component':
                    ucsf_lab_cnt = stats_database.UCSF_COMPONENT_TO_COUNT #dict(stats_database.UCSF_COMPONENTSS_AND_COUNTS)
                df['total_vol'] = df['lab'].apply(lambda x: ucsf_lab_cnt[x])
            elif self.data_source == 'UMich' and self.lab_type=='component' and result_label=='important_components':
                umich_lab_cnt = {'WBC':5280.99347210938,
                'HGB':5281.00748045835,
                'PLT':5274.22743955397,
                'SOD':5784.07530888409,
                'POT':5784.06130053512,
                'CR':5784.04729218614,
                'TBIL':1662.90309024178,
                'CHLOR':5784.07530888409,
                'CO2':5784.04729218614,
                'AST':1667.87605412826,
                'ALB':2239.66884263021,
                'CAL':5791.51374219035,
                # 'PCO2AA':,
                # 'PO2AA':,
                # 'DBIL':,
                # 'pHA':,
                'PROT':1667.87605412826,
                'ALK':1667.87605412826,
                'UN':5784.04729218614,
                # 'IBIL':
                'CREAT': 5784.04729218614,
                'ALT': 1667.87605412826
                }
                df = df[df['lab'].isin(umich_lab_cnt)]


                df['total_vol'] = df['lab'].apply(lambda x: umich_lab_cnt[x])
            else:
                df['total_vol'] = 1



            # TODO: use fractions in the original file!
            df['all_instance'] = df['true_positive'] + df['false_positive'] + df['true_negative'] + df['false_negative']

            for cnt_type in ['true_positive', 'false_positive', 'true_negative', 'false_negative']:
                df[cnt_type] = df[cnt_type]/df['all_instance']


            df['all_positive'] = df['true_positive'] + df['false_positive']

            # print df[['all_positive', 'total_vol']]
            df['predicted_normal_vol'] = df['all_positive'] * df['total_vol']

            if result_label == 'important_components':


                if self.data_source == 'UMich' or self.data_source == 'UCSF':
                    df['lab'] = df['lab'].apply(lambda x: map_lab(x, self.data_source, self.lab_type, map_type='from_src'))

                # df = df.sort_values('predicted_normal_vol', ascending=False)
                #     print df['lab'].values

                df = df[df['lab'].isin(stats_utils.get_important_labs('component'))]
                df['lab'] = pd.Categorical(
                    df['lab'],
                    categories=stats_utils.get_important_labs('component'),
                    ordered=True
                )
                df = df.sort_values('lab')

            else:
                df = df.sort_values('total_vol', ascending=False)



            df['all_negative'] = df['true_negative'] + df['false_negative']

            df['true_negative'] = -df['true_negative']
            df['all_negative'] = -df['all_negative']

            df_toshow = df.copy().drop_duplicates()

            df_toshow['lab'] = df_toshow['lab'].apply(lambda x:self.lab_descriptions.get(x,x))
            df_toshow['true_negative'] = -df_toshow['true_negative']

            df_toshow['Prev'] = df_toshow['true_positive'] + df_toshow['false_negative']
            df_toshow = df_toshow.rename(columns={
               'lab':'Lab Test',
                'num_test_episodes':'Count',
                                                'true_positive':'TP',
                                                  'false_positive':'FP',
                                                  'true_negative':'TN',
                                                  'false_negative':'FN',
                                                  'sensitivity':'sens',
                                                  'specificity':'spec',
                                                  'LR_p':'LR+', 'LR_n':'LR-'})
            df_toshow['AUROC'] = df_toshow['AUROC'].apply(lambda x: '%.2f'%(x))

            numeric_cols = ['Prev', 'PPV', 'TP', 'FP', 'TN', 'FN', 'sens', 'spec']
            for numeric_col in numeric_cols:
                if df_toshow[numeric_col].dtype != type(0.1):
                    df_toshow[numeric_col] = df_toshow[numeric_col].apply(lambda x: stats_utils.convert_floatstr2percentage(x))
                else:
                    df_toshow[numeric_col] = df_toshow[numeric_col].apply(lambda x: stats_utils.convert_floatnum2percentage(x))

            df_toshow['LR+'] = df_toshow['LR+'].apply(lambda x: stats_utils.convert_floatstr2num(x))
            df_toshow['LR-'] = df_toshow['LR-'].apply(lambda x: stats_utils.convert_floatstr2num(x))

            df_toshow['Volume'] = (df_toshow['total_vol'] / float(stats_utils.NUM_DISTINCT_ENCS / 1000.)).apply(
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

                df_toshow['Medicare'] = df_toshow['Medicare'].apply(lambda x: '$%s' % x if x != '-' else x)
                df_toshow['Chargemaster'] = df_toshow['Chargemaster'].apply(lambda x: '$%s' % str(x) if x != '-' else x)



                cols_to_show = ['Lab Test', 'Volume', 'AUROC'] \
                               + numeric_cols \
                               + ['Medicare', 'Chargemaster'] #+ ['LR+', 'LR-'] \
            # elif self.data_source == 'Stanford' and self.lab_type=='component':
            #     cols_to_show = ['Lab Test', 'Vol', 'AUROC'] + numeric_cols + ['LR+', 'LR-']
            else:
                cols_to_show = ['Lab Test', 'AUROC'] + numeric_cols #+ ['LR+', 'LR-']

            df_toshow[cols_to_show].to_csv(cached_tablepath.replace('.csv', '_full.csv'), index=False)
            df_toshow[cols_to_show].iloc[:15].to_csv(cached_tablepath.replace('.csv','_toshow.csv'), index=False) #.sort_values('total_vol', ascending=False)

            df['all_positive_vol'] = df['all_positive'] * df['total_vol']
            df['true_positive_vol'] = df['true_positive'] * df['total_vol']
            df['all_negative_vol'] = df['all_negative'] * df['total_vol']
            df['true_negative_vol'] = df['true_negative'] * df['total_vol']

            df_toplots = df.iloc[:15]

            df_toplots[['lab',
                        'PPV', 'NPV', 'sensitivity', 'specificity', 'LR_p', 'LR_n',
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
            # df_toplots = df_toplots.sort_values(['total_vol'], ascending=True)
            df_toplots = df_toplots.iloc[::-1]
            # pass
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

            # handles, labels = plt.gca().get_legend_handles_labels()
            # order = [1, 0, 3, 2]

            # plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
            #            loc=[0.05,0.1], ncol=2, prop={'size': 12})
                if self.data_source == 'UCSF' or self.data_source == 'Stanford' or self.data_source == 'UMich':
                    plt.xlabel('Number of orders per 1000 patient encounters', fontsize=18) #, targeting at %.0f'%(targeted_PPV*100)+'% PPV'
                else:
                    plt.xlabel('Fraction of orders, targeting at %.0f' % (targeted_PPV * 100) + '% PPV',
                    fontsize=18)
            #plt.ylabel('Labs', fontsize=14)

            plt.tick_params('x', labelsize=24)


            plt.tight_layout()

            plt.savefig(cached_figurepath.replace('ind', 'ind_%i'%ind))


    '''
    refactoring
    '''
    ######################################

    ######################################
    '''
    refactored
    '''

    def plot_order_intensities_barh(self, lab, time_since_last_order_binned, columns, scale,
                                    labeling=True, lab_ind=None, to_annotate_percentages=False):

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
            lab_desciption = lab_descriptions.get(lab, lab)

            if labeling:
                plt.barh([lab_desciption], pre_sum, color=colors[i], alpha=alphas[i], label=key)
            else:
                plt.barh([lab_desciption], pre_sum, color=colors[i], alpha=alphas[i])

        tot_cnt = sum(time_since_last_order_binned.values())
        cur_cnt = time_since_last_order_binned['< 24 hrs'] * scale
        if to_annotate_percentages:

            if cur_cnt < 400:
                return
            percentage = '%.0f' % (time_since_last_order_binned['< 24 hrs'] / float(tot_cnt) * 100) + '%'
            print 'lab', lab, 'lab_ind', lab_ind
            ax.text(cur_cnt / 2. - 100, lab_ind - 0.15, percentage, fontsize=10, fontweight='bold', color='white')
        else:
            '''
            annotate legend
            '''
            if lab == 'LABMETB':
                pass
            pass

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
        # columns = ['< 1 day', '1-3 days', '3-7 days', '> 7 days']
        # columns = ['< 24 hrs', '[24, 72) hrs', '>= 72 hrs']
        columns = ['< 24 hrs', '[24 hrs, 3 days)', '[3 days, 1 week)', '>= 1 week']
        # day_ranges = [[0,1], [1,4], [4,7], [7,None]]

        if os.path.exists(cached_result_path) and use_cached_fig_data:
            # lab2stats = pickle.load(open(cached_result_path, 'r'))
            lab2stats_pd = pd.read_csv(cached_result_path)
            lab2stats_pd = lab2stats_pd.rename(columns={'< 1 day':'< 24 hrs',
                                                        '1-3 days':'[24 hrs, 3 days)',
                                                        '3-7 days':'[3 days, 1 week)',
                                                        '> 7 days':'>= 1 week'})
            lab2stats = lab2stats_pd.set_index('lab').to_dict(orient='index')

        else:
            for lab in labs: #all_labs[:10][::-1]:
                print 'Getting Order Intensities of lab %s..'%lab

                df_lab = stats_utils.get_queried_lab(lab, self.lab_type, time_limit=DEFAULT_TIMELIMIT)

                dict_lab = stats_utils.get_floored_day_to_number_orders_cnts(lab, df_lab)

                # df_lab = pd.DataFrame.from_dict(dict_lab, orient='index').reset_index().rename(columns={'index': 'lab'})
                # df_lab.to_csv(cached_result_foldername + '%s.csv'%lab, index=False)

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

                # The following is extremely confusing
                # sums = [dict_lab[0], sum(dict_lab[x] for x in range(1, 4)), sum(dict_lab[x] for x in range(4, 8))]
                # sums.append(sum(dict_lab[x] for x in dict_lab.keys()) - sum(sums))
                # time_since_last_order_binned = {columns[_]: sums[_] for _ in range(len(columns))}

                lab2stats[lab] = dict(zip(columns, day_counts))

            # pickle.dump(lab2stats, open(cached_result_path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

            df_res = pd.DataFrame.from_dict(lab2stats, orient='index').reset_index().rename(columns={'index':'lab'})

            df_res.to_csv(cached_result_path, index=False)

        print lab2stats
        labs_ordered = sorted(labs, key=lambda x: lab2stats[x]['< 24 hrs'], reverse=True) #< 24 hrs

        # fig = plt.figure(figsize=(12, 6/20.*len(labs) )) # figsize=(20, 12) figsize=(12, 8)

        labs_toplots = [labs_ordered]
        # labs_toplots = [lab_ordered[:39], lab_ordered[39:]]

        for ind_toplot, labs_toplot in enumerate(labs_toplots):
            # print 'Fig Size:', 6 + 2./20.*len(labs), 1 + 5./20.*len(labs)
            fig, ax = plt.subplots(figsize=(8, .3 + 5.7/20.*len(labs))) #5+ 3./20.*len(labs)
            # 8, 3.435 for guideline
            # 8, 6 for freq labs
            # 6 - 3.435 = 2.565
            # Size for saturation is 7, 2.565 ?
            print .3 + 5.7/20.*len(labs)
            for i, lab in enumerate(labs_toplot[::-1]):

                time_since_last_order_binned = lab2stats[lab]


                tot_cnt = float(sum(time_since_last_order_binned.values()))
                for time, cnt in time_since_last_order_binned.items():
                    if scale_method == 'normalize':
                        time_since_last_order_binned[time] = cnt/tot_cnt

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
                           include_baseline=True):
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

        # lab_descriptions = stats_utils.get_lab_descriptions(line_break_at=22)

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

            if include_baseline:
                plt.plot(xVal_base, yVal_base, label='%0.2f' % (score_base))

            dash_num = 20
            plt.plot(np.linspace(0, 1, num=dash_num), np.linspace(0, 1, num=dash_num), color='lightblue',
                     linestyle='--')

            plt.plot(xVal_best, yVal_best, label='%0.2f' % (score_best), color='orange')

            plt.xlim([0,1])
            plt.ylim([0,1])
            plt.xticks([])
            plt.yticks([])

            plt.xlabel(self.lab_descriptions.get(lab, lab))
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





    def draw__Comparing_Savable_Fractions(statsByLab_folderpath,
                             target_PPV=0.95,
                             use_cache=True):
        '''
        Targeting at PPV=0.95, what are the savable fractions from each method?

        :return:
        '''
        result_foldername = 'Fig5_Comparing_Savable_Fractions/'
        result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
        if not os.path.exists(result_folderpath):
            os.mkdir(result_folderpath)

        result_tablename = 'Comparing_Savable_Fractions_PPV_%.2f.csv'%target_PPV
        result_tablepath = os.path.join(result_folderpath, result_tablename)

        result_figname = 'Comparing_Savable_Fractions_PPV_%.2f.png'%target_PPV
        result_figpath = os.path.join(result_folderpath, result_figname)

        if use_cache and os.path.exists(result_tablepath):
            df_twomethods = pd.read_csv(result_tablepath, keep_default_na=False)
            # print df_twomethods
            savable_fractions_baseline1 = stats_utils.pandas2dict(df_twomethods, key='lab', val='savable_fraction_baseline1')
            savable_fractions_baseline2 = stats_utils.pandas2dict(df_twomethods, key='lab',
                                                                  val='savable_fraction_baseline2')
            savable_fractions_mlmodel = stats_utils.pandas2dict(df_twomethods, key='lab', val='savable_fraction_mlmodel')
        else:

            labs = all_labs

            mlByLab_folder = statsByLab_folderpath.replace("lab_statistics", "machine_learning")

            '''
            Baseline 1: consecutive normalites in the last week
            
            The simple rule is: As long as the number of consecutive normalites
            reaches a threshold, then do not order; otherwise, go ahead and order. 
            Advantage: Provides a way to assign conservativeness
            Disadvantage: Too stringent, very few patients will qualify; in most cases have to order. 
            '''
            savable_fractions_baseline1 = {}
            for lab in labs:
                days, normality_lists = stats_utils.get_prevday2normalities(lab, mlByLab_folder, source="train")
                normality_fractions = [float(sum(x)) / float(len(x)) for x in normality_lists]

                '''
                Pick a threshold
                '''
                day_thres = float('inf')
                for i, normality_fraction in enumerate(normality_fractions):
                    if normality_fraction > target_PPV:
                        day_thres = days[i]
                        break


                days, normality_lists = stats_utils.get_prevday2normalities(lab, mlByLab_folder, source="test")
                normality_fractions = [float(sum(x))/float(len(x)) for x in normality_lists]
                normality_cnts = [len(x) for x in normality_lists]

                '''
                Count fraction above this thres
                '''
                savable_cnt = 0
                for i, normality_fraction in enumerate(normality_fractions):
                    if days[i] >= day_thres:
                        savable_cnt += normality_cnts[i]
                savable_fraction = float(savable_cnt) / float(sum(normality_cnts))
                savable_fractions_baseline1[lab] = savable_fraction

                '''
                For the rule of "passing a number of days, then all set 'normal',
                the normal rate is equals to the PPV. "
                '''

            df_baseline1 = stats_utils.dict2pandas(savable_fractions_baseline1, key='lab', val='savable_fraction_baseline1')

            '''
            Baseline 2: last order + prevalence
            
            Since there is no threshold to choose, the rule is to see whether the metric 
                gives a > 0.95 PPV for each lab in the train set. 
            
            If yes, then do not order (save!) when test prediction says 'Normal'.
            If no, then always order (never save). 
            '''
            savable_fractions_baseline2 = {}
            for lab in labs:
                train_prevalence, train_thres = stats_utils.check_baseline2(lab, mlByLab_folder, source="train")

                if train_thres == -1: #
                    savable_fractions_baseline2[lab] = 0
                else:
                    savable_fractions_baseline2[lab] = stats_utils.check_baseline2(lab, mlByLab_folder, source="test",
                                                                                   picked_prevalence=train_prevalence,
                                                                                   picked_thres=train_thres)
                print lab, savable_fractions_baseline2[lab]
            df_baseline2 = stats_utils.dict2pandas(savable_fractions_baseline2, key='lab', val='savable_fraction_baseline2')


            '''
            Machine learning model
            '''
            # TODO: counts in the file needs update
            df_mlmodel = pd.read_csv('data_performance_stats/best-alg-panel-summary-fix-trainPPV.csv',
                             keep_default_na=False)
            df_mlmodel = df_mlmodel[(df_mlmodel['train_PPV']==0.95) & df_mlmodel['lab'].isin(labs)]
            df_mlmodel['savable_fraction_mlmodel'] = (df_mlmodel['true_positive'] + df_mlmodel['false_positive'])#.round(5)
            df_mlmodel = df_mlmodel[['lab', 'savable_fraction_mlmodel']]

            savable_fractions_mlmodel = stats_utils.pandas2dict(df_mlmodel, key='lab', val='savable_fraction_mlmodel')

            df_3methods = df_baseline1.merge(df_baseline2, on='lab', how='left')
            df_3methods = df_3methods.merge(df_mlmodel, on='lab', how='left')
            df_3methods.to_csv(result_tablepath, index=False)

        stats_utils.plot_subfigs([savable_fractions_baseline1,
                                  savable_fractions_baseline2,
                     savable_fractions_mlmodel],
                                 colors=('blue', 'green', 'orange'),
                     result_figpath=result_figpath)


    '''
    refactored
    '''
    ######################################


    def plot_cartoons(self, ml_folderpath):

        alg = 'random-forest'

        labs = ['LABPTT', 'LABLDH', 'LABTNI']
        local_lab_descriptions = {'LABPTT':"PTT PARTIAL\nTHROMBOPLASTIN TIME\n",
                                  'LABLDH':"LDH TOTAL\nSERUM / PLASMA\n",
                                  'LABTNI':"TROPONIN I\n"}

        col = 3
        row = len(labs)/col
        has_left_labs = (len(labs)%col!=0)

        fig_width, fig_heights = col * 3., 12. / col
        plt.figure(figsize=(fig_width, fig_heights))

        for i in range(row):
            for j in range(col):
                ind = i * col + j
                lab = labs[ind]

                df = pd.read_csv(ml_folderpath + "/%s/%s/direct_comparisons.csv"
                                 % (lab, alg), keep_default_na=False)
                scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
                scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

                df1 = pd.read_csv(ml_folderpath + "/%s/%s/%s-normality-prediction-%s-report.tab"
                                  % (lab, alg, lab, alg), sep='\t', keep_default_na=False)
                auc = df1['roc_auc'].values[0]

                if not has_left_labs:
                    plt.subplot2grid((row, col), (i, j))
                else:
                    plt.subplot2grid((row+1, col), (i, j))
                plt.hist(scores_actual_0, bins=30, alpha=0.8, color='r', label="abnormal")
                plt.hist(scores_actual_1, bins=30, alpha=0.8, color='g', label="normal")
                plt.xlim([0, 1])
                plt.ylim([0, 500])
                plt.xticks([])
                plt.yticks([])
                plt.xlabel(local_lab_descriptions[lab] + 'auroc=%.2f'%auc)
                if ind==0:
                    plt.legend()

        # plt.xlabel("%s score for %s"%(alg,lab))
        # plt.ylabel("num episodes, auroc=%f"%auc)
        # plt.legend()
        if has_left_labs:
            i = row
            for j in range(len(labs)%col):
                ind = i * col + j
                lab = labs[ind]

                df = pd.read_csv(ml_folderpath + "/%s/%s/direct_comparisons.csv"
                                 % (lab, alg), keep_default_na=False)
                scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
                scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

                df1 = pd.read_csv(ml_folderpath + "/%s/%s/%s-normality-prediction-%s-report.tab"
                                  % (lab, alg, lab, alg), sep='\t', keep_default_na=False)
                auc = df1['roc_auc'].values[0]

                if not has_left_labs:
                    plt.subplot2grid((row, col), (i, j))
                else:
                    plt.subplot2grid((row + 1, col), (i, j))
                plt.hist(scores_actual_0, bins=30, alpha=0.8, color='r', label="abnormal")
                plt.hist(scores_actual_1, bins=30, alpha=0.8, color='g', label="normal")
                plt.xlim([0, 1])
                plt.ylim([0, 500])
                plt.xticks([])
                plt.yticks([])
                plt.xlabel(lab_descriptions[lab])

        plt.tight_layout()

        plt.savefig('cartoons_%ss.png'%self.lab_type)


    def write_importantFeatures(self):
        stats_utils.output_feature_importances(self.all_labs,
                                               data_source=self.data_source,
                                               lab_type=self.lab_type,
                                               curr_version=self.curr_version)
        return


    def print_HosmerLemeshowTest():
        labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
        alg = 'random-forest'  # 'regress-and-round' #'random-forest'

        p_vals = []

        for lab in labs:
            df_new = pd.read_csv(
                '../machine_learning/data-panels-calibration-sigmoid/%s/%s/%s-normality-prediction-%s-direct-compare-results.csv'
                % (lab, alg, lab, alg),
                keep_default_na=False)
            actual = df_new['actual'].values
            predict = df_new['predict'].values
            p_val = stats_utils.Hosmer_Lemeshow_Test(actual_labels=actual, predict_probas=predict)
            p_vals.append(p_val)

        print sorted(p_vals)



    def get_best_calibrated_labs(statsByLab_folderpath, top_k=20, worst=False):
        df_fix_train = pd.read_csv(statsByLab_folderpath + "/summary-stats-bestalg-fixTrainPPV.csv",
                                   keep_default_na=False)
        df_fix_train['abs_PPV_diff'] = (df_fix_train['targeted_PPV_fixTrainPPV'] - df_fix_train['PPV'].apply(
            lambda x: float(x) if x != '' else float('nan'))).abs()

        lab_diff = {}
        for lab in all_labs:
            cur_tot_diff = df_fix_train[df_fix_train['lab']==lab]['abs_PPV_diff'].values.sum()
            lab_diff[lab] = cur_tot_diff

        if not worst:
            best_labs = [x[0] for x in sorted(lab_diff.iteritems(), key=lambda (k,v):v)[:top_k]]
        else:
            best_labs = [x[0] for x in sorted(lab_diff.iteritems(), key=lambda (k, v): v)[-top_k:]]
        print best_labs
        # for lab in best_labs:
        #     print df_fix_train[df_fix_train['lab']==lab][['lab', 'targeted_PPV_fixTrainPPV', 'PPV']].to_string(index=False)
        df_res = df_fix_train[df_fix_train['lab'].isin(best_labs)][['lab', 'targeted_PPV_fixTrainPPV', 'PPV', 'abs_PPV_diff']]#.sort_values(['lab','targeted_PPV_fixTrainPPV'])
        df_res_long = df_res.pivot(index='lab', columns='targeted_PPV_fixTrainPPV', values='PPV').reset_index()
        # print df_res_long
        df_res_long['abs_PPV_diff'] = df_res_long['lab'].map(lab_diff)
        df_res_long = df_res_long.rename(columns={0.80:'target 0.80', 0.90:'target 0.90', 0.95:'target 0.95', 0.99:'target 0.99'})
        df_res_long['lab'] = df_res_long['lab'].apply(lambda x:lab_descriptions[x])
        df_res_long.sort_values('abs_PPV_diff').drop(columns=['abs_PPV_diff']).to_csv(statsByLab_folderpath+'/best_calibrated_is_worst_%s.csv'%worst, index=False)

    def PPV_guideline(statsByLab_folderpath):

        df_fix_train = pd.read_csv(statsByLab_folderpath + "/summary-stats-bestalg-fixTrainPPV.csv",
                                   keep_default_na=False)

        range_bins = [0.99] + np.linspace(0.95, 0.5, num=10).tolist()
        columns = ['Target PPV', 'Total labs', 'Valid labs']
        columns += ['[0.99, 1]']
        for i in range(len(range_bins) - 1):
            columns += ['[%.2f, %.2f)' % (range_bins[i + 1], range_bins[i])]

        rows = []
        actual_PPVs = {}
        actual_median_PPV = {}
        for targeted_PPV in [0.8, 0.90, 0.95, 0.99][::-1]: # TODO: what is the problem with 0.9? LABHIVWBL
            cur_row = [targeted_PPV]

            PPVs_from_train = df_fix_train.ix[df_fix_train['targeted_PPV_fixTrainPPV']==targeted_PPV, ['PPV']]
            cur_row.append(PPVs_from_train.shape[0]) # "Total number of labs:"

            PPVs_from_train = PPVs_from_train.dropna()['PPV'].values
            PPVs_from_train = np.array([float(x) for x in PPVs_from_train if x!='']) #TODO: why?
            actual_PPVs[targeted_PPV] = PPVs_from_train.tolist()

            vaild_PPV_num = PPVs_from_train.shape[0]
            cur_row.append(vaild_PPV_num) # "Valid number of labs:"

            print "When target at PPV %.2f, the mean/median PPV among %i labs is %.3f/%.3f, std is %.3f"\
                  %(targeted_PPV, vaild_PPV_num, np.mean(PPVs_from_train), np.median(PPVs_from_train), np.std(PPVs_from_train))
            actual_median_PPV[targeted_PPV] = np.median(PPVs_from_train)

            cur_cnt = sum(PPVs_from_train >= 0.99)
            cur_row.append(cur_cnt)

            for i in range(len(range_bins)-1):
                cur_cnt = sum((range_bins[i+1] <= PPVs_from_train) & (PPVs_from_train < range_bins[i]))
                cur_row.append(cur_cnt)

            rows.append(cur_row)

        actual_PPVs_df = pd.DataFrame.from_dict(actual_PPVs, orient='index').transpose()
        actual_PPVs_df = actual_PPVs_df.melt(var_name='Targeted PPV', value_name='Actual PPVs')
        import seaborn
        # seaborn.set(style="ticks", palette="colorblind")
        actual_PPVs_df['side'] = actual_PPVs_df['Targeted PPV'].apply(lambda x:0)
        actual_PPVs_df['side'].iloc[-1]=-999

        fig, ax = plt.subplots(figsize=(8,6))
        seaborn.violinplot(x='Targeted PPV', y='Actual PPVs', data=actual_PPVs_df, hue='side', split=True,
                           #palette = ['o']
                           )

        for i, v in enumerate([0.8, 0.90, 0.95, 0.99]):
            print actual_median_PPV
            ax.text(i, actual_median_PPV[v], '%.3f'%actual_median_PPV[v], color='k')

        leg = plt.gca().legend()
        leg.remove()
        plt.ylim([0.35,1.15])
        plt.savefig(os.path.join(statsByLab_folderpath, 'violinplot.png'))

        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(statsByLab_folderpath + "/predict_power_%ss.csv"%self.lab_type, index=False)


    def test(self, lab):
        # data_file = pd.read_csv('stats_useful_data/' + '%s_Usage_2014-2016.csv' % lab)
        # print data_file['pat_id'].values[:10]
        # print len(list(set(data_file['pat_id'].values.tolist())))

        results = stats_utils.query_lab_usage__df(lab=lab,
                                                  lab_type='panel',
                                                  time_start='2014-01-01',
                                                  time_end='2016-12-31')
        df = pd.DataFrame(results, columns=['pat_id', 'order_time', 'result'])

        prevday_cnts_dict = stats_utils.get_prevday_cnts__dict(df)

    def draw__Comparing_PPVs(self, statsByLab_folderpath, include_labnames=False):
        summary_filename = 'summary-stats-bestalg-fixTrainPPV.csv'
        summary_filepath = os.path.join(statsByLab_folderpath, summary_filename)
        df = pd.read_csv(summary_filepath, keep_default_na=False)
        # print df.shape
        df = df[['lab','targeted_PPV_fixTrainPPV','PPV']]
        df = df[df['PPV']!='']

        result_foldername = 'Fig3_Comparing_PPVs/'
        result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
        if not os.path.exists(result_folderpath):
            os.mkdir(result_folderpath)

        result_figurename = 'Comparing_PPVs.png'
        result_figurepath = os.path.join(result_folderpath, result_figurename)
        labs = df['lab'].values.tolist()

        # print df['targeted_PPV_fixTrainPPV'].values.tolist()
        target_PPVs = df['targeted_PPV_fixTrainPPV'].values.tolist()
        true_PPVs = [float(x) for x in df['PPV'].values.tolist() if x!='']

        fig, ax = plt.subplots(figsize=(8,6))
        plt.scatter(target_PPVs, true_PPVs)
        # plt.xlim([0, 1])
        # plt.ylim([0,1])

        if include_labnames:
            texts = []
            for i, txt in enumerate(labs):
                texts.append(ax.annotate(txt, (target_PPVs[i], true_PPVs[i])))

        plt.xlabel('Targetd PPV')
        plt.ylabel('Actual PPV')

        plt.savefig(result_figurepath)

    def comparing_components(self, stats_folderpath, target_PPV=0.95):
        stats_filename = 'summary-stats-bestalg-fixTrainPPV.csv'

        labs_important = stats_utils.get_important_labs(lab_type='component')

        stanford_filepath = os.path.join(stats_folderpath, 'data-Stanford-component-%s'%self.curr_version, stats_filename)
        umich_filepath = os.path.join(stats_folderpath, 'data-UMich-component-%s'%self.curr_version, stats_filename)
        ucsf_filepath = os.path.join(stats_folderpath, 'data-UCSF-component-%s'%self.curr_version, stats_filename)



        df_stanford = pd.read_csv(stanford_filepath, keep_default_na=False)
        df_stanford = df_stanford[df_stanford['targeted_PPV_fixTrainPPV']==target_PPV]

        df_umich = pd.read_csv(umich_filepath, keep_default_na=False)
        df_umich = df_umich[df_umich['targeted_PPV_fixTrainPPV'] == target_PPV]

        df_ucsf = pd.read_csv(ucsf_filepath, keep_default_na=False)
        df_ucsf = df_ucsf[df_ucsf['targeted_PPV_fixTrainPPV'] == target_PPV]

        for df in [df_stanford, df_umich, df_ucsf]:
            df['total_cnt'] = df['true_positive'] + df['false_positive'] + df['true_negative'] + df['false_negative']
            df['true_positive'] = df['true_positive'] / df['total_cnt']
            df['false_positive'] = df['false_positive'] / df['total_cnt']
            df['true_negative'] = df['true_negative'] / df['total_cnt']
            df['false_negative'] = df['false_negative'] / df['total_cnt']


        df_stanford = df_stanford[df_stanford['lab'].isin(labs_important)]
        df_stanford['predicted_normal_Stanford'] = df_stanford['true_positive']+df_stanford['false_positive']

        df_stanford = df_stanford.rename(columns={'AUROC':'AUC_Stanford',
                                                  #'baseline2_ROC':'B_ROC_Stanford',
                                                  'PPV':'PPV_Stanford',
                                                  'true_positive': 'TP_Stanford',
                                                  'false_positive': 'FP_Stanford',
                                                  'true_negative': 'TN_Stanford',
                                                  'false_negative': 'FN_Stanford'
                                                  })


        #umich_replace = {'SOD':'NA', 'POT':'K', 'CREAT': 'CR'}
        df_convert_table_UMich = pd.read_csv('../machine_learning/data_conversion/map_UMich_component_raw2code.csv', keep_default_na=False)
        umich_replace = dict(zip(df_convert_table_UMich['raw'].values.tolist(), df_convert_table_UMich['lab'].values.tolist()))
        df_umich['lab'] = df_umich['lab'].apply(lambda x: umich_replace[x] if x in umich_replace else x)
        df_umich['predicted_normal_UMich'] = df_umich['true_positive'] + df_umich['false_positive']
        df_umich = df_umich.rename(columns={'AUROC': 'AUC_UMich',
                                            #'baseline2_ROC': 'B_ROC_UMich',
                                                  'PPV':'PPV_UMich',
                                                  'true_positive': 'TP_UMich',
                                                  'false_positive': 'FP_UMich',
                                                  'true_negative': 'TN_UMich',
                                                  'false_negative': 'FN_UMich'
                                                  })

        # ucsf_replace = {'CREAT': 'CR'}
        df_convert_table_UCSF = pd.read_csv('../machine_learning/data_conversion/map_UCSF_component_raw2code.csv',
                                             keep_default_na=False)
        ucsf_replace = dict(
            zip(df_convert_table_UCSF['raw'].values.tolist(), df_convert_table_UCSF['lab'].values.tolist()))
        df_ucsf['lab'] = df_ucsf['lab'].apply(lambda x: ucsf_replace[x] if x in ucsf_replace else x)
        df_ucsf['predicted_normal_UCSF'] = df_ucsf['true_positive'] + df_ucsf['false_positive']
        df_ucsf = df_ucsf.rename(columns={'AUROC': 'AUC_UCSF',
                                          #'baseline2_ROC': 'B_ROC_UCSF',
                                                  'PPV':'PPV_UCSF',
                                            'true_positive': 'TP_UCSF',
                                            'false_positive': 'FP_UCSF',
                                            'true_negative': 'TN_UCSF',
                                            'false_negative': 'FN_UCSF'
                                            })

        columns = ['lab', 'AUC', 'PPV', 'predicted_normal']#, 'true_positive', 'false_positive', 'true_negative', 'false_negative']
        columns_stanford = [x+'_Stanford' if x !='lab' else x for x in columns]
        columns_umich = [x+'_UMich' if x !='lab' else x for x in columns]
        columns_ucsf = [x+'_UCSF' if x !='lab' else x for x in columns]

        merged_df = pd.merge(df_stanford[columns_stanford], df_umich[columns_umich], how='left', on='lab')
        merged_df = pd.merge(merged_df, df_ucsf[columns_ucsf], how='left', on='lab')

        columns_show = [x.replace('_',' ') for x in merged_df.columns]

        merged_df = merged_df.rename(columns=dict(zip(merged_df.columns, columns_show)))

        columns_merged = merged_df.columns.tolist()
        columns_merged.remove('lab')
        columns_merged = ['lab'] + sorted(columns_merged)
        merged_df['lab'] = merged_df['lab'].apply(lambda x: self.lab_descriptions.get(x,x))

        merged_df['PPV Stanford'] = pd.to_numeric(merged_df['PPV Stanford'])
        merged_df['PPV UCSF'] = pd.to_numeric(merged_df['PPV UCSF'])
        merged_df['PPV UMich'] = pd.to_numeric(merged_df['PPV UMich'])

        for col_merged in merged_df.columns.values.tolist():
            if col_merged != 'lab' and 'AUC' not in col_merged:
                merged_df[col_merged] = merged_df[col_merged].apply(lambda x: stats_utils.convert_floatnum2percentage(x))
            elif 'AUC' in col_merged:
                merged_df[col_merged] = merged_df[col_merged].apply(lambda x: '%.2f'%x)
        merged_df[columns_merged].to_csv(os.path.join(stats_folderpath, 'components_comparisons.csv'), index=False)


    def draw__predicted_normal_fractions(statsByLab_folderpath, targeted_PPV):
        labs_stats_filepath = os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')

        df = pd.read_csv(labs_stats_filepath)

        df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]

        result_foldername = 'Predicted_Normal_Fractions'
        result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
        if not os.path.exists(result_folderpath):
            os.mkdir(result_folderpath)
        result_figname = 'Predicted_Normal_Fractions_%.2f.png'%targeted_PPV
        result_figpath = os.path.join(result_folderpath, result_figname)

        df['predicted_normal'] = (df['true_positive'] + df['false_positive']) / df['num_test_episodes']

        df['description'] = df['lab'].apply(lambda x: lab_descriptions.get(x, x))
        # print df[['description', 'predicted_normal']].sort_values(['predicted_normal'], ascending=False).to_string(index=False)

        predicted_normal_fractions = np.linspace(0, 1, num=11)
        nums_labs = []
        for predicted_normal_fraction in predicted_normal_fractions:
            df_predicted_normal = df[df['predicted_normal'] > predicted_normal_fraction]#[['lab', 'predicted_normal']]
            num_labs = df_predicted_normal.shape[0]
            nums_labs.append(num_labs)

            if predicted_normal_fraction == 0.5:
                print 'over-utilized labs:', df_predicted_normal['lab'].values.tolist()

            if predicted_normal_fraction == 0.9:
                these_labs = df_predicted_normal['lab'].values.tolist()
                print 'highly over-utilized labs:', [lab_descriptions[x] for x in these_labs]
        print zip(predicted_normal_fractions, nums_labs)
        plt.scatter(predicted_normal_fractions, nums_labs)
        plt.xlabel('Predicted normal fraction, targeting at PPV=%.2f' % targeted_PPV)
        plt.ylabel('Number of labs')
        plt.savefig(result_figpath)

    def draw_histogram_transfer_modeling(self, src_dataset='Stanford', dst_dataset='UCSF', lab_type='panel'):
        print "Running draw_histogram_transfer_modeling..."

        from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import STRIDE_COMPONENT_TESTS

        ml_folder = ml_results_folderpath

        '''
        
        '''
        panels_stanford = ['LABMGN', 'LABK', 'LABNA', 'LABPHOS', 'LABURIC', 'LABTNI',
                           'LABPT', 'LABPTT', 'LABCAI', 'LABALB', 'LABTSH'
                ]
        # lab_map_df = pd.read_csv(os.path.join(ml_folder, 'data_conversion/map_UCSF_panel_raw2code.csv'), keep_default_na=False)
        # panels_stanford = lab_map_df['lab'].values.tolist()

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
                                                   all_algs=['random-forest'],
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
                                               all_algs=['random-forest'],
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

    def plot_full_cartoon(self, lab='LABLDH', include_threshold_colors = True):
        print 'Running plot_full_cartoon...'

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
        plt.plot(xVal_best, yVal_best, color='orange', linewidth=2) #, label='random forest', AUROC=%0.2f  % (score_best)

        if include_threshold_colors:
            df_directcompare_rf = pd.read_csv(os.path.join(ml_folderpath, lab, 'random-forest', 'direct_comparisons.csv'))
            actual_labels = df_directcompare_rf['actual'].values
            predict_probas = df_directcompare_rf['predict'].values

            sensitivity, specificity, LR_p, LR_n, PPV, NPV = stats_utils.get_confusion_metrics(actual_labels, predict_probas, score_thres, also_return_cnts=False)
            print "sensitivity", sensitivity
            print "specificity", specificity
            print "score_thres", score_thres

            plt.scatter(1-specificity, sensitivity, s=50, color='orange')

            dash_num = 20
            # plt.plot([1-specificity]*dash_num, np.linspace(0,1,num=dash_num), 'k--')
            plt.plot(np.linspace(0,1,num=dash_num),np.linspace(0,1,num=dash_num), color='lightblue', linestyle='--')


        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.xticks([])
        plt.yticks([])
        plt.ylabel('Sensitivity', fontsize=16) #lab_descriptions.get(lab, lab)
        plt.xlabel('1-Specificity', fontsize=16)
        plt.legend(fontsize=12)
        plt.savefig(os.path.join(statsByLab_folderpath, 'ROC_%s.png'%lab))

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

            plt.hist(scores_actual_trueNega, bins=22, alpha=0.8, color='royalblue', label="true negatives")
            plt.hist(scores_actual_falsNega, bins=22, alpha=0.8, color='gold', label="false negatives")
            plt.hist(scores_actual_truePosi, bins=7, alpha=0.8, color='forestgreen', label="true positives")
            plt.hist(scores_actual_falsPosi, bins=7, alpha=0.8, color='orangered', label="false positives")

            plt.plot([score_thres] * dash_num, np.linspace(0, 800, num=dash_num), 'k--')

            plt.legend(loc=(0.1,0.6), fontsize=12)

        else:

            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            plt.hist(scores_actual_0, bins=30, alpha=0.8, color='red', label="Abnormal") #gray
            plt.hist(scores_actual_1, bins=30, alpha=0.8, color='green', label="Normal") #black

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
            plt.savefig(os.path.join(statsByLab_folderpath, 'cartoon_%s_thres.png' % lab))
        else:
            plt.savefig(os.path.join(statsByLab_folderpath, 'cartoon_%s.png' % lab))



    '''
    For each (train-)PPV wanted, each vital-day dataset
    Create a summary of all algs' performances on all labs
    '''

    def main_labs2stats(self, train_data_folderpath, ml_results_folderpath, stats_results_folderpath,
                        targeted_PPVs=train_PPVs, columns=None, thres_mode="fixTrainPPV"):
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

        for lab in self.all_labs:
            '''
            lab, total_vol_20140701_20170701, medicare, chargemaster, 
            num_train_episodes, num_train_patients, num_test_episodes, num_test_patients, 
            AUC_baseline
            '''

            for targeted_PPV in targeted_PPVs:
                # try:
                stats_results_filename = results_filename_template % (lab, thres_mode, str(targeted_PPV))
                stats_results_filepath = os.path.join(stats_results_folderpath, 'stats_by_lab_alg',
                                                      stats_results_filename)
                if not os.path.exists(os.path.join(stats_results_folderpath, 'stats_by_lab_alg')):
                    os.mkdir(os.path.join(stats_results_folderpath, 'stats_by_lab_alg'))

                if not os.path.exists(stats_results_filepath):
                    '''
                    
                    '''

                    stats_utils.lab2stats(lab=lab,
                                          data_source=self.data_source,
                                          lab_type=self.lab_type,
                                          all_algs=all_algs,
                                          targeted_PPV=targeted_PPV,
                                          columns=columns,
                                          thres_mode=thres_mode,
                                          train_data_labfolderpath=os.path.join(train_data_folderpath, lab),
                                          ml_results_labfolderpath=os.path.join(ml_results_folderpath, lab),
                                          stats_results_filepath=stats_results_filepath
                                          )
                # except Exception as e:
                #     print e
                #     continue

    def main_stats2summary(self, targeted_PPVs=train_PPVs, columns=None, thres_mode="fixTrainPPV"):

        df_long = pd.DataFrame(columns=columns)

        columns_best_alg = [x if x != 'alg' else 'best_alg' for x in columns]
        df_best_alg = pd.DataFrame(columns=columns_best_alg)

        project_stats_folderpath = os.path.join(stats_results_folderpath, self.dataset_foldername)

        for targeted_PPV in targeted_PPVs:
            for lab in self.all_labs:
                stats_results_filename = results_filename_template % (lab, thres_mode, str(targeted_PPV))
                stats_results_filepath = os.path.join(project_stats_folderpath, 'stats_by_lab_alg',
                                                      stats_results_filename)
                # results_filepath = results_filepath_template % (lab, thres_mode, str(targeted_PPV))
                df_lab = pd.read_csv(stats_results_filepath, keep_default_na=False)
                df_lab['targeted_PPV_%s' % thres_mode] = targeted_PPV

                df_long = df_long.append(df_lab, ignore_index=True)

                df_cur_best_alg = df_lab.groupby(['lab'], as_index=False).agg({'AUROC': 'max'})
                df_cur_best_alg = pd.merge(df_cur_best_alg, df_lab, on=['lab', 'AUROC'], how='left')

                df_cur_best_alg = df_cur_best_alg.rename(columns={'alg': 'best_alg'})
                df_best_alg = df_best_alg.append(df_cur_best_alg)

        '''
        TODO:!
        '''
        if self.lab_type=='panel' and self.data_source=='Stanford':
            df_chargemasters = pd.read_csv('data_summary_stats/labs_charges_volumes.csv', keep_default_na=False)
            df_chargemasters = df_chargemasters.rename(columns={'name':'lab', 'median_price':'chargemaster'})
            df_long = df_long.drop(['chargemaster'], axis=1)
            df_long = pd.merge(df_long, df_chargemasters[['lab', 'chargemaster']], on='lab', how='left')

            df_best_alg = df_best_alg.drop(['chargemaster'], axis=1)
            df_best_alg = pd.merge(df_best_alg, df_chargemasters[['lab', 'chargemaster']], on='lab', how='left')

        summary_long_filename = 'summary-stats-%s-%s.csv' % ('allalgs', thres_mode)
        summary_long_filepath = os.path.join(project_stats_folderpath, summary_long_filename)

        df_long[columns].to_csv(summary_long_filepath, index=False)

        summary_best_filename = 'summary-stats-%s-%s.csv' % ('bestalg', thres_mode)
        summary_best_filepath = os.path.join(project_stats_folderpath, summary_best_filename)
        df_best_alg[columns_best_alg].to_csv(summary_best_filepath, index=False)

        # df_long[columns].to_csv(summary_filepath_template%('allalgs', thres_mode), index=False)
        # df_best_alg[columns_best_alg].to_csv(summary_filepath_template%('bestalg', thres_mode), index=False)

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

    def main_basic_tables(self, train_data_folderpath, ml_results_folderpath, stats_results_folderpath, thres_mode="fixTrainPPV"):
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
                        thres_mode=thres_mode)

        self.main_stats2summary(targeted_PPVs=train_PPVs,
                           columns=columns,
                           thres_mode=thres_mode)

        # self.main_attachBaseline(targeted_PPVs=train_PPVs,
        #                     columns=[x + '_baseline' for x in columns_statsMetrics],
        #                     thres_mode=thres_mode)

    def main_generate_lab_statistics(self):
        print 'generate_result_tables running...'

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
             thres_mode="fixTrainPPV")

    def main_generate_stats_figures_tables(self, figs_to_plot, params={}):
        print 'stats_sx running...'

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
            labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels) - set(
                ['LABTSH', 'LABLDH']))

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
            get_best_calibrated_labs(statsByDataSet_folderpath, worst=False)

        if 'Savable_Fractions' in figs_to_plot:
            draw__Comparing_Savable_Fractions(statsByDataSet_folderpath, target_PPV=0.95, use_cache=True)

        if 'Comparing_PPVs' in figs_to_plot:
            draw__Comparing_PPVs(statsByDataSet_folderpath)

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
                self.draw__stats_Curves(statsByDataSet_folderpath, lab_set, curve_type="ROC", algs=['random-forest'],
                                   result_label=set_label)
            if 'PRC' in figs_to_plot:
                self.draw__stats_Curves(statsByDataSet_folderpath, lab_set, curve_type="PRC", algs=['random-forest'],
                                   result_label=set_label)

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
            top_panels_cnts = stats_utils.get_top_labs_and_cnts(top_k=20)
            top_panels = [x[0] for x in top_panels_cnts]
            panels = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels)) + ['LABK', 'LABNA', 'LABLIDOL'] #, 'LABCR', 'LABPTT', 'LABCAI'
            components = ['WBC', 'HGB', 'PLT', 'NA', 'K', 'CL', 'CR', 'BUN', 'CO2', 'CA', \
                          'TP', 'ALB', 'ALKP', 'TBIL', 'AST', 'ALT', 'DBIL', 'IBIL', 'PHA']
            important_components = stats_utils.get_important_labs('component')

            result_label = params.get('Diagnostic_Metrics', 'all_labs')

            if self.data_source == 'Stanford':
                if self.lab_type == 'panel':
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label,
                                            targeted_PPV=0.95, scale_by='enc', use_cached_fig_data=False)
                else:
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label,
                                            targeted_PPV=0.95, scale_by='enc', use_cached_fig_data=False)
            elif self.data_source == 'UCSF':
                self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label,
                                        targeted_PPV=0.95, scale_by='enc_ucsf', use_cached_fig_data=False)

            elif self.data_source == 'UMich':
                if self.lab_type == 'component':
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs, result_label=result_label, #important_components
                                            targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False)
                else:
                    self.draw__Diagnostic_Metrics(statsByDataSet_folderpath, labs=self.all_labs,
                                                 result_label=result_label,
                                                 targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False)

        if 'Predicted_Normal' in figs_to_plot:
            self.draw__predicted_normal_fractions(statsByLab_folderpath=statsByDataSet_folderpath, targeted_PPV=0.95)

        if 'Potential_Savings' in figs_to_plot:
            self.draw__Potential_Savings(statsByDataSet_folderpath, scale=scale, result_label='all_four',
                                    targeted_PPV=0.95, use_cached_fig_data=False, price_source='medicare')

        if 'Model_Transfering' in figs_to_plot:
            self.draw_histogram_transfer_modeling()

        if 'Full_Cartoon' in figs_to_plot:
            self.plot_full_cartoon(lab='LABLDH', include_threshold_colors=False)

        if 'write_importantFeatures' in figs_to_plot:
            self.write_importantFeatures()

def statistic_analysis(lab, dataset_folder):
    from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score

    direct_comparisons = pd.read_csv(os.path.join(dataset_folder, 'direct_comparisons.csv'))
    # print direct_comparisons
    return roc_auc_score(direct_comparisons['actual'].values, direct_comparisons['predict'].values)

def get_AUC_transfer_labs(src_dataset='Stanford', dst_dataset='UCSF', lab_type='panel', curr_version='10000-episodes'):
    # main_pipelining(labs=['LABA1C'], data_source='testingSupervisedLearner')
    # dataset_folder = "data-apply-Stanford-to-UCSF-10000-episodes"

    # from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS

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

from scripts.LabTestAnalysis.machine_learning import LabNormalityLearner
def main_transfer_model(curr_version, lab_type='component'):
    all_sites = ['Stanford', 'UMich', 'UCSF']

    res_folderpath = 'data-transferring-component-%s/'%curr_version
    if not os.path.exists(res_folderpath):
        os.mkdir(res_folderpath)

    res_filepath = res_folderpath + 'all_transfers.csv'

    if os.path.exists(res_filepath):
        df_res = pd.read_csv(res_filepath, keep_default_na=False)

    else:

        from scripts.LabTestAnalysis.lab_statistics import stats_utils
        labs = stats_utils.get_important_labs(lab_type='component')


        all_res_dicts = {}
        all_res_dicts['lab'] = labs

        columns = ['lab']
        for i in range(3): # Training sources
            for j in range(3): # Testing sources
                src = all_sites[i]
                dst = all_sites[j]


                '''
                '''
                ml_folder = ml_results_folderpath
                LabNormalityLearner.transfer_labs(src_dataset=src, dst_dataset=dst, lab_type=lab_type,
                                                  cur_version=curr_version)
                transfer_result_folderpath = ml_folder + '/data-%s-src-%s-dst-%s-%s/' \
                                             % (lab_type, src, dst, curr_version)
                cur_res = []
                for lab in labs:
                    direct_comparisons_folderpath = os.path.join(transfer_result_folderpath, lab)

                    cur_AUC = statistic_analysis(lab=lab, dataset_folder=direct_comparisons_folderpath)
                    cur_res.append(cur_AUC)

                '''
                '''


                col = '%s -> %s' % (src, dst)
                all_res_dicts[col] = cur_res

                columns.append(col)
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
                         xticklabels=['S', 'UM', 'UC'], yticklabels=['S', 'UM', 'UC'])
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

def main_full_analysis(curr_version):
    for data_source in ['Stanford', 'UMich', 'UCSF']:
        for lab_type in ['panel', 'component']:

            plotter = Stats_Plotter(data_source=data_source, lab_type=lab_type, curr_version=curr_version)
            plotter.main_generate_lab_statistics()

            if data_source=='Stanford' and lab_type=='panel':
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Full_Cartoon', # Figure 1
                                                                         'Order_Intensities', # Figure 2
                                                                         'Diagnostic_Metrics', # Table 1 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures' # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'}) # TODO ['top_15', 'all_labs']

            elif data_source=='Stanford' and lab_type=='component':
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'important_components'})  # TODO ['common_components', 'all_labs']
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'})

            elif data_source=='UMich' and lab_type=='panel':
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'})  # TODO

            elif data_source=='UMich' and lab_type=='component':
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'important_components'})  # TODO

                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'})  # TODO

            elif data_source=='UCSF' and lab_type=='panel':
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'})  # TODO

            elif data_source=='UCSF' and lab_type=='component':
                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'important_components'})  # TODO

                plotter.main_generate_stats_figures_tables(figs_to_plot=['Diagnostic_Metrics',  # Figure 3 & SI Table
                                                                         'ROC',  # SI Figure
                                                                         'write_importantFeatures'  # SI Table
                                                                         ],
                                                           params={'Diagnostic_Metrics': 'all_labs'})  # TODO

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

    plotter = Stats_Plotter(data_source="Stanford", lab_type='panel')
    if 'LDH_cartoons' in main_figuretables:
        plotter.plot_full_cartoon(lab='LABLDH', include_threshold_colors=False)

    quit()

    figs_to_plot = []


    plotter.main_generate_stats_figures_tables(figs_to_plot=figs_to_plot,
                                               params={'Diagnostic_Metrics': 'important_components'})

    # plotter.main(figs_to_plot=['Normality_Saturations'])
    # plotter.main_generate_lab_statistics()


if __name__ == '__main__':
    curr_version = '10000-episodes-lastnormal'

    # main_one_analysis(curr_version=curr_version)
    main_full_analysis(curr_version=curr_version)
