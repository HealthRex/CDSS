
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
lab_desciptions = stats_utils.get_lab_descriptions()




def draw__Normality_Saturations(stats_folderpath, max_repeat = 5, use_cached_fig_data=True):
    '''
    Drawing Figure 1 in the main text.

    :return:
    '''

    labs = ['LABMETB', 'LABCBCD'] + all_labs #

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

    for ind, labs_to_plot in enumerate(labs_to_plots):
        for lab in labs_to_plot:  # :

            non_empty_inds = []
            for i in range(0,max_repeat+1):
                if lab2frac[lab][i]=='':
                    break
                non_empty_inds.append(i)
            y_s = [float(lab2frac[lab][i]) for i in non_empty_inds]
            print lab, y_s
            plt.plot(non_empty_inds, y_s, label=lab_desciptions[lab])
            plt.scatter(non_empty_inds, y_s)


        plt.xticks(range(0, max_repeat + 1))
        plt.xlabel('Number of Consecutive Normalities in a Week')
        plt.ylabel('Normal Rate')
        # plt.ylim([0, 1])
        plt.legend()
        plt.tight_layout()
        plt.savefig(cached_result_foldername + 'Normality_Saturations_%s_%i'%(lab_type, ind))
        plt.clf()


def draw__Potential_Savings(statsByLab_folderpath, wanted_PPV=0.95, use_cached_fig_data=False):
    '''
    Drawing Figure 4 in the main text.

    :return:
    '''

    df = pd.read_csv(os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv'),
                     keep_default_na=False)
    print df.head()
    df = df[df['targeted_PPV_fixTrainPPV'] == wanted_PPV]

    # labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=50)
    df = df[df['lab'].isin(all_labs)] #[x[0] for x in labs_and_cnts]

    result_foldername = 'Fig4_Potential_Savings/'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)

    '''
    Hierarchy:
    
    '''

    fig_filename = 'Potential_Savings_PPV_%.2f.png'%wanted_PPV
    fig_path = os.path.join(result_folderpath, fig_filename)
    data_filename = 'Potential_Savings_%.2f.csv'%wanted_PPV
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


    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df_sorted_by_normal_cost['lab'], df_sorted_by_normal_cost['normal_cost'],
            color='blue', alpha=0.5, label='Normal lab cost')
    # for i, v in enumerate(df_sorted_by_cnts['normal_volumn']):
    #     ax.text(v + 2, i, str("{0:.0%}".format(df_sorted_by_cnts['normal_rate'].values[i])), color='k', fontweight='bold')

    # if add_predictable:
    ax.barh(df_sorted_by_normal_cost['lab'], df_sorted_by_normal_cost['truepo_cost'],
            color='blue', alpha=1, label='True positive saving')  # 'True Positive@0.95 train_PPV'
    for i, v in enumerate(df_sorted_by_normal_cost['truepo_cost']):
        ax.text(v, i, str("{0:.1%}".format((df_sorted_by_normal_cost['true_positive_fraction']/df_sorted_by_normal_cost['normal_rate']).values[i])), color='k',
                fontweight='bold')

    # plt.xlim([0,1])
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)

    plt.legend()
    plt.xlabel('Total Cnt in 2014.07-2017.06, targeting PPV=%.2f'%wanted_PPV) # (in millions)

    plt.savefig(fig_path)

    plt.show()







######################################
'''
refactoring
'''

