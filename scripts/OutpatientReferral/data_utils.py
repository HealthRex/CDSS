
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
        df = pd.read_csv(cached_filepath, comment='#', sep='\t')

    else:
        client = setup_client('MiningClinicalDecisions_Song.json')
        project_id = 'mining-clinical-decisions'
        df = make_bigquery(query, client=client, project_id=project_id)

        f = open(cached_filepath, 'a')
        f.write('#' + query.replace('\n', '\n#') + '\n')
        df.to_csv(f, index=False, sep='\t', encoding = 'utf-8')
        f.close()

    return df

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


        #
        #
        #
        # '''A bunch of global stats'''
        # if verbose:
        #     print "Original df shape:", df.shape
        #
        # if not newPatientOnly:
        #     '''Task 1: stats of number of specialty visits TODO'''
        #
        #
        #
        #     '''Task 2: Only keep new patient TODO'''
        #     pass
        #
        #
        # """
        # Order-based cnts: each row corresponds to 1 order
        # """
        # '''Total number of any orders in 'New Patient Visit' of any department of any type at any time t1'''
        #
        #
        # if verbose:
        #     print "Current referral's df shape:", self.df.shape
        #
        #
        #
        # '''Count dict of orders associated w/ different specialties'''
        # self.N_to_o = Counter(self.df_full['specialty_order'])
        #
        # ''' Type: Primary Care, Cancer, etc.'''
        self.order_typeCnt_global = self.df_full[['specialty_order', 'specialty_name']] \
            .groupby('specialty_order')['specialty_name'] \
            .apply(list).apply(Counter).to_dict()
        self.order_isPCCnt_global = {}
        # # TODO: be careful of missing specialty departments, could potentially all be PC?
        for order, cnter in self.order_typeCnt_global.items():
            self.order_isPCCnt_global[order] = {'PC_cnt': cnter['Primary Care'],
                                                'nonPC_cnt': sum(cnter.values()) - cnter['Primary Care']}
        #
        # '''Total number of orders corresponding to the current referral'''
        # self.N_by_r = self.df.shape[0]
        #
        # '''Count dict of orders associated w/ different icd10s for the current referral'''
        # self.N_to_ri = Counter(self.df['referral_icd10'])
        # if verbose:
        #     print 'self.N_to_ri.most_common(5):', self.N_to_ri.most_common(5)
        #
        # '''Count dict of occurrences associated w/ different icd10s for any referral'''
        # self.I_to_i = Counter(self.df_full[['referral_enc_id', 'referral_icd10']]
        #                                    .drop_duplicates()['referral_icd10'])
        # self.I_to_ri = Counter(self.df[['referral_enc_id', 'referral_icd10']]
        #                       .drop_duplicates()['referral_icd10'])
        #
        #
        # self.N_to_ri_tfidf = Counter()
        # for icd10, absCnt_local in self.N_to_ri.items():
        #     self.N_to_ri_tfidf[icd10] = float(absCnt_local) * self.N \
        #                                     / (self.N_by_r * self.I_to_i[icd10])
        #
        # self.N_to_ro = Counter(self.df['specialty_order'])
        #
        # '''
        # An order cnt for each icd10
        # '''
        # self.N_to_rio = {}
        # '''
        # tfidf: defined by n(o, rd) * N / n(o) n(rd), where:
        #     n(o, rd) = self.N_to_rio[icd10][order]
        #     N = self.N
        #     n(o) = self.N_to_o[order]
        #     n(rd) = self.N_to_ri[icd10]
        # '''
        # self.N_to_rio_tfidf = {}
        # for icd10, _ in self.N_to_ri.most_common(10):  # TODO:
        #     cur_df = self.df[self.df['referral_icd10'] == icd10]
        #     self.N_to_rio[icd10] = Counter(cur_df['specialty_order'])
        #
        #     self.N_to_rio_tfidf[icd10] = Counter()
        #     for order, _ in self.N_to_rio[icd10].items():
        #         self.N_to_rio_tfidf[icd10][order] = float(self.N_to_rio[icd10][order]) * self.N \
        #                                                / (self.N_to_o[order] * self.N_to_ri[icd10])
        #
        # if verbose:
        #     print self.N_to_rio
        #
        # ''' Initial processing: Keeping only the most recent specialty visit  '''
        # # Almost already make sure of this by requiring "New Patient" in the query
        # #
        # # self.df = self.df.sort_values(['referral_enc_id', 'specialty_time'])
        # # referral_to_1stSpecialtyTime = self.df[['referral_enc_id', 'specialty_time']]\
        # #     .groupby('referral_enc_id')\
        # #     .first()\
        # #     .to_dict()['specialty_time']
        # # self.df = self.df[self.df['specialty_time'] == self.df['referral_enc_id']
        # #     .apply(lambda x: referral_to_1stSpecialtyTime[x])]
        # # print "First-visit-only df shape:", self.df.shape
        #
        # # self.icd10_ipwCnt = Counter()
        # # for icd10, absCnt_local in self.N_to_ri.items():
        # #     self.icd10_ipwCnt[icd10] = float(absCnt_local)/self.I_to_i[icd10]
        # # if verbose:
        # #     print 'self.icd10_ipwCnt.most_common(5):', self.icd10_ipwCnt.most_common(5)
        #
        # '''
        # Event based stats
        # '''
        # self.df_referID_orders = self.df[['referral_enc_id', 'referral_icd10', 'specialty_order']]\
        #                     .groupby(['referral_enc_id','referral_icd10'])['specialty_order']\
        #                     .apply(list).reset_index()

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

    def explore_referral(self, top_k=5, rank_by='abs'):
        icd10_category_mapping = data_config.get_icd10_category_mapping()
        print 'Top icd10s and their categories by %s_cnt:'%rank_by
        if rank_by == 'abs':
            icd10_cnts = self.N_to_ri.most_common(top_k)
        elif rank_by == 'tfidf':
            icd10_cnts = self.N_to_ri_tfidf.most_common(top_k)

        icd10s = [x[0] for x in icd10_cnts]
        categories = [icd10_category_mapping[x] for x in icd10s]
        print zip(icd10s, categories)

    def get_cnt(self, referral=None, order=None, icd10=None):
        cur_df = self.df_full[['referral_enc_id', 'referral_name', 'specialty_order', 'referral_icd10']]

        included_columns = ['referral_enc_id']
        if referral:
            cur_df = cur_df[cur_df['referral_name'] == referral]
            included_columns.append('referral_name')

        if order:
            cur_df = cur_df[cur_df['specialty_order'] == order]
            included_columns.append('specialty_order')

        if icd10:
            cur_df = cur_df[cur_df['referral_icd10'] == icd10]
            included_columns.append('referral_icd10')

        return float(cur_df[included_columns].drop_duplicates().shape[0])


    # def get_icd10_cnt(self, referral=None, icd10=None):
    #     ''''''
    #     '''
    #     Unit of occurrence measured by referral_enc_id, not by row (order!)
    #     '''
    #     cur_df = self.df_full[['referral_enc_id', 'referral_name', 'referral_icd10']].drop_duplicates()
    #
    #     if referral:
    #         cur_df = cur_df[cur_df['referral_name'] == referral]
    #
    #     if icd10:
    #         cur_df = cur_df[cur_df['referral_icd10'] == icd10]
    #
    #     return cur_df.shape[0]


    def get_most_common_orders(self, icd10, top_k, rank_by='abs'):
        cur_df = self.df[self.df['referral_icd10'] == icd10]
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

        top_orders_cnts = self.get_most_common_orders(icd10, top_k, rank_by='abs')

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
            RelaRisk = PPV / ( (P_o-PPV*P_ri)/(1.-P_ri) )
            cur_order_summary['RelaRisk'] = '%.2f' % RelaRisk #'%d' % int(round(RelaRisk))

            TFIDF = cur_order_summary['N(o,r,i)']*self.get_cnt()/\
                    (cur_order_summary['N(r,i)'] * cur_order_summary['N(o)'])
            cur_order_summary['TFIDF'] = '%.2f' % TFIDF #'%d' % int(round(TFIDF))

            # cur_order_summary['PC_cnt'] =  self.order_isPCCnt_global[order]['PC_cnt']
            # cur_order_summary['nonPC_cnt'] = self.order_isPCCnt_global[order]['nonPC_cnt']
            cur_order_summary['PrimaryCareRatio'] = '%.2f' % (float(self.order_isPCCnt_global[order]['PC_cnt'])
                                                              /float(self.order_isPCCnt_global[order]['nonPC_cnt']))

            df_res = df_res.append(cur_order_summary, ignore_index=True)
        df_res.to_csv('tables/%s_%s_%s.csv' % (self.referral_code, icd10, rank_by), index=False)

