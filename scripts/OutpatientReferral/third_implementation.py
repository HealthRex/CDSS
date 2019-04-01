

'''
Goal: Use referral + diagnoses to predict specialty and orders

(1) Focus only on those with unambiguous referral -> specialty mapping

'''

import pandas as pd
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)

from collections import Counter
from first_implementation import prec_at_k, recall_at_k
import numpy as np
import os
from datetime import datetime

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt


def main_onereferral(referral, specialty, explore=None, verbose=False):
    ''''''
    print "Processing %s..."%referral

    '''
    (1.2) Do train and test for REFERRAL TO DERMATOLOGY. 
    
    TODO: Could we assert that a (new visit) specialty has to come from referral?
    '''

    '''
    (1.2.1) Training set query in 2016
    
    Goal: 
    - referral_enc_id, referral_time, referral_name, patient_id, ICD10, ICD9
    - specialty_enc_id, specialty, dep_name, orders 
    
    Referral phase conditions:
    refer_name==REFERRAL TO DERMATOLOGY
    year=2016
    
    Specialty phase conditions:
    new_visit
    FIRST visit of the patient within 3 months of the referral_time
    
    
    p1: referral name
    d1: diagnoses
    e1: referral_enc
     
    p2: specialty
    d2: dep_map
    e2: specialty_enc
    
    BigQuery:
    select 
        p1.pat_enc_csn_id_coded as referral_enc_id,
        p1.description as referral_name, 
        e1.appt_when_jittered as referral_time, 
        e1.jc_uid as pat_id,
        d1.icd9 as referral_icd9,
        d1.icd10 as referral_icd10,
        
        p2.pat_enc_csn_id_coded as specialty_enc_id,
        e2.appt_when_jittered as specialty_time,
        d2.department_name as specialty_dep, 
        d2.specialty as specialty_name, 
        p2.description as specialty_order
    from 
        datalake_47618.encounter e1,
        datalake_47618.order_proc p1,
        datalake_47618.diagnosis_code d1,
        
        datalake_47618.encounter e2,
        datalake_47618.order_proc p2,
        datalake_47618.dep_map d2
    where
        lower(p1.description) like '%referral%' 
        and p1.pat_enc_csn_id_coded = e1.pat_enc_csn_id_coded
        and p1.pat_enc_csn_id_coded = d1.pat_enc_csn_id_coded
        and e1.appt_when_jittered >= '2016-01-01'
        and e1.appt_when_jittered < '2017-01-01'
        
        and e1.jc_uid = e2.jc_uid
        and e1.pat_enc_csn_id_coded != e2.pat_enc_csn_id_coded
        and e1.appt_when_jittered <= e2.appt_when_jittered
        and DATE_ADD(date(timestamp(e1.appt_when_jittered)), INTERVAL 3 month) > date(timestamp(e2.appt_when_jittered))
        
        and e2.visit_type like '%NEW PATIENT%'
        and e2.department_id = d2.department_id
        and p2.pat_enc_csn_id_coded = e2.pat_enc_csn_id_coded
    '''

    '''
    Focus on 1 referral type: REFERRAL TO DERMATOLOGY
    '''
    referral_code = referral.replace("REFERRAL TO ", "").replace(" ","-").replace("/","-")

    train_filepath = 'data/third_implementation/training_data_%s_firstSpecialtyVisit.csv'%referral_code

    if explore=='fraction_do_have_specialty_visit':
        '''
        How many referral encounters have at least one such specialty visit in the next 3 months?
        '''
        df_train = pd.read_csv('data/third_implementation/training_data.csv')
        df_tmp_referenc_specialty = df_train[df_train['referral_name']==referral]\
            [['referral_enc_id', 'specialty_name']].drop_duplicates()

        '''
        One encounter id can still map to multiple specialty_names
        '''
        all_refer_encs = df_tmp_referenc_specialty['referral_enc_id'].drop_duplicates()
        num_has_visit = 0
        for refer_enc in all_refer_encs:
            cur_visit_num = df_tmp_referenc_specialty[(df_tmp_referenc_specialty['referral_enc_id']==refer_enc)
                                & (df_tmp_referenc_specialty['specialty_name']==specialty)].shape[0]
            num_has_visit += (cur_visit_num>0)
        print "Fraction of %s's that has a followup visit in the next 3 months:"%referral_code \
                    + '%.2f'%(float(num_has_visit)/all_refer_encs.shape[0])
        quit()

    if not os.path.exists(train_filepath):

        df_train = pd.read_csv('data/third_implementation/training_data.csv')

        df_train_one = df_train[(df_train['referral_name']==referral)
                                & (df_train['specialty_name']==specialty)]

        df_train_one.to_csv('data/third_implementation/training_data_%s.csv'%referral_code, index=False)


        '''
        For each referral_enc_id, only consider the earliest followup specialty visit
        '''
        df_train_one = pd.read_csv('data/third_implementation/training_data_%s.csv'%referral_code)

        df_train_one = df_train_one.sort_values(['referral_enc_id', 'specialty_time'])

        df_tmp = df_train_one[['referral_enc_id', 'specialty_time']]\
                        .groupby('referral_enc_id').first().reset_index()

        if verbose:
            print 'Training size (num of referral encounters): ', df_tmp.shape[0]
        refer_to_first_special = dict(zip(df_tmp['referral_enc_id'].values, df_tmp['specialty_time'].values))

        df_train_one_firstSpecialtyVisit = df_train_one[df_train_one['specialty_time'] ==
                                df_train_one['referral_enc_id'].apply(lambda x: refer_to_first_special[x])]
        df_train_one_firstSpecialtyVisit.to_csv('data/third_implementation/training_data_%s_firstSpecialtyVisit.csv'%referral_code, index=False)

    else:

        df_train_one_firstSpecialtyVisit = pd.read_csv(train_filepath)

    '''
    Next goal: Based on icd10, predict 10 orders for each referral
    '''
    if verbose:
        print 'df_train_one_firstSpecialtyVisit.shape:', df_train_one_firstSpecialtyVisit.shape
        print df_train_one_firstSpecialtyVisit.head()

    # print df_train_derma_firstSpecialtyVisit['specialty_order'].groupby(
    #         df_train_derma_firstSpecialtyVisit['referral_icd10']).value_counts() \
    #         .groupby(level=[0, 1]).nlargest(3)
    df_tmp = df_train_one_firstSpecialtyVisit[['referral_icd10', 'specialty_order']].copy()
    # print df_tmp.groupby(['referral_icd10', 'specialty_order']).specialty_order.value_counts().nlargest(1)

    '''
    Handle multiple icd10 codes in a cell
    TODO: how to handle this? Not sure the order is for which icd10 code
    '''
    # print df_tmp[df_tmp.referral_icd10.str.contains(',')]

    '''
    Aggregate icd10 codes
    '''
    to_agg_icd10 = True
    if to_agg_icd10:
        df_tmp['referral_icd10'] = df_tmp['referral_icd10'].fillna('NA').apply(lambda x: x.split('.')[0])

    num_rows = df_train_one_firstSpecialtyVisit.shape[0]

    if explore == 'waiting_time_specialty_visit' or explore == 'full_icd10_to_orders_table':
        '''
        What are the common diagnostic codes mapped to the referral, and their stats
        '''
        icd10_cnter = Counter(df_tmp['referral_icd10'])
        icd10_cnt_common = icd10_cnter.most_common(5)

        icd10_prev = {}
        for icd10, cnt in icd10_cnter.items():
            icd10_prev[icd10] = float(cnt) / num_rows

    if explore=='waiting_time_specialty_visit':
        '''
        Waiting time until specialty visit
        '''
        print df_train_one_firstSpecialtyVisit.head()
        time_format = '%Y-%m-%d %H:%M:%S'

        df_tmp_timediff = df_train_one_firstSpecialtyVisit[['referral_enc_id','referral_time','specialty_time']].copy().drop_duplicates()
        df_tmp_timediff['specialty_timestamp'] = \
            df_tmp_timediff['specialty_time'].apply(lambda x: datetime.strptime(x, time_format))
        df_tmp_timediff['referral_timestamp'] = \
            df_tmp_timediff['referral_time'].apply(lambda x: datetime.strptime(x, time_format))
        df_tmp_timediff['time_diff'] = df_tmp_timediff['specialty_timestamp']\
            - df_tmp_timediff['referral_timestamp']

        print 'Train sample size for waiting time:', df_tmp_timediff['time_diff'].shape[0]
        all_waiting_days = df_tmp_timediff['time_diff'].apply(lambda x: x.days)
        plt.hist(all_waiting_days)
        plt.xlabel('Waiting days for %s'%referral)
        plt.savefig('data/third_implementation/figs/waiting_%s.png'%referral_code)
        quit()

    s = df_tmp['specialty_order'].groupby(df_tmp['referral_icd10']).value_counts()
    # print s.groupby(['referral_icd10', 'specialty_order']).nlargest(1)
    s = s.groupby(level=0).nlargest(5).reset_index(level=0, drop=True)

    icd10order_to_cnt = s.to_dict()
    icd10_to_orderCnt = {}
    for key, val in icd10order_to_cnt.items():
        icd10, order = key
        if icd10 in icd10_to_orderCnt:
            icd10_to_orderCnt[icd10].append((order, val))
        else:
            icd10_to_orderCnt[icd10] = [(order, val)]

    if explore=='full_icd10_to_orders_table':

        order_cnter = Counter(df_train_one_firstSpecialtyVisit['specialty_order'])

        '''
        Among all (1) first, (2) new patient visit (3) with that referral code, 
        (so, among all diagnoses code), 
        what are the prevalence for that order.
        '''
        order_prev = {}
        for order, cnt in order_cnter.items():
            order_prev[order] = float(cnt)/num_rows

        if verbose:
            print order_cnter
            print sorted(order_prev.items(), key=lambda (k,v):v)[::-1]

        df_explore_icd10_to_orders = pd.DataFrame(columns=['Icd10'] +
                                                          ['Top ' + str(x+1) +
                                                           ' Order, Prev, PPV, RR, PC_cnt, nonPC_cnt' for x in range(5)])
        top_entries = [[]*6 for _ in range(5)]

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

        for j,pair in enumerate(icd10_cnt_common[:5]):
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
                prev_str = '%.2f'%order_prev[order]
                cur_order_summary.append(prev_str)

                '''
                PPV, P(order|icd10) = P(order|icd10) / P(order|!icd10)
                '''
                ppv = float(conditioned_cnt)/icd10_cnter[icd10]
                ppv_str = '%.2f'%ppv
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
                denominator = (order_prev[order] - ppv*icd10_prev[icd10])/(1.-icd10_prev[icd10])
                rela_risk = ppv/denominator
                rr_str = '%.2f'%rela_risk
                cur_order_summary.append(rr_str)

                cur_order_summary.append(order_to_PCnonPC[order])

                cur_icd10_summary.append(cur_order_summary)


            top_entries[j] += cur_icd10_summary #[icd10] + top_orderCnts

            df_explore_icd10_to_orders.loc[len(df_explore_icd10_to_orders)] = top_entries[j]

        df_explore_icd10_to_orders.to_csv('data/third_implementation/df_explore_%s_icd10_to_orders.csv'%referral_code, index=False, float_format='%.2f')

        quit()
    '''
    (1.2.2) Test set query in 2017
    
    select 
        p1.pat_enc_csn_id_coded as referral_enc_id,
        p1.description as referral_name, 
        e1.appt_when_jittered as referral_time, 
        e1.jc_uid as pat_id,
        d1.icd9 as referral_icd9,
        d1.icd10 as referral_icd10,
        
        p2.pat_enc_csn_id_coded as specialty_enc_id,
        e2.appt_when_jittered as specialty_time,
        d2.department_name as specialty_dep, 
        d2.specialty as specialty_name, 
        p2.description as specialty_order
    from 
        datalake_47618.encounter e1,
        datalake_47618.order_proc p1,
        datalake_47618.diagnosis_code d1,
        
        datalake_47618.encounter e2,
        datalake_47618.order_proc p2,
        datalake_47618.dep_map d2
    where
        lower(p1.description) like '%referral%' 
        and p1.pat_enc_csn_id_coded = e1.pat_enc_csn_id_coded
        and p1.pat_enc_csn_id_coded = d1.pat_enc_csn_id_coded
        and e1.appt_when_jittered >= '2017-01-01'
        and e1.appt_when_jittered < '2018-01-01'
        
        and e1.jc_uid = e2.jc_uid
        and e1.pat_enc_csn_id_coded != e2.pat_enc_csn_id_coded
        and e1.appt_when_jittered <= e2.appt_when_jittered
        and DATE_ADD(date(timestamp(e1.appt_when_jittered)), INTERVAL 3 month) > date(timestamp(e2.appt_when_jittered))
        
        and e2.visit_type like '%NEW PATIENT%'
        and e2.department_id = d2.department_id
        and p2.pat_enc_csn_id_coded = e2.pat_enc_csn_id_coded
    '''
    test_filepath = 'data/third_implementation/test_data_%s_firstSpecialtyVisit.csv'%referral_code

    if not os.path.exists(test_filepath):
        df_test = pd.read_csv('data/third_implementation/test_data.csv')
        df_test_one = df_test[(df_test['referral_name']==referral)
                                & (df_test['specialty_name']==specialty)]
        if verbose:
            print df_test_one.head()

        df_test_one.to_csv('data/third_implementation/test_data_%s.csv'%referral_code, index=False)

        df_test_one = pd.read_csv('data/third_implementation/test_data_%s.csv'%referral_code)
        # print df_test_derma.head()

        df_test_one = df_test_one.sort_values(['referral_enc_id', 'specialty_time'])

        df_tmp = df_test_one[['referral_enc_id', 'specialty_time']]\
                        .groupby('referral_enc_id').first().reset_index()
        if verbose:
            print 'Test size (num of referral encounters): ', df_tmp.shape[0]

        refer_to_first_special = dict(zip(df_tmp['referral_enc_id'].values, df_tmp['specialty_time'].values))

        df_test_one_firstSpecialtyVisit = df_test_one[df_test_one['specialty_time'] ==
                                                           df_test_one['referral_enc_id'].apply(lambda x: refer_to_first_special[x])]
        df_test_one_firstSpecialtyVisit.to_csv('data/third_implementation/test_data_%s_firstSpecialtyVisit.csv'%referral_code, index=False)

    else:
        df_test_one_firstSpecialtyVisit = pd.read_csv(test_filepath)

    all_test_enc_ids = df_test_one_firstSpecialtyVisit['referral_enc_id'].drop_duplicates().values

    all_precisions =[]
    all_recalls = []
    for test_enc_id in all_test_enc_ids:
        df_cur = df_test_one_firstSpecialtyVisit[df_test_one_firstSpecialtyVisit['referral_enc_id']==test_enc_id].copy()

        cur_icd10s = df_cur['referral_icd10'].drop_duplicates().values

        actual_orders = df_cur['specialty_order'].drop_duplicates().values

        predicted_counters = Counter()
        '''
        TODO: How to handle multiple icd10s per encounter?
        '''
        for icd10 in cur_icd10s:
            if to_agg_icd10:
                icd10 = icd10.split('.')[0]
            cur_predicts = icd10_to_orderCnt.get(icd10, [('no-recommend', 0)])
            for cur_predict_order, cur_predict_cnt in cur_predicts:
                predicted_counters[cur_predict_order] += cur_predict_cnt

        predicted_top_5 = [x[0] for x in predicted_counters.most_common(5)]

        cur_prec = prec_at_k(actuals=actual_orders, predicts=predicted_top_5)
        cur_recall = recall_at_k(actuals=actual_orders, predicts=predicted_top_5)

        all_precisions.append(cur_prec)
        all_recalls.append(cur_recall)

    if verbose:
        print "Results for %s:"%referral
        print 'np.mean(all_precisions):', np.mean(all_precisions)
        print 'np.mean(all_recalls):', np.mean(all_recalls)
    return np.mean(all_precisions), np.mean(all_recalls)

