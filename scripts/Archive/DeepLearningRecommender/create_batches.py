import sys
import numpy as np
import pandas as pd
import os
import h5py
import argparse
import keras
import keras.backend as K
from keras.preprocessing.sequence import pad_sequences
import random
from random import shuffle

def extract_middle(nd,Tx):
	'''
	Rows are clinical items, columns are features
	'''

	(rows,cols) = nd.shape
	if rows < Tx: return nd

	leftover = Tx - rows
	left = int(leftover/2)
	right = rows - int(leftover/2)
	
	trim = nd[left:right,:]
	trim = trim[0:Tx,:]
	
	return trim



def create_batches(data_dir,outdir,split,batch_size,Tx,n_feats,n_y,start_batch,end_batch):
	'''
    Loads the next batch of sequence data and pads it for LSTM use.  
    V2 uses the 'window' files.
    
    Parameters: 
        @data_dir: (string) path to data directory
	@outdir: (string) path to output directory
        @split: (string) train/dev/test
        @batch_size: (int) number of files to load for batch
        @Tx: (int): maximum length of LSTM input
        @n_feats: (int) number of features
        @n_y: (int) number of output variables
    Returns:
        @x_batch_total: (nd array) shape (batch_size,Tx,n_feats)
        @y_batch_total: (nd array) shape (batch_size,Tx,n_y)
	'''
	
	random.seed(0)
 
	keep_cols = open('keep_col_names.txt','r').read().splitlines()
	
	fns = os.listdir(data_dir)   
	fns_clean = [fn for fn in fns if fn[0] == 'x']
	fns_clean.sort()	
	shuffle(fns_clean)	
	
	if end_batch == -1:
		end_batch = len(fns_clean)


	response_3003 = open('/home/ubuntu/cs230/RNN/data/Response_3003_complete.txt','r').read().splitlines()

	b_start = start_batch * batch_size
	b_end = b_start + batch_size

	for nb in range(start_batch,end_batch):
		x_batch_total = np.zeros((batch_size,Tx,n_feats))
		y_batch_total = np.zeros((batch_size,Tx,n_y))
    
		for i,x_fn in enumerate(fns_clean[b_start:b_end]):
			y_fn = 'y' + x_fn[1:]

			x_batch_i = pd.read_table(data_dir+x_fn,sep=',',dtype=None,header=0)
			x_batch_i = x_batch_i[keep_cols]
			
			y_batch_i = pd.read_table(data_dir+y_fn,sep=',',dtype=None,header=0,usecols=response_3003)
			try:
				x_batch_i.drop(['analyze_date','patient_item_id','patient_id','clinical_item_id','item_date','encounter_id'],axis=1,inplace = True)
			except:
				print ("Dropping fewer columns...")
			
			
			x_batch_i = x_batch_i.as_matrix()
			y_batch_i = y_batch_i.as_matrix()

			x_batch_i = extract_middle(x_batch_i,Tx)
			y_batch_i = extract_middle(y_batch_i,Tx)

			x_batch_i = x_batch_i.T
			y_batch_i = y_batch_i.T
			
			print(nb, x_batch_i.shape,y_batch_i.shape)


			x_batch_i_padded = pad_sequences(x_batch_i,maxlen=Tx,padding='post',value=-1.).T
			try:
				x_batch_i_padded = pad_sequences(x_batch_i,maxlen=Tx,padding='post',value=-1.).T
			except:
				print ("ERROR")
				print (x_fn)
				print('nrows: %d' % x_batch_i.shape[0])
				print('ncols: %d' % x_batch_i.shape[1])
				continue

			y_batch_i_padded = pad_sequences(y_batch_i,maxlen=Tx,padding='post',value=-1.).T
			y_batch_i_padded = np.sign(y_batch_i_padded)
			x_batch_total[i,:,:] = x_batch_i_padded
			y_batch_total[i,:,:] = y_batch_i_padded
    
		x_h5f = h5py.File(outdir+'%s_x_batch_%d.h5'%(split,nb),'w')
		y_h5f = h5py.File(outdir+'%s_y_batch_%d.h5'%(split,nb),'w')

		x_dset = x_h5f.create_dataset('%s_x_batch_%d'%(split,nb),data=x_batch_total)
		y_dset = y_h5f.create_dataset('%s_y_batch_%d'%(split,nb),data=y_batch_total)

		x_h5f.close()
		y_h5f.close()

		b_start += batch_size
		b_end += batch_size
	
	return


def main(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument('--data_dir',type=str,required=True)
	parser.add_argument('--out_dir',type=str,required=True)
	parser.add_argument('--batch_size',type=int,required=True)
	parser.add_argument('--split',type=str,required=True)	
	parser.add_argument('--Tx',type=int,required=True)
	parser.add_argument('--n_y',type=int,required=True)
	parser.add_argument('--n_feats',type=int,required=True)
	parser.add_argument('--start_batch',type=int,default=0)
	parser.add_argument('--end_batch',type=int,default=-1)

	args = parser.parse_args()
	
	create_batches(args.data_dir,args.out_dir,args.split,args.batch_size,args.Tx,args.n_feats,args.n_y,args.start_batch,args.end_batch)

	return



if __name__ == '__main__':
	main(sys.argv[1:])



