
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

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS

'''
For each lab, get a bunch of stuff
'''

'''
For plotting guideline,

a lab, has n prev consecutive normal. 
'''


DEFAULT_TIMELIMIT = ('2014-07-01', '2017-07-01') # TODO: extremely confusing!
# DEFAULT_TIMESPAN = ('2014-01-01', '2017-06-30') # TODO: extremely confusing!

# DEFAULT_TIMEWINDOWS = [#'2014 1stHalf',
#                        '2014 2stHalf',
#                        '2015 1stHalf', '2015 2stHalf',
#                        '2016 1stHalf', '2016 2stHalf',
#                        '2017 1stHalf']

'''
Meta-data in the last 3 years
'''

'''
select count(distinct pat_id) from stride_order_proc where order_time >= '2014-07-01' and order_time < '2017-07-01';
'''
NUM_DISTINCT_PATS = 44710

'''
select count(distinct pat_enc_csn_id) from stride_order_proc where order_time >= '2014-07-01' and order_time < '2017-07-01';
'''
NUM_DISTINCT_ENCS = 66440

NUM_DISTINCT_ENCS_UCSF = 15989

'''
select count(distinct order_proc_id) from stride_order_proc where proc_code='LABMGN' and order_status='Completed' and order_time >= '2014-07-01' and order_time < '2017-07-01';
'''
NUM_MAGNESIUM_COMPLETED_ORDERS = 282414

umich_lab_cnt = {'WBC':5280.99347210938,
                'HGB':5281.00748045835,
                'PLT':5274.22743955397,
                'SOD':5784.07530888409,
                'POT':5784.06130053512,
                'CR':5784.04729218614,
                'TBIL':1662.90309024178,
                'CHLOR':5784.07530888409,
                'CO2':5784.04729218614,
                'AST':1667.87605412826,
                'ALB':2239.66884263021,
                'CAL':5791.51374219035,
                # 'PCO2AA':,
                # 'PO2AA':,
                # 'DBIL':,
                # 'pHA':,
                'PROT':1667.87605412826,
                'ALK':1667.87605412826,
                'UN':5784.04729218614,
                # 'IBIL':
                'CREAT': 5784.04729218614,
                'ALT': 1667.87605412826
                }

# DEFAULT_TIMELIMITS = []
# for time_window in DEFAULT_TIMEWINDOWS:
#     year_str, section_str = time_window.split(' ')
#
#     if section_str == '1stHalf':
#         section_timestamps = ('01-01', '06-30')
#     else:
#         section_timestamps = ('07-01', '12-31')
#
#     time_limit = ['-'.join([year_str, x]) for x in section_timestamps]
#
#     DEFAULT_TIMELIMITS.append(time_limit)





# labs_ml_folder = os.path.join(main_folder, 'machine_learning/data-%ss-%s/'%(lab_type, curr_version))
# labs_stats_folder = os.path.join(main_folder, 'lab_statistics/stats-%ss-%s/'%(lab_type, curr_version))



# if not os.path.exists(labs_folder):
#     os.mkdir(labs_folder)
# if not os.path.exists(labs_stats_folder):
#     os.mkdir(labs_stats_folder)
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
def prepare_subfigs(num_figs, col = 5):

    row = num_figs / col
    cols_left = num_figs % col
    if cols_left > 0:
        row = row + 1

    fig_width, fig_heights = 2.5 * col, 2.1 * row #8. / col * row

    plt.figure(figsize=(fig_width, fig_heights))

    i_s = []
    j_s = []
    for ind in range(num_figs):
        ind_in_fig = ind % num_figs
        i, j = ind_in_fig / col, ind_in_fig % col
        i_s.append(i)
        j_s.append(j)

    return row, col, i_s, j_s