def explore_referrals():
    '''
    (1.1) What is an example of well-mapped referral among large vol referrals?

    Choose REFERRAL TO DERMATOLOGY, which has vol of 5104 in the first half of 2016

    Top mapped specialties and their counts:
    Dermatology  7027
    Ophthalmology   602
    Oncology   467
    '''
    df = pd.read_csv('data/first_implementation/counter_all_referrals_descriptions_firstHalf2016.csv')
    # print df.head(20)

    df_refer2spec = pd.read_csv('data/JCquestion_20190318/referral_specialty_next3mo_newvisits_cnt_2016.csv')

    df_someRefer = df_refer2spec[df_refer2spec['description'].str.contains('ENDOCRINE')]\
                .copy().reset_index().sort_values('cnt', ascending=False)
    print df_someRefer

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

def main():
    referral_specialty_pairs = \
        [
            # ('REFERRAL TO DERMATOLOGY', 'Dermatology'),
            # ('REFERRAL TO GASTROENTEROLOGY', 'Gastroenterology'),
            # ('REFERRAL TO EYE', 'Ophthalmology'),
            # # REFERRAL TO PAIN CLINIC PROCEDURES,   Pain Management #(cnt: 525, but Neurosurgery has 224)
            # ('REFERRAL TO ORTHOPEDICS', 'Orthopedic Surgery'),
            # ('REFERRAL TO CARDIOLOGY', 'Cardiology'),
            # ('REFERRAL TO PSYCHIATRY', 'Psychiatry'),
            # ('SLEEP CLINIC REFERRAL', 'Sleep Center'),
            # ('REFERRAL TO ENT/OTOLARYNGOLOGY', 'ENT-Otolaryngology'),  # (cnt: 2170, but Oncology has 480)
            # ('REFERRAL TO PAIN CLINIC', 'Pain Management'),
            # ('REFERRAL TO UROLOGY CLINIC', 'Urology')  # (cnt: 2827, but Oncology has 605)
            #
            ('REFERRAL TO ENDOCRINE CLINIC', 'Endocrinology'), # Suggested by Jon Chen
            ('REFERRAL TO HEMATOLOGY', 'Hematology') # Suggested by Jon Chen
        ]
    '''
    Referral names (and their counts) inconsistency:
    2016: {'REFERRAL TO ENT/OTOLARYNGOLOGY': 39949, 'REFERRAL TO SURGERY OTOLARYNGOLOGY/HEAD&NEC': 22632, 'AMB REFERRAL TO ENT/OTOLARYNGOLOGY ALLERGY': 5205, 'REFERRAL TO ENT/OTOLARYNGOLOGY ALLERGY': 2441}
    2017: {'REFERRAL TO ENT/OTOLARYNGOLOGY': 115736}
    '''
    precisions = []
    recalls = []
    for referral, specialty in referral_specialty_pairs:
        precision, recall = main_onereferral(referral, specialty, explore='full_icd10_to_orders_table')
        precisions.append(precision)
        recalls.append(recall)
    res_df = pd.DataFrame({'referral': referral_specialty_pairs, 'precision': precisions, 'recall': recalls})
    print res_df
    res_df.to_csv("data/third_implementation/res_df.csv", index=False)

if __name__ == '__main__':
    main()