def draw__Confusion_Metrics(statsByLab_folderpath, wanted_PPV=0.95, use_cached_fig_data=False):
    '''
    Drawing Figure 3 in the main text.

    :return:
    '''
    # df = pd.read_csv('data_performance_stats/best-alg-%s-summary-fix-trainPPV.csv' % lab_type,
    #                  keep_default_na=False)
    labs_stats_filepath = os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')

    df = pd.read_csv(labs_stats_filepath)

    df = df[df['targeted_PPV_fixTrainPPV'] == wanted_PPV]


    cached_foldername = 'Fig3_Confusion_Metrics/'
    cached_folderpath = os.path.join(os.path.join(statsByLab_folderpath, cached_foldername))

    cached_tablename = 'Confusion_Metrics_%ss_PPV_%.2f.csv'%(lab_type, wanted_PPV)
    cached_tablepath = os.path.join(cached_folderpath, cached_tablename)

    cached_figurename = 'Confusion_Metrics_%ss_PPV_%.2f_ind.png'%(lab_type, wanted_PPV)
    cached_figurepath = os.path.join(cached_folderpath, cached_figurename)

    if not os.path.exists(cached_folderpath):
        os.mkdir(cached_folderpath)

    if os.path.exists(cached_tablepath) and use_cached_fig_data:
        # lab2stats = pickle.load(open(cached_result_path, 'r'))
        df_toplots = pd.read_csv(cached_tablepath, keep_default_na=False)

    else:

        # labs_and_cnts = stats_utils.get_top_labs_and_cnts(lab_type)

        # labs_and_cnts.append(['LABCBCD', stats_utils.query_lab_cnt(lab='LABCBCD',
        #                                                            time_limit=['2014-01-01', '2016-12-31'])])

        labs = all_labs

        df = df[df['lab'].isin(labs)]

        if lab_type == 'panel' or lab_type == 'component':
            # Stanford data, scaled by vol
            df['total_count'] =                            df['2014 2stHalf count'] + \
                                df['2015 1stHalf count'] + df['2015 2stHalf count'] + \
                                df['2016 1stHalf count'] + df['2016 2stHalf count'] + \
                                df['2017 1stHalf count']
        else:
            df['total_count'] = 1

        # TODO: use fractions in the original file!
        df['all_instance'] = df['true_positive'] + df['false_positive'] + df['true_negative'] + df['false_negative']

        df['all_positive'] = df['true_positive'] + df['false_positive']
        df['all_negative'] = df['true_negative'] + df['false_negative']

        df['true_negative'] = -df['true_negative']
        df['all_negative'] = -df['all_negative']

        # df['count'] = df['count'].apply(lambda x: float(x) if x != '' else 0)

        # if lab_type == 'component':
        #     df['count'] = df['count'].apply(lambda x: x / 1000000)

        # print df[['true_positive', 'all_positive',
        #           'true_negative', 'all_negative']].head(5).plot(kind='barh')

        df_toplots = df

        df['all_positive'] *= df['total_count']/df['all_instance']
        df['true_positive'] *= df['total_count']/df['all_instance']
        df['all_negative'] *= df['total_count']/df['all_instance']
        df['true_negative'] *= df['total_count']/df['all_instance']

        df_toplots[['lab', 'total_count',
                   'PPV', 'NPV', 'sensitivity', 'specificity', 'LR_p', 'LR_n',
                   'all_positive', 'true_positive', 'all_negative', 'true_negative']]\
                    .sort_values('total_count', ascending=False)\
                    .to_csv(cached_tablepath, index=False, float_format='%.2f')

    df_toplots = df_toplots.sort_values(['total_count'], ascending=True)

    for ind, df_toplot in enumerate([df_toplots.tail(38), df_toplots.head(38)]):

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.barh(df_toplot['lab'], df_toplot['all_positive'], color='orange', alpha=0.5, label='False Positive')
        ax.barh(df_toplot['lab'], df_toplot['true_positive'], color='blue', alpha=1, label='True Positive')

        ax.barh(df_toplot['lab'], df_toplot['all_negative'], color='blue', alpha=0.5, label='False Negative')
        ax.barh(df_toplot['lab'], df_toplot['true_negative'], color='orange', alpha=1, label='True Negative')

        for i, v in enumerate(df_toplot['all_positive']):
            ax.text(v, i, lab_desciptions[df_toplot['lab'].values[i]], color='k')

        plt.yticks([])

        # plt.xlim([-6*10**9, 2*10**9])

        plt.legend(loc=[0.1,0.1])
        plt.xlabel('total lab cnt in 2014-2017 when fixing train PPV=%.2f'%wanted_PPV)
        plt.ylabel('labs')

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

def draw__Order_Intensities(stats_folderpath, use_cached_fig_data=True):
    '''
    Drawing Figure 2 in the main text.

    :param lab_type:
    :return:
    '''

    '''
    Get labs
    '''
    labs = ['LABCBCD', 'LABMETB'] + all_labs #get_important_labs()
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

            lab_desciption = lab_desciptions[lab]

            if labeling:
                plt.barh([lab_desciption], pre_sum, color='b', alpha=alphas[i], label=key)
            else:
                plt.barh([lab_desciption], pre_sum, color='b', alpha=alphas[i])


    lab_ordered = sorted(labs, key=lambda x:lab2stats[x]['< 1 day'], reverse=True)
    fig = plt.figure(figsize=(20, 12)) #

    labs_toplots = [lab_ordered[:39], lab_ordered[39:]]

    for ind_toplot, labs_toplot in enumerate(labs_toplots):
        for i, lab in enumerate(labs_toplot[::-1]):

            time_since_last_order_binned = lab2stats[lab]

            if i == 0:
                plot_order_intensities_barh(lab, time_since_last_order_binned, columns=columns, labeling=True)
            else:
                plot_order_intensities_barh(lab, time_since_last_order_binned, columns=columns, labeling=False)

        plt.legend(loc=(.9,.1))
        plt.xlabel('Order number between 2014/07-2017/06')

        plt.tight_layout()
        plt.savefig(cached_result_foldername + 'Order_Intensities_%s_%i.png'%(lab_type,ind_toplot))
        plt.clf()