def get_prevday2normalities(lab, mlByLab_folder, time_limit=DEFAULT_TIMELIMIT, source='full'):
    '''
    Why: Plot figure

    What: How consecutive normality indicates the next normality?

    How:

    Args:
        lab:
        time_limit:

    Returns:

    '''

    if source == 'full':
        df_lab = query_to_dataframe(lab, time_limit=time_limit)
        df_lab = df_lab[df_lab['order_status']=='Completed'].reset_index(drop=True)

    else:
        import LocalEnv
        from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

        print "processing %s..."%lab
        # data_folder = LocalEnv.PATH_TO_CDSS + '/scripts/LabTestAnalysis/machine_learning/data-panels/%s/' % lab
        '''
        First, obtain test patients
        '''
        data_processed_filename = '%s-normality-%s-matrix-processed.tab' % (lab, source)
        data_processed_pathname = os.path.join(mlByLab_folder, lab, data_processed_filename)

        fm_io = FeatureMatrixIO()
        df_processed_test_lab = fm_io.read_file_to_data_frame(data_processed_pathname)
        # print df_processed_test_lab.head()
        # quit()
        pat_ids_test = set(df_processed_test_lab['pat_id'].values.tolist())


        '''
        Then, obtain
        '''

        data_raw_filename = '%s-normality-matrix-raw.tab' % lab
        data_raw_pathname = os.path.join(mlByLab_folder, lab, data_raw_filename)

        df_raw = fm_io.read_file_to_data_frame(data_raw_pathname)
        df_lab = df_raw[df_raw['pat_id'].isin(pat_ids_test)]
        df_lab['abnormal_yn'] = df_lab['abnormal_panel'].apply(lambda x: 'Y' if x==1 else 'N')
        df_lab = df_lab[['pat_id', 'order_time', 'abnormal_yn']]

    day2norms = get_prevweek_normal__dict(df_lab, also_get_cnt=True)

    return day2norms.keys(), day2norms.values()

def check_baseline2(lab, mlByLab_folder, source="train", target_PPV=0.95, picked_prevalence=None, picked_thres=None):
    '''
    Pick a threshold

    Args:
        lab:
        mlByLab_folder:
        source:
        target_PPV:

    Returns:

    '''
    data_processed_filename = '%s-normality-%s-matrix-processed.tab' % (lab, source)
    data_processed_pathname = os.path.join(mlByLab_folder, lab, data_processed_filename)

    fm_io = FeatureMatrixIO()
    processed_matrix = fm_io.read_file_to_data_frame(data_processed_pathname)
    pat_ids = set(processed_matrix['pat_id'].values.tolist())

    data_raw_filename = '%s-normality-matrix-raw.tab' % lab
    data_raw_pathname = os.path.join(mlByLab_folder, lab, data_raw_filename) # TODO: create template
    raw_matrix = fm_io.read_file_to_data_frame(data_raw_pathname)


    df_lab = raw_matrix[raw_matrix['pat_id'].isin(pat_ids)].reset_index()[['pat_id', 'order_time', 'all_components_normal']]

    df_lab = df_lab.sort_values(['pat_id', 'order_time'])



    if not picked_prevalence:
        normal_prevalence = df_lab['all_components_normal'].values.sum()/float(df_lab.shape[0])

    else:
        df_lab['predict_proba'] = df_lab['all_components_normal'].apply(lambda x: picked_prevalence)

    for i in range(1, df_lab.shape[0]):
        if df_lab.ix[i-1, 'pat_id'] == df_lab.ix[i, 'pat_id']:
            df_lab.ix[i, 'predict_proba'] = df_lab.ix[i-1, 'all_components_normal']

    if not picked_thres:

        thres_possibles = [0, normal_prevalence, 1]

        thres = -1
        for thres_one in thres_possibles:
            df_lab['predict_label'] = df_lab['predict_proba'].apply(lambda x: 1 if x>=thres_one else 0)

            predicted_normals = df_lab[df_lab['predict_label']==1].shape[0]
            true_normals = df_lab[(df_lab['predict_label']==1) & (df_lab['all_components_normal']==1)].shape[0]
            PPV = float(true_normals)/float(predicted_normals)
            if PPV >= target_PPV:
                thres = thres_one

        return normal_prevalence, thres


    else:

        df_lab['predict_label'] = df_lab['predict_proba'].apply(lambda x: 1 if x >= picked_thres else 0)
        predicted_normals = df_lab[df_lab['predict_label'] == 1].shape[0]
        saved_fraction = float(predicted_normals)/float(df_lab.shape[0])
        return saved_fraction


