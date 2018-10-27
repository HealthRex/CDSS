

import pandas as pd
pd.set_option('display.width', 300)
import numpy as np


MAX_VAL = 10000. # TODO: replace this with NA


# def fill_df_fix_thres(lab, alg, thres = 0.5):
#
#
#     df = pd.read_csv(lab + '/' + alg + '/' +
#                      '%s-normality-prediction-%s-direct-compare-results.csv'%(lab,alg))
#
#     # TODO: calibration?
#
#     df['predict_class'] = df['predict'].apply(lambda x: 1 if x>thres else 0)
#     row, col = df.shape
#
#     actual_list = df['actual'].values.tolist()
#     predict_class_list = df['predict_class'].values.tolist()
#
#     true_positive = 0
#     false_positive = 0
#     true_negative = 0
#     false_negative = 0
#     for i in range(row):
#         if actual_list[i] == 1 and predict_class_list[i] == 1:
#             true_positive += 1
#         elif actual_list[i] == 0 and predict_class_list[i] == 1:
#             false_positive += 1
#         elif actual_list[i] == 1 and predict_class_list[i] == 0:
#             false_negative += 1
#         elif actual_list[i] == 0 and predict_class_list[i] == 0:
#             true_negative += 1
#         else:
#             print "what?!"
#
#     res = {'lab':lab, 'alg':alg}
#     res['sensitivity'] = float(true_positive)/float(true_positive + false_negative)
#     res['specificity'] = float(true_negative)/float(true_negative + false_positive)
#     try:
#         res['LR_p'] = res['sensitivity']/(1-res['specificity'])
#     except ZeroDivisionError:
#         if res['sensitivity'] == 0:
#             res['LR_p'] = float('nan')
#         else:
#             res['LR_p'] = MAX_VAL
#
#     try:
#         res['LR_n'] = (1-res['sensitivity'])/res['specificity']
#     except ZeroDivisionError:
#         if res['sensitivity'] == 1:
#             res['LR_n'] = float('nan')
#         else:
#             res['LR_n'] = MAX_VAL
#
#     try:
#         res['PPV'] = float(true_positive)/float(true_positive + false_positive)
#     except ZeroDivisionError:
#         res['PPV'] = float('nan')
#
#     try:
#         res['NPV'] = float(true_negative)/float(true_negative + false_negative)
#     except ZeroDivisionError:
#         res['PPV'] = float('nan')
#     return res

def get_thres_from_training_data_by_fixing_PPV(lab, alg, data_folder = '', PPV_wanted = 0.9):
    if 'component' not in data_folder:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                     '%s-normality-prediction-%s-direct-compare-results-traindata.csv'%(lab,alg))
    else:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         '%s-component-normality-prediction-%s-direct-compare-results-traindata.csv' % (lab, alg))

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

def fill_df_fix_PPV(lab, alg, data_folder = '', PPV_wanted = 0.9):

    if 'component' not in data_folder:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                     '%s-normality-prediction-%s-direct-compare-results.csv'%(lab,alg))
    else:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         '%s-component-normality-prediction-%s-direct-compare-results.csv' % (lab, alg))
    row, col = df.shape

    # thres = get_thres_from_training_data_by_fixing_PPV(lab, alg, data_folder = data_folder, PPV_wanted = 0.9)
    thres = 0.5 # TODO: for quick test

    actual_list = df['actual'].values.tolist()

    from sklearn.metrics import roc_auc_score
    roc_auc = roc_auc_score(actual_list, df['predict'].values)

    df['predict_class'] = df['predict'].apply(lambda x: 1 if x > thres else 0)
    predict_class_list = df['predict_class'].values.tolist()


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

    res = {'lab':lab, 'alg':alg, 'threshold': thres,
           'true_positive':true_positive, 'false_positive': false_positive,
           'true_negative':true_negative, 'false_negative':false_negative,
           'total_cnt':total_cnt, 'roc_auc': roc_auc}
    res['sensitivity'] = float(true_positive)/float(true_positive + false_negative)
    res['specificity'] = float(true_negative)/float(true_negative + false_positive)
    try:
        res['LR_p'] = res['sensitivity']/(1-res['specificity'])
    except ZeroDivisionError:
        if res['sensitivity'] == 0:
            res['LR_p'] = float('nan')
        else:
            res['LR_p'] = float('inf')

    try:
        res['LR_n'] = (1-res['sensitivity'])/res['specificity']
    except ZeroDivisionError:
        if res['sensitivity'] == 1:
            res['LR_n'] = float('nan')
        else:
            res['LR_n'] = float('inf')

    try:
        res['PPV'] = float(true_positive)/float(true_positive + false_positive)
    except ZeroDivisionError:
        res['PPV'] = float('nan')

    try:
        res['NPV'] = float(true_negative)/float(true_negative + false_negative)
    except ZeroDivisionError:
        res['PPV'] = float('nan')
    return res

