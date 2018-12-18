
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
lab_folder = stats_utils.lab_folder
all_algs = stats_utils.all_algs

def plot_predict_twoside_bar(lab_type="panel", wanted_PPV=0.95):
    df = pd.read_csv('data_performance_stats/best-alg-%s-summary-trainPPV.csv' % lab_type,
                     keep_default_na=False)
    df = df[df['train_PPV']==wanted_PPV]

    df['all_positive'] = df['true_positive'] + df['false_positive']
    df['all_negative'] = df['true_negative'] + df['false_negative']

    df['true_negative'] = -df['true_negative']
    df['all_negative'] = -df['all_negative']

    df['count'] = df['count'].apply(lambda x:float(x) if x!='' else 0)
    if lab_type=='component':
        df['count'] = df['count'].apply(lambda x:x/1000000)

    df['all_positive'] *= df['count']
    df['true_positive'] *= df['count']
    df['all_negative'] *= df['count']
    df['true_negative'] *= df['count']
    # print df[['true_positive', 'all_positive',
    #           'true_negative', 'all_negative']].head(5).plot(kind='barh')

    df_toplot = df.head(10)
    df_toplot.head(10)[['lab', 'PPV', 'NPV', 'sensitivity', 'specificity', 'LR_p', 'LR_n']].to_csv('predict_panel_normal_sample.csv', index=False)

    df_toplot = df_toplot.sort_values('lab', ascending=False)
    fig, ax = plt.subplots()
    ax.barh(df_toplot['lab'], df_toplot['all_positive'], color='orange', alpha=0.5, label='False Positive')
    ax.barh(df_toplot['lab'], df_toplot['true_positive'], color='blue', alpha=1, label='True Positive')

    ax.barh(df_toplot['lab'], df_toplot['all_negative'], color='blue', alpha=0.5, label='False Negative')
    ax.barh(df_toplot['lab'], df_toplot['true_negative'], color='orange', alpha=1, label='True Negative')

    for i, v in enumerate(df_toplot['all_negative']):
        ax.text(-0.15, i, df_toplot['lab'].values[i], color='k')

    plt.yticks([])
    plt.legend()
    if lab_type=='panel':
        plt.xlabel('total lab cnt in 2014-2016')
    elif lab_type=='component':
        plt.xlabel('total lab cnt (in millions) in 2014-2016')
    plt.ylabel('labs')

    plt.show()


def plot_NormalRate__bar(lab_type="panel", wanted_PPV=0.95, add_predictable=False, look_cost=False):
    '''
    Horizontal bar chart for Popular labs.
    '''

    df = pd.read_csv('data_performance_stats/best-alg-%s-summary-fix-trainPPV.csv' % lab_type,
                     keep_default_na=False)
    df = df[df['train_PPV']==wanted_PPV]

    df = df[df['lab']!='LABNA'] # TODO: fix LABNA's price here

    df['normal_rate'] = (df['true_positive'] + df['false_negative']).round(5)

    # if lab_type == "component":
    #     df = df.rename(columns={'2016_Vol': 'count'})
    #     df = df.dropna()
    df['count'] = df['count'].apply(lambda x: 0 if x=='' else x)

    df['volumn'] = df['count'].apply(lambda x: float(x) / 1000000.) #
    volumn_label = 'Total Cnt (in millions) in 2016'

    if look_cost:
        df['volumn'] = df['volumn'] * df['mean_price'].apply(lambda x: float(x)) # cost
        volumn_label = 'Total cost in 2014-2016'

    '''
    Picking the top 20 popular labs.
    '''
    df_sorted_by_cnts = df.sort_values('volumn', ascending=False).ix[:,
                        ['lab', 'normal_rate', 'true_positive', 'volumn']].drop_duplicates().head(20).copy()
    df_sorted_by_cnts = df_sorted_by_cnts.sort_values('volumn', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['volumn'], color='grey', alpha=0.5,
            label=volumn_label)

    df_sorted_by_cnts['normal_volumn'] = df_sorted_by_cnts['normal_rate']*df_sorted_by_cnts['volumn']
    ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['normal_volumn'],
            color='blue', alpha=0.5, label='Normal lab cost')
    # for i, v in enumerate(df_sorted_by_cnts['normal_volumn']):
    #     ax.text(v + 2, i, str("{0:.0%}".format(df_sorted_by_cnts['normal_rate'].values[i])), color='k', fontweight='bold')

    df_sorted_by_cnts['truepo_volumn'] = df_sorted_by_cnts['true_positive']*df_sorted_by_cnts['volumn']
    if add_predictable:
        ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['truepo_volumn'],
                color='blue', alpha=0.9, label='True positive saving') #'True Positive@0.95 train_PPV'
        for i, v in enumerate(df_sorted_by_cnts['truepo_volumn']):
            ax.text(v, i, str("{0:.0%}".format(df_sorted_by_cnts['true_positive'].values[i])), color='k', fontweight='bold')


    # plt.xlim([0,1])
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)

    plt.legend()
    plt.show()

