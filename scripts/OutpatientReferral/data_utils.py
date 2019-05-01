
''''''

import os
import pandas as pd
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)

import data_config

from datetime import datetime
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
time_format = '%Y-%m-%d %H:%M:%S'

import queries

from google.cloud import bigquery

testdf = pd.DataFrame({'test':[1,2,3]})

result_folderpath = 'queried_results'
if not os.path.exists(result_folderpath):
    os.mkdir(result_folderpath)

def setup_client(jsonkey_filepath):
    print 'Setting up client...'
    client = bigquery.Client.from_service_account_json(jsonkey_filepath)
    return client

def make_bigquery(query, client, project_id):
    print 'Making bigquery...'
    df = client.query(query, project=project_id).to_dataframe()

    return df

def get_queried_data(query):
    ''''''

    '''
    Alert: Python hash function which potentially could be random? (not now)
    '''
    query_id = hash(query)

    cached_filepath = os.path.join(result_folderpath, 'queried_data_%d.csv'%query_id)

    if os.path.exists(cached_filepath):
        print "Found cached query data, now loading..."
        df = pd.read_csv(cached_filepath, comment='#', sep='\t')

    else:
        print "Making new query..."
        print "set client path to gcp key" 
        client = setup_client('/Users/jonc101/Documents/Biomedical_Data_Science/gcp/gcp_key.json')
        # client = setup_client('MiningClinicalDecisions_Song.json')
        project_id = 'mining-clinical-decisions'
        df = make_bigquery(query, client=client, project_id=project_id)

        f = open(cached_filepath, 'a')
        f.write('#' + query.replace('\n', '\n#') + '\n')
        df.to_csv(f, index=False, sep='\t', encoding = 'utf-8')
        f.close()

    return df

def calc_PC_cnts(df_full):
    order_typeCnt_global = df_full[['specialty_order', 'specialty_name']] \
        .groupby('specialty_order')['specialty_name'] \
        .apply(list).apply(Counter).to_dict()
    order_isPCCnt_global = {}
    # # TODO: be careful of missing specialty departments, could potentially all be PC?
    for order, cnter in order_typeCnt_global.items():
        order_isPCCnt_global[order] = {'PC_cnt': cnter['Primary Care'],
                                            'nonPC_cnt': sum(cnter.values()) - cnter['Primary Care']}
    return order_isPCCnt_global

from data_config import referral_to_specialty_dict
from collections import Counter

def truncate_icd10(icd10):
    try:
        return icd10.split('.')[0]
    except AttributeError: # empty value 'nan'
        return ''

def plot_visit_cnts(df):
    df_visitCnts = df[['referral_enc_id', 'specialty_enc_id']]\
                    .groupby('referral_enc_id')['specialty_enc_id']\
                    .count().reset_index().rename(columns={'specialty_enc_id':'visit_cnt'})
    plt.hist(df_visitCnts['visit_cnt'])
    plt.show()
    pass

def test_plotVisitCnts():
    df = pd.read_csv('queried_results/queried_data_2690237133563743535_sample.csv')
    print df.head()
    plot_visit_cnts(df)




