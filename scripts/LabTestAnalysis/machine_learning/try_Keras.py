

import keras

from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import roc_auc_score

import os
import collections
import numpy as np
import pandas as pd
pd.set_option('display.width', 500)
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

# TODO: secondary usage of FM

def _train_test_split(processed_matrix, outcome_label, columnToSplitOn='pat_id'):
    all_possible_ids = sorted(set(processed_matrix[columnToSplitOn].values.tolist()))

    train_ids, test_ids = train_test_split(all_possible_ids, random_state=123456789)

    train_matrix = processed_matrix[processed_matrix[columnToSplitOn].isin(train_ids)].copy()
    y_train = pd.DataFrame(train_matrix.pop(outcome_label))
    X_train = train_matrix

    test_matrix = processed_matrix[processed_matrix[columnToSplitOn].isin(test_ids)].copy()
    y_test = pd.DataFrame(test_matrix.pop(outcome_label))
    X_test = test_matrix
    return X_train, y_train, X_test, y_test

'''
Load data
'''
lab = 'LABA1C'
fm_io = FeatureMatrixIO()
processed_matrix = fm_io.read_file_to_data_frame("data-panels/%s/%s-normality-matrix-10000-episodes-processed.tab"
                 %(lab,lab))
X_train, y_train, X_test, y_test = _train_test_split(processed_matrix, 'all_components_normal')
X_train.pop('pat_id')
X_test.pop('pat_id')

features = X_train.columns.tolist()
print features


X_train, y_train, X_test, y_test = X_train.values, y_train.values, X_test.values, y_test.values

scaler = preprocessing.StandardScaler().fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

print "collections.Counter(y_train):", collections.Counter(y_train.flatten())
print "collections.Counter(y_test):", collections.Counter(y_test.flatten())
row, col = X_train.shape


'''
Build model
'''
model_file = "keras_model.h5"
use_cached_model = True

if not os.path.exists(model_file) or not use_cached_model:
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(32, input_dim=col, activation='relu'))
    #model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(32, activation='relu'))
    #model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(1, activation='sigmoid'))

    sgd = keras.optimizers.SGD(lr=0.1, decay=1e-4, momentum=0.1, nesterov=True)
    model.compile(loss='binary_crossentropy',
                  optimizer=sgd,#'adam',
                  metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=200, batch_size=128)
    model.save(model_file)
#pickle.dump(model, open("keras_model.pickle",'wb'), protocol=pickle.HIGHEST_PROTOCOL)
else:
    model = keras.models.load_model(model_file)

# cur_input = [0.]*len(features)
# cur_output = model.predict(np.reshape(cur_input, (1,len(features))))
# print "no feature:", cur_output
#
# for i in range(len(features)):
#     cur_input = [0.]*len(features)
#     cur_input[i] = 1000
#     cur_output = model.predict(np.reshape(cur_input, (1,len(features))))
#     print features[i], cur_output

y_pred_proba = model.predict_proba(X_test, batch_size=128)
# print collections.Counter(y_pred_proba.flatten())
print roc_auc_score(y_test.flatten(), y_pred_proba.flatten())