def get_waste_in_7days(lab_type='panel'):
    if lab_type == 'panel':
        all_labs = all_panels #stats_utils.get_top_labs(lab_type=lab_type, top_k=10)
    elif lab_type == 'component':
        all_labs = all_components

    res_df = pd.DataFrame()
    data_file_all = '%s_waste_in_7days.csv'%lab_type

    if not os.path.exists(data_file_all):

        import tmp

        for i, lab in enumerate(all_labs):
            data_file = '%s_Usage_2014-2016.csv'%lab

            if not os.path.exists(data_file):
                results = stats_utils.query_lab_usage__df(lab=lab,
                                                          lab_type=lab_type,
                                                          time_start='2014-01-01',
                                                          time_end='2016-12-31')
                df = pd.DataFrame(results, columns=['pat_id', 'order_time', 'result'])
                df.to_csv(data_file, index=False)
            else:
                df = pd.read_csv(data_file,keep_default_na=False)

            my_dict = {'lab':lab}
            my_dict.update(stats_utils.get_prevweek_normal__dict(df))

            print my_dict

            # my_dict = tmp.my_dictt[i]
            # print my_dict
            res_df = res_df.append(my_dict, ignore_index=True)

        max_num = len(res_df.columns)-1
        res_df = res_df[['lab'] + range(max_num)]#[str(x)+' repeats' for x in range(max_num)]]
        res_df = res_df.rename(columns={x:str(x)+' repeats' for x in range(max_num)})
        res_df.to_csv(data_file_all, index=False)
    else:
        res_df = pd.read_csv(data_file_all)

    labs_toPlot = stats_utils.get_top_labs_and_cnts(lab_type)
    max_repeat = 10
    for lab in labs_toPlot: #['LABLAC', 'LABLACWB', 'LABK', 'LABPHOS']:
        nums = res_df[res_df['lab']==lab].values[0][1:max_repeat+1]
        print nums
        nums_valid = [x for x in nums if x]
        print nums_valid
        plt.plot(range(len(nums_valid)), nums_valid, label=lab)

    plt.ylim([0,1])
    plt.xlabel('Num Normality in a Week')
    plt.ylabel('Normal Rate')
    plt.legend()
    plt.show()








def get_important_labs(lab_type='panel', order_by=None):
    # TODO: order_by

    if lab_type == 'panel':
        labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=10)
        print labs_and_cnts

        '''
        Adding other important labs
        '''
        labs_and_cnts.append(['LABCBCD', stats_utils.query_lab_cnt(lab='LABCBCD',
                                            time_limit=['2014-01-01','2016-12-31'])])

        #stats_utils.get_top_labs(lab_type=lab_type, top_k=10)
    elif lab_type == 'component':
        # TODO
        all_labs = all_components

    labs_and_cnts = sorted(labs_and_cnts, key=lambda x: x[1])
    return [x[0] for x in labs_and_cnts]


def plot_order_intensities_barh(lab, time_since_last_order_binned, columns, labeling=True):
    pre_sum = 0
    alphas = [1, 0.5, 0.3, 0.2]
    for i, key in enumerate(columns):

        pre_sum += time_since_last_order_binned[key]

        if labeling:
            plt.barh([lab], pre_sum, color='b', alpha=alphas[i], label=key)
        else:
            plt.barh([lab], pre_sum, color='b', alpha=alphas[i])


def dict2pandas(a_dict, key='lab', val='val'):
    return pd.DataFrame.from_dict(a_dict, orient='index').reset_index().rename(columns={'index': key,
                                                                                        0:val})
def pandas2dict(df, key='lab', val='val'):
    return df.set_index(key).to_dict()[val]

