import sys
sys.path.insert(1, '/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/')

import tensorflow.keras as keras
import numpy as np
import tensorflow as tf
import pandas as pd
import json
import h5py
import os
from sklearn.metrics import precision_recall_fscore_support 
from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix

iterations = 1000
sample_size = 10000
num_processes = 40
threshold_log = 0.11
threshold_clinicnet = 0.5

model_dir = '/badvolume/home/ec2-user/cs230/scripts/clinicnet_model'
y_true_p = model_dir + 'evaluation/predictions/'
h5f = h5py.File(model_dir+'/evaluation/predictions/clinical_item/clinitem_test_proba.h5','r')
y_true = h5f['data_y'].value
h5f.close()

h5f = h5py.File(model_dir + '/evaluation/predictions/clinical_item/clinicnet_time_item.h5', 'r')
ClinicNet = h5f['clinicnet_time_item'].value
h5f.close()

h5f = h5py.File(model_dir+'/evaluation/predictions/clinical_item/clinitem_test_proba.h5','r')
y_true = h5f['data_y'].value
h5f.close()

h5f = h5py.File(model_dir+'/evaluation/predictions/clinical_item/log_proba_time.h5','r')
logistic = h5f['baseline_preds'].value
h5f.close()

h5f = h5py.File(model_dir+'/evaluation/predictions/order_set/labels_time.h5','r')
test = h5f['labels_time'].value
h5f.close()

test_list = np.load(model_dir + '/evaluation/predictions/test_ids.npz') # patient item ids
test_list = test_list['p_ids']
test_list = test_list.flatten()
test_list = list(test_list)

test_list_time = np.load(model_dir + '/evaluation/predictions/test_ids_clinitem_time.npz') # patient item ids
test_list_time = test_list_time['p_ids']
test_list_time = test_list_time.flatten()
test_list_time = list(test_list_time)

pid_2_id = {item: idx for idx, item in enumerate(test_list)}
subset_idx = [pid_2_id.get(item) for item in test_list_time]
y_true = y_true[subset_idx,:]


human_authored = pd.read_hdf('predictions/clinical_item/human_authored_df.h5', key='data')
p_id_list = human_authored.index.values
human_authored = human_authored.values.astype(int)

subset_pids = list(set(test_list_time) & set(p_id_list))
pid_2_id_time = {item: idx for idx, item in enumerate(test_list_time)}
pid_2_id_human = {item: idx for idx, item in enumerate(p_id_list)}
subset_idx = [pid_2_id_time.get(item) for item in subset_pids]
subset_log = logistic[subset_idx, :]
subset_ClinicNet = ClinicNet[subset_idx, :]
subset_y = y_true[subset_idx,:].astype(int)

subset_human = [pid_2_id_human.get(item) for item in subset_pids]
human_authored = human_authored[subset_human, :]

h5f = h5py.File(model_dir+'/evaluation/predictions/clinical_item/labels_time.h5','r')
# print(list(h5f.keys()))
labels_time = h5f['labels_time'].value
h5f.close()

pt_list_time = labels_time[:, 1]
pt_list_unique = np.unique(pt_list_time)
p_2_id = {x: [] for x in np.unique(pt_list_time)}
for idx, item in enumerate(pt_list_time):
    p_2_id[item].append(idx)

pt_list_sub = pt_list_time[subset_idx]
pt_list_unique_sub = np.unique(pt_list_sub)
p_2_id_sub = {x: [] for x in np.unique(pt_list_sub)}
for idx, item in enumerate(pt_list_sub):
    p_2_id_sub[item].append(idx)


def boot_logistic(i, sample_size=sample_size):
    np.random.seed(seed=i)
    
    random_pids = np.random.choice(pt_list_unique, size=sample_size, replace=True)
    test = np.array([p_2_id[pid] for pid in random_pids])
    boot_list = []
    for ids in test:
        size = len(ids)
        boot_list.append(np.random.choice(ids))    
    
    y_pred_sub = logistic[boot_list, :]
    y_true_sub = y_true[boot_list, :]
    # evaluate model
#     print('calculating')
    auroc = roc_auc_score(y_true_sub, y_pred_sub, average='micro')
    avg_precision = average_precision_score(y_true_sub, y_pred_sub, average='micro')
#     print('done')
    return (auroc, avg_precision)

def boot_clinicnet(i, sample_size=sample_size):
    np.random.seed(seed=i)
    random_pids = np.random.choice(pt_list_unique, size=sample_size, replace=True)
    test = np.array([p_2_id[pid] for pid in random_pids])
    boot_list = []
    for ids in test:
        size = len(ids)
        boot_list.append(np.random.choice(ids))    
        
    y_pred_sub = ClinicNet[boot_list, :]
    y_true_sub = y_true[boot_list, :]
    # evaluate model
#     print('calculating')
    auroc = roc_auc_score(y_true_sub, y_pred_sub, average='micro')
    avg_precision = average_precision_score(y_true_sub, y_pred_sub, average='micro')
#     print('done')

    return (auroc, avg_precision)

def boot_human(i, sample_size=sample_size):
    np.random.seed(seed=i)
    random_pids = np.random.choice(pt_list_unique_sub, size=sample_size, replace=True)
    test = np.array([p_2_id_sub[pid] for pid in random_pids])
    boot_list = []
    for ids in test:
        size = len(ids)
        boot_list.append(np.random.choice(ids))    
    y_pred_sub = human_authored[boot_list, :]
    y_true_sub = subset_y[boot_list, :]
    # evaluate model
#     print('calculating')

    
    output = precision_recall_fscore_support(y_true_sub.flatten(), y_pred_sub.flatten())
    precision = output[0][2]
    recall = output[1][2]
    f1 = output[2][2]

