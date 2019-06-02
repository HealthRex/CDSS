
import os

import stats_utils

import matplotlib.pyplot as plt

import pandas as pd


def compare_algs(self, alg1, alg2, fixPPV=0.95):
    df_full = pd.read_csv(os.path.join(self.dataset_foldername,
                                       'summary-stats-allalgs-fixTrainPPV.csv'))
    df = df_full[df_full['fixTrainPPV'] == fixPPV]
    auc_1s = []
    auc_2s = []
    for lab in self.all_labs:
        df_cur = df[df['lab'] == lab]
        auc_1 = df_cur[df_cur['alg'] == alg1]['AUC'].values[0]
        auc_2 = df_cur[df_cur['alg'] == alg2]['AUC'].values[0]

        auc_1s.append(auc_1)
        auc_2s.append(auc_2)

    auc_1s = np.array(auc_1s)
    auc_2s = np.array(auc_2s)

    alg1_winFrac = float(sum(auc_1s > auc_2s)) \
                   / float(len(auc_1s))

    plt.scatter(auc_1s[auc_1s > auc_2s],
                auc_2s[auc_1s > auc_2s],
                color='b', label='%s wins' % alg1)
    plt.scatter(auc_1s[auc_1s < auc_2s],
                auc_2s[auc_1s < auc_2s],
                color='r', label='%s wins' % alg2)
    plt.scatter(auc_1s[auc_1s == auc_2s],
                auc_2s[auc_1s == auc_2s],
                color='g', label='equal')
    plt.xlabel('%s AUC, winning %.2f' % (alg1, alg1_winFrac))
    plt.ylabel('%s AUC, winning %.2f' % (alg2, 1. - alg1_winFrac))
    plt.legend()
    plt.show()

def draw__Potential_Savings(statsByLab_folderpath, scale=None, targeted_PPV=0.95,
                            result_label='', use_cached_fig_data=False, price_source='medicare'):
    '''
    Drawing Figure 4 in the main text.

    :return:
    '''

    df = pd.read_csv(os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv'),
                     keep_default_na=False)
    df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]
    df = df.drop_duplicates()

    result_foldername = 'Fig4_Potential_Savings/'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)

    '''
    Hierarchy:

    '''

    fig_filename = 'Potential_Savings_PPV_%.2f_%s_%s.png' % (targeted_PPV, result_label, price_source)
    fig_path = os.path.join(result_folderpath, fig_filename)
    data_filename = 'Potential_Savings_%.2f_%s_%s.csv' % (targeted_PPV, result_label, price_source)
    data_path = os.path.join(result_folderpath, data_filename)

    if os.path.exists(data_path) and use_cached_fig_data:
        df = pd.read_csv(data_path, keep_default_na=False)

    else:
        # df = df[df['lab'] != 'LABNA']  # TODO: fix LABNA's price here

        df = df[df[price_source] != '']
        df[price_source] = df[price_source].astype(float)

        df['TP_cost'] = df['TP'] * df['total_cnt'] * df[price_source]
        df['FP_cost'] = df['FP'] * df['total_cnt'] * df[price_source]
        df['FN_cost'] = df['FN'] * df['total_cnt'] * df[price_source]
        df['TN_cost'] = df['TN'] * df['total_cnt'] * df[price_source]
        df['total_cost'] = df['TP_cost'] + df['FP_cost'] + df['FN_cost'] + df['TN_cost']

        df = df[['lab', 'TP_cost', 'FP_cost', 'FN_cost', 'TN_cost', 'total_cost']]

        df = df.sort_values('TP_cost')
        df.to_csv(data_path, index=False)

    print 'Total saved money:', (df['TP_cost']).sum() * 66440. / 1000 / 3
    df = df.iloc[-20:]

    df['TP_cost'] = df['TP_cost'] * scale
    df['FP_cost'] = df['FP_cost'] * scale
    df['FN_cost'] = df['FN_cost'] * scale
    df['TN_cost'] = df['TN_cost'] * scale
    df['total_cost'] = df['total_cost'] * scale

    df['lab_description'] = df['lab'].apply(
        lambda x: self.lab_descriptions[x])

    '''
    Cost per 1000 pat enc, translate to annual cost
    '''
    df['Annual TP cost'] = df['TP_cost'] * stats_utils.NUM_DISTINCT_ENCS / 3. / 1000.
    df[['lab_description', 'Annual TP cost']].sort_values('Annual TP cost', ascending=False).to_csv(
        os.path.join(result_folderpath, 'info_column.csv'), index=False, float_format='%.0f')

    # fig, ax = plt.subplots(figsize=(8, 6))
    fig, ax = plt.subplots(figsize=(10, 6))  # LABBLC has too long name!
    ax.barh(df['lab_description'], df['total_cost'],
            color='royalblue', alpha=1, label='true negative')  # 'True Positive@0.95 train_PPV'

    ax.barh(df['lab_description'], df['TP_cost'] + df['FN_cost'] + df['FP_cost'],
            color='orangered', alpha=1, label='false positive')

    ax.barh(df['lab_description'], df['TP_cost'] + df['FN_cost'],
            color='gold', alpha=1, label='false negative')

    ax.barh(df['lab_description'], df['TP_cost'],
            color='forestgreen', alpha=1, label='true positive')

    ax.set_xticklabels(['0', '$5,000', '$10,000', '$15,000', '$20,000', '$25,000', '$30,000', '$35,000'])

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(12)

    plt.xlabel('Medicare fee per 1000 patient encounters',
               fontsize=14)  # 'Total Amount (in %s) in 2014.07-2017.06, targeting PPV=%.2f'%(unit, targeted_PPV)
    # plt.xticks(range(0, 15001, 5000))
    # plt.xlim([0,20000])

    plt.tight_layout()
    plt.savefig(fig_path)

    plt.show()