class ReferralDataMunger():

    def __init__(self, referral, df_full, newPatientOnly=False, to_truncate_icd10=True, verbose=False):
        self.referral = referral
        self.referral_code = referral.replace("REFERRAL TO ", "").replace(" ","-").replace("/","-")
        self.specialty = referral_to_specialty_dict[referral]
        self.df_full = df_full
        if to_truncate_icd10:
            self.df_full['referral_icd10'] = self.df_full['referral_icd10'].fillna('NA').apply(lambda x: truncate_icd10(x))

        '''Making df local (only to the current referral)'''
        self.df = self.df_full[(self.df_full['referral_name'] == referral)
                               & (self.df_full['specialty_name'] == self.specialty)].copy()

        self.order_isPCCnt_global = calc_PC_cnts(self.df_full)

    def plot_waiting_times(self, ax):

        df_tmp_timediff = self.df[
            ['referral_enc_id', 'referral_time', 'specialty_time']].copy().drop_duplicates()
        df_tmp_timediff['specialty_timestamp'] = \
            df_tmp_timediff['specialty_time'].apply(lambda x: datetime.strptime(x, time_format))
        df_tmp_timediff['referral_timestamp'] = \
            df_tmp_timediff['referral_time'].apply(lambda x: datetime.strptime(x, time_format))
        df_tmp_timediff['time_diff'] = df_tmp_timediff['specialty_timestamp'] \
                                       - df_tmp_timediff['referral_timestamp']

        print 'Train sample size for waiting time:', df_tmp_timediff['time_diff'].shape[0]
        all_waiting_days = df_tmp_timediff['time_diff'].apply(lambda x: x.days)

        if not ax:
            plt.hist(all_waiting_days, bins=15)
            plt.xlabel('Waiting days for %s' % self.referral)
            plt.xlim([0, 30*6]) # six month by default

            plt.savefig('figures/waiting_time_%s.png' % self.referral_code)
            plt.clf()
        else:
            ax.hist(all_waiting_days, bins=15)
            ax.set_title(self.referral_code)
            ax.set_xlim([0, 30 * 6])  # six month by default

            ax.get_xaxis().set_ticks([])

        # return median and IQR
        return all_waiting_days.median(), \
               all_waiting_days.quantile(0.25), \
               all_waiting_days.quantile(0.75)

    def explore_referral(self, top_k=5, rank_by='abs'):
        icd10_category_mapping = data_config.get_icd10_category_mapping()
        #print 'Top icd10s (categories) and %s_cnt:'%rank_by
        # if rank_by == 'abs':
        #     icd10_cnts = self.N_to_ri.most_common(top_k)
        # elif rank_by == 'tfidf':
        #     icd10_cnts = self.N_to_ri_tfidf.most_common(top_k)
        icd10_cnts = self.get_most_common_icd10s(top_k, rank_by=rank_by)

        icd10s = [x[0] for x in icd10_cnts]
        cnts = [x[1] for x in icd10_cnts]
        categories = [icd10_category_mapping[x] for x in icd10s]

        pd.DataFrame({'icd10':icd10s,
                      '%s_cnt'%rank_by:cnts,
                      'category':categories
                        })[['icd10', 'category', '%s_cnt'%rank_by]]\
            .to_csv('explore_%s_by_%s.csv'%(self.referral, rank_by), index=False)
        # for i in range(len(icd10s)):
        #     print "%s (%s), %f" % (icd10s[i], categories[i], icd10_cnts[i][1])

    def get_cnt(self, referral=None, order=None, icd10=None):
        cur_df = self.df_full[['referral_enc_id', 'referral_name', 'specialty_name', 'specialty_order', 'referral_icd10']].copy()

        included_columns = ['referral_enc_id']
        if referral:
            specialty = referral_to_specialty_dict[referral]
            cur_df = cur_df[(cur_df['referral_name'] == referral) & \
                            (cur_df['specialty_name'] == specialty)]
            included_columns.append('referral_name')

        if order:
            cur_df = cur_df[cur_df['specialty_order'] == order]
            included_columns.append('specialty_order')

        if icd10:
            cur_df = cur_df[cur_df['referral_icd10'] == icd10]
            included_columns.append('referral_icd10')

        return float(cur_df[included_columns].drop_duplicates().shape[0]) #

    def get_most_common_orders(self, icd10, top_k, rank_by='abs'):
        cur_df = self.df[self.df['referral_icd10'] == icd10][['referral_enc_id', 'referral_name', 'specialty_name', 'specialty_order', 'referral_icd10']]\
            .drop_duplicates()
        order_abscnts = Counter(cur_df['specialty_order'])

        if rank_by=='abs':
            return order_abscnts.most_common(top_k)

        else:
            order_tfidfs = Counter()
            for order, abscnt in order_abscnts.items():
                order_tfidfs[order] = float(abscnt) * self.get_cnt() \
                                    / (self.get_cnt(order=order)
                                       * self.get_cnt(referral=self.referral, icd10=icd10))
            return order_tfidfs.most_common(top_k)

    def get_most_common_icd10s(self, top_k, rank_by='abs'):
        cur_df = self.df
        icd10_abscnts = Counter(cur_df['referral_icd10'])

        if rank_by == 'abs':
            return icd10_abscnts.most_common(top_k)

        else:
            icd10_tfidfs = Counter()
            for icd10, abscnt in icd10_abscnts.items():
                icd10_tfidfs[icd10] = float(abscnt) * self.get_cnt() \
                                      / (self.get_cnt(icd10=icd10)
                                         * self.get_cnt(referral=self.referral))
            return icd10_tfidfs.most_common(top_k)


    def generate_order_stats(self, icd10, top_k=5, rank_by='abs'):
        ''''''

        '''
        Find out the top k orders for that icd10
        '''
        df_res = pd.DataFrame(columns=['order', 'N(o)', 'N(o,r)', 'N(o,r,i)', 'N(r,i)',
                                       'PPV', 'RelaRisk', 'TFIDF', 'PrimaryCareRatio'
                                       #'PC_cnt', 'nonPC_cnt'
                                       ])
        # print self.N_to_ri.most_common(top_k)
        # if rank_by == 'abs':
        #     common_absCnt_locals = self.N_to_rio[icd10].most_common(top_k)
        # elif rank_by == 'tfidf':
        #     common_absCnt_locals = self.N_to_rio_tfidf[icd10].most_common(top_k)

        top_orders_cnts = self.get_most_common_orders(icd10, top_k, rank_by=rank_by)
        print top_orders_cnts

        for order, _ in top_orders_cnts:  # TODO: when tfidf?
            '''
            Order_name
            '''
            cur_order_summary = {'order':order}

            '''
            Preva
            '''
            cur_order_summary['N(o)'] = self.get_cnt(order=order)

            '''
            Preva_referrel
            '''
            cur_order_summary['N(o,r)'] = self.get_cnt(order=order,
                                                       referral=self.referral)

            '''
            Preva_referrel_icd10
            '''
            cur_order_summary['N(o,r,i)'] = self.get_cnt(order=order,
                                                       referral=self.referral,
                                                         icd10=icd10)
            print order, cur_order_summary['N(o,r,i)']

            cur_order_summary['N(r,i)'] = self.get_cnt(referral=self.referral,
                                                         icd10=icd10)

            '''
            PPV = P(order|referral, diagnose)=P(o|rd): When (1 referral, 1 icd10 appear)
            predicting order is in the actual order list, the fraction of time correct.
            '''
            # print self.df_referID_orders.head()
            # df_referID_icd10_orders = self.df_referID_orders[self.df_referID_orders['referral_icd10']==icd10]
                                         #self.df_referID_orders['specialty_order'].str.contains('PARATHYROID')].head()
            # TODO: how is this wrong?
            # num_icd10_encs = df_referID_icd10_orders.shape[0]
            # num_icd10_encs_wOrder = df_referID_icd10_orders[df_referID_icd10_orders['specialty_order']
            #                         .map(lambda x: order in x)].shape[0]
            # PPV = float(num_icd10_encs_wOrder)/num_icd10_encs
            PPV = (cur_order_summary['N(o,r,i)']) / (cur_order_summary['N(r,i)'])
            cur_order_summary['PPV'] = '%.2f' % PPV

            '''

            Relative risk = PPV / P(order|!ri)

            According to Bayes formula:
            P(o|ri)P(ri) + p(o|!ri)P(!ri) = P(o)
            So:
            denominator = p(o|!ri) = (P(o)-P(o|ri)P(ri))/P(!ri)
            where:
                P(o) = self.N_to_o[order]/self.N
                P(o|ri) = PPV
                P(ri) = self.N_to_ri[icd10]/self.N
                P(!ri) = 1 - P(ri)
            '''
            P_o = self.get_cnt(order=order)/self.get_cnt()
            P_ri = self.get_cnt(referral=self.referral, icd10=icd10)/self.get_cnt()
            RelaRisk = PPV / ( (P_o-PPV*P_ri)/(1.-P_ri+0.00001) +0.00001)
            cur_order_summary['RelaRisk'] = '%.2f' % RelaRisk #'%d' % int(round(RelaRisk))

            TFIDF = cur_order_summary['N(o,r,i)']*self.get_cnt()/\
                    (cur_order_summary['N(r,i)'] * cur_order_summary['N(o)'])
            cur_order_summary['TFIDF'] = '%.2f' % TFIDF #'%d' % int(round(TFIDF))

            # cur_order_summary['PC_cnt'] =  self.order_isPCCnt_global[order]['PC_cnt']
            # cur_order_summary['nonPC_cnt'] = self.order_isPCCnt_global[order]['nonPC_cnt']
            cur_order_summary['PrimaryCareRatio'] = '%.2f' % (float(self.order_isPCCnt_global[order]['PC_cnt'])
                                                              /float(self.order_isPCCnt_global[order]['nonPC_cnt']))

            df_res = df_res.append(cur_order_summary, ignore_index=True)
        if not os.path.exists("tables"):
            os.mkdir("tables")
        df_res.to_csv('tables/%s_%s_%s.csv' % (self.referral_code, icd10, rank_by), index=False)

