
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


def train_model(k=10, start_col='referral'): #
    '''
    Returns:
        A dictionary that can be used to predict the top 10 orders associated with each referral
    '''
    if start_col=='referral':
        trained_datapath = 'data/refer2order_2016.csv'
        df = pd.read_csv(trained_datapath)
        df = df.drop(['Unnamed: 0', 'specialty'], axis=1)
    elif start_col=='specialty':
        trained_datapath = 'data/top10_orders_newvisits_2016.csv'
        df = pd.read_csv(trained_datapath)


    my_dict = df.set_index(start_col).to_dict(orient='index')
    for key, vals in my_dict.items():
        re_ordered_vals = []
        for i in range(1,11):
            try:
                cur_item = vals[str(i)].split(',')[0][2:-1] # TODO: assumption valid?
            except:
                cur_item = 'nonitem'
            re_ordered_vals.append(cur_item)
        my_dict[key] = re_ordered_vals
    return my_dict

def prec_at_k(actuals, predicts, k=10): # TODO: how to use k
    if len(predicts)==0 and len(actuals)==0:
        return float('nan')

    num_relevant = 0
    for predict in predicts:
        if predict in actuals:
            num_relevant += 1
    prec = float(num_relevant) / len(predicts)
    return prec


if __name__ == '__main__':

    start_col="specialty"

    refer2order_model = train_model(start_col=start_col)

    '''
    An extra layer: referral -> specialty
    '''
    if start_col == 'referral':
        refer2spec_df = pd.read_csv('data/JCquestion_20190318/referral_specialty_next3mo_newvisits_cnt_2016.csv')
        refer2spec_dict = dict(zip(refer2spec_df['description'].values, refer2spec_df['specialty'].values))

    '''
    Get test data by query:
    Granularity: Each row is a specific encounter
    Want referral code (p1.description), department name & specialty, list of orders
    
    Raw queried data: referral, refer_enc_id, department_name, specialty, item
    Key: referral + refer_enc_id (a refer_enc_id could correspond to several referrals)
    Val: associated orders
    
    Ideal processed data: {(referral, enc_id): relevant orders}
    
    for each referral: (TODO: maintain a list of enc_ids for each referral)
        get all (referral, enc_id) keys: (TODO: get a dictionary of key:val)
            get pred by using model
            compare against true orders (val)
    
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

    '''
    get dict: {referral: a list of enc_ids}
    '''
    referral_to_encs_dict = df_test[['referral', 'refer_enc_id']]\
                                .groupby('referral')['refer_enc_id'].apply(list).to_dict()


    '''
    get dict: {(referral, enc_id): relevant orders}
    '''

    keys = zip(df_test['refer_enc_id'].values, df_test['referral'].values)

    vals = df_test['item'].values
    actual_orders_dict = {}
    for i in range(len(keys)):
        if keys[i] in actual_orders_dict:
            actual_orders_dict[keys[i]].append(vals[i])
        else:
            actual_orders_dict[keys[i]] = [vals[i]]

    f = open('data/actual_predict_samples.txt', 'w')


    case_to_look_each_type = 10

    '''
    Check the prec@k for each type
    '''

    avgprecs_by_referral = {}

    all_referrals = referral_to_encs_dict.keys()
    for referral in all_referrals:
        predict_orders = refer2order_model.get(referral, ['nonitem_predict']) # TODO

        enc_ids = referral_to_encs_dict[referral]

        precs_by_referral = []
        case_ind = 0
        for enc_id in enc_ids:
            actual_orders = actual_orders_dict.get((enc_id, referral), ['nonitem_actual']) # TODO

            cur_prec = prec_at_k(actual_orders, predict_orders)

            '''
            For each type of referral, check 10 examples
            '''
            if case_ind < case_to_look_each_type and referral=='REFERRAL TO NEUROGENETICS ONCOLOGY':
                f.write('referral:' + referral + '\n')
                f.write('specialty:' + str(refer2spec_dict.get(referral, 'no_corresponding_specialty')) + '\n')
                f.write('actual_orders:' + str(actual_orders) + '\n')
                f.write('predict_orders:' + str(predict_orders) + '\n')
                if cur_prec > 0:
                    f.write('Something matched!\n')
                f.write('\n')

                case_ind += 1
            precs_by_referral.append(cur_prec)
        avgprecs_by_referral[referral] = sum(precs_by_referral)/len(precs_by_referral)


    f.close()
    for key, val in sorted(avgprecs_by_referral.items(), key=lambda (k,v):v)[::-1]:
        print 'referral, avgprec:', key, val
    # print 'mean precision at 10:', sum(all_precs)/len(all_precs)

