
import os
import stats_utils
import datetime
import collections
import pandas as pd
import numpy as np
import pickle

pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


lab_type = stats_utils.lab_type
all_labs = stats_utils.all_labs
# # labs_ml_folder = stats_utils.labs_ml_folder
# # labs_stats_folder = stats_utils.labs_stats_folder
all_algs = stats_utils.all_algs
#
DEFAULT_TIMELIMIT = stats_utils.DEFAULT_TIMELIMIT
#
lab_descriptions = stats_utils.get_lab_descriptions()




def draw__Normality_Saturations(stats_folderpath, labs=['LABMETB', 'LABCBCD'] + all_labs, max_repeat = 5, use_cached_fig_data=True):
    '''
    Drawing Figure 1 in the main text.

    :return:
    '''

    print "Labs to be plot:", labs

    cached_result_foldername = os.path.join(stats_folderpath, 'Fig1_Normality_Saturations/')
    if not os.path.exists(cached_result_foldername):
        os.mkdir(cached_result_foldername)
    # cached_result_filename = 'Normality_Saturations_%s.csv' % lab_type
    # cached_result_path = os.path.join(cached_result_foldername, cached_result_filename)


    if os.path.exists(cached_result_foldername + 'lab2cnt.csv') and use_cached_fig_data:
        # lab2stats = pickle.load(open(cached_result_path, 'r'))
        # lab2stats_pd = pd.read_csv(cached_result_path)
        # lab2stats_pd = lab2stats_pd.set_index('lab')
        # lab2stats_pd.columns = lab2stats_pd.columns.astype(int)
        #
        # lab2stats = lab2stats_pd.to_dict(orient='index')
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
            df_lab = stats_utils.get_queried_lab(lab, time_limit=DEFAULT_TIMELIMIT)
            df_lab = df_lab[df_lab['order_status'] == 'Completed']

            cur_dict = stats_utils.get_prevweek_normal__dict(df_lab)
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

    print lab2cnt
    print lab2frac

    fig = plt.figure(figsize=(8, 6))

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
            print lab, y_s
            plt.plot(non_empty_inds, y_s, '-'+marker_types[k], label=lab_descriptions[lab])
            # l2, = plt.scatter(non_empty_inds, y_s, marker=marker_types[k])
            # plt.plot(y_s[0], '-'+marker_types[k], color=l2.get_color(), markerfacecolor=l1.get_color(), label='My plots')

        plt.xticks(range(0, max_repeat + 1))
        plt.xlabel('Number of Consecutive Normalities in a Week', fontsize=12)
        plt.ylabel('Normal Rate', fontsize=12)
        # plt.ylim([0, 1])
        plt.legend()
        plt.tight_layout()
        plt.savefig(cached_result_foldername + 'Normality_Saturations_%s_%i'%(lab_type, ind))
        plt.clf()