def plot_subfigs(dicts, colors=('blue','orange'), result_figpath="subfigs.png"):

    num_labs = len(dicts[0])

    row, col, i_s, j_s = prepare_subfigs(num_labs, col=6)


    keys = dicts[0].keys()

    def do_one_plot(x, y, color):
        plt.bar(x, y, color=color)
        plt.text(x, y, '%.2f' % y, color='k')

        plt.xticks([])
        plt.ylim(0, 1.05)
        plt.yticks([])

    lab_descriptions = get_lab_descriptions()
    for ind, key in enumerate(keys):


        i, j = i_s[ind], j_s[ind]
        plt.subplot2grid((row, col), (i, j))

        for k in range(len(dicts)):
            do_one_plot(k, dicts[k][key], color=colors[k])

        plt.xlabel(lab_descriptions[key])

    plt.savefig(result_figpath)


def check_similar_components():
    # common_labs = list(set(STRIDE_COMPONENT_TESTS) & set(UMICH_TOP_COMPONENTS))

    df_UMich = pd.read_csv('RF_important_features_UMichs.csv',keep_default_na=False)
    df_component = pd.read_csv('RF_important_features_components.csv',keep_default_na=False)

    columns_UMich_only = []
    columns_component_only = []
    for i in range(1,4):
        df_UMich = df_UMich.rename(columns={'feature %i'%i:'UMich featu %i'%i,
                                            'score %i'%i:'UMich score %i'%i})
        columns_UMich_only += ['UMich featu %i'%i, 'UMich score %i'%i]
        df_component = df_component.rename(columns={'feature %i'%i:'STRIDE featu %i'%i,
                                                    'score %i' % i:'STRIDE score %i' % i})
        columns_component_only += ['STRIDE featu %i'%i, 'STRIDE score %i'%i]

    df_combined = pd.merge(df_component, df_UMich, on='lab', how='inner')
    (df_combined[['lab'] + columns_UMich_only]).to_csv("UMich_feature_importance_to_compare.csv", index=False)
    (df_combined[['lab'] + columns_component_only]).to_csv("component_feature_importance_to_compare.csv", index=False)

def get_guideline_maxorderfreq():
    maxorderfreq = {}
    maxorderfreq['once'] = ['LABCBCD', 'LABALB', 'LABA1C', 'LABPHOS', 'LABTSH']
    maxorderfreq['three_days'] = ['LABESRP']
    # maxorderfreq['one_day'] = ['LABMETB']

    return maxorderfreq

def get_important_labs(lab_type='panel', data_source='Stanford', order_by=None):
    # TODO: order_by

    if lab_type == 'panel':
        # labs_and_cnts = get_top_labs_and_cnts('panel', top_k=10)
        # print labs_and_cnts
        #
        # '''
        # Adding other important labs
        # '''
        # labs_and_cnts.append(['LABCBCD', stats_utils.query_lab_cnt(lab='LABCBCD',
        #                                     time_limit=['2014-01-01','2016-12-31'])])
        # TODO: ISTAT TROPONIN?
        return ['LABMGN', 'LABALB', 'LABPHOS', 'LABLAC', 'LABBLC', 'LABBLC2', 'LABLDH', 'LABURIC', 'LABTNI', 'LABNA', 'LABK'] #,

        #stats_utils.get_top_labs(lab_type=lab_type, top_k=10)
    elif lab_type == 'component':
        # TODO
        if data_source!='UMich': #TODO!
            return ['WBC', 'HGB', 'PLT', 'NA', 'K', 'CO2', 'BUN', 'CR', #'GLUC',
                    'CA', 'ALB', 'TP',
                    'ALKP', 'TBIL', 'AST', 'ALT']
        else:
            return ['WBC', 'HGB', 'PLT', 'NA', 'K', 'CO2', 'BUN', 'CR',  # 'GLUC',
                    'CA', 'ALB', 'PROT',
                    'ALKP', 'TBIL', 'AST', 'ALT']

    labs_and_cnts = sorted(labs_and_cnts, key=lambda x: x[1])
    return [x[0] for x in labs_and_cnts]

def query_num_instances(instance_type='pat_id', time_limit=DEFAULT_TIMELIMIT):
    # pat_enc_csn_id in ('2014-07-01', '2017-06-30') is 66439
    # pat_id in ('2014-07-01', '2017-06-30') is 44709

    if time_limit:
        time_start, time_end = time_limit[0], time_limit[1]

    query = SQLQuery()
    query.addSelect('COUNT(DISTINCT %s)'%instance_type)
    query.addFrom('stride_order_proc')

    if time_start:
        query.addWhere("order_time > '%s'" % time_start)
    if time_end:
        query.addWhere("order_time < '%s'" % time_end)

    results = DBUtil.execute(query)

    return results


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

