
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
import datetime, collections
from sklearn.metrics import roc_auc_score, roc_curve
import pandas as pd
import numpy as np
from scipy import stats

def query_lab_usage__df(lab, time_start=None, time_end=None):
    # TODO: deal with lab_type == component?

    query = SQLQuery()
    query.addSelect('CAST(pat_id AS BIGINT) as pat_id')
    # query.addSelect('order_proc_id')
    query.addSelect('order_time')
    query.addSelect('abnormal_yn')
    # query.addSelect("CAST(SUM(CASE WHEN result_flag IN ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') THEN 1 ELSE 0 END) = 0 AS INT) AS all_components_normal")

    query.addFrom('stride_order_proc')

    query.addWhere("order_status = 'Completed'")
    query.addWhere("proc_code = '%s'"%lab)

    if time_start:
        query.addWhere("order_time > '%s'"%time_start)
    if time_end:
        query.addWhere("order_time < '%s'"% time_end)
    # query.addWhere("order_time > '2016-01-01' AND order_time < '2016-12-31'")
    # query.addWhere("(result_flag in ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') OR result_flag IS NULL)")

    query.addGroupBy('pat_id')
    # query.addGroupBy('order_proc_id')
    query.addGroupBy('order_time')
    query.addGroupBy('abnormal_yn')

    query.addOrderBy('pat_id')
    # query.addOrderBy('order_proc_id')
    query.addOrderBy('order_time')

    results = DBUtil.execute(query)


    return results


def get_prevday_cnts__dict(df):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    '''
    Cnt of ordering w/i one day
    '''
    df['prev_in_sec'] = df['pat_id'].apply(lambda x: 1000 * 24 * 3600)
    df['order_time'] = df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format))

    prev_days = []
    row, col = df.shape
    for i in range(1, row):
        if df.ix[i, 'pat_id'] == df.ix[i - 1, 'pat_id']:
            time_diff_df = df.ix[i, 'order_time'] - df.ix[i - 1, 'order_time']

            # df.ix[i, 'prev_in_sec'] = time_diff_df.seconds
            # a day has 86400 secs
            # prev_days.append(time_diff_df.seconds/86400.)
            prev_days.append(time_diff_df.days) # TODO: ceiling of days?

    prevday_cnts_dict = collections.Counter(prev_days)

    return prevday_cnts_dict

def get_roc_onelab(lab, all_algs, data_folder):
    # curr_res_file = '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv' % (lab, str(PPV_wanted), vital_day)

    '''
    Baseline curve
    '''

    df = pd.read_csv(data_folder + '/' + lab + '/' + 'baseline_comparisons.csv')
    base_actual = df['actual'].values
    base_auc = roc_auc_score(base_actual, df['predict'].values)
    base_predict = df['predict'].values

    fpr_base, tpr_base, threshold_base = roc_curve(base_actual, base_predict)

    '''
    best alg
    '''
    best_auc = 0
    best_alg = None
    best_actual = None
    best_predict = None
    for alg in all_algs:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         '%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg))
        actual_list = df['actual'].values
        try:
            cur_auc = roc_auc_score(actual_list, df['predict'].values)
        except ValueError:
            cur_auc = float('nan')
        if cur_auc > best_auc:
            best_auc = cur_auc
            best_alg = alg
            best_actual = actual_list
            best_predict = df['predict'].values

    fpr, tpr, threshold = roc_curve(best_actual, best_predict)

    return fpr_base, tpr_base, base_auc, fpr, tpr, best_auc

def split_features(feature):
    divind = feature.find('(')
    featu = feature[:divind - 1]
    score = feature[divind + 1:-1]
    return featu, score


def Hosmer_Lemeshow_Test(predict_probas, actual_labels, num_bins=10):
    # assert between 0 and 1
    minor_shift = 0.00001
    predict_probas_shifted = [max(min(x, 1 - minor_shift), minor_shift) for x in predict_probas]

    bins = np.linspace(0, 1, num=num_bins+1)
    inds = np.digitize(predict_probas_shifted, bins)

    num_rows = len(predict_probas)

    '''
    Minor adjust
    '''

    '''
    Put data inds into bins
    TODO: when proba = 1, it is in the 11-th bin
    '''
    inds_in_bins = [[] for _ in range(num_bins+2)]
    # (-inf,0), (0,1), ..., (9,10), (10,+inf)
    for i in range(num_rows):
        inds_in_bins[inds[i]].append(i)


    mids = (bins[1:] + bins[:-1]) / 2.

    e1_s, o1_s = [], []
    e0_s, o0_s = [], []
    H_stat = 0
    dof = num_bins - 2
    for i in range(1,len(inds_in_bins)-1):
        # if not inds_in_bins[i]:
        #     dof -= 1
        #     continue

        e1 = len(inds_in_bins[i]) * mids[i-1]
        e1_s.append(e1)

        e0 = len(inds_in_bins[i]) * (1.-mids[i-1])
        e0_s.append(e0)

        o1 = 0
        o0 = 0
        for j in inds_in_bins[i]:
            if actual_labels[j] == 1:
                o1 += 1
            else:
                o0 += 1
        o1_s.append(o1)
        o0_s.append(o0)

        H_stat += (o1-e1)**2/float(e1) + (o0-e0)**2/float(e0)


    return 1 - stats.chi2.cdf(H_stat, dof)