def draw__Potential_Savings(statsByLab_folderpath, scale_by=None, targeted_PPV=0.95, use_cached_fig_data=False):
    '''
    Drawing Figure 4 in the main text.

    :return:
    '''

    df = pd.read_csv(os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv'),
                     keep_default_na=False)
    print df.head()
    df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]

    # labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=50)
    df = df[df['lab'].isin(all_labs)] #[x[0] for x in labs_and_cnts]

    result_foldername = 'Fig4_Potential_Savings/'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)

    '''
    Hierarchy:
    
    '''

    fig_filename = 'Potential_Savings_PPV_%.2f.png'%targeted_PPV
    fig_path = os.path.join(result_folderpath, fig_filename)
    data_filename = 'Potential_Savings_%.2f.csv'%targeted_PPV
    data_path = os.path.join(result_folderpath, data_filename)

    if os.path.exists(data_path) and use_cached_fig_data:
        df_sorted_by_normal_cost = pd.read_csv(data_path, keep_default_na=False)

    else:


        # df = df[df['lab'] != 'LABNA']  # TODO: fix LABNA's price here
        df['true_positive_fraction'] = df['true_positive']/df['num_test_episodes']
        df['false_negative_fraction'] = df['false_negative'] / df['num_test_episodes']

        df['normal_rate'] = (df['true_positive_fraction'] + df['false_negative_fraction']).round(5)

        # if lab_type == "component":
        #     df = df.rename(columns={'2016_Vol': 'count'})
        #     df = df.dropna()
        # df['count'] = df['count'].apply(lambda x: 0 if x == '' else x)

        # my_dict = {x[0]: x[1] for x in labs_and_cnts}
        # df['count'] = df['lab'].map(my_dict)

        # df['total cost'] = df['count'].apply(lambda x: float(x) / 1000000.)  #
        df['count'] = df['2014 2stHalf count'] + df['2015 1stHalf count'] \
                      + df['2015 2stHalf count'] + df['2016 1stHalf count'] \
                      + df['2016 2stHalf count'] + df['2017 1stHalf count']

        df['total_cost'] = df['count'] * df['median_price'].apply(lambda x:float(x) if x!='' else 0)  # /1000000., cost
        # volumn_label = 'Total cost in 2014-2016'
        print df.shape
        df = df[df['total_cost']>0]

        print df.shape

        # df_sorted_by_cnts = df.sort_values('total_cost', ascending=True).ix[:,
        #                     ['lab', 'normal_rate', 'true_positive', 'total_cost']].drop_duplicates()#.head(20).copy()
        df = df[['lab', 'normal_rate', 'true_positive_fraction', 'total_cost']]

        # df_sorted_by_cnts = df_sorted_by_cnts.sort_values('volumn', ascending=True)


        # ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['volumn'], color='grey', alpha=0.5,
        #         label=volumn_label)

        df['normal_cost'] = df['normal_rate'] * df['total_cost']
        df['truepo_cost'] = df['true_positive_fraction'] * df['total_cost']

        df_sorted_by_normal_cost = df.sort_values('truepo_cost', ascending=True)#.tail(10)
        df_sorted_by_normal_cost.to_csv(data_path, index=False)


    # unit, scale = 'million', 10.**6


    if not scale_by:
        scale = 1.
    elif scale_by == 'pat':
        scale = float(stats_utils.NUM_DISTINCT_PATS)
    elif scale_by == 'enc':
        scale = float(stats_utils.NUM_DISTINCT_ENCS)

    df_sorted_by_normal_cost['normal_cost'] = df_sorted_by_normal_cost['normal_cost']/scale
    df_sorted_by_normal_cost['truepo_cost'] = df_sorted_by_normal_cost['truepo_cost']/scale
    df_sorted_by_normal_cost['lab_description'] = df_sorted_by_normal_cost['lab'].apply(
        lambda x: lab_descriptions[x])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df_sorted_by_normal_cost['lab_description'], df_sorted_by_normal_cost['normal_cost'],
            color='blue', alpha=0.5, label='Low yield lab cost')
    # for i, v in enumerate(df_sorted_by_cnts['normal_volumn']):
    #     ax.text(v + 2, i, str("{0:.0%}".format(df_sorted_by_cnts['normal_rate'].values[i])), color='k', fontweight='bold')

    # if add_predictable:
    ax.barh(df_sorted_by_normal_cost['lab_description'], df_sorted_by_normal_cost['truepo_cost'],
            color='blue', alpha=1, label='Avoidable cost')  # 'True Positive@0.95 train_PPV'
    for i, v in enumerate(df_sorted_by_normal_cost['truepo_cost']):
        ax.text(v, i, str("{0:.1%}".format((df_sorted_by_normal_cost['true_positive_fraction']/df_sorted_by_normal_cost['normal_rate']).values[i])), color='k',
                fontweight='bold')

    # plt.xlim([0,1])
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)

    plt.legend()
    plt.xlabel('Cost per patient encounter', fontsize=14) # 'Total Amount (in %s) in 2014.07-2017.06, targeting PPV=%.2f'%(unit, targeted_PPV)
    # plt.xticks([0,0.5,1,1.5])

    plt.tight_layout()
    plt.savefig(fig_path)

    plt.show()







