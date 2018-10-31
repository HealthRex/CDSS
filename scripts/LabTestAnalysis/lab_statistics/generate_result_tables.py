

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option("display.max_columns", 10)
import numpy as np


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

def fill_df_fix_PPV(lab, alg, data_folder = '', PPV_wanted = 0.9, lab_type=None):

    if lab_type == 'panel':
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                     '%s-normality-prediction-%s-direct-compare-results.csv'%(lab,alg))
    elif lab_type == 'component':
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         '%s-component-normality-prediction-%s-direct-compare-results.csv' % (lab, alg))
    row, col = df.shape

    thres = get_thres_from_training_data_by_fixing_PPV(lab, alg, data_folder = data_folder, PPV_wanted = PPV_wanted)
    # thres = 0.5 # TODO: for quick test

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
        cnts_fees_dict[key] = cnts_fees_dict[key][0]

    one_lab_alg_dict.update(cnts_fees_dict)
    return one_lab_alg_dict

years = range(2010,2018,1)
def add_component_cnts_fees(one_lab_dict):
    component = one_lab_dict['lab']
    df_cnts = pd.read_csv('data_summary_stats/component_cnts.txt', sep='\t')
    # df = df.rename(columns={'Base':'lab'})



    for year in years:
        one_lab_dict[str(year)+'_Vol'] = df_cnts.ix[df_cnts['Base']==component, str(year)].values[0]
        # TODO: rename total_cnt to avoid confusion between total STRIDE cnt & testing cnt!

    df_fees = pd.read_csv('data_summary_stats/CLAB2018v1.csv', skiprows=3, sep=',')
    df_relevant = df_fees[df_fees['SHORTDESC'].str.lower().str.contains(component.lower())] #, 'RATE2018'

    one_lab_dict['rate_mean'] = df_relevant['RATE2018'].mean()
    one_lab_dict['rate_min'] = df_relevant['RATE2018'].min()
    one_lab_dict['rate_max'] = df_relevant['RATE2018'].max()
    one_lab_dict['rate_median'] = df_relevant['RATE2018'].median()

    one_lab_dict['typical_Vol'] = np.mean([one_lab_dict['2015_Vol'], one_lab_dict['2016_Vol']])
    one_lab_dict['PPV*Cost*Vol'] = one_lab_dict['typical_Vol'] * \
                                   one_lab_dict['typical_Vol'] * \
                                   one_lab_dict['PPV']

    one_lab_dict['RATEs2018'] = df_relevant['RATE2018'].values.tolist()
    one_lab_dict['SHORTDESCs'] = df_relevant['SHORTDESC'].values.tolist()

    return one_lab_dict

columns_components = ['lab', 'alg', 'roc_auc', 'total_cnt']  # basic info
columns_components += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
columns_components += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
columns_components += [str(year) + '_Vol' for year in years]
columns_components += ['rate_mean', 'rate_median', 'rate_min', 'rate_max']
columns_components += ['typical_Vol', 'PPV*Cost*Vol']
columns_components += ['RATEs2018', 'SHORTDESCs']

columns_panels = ['lab', 'alg', 'roc_auc', 'total_cnt']
columns_panels += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
columns_panels += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
columns_panels += ['count',
                    'min_price',
                    'max_price',
                    'mean_price',
                    'median_price',
                    'min_volume_charge',
                    'max_volume_charge',
                    'mean_volume_charge',
                    'median_volume_charge']

def test():
    folder_path = '../machine_learning/'
    all_data_folders = ['LabPanel_Predictions_3daysVitals', 'data_labpanel']
    data_folder = 'data_components'
    lab = 'ALB'
    all_algs = ['adaboost', 'decision-tree', 'gaussian-naive-bayes',
                'l1-logistic-regression-cross-validation', 'random-forest', 'regress-and-round']

    df_test = pd.DataFrame()
    columns = ['lab', 'alg'] # construct columns
    #, 'threshold', 'sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV'
    for alg in all_algs:
        one_lab_alg_dict = fill_df_fix_PPV(lab, alg, data_folder = folder_path+'/'+data_folder, PPV_wanted = 0.99)
        one_lab_alg_dict = add_component_cnts_fees(one_lab_alg_dict)

        df_test = df_test.append(one_lab_alg_dict, ignore_index=True)

    df_test[columns].to_csv('df_test.csv')

