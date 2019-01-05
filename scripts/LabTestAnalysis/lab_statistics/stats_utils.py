
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
import datetime, collections
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)
import numpy as np
from scipy import stats
import os, sys

import LocalEnv

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline \
        import NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS, UMICH_TOP_COMPONENTS, UCSF_TOP_COMPONENTS
from medinfo.ml.SupervisedClassifier import SupervisedClassifier

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

'''
For each lab, get a bunch of stuff
'''

'''
For plotting guideline,

a lab, has n prev consecutive normal. 
'''

lab_type = 'panel'

all_panels = NON_PANEL_TESTS_WITH_GT_500_ORDERS
all_components = STRIDE_COMPONENT_TESTS
all_UMichs = UMICH_TOP_COMPONENTS
all_UCSF = UCSF_TOP_COMPONENTS
all_algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

DEFAULT_TIMELIMIT = ('2014-07-01', '2017-06-30')

DEFAULT_TIMESPAN = ('2014-01-01', '2017-06-30')
DEFAULT_TIMEWINDOWS = ['2014 1stHalf', '2014 2stHalf',
                       '2015 1stHalf', '2015 2stHalf',
                       '2016 1stHalf', '2016 2stHalf',
                       '2017 1stHalf']
DEFAULT_TIMELIMITS = []
for time_window in DEFAULT_TIMEWINDOWS:
    year_str, section_str = time_window.split(' ')

    if section_str == '1stHalf':
        section_timestamps = ('01-01', '06-30')
    else:
        section_timestamps = ('07-01', '12-31')

    time_limit = ['-'.join([year_str, x]) for x in section_timestamps]

    DEFAULT_TIMELIMITS.append(time_limit)

main_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')

curr_version = '10000-episodes'
if lab_type == 'panel':
    all_labs = all_panels #[x[0] for x in labs_and_cnts]
elif lab_type == 'component':
    all_labs = all_components
elif lab_type == 'UMich':
    all_labs = all_UMichs
elif lab_type == 'UCSF':
    all_labs = all_UCSF


# labs_ml_folder = os.path.join(main_folder, 'machine_learning/data-%ss-%s/'%(lab_type, curr_version))
# labs_stats_folder = os.path.join(main_folder, 'lab_statistics/stats-%ss-%s/'%(lab_type, curr_version))
labs_old_stats_folder = os.path.join(main_folder, 'lab_statistics/data_summary_stats/')
labs_query_folder = os.path.join(main_folder, 'lab_statistics/query_lab_results/')


# if not os.path.exists(labs_folder):
#     os.mkdir(labs_folder)
# if not os.path.exists(labs_stats_folder):
#     os.mkdir(labs_stats_folder)


def query_lab_usage__df(lab, lab_type='panel', time_limit=None):
    if time_limit:
        time_start, time_end = time_limit[0], time_limit[1]
    # TODO: deal with lab_type == component?

    if lab_type=='panel':
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

    elif lab_type=='component': # TODO!
        query = SQLQuery()
        query.addSelect('CAST(pat_id AS BIGINT) as pat_id')
        # query.addSelect('order_proc_id')
        query.addSelect('sop.order_time')
        query.addSelect('sor.result_in_range_yn')
        # query.addSelect("CAST(SUM(CASE WHEN result_flag IN ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') THEN 1 ELSE 0 END) = 0 AS INT) AS all_components_normal")

        query.addFrom('stride_order_proc as sop')
        query.addFrom('stride_order_results as sor')

        query.addWhere('sop.order_proc_id = sor.order_proc_id')
        query.addWhere("sop.order_status = 'Completed'")
        query.addWhere("sor.base_name = '%s'" % lab)

        if time_start:
            query.addWhere("sop.order_time > '%s'" % time_start)
        if time_end:
            query.addWhere("sop.order_time < '%s'" % time_end)
        # query.addWhere("order_time > '2016-01-01' AND order_time < '2016-12-31'")
        # query.addWhere("(result_flag in ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') OR result_flag IS NULL)")

        query.addGroupBy('sop.pat_id')
        # query.addGroupBy('order_proc_id')
        query.addGroupBy('sop.order_time')
        query.addGroupBy('sor.result_in_range_yn')

        query.addOrderBy('sop.pat_id')
        # query.addOrderBy('order_proc_id')
        query.addOrderBy('sop.order_time')

    results = DBUtil.execute(query)

    return results

