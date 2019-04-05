
''''''

import pandas as pd
from collections import Counter
import os
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)


referral_to_specialty_tuples =\
[
    ('REFERRAL TO DERMATOLOGY', 'Dermatology'),
    ('REFERRAL TO GASTROENTEROLOGY', 'Gastroenterology'),
    ('REFERRAL TO EYE', 'Ophthalmology'),
    # REFERRAL TO PAIN CLINIC PROCEDURES,   Pain Management #(cnt: 525, but Neurosurgery has 224)
    ('REFERRAL TO ORTHOPEDICS', 'Orthopedic Surgery'),
    ('REFERRAL TO CARDIOLOGY', 'Cardiology'),
    ('REFERRAL TO PSYCHIATRY', 'Psychiatry'),
    ('SLEEP CLINIC REFERRAL', 'Sleep Center'),
    ('REFERRAL TO ENT/OTOLARYNGOLOGY', 'ENT-Otolaryngology'),  # (cnt: 2170, but Oncology has 480)
    ('REFERRAL TO PAIN CLINIC', 'Pain Management'),
    ('REFERRAL TO UROLOGY CLINIC', 'Urology'),  # (cnt: 2827, but Oncology has 605)
    ('REFERRAL TO ENDOCRINE CLINIC', 'Endocrinology'), # Suggested by Jon Chen
    ('REFERRAL TO HEMATOLOGY', 'Hematology')
]
referral_to_specialty_dict = dict(referral_to_specialty_tuples)

def explore_orders():
    if not os.path.exists('data/third_implementation/explore_orders.csv'):

        df = pd.read_csv('data/third_implementation/training_data.csv')
        all_orders = df['specialty_order'].drop_duplicates().values.tolist()
        print "Number of different types of orders:", len(all_orders)

        order_cnter = {}
        for key, val in Counter(df['specialty_order']).items():
            if val >= 100:
                order_cnter[key] = val
        print "Number of common (>100) orders:", len(order_cnter)

        all_cnters = []
        for i, one_order in enumerate(order_cnter.keys()):
            # print "the %d-th order %s..."%(i, one_order)
            cur_specialties = df[df['specialty_order']==one_order]['specialty_name'].values.tolist()
            cur_cnter = Counter(cur_specialties)
            all_cnters.append(cur_cnter.most_common(5))
        df_res = pd.DataFrame({'orders':order_cnter.keys(), 'specialtiy_cnt':all_cnters})
        df_res.to_csv('data/third_implementation/explore_orders.csv', index=False)

    else:
        df = pd.read_csv('data/third_implementation/explore_orders.csv')

    print df.head()

    def specialCntStr_to_dominateType(cntstrs):
        cnts_splited = cntstrs.split('),')

        all_cnts_clean = []

        cnt_splited = [x.strip() for x in cnts_splited[0][2:].split(',')] # Filter out '[('
        if len(cnts_splited) == 1:
            cnt_splited[1] = cnt_splited[1][:-2] # Filter out )]
        all_cnts_clean.append(cnt_splited)

        for i in range(1, len(cnts_splited)-1): # Filter out '('
            cnt_splited = [x.strip() for x in cnts_splited[i][2:].split(',')]
            all_cnts_clean.append(cnt_splited)

        if len(cnts_splited) > 1: # Filter out )]
            cnt_splited = [x.strip() for x in cnts_splited[-1][2:-2].split(',')]
            all_cnts_clean.append(cnt_splited)

        all_cnts_clean = [[x[0][1:-1], float(x[1])] for x in all_cnts_clean]

        PC_cnt = 0
        nonPC_cnt = 0
        for one_cntpair in all_cnts_clean:
            if one_cntpair[0] == 'Primary Care':
                PC_cnt += one_cntpair[1]
            else:
                nonPC_cnt += one_cntpair[1]

        return PC_cnt, nonPC_cnt

    df['PC_nonPC_cnt'] = df['specialtiy_cnt'].apply(lambda x: str(specialCntStr_to_dominateType(x)))
    order_to_PCnonPC = dict(zip(df['orders'], df['PC_nonPC_cnt']))

    return order_to_PCnonPC

def truncate_icd10(icd10):
    try:
        return icd10.split('.')[0]
    except AttributeError: # empty value 'nan'
        return ''

def get_icd10_totcnter():
    '''
    Returns:
    Dict:
        key: truncated icd10
        val: total count

    TODO: note that this 'total cnt' is not necessarily from 'first visit' to that specialty
    Because still could not mapping referral to speicalty for all referrals...
    '''
    df = pd.read_csv('data/third_implementation/training_data.csv')
    icd10_totcnter = Counter(df['referral_icd10'].apply(lambda x: truncate_icd10(x)))
    return icd10_totcnter


