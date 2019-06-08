# Table of contents
1. [Processing the Data Matrix](#processdatamatrix)

# Processing the Data Matrix<a name="processdatamatrix"></a>



## Getting data's statistics

We want to get the means and standard deviations of each feature so we can standardize the dataset via: (x-μ)/s
Additionally, we want to get the frequencies of the response variables being non-zeroes (i.e. for each response variable, what are the percentage of non-zero values). This will be useful for weighting our loss function later on.

To do this, we use the following script (the -x flag denotes which features we don't want to transform). In the output folder, two files: avg_stddev.hdf5 and freq_y.hdf5 will be generated.

<pre>python2 data_processing/compute_stats.py -i data/hdf5/train/ -o data/statistics/train/ -x patient_item_id,external_id,patient_id,clinical_item_id,encounter_id,item_date.month,item_date.month.sin,item_date.month.cos,item_date.hour,item_date.hour.sin,item_date.hour.cos</pre>


## Shuffling the data into batches
<pre>python2 data_processing/make_batches.py -s data/train_shuffling.pickle -i data/hdf5/train/ -o data/hdf5/train_shuffled/ -b 0 -e 100</pre>