def test_query():
    query = queries.query_for_recent6months()
    df = get_queried_data(query)
    print df.shape
    print df.head()

def load_data(test_mode=False, newPatientOnly=True, referral_name=None):
    if test_mode:
        df = pd.read_csv(os.path.join(result_folderpath, 'queried_data_2690237133563743535_sample.csv'))
    else:
        query = queries.query_for_recent6months(newPatientOnly=newPatientOnly, referral_name=referral_name)
        df = get_queried_data(query)
    return df

def test_munger(referral, icd10, test_mode=False):
    print "loading data into test munger for referral:  %s  with icd10: %s " %(referral,icd10)
    df = load_data(test_mode=test_mode, newPatientOnly=True)
    print "running data munger"
    munger = ReferralDataMunger(referral=referral,
                                df_full=df)
    print "generate order stats by abs"
    munger.generate_order_stats(icd10=icd10, top_k=10, rank_by='abs')
    # print "generate order stats by tfidf"
    # munger.generate_order_stats(icd10=icd10, top_k=10, rank_by='tfidf')
    print "test munger complete"

def plot_waiting_times(col=3):
    df = load_data()
    row = len(data_config.referral_to_specialty_tuples)/col

    referrals = []
    medians = []
    Q1s, Q3s = [], []
    fig, axes = plt.subplots(row, col)
    for i, pair in enumerate(data_config.referral_to_specialty_tuples):
        referral = pair[0]
        referrals.append(referral)
        print "plot_waiting_times for %s" % referral

        munger = ReferralDataMunger(referral=referral,
                                    df_full=df)
        median, Q1, Q3 = munger.plot_waiting_times(axes[i/col, i%col])

        medians.append(median)
        Q1s.append(Q1)
        Q3s.append(Q3)

    pd.DataFrame({'referral':referrals, 'median':medians, 'Q1':Q1s, 'Q3':Q3s})\
        [['referral', 'median', 'Q1', 'Q3']].to_csv('waiting_time_stats.csv', index=False)
    plt.tight_layout()
    # fig.suptitle('waiting days (max 6 months)', verticalalignment='bottom')
    plt.show()