#     print('done')
    return precision, recall, f1
def boot_human_spec(i, sample_size=sample_size):
    np.random.seed(seed=i)
    random_pids = np.random.choice(pt_list_unique_sub, size=sample_size, replace=True)
    test = np.array([p_2_id_sub[pid] for pid in random_pids])
    boot_list = []
    for ids in test:
        size = len(ids)
        boot_list.append(np.random.choice(ids))   
    y_pred_sub = human_authored[boot_list, :]
    y_true_sub = subset_y[boot_list, :]
#     print(y_pred_sub)
#     print(y_true_sub)
    # evaluate model
#     print('calculating')
    matrix = confusion_matrix(y_true_sub, y_pred_sub)
    tn, fp, fn, tp = matrix[1:,1:].ravel()
    specificity = tn / (tn+fp)
#     print('done')
    return specificity

def boot_human_clinic(i, sample_size=sample_size):
    np.random.seed(seed=i)
    random_pids = np.random.choice(pt_list_unique_sub, size=sample_size, replace=True)
    test = np.array([p_2_id_sub[pid] for pid in random_pids])
    boot_list = []
    for ids in test:
        size = len(ids)
        boot_list.append(np.random.choice(ids))   
    y_pred_sub = subset_ClinicNet[boot_list, :]
    y_true_sub = subset_y[boot_list, :]
    auroc = roc_auc_score(y_true_sub, y_pred_sub, average='micro')
    avg_precision = average_precision_score(y_true_sub, y_pred_sub, average='micro')
    y_pred_sub[y_pred_sub<threshold_clinicnet] = 0
    y_pred_sub[y_pred_sub>=threshold_clinicnet] = 1
    # evaluate model
#     print('calculating')
    output = precision_recall_fscore_support(y_true_sub.flatten(), y_pred_sub.flatten())
#     print('done')
    precision = output[0][1]
    recall = output[1][1]
    f1 = output[2][1]
#     print('done')
    return auroc, avg_precision, precision, recall, f1
def boot_human_logistic(i, sample_size=sample_size):
    np.random.seed(seed=i)
    random_pids = np.random.choice(pt_list_unique_sub, size=sample_size, replace=True)
    test = np.array([p_2_id_sub[pid] for pid in random_pids])
    boot_list = []
    for ids in test:
        size = len(ids)
        boot_list.append(np.random.choice(ids))   
    y_pred_sub = subset_log[boot_list, :]
    y_true_sub = subset_y[boot_list, :]
    auroc = roc_auc_score(y_true_sub, y_pred_sub, average='micro')
    avg_precision = average_precision_score(y_true_sub, y_pred_sub, average='micro')
    y_pred_sub[y_pred_sub<threshold_log] = 0
    y_pred_sub[y_pred_sub>=threshold_log] = 1
    # evaluate model
#     print('calculating')
    output = precision_recall_fscore_support(y_true_sub.flatten(), y_pred_sub.flatten())
#     print('done')
    precision = output[0][1]
    recall = output[1][1]
    f1 = output[2][1]
#     print('done')
    return auroc, avg_precision, precision, recall, f1

def get_CI(array, alpha=0.95):
    p = ((1.0-alpha)/2.0) * 100
    lower = np.percentile(array, p)
    p = (alpha+((1.0-alpha)/2.0)) * 100
    upper = np.percentile(array, p)
    print('average: {}'.format(np.mean(array)))
    print('%.1f confidence interval %.1f and %.1f' % (alpha*100, lower*100, upper*100))
    
from multiprocessing import Process, Array, Queue, Pool

if __name__ == '__main__':
#     print('general comparison')
#     print('logistic')
#     p = Pool(processes = num_processes)
#     results =  p.map(boot_logistic, range(iterations))
#     list1, list2 = zip(*results)
#     print(list1)
#     get_CI(list1)    
#     print(list2)
#     get_CI(list2)
    
#     print('clinicnet')
#     p = Pool(processes = num_processes)
#     results =  p.map(boot_clinicnet, range(iterations))
#     list1, list2 = zip(*results)
#     print(list1)
#     get_CI(list1)
#     print(list2)
#     get_CI(list2)
    
    print('human authored comparison')
#     print('human')
#     p = Pool(processes = num_processes)
#     results =  p.map(boot_human, range(iterations))
#     pr, recall, f1 = zip(*results)
#     print(pr)
#     get_CI(pr)
#     print(recall)
#     get_CI(recall)
#     print(f1)
#     get_CI(f1)
    
#     # get specificity
#     print('human authored comparison specificity')
#     p = Pool(processes = num_processes)
#     results =  p.map(boot_human_spec, range(iterations))
#     pr= zip(*results)
#     print(pr)
#     get_CI(pr)

    print('log')
    p = Pool(processes = num_processes)
    results =  p.map(boot_human_logistic, range(iterations))
    auroc, avg_precision, pr, recall, f1 = zip(*results)
    print(auroc)
    get_CI(auroc)
    print(avg_precision)
    get_CI(avg_precision)
    print(pr)
    get_CI(pr)
    print(recall)
    get_CI(recall)
    print(f1)
    get_CI(f1)
         
    print('clinicnet')
    p = Pool(processes = num_processes)
    results =  p.map(boot_human_clinic, range(iterations))
    auroc, avg_precision, pr, recall, f1 = zip(*results)
    print(auroc)
    get_CI(auroc)
    print(avg_precision)
    get_CI(avg_precision)
    print(pr)
    get_CI(pr)
    print(recall)
    get_CI(recall)
    print(f1)
    get_CI(f1)
    

    # for i in range(5):
    #     boots(q)

    # p = Process(target = )
