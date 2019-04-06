
''''''

import os
import pandas as pd
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)

import queries

from google.cloud import bigquery

testdf = pd.DataFrame({'test':[1,2,3]})

result_folderpath = 'queried_results'
if not os.path.exists(result_folderpath):
    os.mkdir(result_folderpath)

def setup_client(jsonkey_filepath):
    client = bigquery.Client.from_service_account_json(jsonkey_filepath)
    return client

def make_bigquery(query, client, project_id):
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

class ReferralDataMunger():

    def __init__(self, referral, df, to_truncate_icd10=True, verbose=False):
        self.referral = referral
        self.referral_code = referral.replace("REFERRAL TO ", "").replace(" ","-").replace("/","-")
        self.specialty = referral_to_specialty_dict[referral]
        self.df = df

        if to_truncate_icd10:
            self.df['referral_icd10'] = self.df['referral_icd10'].fillna('NA').apply(lambda x: truncate_icd10(x))

        '''A bunch of global stats'''
        if verbose:
            print "Original df shape:", df.shape
        self.num_rows_global = self.df.shape[0]
        self.icd10_absCnt_global = Counter(self.df['referral_icd10'])
        '''
        More complicated for orders:
        Global: order cnt for any referral, any icd10 code
        Local: order cnt for 1 referral, any icd10 code 
        Inner: order cnt for 1 referral, 1 icd10
        '''
        self.order_absCnt_global = Counter(self.df['specialty_order'])

        '''Making df local (only to the current referral)'''
        self.df = self.df[(self.df['referral_name'] == referral) & (self.df['specialty_name'] == self.specialty)].copy()
        if verbose:
            print "Current referral's df shape:", self.df.shape

        ''' Initial processing: Keeping only the most recent specialty visit  '''
        # Almost already make sure of this by requiring "New Patient" in the query
        #
        # self.df = self.df.sort_values(['referral_enc_id', 'specialty_time'])
        # referral_to_1stSpecialtyTime = self.df[['referral_enc_id', 'specialty_time']]\
        #     .groupby('referral_enc_id')\
        #     .first()\
        #     .to_dict()['specialty_time']
        # self.df = self.df[self.df['specialty_time'] == self.df['referral_enc_id']
        #     .apply(lambda x: referral_to_1stSpecialtyTime[x])]
        # print "First-visit-only df shape:", self.df.shape

        self.num_rows_local = self.df.shape[0]

        '''
        Counts:
        '''
        self.icd10_absCnt_local = Counter(self.df['referral_icd10'])
        if verbose:
            print 'self.icd10_absCnt_local.most_common(5):', self.icd10_absCnt_local.most_common(5)

        self.icd10_ipwCnt = Counter()
        for icd10, absCnt_local in self.icd10_absCnt_local.items():
            self.icd10_ipwCnt[icd10] = float(absCnt_local)/self.icd10_absCnt_global[icd10]
        if verbose:
            print 'self.icd10_ipwCnt.most_common(5):', self.icd10_ipwCnt.most_common(5)

        self.order_absCnt_local = Counter(self.df['specialty_order'])

        '''
        A cnt for each icd10
        '''
        self.order_absCnt_inner = {}
        for icd10, absCnt_local in self.icd10_absCnt_local.most_common(5): # TODO:
            cur_df = self.df[self.df['referral_icd10']==icd10]
            self.order_absCnt_inner[icd10] = Counter(cur_df['specialty_order'])
        if verbose:
            print self.order_absCnt_inner
        # icd10_prev = {}
        # for icd10, cnt in icd10_cnter.items():
        #     icd10_prev[icd10] = float(cnt) / num_rows

        '''
        Event based stats
        '''
        self.df_referID_orders = self.df[['referral_enc_id', 'referral_icd10', 'specialty_order']]\
                            .groupby(['referral_enc_id','referral_icd10'])['specialty_order']\
                            .apply(list).reset_index()



    def generate_order_stats(self, icd10, top_k=5):
        ''''''

        '''
        Find out the top k orders for that icd10
        '''
        df_res = pd.DataFrame(columns=['order', 'Preva', 'Preva_referrel', 'Preva_referrel_icd10',
                                       'PPV', 'RelaRisk' #, , 'PC_cnt', 'NonPC_cnt'
                                       ])
        # print self.icd10_absCnt_local.most_common(top_k)
        common_absCnt_locals = self.order_absCnt_inner[icd10].most_common(top_k)
        for k in range(len(common_absCnt_locals)):
            order, absCnt_local = common_absCnt_locals[k]
            '''
            Order_name
            '''
            cur_order_summary = {'order':order}

            '''
            Preva
            '''
            Preva = self.order_absCnt_global[order]
            cur_order_summary['Preva'] = Preva

            '''
            Preva_referrel
            '''
            Preva_referrel = self.order_absCnt_local[order]
            cur_order_summary['Preva_referrel'] = Preva_referrel

            '''
            Preva_referrel_icd10
            '''
            Preva_referrel_icd10 = self.order_absCnt_inner[icd10][order]
            cur_order_summary['Preva_referrel_icd10'] = Preva_referrel_icd10

            '''
            PPV = P(order|referral, diagnose)=P(o|rd): When (1 referral, 1 icd10 appear) 
            predicting order is in the actual order list, the fraction of time correct.  
            '''
            # print self.df_referID_orders.head()
            df_referID_icd10_orders = self.df_referID_orders[self.df_referID_orders['referral_icd10']==icd10]
                                         #self.df_referID_orders['specialty_order'].str.contains('PARATHYROID')].head()
            num_icd10_encs = df_referID_icd10_orders.shape[0]
            num_icd10_encs_wOrder = df_referID_icd10_orders[df_referID_icd10_orders['specialty_order']
                                    .map(lambda x: order in x)].shape[0]
            PPV = float(num_icd10_encs_wOrder)/num_icd10_encs
            cur_order_summary['PPV'] = '%.2f' % PPV

            '''
            
            Relative risk = PPV / P(order|!rd)

            According to Bayes formula:
            P(o|rd)P(rd) + p(o|!rd)P(!rd) = P(o)
            So:
            denominator = p(o|!rd) = (P(o)-P(o|rd)P(rd))/P(!rd)
            where:
                P(o) = self.order_absCnt_global[order]/self.num_rows_global
                P(o|rd) = PPV
                P(rd) = self.icd10_absCnt_local[icd10]/self.num_rows_global
                P(!rd) = 1 - P(rd)
            '''
            P_o = self.order_absCnt_global[order]/float(self.num_rows_global)
            P_rd = self.icd10_absCnt_local[icd10]/float(self.num_rows_global)
            RelaRisk = PPV/( (P_o-PPV*P_rd)/(1.-P_rd) )
            cur_order_summary['RelaRisk'] = RelaRisk

            # cur_order_summary.append(order_to_PCnonPC[order])

            df_res = df_res.append(cur_order_summary, ignore_index=True)
        df_res.to_csv('tables/%s_%s.csv' % (self.referral_code, icd10), index=False)

def test_query():
    query = queries.query_for_recent6months()
    df = get_queried_data(query)
    print df.shape
    print df.head()

def test_munger(referral, test_mode=False):
    if test_mode:
        df = pd.read_csv(os.path.join(result_folderpath, 'queried_data_2690237133563743535_sample.csv'))
    else:
        query = queries.query_for_recent6months()
        df = get_queried_data(query)

    munger = ReferralDataMunger(referral=referral,
                                df=df)
    munger.generate_order_stats(icd10='E11', top_k=10)

if __name__ == '__main__':
    test_munger('REFERRAL TO ENDOCRINE CLINIC', test_mode=False)