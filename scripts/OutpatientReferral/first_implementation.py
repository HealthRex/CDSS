
'''
Goal:
In the test set, what is the precision@5 recommendations?

Data:
2016, New Patient Visit

Features:
Only 1 feature: Referral.

Methods:
Referral -> Most associated Specialty -> top 5 orders

Metrics:
precision@5 recommendations
'''

import pandas as pd
pd.set_option('display.width', 1000)


'''
Load data that were previously prepared?


Question: What is the "ground truth"?
Detailedly: For each referral, what are the actual "upcoming orders"?

This question seems not the most valid, because:
- When a primary care doctor gives a referral, the doctor should already know
which specialty that should be. So our task should not be "predicting specialty"

- However, this 'specialty' info is not in EMR. We have to statistically find
which specialties are associated with referral. (why though? sanity check?)

- Essentially, want to find which specialty leads to which tests.
    - Even better, adding in patient info upon prior referral?
    - Seems like need to reformulate the problem to focus on specialty, instead of referral!
'''


'''
Next steps:
(1) First implementation, check the top 10 recommendations given the specialty of any department 
(only 1 feature).
(2) Second implementation, check if adding in patient info (N features) upon the referral (will 
need backtrace in time to see which earlier referral leads to this specialty consultation) will 
improve the performance.

Referral -> Specialty mapping is not necessarily one-to-one, because:
(1) No visit by the patient
(2) Primary care doctor only knows the general but not the specific specialty to consult. 
There might be an extra layer (coordinator/scheduler?) to handle the referral-to-speciality mapping. 
(3) Really is referral-to-department mapping, where department has a "speciality" feature. But different 
departments with the same specialty might have different practice/routine of ordering things.
'''

'''
20190321
Try the first implementation of referral-to-department-to-specialty-to-order recommender 
'''


def train_model(refer2spec_df, spec2order_df):
    '''
    Input:
        refer2spec_df
        spec2order_df

    Returns:
        A dictionary that can be used to predict the top 10 orders associated with each referral

    '''

    pass


refer2spec_df = None
spec2order_df = None

refer2order_dict = train_model(refer2spec_df, spec2order_df)


'''
Get test data by query:
Granularity: Each row is a specific encounter
Want referral code (p1.description), department name & specialty, list of orders

select 
    p1.description as referral, 
    p1.pat_enc_csn_id_coded as refer_enc_id,
    d.department_name, 
    d.specialty, 
    p2.description as item
from 
    datalake_47618.order_proc p1,
    datalake_47618.order_proc p2,
    datalake_47618.encounter e1,
    datalake_47618.encounter e2,
    datalake_47618.dep_map d
where
    lower(p1.description) like '%referral%' 
    and p1.pat_enc_csn_id_coded = e1.pat_enc_csn_id_coded
    and e1.jc_uid = e2.jc_uid
    and e1.pat_enc_csn_id_coded != e2.pat_enc_csn_id_coded
    and e2.visit_type like '%NEW PATIENT%'
    and e1.appt_when_jittered <= e2.appt_when_jittered
    and DATE_ADD(date(timestamp(e1.appt_when_jittered)), INTERVAL 3 month) > date(timestamp(e2.appt_when_jittered))
    and e2.department_id = d.department_id
    and e1.appt_when_jittered >= '2017-01-01'
    and p2.pat_enc_csn_id_coded = e2.pat_enc_csn_id_coded
'''

df_test = pd.read_csv('data/JCquestion_20190318/testset_2017.csv')

encnt2order_dict_test = df_test.head(30)[['refer_enc_id', 'item']].\
        groupby('refer_enc_id')['item'].apply(list).to_dict()
refer2order_dict_test = df_test.head(30)[['refer_enc_id', 'referral']].\
        groupby('refer_enc_id')['referral'].apply(list).to_dict()
print encnt2order_dict_test
print refer2order_dict_test
