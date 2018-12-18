

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option("display.max_columns", 10)
import numpy as np
import os
from sklearn.metrics import roc_auc_score, roc_curve
import stats_utils

import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'
import matplotlib.pyplot as plt

train_PPVs = [0.99, 0.95, 0.9, 0.8] #[0.5, 0.75, 0.90, 0.95, 0.975, 0.99]

lab_type = stats_utils.lab_type
all_labs = stats_utils.all_labs
lab_folder = stats_utils.lab_folder
all_algs = stats_utils.all_algs

DEFAULT_TIMEWINDOWS = stats_utils.DEFAULT_TIMEWINDOWS

'''
For each (train-)PPV wanted, each vital-day dataset
Create a summary of all algs' performances on all labs
'''
def main_files_to_separate_stats(PPVs_wanted = train_PPVs,
                                columns = None, thres_mode="from_test"):

    folder_path = '../machine_learning/'

    result_folder = 'data_performance_stats/all_%ss/'%lab_type


    if not os.path.exists(result_folder):
        os.mkdir(result_folder)


    for PPV_wanted in PPVs_wanted:

        for lab in all_labs:

            '''
            For each lab at each (train_PPV, vital_day), 
            write all stats (e.g. roc_auc, PPV, total cnts) into csv file. 
            '''
            try:
                stats_utils.lab2stats_csv(lab, all_algs, PPV_wanted,
                              folder_path, lab_folder, result_folder, columns,
                              thres_mode=thres_mode)
            except Exception as e:
                print e
                pass



def main_agg_stats(lab_type = 'component', vital_days = [3], PPVs_wanted = train_PPVs,
                   columns=None, thres_mode="from_test"):

    df_long = pd.DataFrame(columns=columns)

    columns_best_alg = [x if x!='alg' else 'best_alg' for x in columns]
    df_best_alg = pd.DataFrame(columns=columns_best_alg)

    result_folder = 'data_performance_stats/all_%ss/' % lab_type
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)

    for PPV_wanted in PPVs_wanted:
        for lab in all_labs:
            if thres_mode == "from_train":
                df_cur = pd.read_csv(result_folder + '%s-alg-summary-trainPPV-%s.csv'%(lab, str(PPV_wanted)), keep_default_na=False)
                df_cur['train_PPV'] = PPV_wanted
            elif thres_mode == "from_test":
                df_cur = pd.read_csv(result_folder + '%s-alg-summary-testPPV-%s.csv' % (
                lab, str(PPV_wanted)), keep_default_na=False)
                df_cur['test_PPV'] = PPV_wanted


            df_long = df_long.append(df_cur, ignore_index=True)

            df_cur_best_alg = df_cur.groupby(['lab'], as_index=False).agg({'roc_auc': 'max'})
            df_cur_best_alg = pd.merge(df_cur_best_alg, df_cur, on=['lab', 'roc_auc'], how='left')

            df_cur_best_alg = df_cur_best_alg.rename(columns={'alg': 'best_alg'})
            df_best_alg = df_best_alg.append(df_cur_best_alg)

    df_long[columns].to_csv('data_performance_stats/'+'long-%s-summary.csv'% lab_type, index=False)
    df_best_alg[columns_best_alg].to_csv('data_performance_stats/'+'best-alg-%s-summary-%s.csv'%(lab_type,thres_mode), index=False)

def main(lab_type='panel', thres_mode="trainPPV"):
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
    columns = ['lab', 'alg', 'roc_auc', '95%_CI', 'baseline_roc', 'total_cnt']
    columns += ['targeted %s'%thres_mode]
    columns += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']

    columns_STRIDE = columns[:]
    columns_STRIDE += ['%s count'%x for x in DEFAULT_TIMEWINDOWS]

    columns_panels = columns_STRIDE[:] + ['min_price', 'max_price', 'mean_price', 'median_price']
    # 'min_volume_charge', 'max_volume_charge', 'mean_volume_charge', 'median_volume_charge'
    columns_components = columns_STRIDE[:]

    columns_UMichs = columns[:]

    if lab_type == 'panel':
        columns = columns_panels
    elif lab_type == 'component':
        columns = columns_components
    elif lab_type == 'UMich':
        columns = columns_UMichs

    main_files_to_separate_stats(PPVs_wanted=train_PPVs,
                                 columns=columns, thres_mode=thres_mode)

    main_agg_stats(lab_type=lab_type, vital_days=[3], PPVs_wanted=train_PPVs, columns=columns,
                   thres_mode=thres_mode)

if __name__ == '__main__':
    main(lab_type='UMich', thres_mode="from_train")
    # fill_df_fix_PPV('LABAFBD', alg='random-forest', data_folder='../machine_learning/data-panels/',
    #                 PPV_wanted=0.99, lab_type="panel", thres_mode="from_train")
