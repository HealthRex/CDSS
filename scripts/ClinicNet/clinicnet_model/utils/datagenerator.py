# adapted from https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly
import os
import math
import numpy as np
import tensorflow as tf
import pandas as pd
import tables
import multiprocessing
from collections import OrderedDict
from itertools import repeat
import gc
import _pickle as cPickle # Must use python 3!!
from sklearn.externals import joblib


global transformation
transformation = lambda x: np.log2(x+1)


def read_data_file(f):
    'Reading in the feature matrix from an HDF5 data file'
    filename = f[0] # Name of file containing the data
    path = f[1] # Path to file
    avg_sd = f[2] # Averages and standard deviations computed for the data
    matrix_w = f[3] # PCA projection matrix
    exclude_cols_transformation = f[4] # List of features that we shouldn't log-transform
    # Read in the data
    data_x = pd.read_hdf(path + "/" + filename, 'data_x', mode='r')
    data_x = data_x.fillna(0)
    # Transform and standardize the data if necessary:
    if not (avg_sd is None):
        features = data_x.columns.intersection(list(avg_sd[0].keys()))
        data_x = data_x[features]
        avg = avg_sd[0][features]
        sd = avg_sd[1][features]
        assert data_x.shape[1] == len(avg)
        cols_to_transform = data_x.columns
        if not (exclude_cols_transformation is None):
            cols_to_transform = data_x.columns.difference(exclude_cols_transformation)
        data_x[cols_to_transform] = transformation(data_x[cols_to_transform])
        sd = sd.clip(lower=0.01) # Prevent divide-by-zero error
        data_x = (data_x - avg) / sd
    if not (matrix_w is None):
        data_x = data_x.dot(matrix_w) # PCA dimensionality reduction
    #print("done with " + filename)
    return((filename, data_x))

