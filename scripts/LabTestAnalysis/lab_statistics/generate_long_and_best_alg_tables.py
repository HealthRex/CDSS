

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 10)
# Task 1: generate long table

percents = ['0.99', '0.95', '0.90', '0.80']

columns = [u'lab', u'alg', u'roc_auc', u'total_cnt',
           u'train_PPV', u'threshold', u'true_positive', u'false_positive', u'true_negative', u'false_negative', u'sensitivity', u'specificity', u'LR_p', u'LR_n', u'PPV', u'NPV', u'count', u'min_price', u'max_price', u'mean_price', u'median_price', u'min_volume_charge',
       u'max_volume_charge', u'mean_volume_charge', u'median_volume_charge']
df_long = pd.DataFrame(columns=columns)


columns_best_alg = [u'lab', u'best_alg', u'roc_auc', u'total_cnt',
           u'train_PPV', u'threshold', u'true_positive', u'false_positive', u'true_negative', u'false_negative', u'sensitivity', u'specificity', u'LR_p', u'LR_n', u'PPV', u'NPV', u'count', u'min_price', u'max_price', u'mean_price', u'median_price', u'min_volume_charge',
       u'max_volume_charge', u'mean_volume_charge', u'median_volume_charge']
df_best_alg = pd.DataFrame(columns=columns_best_alg)

do_panel = True
for percent in percents:
    if do_panel:
        lab_file = 'lab-alg-summary-fix-PPV-%s-LabPanel_Predictions_3daysVitals.csv'%(percent)
    else:
        lab_file = 'lab-alg-summary-fix-PPV-%s-data_components.csv' % (percent)
    df_cur = pd.read_csv(lab_file)
    df_cur['train_PPV'] = percent

    df_long = df_long.append(df_cur, ignore_index=True)

    df_cur_best_alg = df_cur.groupby(['lab'], as_index=False).agg({'roc_auc':'max'})
    df_cur_best_alg = pd.merge(df_cur_best_alg, df_cur, on=['lab','roc_auc'], how='left')

    df_cur_best_alg = df_cur_best_alg.rename(columns={'alg': 'best_alg'})
    df_best_alg = df_best_alg.append(df_cur_best_alg)


if do_panel:
    df_long[columns].to_csv('lab-alg-summary-fix-PPVs-long-LabPanel_Predictions_3daysVitals.csv')
    df_best_alg[columns_best_alg].to_csv('lab-alg-summary-fix-PPVs-best-alg-LabPanel_Predictions_3daysVitals.csv')
else:
    df_long[columns].to_csv('lab-alg-summary-fix-PPVs-long-data_components.csv')
    df_best_alg[columns_best_alg].to_csv('lab-alg-summary-fix-PPVs-best-alg-data_components.csv')