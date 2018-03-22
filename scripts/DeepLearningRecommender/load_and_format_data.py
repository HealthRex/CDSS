import sys
import os
import pandas as pd
import numpy as np
from random import shuffle
import h5py


def drop_unwanted_columns(data):
    '''
    Drops unwanted columns from a pandas dataframe
    Parameters:
        @data: (pandas dataframe) pandas df
    Returns:
        @data2: (pandas dataframe) pandas df with dropped columns
    '''

    data2 = data[data.columns.drop(list(data.filter(regex='post.2d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.4d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.7d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.14d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.30d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.90d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.180d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.365d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.730d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.1460d')))]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.post')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.min')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.max')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.median')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.mean')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.std')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.first')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.last')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.diff')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.slope')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.countInRange')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.proximate')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.firstTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.lastTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.proximateTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.2d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.4d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.14d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.90d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.180d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.365d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.730d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.1460d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('external_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.sin')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.cos')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.preTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('analyze_date')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('encounter_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('Birth.pre')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('Death.postTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.postTimeDays')]

    return data2



def replace_none_nan(frame):
    '''
    Replaces None/Nan with median for a column
    Parameters:
        @frame: (pandas dataframe)
    Returns:
        @frame_new = (pandas dataframe) with median value replacement
    
    '''
  
    frame_new = frame.replace(to_replace='None',value=np.nan)    

    for col in list(frame_new):
        if col not in ["patient_item_id", "patient_id", "clinical_item_id", "item_date","enounter_id","analyze_date"]:
            frame_new[col] = frame_new[col].replace(to_replace=np.nan,value = frame_new[col].median(),axis=1)
    
    return frame_new
    



def clean_raw_data(raw_data_dir,data_out_dir='/home/ec2-user/cs230/scripts/DeepLearning/RNN/data_final/',out_prefix='rnn_data_',out_suffix='.txt',file_prefix='final_data_dropcols_',file_suffix='.txt',nfiles=1):
    '''
    Cleans raw data from healthrex database pull
    
    Parameters:
        @raw_data_dir: (string) path to directory containing raw data files
        @data_out_dir: (string) path to directory for writing cleaned data
        @file_prefix: (string) prefix of raw data files
        @file_suffix: (string) suffix of raw data files
        @num_files: (int) how many files to load
    '''
    print ("BEGIN CLEAN DATA...")

    for n in range(10,nfiles):
        fpath = raw_data_dir + file_prefix + str(n) + file_suffix
        print "Cleaning %s..." % fpath
        opath = data_out_dir + out_prefix + str(n) + out_suffix
        df_total = pd.read_table(fpath,sep='\t',dtype=None,header=2)
        df_total = replace_none_nan(df_total)
        df_total.to_csv(opath,sep='\t',header=True,index=False)
    
    print ("CLEAN DATA COMPLETE")

    return


def zero_pad(splits,max_len):
    '''
    Zero pads a clinical item sequence to be of length equal to max_len.
    Parameters:
        @splits: (tuple of lists of pandas dataframes) tuple of form (train,dev,test) where 
                each obj in tuple is a list of pandas dataframes, where each pandas dataframe corresponds
                to all the clinical items for a single patient.
        @max_len: (int) maximum clinical item length
    Returns:
        @splits_zero_pad: (tuple of lists of pandas dataframes) tuple of zero-padded patient clinical items list
    '''

    (train,dev,test) = splits

    columns_to_drop = ["patient_item_id", "patient_id", "clinical_item_id", "item_date","encounter_id"]
    for i,d in enumerate(train):
        d = d[d.columns.drop(columns_to_drop)]
        train[i] = d.append(pd.DataFrame([[0]*d.shape[1]]*(max_len-d.shape[0]), columns=list(d)))
    for i,d in enumerate(dev):
        d = d[d.columns.drop(columns_to_drop)]
        dev[i] = d.append(pd.DataFrame([[0]*d.shape[1]]*(max_len-d.shape[0]), columns=list(d)))
    for i,d in enumerate(test):
        d = d[d.columns.drop(columns_to_drop)]
        test[i] = d.append(pd.DataFrame([[0]*d.shape[1]]*(max_len-d.shape[0]), columns=list(d)))

    splits_zero_pad = (train, dev, test)
    return splits_zero_pad


def select_patients(patient_ids,split_sizes):
    '''
    Splits the patients into train/dev/test.  
    Parameters:
        @patient_ids: (list) list of patient_ids in data
        @split_size_array: (tuple) tuple of (train,dev,test) denoting how many patients should 
                            go into each category.
    Returns:
        @train_patient_ids: (list) list of patients to go into training set
        @dev_patient_ids: (list) list of patients to go into dev set
        @test_patient_ids: (list) list of patients to go into test set
    '''
    
    (train_sz,dev_sz,test_sz) = split_sizes
    shuffle(patient_ids)
    train_patient_ids = patient_ids[0:train_sz]
    dev_patient_ids = patient_ids[train_sz:train_sz+dev_sz]
    test_patient_ids = patient_ids[train_sz+dev_sz:]

    return train_patient_ids,dev_patient_ids,test_patient_ids