######################################
'''
refactoring
'''

def draw__Confusion_Metrics(statsByLab_folderpath, labs=all_labs,
                            targeted_PPV=0.95, scale_by=None, use_cached_fig_data=False):
    '''
    Drawing Figure 3 in the main text.

    :return:
    '''
    # df = pd.read_csv('data_performance_stats/best-alg-%s-summary-fix-trainPPV.csv' % lab_type,
    #                  keep_default_na=False)
    labs_stats_filepath = os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')

    df = pd.read_csv(labs_stats_filepath)

    df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]


    cached_foldername = 'Fig3_Confusion_Metrics/'
    cached_folderpath = os.path.join(os.path.join(statsByLab_folderpath, cached_foldername))

    cached_tablename = 'Confusion_Metrics_%ss_PPV_%.2f.csv'%(lab_type, targeted_PPV)
    cached_tablepath = os.path.join(cached_folderpath, cached_tablename)

    cached_figurename = 'Confusion_Metrics_%ss_PPV_%.2f_ind.png'%(lab_type, targeted_PPV)
    cached_figurepath = os.path.join(cached_folderpath, cached_figurename)

    if not os.path.exists(cached_folderpath):
        os.mkdir(cached_folderpath)

    if os.path.exists(cached_tablepath) and use_cached_fig_data:
        # lab2stats = pickle.load(open(cached_result_path, 'r'))
        df_toplots = pd.read_csv(cached_tablepath, keep_default_na=False)
        print df_toplots

    else:

        # labs_and_cnts = stats_utils.get_top_labs_and_cnts(lab_type)

        # labs_and_cnts.append(['LABCBCD', stats_utils.query_lab_cnt(lab='LABCBCD',
        #                                                            time_limit=['2014-01-01', '2016-12-31'])])

        df = df[df['lab'].isin(labs)]

        if lab_type == 'panel' or lab_type == 'component':
            # Stanford data, scaled by vol
            df['total_vol'] =                            df['2014 2stHalf count'] + \
                                df['2015 1stHalf count'] + df['2015 2stHalf count'] + \
                                df['2016 1stHalf count'] + df['2016 2stHalf count'] + \
                                df['2017 1stHalf count']
        else:
            df['total_vol'] = 1

        # TODO: use fractions in the original file!
        df['all_instance'] = df['true_positive'] + df['false_positive'] + df['true_negative'] + df['false_negative']

        for cnt_type in ['true_positive', 'false_positive', 'true_negative', 'false_negative']:
            df[cnt_type] = df[cnt_type]/df['all_instance']


        df['all_positive'] = df['true_positive'] + df['false_positive']
        df['all_negative'] = df['true_negative'] + df['false_negative']

        df['true_negative'] = -df['true_negative']
        df['all_negative'] = -df['all_negative']

        # df['count'] = df['count'].apply(lambda x: float(x) if x != '' else 0)

        # if lab_type == 'component':
        #     df['count'] = df['count'].apply(lambda x: x / 1000000)

        # print df[['true_positive', 'all_positive',
        #           'true_negative', 'all_negative']].head(5).plot(kind='barh')

        df_toshow = df.copy()
        df_toshow['lab'] = df_toshow['lab'].apply(lambda x:lab_descriptions[x])
        df_toshow['true_negative'] = -df_toshow['true_negative']
        df_toshow = df_toshow.rename(columns={'true_positive':'TP',
                                              'false_positive':'FP',
                                              'true_negative':'TN',
                                              'false_negative':'FN',
                                              'sensitivity':'sens',
                                              'specificity':'spec',
                                              'LR_p':'LR+', 'LR_n':'LR-'})
        df_toshow.sort_values('total_vol', ascending=False)[['lab', 'TP', 'FP', 'TN', 'FN', 'sens', 'spec', 'LR+', 'LR-']]\
            .to_csv(cached_tablepath.replace('.csv','_toshow.csv'), index=False, float_format='%.2f')

        df_toplots = df

        df['all_positive_vol'] = df['all_positive'] * df['total_vol']
        df['true_positive_vol'] = df['true_positive'] * df['total_vol']
        df['all_negative_vol'] = df['all_negative'] * df['total_vol']
        df['true_negative_vol'] = df['true_negative'] * df['total_vol']

        df_toplots[['lab',
                    'PPV', 'NPV', 'sensitivity', 'specificity', 'LR_p', 'LR_n',
                    'total_vol',
                   'all_positive_vol', 'true_positive_vol', 'all_negative_vol', 'true_negative_vol']]\
                    .sort_values('total_vol', ascending=False)\
                    .to_csv(cached_tablepath, index=False, float_format='%.2f')


    if not scale_by:
        scale = 1.
    elif scale_by=='pat':
        scale = float(stats_utils.NUM_DISTINCT_PATS)
    elif scale_by == 'enc':
        scale = float(stats_utils.NUM_DISTINCT_ENCS)

    df_toplots = df_toplots.sort_values(['total_vol'], ascending=True)

    for ind, df_toplot in enumerate([df_toplots.tail(38), df_toplots.head(38)]):

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh(df_toplot['lab'], df_toplot['all_positive_vol']/scale, color='orange', alpha=0.5, label='False Positive')
        ax.barh(df_toplot['lab'], df_toplot['true_positive_vol']/scale, color='blue', alpha=1, label='True Positive')

        ax.barh(df_toplot['lab'], df_toplot['all_negative_vol']/scale, color='blue', alpha=0.5, label='False Negative')
        ax.barh(df_toplot['lab'], df_toplot['true_negative_vol']/scale, color='orange', alpha=1, label='True Negative')

        for i, v in enumerate(df_toplot['all_positive_vol']/scale):
            ax.text(v, i, lab_descriptions[df_toplot['lab'].values[i]], color='k')

        plt.yticks([])

        plt.xlim([-2.5, 3])

        plt.legend(loc=[0.1,0.1])
        plt.xlabel('Number of orders per encounter, targeting at PPV=%.2f'%targeted_PPV, fontsize=14)
        #plt.ylabel('Labs', fontsize=14)

        plt.tight_layout()

        plt.savefig(cached_figurepath.replace('ind', 'ind_%i'%ind))

        plt.show()

