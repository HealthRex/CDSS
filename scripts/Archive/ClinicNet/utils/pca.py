# Performs principal components analysis
# Saves eigen values and eigen vectors to file

import pandas as pd
import numpy as np
import scipy.linalg as la
import tables
import os
import _pickle as cPickle # Must use python 3!!
import sys, getopt

# Convert covariance matrix to correlation matrix
# Since the correlation matrix is standardized,
# it's what we use since we're going to z-score standardize our data
# Argument: a is a pandas dataframe
def cov2corr(a):
	dd = np.sqrt(np.matrix(a).diagonal())
	a = ((np.matrix(a).T/dd).T)/dd
	return a

def doPCA(cov_mat):
	eig_vals, eig_vecs = la.eigh(cov_mat)
	eig_tuple = (eig_vals, eig_vecs)
	return eig_tuple

def main(argv):
	covar_file = ''
	output_file = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:")
	except getopt.GetoptError:
		print('pca.py -i <covar_file> -o <output_file> [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('pca.py -i <covar_file> -o <output_file> [-h]')
			print('')
			print('This script performs PCA given covariance matrix hdf5 file <covar_file> and outputs eigenvalues/eigenvectors in pickle output file: <output_file>.')
			sys.exit()
		elif opt == '-i':
			covar_file = arg
		elif opt == '-o':
			output_file = arg
	if len(argv) < 2 or covar_file == '' or output_file == '':
                print('feature_selection.py -i <covar_file> -o <output_file> [-h]')
                sys.exit(2)

	print("Reading in covariance matrix...")
	covar_matrix = cov2corr(pd.read_hdf(covar_file, 'covar'))
	print("Doing decomposition of correlation matrix...")
	eig_tuples = doPCA(covar_matrix) # Tuple of eigenvalues and eigenvectors
	cPickle.dump(eig_tuples, open(output_file, "wb"), protocol=4)

if __name__ == "__main__":
   main(sys.argv[1:])
 