def write_features_responses(df,name,outdir,iters,response_vars):
    '''
    Separates the data into feature and response variables.
    Generates x_train,x_dev,x_test,y_train,y_dev,y_test.
    
    Parameters:
        @df: (pandas dataframe) pandas dataframe to be written to file
        @name: (string) 'train', 'dev', or 'test'
        @outdir: (string) output directory
        @iters: (int) number to be used in outfile name 
        @response_vars: (list) list of response variables
    Returns:
        None
    '''

    df.sort_values(by='item_date',ascending=True,inplace=True)

    x_ = df.drop(response_vars,axis=1)
    y_ = df[response_vars]

    if name == 'train':
        x_.to_csv(outdir+'train_dir_date_v3/'+'x_train_%d.dat' % iters,sep='\t')
        y_.to_csv(outdir+'train_dir_date_v3/'+'y_train_%d.dat' % iters,sep='\t')

    elif name == 'dev':

        x_.to_csv(outdir+'dev_dir_date_v3/'+'x_dev_%d.dat' % iters,sep='\t')
        y_.to_csv(outdir+'dev_dir_date_v3/'+'y_dev_%d.dat' % iters,sep='\t')

    elif name == 'test':

        x_.to_csv(outdir+'test_dir_date_v3/'+'x_test_%d.dat' % iters,sep='\t')
        y_.to_csv(outdir+'test_dir_date_v3/'+'y_test_%d.dat' % iters,sep='\t')


    return



def variable_length_splits(all_data,all_patient_ids,id_splits,outdir,counter=(0,0,0)):
    '''
    Assigns patient data to either train,dev, or test split. Variable length
    because not yet zero-padded.
    Parameters:
        @pgs: (generator object) iterable pd groupby patient_id 
        @splits: (tuple) tuple of (train_ids,dev_ids,test_ids)
    Returns:
        @train: (list) list of pandas dataframes for patients in training set
        @dev: (list) list of pandas dataframes for patients in dev set
        @test: (list) list of pandas dataframes for patients in test set
    '''

    response_vars = open('/home/ec2-user/cs230/scripts/Response_3003_complete.txt','r').read().splitlines()

    (train_ids,dev_ids,test_ids) = id_splits
    train,dev,test = [],[],[]
    (train_iter, dev_iter, test_iter) = counter
    for p_id in all_patient_ids:
        p_df = all_data[all_data['encounter_id'] == p_id] 
        if p_id in train_ids:
            write_features_responses(p_df,'train',outdir,train_iter,response_vars)
            train_iter += 1
        elif p_id in dev_ids:
            write_features_responses(p_df,'dev',outdir,dev_iter,response_vars)
            dev_iter += 1
        elif p_id in test_ids:
            write_features_responses(p_df,'test',outdir,test_iter,response_vars)
            test_iter += 1
        else:
            print "UNMATCHED PATIENT ERROR: %d" %p_id

    return train,dev,test, (train_iter,dev_iter,test_iter)




def convert_to_tensor(frame_list):
    '''
    Converts a list pandas dataframes into a tensor.
    
    Parameters:
        @frame_list: (list of pandas dataframes) all patient data for a split
    Returns:
        @tensor: (tensor i.e numpy nd array) 
    '''

    tensor = []
    for frame in frame_list:
        tensor.append(frame.as_matrix())

    tensor = np.asarray(tensor)
    
    return tensor


def extract_features_responses(splits_padded,outdir):
    '''
    Separates the data into feature and response variables.
    Generates x_train,x_dev,x_test,y_train,y_dev,y_test.
    
    Parameters:
        @splits_padded: tuple of lists of pandas dataframes for train,dev,test sets.
    Returns:
        @splits_x: (tuple of tensors) (x_train,x_dev,x_test) 
        @splits_y: (tuple of tensors) (y_train,y_dev,y_test)
    '''

    response_vars = open('/home/ec2-user/cs230/scripts/matrix/response.txt','r').read().splitlines()

    (train,dev,test) = splits_padded
        
    x_train,x_dev,x_test = [],[],[]
    y_train,y_dev,y_test = [],[],[]

    train_count,dev_count,test_count = 0,0,0
    for name,split in zip(['train','dev','test'],[train,dev,test]):

        for patient in split:
            patient.drop(["patient_item_id", "patient_id", "clinical_item_id", "item_date","encounter_id"],axis=1,inplace=True)
            
            x_ = patient.drop(response_vars,axis=1)
            y_ = patient[response_vars]    

            if name == 'train':
                x_.to_csv(outdir+'/train_dir_v2/'+'x_train_%d.dat' % train_count,sep='\t')
                y_.to_csv(outdir+'/train_dir_v2/'+'y_train_%d.dat' % train_count,sep='\t')
                
                train_count += 1

                x_train.append(x_)
                y_train.append(y_)
   
            elif name == 'dev':

                x_.to_csv(outdir+'/dev_dir_v2/'+'x_dev_%d.dat' % dev_count,sep='\t')
                y_.to_csv(outdir+'/dev_dir_v2/'+'y_dev_%d.dat' % dev_count,sep='\t')            
        
                dev_count += 1

                x_dev.append(x_)
                y_dev.append(y_)

            elif name == 'test':
            
                x_.to_csv(outdir+'/test_dir_v2/'+'x_test_%d.dat' % test_count,sep='\t')
                y_.to_csv(outdir+'/test_dir_v2/'+'y_test_%d.dat' % test_count,sep='\t')

                test_count += 1

                x_test.append(x_)
                y_test.append(y_)

	return