class DataGenerator(tf.keras.utils.Sequence):
    'Generates data for Keras'

    def __init__(self, path, batch_size=32, shuffle=True, transformation_file=None, pca_file=None, num_pc=None, num_processes=1, num_files_cache=None, exclude_cols_transformation=None, batches_per_epoch=None, cache=None, seed=1):
        'Initialization path = path to data directory of interest (train, val, or test)'
        self.path = path # Path to data directory
        self.files = np.array(os.listdir(path)) # List of files in data directory
        self.batch_size = batch_size
        self.shuffle = shuffle # Should we shuffle the data after we go through the entire dataset
        self.len = self.setup_HDF5(self.files, self.batch_size) # Figure out how many batches our dataset contains
        self.idx2file = None # Dict mapping from batch number to file name
        self.idx2batch = None # Dict mapping from batch number to the row indices of the data file for that batch
        self.matrix_w = None # PCA projection matrix
        self.avg_sd = None
        self.batches_per_epoch = batches_per_epoch
        self.counter = -1 # The batch number for the batch that we've just retrieved
        self.initial_seed = seed # Initialize random seed for shuffling
        self.seed = seed # Current seed value
        if exclude_cols_transformation: # List of features that we shouldn't log-transform (e.g. those that can have negative values)
            self.exclude_cols_transformation = exclude_cols_transformation.split(',')
        else:
            self.exclude_cols_transformation = []
        self.num_processes = num_processes # For processing data files in parallel
        self.num_files_cache = num_files_cache # How many data files to store in cache at one time
        if num_files_cache is None:
            self.num_files_cache = self.num_processes
        if self.num_files_cache > len(self.files):
            self.num_files_cache = len(self.files)
        self.cache = {} # For caching data as it is being generated
        if not (cache is None): # If we already have stuff precached
            self.cache = joblib.load(cache)
        if not (pca_file is None): # Read in eigenvectors/eigenvalues to make projection matrix
            eigs = cPickle.load(open(pca_file, "rb"))
            eig_vals = eigs[0]
            eig_vecs = eigs[1]
            eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
            eig_pairs.sort() # Sort the (eigenvalue, eigenvector) tuples
            eig_pairs.reverse() # Make the sorting from high to low
            matrix_w = np.hstack([eig_pairs[i][1].reshape(len(eig_pairs),1) for i in range(num_pc)])
            matrix_w = np.matrix(matrix_w)
            # alternately, the following works (if we generated our eigenvectors/eigenvalues via eigh):
            ## u = eigs[1]
            ## U = u.T[::-1]
            ## matrix_w = U[:2].T
            self.matrix_w = matrix_w
        if not (transformation_file is None): # Read in avg and sd
            avg = pd.read_hdf(transformation_file, 'avg')
            std_dev = pd.read_hdf(transformation_file, 'sd')
            self.avg_sd = (avg, std_dev)
        self.setup_batches(False)
        self.on_epoch_end()

    # Returns number of mini-epochs
    def __len__(self):
        'Denotes the number of batches to go through per mini-epoch'
        if self.batches_per_epoch:
            return self.batches_per_epoch
        return self.len # If batches_per_epoch isn't specified, we just have epochs instead of mini-epochs
    
    def getState(self):
        '''
        Gets info: (initial random seed, number of batches read, number of mini-epochs elapsed)
        that we need for resuming data generation
        '''
        return (self.initial_seed, self.counter+1, (self.counter+1)/(self.batches_per_epoch))
    
    def setState(self, num_batches=None, num_epochs=None): # Must be called immediately after object is initialized
        'Resume data generation starting from number of batches read of number of mini-epochs elapsed'
        #print("Setting state")
        if not num_epochs is None:
            num_batches = num_epochs*self.batches_per_epoch
        for i in range(num_batches):
            self.__getitem__(0, proxy=True)
    
    def setup_HDF5(self, files, batch_size):
        'For figuring out how many batches our dataset contains'
        num_iters = 0
        hdf_conns = {}
        for f in files:
            h5file = tables.open_file(self.path + "/" + f, mode="r")
            nrows = len(h5file.root.data_x.axis1)
            num_batches = int(np.ceil((nrows) / batch_size))
            num_iters += num_batches
            h5file.close()
        print("DataGenerator: Setting up {} files in {} batches".format(len(files), num_iters))
        return num_iters

    def __getitem__(self, index, proxy=False, read_saved_features=False):
        'Generate one batch of data'
        self.counter += 1
        if self.counter == len(self.idx2file): # If we've gone through all the data
            self.counter = 0 # Reset the batch number
            if self.shuffle == True:
                self.setup_batches() # Reshuffle everything if necessary
        index = self.counter
        
        if proxy: # Proxy means we 'pretend' to get the batch (no data will be returned if proxy is True)
            #print("PROXY BATCH: " + str(index))
            return None
        
        #print("GETTING BATCH: " + str(index))
        f = self.idx2file[index] # This is the file for our current batch
        if f in self.cache: # See if the file has already been loaded into the cache
            #print("READING FROM CACHE: " + f)
            data_x = self.cache[f][0]
            data_y = self.cache[f][1]
            data_s = None
            if read_saved_features:
                data_s = self.cache[f][2]
        else: # If file isn't in the cache, we'll load it here
            #print("READING FILE: " + f)
            del self.cache
            self.cache = {} # Once we come across a file that isn't cached, we know it's time to cache a new set of files!
            pool = multiprocessing.Pool(self.num_processes)
            files_list_all = list(OrderedDict.fromkeys([ v for k, v in self.idx2file.items() if k >= index ]))[0:self.num_files_cache] # Here's our new list of files to cache
            if self.num_files_cache > 100:
                # We partition our new list of files into chunks if we have more than 100 files to cache
                # Otherwise, pool.map runs into problems when trying to return a huge amount of data at once
                files_list_all = np.array_split(files_list_all, self.num_files_cache / 100)
            else:
                files_list_all = np.array_split(files_list_all, 1)
            for files_list in files_list_all:
                #print("NEW FILE LIST")
                datas = pool.map(read_data_file, zip(files_list,repeat(self.path), repeat(self.avg_sd), repeat(self.matrix_w), repeat(self.exclude_cols_transformation))) # Read in data from list of files
                for data in datas: # Go through (and cache) all the data we read in from list of files (each iteration of this loop is the data returned from a single file)
                    fname = data[0]
                    data_x = data[1]
                    data_x = data_x.astype(np.float32)
                    data_x = data_x.values
                    data_y = pd.read_hdf(self.path + "/" + fname, 'data_y', mode='r').values
                    if read_saved_features: # Should we read in features that were saved in their raw form?
                        data_s = pd.read_hdf(self.path + "/" + fname, 'data_s', mode='r').values
                        self.cache[fname] = (data_x, data_y, data_s)
                    else:
                        self.cache[fname] = (data_x, data_y)
                    #print("STORING FILE: " + fname)
            # Get the data for the file for the current batch:
            data_x = self.cache[f][0]
            data_y = self.cache[f][1]
            if read_saved_features:
                data_s = self.cache[f][2]
            else:
                data_s = None

        # Get the relevant parts of the data file for the current batch
        batch_idxs = self.idx2batch[index]
        data_x = data_x[batch_idxs,:]
        data_y = np.clip(data_y[batch_idxs,:],0,1) # Make the response values binary
        gc.collect()
        if read_saved_features:
            return data_x, data_y, data_s
        return data_x, data_y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        print('miniepoch_end: {} out of {} batches done'.format(self.counter+1, len(self.idx2file)))
    
    def setup_batches(self, reset_cache=True):
        '''
        Setup batches to be used for the data generation pipeline
        Prepares the idx2batch and idx2file dicts that map batch number to the relevant data
        '''
        self.seed += 1
        if self.shuffle == True:
            np.random.RandomState(seed=self.seed).shuffle(self.files)
        if reset_cache:
            del self.cache
            self.cache = {} # Reset the cache
        idx = 0 
        self.idx2file = {} #reset the dictionaries
        self.idx2batch = {}
        for f in self.files:
            h5file = tables.open_file(self.path + "/" + f, mode="r")
            nrows = len(h5file.root.data_x.axis1)
            num_batches = int(np.ceil((nrows) / self.batch_size))
            indices = np.arange(nrows)
            if self.shuffle:
                np.random.RandomState(seed=(self.seed+idx)).shuffle(indices)
            num_rows_remaining = int(nrows % self.batch_size)
            padding = int(self.batch_size - num_rows_remaining) # The "padding" to add to make divisible by batch_size
            if num_rows_remaining > 0:
                batches = np.array_split(np.concatenate((indices, np.repeat(-1,padding))), num_batches) # Do batch assignments
                batches = [i[i != -1] for i in batches]
            else:
                batches = np.array_split(indices, num_batches)
            self.idx2batch.update(dict(zip(range(idx, idx+num_batches), batches)))
            self.idx2file.update(dict.fromkeys(range(idx, idx+num_batches), f))
            h5file.close()
            idx += num_batches
            
