

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option("display.max_columns", 10)
import numpy as np
import os
from sklearn.metrics import roc_auc_score, roc_curve

import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'
import matplotlib.pyplot as plt
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import \
        NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS

train_PPVs = [0.99, 0.95, 0.9, 0.8] #[0.5, 0.75, 0.90, 0.95, 0.975, 0.99]

def get_thres_from_training_data_by_fixing_PPV(lab, alg, data_folder = '', PPV_wanted = 0.9):
    df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                     '%s-normality-prediction-%s-direct-compare-results-traindata.csv'%(lab,alg))

    # TODO: calibration?
    row, col = df.shape
    thres_last, PPV_last = 1., 1.
    actual_list = df['actual'].values.tolist()

    for thres in np.linspace(1,0,num=1001):

        df['predict_class'] = df['predict'].apply(lambda x: 1 if x>thres else 0)
        predict_class_list = df['predict_class'].values.tolist()

        true_positive = 0
        false_positive = 0
        true_negative = 0
        false_negative = 0
        for i in range(row):
            if actual_list[i] == 1 and predict_class_list[i] == 1:
                true_positive += 1
            elif actual_list[i] == 0 and predict_class_list[i] == 1:
                false_positive += 1
            elif actual_list[i] == 1 and predict_class_list[i] == 0:
                false_negative += 1
            elif actual_list[i] == 0 and predict_class_list[i] == 0:
                true_negative += 1
            else:
                print "what?!"

        try:
            PPV = float(true_positive) / float(true_positive + false_positive)
        except ZeroDivisionError:
            # PPV = float('nan')
            continue

        if PPV < PPV_wanted:
            thres = thres_last
            PPV = PPV_last
            break
        else:
            thres_last = thres
            PPV_last = PPV

    return thres_last

def bootstrap_CI(actual_list, predict_list, num_repeats=1000, stat = 'roc_auc',
                 confident_lvl=0.95, side='two', random_state=0):
    assert len(actual_list) == len(predict_list)

    from sklearn.utils import resample

    all_stats = []
    for i in range(num_repeats):
        actual_list_resampled, predict_list_resampled = resample(actual_list, predict_list)
        if stat == 'roc_auc':
            cur_roc_auc = roc_auc_score(actual_list_resampled, predict_list_resampled)
            all_stats.append(cur_roc_auc)

    roc_auc_left = np.percentile(all_stats, (1-confident_lvl)/2.*100)
    roc_auc_right = np.percentile(all_stats, (1+confident_lvl)/2.*100)

    return roc_auc_left, roc_auc_right