def draw__Normality_Saturations(lab_type, use_cached_fig_data=True):
    '''
    Drawing Figure 1 in the main text.

    :return:
    '''

    labs = get_important_labs()

    print "Labs to be plot:", labs

    cached_result_foldername = 'Fig1_Normality_Saturations/'
    if not os.path.exists(cached_result_foldername):
        os.mkdir(cached_result_foldername)
    cached_result_filename = 'Normality_Saturations_%s.csv' % lab_type
    cached_result_path = os.path.join(cached_result_foldername, cached_result_filename)


    if os.path.exists(cached_result_path) and use_cached_fig_data:
        # lab2stats = pickle.load(open(cached_result_path, 'r'))
        lab2stats_pd = pd.read_csv(cached_result_path)
        lab2stats_pd = lab2stats_pd.set_index('lab')
        lab2stats_pd.columns = lab2stats_pd.columns.astype(int)

        lab2stats = lab2stats_pd.to_dict(orient='index')


    else:

        lab2stats = {}
        for lab in labs:
            df_lab = stats_utils.query_to_dataframe(lab, time_limit=('2014-01-01', '2016-12-31'))
            df_lab = df_lab[df_lab['order_status'] == 'Completed']

            cur_dict = stats_utils.get_prevweek_normal__dict(df_lab)
            lab2stats[lab] = cur_dict
        df_res = pd.DataFrame.from_dict(lab2stats, orient='index').reset_index().rename(columns={'index': 'lab'})
        df_res.to_csv(cached_result_path, index=False)

    print lab2stats

    fig = plt.figure(figsize=(8, 6))
    max_repeat = 5
    for lab in labs:  # ['LABLAC', 'LABLACWB', 'LABK', 'LABPHOS']:
        cur_dict = lab2stats[lab]
        nums = []
        for x in range(0,max_repeat+1):
            if x in cur_dict:
                nums.append(cur_dict[x])
            else:
                nums.append(float('nan'))

        #res_df[res_df['lab'] == lab].values[0][1:max_repeat + 1]
        print nums
        # nums_valid = [x for x in nums if x]
        # print nums_valid


        plt.plot(range(0,max_repeat+1), nums, label=lab)
        plt.scatter(range(0, max_repeat + 1), nums)

    plt.ylim([0, 1])
    plt.xticks(range(0, max_repeat + 1))
    plt.xlabel('Number of Consecutive Normalities in a Week')
    plt.ylabel('Normal Rate')
    plt.legend()
    plt.savefig(cached_result_foldername + 'Normality_Saturations_%s'%lab_type)







    # if lab_type == 'panel':
    #     all_labs = all_panels #stats_utils.get_top_labs(lab_type=lab_type, top_k=10)
    # elif lab_type == 'component':
    #     all_labs = all_components
    #
    # res_df = pd.DataFrame()
    # data_file_all = '%s_waste_in_7days.csv'%lab_type
    #
    # if not os.path.exists(data_file_all):
    #
    #     import tmp
    #
    #     for i, lab in enumerate(all_labs):
    #         data_file = '%s_Usage_2014-2016.csv'%lab
    #
    #         if not os.path.exists(data_file):
    #             results = stats_utils.query_lab_usage__df(lab=lab,
    #                                                       lab_type=lab_type,
    #                                                       time_start='2014-01-01',
    #                                                       time_end='2016-12-31')
    #             df = pd.DataFrame(results, columns=['pat_id', 'order_time', 'result'])
    #             df.to_csv(data_file, index=False)
    #         else:
    #             df = pd.read_csv(data_file,keep_default_na=False)
    #
    #         my_dict = {'lab':lab}
    #         my_dict.update(stats_utils.get_prevweek_normal__dict(df))
    #
    #         print my_dict
    #
    #         # my_dict = tmp.my_dictt[i]
    #         # print my_dict
    #         res_df = res_df.append(my_dict, ignore_index=True)
    #
    #     max_num = len(res_df.columns)-1
    #     res_df = res_df[['lab'] + range(max_num)]#[str(x)+' repeats' for x in range(max_num)]]
    #     res_df = res_df.rename(columns={x:str(x)+' repeats' for x in range(max_num)})
    #     res_df.to_csv(data_file_all, index=False)
    # else:
    #     res_df = pd.read_csv(data_file_all)
    #
    # labs_toPlot = stats_utils.get_top_labs(lab_type)
    # max_repeat = 10
    # for lab in labs_toPlot: #['LABLAC', 'LABLACWB', 'LABK', 'LABPHOS']:
    #     nums = res_df[res_df['lab']==lab].values[0][1:max_repeat+1]
    #     print nums
    #     nums_valid = [x for x in nums if x]
    #     print nums_valid
    #     plt.plot(range(len(nums_valid)), nums_valid, label=lab)
    #
    # plt.ylim([0,1])
    # plt.xlabel('Num Normality in a Week')
    # plt.ylabel('Normal Rate')
    # plt.legend()
    # plt.show()


