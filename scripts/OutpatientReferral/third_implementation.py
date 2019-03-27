

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


def main(referral, specialty, verbose=False):
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

def explore_data():
    '''
    (1.1) What is an example of well-mapped referral among large vol referrals?

    Choose REFERRAL TO DERMATOLOGY, which has vol of 5104 in the first half of 2016

    Top mapped specialties and their counts:
    Dermatology  7027
    Ophthalmology   602
    Oncology   467
    '''
    df = pd.read_csv('data/first_implementation/counter_all_referrals_descriptions_firstHalf2016.csv')
    print df.head(20)

    df_refer2spec = pd.read_csv('data/JCquestion_20190318/referral_specialty_next3mo_newvisits_cnt_2016.csv')

    df_someRefer = df_refer2spec[df_refer2spec['description']=='REFERRAL TO UROLOGY CLINIC']\
                .copy().reset_index().sort_values('cnt', ascending=False)
    print df_someRefer.head(10)

if __name__ == '__main__':
    referral_specialty_pairs =\
    [
        ('REFERRAL TO DERMATOLOGY', 'Dermatology'),
        ('REFERRAL TO GASTROENTEROLOGY',   'Gastroenterology'),
        ('REFERRAL TO EYE',    'Ophthalmology'),
            # REFERRAL TO PAIN CLINIC PROCEDURES,   Pain Management #(cnt: 525, but Neurosurgery has 224)
        ('REFERRAL TO ORTHOPEDICS',    'Orthopedic Surgery'),
        ('REFERRAL TO CARDIOLOGY',     'Cardiology'),
        ('REFERRAL TO PSYCHIATRY', 'Psychiatry'),
        ('SLEEP CLINIC REFERRAL', 'Sleep Center'),
        ('REFERRAL TO SURGERY OTOLARYNGOLOGY/HEAD&NEC', 'ENT-Otolaryngology'), #(cnt: 2170, but Oncology has 480)
        ('REFERRAL TO PAIN CLINIC', 'Pain Management'),
        ('REFERRAL TO UROLOGY CLINIC', 'Urology') #(cnt: 2827, but Oncology has 605)
    ]
    precisions = []
    recalls = []
    for referral, specialty in referral_specialty_pairs:
        precision, recall = main(referral, specialty)
        precisions.append(precision)
        recalls.append(recall)
    res_df = pd.DataFrame({'referral':referral_specialty_pairs, 'precision':precisions, 'recall':recalls})
    print res_df
    res_df.to_csv("data/third_implementation/res_df.csv", index=False)