def make_train_dev_test(data_dir,fname='rnn_data.txt',outdir='/home/ec2-user/cs230/scripts/DeepLearning/RNN/data/',train_percent=0.9,dev_percent=0.05):
    '''
    Generates train,dev,and test set for RNN model.  
    A single training example comprises all clinical item orders for a given patient. 
    Therefore the shape of a single example will be (# of clinical item orders, # of features).
    
    Parameters:
        @data_dir: (string) path to directory containing cleaned data
    Returns:
        @train: (tensor) tensor of shape (#train examples, #clinical item orders, #features)
        @dev: (tensor) tensor of shape (#dev examples, #clinical item orders, #features)
        @test: (tensor) tensor of shape (#test examples, #clinical item orders, #features)
    '''


    print ("BEGIN GENERATE TRAIN/DEV/TEST")   
    test_percent = 1 - train_percent - dev_percent
    all_data = pd.read_table(data_dir+fname,sep='\t',dtype=None,header=0)
 
   patient_groups = all_data.groupby(by='encounter_id')
    
    max_clinical_items = max([len(p[1]) for p in patient_groups])
    
    all_patient_ids = all_data['encounter_id'].unique().tolist()
    total_patients = len(all_patient_ids)

    train_num_patients = int(total_patients * train_percent)
    dev_num_patients = int(total_patients * dev_percent)
    test_num_patients = total_patients - train_num_patients - dev_num_patients

    print "TOTAL NUMBER OF Encounters: %d" % len(patient_groups)
    print "NUMBER OF TRAIN Encounters: %d" % train_num_patients
    print "NUMBER OF DEV Encounters: %d" % dev_num_patients
    print "NUMBER OF TEST Encounters: %d" % test_num_patients
    print "MAX CLINICAL ITEMS: %d" % max_clinical_items

    train_patient_ids,dev_patient_ids,test_patient_ids = select_patients(all_patient_ids,(train_num_patients,dev_num_patients,test_num_patients))
    train,dev,test = variable_length_splits(all_data,all_patient_ids,(train_patient_ids,dev_patient_ids,test_patient_ids),outdir)


    return



def make_train_dev_test_v2(data_dir,in_prefix='rnn_data_',outdir='/home/ec2-user/cs230/scripts/DeepLearning/RNN/data/',train_percent=0.9,dev_percent=0.05,nfiles=1):
    '''
    Generates train,dev,and test set for RNN model.  
    A single training example comprises all clinical item orders for a given patient. 
    Therefore the shape of a single example will be (# of clinical item orders, # of features).
    
    Parameters:
        @data_dir: (string) path to directory containing cleaned data
    Returns:
        @train: (tensor) tensor of shape (#train examples, #clinical item orders, #features)
        @dev: (tensor) tensor of shape (#dev examples, #clinical item orders, #features)
        @test: (tensor) tensor of shape (#test examples, #clinical item orders, #features)
    '''

    print ("BEGIN GENERATE TRAIN/DEV/TEST")
    test_percent = 1 - train_percent - dev_percent
    
    out_counter = (0,0,0)
    for i in range(nfiles):
        fname = in_prefix + str(i) + '.txt'
        all_data = pd.read_table(data_dir+fname,sep='\t',dtype=None,header=0)
        patient_groups = all_data.groupby(by='encounter_id')

        max_clinical_items = max([len(p[1]) for p in patient_groups])

        all_patient_ids = all_data['encounter_id'].unique().tolist()
        total_patients = len(all_patient_ids)

        train_num_patients = int(total_patients * train_percent)
        dev_num_patients = int(total_patients * dev_percent)
        test_num_patients = total_patients - train_num_patients - dev_num_patients

        print "TOTAL NUMBER OF Encounters: %d" % len(patient_groups)
        print "NUMBER OF TRAIN Encounters: %d" % train_num_patients
        print "NUMBER OF DEV Encounters: %d" % dev_num_patients
        print "NUMBER OF TEST Encounters: %d" % test_num_patients
        print "MAX CLINICAL ITEMS: %d" % max_clinical_items

        train_patient_ids,dev_patient_ids,test_patient_ids = select_patients(all_patient_ids,(train_num_patients,dev_num_patients,test_num_patients))
        train,dev,test,out_counter = variable_length_splits(all_data,all_patient_ids,(train_patient_ids,dev_patient_ids,test_patient_ids),outdir,counter=out_counter)


    return