def draw__Comparing_Savable_Fractions(self, statsByLab_folderpath,
                                      target_PPV=0.95,
                                      use_cache=True):
    '''
    Targeting at PPV=0.95, what are the savable fractions from each method?

    :return:
    '''
    result_foldername = 'Fig5_Comparing_Savable_Fractions/'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)

    result_tablename = 'Comparing_Savable_Fractions_PPV_%.2f.csv' % target_PPV
    result_tablepath = os.path.join(result_folderpath, result_tablename)

    result_figname = 'Comparing_Savable_Fractions_PPV_%.2f.png' % target_PPV
    result_figpath = os.path.join(result_folderpath, result_figname)

    if use_cache and os.path.exists(result_tablepath):
        df_twomethods = pd.read_csv(result_tablepath, keep_default_na=False)
        # print df_twomethods
        savable_fractions_baseline1 = stats_utils.pandas2dict(df_twomethods, key='lab',
                                                              val='savable_fraction_baseline1')
        savable_fractions_baseline2 = stats_utils.pandas2dict(df_twomethods, key='lab',
                                                              val='savable_fraction_baseline2')
        savable_fractions_mlmodel = stats_utils.pandas2dict(df_twomethods, key='lab',
                                                            val='savable_fraction_mlmodel')
    else:

        labs = self.all_labs

        mlByLab_folder = statsByLab_folderpath.replace("lab_statistics", "machine_learning")

        '''
        Baseline 1: consecutive normalites in the last week

        The simple rule is: As long as the number of consecutive normalites
        reaches a threshold, then do not order; otherwise, go ahead and order. 
        Advantage: Provides a way to assign conservativeness
        Disadvantage: Too stringent, very few patients will qualify; in most cases have to order. 
        '''
        savable_fractions_baseline1 = {}
        for lab in labs:
            days, normality_lists = stats_utils.get_prevday2normalities(lab, mlByLab_folder, source="train")
            normality_fractions = [float(sum(x)) / float(len(x)) for x in normality_lists]

            '''
            Pick a threshold
            '''
            day_thres = float('inf')
            for i, normality_fraction in enumerate(normality_fractions):
                if normality_fraction > target_PPV:
                    day_thres = days[i]
                    break

            days, normality_lists = stats_utils.get_prevday2normalities(lab, mlByLab_folder, source="test")
            normality_fractions = [float(sum(x)) / float(len(x)) for x in normality_lists]
            normality_cnts = [len(x) for x in normality_lists]

            '''
            Count fraction above this thres
            '''
            savable_cnt = 0
            for i, normality_fraction in enumerate(normality_fractions):
                if days[i] >= day_thres:
                    savable_cnt += normality_cnts[i]
            savable_fraction = float(savable_cnt) / float(sum(normality_cnts))
            savable_fractions_baseline1[lab] = savable_fraction

            '''
            For the rule of "passing a number of days, then all set 'normal',
            the normal rate is equals to the PPV. "
            '''

        df_baseline1 = stats_utils.dict2pandas(savable_fractions_baseline1, key='lab',
                                               val='savable_fraction_baseline1')

        '''
        Baseline 2: last order + prevalence

        Since there is no threshold to choose, the rule is to see whether the metric 
            gives a > 0.95 PPV for each lab in the train set. 

        If yes, then do not order (save!) when test prediction says 'Normal'.
        If no, then always order (never save). 
        '''
        savable_fractions_baseline2 = {}
        for lab in labs:
            train_prevalence, train_thres = stats_utils.check_baseline2(lab, mlByLab_folder, source="train")

            if train_thres == -1:  #
                savable_fractions_baseline2[lab] = 0
            else:
                savable_fractions_baseline2[lab] = stats_utils.check_baseline2(lab, mlByLab_folder, source="test",
                                                                               picked_prevalence=train_prevalence,
                                                                               picked_thres=train_thres)
            print lab, savable_fractions_baseline2[lab]
        df_baseline2 = stats_utils.dict2pandas(savable_fractions_baseline2, key='lab',
                                               val='savable_fraction_baseline2')

        '''
        Machine learning model
        '''
        # TODO: counts in the file needs update
        df_mlmodel = pd.read_csv('data_performance_stats/best-alg-panel-summary-fix-trainPPV.csv',
                                 keep_default_na=False)
        df_mlmodel = df_mlmodel[(df_mlmodel['train_PPV'] == 0.95) & df_mlmodel['lab'].isin(labs)]
        df_mlmodel['savable_fraction_mlmodel'] = (df_mlmodel['TP'] + df_mlmodel['FP'])  # .round(5)
        df_mlmodel = df_mlmodel[['lab', 'savable_fraction_mlmodel']]

        savable_fractions_mlmodel = stats_utils.pandas2dict(df_mlmodel, key='lab', val='savable_fraction_mlmodel')

        df_3methods = df_baseline1.merge(df_baseline2, on='lab', how='left')
        df_3methods = df_3methods.merge(df_mlmodel, on='lab', how='left')
        df_3methods.to_csv(result_tablepath, index=False)

    stats_utils.plot_subfigs([savable_fractions_baseline1,
                              savable_fractions_baseline2,
                              savable_fractions_mlmodel],
                             colors=('blue', 'green', 'orange'),
                             result_figpath=result_figpath)