def add_cnts_fees(one_row):
    component = one_row['lab']
    df = pd.read_csv('data_summary_stats/component_cnts.txt', sep='\t')

    cnt = df.ix[df['Base']==component, '2015'].values[0]

    df = pd.read_csv('data_summary_stats/CLAB2018v1.csv', skiprows=3, sep=',')
    fees = df.ix[df['SHORTDESC'].str.lower().str.contains(component.lower()), 'RATE2018']
    print fees
    print component, cnt, fees.mean(), fees.std()
    quit()
    return one_row

def test():
    folder_path = '../machine_learning/'
    all_data_folders = ['LabPanel_Predictions_3daysVitals', 'data_labpanel']
    data_folder = 'data_components'
    lab = 'ALB'
    all_algs = ['adaboost', 'decision-tree', 'gaussian-naive-bayes',
                'l1-logistic-regression-cross-validation', 'random-forest', 'regress-and-round']
    for alg in all_algs:
        res = fill_df_fix_PPV(lab, alg, data_folder = folder_path+'/'+data_folder, PPV_wanted = 0.99)
        res = add_cnts_fees(res)
        quit()

def main():
    all_panels = [
        'LABA1C', 'LABAFBC', 'LABAFBD', 'LABALB', 'LABANER', 'LABB12', 'LABBLC', 'LABBLC2',
        'LABBLCSTK', 'LABBLCTIP', 'LABBUN', 'LABBXTG', 'LABCA', 'LABCAI', 'LABCDTPCR', 'LABCK',
        'LABCMVQT', 'LABCORT', 'LABCRP', 'LABCSFC', 'LABCSFGL', 'LABCSFTP', 'LABDIGL', 'LABESRP',
        'LABFCUL', 'LABFE', 'LABFER', 'LABFIB', 'LABFLDC', 'LABFOL', 'LABFT4', 'LABGRAM',
        'LABHAP', 'LABHBSAG', 'LABHCTX', 'LABHEPAR', 'LABHIVWBL', 'LABK', 'LABLAC', 'LABLACWB',
        'LABLDH', 'LABLIDOL', 'LABLIPS', 'LABMB', 'LABMGN', 'LABNA', 'LABNH3', 'LABNONGYN',
        'LABNTBNP', 'LABOSM', 'LABPALB', 'LABPCCG4O', 'LABPCCR', 'LABPCTNI', 'LABPHOS', 'LABPLTS',
        'LABPROCT', 'LABPT', 'LABPTEG', 'LABPTT', 'LABRESP', 'LABRESPG', 'LABRETIC', 'LABSPLAC',
        'LABSTLCX', 'LABSTOBGD', 'LABTNI', 'LABTRFS', 'LABTRIG', 'LABTSH', 'LABUCR', 'LABUOSM',
        'LABUA', 'LABUAPRN', 'LABUPREG', 'LABURIC', 'LABURNA', 'LABURNC', 'LABUSPG'
    ]
    all_algs = ['adaboost', 'decision-tree', 'gaussian-naive-bayes',
                'l1-logistic-regression-cross-validation', 'random-forest', 'regress-and-round']

    PPVs_wanted = [0.99, 0.95, 0.90, 0.8]
    for PPV_wanted in PPVs_wanted:
        df = pd.DataFrame(
            columns=['lab', 'alg', 'threshold', 'sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV'])
        for lab in all_panels:
            for alg in all_algs:
                try:
                    one_row = fill_df_fix_PPV(lab, alg, PPV_wanted=PPV_wanted)
                    df = df.append(one_row, ignore_index=True)
                except Exception as e:
                    print e
                    pass
        print 'PPV_wanted=%.2f finished!' % PPV_wanted
        df.to_csv('lab-alg-summary-fix-PPV-%.2f.csv' % PPV_wanted, index=False)

def test_CLAB():
    df = pd.read_csv('data_summary_stats/CLAB2018v1.csv', skiprows=3, sep=',')
    print df.ix[df['SHORTDESC'].str.lower().str.contains('wbc'), 'RATE2018'].mean() #

if __name__ == '__main__':
    test()