def explore_referrals(referral, top_k=5):
    df = load_data(test_mode=False)
    print "reading data into munger"
    munger = ReferralDataMunger(referral=referral,
                                df_full=df)
    print "calculating by abs"
    munger.explore_referral(top_k=top_k, rank_by='abs')

    print "calculating tfidf"
    munger.explore_referral(top_k=top_k, rank_by='tfidf')
    print "finished explore_referral"

def explore_savable_frac():
    df = load_data(test_mode=False)
    pc_cnts = calc_PC_cnts(df)
    df = df[['specialty_enc_id', 'specialty_name', 'specialty_order']]

    df['savable_order'] = df['specialty_order']\
        .apply(lambda x: float(pc_cnts[x]['PC_cnt'])/(pc_cnts[x]['nonPC_cnt']+0.1) >= 0.1)

    df_tmp = df[['specialty_enc_id', 'specialty_name', 'savable_order']]\
              .groupby(['specialty_enc_id', 'specialty_name'])['savable_order']\
        .all().reset_index().rename(columns={'savable_order':'savable_enc'})
    df_tmp.groupby(['specialty_name'])['savable_enc'].mean().reset_index()\
        .rename(columns={'savable_enc':'savable_frac'}).to_csv('savable_frac.csv', index=False)

def explore_savable_time(specialty='Hematology'):
    df = load_data(newPatientOnly=False, referral_name='REFERRAL TO HEMATOLOGY')
    print df.head()
    pass

def explore_PC_freq():
    df = load_data(test_mode=False)
    top_orders_cnts = Counter(df['specialty_order']).most_common(1000)
    PC_dict = calc_PC_cnts(df)

    orders = []
    PC_cnts = []
    nonPC_cnts = []
    for order, cnt in top_orders_cnts:
        orders.append(order)
        PC_cnts.append(PC_dict[order]['PC_cnt'])
        nonPC_cnts.append(PC_dict[order]['nonPC_cnt'])
        # print order, PC_dict[order]
    pd.DataFrame({'order':orders, 'PC_cnt':PC_cnts, 'nonPC_cnt':nonPC_cnts})\
        [['order', 'PC_cnt', 'nonPC_cnt']].to_csv('PC_freqs.csv', index=False)
    pass

if __name__ == '__main__':
    # REFERRAL TO ENDOCRINE CLINIC, 'E11'
    # explore_referrals('REFERRAL TO HEMATOLOGY', top_k=10)
    test_munger('REFERRAL TO HEMATOLOGY', 'D50', test_mode=False)
    # plot_waiting_times()

    # test_plotVisitTimes()

    # explore_savable_frac()
    # explore_savable_time()
    # explore_PC_freq(
