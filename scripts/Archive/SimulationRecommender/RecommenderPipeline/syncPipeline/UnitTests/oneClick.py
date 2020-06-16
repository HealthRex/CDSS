from helper import *
from configuration import *
import pandas as pd
import datetime
import re



# read pandas data from tracker into environment
df_4 = pd.read_csv(tracker_data + 'tracker_output/final_4.csv')
df_5 = pd.read_csv(tracker_data + 'tracker_output/final_5.csv')

# checks columns is same
set1 = set(df_5.columns)
set2 = set(df_4.columns)

# confirms columns are similar
diff1 = set1 - set2
diff2 = set2 - set1
print(diff1 == set())
print(diff2 == set())

df_tracker = pd.DataFrame(df_4.append(df_5))

now = datetime.datetime.now()
date_string = str(now.year) + '_' + str(now.month) + '_' + str(now.day) + '_' + str(now.hour) + '_' + str(now.second) + '_'
out_file = tracker_data + 'tracker_output/' + date_string + 'tracker_data_join.csv'  # Fill in with path to which csv output will be saved

#df_tracker.to_csv(out_file)

# join df_tracker with database joins (sim_patient joins on patient and sim_patient_id):

'''
$sim_patient_state
> base_table['sim_patient']
$sim_patient
   sim_patient_id                         name age_years gender
1              23 (User3) Hematemesis, Alcohol        59   Male

'''

df_tracker_merge = df_tracker.merge(sim_patient, left_on='patient', right_on='sim_patient_id')


# join df_tracker to user
'''
$sim_user
   sim_user_id            name
1            0    Default User
2            1   Jonathan Chen
3

'''

df_tracker_merge2 = df_tracker_merge.merge(sim_user, left_on='user', right_on='sim_user_id')

dx = df_tracker_merge2.drop_duplicates()

#print(df_tracker_merge2)

dx.to_csv(out_file)


#print(re.split('_ , _', dx.name_x))
#