def get_prevweek_normal__dict(df, lab_type, also_get_cnt=False):
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
        j = i - 1

        if lab_type=='panel':
            curr_normal = 0 if df.ix[i, 'abnormal_yn'] == 'Y' else 1 # TODO: update the criterion

            while j >= 0 \
                and df.ix[i,'pat_id'] == df.ix[j,'pat_id'] \
                and (df.ix[i,'order_time'] - df.ix[j,'order_time']).days < 7 \
                and df.ix[j,'abnormal_yn'] != 'Y':

                j -= 1
        else:
            curr_normal = 0 if df.ix[i, 'result_flag'] != '' else 1

            while j >= 0 \
                    and df.ix[i, 'pat_id'] == df.ix[j, 'pat_id'] \
                    and (df.ix[i, 'order_time'] - df.ix[j, 'order_time']).days < 7 \
                    and df.ix[j, 'result_flag'] == '':
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

def get_floored_day_to_number_orders_cnts(lab, df):
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

    prev_days = [sys.maxint] # The first record
    row, col = df.shape
    for i in range(1, row):
        if df.ix[i, 'pat_id'] == df.ix[i - 1, 'pat_id']:
            time_diff_df = df.ix[i, 'order_time'] - df.ix[i - 1, 'order_time']
            if time_diff_df.days < 1:
                #
                order_in_1day__inds.append(i)

                # print df.ix[i, 'order_status'], df.ix[i - 1, 'order_time'], df.ix[i, 'order_time']

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

def get_curve_onelab(lab, all_algs, data_folder, curve_type, get_pval=False, get_baseline=True):
    # curr_res_file = '%s-alg-summary-trainPPV-%s-vitalDays-%d.csv' % (lab, str(PPV_wanted), vital_day)

    '''
    Baseline curve
    '''
    if get_baseline:
        df = pd.read_csv(data_folder + '/' + lab + '/' + 'baseline_comparisons.csv')
        baseline_shape = df.shape

        base_actual = df['actual'].values #df['actual'].values #all_components_normal
        base_predict = df['predict'].values # predict

        if curve_type == 'ROC':
            fpr_base, tpr_base, _ = roc_curve(base_actual, base_predict)
            xVal_base, yVal_base = fpr_base, tpr_base

            try:
                base_auc = roc_auc_score(base_actual, base_predict)
            except:
                base_auc = float('nan')
            base_score = base_auc
        elif curve_type == 'PRC':
            precision, recall, _ = precision_recall_curve(base_actual, base_predict)
            xVal_base, yVal_base = recall, precision

            base_aps = average_precision_score(base_actual, base_predict)
            base_score = base_aps
    else:
        xVal_base, yVal_base, base_score = None, None, None

    '''
    best alg
    '''
    best_score = 0
    best_alg = None
    best_actual = None
    best_predict = None
    for alg in all_algs:
        df = pd.read_csv(data_folder + '/' + lab +  '/' + alg + '/' +
                         'direct_comparisons.csv')
        alg_shape = df.shape

        # print baseline_shape, alg_shape
        # print lab, baseline_shape[0], alg_shape[0]
        if get_baseline:
            assert baseline_shape[0] == alg_shape[0] # Make sure the same test set!

        actual_list = df['actual'].values
        try:
            if curve_type == 'ROC':
                cur_auc = roc_auc_score(actual_list, df['predict'].values)
                cur_score = cur_auc
            elif curve_type == 'PRC':
                cur_aps = average_precision_score(actual_list, df['predict'].values)
                cur_score = cur_aps

        except ValueError:
            cur_score = float('nan')
        if cur_score > best_score:
            best_score = cur_score
            best_alg = alg
            best_actual = actual_list
            best_predict = df['predict'].values

    if get_pval:
        p_val = random_permutation_test(base_actual, base_predict, best_actual, best_predict, curve_type)
    else:
        p_val = -1

    if curve_type == 'ROC':
        fpr, tpr, _ = roc_curve(best_actual, best_predict)
        xVal_best, yVal_best = fpr, tpr

    elif curve_type == 'PRC':
        precision, recall, _ = precision_recall_curve(best_actual, best_predict)
        xVal_best, yVal_best = recall, precision


    return xVal_base, yVal_base, base_score, xVal_best, yVal_best, best_score, p_val