'''
refactoring
'''
######################################

######################################
'''
refactored
'''

def draw__Order_Intensities(stats_folderpath, labs=['LABCBCD', 'LABMETB']+all_labs, scale_by=None,  use_cached_fig_data=True):
    '''
    Drawing Figure 2 in the main text.

    :param lab_type:
    :return:
    '''

    '''
    Get labs
    '''
    print "Labs to be plot:", labs

    cached_result_foldername = os.path.join(stats_folderpath, 'Fig2_Order_Intensities/')
    if not os.path.exists(cached_result_foldername):
        os.mkdir(cached_result_foldername)
    cached_result_filename = 'Order_Intensities_%s.csv'%lab_type
    cached_result_path = os.path.join(cached_result_foldername, cached_result_filename)

    '''
    Each lab 
        -> all its orders in 2014/07-2017/06 (implicit) 
        -> {time since last order:cnts} (cached)
        -> {0-1 days: cnt, 1-3 days: ...} 
        -> barh
    '''
    lab2stats = {}
    columns = ['< 1 day', '1-3 days', '3-7 days', '> 7 days']

    if os.path.exists(cached_result_path) and use_cached_fig_data:
        # lab2stats = pickle.load(open(cached_result_path, 'r'))
        lab2stats_pd = pd.read_csv(cached_result_path)
        lab2stats = lab2stats_pd.set_index('lab').to_dict(orient='index')

    else:
        for lab in labs: #all_labs[:10][::-1]:
            print 'Getting Order Intensities of lab %s..'%lab

            df_lab = stats_utils.get_queried_lab(lab, time_limit=DEFAULT_TIMELIMIT)

            dict_lab = stats_utils.get_time_since_last_order_cnts(lab, df_lab)

            # df_lab = pd.DataFrame.from_dict(dict_lab, orient='index').reset_index().rename(columns={'index': 'lab'})
            # df_lab.to_csv(cached_result_foldername + '%s.csv'%lab, index=False)

            sums = [dict_lab[0], sum(dict_lab[x] for x in range(1, 4)), sum(dict_lab[x] for x in range(4, 8))]
            sums.append(sum(dict_lab[x] for x in dict_lab.keys()) - sum(sums))

            time_since_last_order_binned = {columns[_]: sums[_] for _ in range(len(columns))}

            lab2stats[lab] = time_since_last_order_binned

        # pickle.dump(lab2stats, open(cached_result_path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

        df_res = pd.DataFrame.from_dict(lab2stats, orient='index').reset_index().rename(columns={'index':'lab'})

        df_res.to_csv(cached_result_path, index=False)


    def plot_order_intensities_barh(lab, time_since_last_order_binned, columns, labeling=True):
        pre_sum = 0
        alphas = [1, 0.5, 0.3, 0.2]
        for i, key in enumerate(columns):

            pre_sum += time_since_last_order_binned[key]
            if not scale_by:
                cur_cnt = pre_sum
            elif scale_by == 'pat':
                cur_cnt = float(pre_sum)/stats_utils.NUM_DISTINCT_PATS
            elif scale_by == 'enc':
                cur_cnt = float(pre_sum)/stats_utils.NUM_DISTINCT_ENCS

            lab_desciption = lab_descriptions[lab]

            if labeling:
                plt.barh([lab_desciption], cur_cnt, color='b', alpha=alphas[i], label=key)
            else:
                plt.barh([lab_desciption], cur_cnt, color='b', alpha=alphas[i])

    labs_ordered = sorted(labs, key=lambda x: sum(lab2stats[x].values()), reverse=True)
    fig = plt.figure(figsize=(12, 8)) # figsize=(20, 12)

    labs_toplots = [labs_ordered]
    # labs_toplots = [lab_ordered[:39], lab_ordered[39:]]

    for ind_toplot, labs_toplot in enumerate(labs_toplots):
        for i, lab in enumerate(labs_toplot[::-1]):

            time_since_last_order_binned = lab2stats[lab]

            if i == 0:
                plot_order_intensities_barh(lab, time_since_last_order_binned, columns=columns, labeling=True)
            else:
                plot_order_intensities_barh(lab, time_since_last_order_binned, columns=columns, labeling=False)

        plt.legend()
        plt.xlabel('Number of orders per patient encounter', fontsize=14) #'Order number between 2014/07-2017/06'

        plt.tight_layout()
        plt.savefig(cached_result_foldername + 'Order_Intensities_%s_%i.png'%(lab_type,ind_toplot))
        plt.clf()

