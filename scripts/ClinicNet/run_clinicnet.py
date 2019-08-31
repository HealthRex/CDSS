import numpy as np
import tensorflow as tf
import pandas as pd
import json
import h5py
import os
from os import path
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Conv2D
from tensorflow import keras
from tensorflow.keras import Model
from tensorflow.python.client import device_lib
from utils.datagenerator import DataGenerator
from tensorflow.keras import backend as K
from sklearn.metrics import precision_recall_fscore_support as pr
import datetime
import sys
import shutil

load_model=True
NUM_EPOCH_START = int(sys.argv[1])
if NUM_EPOCH_START == 0:
    load_model=False
    
print('starting on epoch: {}'.format(NUM_EPOCH_START))
PATH = 'best_models/order_set/'
NOW = sys.argv[2]
if not os.path.exists('{}{}'.format(PATH,NOW)):
    print('making dir since DNE')
    os.makedirs('{}{}'.format(PATH,NOW))
if NUM_EPOCH_START == 0:
    shutil.copy(__file__, '{}{}/script_ran.py'.format(PATH,NOW))

if tf.test.is_gpu_available():
    print("GPU detected")
else:
    print('no GPU detected')
    


          
# get class weights for loss function if performing binary_crossentropy with class weights
path = '/badvolume/home/ec2-user/cs230/scripts/data/statistics/train2/freq_y.hdf5'
weights = pd.read_hdf(path)

class_weight = dict(zip(np.arange(0, len(weights)),1/(weights.values+0.0001)))
          
from tensorflow.keras import backend as K
import pandas as pd 
from sklearn.metrics import precision_recall_fscore_support as pr

          
# useful classes and functions for later 

def weighted_binary_crossentropy(y_true, y_pred):
    # Calculate the binary crossentropy
    zero_weight = 1
    one_weight = pw
    b_ce = K.binary_crossentropy(y_true, y_pred)

    # Apply the weights
    weight_vector = y_true * one_weight  + (1. - y_true) * zero_weight
    weighted_b_ce = weight_vector * b_ce

    # Return the mean error
    return K.mean(weighted_b_ce)

#     return weighted_binary_crossentropy

def binary_accuracy_V2(y_true, y_pred):
    '''Calculates the mean accuracy rate across all predictions for binary
    classification problems.
    '''
    y_true_edited = y_true[:,2:]
    y_pred_edited = y_pred[:,2:]
    return K.mean(K.equal(y_true, K.round(y_pred)))


def f1(y_true, y_pred):
    K.set_epsilon(1e-05)
    def recall(y_true, y_pred):
        """Recall metric.

        Only computes a batch-wise average of recall.

        Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        K.set_epsilon(1e-05)
        #y_pred = tf.convert_to_tensor(y_pred, np.float32)
        #y_true = tf.convert_to_tensor(y_true, np.float32)
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        """Precision metric.

        Only computes a batch-wise average of precision.

        Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        K.set_epsilon(1e-05)
        #y_pred = tf.convert_to_tensor(y_pred, np.float32)
        #y_true = tf.convert_to_tensor(y_true, np.float32)
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision
    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))
def precision(y_true, y_pred):
    K.set_epsilon(1e-05)
    #y_pred = tf.convert_to_tensor(y_pred, np.float32)
    #y_true = tf.convert_to_tensor(y_true, np.float32)
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision
def recall(y_true, y_pred):
    K.set_epsilon(1e-05)
    #y_pred = tf.convert_to_tensor(y_pred, np.float32)
    #y_true = tf.convert_to_tensor(y_true, np.float32)
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall
    
    
def f1_loss(y_true, y_pred):
    tp = K.sum(K.cast(y_true*y_pred, 'float'), axis=0)
    tn = K.sum(K.cast((1-y_true)*(1-y_pred), 'float'), axis=0)
    fp = K.sum(K.cast((1-y_true)*y_pred, 'float'), axis=0)
    fn = K.sum(K.cast(y_true*(1-y_pred), 'float'), axis=0)

    p = tp / (tp + fp + K.epsilon())
    r = tp / (tp + fn + K.epsilon())

    f1 = 2*p*r / (p+r+K.epsilon())
    f1 = tf.where(tf.math.is_nan(f1), tf.zeros_like(f1), f1)
    return 1 - K.mean(f1)


