'''
Regression:
predict glucose level at current time stamp
Files of input data are stored under directory "../data/preprocessed".
Output files (patient IDs) are stored under directory ""../data/plots/patients-class".
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from sklearn import metrics
from sklearn.svm import SVC
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel, RBF
from sklearn.gaussian_process import GaussianProcessClassifier


PATH_TO_OUTPUT = "../data/plots/patients-class/"

feature_names = ['pat_idx', 'gender','age', 'closest_weight', 'npo', 'prev_glu_lvl',
                      'avg_24h_glu', 'var_24h_glu', 'weighted_sum_glu_lvl_24h', 'cur_glu_lvl', 'glu_lvl_1d_before',
                      'steroids_24h_total', 'steroids_3d_total', 'closest_a1c',
                      'since_midnight_sine', 'since_midnight_cosine',
                      'closest_crea', 'closest_crea_time_h', 'cur_ts',
                      'next_glu_time_diff_h', 'next_glu_lvl']
# time difference since short/long-acting insulin doses
short_enum = [0.5,1,3]
long_enum = [6,12,24]
for dose_time_diff in [str(i) for i in short_enum]:
    feature_names.append('short_'+dose_time_diff+'h')
for dose_time_diff in [str(i) for i in long_enum]:
    feature_names.append('long_'+dose_time_diff+'h')
feature_names.append('cur_glu_lvl')

df = pd.read_csv('../data/preprocessed/data.csv', sep=',')
df.head()

df = df.drop(df.columns[0], axis=1)  # drop first unused column
y = df["cur_glu_lvl"]

######################
# Feature Selection

selected_features = ['avg_24h_glu', 'steroids_24h_total', 'steroids_3d_total', 'closest_a1c',
                     'gender','age', 'closest_weight', 'npo',  # 'prev_glu_lvl',
                     'var_24h_glu', 'glu_lvl_1d_before', #'weighted_sum_glu_lvl_24h',
                     'closest_crea', 'closest_crea_time_h',
                     'since_midnight_sine', 'since_midnight_cosine']
for dose_time_diff in [str(i) for i in short_enum]:
    selected_features.append('short_'+dose_time_diff+'h')
for dose_time_diff in [str(i) for i in long_enum]:
    selected_features.append('long_'+dose_time_diff+'h')
features = df[selected_features]

# time stamps
time = df['cur_ts']

data_IDs = df['pat_idx'].values.tolist()
data_IDs = [int(i) for i in data_IDs]


# check for irregular data
labels = y.values.tolist()
X = np.array(features.values.tolist())
# print(np.any(np.isnan(X)))

# remove nans
X_rmnan = X
y_rmnan = labels
time_rmnan = np.array(time.tolist())
for i in range(len(selected_features)):
    nan_glu_idx = np.where(np.isnan(X_rmnan[:,i]))[0]
    X_rmnan = np.delete(X_rmnan, nan_glu_idx, 0)
    y_rmnan = np.delete(y_rmnan, nan_glu_idx, 0)
    data_IDs = np.delete(data_IDs, nan_glu_idx, 0)
    time_rmnan = np.delete(time_rmnan,nan_glu_idx)
nan_glu_idx = np.where(np.isnan(y_rmnan))[0]
X_rmnan = np.delete(X_rmnan, nan_glu_idx, 0)
y_rmnan = np.delete(y_rmnan, nan_glu_idx, 0)
data_IDs = np.delete(data_IDs, nan_glu_idx, 0)
time_rmnan = np.delete(time_rmnan,nan_glu_idx)
data_idx = list(range(len(data_IDs)))


######################

# split training patients and testing patients
unique_IDs = np.unique(data_IDs)
print("Number of unique patients: ", len(unique_IDs))

num_pat = 500  # number of patients used | len(unique_IDs)
print("Patient used:", num_pat)

unique_IDs = unique_IDs[0:num_pat]

tr_te_split = 0.7
tr_num = int(tr_te_split*len(unique_IDs))
train_IDs = unique_IDs[0:tr_num]
test_IDs = unique_IDs[tr_num:]

last_train = np.where(data_IDs==train_IDs[-1])[0][-1]
last_test = np.where(data_IDs==test_IDs[-1])[0][-1]

train_idx = np.array(data_idx)[0:last_train+1]
test_idx = np.array(data_idx)[last_train+1:last_test+1]
test_IDs = np.array(data_IDs)[last_train+1:last_test+1]


# change to classification:
# 1: high, 0: in-range, -1: low

y_new = np.zeros(y_rmnan.shape)
for i in range(len(y_rmnan)):
    if y_rmnan[i]>200:
        y_new[i] = 1
    elif y_rmnan[i]<70:
        y_new[i] = -1
print("Number of data points:", len(y_new))
for v in [-1,0,1]:
    print("class "+str(v)+": "+str(np.sum(y_new==v)))


print("Try training...")
X_train = X_rmnan[train_idx,:]
y_train = y_new[train_idx]
time_train = time_rmnan[train_idx]
X_test = X_rmnan[test_idx,:]
y_test = y_new[test_idx]
time_test = time_rmnan[test_idx]


# Validation Set
# val_IDs = unique_IDs[num_pat:num_pat+int(0.1*num_pat)]
# last_val = np.where(data_IDs==val_IDs[-1])[0][-1]
# val_idx = np.array(data_idx)[last_test+1:last_val+1]
# X_val = X_rmnan[val_idx,:]
# y_val = y_rmnan[val_idx]

print("train", X_train.shape)
print("test", X_test.shape)


# Normalize
scaler = preprocessing.MinMaxScaler()
X_rescale = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
# X_val = scaler.transform(X_val)


######################
# Classification Models: uncomment corresponding classifier part to use

weight = {-1:1.5, 0:0.5, 1:1.5}

# SVC
# clf = SVC(gamma='auto', class_weight=weight)

# # Random Forest
clf = RandomForestClassifier(n_estimators=100, max_depth=10,random_state=0, class_weight=weight) #max_depth=10, random_state=0,

# Guassian Process
# kernel = DotProduct(sigma_0=1)
# clf = GaussianProcessClassifier(kernel=kernel, random_state=0)


clf.fit(X_rescale, y_train)
y_pred = clf.predict(X_test)

accr = metrics.accuracy_score(y_test, y_pred)
print("Accuracy", accr)
r2 = metrics.r2_score(y_test, y_pred)
print("R2", r2)

cm = metrics.confusion_matrix(y_test, y_pred)
print("Confusion matrix")
print(cm)
print("accuracy within each class:")
print(np.diag(cm)/np.sum(cm, axis=1))
