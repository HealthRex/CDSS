'''
Filter out patients without consecutive glucose level test records.
CSV files of EHR data are stored under directory "../data/bq/".
Output files (patient IDs) are stored under directory "../data/preprocessed".
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# path to csv files

PATH_TO_ID = "../data/bq/pat_id.csv"
PATH_TO_GLU = "../data/bq/lab_glu.csv"


# list of patients (unique ID)

df_glu = pd.read_csv(PATH_TO_GLU)
ID_list = np.unique(df_glu['rit_uid'].values)
print("Number of patients with glucose level record:", len(ID_list))

used_ID_list = list()


# restrict to those bing in hospital long enough and having enough glucose level records
df_glu['taken_time_jittered'] = pd.to_datetime(df_glu['taken_time_jittered'])
for pat_id in ID_list:
    print("--------Patient ID", pat_id)

    pat_glu = df_glu.loc[df_glu['rit_uid'] == pat_id]
    glu_time = pat_glu['taken_time_jittered'].values
    glu_t0 = glu_time[0]
    glu_tN = glu_time[-1]

    if len(glu_time) < 2: # at least 2 glu measure and 24 hours data
        print("-Too few glucose measure available.")
    elif (glu_tN-glu_t0).astype('timedelta64[h]').astype('int')<24:
        print("-Recorded time range too short.")
    else:
        # having at least 5 consecutive measure within 72 hours
        glu_time_diff = np.diff(glu_time).astype('timedelta64[h]').astype('int')
        start_ts_idx = [x_i for x_i, x in enumerate(glu_time_diff) if x > 72]
        start_ts_idx = [x+1 for x in start_ts_idx]
        start_ts_idx.insert(0,0)
        start_ts_diff_idx = [ts_i for ts_i, td in enumerate(np.diff(start_ts_idx)) if td > 3]
        start_ts_cont_idx = np.array(start_ts_idx)[start_ts_diff_idx]
        if len(start_ts_cont_idx)>0:
            used_ID_list.append(pat_id)

# save data
np.savetxt('../data/preprocessed/used_pat_id.csv', used_ID_list, delimiter=',', fmt='%s')