def draw__Order_Intensities(lab_type='panel', use_cached_fig_data=True):
    '''
    Drawing Figure 2 in the main text.

    :param lab_type:
    :return:
    '''

    '''
    Get labs
    '''
    labs = get_important_labs()
    print "Labs to be plot:", labs

    cached_result_foldername = 'Fig2_Order_Intensities/'
    if not os.path.exists(cached_result_foldername):
        os.mkdir(cached_result_foldername)
    cached_result_filename = 'Order_Intensities_%s.csv'%lab_type
    cached_result_path = os.path.join(cached_result_foldername, cached_result_filename)

    '''
    Each lab 
        -> all its orders in 2014-2016 (implicit) 
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

            df_lab = stats_utils.query_to_dataframe(lab, time_limit=('2014-01-01','2016-12-31'))
            df_lab = df_lab[df_lab['order_status']=='Completed']

            dict_lab = stats_utils.get_time_since_last_order_cnts(lab, df_lab)

            df_lab = pd.DataFrame.from_dict(dict_lab, orient='index').reset_index().rename(columns={'index': 'lab'})
            # df_lab.to_csv(cached_result_foldername + '%s.csv'%lab, index=False)

            sums = [dict_lab[0], sum(dict_lab[x] for x in range(1, 4)), sum(dict_lab[x] for x in range(4, 8))]
            sums.append(sum(dict_lab[x] for x in dict_lab.keys()) - sum(sums))

            time_since_last_order_binned = {columns[_]: sums[_] for _ in range(len(columns))}

            lab2stats[lab] = time_since_last_order_binned

        # pickle.dump(lab2stats, open(cached_result_path, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
        df_res = pd.DataFrame.from_dict(lab2stats, orient='index').reset_index().rename(columns={'index':'lab'})
        df_res.to_csv(cached_result_path, index=False)



    fig = plt.figure(figsize=(8, 6))
    for i, lab in enumerate(labs):
        time_since_last_order_binned = lab2stats[lab]

        if i == 0:
            plot_order_intensities_barh(lab, time_since_last_order_binned, columns=columns, labeling=True)
        else:
            plot_order_intensities_barh(lab, time_since_last_order_binned, columns=columns, labeling=False)

    plt.legend()
    plt.xlabel('Order number between 2014-2016')
    plt.savefig(cached_result_foldername + 'Order_Intensities_%s.png'%lab_type)
    # quit()
    #
    # print 'total cnt:', df.shape[0]
    # print 'repetitive cnt:', sum(prevday_cnts_dict.values())
    # print 'within 24 hrs:', prevday_cnts_dict[0]
    # print 'within 48 hrs:', prevday_cnts_dict[1]





def draw__Potential_Savings(wanted_PPV=0.95):
    '''
    Drawing Figure 4 in the main text.

    :return:
    '''

    df = pd.read_csv('data_performance_stats/best-alg-panel-summary-fix-trainPPV.csv',
                     keep_default_na=False)
    df = df[df['train_PPV'] == wanted_PPV]

    labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=50)
    df = df[df['lab'].isin([x[0] for x in labs_and_cnts])]

    data_folder = 'Fig4_Potential_Savings/'
    fig_filename = 'Potential_Savings.png'
    fig_path = os.path.join(data_folder, fig_filename)
    data_filename = 'Potential_Savings.csv'
    data_path = os.path.join(data_folder, data_filename)

    if os.path.exists(data_path):
        df_sorted_by_normal_cost = pd.read_csv(data_path, keep_default_na=False)

    else:


        # df = df[df['lab'] != 'LABNA']  # TODO: fix LABNA's price here

        df['normal_rate'] = (df['true_positive'] + df['false_negative']).round(5)

        # if lab_type == "component":
        #     df = df.rename(columns={'2016_Vol': 'count'})
        #     df = df.dropna()
        # df['count'] = df['count'].apply(lambda x: 0 if x == '' else x)

        my_dict = {x[0]: x[1] for x in labs_and_cnts}
        df['count'] = df['lab'].map(my_dict)

        # df['total cost'] = df['count'].apply(lambda x: float(x) / 1000000.)  #

        df['total_cost'] = df['count'] * df['median_price'].apply(lambda x:float(x)/1000000. if x!='' else 0)  # cost
        # volumn_label = 'Total cost in 2014-2016'

        '''
        Picking the top 20 popular labs.
        '''
        # df_sorted_by_cnts = df.sort_values('total_cost', ascending=True).ix[:,
        #                     ['lab', 'normal_rate', 'true_positive', 'total_cost']].drop_duplicates()#.head(20).copy()
        df = df[['lab', 'normal_rate', 'true_positive', 'total_cost']]

        # df_sorted_by_cnts = df_sorted_by_cnts.sort_values('volumn', ascending=True)


        # ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['volumn'], color='grey', alpha=0.5,
        #         label=volumn_label)

        df['normal_cost'] = df['normal_rate'] * df['total_cost']
        df['truepo_cost'] = df['true_positive'] * df['total_cost']

        df_sorted_by_normal_cost = df.sort_values('truepo_cost', ascending=True).tail(10)
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
        ax.text(v, i, str("{0:.0%}".format((df_sorted_by_normal_cost['true_positive']/df_sorted_by_normal_cost['normal_rate']).values[i])), color='k',
                fontweight='bold')

    # plt.xlim([0,1])
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)

    plt.legend()
    plt.xlabel('Total Cnt (in millions) in 2014-2016')

    plt.savefig(fig_path)

    plt.show()








def plot_curves__overlap(lab_type='panel', curve_type="roc"):
    if lab_type == 'panel':
        data_folder = '../machine_learning/data-panels/'
        all_labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
    elif lab_type == 'component':
        data_folder = '../machine_learning/data-components/'
        all_labs = STRIDE_COMPONENT_TESTS
    elif lab_type == 'UMich':
        data_folder = "../machine_learning/data-UMich/"
        all_labs = UMICH_TOP_COMPONENTS

    num_labs_in_one_fig = 10
    for i, lab in enumerate(all_labs):
        xVal_base, yVal_base, base_score, xVal_best, yVal_best, best_score = \
            stats_utils.get_curve_onelab(lab,
                                     all_algs=SupervisedClassifier.SUPPORTED_ALGORITHMS,
                                     data_folder=data_folder,
                                     curve_type=curve_type)
        plt.plot(xVal_base, yVal_base, label=lab+' %.2f'%base_score)

        if (i+1)%num_labs_in_one_fig == 0:
            plt.legend()
            #plt.show()
            plt.savefig('%s-%s-baseline.png'%(all_labs[i+1-num_labs_in_one_fig],lab))
            plt.close()
    plt.close()

    for i, lab in enumerate(all_labs):
        xVal_base, yVal_base, base_score, xVal_best, yVal_best, best_score = \
            stats_utils.get_curve_onelab(lab,
                                     all_algs=SupervisedClassifier.SUPPORTED_ALGORITHMS,
                                     data_folder=data_folder,
                                     curve_type=curve_type)
        plt.plot(xVal_best, yVal_best, label=lab+' %.2f'%best_score)

        if (i+1)%num_labs_in_one_fig == 0:
            plt.legend()
            #plt.show()
            plt.savefig('%s-%s-bestalg.png'%(all_labs[i+1-num_labs_in_one_fig],lab))
            plt.close()


######################################
'''
refactoring
'''

def draw__Confusion_Metrics(wanted_PPV=0.95, use_cached_fig_data=True):
    '''
    Drawing Figure 3 in the main text.

    :return:
    '''
    df = pd.read_csv('data_performance_stats/best-alg-%s-summary-fix-trainPPV.csv' % lab_type,
                     keep_default_na=False)
    df = df[df['train_PPV'] == wanted_PPV]

    cached_foldername = 'Fig3_Confusion_Metrics/'
    cached_filename = 'Confusion_Metrics_%ss.csv'%lab_type
    cached_result_path = os.path.join(cached_foldername, cached_filename)

    if os.path.exists(cached_result_path) and use_cached_fig_data:
        # lab2stats = pickle.load(open(cached_result_path, 'r'))
        df_toplot = pd.read_csv(cached_result_path, keep_default_na=False)

    else:

        labs_and_cnts = stats_utils.get_top_labs_and_cnts(lab_type)
        # labs_and_cnts.append(['LABCBCD', stats_utils.query_lab_cnt(lab='LABCBCD',
        #                                                            time_limit=['2014-01-01', '2016-12-31'])])

        df = df[df['lab'].isin([x[0] for x in labs_and_cnts])]
        print df.head()
        my_dict = {x[0]:x[1] for x in labs_and_cnts}
        df['count'] = df['lab'].map(my_dict)

        df['all_positive'] = df['true_positive'] + df['false_positive']
        df['all_negative'] = df['true_negative'] + df['false_negative']

        df['true_negative'] = -df['true_negative']
        df['all_negative'] = -df['all_negative']

        df['count'] = df['count'].apply(lambda x: float(x) if x != '' else 0)
        # if lab_type == 'component':
        #     df['count'] = df['count'].apply(lambda x: x / 1000000)

        # print df[['true_positive', 'all_positive',
        #           'true_negative', 'all_negative']].head(5).plot(kind='barh')

        df_toplot = df

        df['all_positive'] *= df['count']
        df['true_positive'] *= df['count']
        df['all_negative'] *= df['count']
        df['true_negative'] *= df['count']

        df_toplot[['lab', 'count',
                   'PPV', 'NPV', 'sensitivity', 'specificity', 'LR_p', 'LR_n',
                   'all_positive', 'true_positive', 'all_negative', 'true_negative']]\
                    .sort_values('count', ascending=False)\
                    .to_csv(cached_result_path, index=False, float_format='%.2f')

    df_toplot = df_toplot.sort_values('count', ascending=True)

    fig, ax = plt.subplots()
    ax.barh(df_toplot['lab'], df_toplot['all_positive'], color='orange', alpha=0.5, label='False Positive')
    ax.barh(df_toplot['lab'], df_toplot['true_positive'], color='blue', alpha=1, label='True Positive')

    ax.barh(df_toplot['lab'], df_toplot['all_negative'], color='blue', alpha=0.5, label='False Negative')
    ax.barh(df_toplot['lab'], df_toplot['true_negative'], color='orange', alpha=1, label='True Negative')


    if lab_type == 'panel':
        for i, v in enumerate(df_toplot['all_negative']):
            ax.text(-60000, i, df_toplot['lab'].values[i], color='k')

    elif lab_type == 'component':
        for i, v in enumerate(df_toplot['all_negative']):
            ax.text(-150000, i, df_toplot['lab'].values[i], color='k')
            plt.xticks([-1500000, -1000000, -500000, 0, 500000])

    plt.yticks([])

    plt.legend()
    plt.xlabel('total lab cnt in 2014-2016')
    plt.ylabel('labs')

    plt.savefig(cached_foldername+'Confusion_Metrics_%ss.png'%lab_type)

    plt.show()

'''
refactoring
'''
######################################

######################################
'''
refactored
'''

def draw__ROC_PRC_Curves(curve_type="roc", algs=['random-forest']):
    num_labs = len(all_labs)
    row, col, i_s, j_s = prepare_subfigs(num_labs)

    scores_base = []
    scores_best = []
    for ind, lab in enumerate(all_labs):

        xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best \
            = stats_utils.get_curve_onelab(lab,
                                           all_algs=algs,
                                           data_folder=lab_folder,
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
    plt.savefig('%s_%s.png'%(lab_type, curve_type))

    avg_base, avg_best = np.mean(scores_base), np.mean(scores_best)
    print "Average %s among %i labs: %.3f baseline, %.3f bestalg (an improvement of %.3f)."\
          %(curve_type, len(scores_base), avg_base, avg_best, avg_best-avg_base)



def get_prevday2normalities(lab, time_limit=DEFAULT_TIMELIMIT, source='full'):
    '''
    Args:
        lab:
        time_limit:

    Returns:

    '''

    if source == 'full':
        df_lab = stats_utils.query_to_dataframe(lab, time_limit=time_limit)
        df_lab = df_lab[df_lab['order_status']=='Completed'].reset_index(drop=True)

    elif source == 'test':
        import LocalEnv
        from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

        print "processing %s..."%lab
        data_folder = LocalEnv.PATH_TO_CDSS + '/scripts/LabTestAnalysis/machine_learning/data-panels/%s/' % lab
        data_processed_filename = '%s-normality-test-matrix-10000-episodes-processed.tab' % lab
        data_processed_pathname = data_folder + data_processed_filename

        fm_io = FeatureMatrixIO()
        df_processed_test_lab = fm_io.read_file_to_data_frame(data_processed_pathname)
        pat_ids_test = set(df_processed_test_lab['pat_id'].values.tolist())

        data_raw_filename = '%s-normality-matrix-10000-episodes-raw.tab' % lab
        data_raw_pathname = data_folder + data_raw_filename

        df_raw = fm_io.read_file_to_data_frame(data_raw_pathname)
        df_lab = df_raw[df_raw['pat_id'].isin(pat_ids_test)]
        df_lab['abnormal_yn'] = df_lab['abnormal_panel'].apply(lambda x: 'Y' if x==1 else 'N')
        df_lab = df_lab[['pat_id', 'order_time', 'abnormal_yn']]

    day2norms = stats_utils.get_prevweek_normal__dict(df_lab, also_get_cnt=True)

    return day2norms.keys(), day2norms.values()



def draw__Comparing_Savable_Fractions(lab_type='panel',
                         target_PPV=0.95,
                         use_cache=True):
    '''
    Targeting at PPV=0.95, what are the savable fractions from each method?

    :return:
    '''
    result_folder = 'Fig5_Comparing_Savable_Fractions/'
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)

    result_filename = 'Comparing_Savable_Fractions.csv'
    result_filepath = os.path.join(result_folder, result_filename)

    result_figname = 'Comparing_Savable_Fractions.png'
    result_figpath = os.path.join(result_folder, result_figname)

    if use_cache and os.path.exists(result_filepath):
        df_twomethods = pd.read_csv(result_filepath, keep_default_na=False)
        print df_twomethods
        savable_fractions_simple = pandas2dict(df_twomethods, key='lab', val='savable_fraction_simple')
        savable_fractions_mlmodel = pandas2dict(df_twomethods, key='lab', val='savable_fraction_mlmodel')
        print savable_fractions_simple, savable_fractions_mlmodel
    else:


        # labs_and_cnts = stats_utils.get_top_labs_and_cnts('panel', top_k=76)
        # labs = [x[0] for x in labs_and_cnts]
        labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
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
            for lab in labs:
                # try:
                    days, normality_lists = get_prevday2normalities(lab, source="test")
                    normality_fractions = [float(sum(x))/float(len(x)) for x in normality_lists]
                    normality_cnts = [len(x) for x in normality_lists]
                    '''
                    For the rule of "passing a number of days, then all set 'normal',
                    the normal rate is equals to the PPV. "
                    '''
                    import sys
                    day_thres = sys.maxint
                    savable_cnt = 0
                    for i, normality_fraction in enumerate(normality_fractions):
                        if normality_fraction > target_PPV:
                            day_thres = days[i]

                            '''
                            Assumption: noramlity rate monotonically increases
                            '''
                            savable_cnt += normality_cnts[i]
                    savable_fraction = float(savable_cnt)/float(sum(normality_cnts))
                    savable_fractions_simple[lab] = savable_fraction
                # except Exception as e:
                #     print e
            df_simple = dict2pandas(savable_fractions_simple, key='lab', val='savable_fraction_simple')

        '''
        Machine learning model
        '''
        # TODO: counts in the file needs update
        df_mlmodel = pd.read_csv('data_performance_stats/best-alg-panel-summary-fix-trainPPV.csv',
                         keep_default_na=False)
        df_mlmodel = df_mlmodel[(df_mlmodel['train_PPV']==0.95) & df_mlmodel['lab'].isin(labs)]
        df_mlmodel['savable_fraction_mlmodel'] = (df_mlmodel['true_positive'] + df_mlmodel['false_positive'])#.round(5)
        df_mlmodel = df_mlmodel[['lab', 'savable_fraction_mlmodel']]

        savable_fractions_mlmodel = pandas2dict(df_mlmodel, key='lab', val='savable_fraction_mlmodel')

        df_twomethods = df_simple.merge(df_mlmodel, on='lab', how='left')
        df_twomethods.to_csv(result_filepath, index=False)

    plot_subfigs(savable_fractions_simple,
                 savable_fractions_mlmodel,
                 plot_type='bar',
                 result_figpath=result_figpath)




def prepare_subfigs(num_figs):
    col = 5
    row = num_figs / col
    cols_left = num_figs % col
    if cols_left > 0:
        row = row + 1

    fig_width, fig_heights = col * 3., 8. / col * row

    plt.figure(figsize=(fig_width, fig_heights))

    i_s = []
    j_s = []
    for ind in range(num_figs):
        ind_in_fig = ind % num_figs
        i, j = ind_in_fig / col, ind_in_fig % col
        i_s.append(i)
        j_s.append(j)

    return row, col, i_s, j_s

def plot_subfigs(dict1, dict2, plot_type, result_figpath="subfigs.png"):
    print dict1
    print dict2
    assert len(dict1) == len(dict2)


    num_labs = len(dict1)

    row, col, i_s, j_s = prepare_subfigs(num_labs)


    keys = dict1.keys()

    def do_one_plot(x, y, color):
        plt.bar(x, y, color=color)
        plt.text(x, y, '%.2f' % y, color='k')

        plt.xticks([])
        plt.ylim(0, 1.05)
        plt.yticks([])

    for ind, key in enumerate(keys):


        i, j = i_s[ind], j_s[ind]
        plt.subplot2grid((row, col), (i, j))


        do_one_plot(1, dict1[key], color='blue')
        do_one_plot(2, dict2[key], color='orange')

        plt.xlabel(key)

    plt.savefig(result_figpath)

'''
refactored
'''
######################################



def plot_cartoons(lab_type='panel', labs=all_panels):
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

def PPV_judgement(lab_type="panel", PPV_wanted=0.95):
    df_fix_test = pd.read_csv(
        "data_performance_stats/thres_from_testPPV/best-alg-%s-summary.csv" % lab_type,
        keep_default_na=False)
    df_fix_test = df_fix_test[df_fix_test['test_PPV']==PPV_wanted]
    df_fix_test['actual_normal'] = df_fix_test['true_positive'] + df_fix_test['false_negative']
    df_fix_test['predict_normal'] = df_fix_test['true_positive'] + df_fix_test['false_positive'] #[['normal_prevalence', '']]
    df_fix_test[['lab', 'actual_normal', 'predict_normal']].sort_values('predict_normal', ascending=False).to_csv("validation_fixPPV_%ss.csv"%lab_type, index=False) #.to_string(index=False)

def PPV_guideline(lab_type="panel"):

    df_fix_train = pd.read_csv("data_performance_stats/best-alg-%s-summary-trainPPV.csv"%lab_type,
                               keep_default_na=False)

    range_bins = [0.99] + np.linspace(0.95, 0.5, num=10).tolist()
    columns = ['Target PPV', 'Total labs', 'Valid labs']
    columns += ['[0.99, 1]']
    for i in range(len(range_bins) - 1):
        columns += ['[%.2f, %.2f)' % (range_bins[i + 1], range_bins[i])]

    rows = []
    for wanted_PPV in [0.8, 0.90, 0.95, 0.99][::-1]: # TODO: what is the problem with 0.9? LABHIVWBL
        cur_row = [wanted_PPV]

        PPVs_from_train = df_fix_train.ix[df_fix_train['train_PPV']==wanted_PPV, ['PPV']]
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
    df.to_csv("predict_power_%ss.csv"%lab_type, index=False)

def check_similar_components():
    # common_labs = list(set(STRIDE_COMPONENT_TESTS) & set(UMICH_TOP_COMPONENTS))

    df_UMich = pd.read_csv('RF_important_features_UMichs.csv',keep_default_na=False)
    df_component = pd.read_csv('RF_important_features_components.csv',keep_default_na=False)

    columns_UMich_only = []
    columns_component_only = []
    for i in range(1,4):
        df_UMich = df_UMich.rename(columns={'feature %i'%i:'UMich featu %i'%i,
                                            'score %i'%i:'UMich score %i'%i})
        columns_UMich_only += ['UMich featu %i'%i, 'UMich score %i'%i]
        df_component = df_component.rename(columns={'feature %i'%i:'STRIDE featu %i'%i,
                                                    'score %i' % i:'STRIDE score %i' % i})
        columns_component_only += ['STRIDE featu %i'%i, 'STRIDE score %i'%i]

    df_combined = pd.merge(df_component, df_UMich, on='lab', how='inner')
    (df_combined[['lab'] + columns_UMich_only]).to_csv("UMich_feature_importance_to_compare.csv", index=False)
    (df_combined[['lab'] + columns_component_only]).to_csv("component_feature_importance_to_compare.csv", index=False)

def get_labs_cnts(lab_type):
    df = pd.DataFrame(columns=['lab', 'cnt 2014-2016'])

    if lab_type == 'panel':
        labs = all_panels
    elif lab_type == 'component':
        labs = all_components

    for lab in labs:
        try:
            cur_result = stats_utils.query_lab_cnts(lab=lab,
                                                    lab_type=lab_type,
                                                    time_limit=('2014-01-01', '2016-12-31'))
            print cur_result
            df = df.append({'lab': cur_result[0], 'cnt 2014-2016': cur_result[1]}, ignore_index=True)
        except Exception as e:
            print e

    df.to_csv('%s-cnts-2014-2016.csv' % lab_type, index=False)

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

if __name__ == '__main__':
    # plot_cartoons(lab_type='panel', labs=['LABUAPRN','LABCAI','LABPT',
    #                                       'LABUA', 'LABPTT', 'LABHEPAR',
    #                                       'LABCMVQT', 'LABURNC', 'LABPTEG'])
    # plot_cartoons('UMich', labs=UMICH_TOP_COMPONENTS)
    # plot_cartoons('component', labs=['HGB'])

    # plot_cartoons('UMich')

    # draw__guidelines_bar()

    # plot_curves__subfigs(lab_type='component', curve_type="roc")
    # plot_curves__overlap(lab_type='UMich', curve_type="roc")
    # PPV_guideline(lab_type="UMich")

    # check_similar_components()
    # write_importantFeatures(lab_type='UMich')

    # plot_NormalRate__bar(lab_type="panel", wanted_PPV=0.95, add_predictable=True, look_cost=True)
    # get_waste_in_7days('component')

    # plot_curves__subfigs('UMich', curve_type='prc')

    # draw__Potential_Savings()
    # draw__Order_Intensities('panel')
    # draw__Normality_Saturations('panel')
    # draw__Confusion_Metrics('panel')


    # plot_predict_twoside_bar('component')

    # test('LABALB')

    '''
    refactored: 
    '''
    # draw__Comparing_Savable_Fractions('panel', use_cache=True)

    #draw__ROC_PRC_Curves(curve_type='prc', algs=['random-forest'])

    draw__Confusion_Metrics()