def get_prevweek_normal__dict(df, also_get_cnt=False):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    '''
    Cnt of ordering w/i one day
    '''
    df['prev_in_sec'] = df['pat_id'].apply(lambda x: 1000 * 24 * 3600) # 1000 days
    df['order_time'] = df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)
                                if isinstance(x, str) else x)

    df = df.sort_values(['pat_id', 'order_time'])
    df = df.reset_index(drop=True)

    row, col = df.shape
    day2norms = {}
    '''
    key: num of CONSECUTIVE normal in past week. val: [normal, normal, abnormal...]
    '''
    for i in range(1, row):
        curr_normal = 0 if df.ix[i, 'abnormal_yn'] == 'Y' else 1

        j = i-1
        while j >= 0 \
            and df.ix[i,'pat_id'] == df.ix[j,'pat_id'] \
            and (df.ix[i,'order_time'] - df.ix[j,'order_time']).days < 7 \
            and df.ix[j,'abnormal_yn'] != 'Y':

            j -= 1

        prev_cnt = i-1-j
        if prev_cnt in day2norms:
            day2norms[prev_cnt].append(curr_normal)
        else:
            day2norms[prev_cnt] = [curr_normal]

    return day2norms



            # df.ix[i, 'prev_in_sec'] = time_diff_df.seconds
            # a day has 86400 secs
            # prev_days.append(time_diff_df.seconds/86400.)

def get_time_since_last_order_cnts(lab, df):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    # print df.head()
    '''
    Cnt of ordering w/i one day
    '''
    df['prev_in_day'] = df['pat_id'].apply(lambda x: -1)
    df['order_time'] = df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)
                                              if isinstance(x, str) else x)
    df = df.sort_values(['pat_id', 'order_time']) # TODO: bug...
    df = df.reset_index(drop=True)

    df['order_in_1day'] = df['order_time'].apply(lambda x: 'No')
    order_in_1day__inds = []

    prev_days = []
    row, col = df.shape
    for i in range(1, row):

        if df.ix[i, 'pat_id'] == df.ix[i - 1, 'pat_id']:
            time_diff_df = df.ix[i, 'order_time'] - df.ix[i - 1, 'order_time']

            if time_diff_df.days < 1:
                #
                order_in_1day__inds.append(i)

            #     pass
                #print df.ix[i - 1, ['pat_id', 'order_time']].values, df.ix[i, ['pat_id', 'order_time']].values

            # df.ix[i, 'prev_in_sec'] = time_diff_df.seconds
            # a day has 86400 secs
            # prev_days.append(time_diff_df.seconds/86400.)
            prev_days.append(time_diff_df.days) # TODO: ceiling of days?
        else:
            prev_days.append(sys.maxint)

    # df.ix[order_in_1day__inds, 'order_in_1day'] = 'Yes'
    # df.to_csv('Fig2_Order_Intensities/surprising_orders_in_1day_%s.csv'%lab)

    prevday_cnts_dict = collections.Counter(prev_days)

    return prevday_cnts_dict

def get_curve_onelab(lab, all_algs, data_folder, curve_type):
    # curr_res_file = '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv' % (lab, str(PPV_wanted), vital_day)

    '''
    Baseline curve
    '''

    df = pd.read_csv(data_folder + '/' + lab + '/' + 'baseline_comparisons.csv')
    base_actual = df['actual'].values
    base_predict = df['predict'].values

    if curve_type == 'roc':
        fpr_base, tpr_base, _ = roc_curve(base_actual, base_predict)
        xVal_base, yVal_base = fpr_base, tpr_base

        base_auc = roc_auc_score(base_actual, base_predict)
        base_score = base_auc
    elif curve_type == 'prc':
        precision, recall, _ = precision_recall_curve(base_actual, base_predict)
        xVal_base, yVal_base = recall, precision

        base_aps = average_precision_score(base_actual, base_predict)
        base_score = base_aps


    '''
    best alg
    '''
    best_score = 0
    best_alg = None
    best_actual = None
    best_predict = None
    for alg in all_algs:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         'direct_comparisons.csv')
        actual_list = df['actual'].values
        try:
            if curve_type == 'roc':
                cur_auc = roc_auc_score(actual_list, df['predict'].values)
                cur_score = cur_auc
            elif curve_type == 'prc':
                cur_aps = average_precision_score(actual_list, df['predict'].values)
                cur_score = cur_aps

        except ValueError:
            cur_score = float('nan')
        if cur_score > best_score:
            best_score = cur_score
            best_alg = alg
            best_actual = actual_list
            best_predict = df['predict'].values

    if curve_type == 'roc':
        fpr, tpr, _ = roc_curve(best_actual, best_predict)
        xVal_best, yVal_best = fpr, tpr

    elif curve_type == 'prc':
        precision, recall, _ = precision_recall_curve(best_actual, best_predict)
        xVal_best, yVal_best = recall, precision


    return xVal_base, yVal_base, base_score, xVal_best, yVal_best, best_score

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


