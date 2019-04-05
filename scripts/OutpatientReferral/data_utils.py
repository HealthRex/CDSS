
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

    def __init__(self, referral, df):
        self.referral = referral
        self.specialty = referral_to_specialty_dict[referral]

        print "Original df shape:", df.shape
        self.df = df[(df['referral_name']==referral)&(df['specialty_name']==self.specialty)].copy()

        print "This referral's df shape:", self.df.shape

        ''' Initial processing: Keeping only the most recent specialty visit  '''
        # TODO: For now, consider them the same!
        # self.df = self.df.sort_values(['referral_enc_id', 'specialty_time'])
        # referral_to_1stSpecialtyTime = self.df[['referral_enc_id', 'specialty_time']]\
        #     .groupby('referral_enc_id')\
        #     .first()\
        #     .to_dict()['specialty_time']
        # self.df = self.df[self.df['specialty_time'] == self.df['referral_enc_id']
        #     .apply(lambda x: referral_to_1stSpecialtyTime[x])]
        # print "First-visit-only df shape:", self.df.shape

        self.df['referral_icd10short'] = self.df['referral_icd10'].fillna('NA').apply(lambda x: truncate_icd10(x))

        self.num_rows = self.df.shape[0]

        '''
        Counts:
        Global abs: appear in any order
        '''
        self.icd10_absCnt_local = Counter(self.df['referral_icd10short'])
        icd10pair_common_abs = self.icd10_absCnt_local.most_common(5)
        print icd10pair_common_abs
        quit()

        # icd10_prev = {}
        # for icd10, cnt in icd10_cnter.items():
        #     icd10_prev[icd10] = float(cnt) / num_rows



        self.icd10_to_orderAbsCnt = {}

        pass

    # def generate_order_stats(self, icd10):
    #     ''''''
    #
    #     '''
    #     Find out the top k orders for that icd10
    #     '''
    #     for k in range(5):
    #         order, conditioned_cnt = top_orderCnts[k]
    #         '''
    #         order_name
    #         '''
    #         cur_order_summary = [order]
    #
    #         '''
    #         prev
    #         '''
    #         prev_str = '%.2f' % order_prev[order]
    #         cur_order_summary.append(prev_str)
    #
    #         '''
    #         PPV, P(order|icd10) = P(order|icd10) / P(order|!icd10)
    #         '''
    #         ppv = float(conditioned_cnt) / icd10_cnter[icd10]
    #         ppv_str = '%.2f' % ppv
    #         cur_order_summary.append(ppv_str)
    #
    #         '''
    #         Relative risk = P(order|diagnose) / P(order|!diagnose)
    #
    #         According to Bayes formula:
    #         P(o|d)P(d) + p(o|!d)P(!d) = P(o)
    #         So:
    #         denominator = p(o|!d) = (P(o)-P(o|d)P(d))/P(!d)
    #         where:
    #             P(o) = order_prev[order]
    #             P(o|d) = PPV
    #             P(d) = icd10_prev[icd10]
    #             P(!d) = 1-icd10_prev[icd10]
    #         '''
    #         denominator = (order_prev[order] - ppv * icd10_prev[icd10]) / (1. - icd10_prev[icd10])
    #         rela_risk = ppv / denominator
    #         rr_str = '%.2f' % rela_risk
    #         cur_order_summary.append(rr_str)
    #
    #         cur_order_summary.append(order_to_PCnonPC[order])
    #
    #         cur_icd10_summary.append(cur_order_summary)

def test_query():
    query = queries.query_for_recent6months()
    df = get_queried_data(query)
    print df.shape
    print df.head()

def test_munger(referral):
    query = queries.query_for_recent6months()
    df = get_queried_data(query)

    munger = ReferralDataMunger(referral=referral,
                                df=df)
    # munger.generate_order_stats()

if __name__ == '__main__':
    test_munger('REFERRAL TO HEMATOLOGY')