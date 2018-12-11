
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
import datetime, collections
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)
import numpy as np
from scipy import stats
import os

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline \
        import NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS

def query_lab_usage__df(lab, lab_type='panel', time_start=None, time_end=None):
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

def get_prevweek_normal__dict(df):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    '''
    Cnt of ordering w/i one day
    '''
    df['prev_in_sec'] = df['pat_id'].apply(lambda x: 1000 * 24 * 3600) # 1000 days
    df['order_time'] = df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)
                                if isinstance(x, str) else x)
    df = df.reset_index(drop=True)

    row, col = df.shape
    my_dict = {}
    '''
    key: num of CONSECUTIVE normal in past week. val: [normal, normal, abnormal...]
    '''
    for i in range(1, row):
        curr_normal = False if df.ix[i, 'abnormal_yn'] == 'Y' else True
        if df.ix[i, 'pat_id'] == df.ix[i - 1, 'pat_id']:
            # There is a possibility

            prev_cnt = 0
            # TODO: prev_cnt = 0 is different from prev has some normals?" For now, don't consider either

            # if prev_cnt in my_dict:
            #     my_dict[prev_cnt].append(curr_normal)
            # else:
            #     my_dict[prev_cnt] = [curr_normal]
            time_diff = df.ix[i, 'order_time'] - df.ix[i - 1, 'order_time']

            j = i - 1
            while time_diff.days < 7:
                prev_normal = False if df.ix[j, 'abnormal_yn'] == 'Y' else True
                if not prev_normal: # "Consecutivity" is broken
                    break

                prev_cnt += 1
                if prev_cnt in my_dict:
                    my_dict[prev_cnt].append(curr_normal)
                else:
                    my_dict[prev_cnt] = [curr_normal]

                j -= 1
                if j < 0 or df.ix[i, 'pat_id'] != df.ix[j, 'pat_id']:
                    break
                time_diff = df.ix[i, 'order_time'] - df.ix[j, 'order_time']
        else:
            if 0 in my_dict:
                my_dict[0].append(curr_normal)
            else:
                my_dict[0] = [curr_normal]

    for key in my_dict:
        my_dict[key] = float(sum(my_dict[key]))/len(my_dict[key])
    return my_dict



            # df.ix[i, 'prev_in_sec'] = time_diff_df.seconds
            # a day has 86400 secs
            # prev_days.append(time_diff_df.seconds/86400.)

def get_time_since_last_order_cnts(df):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    '''
    Cnt of ordering w/i one day
    '''
    df['prev_in_sec'] = df['pat_id'].apply(lambda x: 1000 * 24 * 3600)
    df['order_time'] = df['order_time'].apply(lambda x: datetime.datetime.strptime(x, datetime_format)
                                              if isinstance(x, str) else x)
    df = df.reset_index(drop=True)

    prev_days = []
    row, col = df.shape
    for i in range(1, row):

        if df.ix[i, 'pat_id'] == df.ix[i - 1, 'pat_id']:
            time_diff_df = df.ix[i, 'order_time'] - df.ix[i - 1, 'order_time']

            if time_diff_df.days < 1:
                pass
                #print df.ix[i - 1, ['pat_id', 'order_time']].values, df.ix[i, ['pat_id', 'order_time']].values

            # df.ix[i, 'prev_in_sec'] = time_diff_df.seconds
            # a day has 86400 secs
            # prev_days.append(time_diff_df.seconds/86400.)
            prev_days.append(time_diff_df.days) # TODO: ceiling of days?
        else:
            prev_days.append(-1)

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
                         '%s-normality-prediction-%s-direct-compare-results.csv' % (lab, alg))
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

    all_stats = []
    for i in range(num_repeats):
        actual_list_resampled, predict_list_resampled = resample(actual_list, predict_list)
        if stat == 'roc_auc':
            cur_roc_auc = roc_auc_score(actual_list_resampled, predict_list_resampled)
            all_stats.append(cur_roc_auc)

    roc_auc_left = np.percentile(all_stats, (1 - confident_lvl) / 2. * 100)
    roc_auc_right = np.percentile(all_stats, (1 + confident_lvl) / 2. * 100)

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


def get_baseline(file_path):
    # try:
    df = pd.read_csv(file_path + 'baseline_comparisons.csv')  # TODO: baseline file should not have index!
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


