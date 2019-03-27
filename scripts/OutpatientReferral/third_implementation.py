

'''
Goal: Use referral + diagnoses to predict specialty and orders

(1) Focus only on those with unambiguous referral -> specialty mapping

'''

import pandas as pd
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)

'''
(1.1) What is an example of well-mapped referral among large vol referrals?

Choose REFERRAL TO DERMATOLOGY, which has vol of 5104 in the first half of 2016

Top mapped specialties and their counts: 
Dermatology  7027
Ophthalmology   602
Oncology   467
'''
# df = pd.read_csv('data/first_implementation/counter_all_referrals_descriptions_firstHalf2016.csv')
#
# df_refer2spec = pd.read_csv('data/JCquestion_20190318/referral_specialty_next3mo_newvisits_cnt_2016.csv')
# df_derm = df_refer2spec[df_refer2spec['description']=='REFERRAL TO DERMATOLOGY']\
#             .copy().reset_index().sort_values('cnt', ascending=False)

'''
(1.2) Do train and test for REFERRAL TO DERMATOLOGY. 

TODO: Could we assert that a (new visit) specialty has to come from referral?
'''

'''
(1.2.1) Training set query for 2016

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
# df_train = pd.read_csv('data/third_implementation/training_data.csv')
#
# df_train_derma = df_train[(df_train['referral_name']=='REFERRAL TO DERMATOLOGY')
#                         & (df_train['specialty_name']=='Dermatology')]
#
# df_train_derma.to_csv('data/third_implementation/training_data_derma.csv', index=False)

'''
For each referral_enc_id, only consider the earliest followup specialty visit
'''
# df_train_derma = pd.read_csv('data/third_implementation/training_data_derma.csv')
# # print df_train_derma.head()
#
# df_train_derma = df_train_derma.sort_values(['referral_enc_id', 'specialty_time'])
#
# df_tmp = df_train_derma[['referral_enc_id', 'specialty_time']]\
#                 .groupby('referral_enc_id').first().reset_index()
# print 'Training size (num of referral encounters): ', df_tmp.shape[0]
# refer_to_first_special = dict(zip(df_tmp['referral_enc_id'].values, df_tmp['specialty_time'].values))
#
# df_train_derma_firstSpecialtyVisit = df_train_derma[df_train_derma['specialty_time'] ==
#                         df_train_derma['referral_enc_id'].apply(lambda x: refer_to_first_special[x])]
# df_train_derma_firstSpecialtyVisit.to_csv('data/third_implementation/training_data_derma_firstSpecialtyVisit.csv', index=False)

df_train_derma_firstSpecialtyVisit = pd.read_csv('data/third_implementation/training_data_derma_firstSpecialtyVisit.csv')
print df_train_derma_firstSpecialtyVisit.shape