def print_HosmerLemeshowTest():
        labs = NON_PANEL_TESTS_WITH_GT_500_ORDERS
        alg = 'random-forest'  # 'regress-and-round' #'random-forest'

        p_vals = []

        for lab in labs:
            df_new = pd.read_csv(
                '../machine_learning/data-panels-calibration-sigmoid/%s/%s/%s-normality-prediction-%s-direct-compare-results.csv'
                % (lab, alg, lab, alg),
                keep_default_na=False)
            actual = df_new['actual'].values
            predict = df_new['predict'].values
            p_val = stats_utils.Hosmer_Lemeshow_Test(actual_labels=actual, predict_probas=predict)
            p_vals.append(p_val)

        print sorted(p_vals)

def get_best_calibrated_labs(statsByLab_folderpath, top_k=20, worst=False):
    df_fix_train = pd.read_csv(statsByLab_folderpath + "/summary-stats-bestalg-fixTrainPPV.csv",
                               keep_default_na=False)
    df_fix_train['abs_PPV_diff'] = (df_fix_train['targeted_PPV_fixTrainPPV'] - df_fix_train['PPV'].apply(
        lambda x: float(x) if x != '' else float('nan'))).abs()

    lab_diff = {}
    for lab in self.all_labs:
        cur_tot_diff = df_fix_train[df_fix_train['lab']==lab]['abs_PPV_diff'].values.sum()
        lab_diff[lab] = cur_tot_diff

    if not worst:
        best_labs = [x[0] for x in sorted(lab_diff.iteritems(), key=lambda (k,v):v)[:top_k]]
    else:
        best_labs = [x[0] for x in sorted(lab_diff.iteritems(), key=lambda (k, v): v)[-top_k:]]
    print best_labs
    # for lab in best_labs:
    #     print df_fix_train[df_fix_train['lab']==lab][['lab', 'targeted_PPV_fixTrainPPV', 'PPV']].to_string(index=False)
    df_res = df_fix_train[df_fix_train['lab'].isin(best_labs)][['lab', 'targeted_PPV_fixTrainPPV', 'PPV', 'abs_PPV_diff']]#.sort_values(['lab','targeted_PPV_fixTrainPPV'])
    df_res_long = df_res.pivot(index='lab', columns='targeted_PPV_fixTrainPPV', values='PPV').reset_index()
    # print df_res_long
    df_res_long['abs_PPV_diff'] = df_res_long['lab'].map(lab_diff)
    df_res_long = df_res_long.rename(columns={0.80:'target 0.80', 0.90:'target 0.90', 0.95:'target 0.95', 0.99:'target 0.99'})
    df_res_long['lab'] = df_res_long['lab'].apply(lambda x: lab_descriptions[x])
    df_res_long.sort_values('abs_PPV_diff').drop(columns=['abs_PPV_diff']).to_csv(statsByLab_folderpath+'/best_calibrated_is_worst_%s.csv'%worst, index=False)

