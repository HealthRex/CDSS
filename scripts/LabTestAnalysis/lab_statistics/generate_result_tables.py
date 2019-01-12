

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option("display.max_columns", 10)
import numpy as np
import os
from sklearn.metrics import roc_auc_score, roc_curve
import stats_utils

import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'

import LocalEnv
import matplotlib.pyplot as plt

train_PPVs = (0.99, 0.95, 0.9, 0.8) #[0.5, 0.75, 0.90, 0.95, 0.975, 0.99]

lab_type = stats_utils.lab_type
all_labs = stats_utils.all_labs
# labs_folder = stats_utils.labs_ml_folder
all_algs = stats_utils.all_algs

DEFAULT_TIMEWINDOWS = stats_utils.DEFAULT_TIMEWINDOWS


results_subfoldername = 'stats_by_lab_alg'
# results_subfolderpath = os.path.join(stats_utils.labs_stats_folder, results_subfoldername)
# if not os.path.exists(results_subfolderpath):
#     os.mkdir(results_subfolderpath)
results_filename_template = '%s-stats-target-%s-%s.csv'
# results_filepath_template = os.path.join(results_subfolderpath, results_filename_template)

summary_filename_template = 'summary-stats-%s-%s.csv'
# summary_filepath_template = os.path.join(stats_utils.labs_stats_folder, summary_filename_template)

'''
For each (train-)PPV wanted, each vital-day dataset
Create a summary of all algs' performances on all labs
'''
def main_labs2stats(train_data_folderpath, ml_results_folderpath, stats_results_folderpath, targeted_PPVs=train_PPVs, columns=None, thres_mode="fixTrainPPV"):

    for targeted_PPV in targeted_PPVs:
        for lab in all_labs:
            '''
            For each lab at each (train_PPV), 
            write all stats (e.g. AUROC, PPV, total cnts) into csv file. 
            '''
            stats_results_filename = results_filename_template%(lab, thres_mode, str(targeted_PPV))
            stats_results_filepath = os.path.join(stats_results_folderpath, 'stats_by_lab_alg', stats_results_filename)
            if not os.path.exists(os.path.join(stats_results_folderpath, 'stats_by_lab_alg')):
                os.mkdir(os.path.join(stats_results_folderpath, 'stats_by_lab_alg'))

            if not os.path.exists(stats_results_filepath):
                stats_utils.lab2stats(lab=lab,
                                      targeted_PPV=targeted_PPV,
                                      columns=columns,
                                      thres_mode=thres_mode,
                                      train_data_labfolderpath=os.path.join(train_data_folderpath, lab),
                                      ml_results_labfolderpath=os.path.join(ml_results_folderpath, lab),
                                      stats_results_filepath=stats_results_filepath
                                      )

def main_stats2summary(targeted_PPVs = train_PPVs, columns=None, thres_mode="fixTrainPPV"):

    df_long = pd.DataFrame(columns=columns)

    columns_best_alg = [x if x!='alg' else 'best_alg' for x in columns]
    df_best_alg = pd.DataFrame(columns=columns_best_alg)

    for targeted_PPV in targeted_PPVs:
        for lab in all_labs:
            stats_results_filename = results_filename_template % (lab, thres_mode, str(targeted_PPV))
            stats_results_filepath = os.path.join(stats_results_folderpath, 'stats_by_lab_alg', stats_results_filename)
            # results_filepath = results_filepath_template % (lab, thres_mode, str(targeted_PPV))
            df_lab = pd.read_csv(stats_results_filepath, keep_default_na=False)
            df_lab['targeted_PPV_%s'%thres_mode] = targeted_PPV

            df_long = df_long.append(df_lab, ignore_index=True)

            df_cur_best_alg = df_lab.groupby(['lab'], as_index=False).agg({'AUROC': 'max'})
            df_cur_best_alg = pd.merge(df_cur_best_alg, df_lab, on=['lab', 'AUROC'], how='left')

            df_cur_best_alg = df_cur_best_alg.rename(columns={'alg': 'best_alg'})
            df_best_alg = df_best_alg.append(df_cur_best_alg)

    summary_long_filename = 'summary-stats-%s-%s.csv'%('allalgs', thres_mode)
    summary_long_filepath = os.path.join(stats_results_folderpath, summary_long_filename)
    df_long[columns].to_csv(summary_long_filepath, index=False)

    summary_best_filename = 'summary-stats-%s-%s.csv'%('bestalg', thres_mode)
    summary_best_filepath = os.path.join(stats_results_folderpath, summary_best_filename)
    df_best_alg[columns_best_alg].to_csv(summary_best_filepath, index=False)

    # df_long[columns].to_csv(summary_filepath_template%('allalgs', thres_mode), index=False)
    # df_best_alg[columns_best_alg].to_csv(summary_filepath_template%('bestalg', thres_mode), index=False)

def main(train_data_folderpath, ml_results_folderpath, stats_results_folderpath, thres_mode="fixTrainPPV"):
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
    columns = ['lab', 'num_train_episodes', 'num_train_patient', 'num_test_episodes', 'num_test_patient']
    columns += ['alg', 'AUROC', '95%_CI', 'baseline2_ROC']
    columns += ['targeted_PPV_%s' % thres_mode]

    columns_statsMetrics = []
    columns_statsMetrics += ['score_thres', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns_statsMetrics += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']

    columns += columns_statsMetrics

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

    main_labs2stats(train_data_folderpath=train_data_folderpath,
                    ml_results_folderpath=ml_results_folderpath,
                    stats_results_folderpath=stats_results_folderpath,
                    targeted_PPVs=train_PPVs,
                                 columns=columns,
                                 thres_mode=thres_mode)

    main_stats2summary(targeted_PPVs=train_PPVs,
                   columns=columns,
                   thres_mode=thres_mode)

    main_attachBaseline(targeted_PPVs=train_PPVs,
                   columns=[x+'_baseline' for x in columns_statsMetrics],
                   thres_mode=thres_mode)

def main_attachBaseline(targeted_PPVs, columns, thres_mode):
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
    print df_best_alg.head()

    '''
    Get Baseline results for each lab
    '''

    print columns



if __name__ == '__main__':
    project_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
    train_data_folderpath = os.path.join(project_folder, 'machine_learning/',
                                         'data-%s-%s-10000-episodes'%(stats_utils.data_source, stats_utils.lab_type)
                                         )
    ml_results_folderpath = os.path.join(project_folder, 'machine_learning/',
                                   #'results-from-panels-10000-to-panels-5000-part-1'
                                         'data-%s-%s-10000-episodes'%(stats_utils.data_source, stats_utils.lab_type)
                                         )
    stats_results_folderpath = ml_results_folderpath.replace('machine_learning/', 'lab_statistics/')

    if not os.path.exists(stats_results_folderpath):
        os.mkdir(stats_results_folderpath)

    main(train_data_folderpath=train_data_folderpath,
         ml_results_folderpath=ml_results_folderpath,
         stats_results_folderpath=stats_results_folderpath,
         thres_mode="fixTrainPPV")
    # fill_df_fix_PPV('LABAFBD', alg='random-forest', data_folder='../machine_learning/data-panels/',
    #                 PPV_wanted=0.99, lab_type="panel", thres_mode="from_train")