def get_thres_by_fixing_PPV(lab, alg, data_folder='', PPV_wanted=0.9, thres_mode="from_test"):
    if thres_mode == "from_train":
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         '%s-normality-prediction-%s-direct-compare-results-traindata.csv' % (lab, alg))
    else:
        df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                         '%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg))

    # TODO: calibration?
    row, col = df.shape
    thres_last, PPV_last = 1., 1.
    actual_list = df['actual'].values.tolist()

    for thres in np.linspace(1, 0, num=1001):

        df['predict_class'] = df['predict'].apply(lambda x: 1 if x > thres else 0)
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


def bootstrap_CI(actual_list, predict_list, num_repeats=1000, stat='roc_auc',
                 confident_lvl=0.95, side='two', random_state=0):
    assert len(actual_list) == len(predict_list)

    from sklearn.utils import resample

    try:

        all_stats = []
        for i in range(num_repeats):
            actual_list_resampled, predict_list_resampled = resample(actual_list, predict_list)
            if stat == 'roc_auc':
                cur_roc_auc = roc_auc_score(actual_list_resampled, predict_list_resampled)
                all_stats.append(cur_roc_auc)

        roc_auc_left = np.percentile(all_stats, (1 - confident_lvl) / 2. * 100)
        roc_auc_right = np.percentile(all_stats, (1 + confident_lvl) / 2. * 100)

    except Exception as e:
        print e
        roc_auc_left, roc_auc_right = float('nan'), float('nan')

    return roc_auc_left, roc_auc_right