def random_permutation_test(base_actual, base_predict, best_actual, best_predict, curve_type):
    '''
    Why: Check statistical significance of our model's AUC compared to baseline AUC.

    How:
    https://stats.stackexchange.com/questions/214687/what-statistical-tests-to-compare-two-aucs-from-two-models-on-the-same-dataset

    Args:
        base_actual:
        base_predict:
        best_actual:
        best_predict:
        curve_type:

    Returns:

    '''

    # 1.
    # auc_base = roc_auc_score(base_actual, base_predict)
    if curve_type == 'ROC':
        auc_best = roc_auc_score(best_actual, best_predict)
    elif curve_type == 'PRC':
        auc_best = average_precision_score(best_actual, best_predict)

    # 2.
    num_episodes = base_actual.shape[0] #, base_predict.shape, best_actual.shape, best_predict.shape
    all_actual =np.hstack((base_actual, best_actual))
    all_predict = np.hstack((base_predict, best_predict))

    import random

    num_permute = 1000
    damn = 0
    for i in range(num_permute):
        all_actual_i = all_actual
        all_predict_i = all_predict


        random.seed(i)
        random.shuffle(all_actual_i)
        actual_i = all_actual_i[:num_episodes]

        random.seed(i)
        random.shuffle(all_predict_i)
        predict_i = all_predict_i[:num_episodes]

        if curve_type == 'ROC':
            auc_i = roc_auc_score(actual_i, predict_i)
        elif curve_type == 'PRC':
            auc_i = average_precision_score(actual_i, predict_i)

        if auc_i > auc_best:
            damn += 1
    p = float(damn)/float(num_permute)
    return p


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

def map_pval_significance(p_val):
    significance = ''
    if p_val < 0.001:
        significance = '***'
    elif p_val < 0.01:
        significance = '**'
    elif p_val < 0.05:
        significance = '*'

    return significance

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
        # print e
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
        # print e
        roc_auc = float('nan')

    try:
        roc_auc_left, roc_auc_right = bootstrap_CI(actual_list, df['predict'], confident_lvl=0.95)
    except Exception as e:
        # print e
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

def add_line_breaker(astring, seg_len):
    str_len = len(astring)
    num_lines = str_len/seg_len

    new_str = ''
    for i in range(num_lines):
        new_str += astring[i*seg_len:(i+1)*seg_len] + '\n'
    if str_len%seg_len != 0:
        new_str += astring[num_lines*seg_len:]

    if new_str[-1] == '\n':
        new_str = new_str[:-1]
    return new_str

main_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')

def convert_floatnum2percentage(anum):
    if anum != anum:
        return '-'
    elif anum == 0:
        return '0'
    elif anum < 0.01:
        return '%.2f' % (anum * 100) + '%'
    elif anum < 0.1:
        return '%.1f' % (anum * 100) + '%'
    else:
        return '%.0f' % (anum * 100) + '%'

def convert_floatstr2percentage(astr):
    if astr == '':
        return '-'
    else:
        return convert_floatnum2percentage(float(astr))
    # elif astr == '1':
    #     return '100%'
    # elif astr == '0':
    #     return '0'
    # else:
    #     return str('%.0f' % (float(astr) * 100)) + '%'

def convert_floatstr2num(astr):
    if astr == '' or astr == 'inf':
        return '-'
    elif astr == '1' or astr == '0':
        return astr
    else:
        anum = float(astr)
        if anum >= 10:
            return str('%.0f'%anum)
        elif 10 > anum >= 1:
            return str('%.1f' %anum)
        else:
            return str('%.2f' % anum)

def get_lab_descriptions(lab_type, data_source='Stanford', succinct=True, line_break_at=-1):
    code2description_filepath = os.path.join(main_folder, 'machine_learning/data_conversion',
                                             'map_%s.csv' % lab_type)
    df = pd.read_csv(code2description_filepath, keep_default_na=False)
    if succinct:
        df['description'] = df['description'].apply(lambda x: x.split(',')[0].strip())
    if line_break_at != -1:
        df['description'] = df['description'].apply(lambda x: x[:line_break_at] + '\n' + x[line_break_at:])
    lab_descriptions = dict(zip(df[data_source].values.tolist(), df['description'].values.tolist()))

    if lab_type == 'panel':
        lab_descriptions['LABCBCD'] = 'Complete Blood Count w/ Differential'
        lab_descriptions['LABMETB'] = 'Basic Metabolic Panel'

    return lab_descriptions

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