def fill_df_fix_PPV(lab, alg, data_folder = '', PPV_wanted = 0.9, lab_type=None, quick_test=False):

    df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                     '%s-normality-prediction-%s-direct-compare-results.csv'%(lab,alg))
    row, col = df.shape


    '''
    roc_auc, and its confidence interval (CI)
    Independent of any threshold
    '''
    actual_list = df['actual'].values.tolist()

    try:
        roc_auc = roc_auc_score(actual_list, df['predict'].values)
        roc_auc_left, roc_auc_right = bootstrap_CI(actual_list, df['predict'], confident_lvl=0.95)
    except ValueError:
        roc_auc, roc_auc_left, roc_auc_right = float('nan'), float('nan'), float('nan')


    '''
    Score threshold is used for "predict_proba --> predict_label"
    Learning score threshold by fixing training PPV at desired lvl
    This way, learned test (evaluation) PPV is "unbiased". 
    '''
    if quick_test:
        thres = 0.5
    else:
        thres = get_thres_from_training_data_by_fixing_PPV(lab, alg, data_folder=data_folder, PPV_wanted=PPV_wanted)
    df['predict_class'] = df['predict'].apply(lambda x: 1 if x > thres else 0)
    predict_class_list = df['predict_class'].values.tolist()

    '''
    Based on threshold, counting:
    'true_positive', 'false_positive', 'true_negative', 'false_negative'
    
    Calculating:
    'sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV'
    '''
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    total_cnt = 0
    for i in range(row):
        if actual_list[i] == 1 and predict_class_list[i] == 1:
            true_positive += 1
        elif actual_list[i] == 0 and predict_class_list[i] == 1:
            false_positive += 1
        elif actual_list[i] == 1 and predict_class_list[i] == 0:
            false_negative += 1
        elif actual_list[i] == 0 and predict_class_list[i] == 0:
            true_negative += 1
        else:
            print "what?!"
        total_cnt += 1

    res_dict = {'lab':lab, 'alg':alg, 'threshold': thres,
           'true_positive':true_positive/float(total_cnt), 'false_positive': false_positive/float(total_cnt),
           'true_negative':true_negative/float(total_cnt), 'false_negative':false_negative/float(total_cnt),
           'total_cnt':total_cnt, 'roc_auc': roc_auc,
           '95%_CI': '[%f, %f]'%(roc_auc_left,roc_auc_right)}
    res_dict['sensitivity'] = float(true_positive)/float(true_positive + false_negative)
    res_dict['specificity'] = float(true_negative)/float(true_negative + false_positive)
    try:
        res_dict['LR_p'] = res_dict['sensitivity']/(1-res_dict['specificity'])
    except ZeroDivisionError:
        if res_dict['sensitivity'] == 0:
            res_dict['LR_p'] = float('nan')
        else:
            res_dict['LR_p'] = float('inf')

    try:
        res_dict['LR_n'] = (1-res_dict['sensitivity'])/res_dict['specificity']
    except ZeroDivisionError:
        if res_dict['sensitivity'] == 1:
            res_dict['LR_n'] = float('nan')
        else:
            res_dict['LR_n'] = float('inf')

    try:
        res_dict['PPV'] = float(true_positive)/float(true_positive + false_positive)
    except ZeroDivisionError:
        res_dict['PPV'] = float('nan')

    try:
        res_dict['NPV'] = float(true_negative)/float(true_negative + false_negative)
    except ZeroDivisionError:
        res_dict['PPV'] = float('nan')


    return res_dict


def add_panel_cnts_fees(one_lab_alg_dict):
    panel =  one_lab_alg_dict['lab']
    df_cnts_fees = pd.read_csv('data_summary_stats/labs_charges_volumes.csv')
    cnts_fees_dict = df_cnts_fees.ix[df_cnts_fees['name']==panel, ['count',
                                                        'min_price',
                                                        'max_price',
                                                        'mean_price',
                                                        'median_price',
                                                        'min_volume_charge',
                                                        'max_volume_charge',
                                                        'mean_volume_charge',
                                                        'median_volume_charge']].to_dict(orient='list')
    # print cnts_fees_dict
    for key in cnts_fees_dict.keys():
        try:
            cnts_fees_dict[key] = cnts_fees_dict[key][0]
        except IndexError:
            cnts_fees_dict[key] = float('nan')

    one_lab_alg_dict.update(cnts_fees_dict)
    return one_lab_alg_dict


'''
For individual component, there is no well-defined "fee".
'''
def add_component_cnts(one_lab_dict, years):
    component = one_lab_dict['lab']
    df_cnts = pd.read_csv('data_summary_stats/component_cnts.txt', sep='\t', keep_default_na=False)
    # df = df.rename(columns={'Base':'lab'})

    for year in years:
        one_lab_dict[str(year)+'_Vol'] = df_cnts.ix[df_cnts['Base']==component, str(year)].values[0]
        # TODO: rename total_cnt to avoid confusion between total STRIDE cnt & testing cnt!

    return one_lab_dict


def get_baseline(file_path):
    # try:
    df = pd.read_csv(file_path + 'baseline_comparisons.csv') # TODO: baseline file should not have index!
    # except IOError:
    #     from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
    #     f = FeatureMatrixFactory()
    #     f.obtain_baseline_results(raw_matrix_path=file_path, random_state=123456789, isLabPanel=True)
    #     df = pd.read_csv(file_path + 'baseline_comparisons.csv')

    try:
        res = roc_auc_score(df['actual'], df['predict'])
    except ValueError:
        res = float('nan')

    return res