def fill_df_fix_PPV(lab, alg, data_folder='', PPV_wanted=0.9, lab_type=None, thres_mode="from_test"):
    df = pd.read_csv(data_folder + '/' + lab + '/' + alg + '/' +
                     '%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg))
    row, col = df.shape

    '''
    roc_auc, and its confidence interval (CI)
    Independent of any threshold
    '''
    actual_list = df['actual'].values.tolist()

    try:
        roc_auc = roc_auc_score(actual_list, df['predict'].values)
    except Exception as e:
        print e
        roc_auc = float('nan')

    try:
        roc_auc_left, roc_auc_right = bootstrap_CI(actual_list, df['predict'], confident_lvl=0.95)
    except Exception as e:
        print e
        roc_auc_left, roc_auc_right = float('nan'), float('nan')

    '''
    Score threshold is used for "predict_proba --> predict_label"
    Learning score threshold by fixing training PPV at desired lvl
    This way, learned test (evaluation) PPV is "unbiased". 
    '''
    if thres_mode == "quick_test":
        thres = 0.5
    else:
        thres = get_thres_by_fixing_PPV(lab, alg, data_folder=data_folder, PPV_wanted=PPV_wanted, thres_mode=thres_mode)

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

    res_dict = {'lab': lab, 'alg': alg, 'threshold': thres,
                'true_positive': true_positive / float(total_cnt), 'false_positive': false_positive / float(total_cnt),
                'true_negative': true_negative / float(total_cnt), 'false_negative': false_negative / float(total_cnt),
                'total_cnt': total_cnt, 'roc_auc': roc_auc,
                '95%_CI': '[%f, %f]' % (roc_auc_left, roc_auc_right)}
    res_dict['sensitivity'] = float(true_positive) / float(true_positive + false_negative)
    res_dict['specificity'] = float(true_negative) / float(true_negative + false_positive)
    try:
        res_dict['LR_p'] = res_dict['sensitivity'] / (1 - res_dict['specificity'])
    except ZeroDivisionError:
        if res_dict['sensitivity'] == 0:
            res_dict['LR_p'] = float('nan')
        else:
            res_dict['LR_p'] = float('inf')

    try:
        res_dict['LR_n'] = (1 - res_dict['sensitivity']) / res_dict['specificity']
    except ZeroDivisionError:
        if res_dict['sensitivity'] == 1:
            res_dict['LR_n'] = float('nan')
        else:
            res_dict['LR_n'] = float('inf')

    try:
        res_dict['PPV'] = float(true_positive) / float(true_positive + false_positive)
    except ZeroDivisionError:
        res_dict['PPV'] = float('nan')

    try:
        res_dict['NPV'] = float(true_negative) / float(true_negative + false_negative)
    except ZeroDivisionError:
        res_dict['NPV'] = float('nan')

    return res_dict


def add_panel_cnts_fees(one_lab_alg_dict):
    panel = one_lab_alg_dict['lab']
    df_cnts_fees = pd.read_csv('data_summary_stats/labs_charges_volumes.csv')
    cnts_fees_dict = df_cnts_fees.ix[df_cnts_fees['name'] == panel, ['count',
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
        one_lab_dict[str(year) + '_Vol'] = df_cnts.ix[df_cnts['Base'] == component, str(year)].values[0]
        # TODO: rename total_cnt to avoid confusion between total STRIDE cnt & testing cnt!

    return one_lab_dict

'''
Baseline 1: Predict normal only when reaching a certain number of previous consecutive normalities.
In most cases, can not make a prediction, so have to do the test. 
Have to pick a threshold. Cannot calculate ROC. 
'''
def get_baseline1_auroc(lab):
    pass

'''
Baseline 2: Predict by last normality (when it is available), or by population average.
In all cases, can make a prediction, so no need to make a prediction. 
Can calculate ROC, PPV etc. Can pick a threshold. 
'''
def get_baseline2_auroc(data_filepath=None):
    #TODO: does not care file structure, only take care of function and logic
    # if not data_folderpath:
    #     df = pd.read_csv(os.path.join(labs_ml_folder, lab, 'baseline_comparisons.csv'))  # TODO: baseline file should not have index!
    # else:
    #     df = pd.read_csv(os.path.join(data_filepath, 'baseline_comparisons.csv'))
    df = pd.read_csv(os.path.join(data_filepath, 'baseline_comparisons.csv'))

    try:
        res = roc_auc_score(df['actual'], df['predict'])
    except ValueError:
        res = float('nan')

    return res

############# Stats functions #############
# TODO: move to the stats module

############# Stats functions #############



######################################
'''
refactored
'''
def get_confusion_counts(actual_labels, predict_labels):

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    for i in range(len(actual_labels)):
        if actual_labels[i] == 1 and predict_labels[i] == 1:
            true_positive += 1
        elif actual_labels[i] == 0 and predict_labels[i] == 1:
            false_positive += 1
        elif actual_labels[i] == 1 and predict_labels[i] == 0:
            false_negative += 1
        elif actual_labels[i] == 0 and predict_labels[i] == 0:
            true_negative += 1
        else:
            print "what?!"
    return true_positive, false_positive, true_negative, false_negative

def get_confusion_metrics(actual_labels, predict_probas, threshold, also_return_cnts=False):
    #TODO: move to stats unit
    predict_labels = [1 if x > threshold else 0 for x in predict_probas]
    true_positive, false_positive, true_negative, false_negative = \
        get_confusion_counts(actual_labels, predict_labels)

    sensitivity = float(true_positive) / float(true_positive + false_negative)
    #res_dict['specificity'] \
    specificity = float(true_negative) / float(true_negative + false_positive)
    LR_p = np.divide(sensitivity, 1.-specificity)
    LR_n = np.divide(1-sensitivity, specificity)

    PPV = np.divide(float(true_positive), float(true_positive + false_positive))
    NPV = np.divide(float(true_negative), float(true_negative + false_negative))

    if not also_return_cnts:
        return sensitivity, specificity, LR_p, LR_n, PPV, NPV #res_dict
    else:
        return true_positive, false_positive, true_negative, false_negative, \
               sensitivity, specificity, LR_p, LR_n, PPV, NPV


def pick_threshold(y_pick, y_pick_pred, target_PPV=0.95):
    # TODO: assume both are numpy arrays
    thres_last, PPV_last = 1., 1.
    actual_list = y_pick.flatten().tolist()
    predicted_proba = y_pick_pred.flatten().tolist()
    assert len(actual_list) == len(predicted_proba)
    # TODO: also check proba's and labels

    for thres in np.linspace(1, 0, num=1001):

        predict_class_list = [1 if x > thres else 0 for x in predicted_proba]

        TP, FP, _, _ = get_confusion_counts(actual_list, predict_class_list)
        PPV = np.divide(float(TP), float(TP + FP))

        if PPV < target_PPV:
            break
        else:
            thres_last = thres

    return thres_last

def get_lab_descriptions():
    if lab_type=='panel':
        descriptions_filepath = os.path.join(labs_old_stats_folder, 'labs.csv')
    elif lab_type=='component':
        descriptions_filepath = os.path.join(labs_old_stats_folder, 'components.csv')
    elif lab_type=='UCSF':
        descriptions_filepath = os.path.join(labs_old_stats_folder, 'UCSF.csv')
    elif lab_type=='UMich':
        descriptions_filepath = os.path.join(labs_old_stats_folder, 'UMich.csv')

    df = pd.read_csv(descriptions_filepath, keep_default_na=False)
    descriptions = pandas2dict(df[['name', 'description']], key='name', val='description')
    return descriptions

def get_safe(func, *args):
    try:
        res = func(*args)
    except Exception as e:
        print e
        res = float('nan')
    return res

def dict2pandas(a_dict, key='lab', val='val'):
    return pd.DataFrame.from_dict(a_dict, orient='index').reset_index().rename(columns={'index': key,
                                                                                        0:val})
def pandas2dict(df, key='lab', val='val'):
    return df.set_index(key).to_dict()[val]

def get_queried_lab(lab, time_limit=DEFAULT_TIMELIMIT):
    lab_query_filepath = os.path.join(labs_query_folder, lab + '.csv')
    if not os.path.exists(lab_query_filepath):
        df = query_to_dataframe(lab, lab_query_filepath=lab_query_filepath)
    else:
        df = pd.read_csv(lab_query_filepath, keep_default_na=False)

    if lab_type == 'component':
        df = df[df['sop.order_status'] == 'Completed']
        df = df[(df['sop.order_time'] >= time_limit[0]) & (df['sop.order_time'] <= time_limit[1])]
    elif lab_type == 'panel':
        df = df[df['order_status'] == 'Completed']
        df = df[(df['order_time'] >= time_limit[0]) & (df['order_time'] <= time_limit[1])]
    df.drop_duplicates(inplace=True)
    return df

def get_labvol(lab, time_limit=DEFAULT_TIMELIMIT):
    df = get_queried_lab(lab, time_limit=time_limit)
    return df.shape[0]

def get_medicare_price_dict():
    data_folder = os.path.join(main_folder, 'lab_statistics/', 'data_summary_stats/')

    df_match = pd.read_csv(os.path.join(data_folder, 'potential_matches.csv'))
    dict_match = df_match.to_dict(orient='index')

    dict_match_new = {}
    for val in dict_match.values():
        dict_match_new[val['lab']] = val
    dict_match = dict_match_new

    df_price = pd.read_csv(os.path.join(data_folder, 'CLAB2018v1.csv'), skiprows=3)
    dict_price = df_price.to_dict(orient='index')

    dict_price_new = {}
    for val in dict_price.values():
        dict_price_new[val['SHORTDESC']] = val
    dict_price = dict_price_new
    #

    lab_price = {}
    for lab in dict_match:
        cur_match = dict_match[lab]
        cond1 = cur_match['JC'] != cur_match['JC']  # TODO: other suggestions
        cond2 = '?' not in cur_match['best matched description']
        if cond1 and cond2:
            cur_new_description = cur_match['best matched description']
            lab_price[lab] = dict_price[cur_new_description]['RATE2018']
    return lab_price

def lab2stats(lab, targeted_PPV, columns, thres_mode, train_data_labfolderpath, ml_results_labfolderpath, stats_results_filepath, price_source='medicare'):
    '''
    For each lab at each train_PPV,
    write all stats (e.g. roc_auc, PPV, total cnts) into csv file.

    '''

    df = pd.DataFrame(columns=columns)

    '''
    Baseline 2: Predict by last normality (when it is available), or by population average.

    Same across all algs
    '''
    baseline_roc_auc = get_baseline2_auroc(train_data_labfolderpath)

    # For STRIDE, also do cnts and costs
    if lab_type == 'panel' or lab_type == 'component':
        lab_vols = []
        for time_limit in DEFAULT_TIMELIMITS:
            print time_limit
            lab_vols.append(get_labvol(lab, time_limit=time_limit))

    # For panels, also include price info
    # TODO: this operation was repeated for each lab?!
    if lab_type == 'panel': #TODO: no price info for LABNA
        if price_source == 'chargemaster':
            prices_filepath = os.path.join(labs_old_stats_folder, 'labs_charges_volumes.csv')
            df_prices = pd.read_csv(prices_filepath, keep_default_na=False)
            df_prices_dict = df_prices.ix[df_prices['name'] == lab,
                                          ['min_price', 'max_price', 'mean_price', 'median_price']].to_dict(orient='list')
            for key, val in df_prices_dict.items():
                if lab == 'LABNA':
                    df_prices_dict[key] = 219
                else:
                    df_prices_dict[key] = val[0]
        elif price_source == 'medicare':
            medicare_price_dict = get_medicare_price_dict()
            cur_price = medicare_price_dict.get(lab, float('nan'))
            df_prices_dict = {'min_price':cur_price, 'max_price':cur_price,
                              'mean_price':cur_price, 'median_price':cur_price}



    fm_io = FeatureMatrixIO()
    processed_matrix_train_path = os.path.join(train_data_labfolderpath,
                                         '%s-normality-train-matrix-processed.tab'%lab)
    # TODO: get rid of '10000' in file name
    processed_matrix_train = fm_io.read_file_to_data_frame(processed_matrix_train_path)
    num_train_episodes = processed_matrix_train.shape[0]
    num_train_patient = len(set(processed_matrix_train['pat_id'].values.tolist()))

    processed_matrix_test_path = os.path.join(ml_results_labfolderpath,
                                               '%s-normality-test-matrix-processed.tab' % lab)
    # TODO: get rid of '10000' in file name
    processed_matrix_test = fm_io.read_file_to_data_frame(processed_matrix_test_path)
    #pd.read_csv(processed_matrix_test_path, keep_default_na=False)#fm_io.read_file_to_data_frame(processed_matrix_test_path)
    num_test_episodes = processed_matrix_test.shape[0]
    num_test_patient = len(set(processed_matrix_test['pat_id'].values.tolist()))

    for alg in all_algs:
        print 'Processing lab %s with alg %s' % (lab, alg)
        one_row = {}

        one_row['lab'] = lab
        one_row['alg'] = alg

        one_row.update({'num_train_episodes':num_train_episodes,
                        'num_train_patient':num_train_patient,
                        'num_test_episodes': num_test_episodes,
                        'num_test_patient': num_test_patient
                        })

        one_row['baseline2_ROC'] = baseline_roc_auc

        df_direct_compare = pd.read_csv(ml_results_labfolderpath + '/' + alg + '/' + 'direct_comparisons.csv',
                                        #'%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg),
                                        keep_default_na=False)

        actual_labels, predict_scores = df_direct_compare['actual'].values, df_direct_compare['predict'].values

        one_row['AUROC'] = get_safe(roc_auc_score, actual_labels, predict_scores)
        AUROC_left, AUROC_right = bootstrap_CI(actual_labels, predict_scores, confident_lvl=0.95)
        one_row['95%_CI'] = '[%f, %f]' % (AUROC_left, AUROC_right)

        '''
        Adding confusion metrics after picking a threshold
        '''
        one_row['targeted_PPV_%s'%thres_mode] = targeted_PPV

        if thres_mode=='fixTestPPV':
            score_thres = pick_threshold(actual_labels, predict_scores, target_PPV=targeted_PPV) # TODO!
        else:
            df_direct_compare_train = pd.read_csv(ml_results_labfolderpath + '/' + alg + '/' + 'direct_comparisons_train.csv',
                                        #'%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg),
                                        keep_default_na=False)
            actual_labels_train, predict_scores_train = df_direct_compare_train['actual'].values, df_direct_compare_train['predict'].values
            score_thres = pick_threshold(actual_labels_train, predict_scores_train, target_PPV=targeted_PPV)

        one_row['score_thres'] = score_thres

        true_positive, false_positive, true_negative, false_negative, \
        sensitivity, specificity, LR_p, LR_n, PPV, NPV = get_confusion_metrics(actual_labels,
                                                                               predict_scores,
                                                                               threshold=score_thres,
                                                                               also_return_cnts=True)
        one_row.update({
            'true_positive':true_positive,
            'false_positive':false_positive,
            'true_negative':true_negative,
            'false_negative':false_negative,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'LR_p': LR_p,
            'LR_n': LR_n,
            'PPV': PPV,
            'NPV': NPV
                   })

        if lab_type == 'panel' or lab_type == 'component':
            for i_tw, time_window in enumerate(DEFAULT_TIMEWINDOWS):
                one_row['%s count'%time_window] = lab_vols[i_tw]

        if lab_type == 'panel':
            one_row.update(df_prices_dict)

        df = df.append(one_row, ignore_index=True)

    df[columns].to_csv(stats_results_filepath, index=False)

    return df

'''
refactored
'''
######################################




def get_top_labs_and_cnts(lab_type='panel', top_k=None, bottom_k=None, criterion='count', time_limit=None):
    # df = pd.read_csv('data_performance_stats/best-alg-%s-summary-fix-trainPPV.csv'%lab_type,
    #                  keep_default_na=False)
    # if lab_type == 'component':
    #     df = df.rename(columns={'2016_Vol':'count'})
    # else:
    #     df['median_price'] = df['median_price'].apply(lambda x: float(x) if x else 0)
    #
    # df['count'] = df['count'].apply(lambda x: float(x) if x else 0) # TODO: LABNA == 0!
    #
    # if lab_type == 'component' or criterion == 'count':
    #     df = df[['lab', criterion]].drop_duplicates()
    # elif criterion == 'count*price': # TODO: probably confusing, but it means count*median_price
    #     df[criterion] = df['count']*df['median_price']
    #     df = df[['lab', criterion]].drop_duplicates()
    #
    # res = df.sort_values(criterion, ascending=False).head(top_k)
    # if lab_name_only:
    #     return res['lab'].values
    # else:
    #     return res

    data_folder = "query_lab_results/"
    labs_and_cnts_file = "%ss_and_cnts_2014-2016.csv" % lab_type
    labs_and_cnts_path = os.path.join(data_folder, labs_and_cnts_file)
    if os.path.exists(labs_and_cnts_path):
        print "%s exists.."%labs_and_cnts_path
        labs_and_cnts_df = pd.read_csv(labs_and_cnts_path, keep_default_na=False)
        labs_and_cnts = labs_and_cnts_df.values.tolist()

    else:

        labs_and_cnts = []

        if lab_type == 'panel':
            all_labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
        elif lab_type == 'component':
            all_labs = STRIDE_COMPONENT_TESTS

        for lab in all_labs: # TODO here
            lab_data_filename = '%s.csv'%lab
            lab_data_path = os.path.join(data_folder, lab_data_filename)

            df = pd.read_csv(lab_data_path, keep_default_na=False)
            if lab_type == 'panel':
                df = df[df['order_status']=='Completed']
            if time_limit:
                if time_limit[0]:
                    df = df[df['order_time']>=time_limit[0]]
                if time_limit[1]:
                    df = df[df['order_time'] <= time_limit[1]]
            cnt = df.shape[0]

            labs_and_cnts.append([lab, cnt])

        labs_and_cnts = sorted(labs_and_cnts, key=lambda x:x[1])[::-1]

        labs_and_cnts_df = pd.DataFrame(labs_and_cnts, columns=['lab', 'cnt'])

        labs_and_cnts_df.to_csv(labs_and_cnts_path, index=False)

    # print "[x[0] for x in labs_and_cnts[:top_k]]", [x[0] for x in labs_and_cnts[:top_k]]

    if top_k and not bottom_k:
        return labs_and_cnts[:top_k]
    else:
        return labs_and_cnts[-bottom_k:]

    # return df.ix[:top_k, ['lab','total cnt']].values.tolist()


def main():
    columns_panels = ['lab', 'alg', 'roc_auc', '95%_CI', 'baseline_roc', 'total_cnt']
    columns_panels += ['threshold', 'true_positive', 'false_positive', 'true_negative', 'false_negative']
    columns_panels += ['sensitivity', 'specificity', 'LR_p', 'LR_n', 'PPV', 'NPV']
    columns_panels += ['count', 'min_price', 'max_price', 'mean_price', 'median_price',
                       'min_volume_charge', 'max_volume_charge', 'mean_volume_charge', 'median_volume_charge']
    import generate_result_tables
    lab2stats_csv(lab_type="panel",
                  lab="LABHIVWBL",
                  years=[2016],
                  all_algs=generate_result_tables.all_algs,
                  PPV_wanted=0.95,
                  vital_day=3,
                  folder_path='../machine_learning/',
                  data_folder="data-panels/",
                  result_folder="",
                  columns=columns_panels,
                  thres_mode="from_train")

def query_to_dataframe(lab, lab_type='panel',
                     columns=None,
                     time_limit=None,
                       lab_query_filepath=""):

    # output_filename = '%s.csv'%lab
    #
    # output_path = os.path.join(output_foldername, output_filename)
    #
    # if os.path.exists(output_path):
    #     print "Cached dataframe %s exists..." % lab
    #     return pd.read_csv(output_path)

    print "Running query of %s..." % lab


    query = SQLQuery()

    if lab_type == 'panel':
        if not columns:
            columns = ["proc_code", "order_proc_id", "pat_id", "order_time",
                       "abnormal_yn", "lab_status", "order_status"]

        for column in columns:
            query.addSelect(column)

        query.addFrom('stride_order_proc')
        # query.addFrom('stride_order_results AS sor')
        if time_limit:
            if time_limit[0]:
                query.addWhere("order_time >= '%s'" % time_limit[0])
            if time_limit[1]:
                query.addWhere("order_time <= '%s'" % time_limit[1])
        # query.addWhere('sop.order_proc_id = sor.order_proc_id')
        query.addWhere("proc_code = '%s'" % lab)
        # query.addGroupBy("proc_code")
        query.addOrderBy("proc_code")

    elif lab_type == 'component':  # see NA
        if not columns:
            columns = ["sor.base_name", "sor.order_proc_id", "sor.result_time",
                       "sor.result_in_range_yn", 'sor.ord_num_value', 'sor.reference_unit', 'sor.result_flag',
                       "sor.lab_status",
                       "sop.proc_code", "sop.order_proc_id", "sop.pat_id", "sop.order_time",
                       "sop.abnormal_yn", "sop.lab_status", "sop.order_status"]

        for column in columns:
            query.addSelect(column)

        query.addFrom('stride_order_results as sor')
        query.addFrom('stride_order_proc as sop')
        query.addWhere('sor.order_proc_id = sop.order_proc_id')
        if time_limit:
            if time_limit[0]:
                query.addWhere("sop.order_time >= '%s'" % time_limit[0])
            if time_limit[1]:
                query.addWhere("sop.order_time <= '%s'" % time_limit[1])
        query.addWhere("base_name = '%s'" % lab)

    results = DBUtil.execute(query)

    df = pd.DataFrame(results, columns=columns)
    # if not os.path.exists(output_foldername):
    #     os.mkdir(output_foldername)
    df.to_csv(lab_query_filepath, index=False)

    return df

def main_queryAllLabsToDF(lab_type='panel'):
    '''
    query all labs from sql to df to make them faster for stats analysis.

    Returns:

    '''
    # time_limits = [['2014-07-01', '2014-12-31'],
    #                 ['2015-01-01', '2015-06-30'],
    #                 ['2015-07-01', '2015-12-31'],
    #                 ['2016-01-01', '2016-06-30'],
    #                 ['2016-07-01', '2016-12-31'],
    #                 ['2017-01-01', '2017-06-30']]

    dst_folder = 'query_lab_results/'
    for lab in all_labs:
        # res = query_lab_usage__df(lab, lab_type='panel', time_limit=('2014-07-01', '2014-12-31'))
        # print res
        # quit()
        # for i, time_limit in time_limits:
        src_filepath = os.path.join(dst_folder, lab+'.csv')
        lab_df_old = pd.read_csv(src_filepath, keep_default_na=False)

        lab_df_new = query_to_dataframe(lab, lab_type=lab_type,
                           time_limit=['2017-01-01', '2017-06-30'])

        lab_df = pd.concat([lab_df_old, lab_df_new], axis=0, ignore_index=True)

        dst_filepath = src_filepath
        lab_df.to_csv(dst_filepath, index=False)




if __name__ == '__main__':
    # print get_top_labs(lab_type='component', top_k=20, lab_name_only=False)
    # print get_top_labs(lab_type='panel', top_k=20, criterion='count*price')

    # print query_lab_cnt('LABMGN')
    # print query_lab_cnt('LABCBCD')
    main_queryAllLabsToDF(lab_type='component')