def flattenMatrix(mat):
    mat = pd.DataFrame(mat)
    n = len(mat)
    flattened = []
    for i in range(n):
        actual_vals = mat.loc[i, ].tolist()
        flattened.extend(actual_vals)
    return flattened

          
from sklearn.metrics import roc_curve, auc


def auc(y_true, y_pred):
    auc = tf.keras.metrics.AUC(y_true, y_pred)[1]
    K.get_session().run(tf.local_variables_initializer())
    return auc

import math
# if scale == None: generates uniform random value between start/end
# if scale == 'log': generate random variable r in [log(start),log(end)], then return 10^r
#     ex. if you input start:0.0001, end:1 it will return 10^r, where r in [-4,0]
def random_search(start, end, scale='uniform'):
    if scale == 'uniform':
        return np.random.uniform(start, end)
    elif scale == 'int':
        return np.random.randint(start,end)
    elif scale == 'log':
        a = math.log(start, 10)
        b = math.log(end, 10)
        r = np.random.uniform(a, b)
        return 10**r
    else:
        return 'ERROR'

# get random value from list
def random_grid_search(vals):
    length = len(vals)
    return vals[np.random.randint(0,length)]

def decrement_num_neurons(first, min_val, num_layers):
    layers = [first]
    random = np.random.rand()
    if random > 0.5:
        random = 50
    else:
        random = 0
    prev = first
    for j in range(num_layers-1):
        prev = max(prev-25, min_val) 
        layers.append(prev)
    return layers

def dropout_search(num_layers):
    possible_vals = [0.5, 0.4,0.35,0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0]
    d = []
    prev = None
    for l in range(num_layers-1):
        if l == 0:
            dl = possible_vals[np.random.randint(0,len(possible_vals))]
            d.append(dl)
            prev = dl
        else:
            dl = possible_vals[np.random.randint(0,len(possible_vals))]
            while dl > prev:
                dl = possible_vals[np.random.randint(0,len(possible_vals))]
            d.append(dl)
            prev = dl
    d.append(0)
    return d
          
def neural_network(num_layers, num_neurons, learning_rate, activation, dropout_rate, x_shape, y_shape, lam):
#     assert len(num_neurons) == len(dropout_rate)
    layers = []
    layers.append(tf.keras.layers.Dense(num_neurons[0], activation=activation, kernel_initializer=keras.initializers.glorot_normal(), 
                                        kernel_regularizer=keras.regularizers.l2(lam), 
                                        input_shape=(x_shape[1],)))
    for l in range(1, num_layers-2):
        layers.append(tf.keras.layers.Dense(num_neurons[l],kernel_initializer=keras.initializers.glorot_normal(), activation=activation, 
                                        kernel_regularizer=keras.regularizers.l2(lam)
                                           ))
        layers.append(tf.keras.layers.Dropout(dropout_rate))
        if use_batchnorm:
            layers.append(tf.keras.layers.BatchNormalization())
    layers.append(tf.keras.layers.Dense(y_shape[1], activation='sigmoid'))
    model = tf.keras.Sequential(layers)
#     optim = tf.keras.optimizers.Adam(learning_rate=learning_rate)
#     optim = tf.keras.optimizers.SGD()
    optim = tf.keras.optimizers.Nadam(learning_rate=learning_rate)
    model.compile(loss= 
#                   f1_loss,
#                   'binary_crossentropy',
                  weighted_binary_crossentropy,
              optimizer=optim,
              metrics = [binary_accuracy_V2, precision,recall, f1])

    return model