'''
For each lab at each (train_PPV, vital_day), 
write all stats (e.g. roc_auc, PPV, total cnts) into csv file. 
'''
def lab2stats_csv(lab_type, lab, years, all_algs, PPV_wanted, vital_day, folder_path, data_folder, result_folder, columns):
    curr_res_file = '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv' % (lab, str(PPV_wanted), vital_day)
    if os.path.exists(result_folder + curr_res_file):
        return

    df = pd.DataFrame(columns=columns)

    baseline_roc_auc = get_baseline(file_path=folder_path + '/' + data_folder + '/' + lab + '/')

    for alg in all_algs:
        print 'Processing lab %s with alg %s' % (lab, alg)
        # try:
        one_lab_alg_dict = fill_df_fix_PPV(lab, alg, data_folder=folder_path + '/' + data_folder,
                                           PPV_wanted=PPV_wanted, lab_type=lab_type, quick_test=False)

        if lab_type == 'component':
            one_lab_alg_dict = add_component_cnts(one_lab_alg_dict, years=years)
        elif lab_type == 'panel':
            one_lab_alg_dict = add_panel_cnts_fees(one_lab_alg_dict)

        one_lab_alg_dict['baseline_roc'] = baseline_roc_auc

        df = df.append(one_lab_alg_dict, ignore_index=True)
        # except Exception as e:
        #     print e
        #     pass

    # print 'PPV_wanted=%.2f finished!' % PPV_wanted #TODO

    df[columns].to_csv(result_folder + curr_res_file, index=False)


all_panels = NON_PANEL_TESTS_WITH_GT_500_ORDERS
all_components = STRIDE_COMPONENT_TESTS #['WBC', 'HGB', 'K', 'NA', 'CR', 'GLU'] #STRIDE_COMPONENT_TESTS
all_UMich = [
                'WBC', 'HGB',
                'PLT', 'SOD', 'POT', 'CREAT', 'TBIL', 'CHLOR', 'CO2',
                'AST', 'ALT',
            'ALB', 'CAL',
            'PO2AA', 'PCOAA2']
'''
For each (train-)PPV wanted, each vital-day dataset
Create a summary of all algs' performances on all labs
'''
def main_files_to_separate_stats(lab_type = 'component', years=[2016], vital_days = [3], PPVs_wanted = train_PPVs,
                                columns = None):

    folder_path = '../machine_learning/'


    for vital_day in vital_days:
        if lab_type == 'panel':
            data_folder = 'data-panels' #'data-panels-%ddaysVitals'%vital_day
            all_labs = all_panels
        elif lab_type == 'component':
            all_labs = all_components
            data_folder = 'data-components'#'data-components-3daysVitals' #'data-components-%ddaysVitals'%vital_day
        elif lab_type == 'UMich':
            all_labs = all_UMich
            data_folder = 'data-UMich'


        result_folder = 'data_performance_stats/all_%ss/'%lab_type


        if not os.path.exists(result_folder):
            os.mkdir(result_folder)


        all_algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

        for PPV_wanted in PPVs_wanted:

            for lab in all_labs:

                '''
                For each lab at each (train_PPV, vital_day), 
                write all stats (e.g. roc_auc, PPV, total cnts) into csv file. 
                '''
                try:
                    lab2stats_csv(lab_type, lab, years, all_algs, PPV_wanted, vital_day, folder_path, data_folder, result_folder, columns)
                except:
                    pass



def main_agg_stats(lab_type = 'component', vital_days = [3], PPVs_wanted = train_PPVs, columns=None):

    df_long = pd.DataFrame(columns=columns)

    columns_best_alg = [x if x!='alg' else 'best_alg' for x in columns]
    df_best_alg = pd.DataFrame(columns=columns_best_alg)

    result_folder = 'data_performance_stats/all_%ss/' % lab_type

    if lab_type == 'panel':
        all_labs = all_panels
    elif lab_type == 'component':
        all_labs = all_components
    elif lab_type == 'UMich':
        all_labs = all_UMich

    for PPV_wanted in PPVs_wanted:
        for vital_day in vital_days: #TODO: create the column of vitals
            for lab in all_labs:

                df_cur = pd.read_csv(result_folder + '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv'%(lab, str(PPV_wanted), vital_day), keep_default_na=False)
                df_cur['train_PPV'] = PPV_wanted
                df_cur['vital_day'] = vital_day


                df_long = df_long.append(df_cur, ignore_index=True)

                df_cur_best_alg = df_cur.groupby(['lab'], as_index=False).agg({'roc_auc': 'max'})
                df_cur_best_alg = pd.merge(df_cur_best_alg, df_cur, on=['lab', 'roc_auc'], how='left')

                df_cur_best_alg = df_cur_best_alg.rename(columns={'alg': 'best_alg'})
                df_best_alg = df_best_alg.append(df_cur_best_alg)

    df_long[columns].to_csv('data_performance_stats/'+'long-%s-summary.csv'% lab_type, index=False)
    df_best_alg[columns_best_alg].to_csv('data_performance_stats/'+'best-alg-%s-summary.csv'% lab_type, index=False)