def draw__Comparing_PPVs(self, statsByLab_folderpath, include_labnames=False):
    summary_filename = 'summary-stats-bestalg-fixTrainPPV.csv'
    summary_filepath = os.path.join(statsByLab_folderpath, summary_filename)
    df = pd.read_csv(summary_filepath, keep_default_na=False)
    # print df.shape
    df = df[['lab','targeted_PPV_fixTrainPPV','PPV']]
    df = df[df['PPV']!='']

    result_foldername = 'Fig3_Comparing_PPVs/'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)

    result_figurename = 'Comparing_PPVs.png'
    result_figurepath = os.path.join(result_folderpath, result_figurename)
    labs = df['lab'].values.tolist()

    # print df['targeted_PPV_fixTrainPPV'].values.tolist()
    target_PPVs = df['targeted_PPV_fixTrainPPV'].values.tolist()
    true_PPVs = [float(x) for x in df['PPV'].values.tolist() if x!='']

    fig, ax = plt.subplots(figsize=(8,6))
    plt.scatter(target_PPVs, true_PPVs)
    # plt.xlim([0, 1])
    # plt.ylim([0,1])

    if include_labnames:
        texts = []
        for i, txt in enumerate(labs):
            texts.append(ax.annotate(txt, (target_PPVs[i], true_PPVs[i])))

    plt.xlabel('Targetd PPV')
    plt.ylabel('Actual PPV')

    plt.savefig(result_figurepath)

def PPV_guideline(self, statsByLab_folderpath):

    df_fix_train = pd.read_csv(statsByLab_folderpath + "/summary-stats-bestalg-fixTrainPPV.csv",
                               keep_default_na=False)

    range_bins = [0.99] + np.linspace(0.95, 0.5, num=10).tolist()
    columns = ['Target PPV', 'Total labs', 'Valid labs']
    columns += ['[0.99, 1]']
    for i in range(len(range_bins) - 1):
        columns += ['[%.2f, %.2f)' % (range_bins[i + 1], range_bins[i])]

    rows = []
    actual_PPVs = {}
    actual_median_PPV = {}
    for targeted_PPV in [0.8, 0.90, 0.95, 0.99][::-1]: # TODO: what is the problem with 0.9? LABHIVWBL
        cur_row = [targeted_PPV]

        PPVs_from_train = df_fix_train.ix[df_fix_train['targeted_PPV_fixTrainPPV']==targeted_PPV, ['PPV']]
        cur_row.append(PPVs_from_train.shape[0]) # "Total number of labs:"

        PPVs_from_train = PPVs_from_train.dropna()['PPV'].values
        PPVs_from_train = np.array([float(x) for x in PPVs_from_train if x!='']) #TODO: why?
        actual_PPVs[targeted_PPV] = PPVs_from_train.tolist()

        vaild_PPV_num = PPVs_from_train.shape[0]
        cur_row.append(vaild_PPV_num) # "Valid number of labs:"

        print "When target at PPV %.2f, the mean/median PPV among %i labs is %.3f/%.3f, std is %.3f"\
              %(targeted_PPV, vaild_PPV_num, np.mean(PPVs_from_train), np.median(PPVs_from_train), np.std(PPVs_from_train))
        actual_median_PPV[targeted_PPV] = np.median(PPVs_from_train)

        cur_cnt = sum(PPVs_from_train >= 0.99)
        cur_row.append(cur_cnt)

        for i in range(len(range_bins)-1):
            cur_cnt = sum((range_bins[i+1] <= PPVs_from_train) & (PPVs_from_train < range_bins[i]))
            cur_row.append(cur_cnt)

        rows.append(cur_row)

    actual_PPVs_df = pd.DataFrame.from_dict(actual_PPVs, orient='index').transpose()
    actual_PPVs_df = actual_PPVs_df.melt(var_name='Targeted PPV', value_name='Actual PPVs')
    import seaborn
    # seaborn.set(style="ticks", palette="colorblind")
    actual_PPVs_df['side'] = actual_PPVs_df['Targeted PPV'].apply(lambda x:0)
    actual_PPVs_df['side'].iloc[-1]=-999

    fig, ax = plt.subplots(figsize=(8,6))
    seaborn.violinplot(x='Targeted PPV', y='Actual PPVs', data=actual_PPVs_df, hue='side', split=True,
                       #palette = ['o']
                       )

    for i, v in enumerate([0.8, 0.90, 0.95, 0.99]):
        print actual_median_PPV
        ax.text(i, actual_median_PPV[v], '%.3f'%actual_median_PPV[v], color='k')

    leg = plt.gca().legend()
    leg.remove()
    plt.ylim([0.35,1.15])
    plt.savefig(os.path.join(statsByLab_folderpath, 'violinplot.png'))

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(statsByLab_folderpath + "/predict_power_%ss.csv"%self.lab_type, index=False)

