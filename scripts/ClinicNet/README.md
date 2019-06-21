# Table of contents
1. [Data Preprocessing](#preprocessing)
2. [Processing the Data Matrix](#processdatamatrix)
3. [Model and Tuning](#model)
# Data Preprocessing<a name="preprocessing"></a>

## Splitting Data into Train/Dev/Test

Now we have our dataset in one folder; all files are .txt.gz files containing tab-delimited plaintext data. Each data file should be a patient encounter with the encounter ID followed by .txt or .txt.gz in the filename. Also, in that same folder, there should be a columns.txt file specifying column names for all the fields in the data files. (Note: The fields, patient_id and encounter_id, must be present as columns in order for us to proceed).

To split our data set into train/dev/test on the basis of patients (not encounters!) so that data from any single patient won't spill over across the train/dev/test sets, we run the following script (note: -g specifies our files are gzip compressed files):

<pre>preprocessing/data_split.sh -g ./data/unprocessed/ 70 15 15</pre>

This will create a 70/15/15 split for train/dev/test sets. You'll also get some summary statistics such as: 
<ul><li>Number of patients: 57624 (total), 40336 (train), 8644 (dev), 8644 (test)</li>
  <li>Number of encounters: 83226 (total), 58290 (train), 12401 (dev), 12535 (test)</li></ul>

## Putting the data into HDF5 files

For all the data files (that are tab-delimited in plaintext format) in a folder, we'll convert them to (partially compressed) HDF5 files so they can efficiently be loaded into python pandas data frames later on. From here on out, we'll only load data via HDF5 files.

To do the conversion, run the following script where you specify the input data directory, output folder (which you should create beforehand with mkdir), the number of chunks to split the data into (this will be the number of HDF5 files we'll get), the clinical item IDs to retain for the post.1d response variables, and the features that we want to exclude altogether. Since the data will be split into multiple chunks, we can leverage multiprocessing via -p.


<pre>python2 preprocessing/make_hdf5.py -i data/unprocessed/train -c data/columns.txt -o data/hdf5/train -n 360 -r data/response_vars.tsv -e item_date,analyze_date -p 2</pre>

Running the above command will give you something like this: "Using 2 processes for processing 58290 files divided into 360 chunks". Once it's finished running, you'll see "FINISHED" printed out and you'll see 360 .h5 files in the output folder. In each HDF5 file, two data frames: data_x and data_y (for the feature matrix and response variables, respectively) are stored.

IMPORTANT: The HDF5 files will store the data frames as float32 types. This means we can't have any non-numeric columns (in the example above, we removed the item_date and analyze_date columns because these columns store dates in string format). Use -e to remove non-numeric columns.

# Processing the Data Matrix<a name="processdatamatrix"></a>


## Shuffling the data into batches

We can kill two birds with one stone: Shuffling (randomly) the entire dataset and putting the shuffled data into equally sized batches. We have to run two scripts. The first does the batch assignments (e.g. below, we make batches of size 4096 using the entire dataset) and produces a pickle file as output. The second takes the pickle file (containing the batch assignments) and uses it write out the batches (each batch being one file) to a specified folder (which we should create via mkdir).
<pre>python2 data_processing/prep_batches.py -i data/hdf5/train/ -o data/train_shuffling.pickle -b 4096</pre>
<pre>python2 data_processing/make_batches.py -s data/train_shuffling.pickle -i data/hdf5/train/ -o data/hdf5/train_shuffled/ -b 0 -e 100</pre>
Note: The first script will print out info about the batches generated. Here was the output obtained when the command was run on the training set data and subsequently, on the dev set data:
<ul>
  <li>Training set data: "Read 25606920 data rows in 360 files. Created 6252 batches of size 4096."</li>
  <li>Dev set data: "Read 5539705 data rows in 120 files. Created 1353 batches of size 4096"</li>
</ul>

Note: For the second script, we set the -b and -e options to indicate the beginning index and the end index of the batches we want to write out. In the example above, we write out batches 0 through 99. This is because doing the entire operation at once would consume too much memory so we need to split it into chunks.

## Getting data's statistics

We want to get the means and standard deviations of each feature so we can standardize the dataset via: (x-μ)/s
Note that prior to calculating the means and standard deviations, the data will be log2(x+1) transformed.
Additionally, we want to get the frequencies of the response variables being non-zeroes (i.e. for each response variable, what are the percentage of non-zero values). This will be useful for weighting our loss function later on. Finally, we want to build a covariance matrix for principal components analysis (PCA).

To do this, we use the following script (the -x flag denotes which features we don't want to transform and we use -n to specify we'll only going to use 626 files, which is just 10% of the 6252 training data files, for average and covariance computation; we also specify data/tmp as our tmp directory that the script utilizes for caching and we specify 24 processors). In the output folder (which we should create via mkdir), two files: <b>avg_stddev.hdf5</b> and <b>freq_y.hdf5</b> will be generated.

<pre>python3 data_processing/compute_stats.py -p 24 -i data/hdf5/train_shuffled/ -o data/statistics/train/ -x patient_item_id,external_id,patient_id,clinical_item_id,encounter_id,item_date.month,item_date.month.sin,item_date.month.cos,item_date.hour,item_date.hour.sin,item_date.hour.cos -t data/tmp -n 626</pre>

## Feature selection

To remove very low variance features, run the following script where you specify the directory of the data you want to remove features from, the output directory (which you should create with mkdir beforehand), and the statistics directory corresponding to the statistics for the data. Below, we specify a standard deviation threshold of 0.01 (such that all features with a standard deviation below 0.01 will be removed) and we also specify a list of features we want to remove anyway.
<pre>python3 data_processing/feature_selection.py -i data/hdf5/train_shuffled/ -o data/hdf5/train_feature_selected/ -s data/statistics/train/ -t 0.01 -r patient_item_id,external_id,patient_id,clinical_item_id,encounter_id,item_date,analyze_date,item_date.month,item_date.hour</pre>
Running the script above tells us that 5214 features out of 24875 were removed, leaving 19661 features remaining. This script also outputs new statistics files (with the features removed) in the statistis directory for the data.

## Principal Component Analysis (PCA)

To run PCA, we read in a covariance matrix and get its eigenvalues & eigenvectors (stored in an output pickle file):
<pre>python3 utils/pca.py -i data/statistics/train/covar_featureselected.hdf5 -o data/eig.pickle</pre>
Following this, we can do the analysis and create scree plots via the notebook: <b>plotPCA.ipynb</b>

# Model and tuning <a name="processdatamatrix"></a>

## Data generator
Located in utils/datagenerator.py. Shuffles files, then shuffles rows within each file, then loads in batches one by one. Used for training the network.

## 