main_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
stats_results_folderpath = os.path.join(main_folder, 'lab_statistics')
labs_old_stats_folder = os.path.join(stats_results_folderpath, 'data_summary_stats/')
labs_query_folder = os.path.join(stats_results_folderpath, 'query_lab_results/')

def get_queried_lab(lab, lab_type, time_limit=DEFAULT_TIMELIMIT):


    lab_query_filepath = os.path.join(labs_query_folder, lab + '.csv')
    # print lab, 'os.path.exists(lab_query_filepath)', os.path.exists(lab_query_filepath)
    if not os.path.exists(lab_query_filepath):
        df = query_to_dataframe(lab, lab_type, lab_query_filepath=lab_query_filepath)
    else:
        df = pd.read_csv(lab_query_filepath, keep_default_na=False)

    if lab_type == 'component':
        df = df[df['sop.order_status'] == 'Completed']
        df = df[(df['sop.order_time'] >= time_limit[0]) & (df['sop.order_time'] <= time_limit[1])]

        df = df.rename(columns={'sop.pat_id': 'pat_id',
                                'sop.order_time':'order_time',
                                'sor.result_in_range_yn':'result_in_range_yn',
                                'sor.result_flag':'result_flag'})
    elif lab_type == 'panel':
        df = df[df['order_status'] == 'Completed']
        df = df[(df['order_time'] >= time_limit[0]) & (df['order_time'] <= time_limit[1])]

    df.drop_duplicates(inplace=True)
    return df

def get_labvol(lab, lab_type, data_source='Stanford', time_limit=DEFAULT_TIMELIMIT):
    if data_source=='Stanford':
        df = get_queried_lab(lab, lab_type, time_limit=time_limit)
        return df.shape[0]
    elif data_source == 'UMich':
        return umich_lab_cnt.get(lab, 0)

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

def describe_lab_train_test_datasets(lab, dataset_folderpath):
    fm_io = FeatureMatrixIO()
    processed_matrix_train_path = os.path.join(dataset_folderpath, lab,
                                               '%s-normality-train-matrix-processed.tab' % lab)
    # TODO: get rid of '10000' in file name
    processed_matrix_train = fm_io.read_file_to_data_frame(processed_matrix_train_path)
    num_train_episodes = processed_matrix_train.shape[0]
    num_train_patient = len(set(processed_matrix_train['pat_id'].values.tolist()))

    processed_matrix_test_path = os.path.join(dataset_folderpath, lab,
                                              '%s-normality-test-matrix-processed.tab' % lab)
    # TODO: get rid of '10000' in file name
    processed_matrix_test = fm_io.read_file_to_data_frame(processed_matrix_test_path)
    # pd.read_csv(processed_matrix_test_path, keep_default_na=False)#fm_io.read_file_to_data_frame(processed_matrix_test_path)
    num_test_episodes = processed_matrix_test.shape[0]
    num_test_patient = len(set(processed_matrix_test['pat_id'].values.tolist()))

    return num_train_episodes, num_train_patient, num_test_episodes, num_test_patient

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
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
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

            if os.path.exists(lab_data_path):
                df = pd.read_csv(lab_data_path, keep_default_na=False)
            else:
                df = query_to_dataframe(lab, lab_type=lab_type)
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

    elif lab_type == 'mixed':
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
        query.addWhere("proc_code = '%s'" % lab)

    results = DBUtil.execute(query)

    df = pd.DataFrame(results, columns=columns)
    # if not os.path.exists(output_foldername):
    #     os.mkdir(output_foldername)
    # df.to_csv(lab_query_filepath, index=False)

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