def draw__predicted_normal_fractions(self, statsByLab_folderpath, targeted_PPV):
    labs_stats_filepath = os.path.join(statsByLab_folderpath, 'summary-stats-bestalg-fixTrainPPV.csv')

    df = pd.read_csv(labs_stats_filepath)

    df = df[df['targeted_PPV_fixTrainPPV'] == targeted_PPV]

    result_foldername = 'Predicted_Normal_Fractions'
    result_folderpath = os.path.join(statsByLab_folderpath, result_foldername)
    if not os.path.exists(result_folderpath):
        os.mkdir(result_folderpath)
    result_figname = 'Predicted_Normal_Fractions_%.2f.png'%targeted_PPV
    result_figpath = os.path.join(result_folderpath, result_figname)

    df['predicted_normal'] = (df['TP'] + df['FP']) / df['num_test_episodes']

    df['description'] = df['lab'].apply(lambda x: self.lab_descriptions.get(x, x))
    # print df[['description', 'predicted_normal']].sort_values(['predicted_normal'], ascending=False).to_string(index=False)

    predicted_normal_fractions = np.linspace(0, 1, num=11)
    nums_labs = []
    for predicted_normal_fraction in predicted_normal_fractions:
        df_predicted_normal = df[df['predicted_normal'] > predicted_normal_fraction]#[['lab', 'predicted_normal']]
        num_labs = df_predicted_normal.shape[0]
        nums_labs.append(num_labs)

        if predicted_normal_fraction == 0.5:
            print 'over-utilized labs:', df_predicted_normal['lab'].values.tolist()

        if predicted_normal_fraction == 0.9:
            these_labs = df_predicted_normal['lab'].values.tolist()
            print 'highly over-utilized labs:', [self.lab_descriptions[x] for x in these_labs]
    print zip(predicted_normal_fractions, nums_labs)
    plt.scatter(predicted_normal_fractions, nums_labs)
    plt.xlabel('Predicted normal fraction, targeting at PPV=%.2f' % targeted_PPV)
    plt.ylabel('Number of labs')
    plt.savefig(result_figpath)