def logistic_model(num_layers, num_neurons, learning_rate, activation, dropout_rate, x_shape, y_shape, lam):
    layers = []
    layers.append(tf.keras.layers.Dense(y_shape[1], activation='sigmoid', kernel_initializer=keras.initializers.glorot_normal(), input_shape=(x_shape[1],)))
    model = tf.keras.Sequential(layers)
    SGD = tf.keras.optimizers.SGD()
    model.compile(loss='binary_crossentropy',
              optimizer=SGD,
              metrics = [binary_accuracy_V2, f1])
    return model

def initialize_keys(d,now):
    keys = ['parameters','loss','val_loss','f1','val_f1', 'acc', 'val_acc']
    new_entry = {}
    for k in keys:
        new_entry[k] = []
        
    d[now] = new_entry
    
    return d
def update_dicts(d, now, params, mod_hist):
    
    d[now]['parameters'] = params

    d[now]['loss'] = mod_hist['loss']
    d[now]['val_loss'] = mod_hist['val_loss']
    d[now]['f1'] = mod_hist['f1']
    d[now]['val_f1'] = mod_hist['val_f1']
    d[now]['acc'] = mod_hist['binary_accuracy_V2']
    d[now]['val_acc'] = mod_hist['val_binary_accuracy_V2']
#     d[now]['test_fscore'] = test_f_score
    return d

def run_nn(train_gen, val_gen, params, now):
    num_layers = params['num_layers']
    num_neurons = params['num_neurons']
    learning_rate = params['learning_rate']
    activation = params['activation']
    dropout_rate = params['dropout_rate']
    epochs = params['epochs']
    lam = params['lambda']
    batch_size = params['batch_size']
    
    checkpoints = keras.callbacks.ModelCheckpoint('{}{}/model_callback.h5'.format(PATH,NOW), monitor='val_loss', verbose=1, save_best_only=True, save_weights_only=False, mode='min')
    earlystopping = keras.callbacks.EarlyStopping(monitor='val_loss', min_delta = 0.01, patience=1, verbose=1, mode='min')
    logger = keras.callbacks.CSVLogger('{}{}/log.txt'.format(PATH,NOW), append=True)

    callbacks = [checkpoints, earlystopping, logger]
    
    if load_model:
        if train_logistic:
            model = keras.models.load_model('{}{}/model_callback.h5'.format(PATH,NOW), custom_objects={'binary_accuracy_V2':binary_accuracy_V2,'f1':f1})
        else:
            model = keras.models.load_model('{}{}/model_callback.h5'.format(PATH,NOW), custom_objects={'binary_accuracy_V2':binary_accuracy_V2, 'weighted_binary_crossentropy':weighted_binary_crossentropy, 'precision':precision, 'recall':recall,'f1':f1, 'f1_loss':f1_loss})
            model.compile(loss= 
                          weighted_binary_crossentropy,
    #                   f1_loss,
    #                   'binary_crossentropy',
                  optimizer = tf.keras.optimizers.Nadam(learning_rate=learning_rate),
                  metrics = [binary_accuracy_V2, precision, recall, f1])
    else:
        if train_logistic:
            model = logistic_model(num_layers, num_neurons, learning_rate, activation, dropout_rate, (batch_size, 4632), (batch_size, 610), lam)
        else:
            model = neural_network(num_layers, num_neurons, learning_rate, activation, dropout_rate, (batch_size, 4632), (batch_size, 610), lam)
    if test_mode:
        mod_hist = model.fit_generator(train_gen,steps_per_epoch=steps_per_epoch, #512
#                                    validation_data = val_gen, 
#                                    validation_steps = len(val_gen),
                                   verbose=1,  
                                   epochs = epochs + NUM_EPOCH_START, 
                                   use_multiprocessing = False, workers = 1, max_queue_size = 1, 
                                   callbacks = callbacks,
#                                   class_weight = class_weight, 
                                   shuffle=False,
                                  initial_epoch = NUM_EPOCH_START)
    else:
        mod_hist = model.fit_generator(train_gen,steps_per_epoch=steps_per_epoch, #512
                                       validation_data = val_gen, 
                                       validation_steps = len(val_gen),
                                       verbose=1,  
                                       epochs = epochs + NUM_EPOCH_START, 
                                       use_multiprocessing = False, workers = 1, max_queue_size = 1, 
                                       callbacks = callbacks,
    #                                   class_weight = class_weight, 
                                       shuffle=False,
                                      initial_epoch = NUM_EPOCH_START)
    return mod_hist, model
          
          