def draw__stats_Curves(statsByLab_folderpath, labs=all_labs, curve_type="ROC", algs=['random-forest']):
    num_labs = len(labs)
    row, col, i_s, j_s = stats_utils.prepare_subfigs(num_labs, col=4)

    scores_base = []
    scores_best = []
    fig, ax = plt.subplots(figsize=(12, 6))

    for ind, lab in enumerate(labs):

        xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best \
            = stats_utils.get_curve_onelab(lab,
                                           all_algs=algs,
                                           data_folder=statsByLab_folderpath.replace("lab_statistics", "machine_learning"),
                                           curve_type=curve_type)
        scores_base.append(score_base)
        scores_best.append(score_best)

        i, j = i_s[ind], j_s[ind]
        plt.subplot2grid((row, col), (i, j))

        plt.plot(xVal_base, yVal_base, label='%0.2f' % (score_base))
        plt.plot(xVal_best, yVal_best, label='%0.2f' % (score_best))
        plt.xticks([])
        plt.yticks([])
        plt.xlabel(lab_descriptions[lab])
        plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(statsByLab_folderpath, '%s_%s.png'%(lab_type, curve_type)))

    avg_base, avg_best = np.mean(scores_base), np.mean(scores_best)
    print "Average %s among %i labs: %.3f baseline, %.3f bestalg (an improvement of %.3f)."\
          %(curve_type, len(scores_base), avg_base, avg_best, avg_best-avg_base)



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
        print df_twomethods
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


