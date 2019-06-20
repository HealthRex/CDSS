# adapted from https://stanford.edu/~shervine/blog/keras-how-to-generate-data-on-the-fly
import os
import math
import numpy as np
import tensorflow as tf
import pandas as pd

class DataGenerator(tf.keras.utils.Sequence):
    'Generates data for Keras'
    def __init__(self, path, batch_size=32, shuffle=True):
        'Initialization path = path to data directory of interest (train, val, or test)'

        self.path = path
        self.files = np.array(os.listdir(path))
        self.num_files = self.files.shape[0]
#         self.input_shape = self.get_input_shape()
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.idx2file = None
        self.idx2batch = None
        self.hdf_conns, self.len = self.setup_HDF5(self.files, self.batch_size)
        self.on_epoch_end()
        self.curr_file = self.files[0]
      

        
    def __len__(self):
        'Denotes the number of batches to go through per epoch'
        return self.len
#     int(np.floor(len(self.list_IDs) / self.batch_size))
    
    def setup_HDF5(self, files, batch_size):
        num_iters = 0
        batch_size = 32
        hdf_conns = {}
        for f in files:
        #hdf=pd.HDFStore(f)
        #data_x=hdf.select('data_x')
        #data_y=hdf.select('data_y')
            hdf_conns[f] = pd.HDFStore(self.path + "/" + f, mode='r')
            nrows = hdf_conns[f].get_storer('data_x').shape[0]
            num_batches = int(np.floor((nrows) / batch_size))
            num_iters += num_batches
        return hdf_conns, num_iters

    
#     def file_2_batches(self):
#         # pick a file and determine input shape
#         file = self.files[0]
#         npz = np.load(os.path.join(self.path, file))
#         x = npz['x']
#         return x.shape

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indexes of the batch
        # can do preprocessing here if interested
        file = self.idx2file[index]
        batch_idxs = self.idx2batch[index]
        X = pd.read_hdf(self.hdf_conns[file], 'data_x', mode='r').values
        y = pd.read_hdf(self.hdf_conns[file], 'data_y', mode='r').values

        # Find list of IDs
#         list_IDs_temp = [self.list_IDs[k] for k in indexes]

#         # Generate data
#         X, y = self.__data_generation(list_IDs_temp)
        X = X[batch_idxs, 5:]
        y = y[batch_idxs,:]
        return X, y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
#         self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle == True:
            np.random.shuffle(self.files)
            self.setup_batches()
    
    def setup_batches(self):
        '''
        setup batches to be used for the data generation pipeline
        '''
        idx = 0 
        self.idx2file = {} #reset the dictionaries
        self.idx2batch = {}
        for f in self.files:
            nrows = self.hdf_conns[f].get_storer('data_x').shape[0]
            num_batches = int(np.floor((nrows) / self.batch_size))
            indices = np.arange(nrows)
            if self.shuffle:
#             if shuffle:
                np.random.shuffle(indices)
            num_rows_remaining = int(nrows % self.batch_size)
            padding = int(self.batch_size - num_rows_remaining) # The "padding" to add to make divisible by batch_size
            batches = np.array_split(np.concatenate((indices, np.repeat(0,padding))), num_batches+1) # Do batch assignments
            batches = batches[:num_batches]
            self.idx2batch.update(dict(zip(range(idx, idx+num_batches), batches)))
            self.idx2file.update(dict.fromkeys(range(idx, idx+num_batches), f))
            idx += num_batches
    
    
#     def __data_generation(self, list_IDs_temp):
#         'Generates data containing batch_size samples' # X : (n_samples, *dim, n_channels)
#         # Initialization
#         X = np.empty((self.batch_size, *self.dim, self.n_channels))
#         y = np.empty((self.batch_size), dtype=int)

#         # Generate data
#         for i, ID in enumerate(list_IDs_temp):
#             # Store sample
#             X[i,] = np.load('data/' + ID + '.npy')
#             # can do data preprocessing here
#             # Store class
#             y[i] = self.labels[ID]

#         return X, keras.utils.to_categorical(y, num_classes=self.n_classes)
