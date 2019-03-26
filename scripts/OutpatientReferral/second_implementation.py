
'''


'''
import numpy as np
import pandas as pd
pd.set_option('display.width', 1000)

'''
Preparing Training data:

select
    d.department_name,
    p2.pat_enc_csn_id_coded as specialty_enc_id,
    d.specialty,
    p2.description as item
from
    datalake_47618.order_proc p2,
    datalake_47618.encounter e2,
    datalake_47618.dep_map d
where
    e2.visit_type like '%NEW PATIENT%'
    and e2.department_id = d.department_id
    and e2.appt_when_jittered >= '2016-01-01'
    and e2.appt_when_jittered < '2017-01-01'
    and p2.pat_enc_csn_id_coded = e2.pat_enc_csn_id_coded
    
Then, create dictionary specialty_to_orders as training
'''
df_train = pd.read_csv('data/second_implementation/training_data.csv')
print df_train.head()
all_specialties = df_train['specialty'].drop_duplicates().values.tolist()

df_tmp = df_train[['specialty', 'item', 'specialty_enc_id']].groupby(['specialty', 'item']).count()\
        .rename(columns={'specialty_enc_id':'cnt'}).reset_index().sort_values('cnt', ascending=False)
print df_tmp.head()
specialty_to_orders = {}
for specialty in all_specialties:
    df_tmptmp = df_tmp[df_tmp['specialty']==specialty].copy().reset_index().iloc[:10]
    specialty_to_orders[specialty] = df_tmptmp['item'].values.tolist()

'''
Preparing Test data:

select
    d.department_name,
    p2.pat_enc_csn_id_coded as specialty_enc_id,
    d.specialty,
    p2.description as item
from
    datalake_47618.order_proc p2,
    datalake_47618.encounter e2,
    datalake_47618.dep_map d
where
    e2.visit_type like '%NEW PATIENT%'
    and e2.department_id = d.department_id
    and e2.appt_when_jittered >= '2017-01-01'
    and p2.pat_enc_csn_id_coded = e2.pat_enc_csn_id_coded
    
For testing, group by encounters!
'''
df_test = pd.read_csv('data/second_implementation/test_data.csv')
all_encounters = df_test['specialty_enc_id'].drop_duplicates().sample(1000).values.tolist()

from first_implementation import prec_at_k
all_precs = []
precs_by_specialty = {}
f = open('data/actual_predict_start_from_specialties_samples.txt', 'w')
for encounter in all_encounters:
    df_tmp = df_test[df_test['specialty_enc_id']==encounter]
    cur_items = df_tmp['item'].values.tolist()
    specialty = df_tmp['specialty'].values.tolist()[0]

    actuals = cur_items
    predicts = specialty_to_orders.get(specialty, 'no_mapped_order')
    if len(predicts)==0:
        continue
    cur_prec = prec_at_k(actuals=actuals, predicts=predicts)

    f.write('specialty:' + specialty + '\n')
    f.write('actual_orders:' + str(actuals) + '\n')
    f.write('predict_orders:' + str(predicts) + '\n')
    f.write('precision at 10: ' + str(cur_prec) + '\n')
    f.write('\n')

    if specialty in precs_by_specialty:
        precs_by_specialty[specialty].append(cur_prec)
    else:
        precs_by_specialty[specialty] = [cur_prec]

    all_precs.append(cur_prec)
f.close()
print 'average prec:', sum(all_precs)/len(all_precs)

print sorted(precs_by_specialty.items(), key=lambda (k,v):np.mean(v))[::-1]