def main():
    folder_path = '../machine_learning/'
    # all_data_folders = ['LabPanel_Predictions_3daysVitals']

    lab_type = 'panel'

    if lab_type == 'panel':
        data_folder = 'data-LabNorm-3daysVitals' #'LabPanel_Predictions_3daysVitals'

        all_panels = [
            'LABA1C', 'LABAFBC', 'LABAFBD', 'LABALB', 'LABANER', 'LABB12', 'LABBLC', 'LABBLC2',
            'LABBLCSTK', 'LABBLCTIP', 'LABBUN', 'LABBXTG', 'LABCA', 'LABCAI', 'LABCDTPCR', 'LABCK',
            'LABCMVQT', 'LABCORT', 'LABCRP', 'LABCSFC', 'LABCSFGL', 'LABCSFTP', 'LABDIGL', 'LABESRP',
            'LABFCUL', 'LABFE', 'LABFER', 'LABFIB', 'LABFLDC', 'LABFOL', 'LABFT4', 'LABGRAM',
            'LABHAP', 'LABHBSAG', 'LABHCTX', 'LABHEPAR', 'LABHIVWBL', 'LABK', 'LABLAC', 'LABLACWB',
            'LABLDH', 'LABLIDOL', 'LABLIPS', 'LABMB', 'LABMGN',
            # 'LABNA',
            'LABNH3', 'LABNONGYN',
            'LABNTBNP', 'LABOSM', 'LABPALB', 'LABPCCG4O', 'LABPCCR', 'LABPCTNI', 'LABPHOS', 'LABPLTS',
            'LABPROCT', 'LABPT', 'LABPTEG', 'LABPTT', 'LABRESP', 'LABRESPG', 'LABRETIC', 'LABSPLAC',
            'LABSTLCX', 'LABSTOBGD', 'LABTNI', 'LABTRFS', 'LABTRIG', 'LABTSH', 'LABUCR', 'LABUOSM',
            'LABUA', 'LABUAPRN', 'LABUPREG', 'LABURIC', 'LABURNA', 'LABURNC', 'LABUSPG'
        ]
        columns = columns_panels
    else:
        all_panels = ['WBC', 'HGB', 'PLT', 'NA', 'K', 'CL',
                           'CR', 'BUN', 'GLU', 'CO2', 'CA', 'HCO3', # good, from 'LABMETB'
                            'TP', 'ALB', 'ALKP', 'TBIL', 'AST', 'ALT',
                           'DBIL', 'IBIL', 'PHA', 'PCO2A', 'PO2A']

        data_folder = 'data_components'
        columns = columns_components
    all_algs = ['adaboost', 'decision-tree', 'gaussian-naive-bayes',
                'l1-logistic-regression-cross-validation', 'random-forest', 'regress-and-round']

    PPVs_wanted = [0.99, 0.95, 0.90, 0.8]
    for PPV_wanted in PPVs_wanted:
        df = pd.DataFrame(
            columns=['lab', 'alg', 'threshold', 'sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV'])
        for lab in all_panels:
            for alg in all_algs:
                print 'Processing lab %s with alg %s'%(lab, alg)
                try:
                    one_lab_alg_dict = fill_df_fix_PPV(lab, alg, data_folder=folder_path + '/' + data_folder,
                                                       PPV_wanted=PPV_wanted, lab_type=lab_type)

                    if lab_type == 'component':
                        one_lab_alg_dict = add_component_cnts_fees(one_lab_alg_dict)
                    elif lab_type == 'panel':
                        one_lab_alg_dict = add_panel_cnts_fees(one_lab_alg_dict)
                    df = df.append(one_lab_alg_dict, ignore_index=True)
                except Exception as e:
                    print e
                    pass
        print 'PPV_wanted=%.2f finished!' % PPV_wanted

        df[columns].to_csv('lab-alg-summary-fix-PPV-%.2f-%s.csv'%(PPV_wanted,data_folder), index=False)

if __name__ == '__main__':
    main()