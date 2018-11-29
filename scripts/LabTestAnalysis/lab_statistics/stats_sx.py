
import os
import stats_utils
import datetime
import collections
import pandas as pd

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from medinfo.ml.SupervisedClassifier import SupervisedClassifier

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline \
    import NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS


def plot_NormalRate__bar(lab_type="panel"):
    '''
    Horizontal bar chart for Popular labs.
    '''

    df = pd.read_csv('data_performance_stats/best-alg-%s-summary.csv' % lab_type)
    df['normal_rate'] = (df['true_positive'] + df['false_negative']).round(5)

    if lab_type == "component":
        df = df.rename(columns={'2016_Vol': 'count'})
        df = df.dropna()
    df['count_scaled'] = df['count'].apply(lambda x: x / 1000000.)

    '''
    Picking the top 20 popular labs.
    '''
    df_sorted_by_cnts = df.sort_values('count_scaled', ascending=False).ix[:,
                        ['lab', 'normal_rate', 'count_scaled']].drop_duplicates().head(20).copy()
    df_sorted_by_cnts = df_sorted_by_cnts.sort_values('count_scaled', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['normal_rate'], color='blue', label='Normal Rate')
    for i, v in enumerate(df_sorted_by_cnts['normal_rate']):
        ax.text(v + 0.01, i, str("{0:.0%}".format(v)), color='k', fontweight='bold')

    ax.barh(df_sorted_by_cnts['lab'], df_sorted_by_cnts['count_scaled'], color='grey', alpha=0.5,
            label='Total Cnt (in millions) in 2016')

    plt.xlim([0, 1])
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(14)

    plt.legend()
    plt.show()

def get_LabUsage__csv():
    '''
    Overuse of labs figure.
    '''
    data_file = 'A1C_Usage_2016.csv'

    if not os.path.exists(data_file):
        results = stats_utils.query_lab_usage__df(lab='LABA1C',
                                                  time_start='2016-01-01',
                                                  time_end='2016-12-31')
        df = pd.DataFrame(results, columns=['pat_id', 'order_time', 'result'])
        df.to_csv(data_file, index=False)
    else:
        df = pd.read_csv(data_file)

    prevday_cnts_dict = stats_utils.get_prevday_cnts__dict(df)

    print 'total cnt:', df.shape[0]
    print 'repetitive cnt:', sum(prevday_cnts_dict.values())
    print 'within 24 hrs:', prevday_cnts_dict[0]
    print 'within 48 hrs:', prevday_cnts_dict[1]

def plot_curves(lab_type='component', curve_type="roc"):

    if lab_type == 'panel':
        data_folder = '../machine_learning/data-panels/'
        df = pd.read_csv('RF_important_features_panels.csv', keep_default_na=False)
    elif lab_type == 'component':
        data_folder = '../machine_learning/data-components/'
        df = pd.read_csv('RF_important_features_components.csv', keep_default_na=False)

    labs = df.sort_values('score 1', ascending=False)['lab'].values.tolist()[:15]
    print labs

    plt.figure(figsize=(8, 12))
    for i in range(5):
        for j in range(3):
            ind = i * 3 + j
            lab = labs[ind]

            plt.subplot2grid((5, 3), (i, j))

            #fpr_base, tpr_base, base_auc, fpr, tpr, best_auc \
            '''
            For precision-recall curve, the output are:
                fpr_base, tpr_base, base_auc, 
                fpr, tpr, best_auc.
            For roc curve, the output are:
                recall_base, precision_base, base_auc, 
                fpr, tpr, best_auc
            '''
            xVal_base, yVal_base, score_base, xVal_best, yVal_best, score_best  \
                = stats_utils.get_curve_onelab(lab,
                                            all_algs=SupervisedClassifier.SUPPORTED_ALGORITHMS,
                                            data_folder=data_folder,
                                            curve_type=curve_type)

            plt.plot(xVal_base, yVal_base, label='%0.2f' % (score_base))
            plt.plot(xVal_best, yVal_best, label='%0.2f' % (score_best))

            plt.xticks([])
            plt.yticks([])
            plt.xlabel(lab)  # + ' ' + str(best_auc)[:4] + ' ' + str(base_auc)[:4]
            plt.legend()

    plt.show()

def plot_cartoons():
    df = pd.read_csv('RF_important_features_panels.csv', keep_default_na=False)
    labs = df.sort_values('score 1', ascending=False)['lab'].values.tolist()[:15]
    print labs
    plt.figure(figsize=(8, 12))

    lab = 'WBC'
    alg = 'random-forest'

    data_folder = "../machine_learning/data-panels/"

    for i in range(5):
        for j in range(3):
            ind = i * 3 + j
            lab = labs[ind]

            df = pd.read_csv(data_folder + "%s/%s/%s-normality-prediction-%s-direct-compare-results.csv"
                             % (lab, alg, lab, alg), keep_default_na=False)
            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            df1 = pd.read_csv(data_folder + "%s/%s/%s-normality-prediction-%s-report.tab"
                              % (lab, alg, lab, alg), sep='\t', keep_default_na=False)
            auc = df1['roc_auc'].values[0]

            plt.subplot2grid((5, 3), (i, j))
            plt.hist(scores_actual_0, bins=30, alpha=0.8, color='r', label="abnormal")
            plt.hist(scores_actual_1, bins=30, alpha=0.8, color='g', label="normal")
            plt.xlim([0, 1])
            plt.ylim([0, 500])
            plt.xticks([])
            plt.yticks([])
            plt.xlabel(lab)
            # plt.legend(lab)

    # plt.xlabel("%s score for %s"%(alg,lab))
    # plt.ylabel("num episodes, auroc=%f"%auc)
    # plt.legend()

    plt.savefig('cartoons_panels.png')


def write_importantFeatures():
    all_rows = []
    num_rf_best = 0

    for lab in STRIDE_COMPONENT_TESTS:
        df = pd.read_csv(
            '../machine_learning/data-components/%s/%s-normality-prediction-report.tab'
            %(lab,lab), sep='\t', skiprows=1)

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
    result_df.to_csv('RF_important_features_components.csv', index=False)

def print_HosmerLemeshowTest():
    labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
    alg = 'random-forest'  # 'regress-and-round' #'random-forest'

    p_vals = []

    for lab in labs:
        df_new = pd.read_csv(
            '../machine_learning/data-panels-calibration-sigmoid/%s/%s/%s-normality-prediction-%s-direct-compare-results.csv'
            % (lab, alg, lab, alg))
        actual = df_new['actual'].values
        predict = df_new['predict'].values
        p_val = stats_utils.Hosmer_Lemeshow_Test(actual_labels=actual, predict_probas=predict)
        p_vals.append(p_val)

    print sorted(p_vals)

if __name__ == '__main__':
    plot_curves(lab_type='panel', curve_type="prc")