'''
Old version
'''
def comparing_components(self, stats_folderpath, target_PPV=0.95):
    stats_filename = 'summary-stats-bestalg-fixTrainPPV.csv'

    labs_important = stats_utils.get_important_labs(lab_type='component')

    stanford_filepath = os.path.join(stats_folderpath, 'data-Stanford-component-%s'%self.curr_version, stats_filename)
    umich_filepath = os.path.join(stats_folderpath, 'data-UMich-component-%s'%self.curr_version, stats_filename)
    ucsf_filepath = os.path.join(stats_folderpath, 'data-UCSF-component-%s'%self.curr_version, stats_filename)



    df_stanford = pd.read_csv(stanford_filepath, keep_default_na=False)
    df_stanford = df_stanford[df_stanford['targeted_PPV_fixTrainPPV']==target_PPV]

    df_umich = pd.read_csv(umich_filepath, keep_default_na=False)
    df_umich = df_umich[df_umich['targeted_PPV_fixTrainPPV'] == target_PPV]

    df_ucsf = pd.read_csv(ucsf_filepath, keep_default_na=False)
    df_ucsf = df_ucsf[df_ucsf['targeted_PPV_fixTrainPPV'] == target_PPV]

    for df in [df_stanford, df_umich, df_ucsf]:
        df['total_cnt'] = df['TP'] + df['FP'] + df['TN'] + df['FN']
        df['TP'] = df['TP'] / df['total_cnt']
        df['FP'] = df['FP'] / df['total_cnt']
        df['TN'] = df['TN'] / df['total_cnt']
        df['FN'] = df['FN'] / df['total_cnt']


    df_stanford = df_stanford[df_stanford['lab'].isin(labs_important)]
    df_stanford['predicted_normal_Stanford'] = df_stanford['TP']+df_stanford['FP']

    df_stanford = df_stanford.rename(columns={'AUC':'AUC_Stanford',
                                              #'baseline2_ROC':'B_ROC_Stanford',
                                              'PPV':'PPV_Stanford',
                                              'TP': 'TP_Stanford',
                                              'FP': 'FP_Stanford',
                                              'TN': 'TN_Stanford',
                                              'FN': 'FN_Stanford'
                                              })


    #umich_replace = {'SOD':'NA', 'POT':'K', 'CREAT': 'CR'}
    df_convert_table_UMich = pd.read_csv('../machine_learning/data_conversion/map_UMich_component_raw2code.csv', keep_default_na=False)
    umich_replace = dict(zip(df_convert_table_UMich['raw'].values.tolist(), df_convert_table_UMich['lab'].values.tolist()))
    df_umich['lab'] = df_umich['lab'].apply(lambda x: umich_replace[x] if x in umich_replace else x)
    df_umich['predicted_normal_UMich'] = df_umich['TP'] + df_umich['FP']
    df_umich = df_umich.rename(columns={'AUC': 'AUC_UMich',
                                        #'baseline2_ROC': 'B_ROC_UMich',
                                              'PPV':'PPV_UMich',
                                              'TP': 'TP_UMich',
                                              'FP': 'FP_UMich',
                                              'TN': 'TN_UMich',
                                              'FN': 'FN_UMich'
                                              })

    # ucsf_replace = {'CREAT': 'CR'}
    df_convert_table_UCSF = pd.read_csv('../machine_learning/data_conversion/map_UCSF_component_raw2code.csv',
                                         keep_default_na=False)
    ucsf_replace = dict(
        zip(df_convert_table_UCSF['raw'].values.tolist(), df_convert_table_UCSF['lab'].values.tolist()))
    df_ucsf['lab'] = df_ucsf['lab'].apply(lambda x: ucsf_replace[x] if x in ucsf_replace else x)
    df_ucsf['predicted_normal_UCSF'] = df_ucsf['TP'] + df_ucsf['FP']
    df_ucsf = df_ucsf.rename(columns={'AUC': 'AUC_UCSF',
                                      #'baseline2_ROC': 'B_ROC_UCSF',
                                              'PPV':'PPV_UCSF',
                                        'TP': 'TP_UCSF',
                                        'FP': 'FP_UCSF',
                                        'TN': 'TN_UCSF',
                                        'FN': 'FN_UCSF'
                                        })

    columns = ['lab', 'AUC', 'PPV', 'predicted_normal']#, 'TP', 'FP', 'TN', 'FN']
    columns_stanford = [x+'_Stanford' if x !='lab' else x for x in columns]
    columns_umich = [x+'_UMich' if x !='lab' else x for x in columns]
    columns_ucsf = [x+'_UCSF' if x !='lab' else x for x in columns]

    merged_df = pd.merge(df_stanford[columns_stanford], df_umich[columns_umich], how='left', on='lab')
    merged_df = pd.merge(merged_df, df_ucsf[columns_ucsf], how='left', on='lab')

    columns_show = [x.replace('_',' ') for x in merged_df.columns]

    merged_df = merged_df.rename(columns=dict(zip(merged_df.columns, columns_show)))

    columns_merged = merged_df.columns.tolist()
    columns_merged.remove('lab')
    columns_merged = ['lab'] + sorted(columns_merged)
    merged_df['lab'] = merged_df['lab'].apply(lambda x: self.lab_descriptions.get(x,x))

    merged_df['PPV Stanford'] = pd.to_numeric(merged_df['PPV Stanford'])
    merged_df['PPV UCSF'] = pd.to_numeric(merged_df['PPV UCSF'])
    merged_df['PPV UMich'] = pd.to_numeric(merged_df['PPV UMich'])

    for col_merged in merged_df.columns.values.tolist():
        if col_merged != 'lab' and 'AUC' not in col_merged:
            merged_df[col_merged] = merged_df[col_merged].apply(lambda x: stats_utils.convert_floatnum2percentage(x))
        elif 'AUC' in col_merged:
            merged_df[col_merged] = merged_df[col_merged].apply(lambda x: '%.2f'%x)
    merged_df[columns_merged].to_csv(os.path.join(stats_folderpath, 'components_comparisons.csv'), index=False)