def output_feature_importances(labs, data_source='Stanford', lab_type='panel', curr_version='10000-episodes'):
    data_set_folder = 'data-%s-%s-%s'%(data_source, lab_type, curr_version)


    def split_features(feature):
        divind = feature.find('(')
        featu = feature[:divind - 1]
        score = feature[divind + 1:-1]
        return featu, float(score)

    num_rf_best = 0


    lab_descriptions = get_lab_descriptions(lab_type=lab_type, data_source=data_source)

    ml_folderpath = '../machine_learning/'

    result_filepath = os.path.join(data_set_folder, 'RF_important_features.csv')

    '''
    Rules:
    merge proximate to last
    '''

    def grouped(feature):
        # Features that needs the first two element to identify
        complex_feature_types = ['Comorbidity', 'Team']
        for complex_feature_type in complex_feature_types:
            if complex_feature_type in feature:
                return '.'.join(feature.split('.')[:2])

        return feature.split('.')[0]

    result_df = pd.DataFrame(columns=['lab', 'feature 1', 'score 1', 'feature 2', 'score 2', 'feature 3', 'score 3'])
    from scripts.LabTestAnalysis.machine_learning import ml_utils
    for lab in labs:
        # if data_source == 'UCSF' and lab_type == 'panel':
        #
        #
        #     lab = ml_utils.map_lab(lab=lab.replace('-','/'), # TODO...
        #                            data_source=data_source,
        #                            lab_type=lab_type,
        #                            map_type='from_src')
        report_folderpath = os.path.join(ml_folderpath, data_set_folder, lab, 'random-forest')
        report_filepath = os.path.join(report_folderpath, '%s-normality-prediction-random-forest-report.tab' % lab)

        df = pd.read_csv(report_filepath, sep='\t', skiprows=0)
        rf_description = df['model'].values.tolist()[0]
        features_start = rf_description.index('features=[')
        features_str = rf_description[features_start + len('features=['):-2]

        if data_source == 'UCSF' and lab_type == 'panel':
            from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import UCSF_TOP_PANELS
            for raw_lab in UCSF_TOP_PANELS:
            # for ml_utils.map_lab()
                new_lab = ml_utils.map_lab(lab=raw_lab.replace('-', '/'),  # TODO...
                             data_source=data_source,
                             lab_type=lab_type,
                             map_type='from_src')
                # print raw_lab, new_lab
                features_str = features_str.replace(raw_lab, new_lab)

        feature_tuples = [x.strip() for x in features_str.split(',')]
        # print feature_tuples

        one_lab_dict = {}
        for feature_tuple in feature_tuples:
            feature, score = split_features(feature_tuple)
            grouped_feature = grouped(feature)
            one_lab_dict[grouped_feature] = one_lab_dict.get(grouped_feature, 0) + score
        sorted_tuples = sorted(one_lab_dict.items(), key=lambda x: x[1])[::-1]

        # one_df_dict = {'lab': lab,
        #                'feature 1': sorted_tuples[0][0],
        #                'score 1': sorted_tuples[0][1],
        #                'feature 2': sorted_tuples[1][0],
        #                'score 2': sorted_tuples[1][1],
        #                'feature 3': sorted_tuples[2][0],
        #                'score 3': sorted_tuples[2][1],
        #                }

        # result_df.append(one_df_dict)
        # print sorted_tuples

        cur_rec = [lab_descriptions.get(lab,lab)]
        for i in range(3):
            if i < len(sorted_tuples):
                cur_rec += [sorted_tuples[i][0], sorted_tuples[i][1]]
            else:
                cur_rec += ['-', '-']

        result_df.loc[len(result_df)] = cur_rec

    dict_panel = get_lab_descriptions(lab_type='panel', data_source=data_source)
    dict_component = get_lab_descriptions(lab_type='component', data_source=data_source)
    dict_misc = {'last_normality':'Prior Test Negative',
                 'AdmitDxDate':'Admit Date',
                 'order_time':'Order Time'}
    for col in result_df.columns:
        if col == 'lab':
            continue
        result_df[col] = result_df[col].apply(lambda x: dict_panel.get(x, x))
        result_df[col] = result_df[col].apply(lambda x: dict_component.get(x, x))
        result_df[col] = result_df[col].apply(lambda x: dict_misc.get(x, x))

    result_df.to_csv(result_filepath, index=False, float_format='%.2f')

if __name__ == '__main__':
    # output_feature_importances(data_source='UCSF', lab_type='panel') # TODO: do this for UCSF...

    df = query_to_dataframe(lab='LABNA')
    df.to_csv('LABNA_query_look_numerics.csv',index=False)
    # lab_type='panel'
    # print get_labvol('LABPCCR')
    #
    # lab_type = 'component'
    # print get_labvol('CR')