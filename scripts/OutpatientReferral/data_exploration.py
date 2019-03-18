
import pandas as pd
pd.set_option('display.width', 1000)

from collections import Counter

'''
Scenario: upon referral
Query to obtain all primary-care encounters that referred the patient to a different unit

select 
    distinct t1.pat_enc_csn_id_coded 
from
  datalake_47618.order_proc t1,
  datalake_47618.encounter t2, 
  datalake_47618.dep_map t3 
where 
  t1.pat_enc_csn_id_coded = t2.pat_enc_csn_id_coded
  and t1.ordering_date_jittered < '2016-07-01'
  and t1.ordering_date_jittered >= '2016-01-01'
  and lower(t1.description) like '%referral%'
  and t2.department_id = t3.department_id
  and t3.specialty = 'Primary Care'
;
'''

# df = pd.read_csv('data/pat_enc_primary2other.csv')
# print df.shape
# print df.head()
#
# df = df.drop_duplicates()
# df.to_csv('data/pat_enc_primary2other.csv', index=False)

'''
Scenario: upon consultation
How does t1.description map to t3.specialty? 
'''

'''
(1) How many order_proc descriptions are there?
select 
    description
from 
    datalake_47618.order_proc t1
where
    t1.ordering_date_jittered < '2016-07-01'
    and t1.ordering_date_jittered >= '2016-01-01'
;
'''

# df = pd.read_csv('data/all_orderProc_descriptions_firstHalf2016.csv')
# print df.shape
#
# from collections import Counter
# cnter = Counter(df['description'].values.tolist())
# df_counter = pd.DataFrame.from_dict(cnter, orient='index').reset_index().rename(columns={0:'cnt'}).sort_values('cnt', ascending=False)
# print df_counter.head()
# df_counter.to_csv('data/counter_all_orderProc_descriptions_firstHalf2016.csv', index=False)

'''
(2) How many order_proc descriptions (that contains "referral") are there?
'''
# df = pd.read_csv('data/counter_all_orderProc_descriptions_firstHalf2016.csv')
# df_referral = df[df['index'].str.contains('REFERRAL')]
# print df_referral
# df_referral.rename(columns={'index':'description'}).to_csv('data/counter_all_referrals_descriptions_firstHalf2016.csv')

'''
(3) How many departments are there?
'''
# df = pd.read_csv('data/dep_map.csv')
# df['specialty'].drop_duplicates().to_csv('data/deduplicated_specialties.csv', index=False)

'''
(4) Mapping referrals and specialties 
'''
from editdistance import distance
df_referral = pd.read_csv('data/counter_all_referrals_descriptions_firstHalf2016.csv')
referrals = df_referral['description'].values.tolist()
print 'numbers of unique referrals: ', len(referrals)

df_specialty = pd.read_csv('data/deduplicated_specialties.csv').rename(columns={'Unnamed: 0':'specialty'})
specialties = df_specialty['specialty'].values.tolist()
print 'number of unique specialties: ', len(specialties)

all_dists = {}
all_res = []
for referral in referrals:
    referral_cleaned = referral.replace("REFERRAL TO ", "").lower()
    cur_dists = {}
    for specialty in specialties:
        specialty_cleaned = specialty.lower()
        cur_dists[specialty] = distance(referral_cleaned, specialty_cleaned)/float(len(specialty_cleaned))

    top_10_mapped = sorted(cur_dists.items(), key=lambda (k,v):v)[:10]
    all_dists[referral] = top_10_mapped
    all_res.append([referral] + top_10_mapped)

df_mapping = pd.DataFrame(all_res, columns=['referral']+[str(x+1) for x in range(10)])
df_mapping.to_csv('data/map_referral_to_specialties.csv', index=False)