# '''
# Set parameters of interest
# '''

# learning_rate = 0.01
learning_rate = 0.008/((NUM_EPOCH_START+1)*6) # use decay, this is manually adjusted
num_layers = 2
num_neurons_1 = [3495]
# maybe remove batcnorm?
dropout = 0.05
num_epochs = 2
epochs=num_epochs
batch_size = 32
lam = .0025
steps_per_epoch = 16384
pw=4 # this is weight (higher = predict more ones in response variable)
exclude_cols_transformation='item_date.month.sin,item_date.month.cos,item_date.hour.sin,item_date.hour.cos'
use_batchnorm = False
test_mode = False
train_logistic = True
# comment out val_gen len(val_gen) in fit_generator also
# '''
# 
# '''


model_time_start = str(datetime.datetime.now())
now = str(datetime.datetime.now())
iteration_param_dict = {}
iteration_param_dict['learning_rate'] = learning_rate
iteration_param_dict['num_layers'] = num_layers
iteration_param_dict['num_neurons'] = num_neurons_1
iteration_param_dict['activation'] = 'relu'
iteration_param_dict['dropout_rate'] = dropout
iteration_param_dict['epochs'] = num_epochs
iteration_param_dict['lambda'] = lam
iteration_param_dict['batch_size'] = batch_size
print('########')
print(iteration_param_dict)
# loading model now
model_dicts = {}
model_dicts = initialize_keys(model_dicts,now)

exclude_cols_transformation='item_date.month.sin,item_date.month.cos,item_date.hour.sin,item_date.hour.cos'
data_dir = '/badvolume/home/ec2-user/cs230/scripts/matrix/final_may_6/hdf5/dev2_feature_selected_small/'
val_gen = None
if not test_mode:
    val_gen = DataGenerator(path=data_dir, cache='dev2_generator_small.sav', batch_size = 4096, shuffle=False)

model_dicts = {}
model_dicts = initialize_keys(model_dicts,now)

# for i in range(23):
# K.clear_session()
data_dir = '/badvolume/home/ec2-user/cs230/scripts/data/hdf5/train2_feature_selected'
train_gen = DataGenerator(path=data_dir, pca_file='/badvolume/home/ec2-user/cs230/scripts/data/eig.pickle', 
                                transformation_file='/badvolume/home/ec2-user/cs230/scripts/data/statistics/train/avg_stddev_featureselected.hdf5', 
                                num_pc=4632, 
                                num_processes=10, 
                                batches_per_epoch = steps_per_epoch, 
                                exclude_cols_transformation=exclude_cols_transformation)


# set state to start somewhere new
if load_model:
    train_gen.setState(num_epochs=NUM_EPOCH_START)
mod_hist, model = run_nn(train_gen, val_gen, iteration_param_dict, now)
class MyEncoder(json.JSONEncoder):
    # source: https://stackoverflow.com/questions/27050108/convert-numpy-type-to-python
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
print('saving models')
model.save('{}{}/model.h5'.format(PATH,NOW))

model_dicts = update_dicts(model_dicts, now, iteration_param_dict, mod_hist.history)
with open('{}{}/history.json'.format(PATH,NOW), 'w') as mdj:
    json.dump(model_dicts, mdj, cls = MyEncoder)
#     del train_gen
