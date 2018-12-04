

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
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import \
        NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS

train_PPVs = [0.99, 0.95, 0.9, 0.8] #[0.5, 0.75, 0.90, 0.95, 0.975, 0.99]

all_panels = NON_PANEL_TESTS_WITH_GT_500_ORDERS
all_components = STRIDE_COMPONENT_TESTS #['WBC', 'HGB', 'K', 'NA', 'CR', 'GLU'] #STRIDE_COMPONENT_TESTS
all_UMich = ['WBC', 'HGB',
                'PLT', 'SOD', 'POT', 'CREAT', 'TBIL', 'CHLOR', 'CO2',
                'AST', 'ALT',
            'ALB', 'CAL',
            'PO2AA', 'PCOAA2']
all_algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

'''
For each (train-)PPV wanted, each vital-day dataset
Create a summary of all algs' performances on all labs
'''
def main_files_to_separate_stats(lab_type = 'component', years=[2016], vital_days = [3],
                                 PPVs_wanted = train_PPVs,
                                columns = None, thres_mode="from_test"):

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




        for PPV_wanted in PPVs_wanted:

            for lab in all_labs:

                '''
                For each lab at each (train_PPV, vital_day), 
                write all stats (e.g. roc_auc, PPV, total cnts) into csv file. 
                '''
                try:
                    stats_utils.lab2stats_csv(lab_type, lab, years, all_algs, PPV_wanted,
                                  vital_day, folder_path, data_folder, result_folder, columns,
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

    if lab_type == 'panel':
        all_labs = all_panels
    elif lab_type == 'component':
        all_labs = all_components
    elif lab_type == 'UMich':
        all_labs = all_UMich

    for PPV_wanted in PPVs_wanted:
        for vital_day in vital_days: #TODO: create the column of vitals
            for lab in all_labs:
                if thres_mode == "from_train":
                    df_cur = pd.read_csv(result_folder + '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv'%(lab, str(PPV_wanted), vital_day), keep_default_na=False)
                    df_cur['train_PPV'] = PPV_wanted
                elif thres_mode == "from_test":
                    df_cur = pd.read_csv(result_folder + '%s-alg-summary-testPPV-%s-vitalDays-%d.csv' % (
                    lab, str(PPV_wanted), vital_day), keep_default_na=False)
                    df_cur['test_PPV'] = PPV_wanted

                df_cur['vital_day'] = vital_day


                df_long = df_long.append(df_cur, ignore_index=True)

                df_cur_best_alg = df_cur.groupby(['lab'], as_index=False).agg({'roc_auc': 'max'})
                df_cur_best_alg = pd.merge(df_cur_best_alg, df_cur, on=['lab', 'roc_auc'], how='left')

                df_cur_best_alg = df_cur_best_alg.rename(columns={'alg': 'best_alg'})
                df_best_alg = df_best_alg.append(df_cur_best_alg)

    df_long[columns].to_csv('data_performance_stats/'+'long-%s-summary.csv'% lab_type, index=False)
    df_best_alg[columns_best_alg].to_csv('data_performance_stats/'+'best-alg-%s-summary-%s.csv'%(lab_type,thres_mode), index=False)

def main(lab_type='panel', thres_mode="from_test"):


    columns_panels = ['lab', 'alg', 'roc_auc', '95%_CI', 'baseline_roc', 'total_cnt']
    columns_panels += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns_panels += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
    columns_panels += ['count', 'min_price', 'max_price', 'mean_price', 'median_price',
                       'min_volume_charge', 'max_volume_charge', 'mean_volume_charge', 'median_volume_charge']

    if thres_mode == "from_train":
        wanted_PPV_col = 'train_PPV'
    elif thres_mode == "from_test":
        wanted_PPV_col = 'test_PPV'
    # TODO: Finish the panel routine, but first deal with the NA 2015 issue?
    columns_panels_agg = columns_panels[:6] + ['vital_day', wanted_PPV_col] + columns_panels[6:]

    years = [2016]  # which years' cnt to look at
    columns_components = ['lab', 'alg', 'roc_auc', '95%_CI', 'baseline_roc', 'total_cnt']  # basic info
    columns_components += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns_components += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
    columns_components += [str(year) + '_Vol' for year in years]

    columns_components_agg = columns_components[:6] + ['vital_day', wanted_PPV_col] + columns_components[6:]

    if lab_type == 'panel':
        columns = columns_panels
        columns_agg = columns_panels_agg
    else:
        columns = columns_components
        columns_agg = columns_components_agg

    main_files_to_separate_stats(lab_type=lab_type, years=[2016], vital_days=[3], PPVs_wanted=train_PPVs,
                                 columns=columns, thres_mode=thres_mode)

    main_agg_stats(lab_type=lab_type, vital_days=[3], PPVs_wanted=train_PPVs, columns=columns_agg,
                   thres_mode=thres_mode)

if __name__ == '__main__':
    main(lab_type='component', thres_mode="from_test")
    # fill_df_fix_PPV('LABAFBD', alg='random-forest', data_folder='../machine_learning/data-panels/',
    #                 PPV_wanted=0.99, lab_type="panel", thres_mode="from_train")
