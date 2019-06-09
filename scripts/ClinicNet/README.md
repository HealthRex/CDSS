# Table of contents
1. [Processing the Data Matrix](#processdatamatrix)

# Processing the Data Matrix<a name="processdatamatrix"></a>



## Getting data's statistics

We want to get the means and standard deviations of each feature so we can standardize the dataset via: (x-μ)/s
Note that prior to calculating the means and standard deviations, the data will be log2(x+1) transformed.
Additionally, we want to get the frequencies of the response variables being non-zeroes (i.e. for each response variable, what are the percentage of non-zero values). This will be useful for weighting our loss function later on.

To do this, we use the following script (the -x flag denotes which features we don't want to transform). In the output folder (which we should create via mkdir), two files: <b>avg_stddev.hdf5</b> and <b>freq_y.hdf5</b> will be generated.

<pre>python2 data_processing/compute_stats.py -i data/hdf5/train/ -o data/statistics/train/ -x patient_item_id,external_id,patient_id,clinical_item_id,encounter_id,item_date.month,item_date.month.sin,item_date.month.cos,item_date.hour,item_date.hour.sin,item_date.hour.cos</pre>


## Shuffling the data into batches

We can kill two birds with one stone: Shuffling (randomly) the entire dataset and putting the shuffled data into equally sized batches. We have to run two scripts. The first does the batch assignments (e.g. below, we make batches of size 4096 using the entire dataset) and produces a pickle file as output. The second takes the pickle file (containing the batch assignments) and uses it write out the batches (each batch being one file) to a specified folder (which we should create via mkdir).
<pre>python2 data_processing/prep_batches.py -i data/hdf5/train/ -o data/train_shuffling.pickle -b 4096</pre>
<pre>python2 data_processing/make_batches.py -s data/train_shuffling.pickle -i data/hdf5/train/ -o data/hdf5/train_shuffled/ -b 0 -e 100</pre>
Note: The first script will print out info about the batches generated, like the following: "Read 25606920 data rows in 360 files. Created 6252 batches of size 4096."
Note: For the second script, we set the -b and -e options to indicate the beginning index and the end index of the batches we want to write out. In the example above, we write out batches 0 through 99. This is because doing the entire operation at once would consume too much memory so we need to split it into chunks.