def test_query():
    query = queries.query_for_recent6months()
    df = get_queried_data(query)
    print df.shape
    print df.head()

def load_data(test_mode=False, newPatientOnly=True):
    if test_mode:
        df = pd.read_csv(os.path.join(result_folderpath, 'queried_data_2690237133563743535_sample.csv'))
    else:
        query = queries.query_for_recent6months(newPatientOnly=newPatientOnly)
        df = get_queried_data(query)
    return df

def test_munger(referral, icd10, test_mode=False):
    df = load_data(test_mode=test_mode, newPatientOnly=True)
    munger = ReferralDataMunger(referral=referral,
                                df_full=df)
    munger.generate_order_stats(icd10=icd10, top_k=10, rank_by='abs')
    munger.generate_order_stats(icd10=icd10, top_k=10, rank_by='tfidf')

def plot_waiting_times(col=3):
    df = load_data()
    row = len(data_config.referral_to_specialty_tuples)/col

    fig, axes = plt.subplots(row, col)
    for i, pair in enumerate(data_config.referral_to_specialty_tuples):
        referral = pair[0]
        munger = ReferralDataMunger(referral=referral,
                                    df=df)
        munger.plot_waiting_times(axes[i/col, i%col])
    plt.tight_layout()
    # fig.suptitle('waiting days (max 6 months)', verticalalignment='bottom')
    plt.show()

def explore_referrals(referral, rank_by='abs'):
    df = load_data(test_mode=False)
    munger = ReferralDataMunger(referral=referral,
                                df=df)
    munger.explore_referral(rank_by=rank_by)

if __name__ == '__main__':
    # REFERRAL TO ENDOCRINE CLINIC, 'E11'
    # explore_referrals('REFERRAL TO HEMATOLOGY', rank_by='abs')
    test_munger('REFERRAL TO HEMATOLOGY', 'D69', test_mode=False)
    # plot_waiting_times()

    # df = load_data()
    # print df.shape

    # test_plotVisitTimes()