def plot_cartoons():
    try:
        df = pd.read_csv('RF_important_features_%ss.csv'%lab_type, keep_default_na=False)
    except:
        write_importantFeatures(lab_type)
    # labs = df.sort_values('score 1', ascending=False)['lab'].values.tolist()[:15]
    # print labs


    # lab = 'WBC'
    alg = 'random-forest'



    labs = all_labs

    col = 5
    row = len(labs)/col
    has_left_labs = (len(labs)%col!=0)

    fig_width, fig_heights = col * 3., 24. / col
    plt.figure(figsize=(fig_width, fig_heights))

    for i in range(row):
        for j in range(col):
            ind = i * col + j
            lab = labs[ind]

            df = pd.read_csv(data_folder + "%s/%s/%s-normality-prediction-%s-direct-compare-results.csv"
                             % (lab, alg, lab, alg), keep_default_na=False)
            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            df1 = pd.read_csv(data_folder + "%s/%s/%s-normality-prediction-%s-report.tab"
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
            plt.xlabel(lab + ', auroc=%.2f'%auc)
            # plt.legend(lab)

    # plt.xlabel("%s score for %s"%(alg,lab))
    # plt.ylabel("num episodes, auroc=%f"%auc)
    # plt.legend()
    if has_left_labs:
        i = row
        for j in range(len(labs)%col):
            ind = i * col + j
            lab = labs[ind]

            df = pd.read_csv(data_folder + "%s/%s/%s-normality-prediction-%s-direct-compare-results.csv"
                             % (lab, alg, lab, alg), keep_default_na=False)
            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            df1 = pd.read_csv(data_folder + "%s/%s/%s-normality-prediction-%s-report.tab"
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
            plt.xlabel(lab)
    plt.show()

    plt.savefig('cartoons_%ss.png'%lab_type)


def write_importantFeatures(lab_type="component"):
    all_rows = []
    num_rf_best = 0

    if lab_type == 'component':
        all_labs = STRIDE_COMPONENT_TESTS
    elif lab_type == 'panel':
        all_labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
    elif lab_type == 'UMich':
        all_labs = UMICH_TOP_COMPONENTS

    for lab in all_labs: #TODO
        df = pd.read_csv(
            '../machine_learning/data-UMichs-10000-episodes/%s/%s-normality-prediction-report.tab'
            %(lab,lab), sep='\t', skiprows=1, keep_default_na=False)

        best_row = df['roc_auc'].values.argmax()
        if best_row == 2:
            num_rf_best += 1

        best_row = 2#df['roc_auc'].values.argmax()
        best_model = df.ix[best_row, 'model']
        best_model_split = best_model.split(',')

        #best_alg = best_model_split[0][:best_model_split[0].find('(')]
        top_1_feature = best_model_split[1][best_model_split[1].find('[')+1:].strip()
        featu1, score1 = stats_utils.split_features(top_1_feature)

        top_2_feature = best_model_split[2].strip()
        featu2, score2 = stats_utils.split_features(top_2_feature)

        top_3_feature = best_model_split[3].strip()
        featu3, score3 = stats_utils.split_features(top_3_feature)

        curr_row = [lab, featu1, score1, featu2, score2, featu3, score3]

        all_rows.append(curr_row)

    print "Total number of labs:", len(all_rows), "num of RF best:", (num_rf_best)

    result_df = pd.DataFrame(all_rows, columns=['lab', 'feature 1', 'score 1', 'feature 2', 'score 2','feature 3', 'score 3'])
    result_df.to_csv('RF_important_features_%ss.csv'%lab_type, index=False)

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



def get_best_calibrated_labs(statsByLab_folderpath, top_k=20):
    df_fix_train = pd.read_csv(statsByLab_folderpath + "/summary-stats-bestalg-fixTrainPPV.csv",
                               keep_default_na=False)
    df_fix_train['abs_PPV_diff'] = (df_fix_train['targeted_PPV_fixTrainPPV'] - df_fix_train['PPV'].apply(
        lambda x: float(x) if x != '' else float('nan'))).abs()

    lab_diff = {}
    for lab in all_labs:
        cur_tot_diff = df_fix_train[df_fix_train['lab']==lab]['abs_PPV_diff'].values.sum()
        lab_diff[lab] = cur_tot_diff

    best_labs = [x[0] for x in sorted(lab_diff.iteritems(), key=lambda (k,v):v)[:top_k]]
    print best_labs
    # for lab in best_labs:
    #     print df_fix_train[df_fix_train['lab']==lab][['lab', 'targeted_PPV_fixTrainPPV', 'PPV']].to_string(index=False)
    df_res = df_fix_train[df_fix_train['lab'].isin(best_labs)][['lab', 'targeted_PPV_fixTrainPPV', 'PPV', 'abs_PPV_diff']]#.sort_values(['lab','targeted_PPV_fixTrainPPV'])
    df_res_long = df_res.pivot(index='lab', columns='targeted_PPV_fixTrainPPV', values='PPV').reset_index()
    # print df_res_long
    df_res_long['abs_PPV_diff'] = df_res_long['lab'].map(lab_diff)
    df_res_long = df_res_long.rename(columns={0.80:'target 0.80', 0.90:'target 0.90', 0.95:'target 0.95', 0.99:'target 0.99'})
    df_res_long.sort_values('abs_PPV_diff').drop(columns=['abs_PPV_diff']).to_csv(statsByLab_folderpath+'/best_calibrated.csv', index=False)

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
    df.to_csv(statsByLab_folderpath + "/predict_power_%ss.csv"%lab_type, index=False)


def test(lab):
    # data_file = pd.read_csv('stats_useful_data/' + '%s_Usage_2014-2016.csv' % lab)
    # print data_file['pat_id'].values[:10]
    # print len(list(set(data_file['pat_id'].values.tolist())))

    results = stats_utils.query_lab_usage__df(lab=lab,
                                              lab_type='panel',
                                              time_start='2014-01-01',
                                              time_end='2016-12-31')
    df = pd.DataFrame(results, columns=['pat_id', 'order_time', 'result'])

    prevday_cnts_dict = stats_utils.get_prevday_cnts__dict(df)

def draw__Comparing_PPVs(statsByLab_folderpath, include_labnames=False):
    summary_filename = 'summary-stats-bestalg-fixTrainPPV.csv'
    summary_filepath = os.path.join(statsByLab_folderpath, summary_filename)
    df = pd.read_csv(summary_filepath, keep_default_na=False)
    print df.shape
    df = df[['lab','targeted_PPV_fixTrainPPV','PPV']]
    df = df[df['PPV']!='']

    result_foldername = 'Fig3_Comparing_PPVs/'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)

    result_figurename = 'Comparing_PPVs.png'
    result_figurepath = os.path.join(result_folderpath, result_figurename)
    labs = df['lab'].values.tolist()

    print df['targeted_PPV_fixTrainPPV'].values.tolist()
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

    import adjust_text

    # adjust_text.adjust_text(texts)

    plt.savefig(result_figurepath)

def comparing_components(stats_folderpath, target_PPV=0.95):
    stats_filename = 'summary-stats-bestalg-fixTrainPPV.csv'

    labs_important = stats_utils.get_important_labs(lab_type='component')

    stanford_filepath = os.path.join(stats_folderpath, 'data-component-10000-episodes', stats_filename)
    umich_filepath = os.path.join(stats_folderpath, 'data-UMich-10000-episodes', stats_filename)
    ucsf_filepath = os.path.join(stats_folderpath, 'data-UCSF-10000-episodes', stats_filename)

    df_stanford = pd.read_csv(stanford_filepath, keep_default_na=False)
    labs_stanford = set(df_stanford['lab'].values.tolist())
    df_stanford = df_stanford[df_stanford['targeted_PPV_fixTrainPPV']==target_PPV]

    df_umich = pd.read_csv(umich_filepath, keep_default_na=False)
    labs_umich = set(df_umich['lab'].values.tolist())
    df_umich = df_umich[df_umich['targeted_PPV_fixTrainPPV'] == target_PPV]

    df_ucsf = pd.read_csv(ucsf_filepath, keep_default_na=False)
    labs_ucsf = set(df_ucsf['lab'].values.tolist())
    df_ucsf = df_ucsf[df_ucsf['targeted_PPV_fixTrainPPV'] == target_PPV]

    print labs_stanford
    print labs_umich
    print labs_ucsf

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


    umich_replace = {'SOD':'NA', 'POT':'K', 'CREAT': 'CR'}
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

    ucsf_replace = {'NAWB': 'NA', 'CREAT': 'CR'}
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
    merged_df.to_csv(os.path.join(stats_folderpath, 'components_comparisons.csv'), index=False)



if __name__ == '__main__':

    figs_to_plot = ['Potential_Savings']

    possible_labtypes = ['panel', 'component', 'UMich', 'UCSF']

    stats_folderpath = os.path.join(stats_utils.main_folder, 'lab_statistics/')

    import LocalEnv
    statsByDataSet_foldername = 'data-%s-10000-episodes'%lab_type #'results-from-panels-10000-to-panels-5000-part-1_medicare/'
    statsByDataSet_folderpath = os.path.join(stats_folderpath, statsByDataSet_foldername)

    labs_guideline_nested = stats_utils.get_guideline_maxorderfreq().values()
    labs_guideline = [lab for sublist in labs_guideline_nested for lab in sublist]

    labs_common_panels = ['LABMETB', 'LABCBCD']

    if 'Comparing_Components' in figs_to_plot:
        comparing_components(stats_folderpath)

    if 'Order_Intensities' in figs_to_plot:

        labs = list(set(labs_common_panels + labs_guideline + stats_utils.get_important_labs()))

        draw__Order_Intensities(statsByDataSet_folderpath, labs=labs, scale_by='enc', use_cached_fig_data=True)

    if 'Normality_Saturations' in figs_to_plot:
        labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels) - set(['LABTSH', 'LABLDH']))

        draw__Normality_Saturations(statsByDataSet_folderpath, labs=labs, use_cached_fig_data=True)

    if 'PPV_distribution' in figs_to_plot:
        PPV_guideline(statsByDataSet_folderpath) #TODO
        get_best_calibrated_labs(statsByDataSet_folderpath)

    if 'Savable_Fractions' in figs_to_plot:
        draw__Comparing_Savable_Fractions(statsByDataSet_folderpath, target_PPV=0.95, use_cache=True)

    if 'Comparing_PPVs' in figs_to_plot:
        draw__Comparing_PPVs(statsByDataSet_folderpath)

    if 'ROC' in figs_to_plot:
        labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels))
        draw__stats_Curves(statsByDataSet_folderpath, labs, curve_type="ROC", algs=['random-forest'])

    if 'PRC' in figs_to_plot:
        labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels))
        draw__stats_Curves(statsByDataSet_folderpath, all_labs, curve_type="PRC", algs=['random-forest'])

    if 'Confusion_Metrics' in figs_to_plot:
        labs = list(set(labs_guideline + stats_utils.get_important_labs()) - set(labs_common_panels))
        draw__Confusion_Metrics(statsByDataSet_folderpath, labs=labs,
            targeted_PPV=0.95, scale_by='enc', use_cached_fig_data=False)

    if 'Potential_Savings' in figs_to_plot:
        draw__Potential_Savings(statsByDataSet_folderpath, scale_by='enc', targeted_PPV=0.95, use_cached_fig_data=False)