def lab2stats_csv(lab_type, lab, years, all_algs, PPV_wanted, vital_day,
                  folder_path, data_folder, result_folder, columns,
                  thres_mode="from_test"):
    if thres_mode == "from_train":
        curr_res_file = '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv' % (lab, str(PPV_wanted), vital_day)
    elif thres_mode == "from_test":
        curr_res_file = '%s-alg-summary-testPPV-%s-vitalDays-%d.csv' % (lab, str(PPV_wanted), vital_day)

    if os.path.exists(result_folder + curr_res_file):
        return

    df = pd.DataFrame(columns=columns)

    baseline_roc_auc = get_baseline(file_path=folder_path + '/' + data_folder + '/' + lab + '/')

    for alg in all_algs:
        print 'Processing lab %s with alg %s' % (lab, alg)
        # try:
        one_lab_alg_dict = fill_df_fix_PPV(lab, alg, data_folder=folder_path + '/' + data_folder,
                                           PPV_wanted=PPV_wanted, lab_type=lab_type, thres_mode=thres_mode)
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

def get_top_labs_and_cnts(lab_type='panel', top_k=10, criterion='count', time_limit=None):
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

    return labs_and_cnts[:top_k]

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
                     output_foldername = "query_lab_results/",
                     time_limit=None):

    output_filename = '%s.csv'%lab

    output_path = os.path.join(output_foldername, output_filename)

    if os.path.exists(output_path):
        print "Cached dataframe %s exists..." % lab
        return pd.read_csv(output_path)

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
    if not os.path.exists(output_foldername):
        os.mkdir(output_foldername)
    df.to_csv(output_path, index=False)

    return df

def query_lab_cnt(lab, lab_type='panel', time_limit=('2014-01-01','2016-12-31')):
    output_filename = '%s.csv'%lab
    output_foldername = "query_lab_results/"
    if not os.path.exists(output_foldername + output_filename):
        query_to_dataframe(lab)

    df = pd.read_csv(output_foldername + output_filename)
    if time_limit:
        if time_limit[0]:
            df = df[df['order_time'] >= time_limit[0]]
        if time_limit[1]:
            df = df[df['order_time'] <= time_limit[1]]
    return df.shape[0]
    # query = SQLQuery()
    #
    # if lab_type == 'panel':
    #
    #     query.addSelect("proc_code")
    #     query.addSelect('COUNT(sop.order_proc_id) AS num_orders')
    #     # query.addSelect("sop.order_proc_id")
    #     # query.addSelect("sop.lab_status")
    #     # query.addSelect('sop.order_status')
    #
    #     query.addFrom('stride_order_proc AS sop')
    #     # query.addFrom('stride_order_results AS sor')
    #     if time_limit:
    #         if time_limit[0]:
    #             query.addWhere("sop.order_time >= '%s'" % time_limit[0])
    #         if time_limit[1]:
    #             query.addWhere("sop.order_time <= '%s'" % time_limit[1])
    #     # query.addWhere('sop.order_proc_id = sor.order_proc_id')
    #     query.addWhere("proc_code = '%s'"%lab)
    #     query.addGroupBy("proc_code")
    #     query.addOrderBy("proc_code")
    #
    # elif lab_type == 'component': # see NA
    #     query.addSelect("base_name")
    #     query.addSelect('COUNT(order_proc_id) AS num_orders')
    #     query.addFrom('stride_order_results')
    #     if time_limit:
    #         if time_limit[0]:
    #             query.addWhere("result_time >= '%s'" % time_limit[0])
    #         if time_limit[1]:
    #             query.addWhere("result_time <= '%s'" % time_limit[1])
    #     query.addWhere("base_name = '%s'"%lab)
    #     query.addGroupBy("base_name")
    #
    # results = DBUtil.execute(query)



def test_():
    ress = query_lab_usage__df(lab='LABALB')
    # for i in range(1,len(ress)):
    #     if
    print 'Unique num of patients:', len(list(set(x[0] for x in ress)))
    for res in ress[:10]:
        print res

    df = pd.DataFrame(ress, columns=['pat_id', 'order_time', 'result'])
    print len(list(set(df['pat_id'].values.tolist())))
    df.to_csv('tmpLABALB.csv', index=False)

    df1 = pd.read_csv('tmpLABALB.csv')
    print len(list(set(df1['pat_id'].values.tolist())))


if __name__ == '__main__':
    # print get_top_labs(lab_type='component', top_k=20, lab_name_only=False)
    # print get_top_labs(lab_type='panel', top_k=20, criterion='count*price')

    # print query_lab_cnt('LABMGN')
    # print query_lab_cnt('LABCBCD')

    for lab in STRIDE_COMPONENT_TESTS:
        query_to_dataframe(lab, lab_type='component',
                               columns=None,
                               output_foldername="query_lab_results/",
                               time_limit=['2014-01-01','2016-12-31'])