def get_top_orders(df_full, referral, k=5, method='abs'):
    print 'Getting the top %d orders for referral %s, using %s count...' \
            % (k, referral, method)
    specialty = referral_to_specialty_dict[referral]
    df_one = df_full[(df_full['referral_name'] == referral)
                            & (df_full['specialty_name'] == specialty)]
    print df_one.head()

    df_tmp = df_one[['referral_enc_id', 'specialty_time']] \
        .groupby('referral_enc_id').first().reset_index()
    refer_to_first_special = dict(zip(df_tmp['referral_enc_id'].values, df_tmp['specialty_time'].values))

    df_train_one_firstSpecialtyVisit = df_one[df_one['specialty_time'] ==
                                                    df_one['referral_enc_id'].apply(
                                                        lambda x: refer_to_first_special[x])]
    num_rows = df_train_one_firstSpecialtyVisit.shape[0]
    '''
    Aggregate icd10 codes
    '''
    df_tmp = df_train_one_firstSpecialtyVisit[['referral_icd10', 'specialty_order']].copy()
    to_agg_icd10 = True
    if to_agg_icd10:
        df_tmp['referral_icd10'] = df_tmp['referral_icd10'].fillna('NA').apply(lambda x: truncate_icd10(x))

    '''
    What are the common diagnostic codes mapped to the referral, and their stats
    '''
    icd10_abscnter = Counter(df_tmp['referral_icd10'])
    icd10_totscnter = explore_icd10s()
    icd10_ipwcnter = {}
    for icd10, abscnt in icd10_abscnter.items():
        if abscnt < 50: # Penalty for rare orders!
            icd10_ipwcnter[icd10] = 0
        else:
            icd10_ipwcnter[icd10] = float(abscnt)/icd10_totscnter[icd10]
    icd10_ipwcnter = Counter(icd10_ipwcnter)

    for icd10, abscnt in icd10_abscnter.most_common(5):
        print icd10, abscnt, icd10_ipwcnter[icd10]

    for icd10, ipwcnt in icd10_ipwcnter.most_common(5):
        print icd10, icd10_abscnter[icd10], ipwcnt
    quit()

    icd10_cnt_common = icd10_abscnter.most_common(5)

    icd10_prev = {}
    for icd10, cnt in icd10_cnter.items():
        icd10_prev[icd10] = float(cnt) / num_rows

    icd10order_to_cnt = df_tmp['specialty_order']\
        .groupby(df_tmp['referral_icd10'])\
        .value_counts()\
        .groupby(level=0)\
        .nlargest(5)\
        .reset_index(level=0, drop=True)\
        .to_dict()

    icd10_to_orderCnt = {}
    for key, val in icd10order_to_cnt.items():
        icd10, order = key
        if icd10 in icd10_to_orderCnt:
            icd10_to_orderCnt[icd10].append((order, val))
        else:
            icd10_to_orderCnt[icd10] = [(order, val)]

    order_cnter = Counter(df_train_one_firstSpecialtyVisit['specialty_order'])

    '''
    Among all (1) first, (2) new patient visit (3) with that referral code, 
    (so, among all diagnoses code), 
    what are the prevalence for that order.
    '''
    order_prev = {}
    for order, cnt in order_cnter.items():
        order_prev[order] = float(cnt) / num_rows

    df_explore_icd10_to_orders = pd.DataFrame(columns=['Icd10'] +
                                                      ['Top ' + str(x + 1) +
                                                       ' Order, Prev, PPV, RR, PC_cnt, nonPC_cnt' for x in range(5)])
    top_entries = [[] * 6 for _ in range(5)]

    '''
    Construct 5 rows for the table. 
    Each row is an icd10, including:
    icd10_code,
    top1 order summary, 
    top2 order summary, 
    top3 order summary, 
    top4 order summary, 
    top5 order summary. 
    '''
    order_to_PCnonPC = explore_orders()

    for j, pair in enumerate(icd10_cnt_common[:5]):
        # print icd10, sorted(icd10_to_orderCnt[icd10], key=lambda (k,v):v)[::-1]
        icd10 = pair[0]
        cur_icd10_summary = [icd10]

        '''
        Summary for each order, including: 
        order_name,
        prev,
        PPV,
        rela_risk
        '''
        top_orderCnts = sorted(icd10_to_orderCnt[icd10], key=lambda (k, v): v)[::-1][:5]
        for k in range(5):
            order, conditioned_cnt = top_orderCnts[k]
            '''
            order_name
            '''
            cur_order_summary = [order]

            '''
            prev
            '''
            prev_str = '%.2f' % order_prev[order]
            cur_order_summary.append(prev_str)

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

        top_entries[j] += cur_icd10_summary  # [icd10] + top_orderCnts

        df_explore_icd10_to_orders.loc[len(df_explore_icd10_to_orders)] = top_entries[j]

    df_explore_icd10_to_orders.to_csv('data/third_implementation/df_explore_%s_icd10_to_orders.csv' % referral_code,
                                      index=False, float_format='%.2f')
    pass


def task1():
    '''
    Task 1: For each Referral and icd10 code, list top 5 orders by
    abs (absolute) and ipw (inverse probability weighting) counts

    Input: "Full pandas table"

    '''

    df_full = pd.read_csv('data/third_implementation/training_data.csv')
    top_orders = get_top_orders(df_full=df_full,
                                referral='REFERRAL TO HEMATOLOGY'
                                )
    pass

if __name__ == '__main__':
    task1()