def main():
    lab_type = 'component'

    columns_panels = ['lab', 'alg', 'roc_auc', '95%_CI', 'baseline_roc', 'total_cnt']
    columns_panels += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns_panels += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
    columns_panels += ['count', 'min_price', 'max_price', 'mean_price', 'median_price',
                       'min_volume_charge', 'max_volume_charge', 'mean_volume_charge', 'median_volume_charge']

    columns_panels_agg = columns_panels[:6] + ['vital_day', 'train_PPV'] + columns_panels[6:]
    # TODO: Finish the panel routine, but first deal with the NA 2015 issue?

    years = [2016]  # which years' cnt to look at
    columns_components = ['lab', 'alg', 'roc_auc', '95%_CI', 'baseline_roc', 'total_cnt']  # basic info
    columns_components += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns_components += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
    columns_components += [str(year) + '_Vol' for year in years]

    columns_components_agg = columns_components[:6] + ['vital_day', 'train_PPV'] + columns_components[6:]

    if lab_type == 'panel':
        columns = columns_panels
        columns_agg = columns_panels_agg
    else:
        columns = columns_components
        columns_agg = columns_components_agg

    main_files_to_separate_stats(lab_type=lab_type, years=[2016], vital_days=[3], PPVs_wanted=train_PPVs,
                                 columns=columns)

    main_agg_stats(lab_type=lab_type, vital_days=[3], PPVs_wanted=train_PPVs, columns=columns_agg)

def main_plot_roc(lab_type = 'component', vital_day = 3, look_baseline=False):
    folder_path = '../machine_learning/'

    if lab_type == 'panel':
        data_folder = 'data-panels-%ddaysVitals_old' % vital_day
        all_labs = all_panels #['LABA1C', 'LABLAC', 'LABK', 'LABNTBNP', 'LABOSM', 'LABPALB', 'LABPCCG4O', 'LABPCCR']
    else:
        all_labs = all_components
        # data_folder = 'data-components-%ddaysVitals' % vital_day
        data_folder = 'data'

    from medinfo.ml.SupervisedClassifier import SupervisedClassifier
    all_algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

    for lab in all_labs:

        plot_roc(lab, all_algs, folder_path+data_folder, look_baseline=look_baseline)
    plt.legend()
    plt.show()

def main_plot_sensitivity():
    lab = 'WBC'
    df = pd.read_csv('data_performance_stats/for_plotting_sensitivities.csv') # TODO

    xs = train_PPVs
    ys1 = []

    ys2 = []

    for train_PPV in train_PPVs:
        tmp_df = df[df['train_PPV']==train_PPV].copy()
        tmp_df['predict_positive_ratio'] = tmp_df['true_positive'] + tmp_df['false_positive']
        tmp_df['predict_positive_num_2016'] = tmp_df['predict_positive_ratio'] * tmp_df['2016_Vol']
        res1 = tmp_df.ix[tmp_df['lab']==lab, 'predict_positive_num_2016']
        ys1.append(res1.values[0])
        # ys1 = (df['true_positive'] + df['false_positive']).values # anual cnt of positive

        res2 = tmp_df.ix[tmp_df['lab']==lab, 'PPV']
        ys2.append(res2.values[0])
    print ys1
    print ys2

    fig, ax1 = plt.subplots()

    ax1.bar(xs, ys1, width=0.01)
    ax1.set_xlabel('train PPVs (%s)'%lab)
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('annual cnt of positive predictions', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(xs, ys2, 'r.')
    ax2.set_ylabel('test PPVs', color='r')
    ax2.tick_params('y', colors='r')

    fig.tight_layout()
    plt.show()



if __name__ == '__main__':
    # main_plot_roc(lab_type='component', vital_day=3, look_baseline=False)
    main()

    # main_plot_sensitivity()