# Table of contents
1. [Processing the Data Matrix](#processdatamatrix)

# Processing the Data Matrix<a name="processdatamatrix"></a>

## Shuffling the data into batches
<pre>python2 data_processing/make_batches.py -s data/train_shuffling.pickle -i data/train/ -o data/hdf5/train_shuffled/ -b 0 -e 100</pre>
