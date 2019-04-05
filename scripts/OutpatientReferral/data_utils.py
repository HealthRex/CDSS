
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
        self.specialty = referral_to_specialty_dict[referral]
        self.df = df

        if to_truncate_icd10:
            self.df['referral_icd10'] = self.df['referral_icd10'].fillna('NA').apply(lambda x: truncate_icd10(x))

        '''A bunch of global stats'''
        if verbose:
            print "Original df shape:", df.shape
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

        self.num_rows = self.df.shape[0]

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


    def generate_order_stats(self, icd10, top_k=5):
        ''''''

        '''
        Find out the top k orders for that icd10
        '''
        df_res = pd.DataFrame(columns=['order', 'Preva', 'PPV',
                                       'RelaRisk', 'PC_cnt', 'NonPC_cnt'])
        # print self.icd10_absCnt_local.most_common(top_k)
        common_absCnt_locals = self.order_absCnt_local.most_common(top_k)
        for k in range(top_k):
            order, absCnt_local = common_absCnt_locals[k]
            '''
            Order_name
            '''
            cur_order_summary = [order]

            '''
            Preva:
            '''
            preva_str = '%.2f' % self.order_absCnt_inner[icd10][order]
            cur_order_summary.append(preva_str)
            print cur_order_summary
            quit()

            '''
            PPV, P(order|icd10) = P(order|icd10) / P(order|!icd10)
            '''
            ppv = float(conditioned_cnt) / icd10_cnter[icd10]
            ppv_str = '%.2f' % ppv
            cur_order_summary.append(ppv_str)

            '''
            Relative risk = P(order|diagnose) / P(order|!diagnose)

            According to Bayes formula:
            P(o|d)P(d) + p(o|!d)P(!d) = P(o)
            So:
            denominator = p(o|!d) = (P(o)-P(o|d)P(d))/P(!d)
            where:
                P(o) = order_prev[order]
                P(o|d) = PPV
                P(d) = icd10_prev[icd10]
                P(!d) = 1-icd10_prev[icd10]
            '''
            denominator = (order_prev[order] - ppv * icd10_prev[icd10]) / (1. - icd10_prev[icd10])
            rela_risk = ppv / denominator
            rr_str = '%.2f' % rela_risk
            cur_order_summary.append(rr_str)

            cur_order_summary.append(order_to_PCnonPC[order])

            cur_icd10_summary.append(cur_order_summary)

def test_query():
    query = queries.query_for_recent6months()
    df = get_queried_data(query)
    print df.shape
    print df.head()

def test_munger(referral, test_mode=True):
    if test_mode:
        df = pd.read_csv(os.path.join(result_folderpath, 'queried_data_2690237133563743535_sample.csv'))
    else:
        query = queries.query_for_recent6months()
        df = get_queried_data(query).sample(n=10000)

    munger = ReferralDataMunger(referral=referral,
                                df=df)
    munger.generate_order_stats(icd10='E11')

if __name__ == '__main__':
    test_munger('REFERRAL TO ENDOCRINE CLINIC')