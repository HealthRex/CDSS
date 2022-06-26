'''
From EHR data, extract features that potentially relate to the glucose level.
CSV files of EHR data are stored under directory "../data/bq/".
Output files (features extracted) are stored under directory "../data/plots/patients/" and "../data/preprocessed".
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# paths to csv files

PATH_TO_ID = '../data/preprocessed/used_pat_id.csv'
PATH_TO_DIA_ID = '../data/bq/hemodialysis_pat.csv'

PATH_TO_DEMO = "../data/bq/pat_demo.csv"
PATH_TO_WEIGHT = "../data/bq/pat_w.csv"

PATH_TO_GLU = "../data/bq/lab_glu.csv"
PATH_TO_A1C = "../data/bq/lab_a1c.csv"
PATH_TO_CREA = "../data/bq/lab_crea.csv"  # creatine

PATH_TO_INS = "../data/bq/ord_ins.csv"
PATH_TO_ST1 = "../data/bq/ord_hyd.csv"  # hydrocortisone
PATH_TO_ST2 = "../data/bq/ord_pre.csv"  # prednisone
PATH_TO_ST3 = "../data/bq/ord_met.csv"  # methylprednisolone
PATH_TO_ST4 = "../data/bq/ord_dex.csv"  # dexamethasone

PATH_TO_DIET = "../data/bq/diet.csv"

PATH_TO_OUTPUT = "../data/plots/patients/"
PATH_TO_USED_ID = "../data/bq/used_pat_id.csv"
PATH_TO_SAVE = "../data/preprocessed/"

# corticosteroid equivalence
steroid_name = ['hydrocortisone', 'prednisone', 'methylprednisolone', 'dexamethasone']
steroid_equiv = {'hydrocortisone':20, 'prednisone': 5, 'methylprednisolone': 4, 'dexamethasone': 0.75}

# glucose to a1c conversion
glu_2_a1c = {126:6, 140:6.5, 154:7, 169:7.5, 183:8, 197:8.5, 212:9, 226:9.5, 240:10}
ref_glu = list(glu_2_a1c.keys())


# list of patient IDs to be used
IDs = pd.read_csv(PATH_TO_ID, header=None).values.tolist()
dia_IDs = pd.read_csv(PATH_TO_DIA_ID, header=None).values.tolist()  # filter out those with hemodialysis
IDs = [x for x in IDs if not x in dia_IDs]


# Data tables

# demographic info
df_demo = pd.read_csv(PATH_TO_DEMO)
# weights
df_w = pd.read_csv(PATH_TO_WEIGHT)
# glucose measure
df_glu = pd.read_csv(PATH_TO_GLU)
df_glu['taken_time_jittered'] = pd.to_datetime(df_glu['taken_time_jittered'])
# A1c measure
df_a1c = pd.read_csv(PATH_TO_A1C)
df_a1c['taken_time_jittered'] = pd.to_datetime(df_a1c['taken_time_jittered'])
# creatinine measure: mg/dL
df_crea = pd.read_csv(PATH_TO_CREA)
df_crea['taken_time_jittered'] = pd.to_datetime(df_crea['taken_time_jittered'])
# insulin
df_ins = pd.read_csv(PATH_TO_INS)
# steroid order record
steroid = dict()
for i in range(1, 4):
    file = 'PATH_TO_ST' + str(i)
    df_ste = None
    exec("steroid[steroid_name[i-1]] = pd.read_csv(%s)" % file)
# diet order
df_diet = pd.read_csv(PATH_TO_DIET)


data_dict = dict()
data = list()

err_ID_list = list()  # to store erroneous patients (missing information thus table can not be read correctly)

# time difference since short/long-acting insulin doses
short_enum = [0.5,1,3]
long_enum = [6,12,24]


for pat_idx, pat_id in enumerate(IDs[:]):
    pat_id = pat_id[0]
    print("--------Patient ID", pat_id, pat_idx)

    try:
        # Load patient-specific data
        print("Loading...")

        # creatinine measures
        pat_crea = df_crea.loc[df_crea['rit_uid'] == pat_id]
        ignore_by_crea = False
        if len(pat_crea)>0:
            crea_lvl = pat_crea['ord_num_value'].values
            crea_time = pat_crea['taken_time_jittered'].values
            ignore_by_crea = np.max(crea_lvl)>5  # ignore patient with crea_lvl>5
            print(np.max(crea_lvl))
        else:
            ignore_by_crea = True  # discard patient with no crea measure

        if ignore_by_crea:
            print("Filtered out by CREATININE")
        else:
            # glucose measures
            pat_glu = df_glu.loc[df_glu['rit_uid'] == pat_id]
            glu_lvl = pat_glu['result'].values
            glu_time = pat_glu['taken_time_jittered'].values

            # demo
            pat_demo = df_demo.loc[df_demo['rit_uid'] == pat_id]
            gender = pat_demo['gender'].values[0]
            dob = pd.to_datetime(pat_demo['dob'].values[0])

            # weight
            pat_w = df_w.loc[df_w['rit_uid'] == pat_id]
            if len(pat_w) > 0:
                weights = pat_w['meas_value'].values.tolist()
                weight_time = pat_w['recorded_time_jittered'].values

            # A1c
            pat_a1c = df_a1c.loc[df_a1c['rit_uid'] == pat_id]
            if len(pat_a1c) > 0:
                unit_a1c = pat_a1c['reference_unit'].values[0]
                a1c_lvl = pat_a1c['result'].values
                a1c_time = pat_a1c['taken_time_jittered'].values

            # insulin
            pat_ins = df_ins.loc[df_ins['jc_uid'] == pat_id]
            dose = pat_ins['sig'].values
            dose_time = pd.to_datetime(pat_ins['taken_time_jittered'].values)
            ins_des = pat_ins['med_description'].values
            ins_type = np.zeros(dose.shape)  # 1 for short-acting, 2 for long-acting
            for ins_i, ins_d in enumerate(ins_des):
                if 'REGULAR' in ins_d or 'LISPRO' in ins_d or 'ASPART' in ins_d:
                    ins_type[ins_i] = 1
                elif 'NPH' in ins_d or 'DETEMIR' in ins_d or 'GLARGINE' in ins_d:
                    ins_type[ins_i] = 2

            # steroid order record
            steroid = dict()
            for i in range(1, 4):
                # print(steroid_name[i-1])
                file = 'PATH_TO_ST' + str(i)
                df_ste = None
                exec("df_ste = pd.read_csv(%s)" % file)
                pat_ste = df_ste.loc[df_ste['jc_uid'] == pat_id]
                if len(pat_ste) > 0:
                    ste = pat_ste['sig'].values
                    ste_time = pd.to_datetime(pat_ste['taken_time_jittered'].values)
                    ste_dcrp = pat_ste['med_description'].values
                    steroid[steroid_name[i - 1]] = [ste, ste_time, ste_dcrp]

            # diet record
            pat_diet = df_diet.loc[df_diet['jc_uid'] == pat_id]
            npo_sign = False
            if len(pat_diet)>0:
                diet_time = pat_diet['proc_start_time_jittered'].values
                diet_des = pat_diet['description'].values
                npo_sign = 'NPO' in diet_des[0]


            # Process data
            print("Processing...")
            pat_data = list()
            gd = gender == "Male"

            # glucose measures
            glu_time_diff = np.diff(glu_time).astype('timedelta64[h]').astype('int')
            cont_meas_indices = [x_i for x_i, x in enumerate(glu_time_diff) if x < 24]

            for cont_meas_idx in cont_meas_indices[:-2]:
                prev_glu_lvl = glu_lvl[cont_meas_idx]
                cur_ts = glu_time[cont_meas_idx+1]
                cur_glu_lvl = glu_lvl[cont_meas_idx+1]

                # average measure in past 24 hours
                within_24h_measure_idx = np.where(np.logical_and(
                    (cur_ts - glu_time) <= np.timedelta64(24 * 60, 'm'), (cur_ts - glu_time) > np.timedelta64(0, 'm')))[0]
                glu_lvl_24h = glu_lvl[within_24h_measure_idx]
                avg_24h_glu = np.mean(glu_lvl_24h)  # mean
                var_24h_glu = np.var(glu_lvl_24h)  # variance
                time_diff_24h = (cur_ts - glu_time[within_24h_measure_idx]).astype('timedelta64[m]')  # in hour
                inverse_time_diff_24h = np.timedelta64(24 * 60, 'm') - time_diff_24h
                weighted_sum_glu_lvl_24h = np.sum(inverse_time_diff_24h / np.sum(inverse_time_diff_24h) * glu_lvl_24h)

                # Last glucose level at the similar time of the day
                time_1d_before = cur_ts - np.timedelta64(24 * 60, 'm')
                diff_1d_before_time = np.abs(time_1d_before - glu_time)
                closest_idx = np.argmin(diff_1d_before_time).astype('int')
                cloest_1d_before_time = glu_time[closest_idx]
                tol_time = np.timedelta64(120, 'm')
                if diff_1d_before_time[closest_idx] < tol_time:
                    glu_lvl_1d_before = glu_lvl[closest_idx]
                else:
                    glu_lvl_1d_before = np.nan

                # last insulin
                time_since_doses = (cur_ts - dose_time).astype('timedelta64[m]').astype('int')
                prev_doses_idx = set(np.where(time_since_doses >= 0)[0])
                short_doses_idx = set(np.where(ins_type == 1)[0])
                long_doses_idx = set(np.where(ins_type == 2)[0])

                # total dose in past 1 hours, 3 hours, 6 hours, 12 hours, 24 hours
                # doses_accum = np.zeros(5)
                short_accum = np.zeros(3)  # total short-acting in past 0.5 hours, 1 hours, 3 hours
                long_accum = np.zeros(3)  # total long-acting in past 6 hours, 12 hours, 24 hours

                for dose_time_diff_i, dose_time_diff in enumerate(short_enum):
                    short_time_diff = short_enum[dose_time_diff_i]
                    long_time_diff = long_enum[dose_time_diff_i]
                    dose_after_time_diff_start_idx = np.where(time_since_doses < dose_time_diff*60)[0]
                    dose_in_time_idx = prev_doses_idx & set(dose_after_time_diff_start_idx)
                    short_in_time_idx = short_doses_idx & dose_in_time_idx
                    if len(short_in_time_idx)>0:
                        short_accum[dose_time_diff_i] = np.sum([dose[j] for j in short_in_time_idx])
                for dose_time_diff_i, dose_time_diff in enumerate(long_enum):
                    dose_after_time_diff_start_idx = np.where(time_since_doses < dose_time_diff*60)[0]
                    dose_in_time_idx = prev_doses_idx & set(dose_after_time_diff_start_idx)
                    long_in_time_idx = long_doses_idx & dose_in_time_idx
                    if len(long_in_time_idx)>0:
                        long_accum[dose_time_diff_i] = np.sum([dose[j] for j in long_in_time_idx])

                # Total dose of steroids received (past 24 hours, or past 3 days)
                steroids_24h_total = 0
                steroids_3d_total = 0
                for i_sn, sn in enumerate(steroid_name):
                    # steroid_name: ['hydrocortisone', 'prednisone', 'methylprednisolone', 'dexamethasone']
                    if sn in steroid:
                        ste_24h_idx = np.where(np.logical_and(
                            (cur_ts - steroid[sn][1]) <= np.timedelta64(1, 'D'),
                            (cur_ts - steroid[sn][1]) >= np.timedelta64(0, 'D')))[0]
                        ste_24h = steroid[sn][0][ste_24h_idx]
                        steroids_24h_total += np.sum(ste_24h)/steroid_equiv[sn]

                        ste_3d_idx = np.where(np.logical_and(
                            (cur_ts - steroid[sn][1]) <= np.timedelta64(3, 'D'),
                            (cur_ts - steroid[sn][1]) >= np.timedelta64(0, 'D')))[0]
                        ste_3d = steroid[sn][0][ste_3d_idx]
                        steroids_3d_total += np.sum(ste_3d)/steroid_equiv[sn]

                # creatinine test
                closest_crea = np.nan
                closest_crea_idx = \
                    np.where(cur_ts - pd.DatetimeIndex(crea_time) >= np.timedelta64(0, 'D'))[0][-1]
                closest_crea = crea_lvl[closest_crea_idx]
                closest_crea_time = (cur_ts - crea_time[closest_crea_idx]).astype('timedelta64[m]').astype('int')
                closest_crea_time_h = float(closest_crea_time)/60

                # Weight (in ounces)
                closest_weight = np.nan
                if len(pat_w) > 0:
                    closest_weight_idx = \
                        np.where(cur_ts - pd.DatetimeIndex(weight_time) >= np.timedelta64(0, 'D'))[0][-1]
                    closest_weight = weights[closest_weight_idx]

                # Age (in years)
                age = (np.datetime64(cur_ts) - np.datetime64(dob)).astype('timedelta64[Y]').astype(int)

                # A1c  (past 3 months / most recent one / within 1 year)
                closest_a1c = np.nan
                if len(pat_a1c) > 0:
                    time_since_a1c = cur_ts - pd.DatetimeIndex(a1c_time)
                    closest_a1c_idx = np.where(np.logical_and(time_since_a1c >= np.timedelta64(0, 'm'),
                                                              time_since_a1c <= np.timedelta64(1, 'Y')))[0]
                    if len(closest_a1c_idx) > 0:
                        closest_a1c = a1c_lvl[closest_a1c_idx][-1]

                if np.isnan(closest_a1c): # calculate a1c from glu
                    closest_a1c = glu_2_a1c[ref_glu[np.argmin(np.abs(ref_glu-prev_glu_lvl))]]

                # characteristic of timestamp
                # how close to midnight (the day before)
                midnight = pd.Timestamp(pd.to_datetime(cur_ts).date())
                # take sine and cosine
                since_midnight_sine = np.sin((cur_ts - np.datetime64(midnight)) / np.timedelta64(1, 'D') * 2 * np.pi)
                since_midnight_cosine = np.cos((cur_ts - np.datetime64(midnight)) / np.timedelta64(1, 'D') * 2 * np.pi)

                # next glucose
                next_glu_time_diff_h = (glu_time[cont_meas_idx + 2] - cur_ts).astype('timedelta64[h]').astype(int)
                next_glu_lvl = glu_lvl[cont_meas_idx + 2]

                # combine all data into array
                data_point = [pat_idx, gd, age, closest_weight, npo_sign, prev_glu_lvl,
                              avg_24h_glu, var_24h_glu, weighted_sum_glu_lvl_24h, cur_glu_lvl, glu_lvl_1d_before,
                              steroids_24h_total, steroids_3d_total, closest_a1c,
                              since_midnight_sine, since_midnight_cosine,
                              closest_crea, closest_crea_time_h, cur_ts,
                              next_glu_time_diff_h, next_glu_lvl]
                # data_point.extend(doses_accum)
                data_point.extend(short_accum)
                data_point.extend(long_accum)
                data_point.append(cur_glu_lvl)

                pat_data.append(data_point)

            pat_data_all = np.vstack(pat_data).T
            data_dict[pat_id] = pat_data_all
            data.append(pat_data_all)
            print("DONE!")
    except:
        print("Error!")
        err_ID_list.append(pat_id)  # if any info missing and cannot read table correctly

data_all = np.hstack(data)


# save data

np.savetxt(PATH_TO_SAVE+'0519data.out', data_all, delimiter=',')
np.savetxt(PATH_TO_SAVE+'0519errIDs.csv', err_ID_list, delimiter=',', fmt='%s')

feature_names = ['pat_idx', 'gender','age', 'closest_weight', 'npo', 'prev_glu_lvl',
                      'avg_24h_glu', 'var_24h_glu', 'weighted_sum_glu_lvl_24h', 'cur_glu_lvl', 'glu_lvl_1d_before',
                      'steroids_24h_total', 'steroids_3d_total', 'closest_a1c',
                      'since_midnight_sine', 'since_midnight_cosine',
                      'closest_crea', 'closest_crea_time_h', 'cur_ts',
                      'next_glu_time_diff_h', 'next_glu_lvl']

for dose_time_diff in [str(i) for i in short_enum]:
    feature_names.append('short_'+dose_time_diff+'h')
for dose_time_diff in [str(i) for i in long_enum]:
    feature_names.append('long_'+dose_time_diff+'h')
feature_names.append('cur_glu_lvl')

df = pd.DataFrame(data_all.T, columns=feature_names)
df.to_csv(PATH_TO_SAVE+'data.csv', sep=',')