def plot_cartoons(self, ml_folderpath):

    alg = 'random-forest'

    labs = ['LABPTT', 'LABLDH', 'LABTNI']
    local_lab_descriptions = {'LABPTT':"PTT PARTIAL\nTHROMBOPLASTIN TIME\n",
                              'LABLDH':"LDH TOTAL\nSERUM / PLASMA\n",
                              'LABTNI':"TROPONIN I\n"}

    col = 3
    row = len(labs)/col
    has_left_labs = (len(labs)%col!=0)

    fig_width, fig_heights = col * 3., 12. / col
    plt.figure(figsize=(fig_width, fig_heights))

    for i in range(row):
        for j in range(col):
            ind = i * col + j
            lab = labs[ind]

            df = pd.read_csv(ml_folderpath + "/%s/%s/direct_comparisons.csv"
                             % (lab, alg), keep_default_na=False)
            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            df1 = pd.read_csv(ml_folderpath + "/%s/%s/%s-normality-prediction-%s-report.tab"
                              % (lab, alg, lab, alg), sep='\t', keep_default_na=False)
            auc = df1['roc_auc'].values[0]

            if not has_left_labs:
                plt.subplot2grid((row, col), (i, j))
            else:
                plt.subplot2grid((row+1, col), (i, j))
            plt.hist(scores_actual_0, bins=30, alpha=0.8, color='r', label="abnormal")
            plt.hist(scores_actual_1, bins=30, alpha=0.8, color='g', label="normal")
            plt.xlim([0, 1])
            plt.ylim([0, 500])
            plt.xticks([])
            plt.yticks([])
            plt.xlabel(local_lab_descriptions[lab] + 'auroc=%.2f'%auc)
            if ind==0:
                plt.legend()

    # plt.xlabel("%s score for %s"%(alg,lab))
    # plt.ylabel("num episodes, auroc=%f"%auc)
    # plt.legend()
    if has_left_labs:
        i = row
        for j in range(len(labs)%col):
            ind = i * col + j
            lab = labs[ind]

            df = pd.read_csv(ml_folderpath + "/%s/%s/direct_comparisons.csv"
                             % (lab, alg), keep_default_na=False)
            scores_actual_0 = df.ix[df['actual'] == 0, 'predict'].values
            scores_actual_1 = df.ix[df['actual'] == 1, 'predict'].values

            df1 = pd.read_csv(ml_folderpath + "/%s/%s/%s-normality-prediction-%s-report.tab"
                              % (lab, alg, lab, alg), sep='\t', keep_default_na=False)
            auc = df1['roc_auc'].values[0]

            if not has_left_labs:
                plt.subplot2grid((row, col), (i, j))
            else:
                plt.subplot2grid((row + 1, col), (i, j))
            plt.hist(scores_actual_0, bins=30, alpha=0.8, color='r', label="abnormal")
            plt.hist(scores_actual_1, bins=30, alpha=0.8, color='g', label="normal")
            plt.xlim([0, 1])
            plt.ylim([0, 500])
            plt.xticks([])
            plt.yticks([])
            plt.xlabel(self.lab_descriptions[lab])

    plt.tight_layout()

    plt.savefig('cartoons_%ss.png'%self.lab_type)

def test(self, lab):
    results = stats_utils.query_lab_usage__df(lab=lab,
                                              lab_type='panel',
                                              time_start='2014-01-01',
                                              time_end='2016-12-31')
    df = pd.DataFrame(results, columns=['pat_id', 'order_time', 'result'])

    prevday_cnts_dict = stats_utils.get_prevday_cnts__dict(df)