def draw__stats_Curves(statsByLab_folderpath, curve_type="roc", algs=['random-forest']):
    num_labs = len(all_labs)
    row, col, i_s, j_s = prepare_subfigs(num_labs)

    scores_base = []
    scores_best = []
    for ind, lab in enumerate(all_labs):

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
        plt.xlabel(lab)
        plt.legend()
    plt.savefig(statsByLab_folderpath+'%s_%s.png'%(lab_type, curve_type))

    avg_base, avg_best = np.mean(scores_base), np.mean(scores_best)
    print "Average %s among %i labs: %.3f baseline, %.3f bestalg (an improvement of %.3f)."\
          %(curve_type, len(scores_base), avg_base, avg_best, avg_best-avg_base)



def get_prevday2normalities(lab, mlByLab_folder, time_limit=DEFAULT_TIMELIMIT, source='full'):
    '''
    Why: Plot figure

    What: How consecutive normality indicates the next normality?

    How:

    Args:
        lab:
        time_limit:

    Returns:

    '''

    if source == 'full':
        df_lab = stats_utils.query_to_dataframe(lab, time_limit=time_limit)
        df_lab = df_lab[df_lab['order_status']=='Completed'].reset_index(drop=True)

    else:
        import LocalEnv
        from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

        print "processing %s..."%lab
        # data_folder = LocalEnv.PATH_TO_CDSS + '/scripts/LabTestAnalysis/machine_learning/data-panels/%s/' % lab
        '''
        First, obtain test patients
        '''
        data_processed_filename = '%s-normality-%s-matrix-processed.tab' % (lab, source)
        data_processed_pathname = os.path.join(mlByLab_folder, lab, data_processed_filename)

        fm_io = FeatureMatrixIO()
        df_processed_test_lab = fm_io.read_file_to_data_frame(data_processed_pathname)
        # print df_processed_test_lab.head()
        # quit()
        pat_ids_test = set(df_processed_test_lab['pat_id'].values.tolist())


        '''
        Then, obtain
        '''

        data_raw_filename = '%s-normality-matrix-raw.tab' % lab
        data_raw_pathname = os.path.join(mlByLab_folder, lab, data_raw_filename)

        df_raw = fm_io.read_file_to_data_frame(data_raw_pathname)
        df_lab = df_raw[df_raw['pat_id'].isin(pat_ids_test)]
        df_lab['abnormal_yn'] = df_lab['abnormal_panel'].apply(lambda x: 'Y' if x==1 else 'N')
        df_lab = df_lab[['pat_id', 'order_time', 'abnormal_yn']]

    day2norms = stats_utils.get_prevweek_normal__dict(df_lab, also_get_cnt=True)

    return day2norms.keys(), day2norms.values()



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

    result_tablename = 'Comparing_Savable_Fractions_PPV_%.csv'
    result_tablepath = os.path.join(result_folderpath, result_tablename)

    result_figname = 'Comparing_Savable_Fractions_PPV_%.2f.png'%target_PPV
    result_figpath = os.path.join(result_folderpath, result_figname)

    if use_cache and os.path.exists(result_tablepath):
        df_twomethods = pd.read_csv(result_tablepath, keep_default_na=False)
        print df_twomethods
        savable_fractions_simple = pandas2dict(df_twomethods, key='lab', val='savable_fraction_simple')
        savable_fractions_mlmodel = pandas2dict(df_twomethods, key='lab', val='savable_fraction_mlmodel')
        print savable_fractions_simple, savable_fractions_mlmodel
    else:


        # labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=76)
        # labs = [x[0] for x in labs_and_cnts]
        labs = all_labs
        # labs = ['LABA1C', 'LABLAC']

        '''
        Baseline 1: consecutive normalites in the last week
        
        The simple rule is: As long as the number of consecutive normalites
        reaches a threshold, then do not order; otherwise, go ahead and order. 
        Advantage: Provides a way to assign conservativeness
        Disadvantage: Too stringent, very few patients will qualify; in most cases have to order. 
        '''
        if True:
            savable_fractions_simple = {}
            mlByLab_folder = statsByLab_folderpath.replace("lab_statistics", "machine_learning")
            for lab in labs:
                processed_matrix_filename = '%s-normality-test-matrix-processed.tab' % lab
                processed_matrix_filepath = os.path.join(mlByLab_folder, processed_matrix_filename)

                days, normality_lists = get_prevday2normalities(lab, mlByLab_folder, source="train")
                normality_fractions = [float(sum(x)) / float(len(x)) for x in normality_lists]
                normality_cnts = [len(x) for x in normality_lists]

                '''
                Pick a threshold
                '''
                day_thres = float('inf')
                savable_cnt = 0
                for i, normality_fraction in enumerate(normality_fractions):
                    if normality_fraction > target_PPV:
                        day_thres = days[i]
                        break


                days, normality_lists = get_prevday2normalities(lab, mlByLab_folder, source="test")
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
                savable_fractions_simple[lab] = savable_fraction

                '''
                For the rule of "passing a number of days, then all set 'normal',
                the normal rate is equals to the PPV. "
                '''
                # import sys
                # day_thres = sys.maxint
                # savable_cnt = 0
                # for i, normality_fraction in enumerate(normality_fractions):
                #     if normality_fraction > target_PPV:
                #         day_thres = days[i]
                #
                #         '''
                #         Assumption: noramlity rate monotonically increases
                #         '''
                #         savable_cnt += normality_cnts[i]
                # savable_fraction = float(savable_cnt)/float(sum(normality_cnts))
                # savable_fractions_simple[lab] = savable_fraction

                # except Exception as e:
                #     print e
            df_simple = stats_utils.dict2pandas(savable_fractions_simple, key='lab', val='savable_fraction_simple')

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

        df_twomethods = df_simple.merge(df_mlmodel, on='lab', how='left')
        df_twomethods.to_csv(result_tablepath, index=False)

    plot_subfigs(savable_fractions_simple,
                 savable_fractions_mlmodel,
                 plot_type='bar',
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
    for wanted_PPV in [0.8, 0.90, 0.95, 0.99][::-1]: # TODO: what is the problem with 0.9? LABHIVWBL
        cur_row = [wanted_PPV]

        PPVs_from_train = df_fix_train.ix[df_fix_train['targeted_PPV_fixTrainPPV']==wanted_PPV, ['PPV']]
        cur_row.append(PPVs_from_train.shape[0]) # "Total number of labs:"

        PPVs_from_train = PPVs_from_train.dropna()['PPV'].values
        PPVs_from_train = np.array([float(x) for x in PPVs_from_train if x!='']) #TODO: why?
        vaild_PPV_num = PPVs_from_train.shape[0]
        cur_row.append(vaild_PPV_num) # "Valid number of labs:"

        print "When target at PPV %.2f, the mean PPV among %i labs is %.3f, std is %.3f"\
              %(wanted_PPV, vaild_PPV_num, np.mean(PPVs_from_train), np.std(PPVs_from_train))

        cur_cnt = sum(PPVs_from_train >= 0.99)
        cur_row.append(cur_cnt)

        for i in range(len(range_bins)-1):
            cur_cnt = sum((range_bins[i+1] <= PPVs_from_train) & (PPVs_from_train < range_bins[i]))
            cur_row.append(cur_cnt)

        rows.append(cur_row)

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


if __name__ == '__main__':

    figs_to_plot = ['Comparing_PPVs']

    possible_labtypes = ['panel', 'component', 'UMich', 'UCSF']

    stats_folderpath = os.path.join(stats_utils.main_folder, 'lab_statistics/')

    import LocalEnv
    statsByLab_foldername = 'data-%s-10000-episodes'%lab_type #'results-from-panels-10000-to-panels-5000-part-1_medicare/'
    statsByLab_folderpath = os.path.join(stats_folderpath, statsByLab_foldername)

    for lab_type in possible_labtypes:
        if lab_type in statsByLab_foldername:
            break

    if 'Order_Intensities' in figs_to_plot:
        draw__Order_Intensities(stats_folderpath, use_cached_fig_data=True)

    if 'Normality_Saturations' in figs_to_plot:
        draw__Normality_Saturations(stats_folderpath, use_cached_fig_data=True)

    if 'PPV_distribution' in figs_to_plot:
        PPV_guideline(statsByLab_folderpath) #TODO
        get_best_calibrated_labs(statsByLab_folderpath)

    if 'Savable_Fractions' in figs_to_plot:
        draw__Comparing_Savable_Fractions(statsByLab_folderpath, target_PPV=0.95, use_cache=False)

    if 'Comparing_PPVs' in figs_to_plot:
        draw__Comparing_PPVs(statsByLab_folderpath)

    if 'roc' in figs_to_plot:
        draw__stats_Curves(statsByLab_folderpath, curve_type="roc", algs=['random-forest'])

    if 'prc' in figs_to_plot:
        draw__stats_Curves(statsByLab_folderpath, curve_type="prc", algs=['random-forest'])

    if 'Confusion_Metrics' in figs_to_plot:

        draw__Confusion_Metrics(statsByLab_folderpath,
            wanted_PPV=0.95, use_cached_fig_data=False)

    if 'Potential_Savings' in figs_to_plot:
        draw__Potential_Savings(statsByLab_folderpath, wanted_PPV=0.95, use_cached_fig_data=False)

