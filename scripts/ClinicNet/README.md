# Table of contents
1. [Data Preprocessing](#preprocessing)
2. [Processing the Data Matrix](#processdatamatrix)
3. [Model and Tuning](#model)
4. [Evaluation](#evaluation)
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

To do the conversion, run the following script where you specify the input data directory, output folder (which you should create beforehand with mkdir), the number of chunks to split the data into (this will be the number of HDF5 files we'll get), the clinical item IDs to retain for the post.1d response variables, the features that we want to exclude altogether (-e), and the features that we want to save in their raw form (-s). Since the data will be split into multiple chunks, we can leverage multiprocessing via -p.


<pre>python2 preprocessing/make_hdf5.py -i data/unprocessed/train -c data/columns.txt -o data/hdf5/train -n 360 -r data/response_vars.tsv -e item_date,analyze_date -s patient_id,patient_item_id,encounter_id,clinical_item_id -p 2</pre>

Running the above command will give you something like this: "Using 2 processes for processing 58290 files divided into 360 chunks". Once it's finished running, you'll see "FINISHED" printed out and you'll see 360 .h5 files in the output folder. In each HDF5 file, two data frames: data_x and data_y (for the feature matrix and response variables, respectively) are stored. The features specified via -s will be contained in the data frame: data_s.

IMPORTANT: The HDF5 files will store the data frames as float32 types. This means we can't have any non-numeric columns (in the example above, we removed the item_date and analyze_date columns because these columns store dates in string format). Use -e to remove non-numeric columns. Beware that large integers lose precision when casted to float32 -- therefore, large numbers (such as patient IDs) are best stored separately by specifying the -s option.

# Processing the Data Matrix<a name="processdatamatrix"></a>


## Shuffling the data into batches

We can kill two birds with one stone: Shuffling (randomly) the entire dataset and putting the shuffled data into equally sized batches. We have to run two scripts. The first does the batch assignments (e.g. below, we make batches of size 4096 using the entire dataset) and produces a pickle file as output. The second takes the pickle file (containing the batch assignments) and uses it write out the batches (each batch being one file) to a specified folder (which we should create via mkdir).
<pre>python2 data_processing/prep_batches.py -i data/hdf5/train/ -o data/train_shuffling.pickle -b 4096</pre>
<pre>python2 data_processing/make_batches.py -s data/train_shuffling.pickle -i data/hdf5/train/ -o data/hdf5/train_shuffled/ -b 0 -e 100</pre>
Note: The first script will print out info about the batches generated. Here was the output obtained when the command was run on the training set data and subsequently, on the dev set and test set data:
<ul>
  <li>Training set data: "Read 25606920 data rows in 360 files. Created 6252 batches of size 4096."</li>
  <li>Dev set data: "Read 5539705 data rows in 120 files. Created 1353 batches of size 4096"</li>
  <li>Test set data: "Read 5481460 data rows in 360 files. Created 1339 batches of size 4096"</li>
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
Running the script above tells us that 5214 features out of 24875 were removed, leaving 19661 features remaining. This script also outputs new statistics files (with the features removed) in the statistics directory for the data. (Note: When rerunning feature selection on the dev and test sets, be sure to use the same statistics directory specified for feature selection on the training set.)

## Adding item date timestamps

Now, we'll add item_date timestamps to our dataset (because by default, the date timestamps aren't preserved). You specify the input data directory and and patient_itemdate_mapping_file (HDF5 file specified via -d). We can leverage multiprocessing via -p. The patient_itemdate_mapping_file contains a data frame of patient items with columns being item_date (as nanoseconds since epoch) and patient_item_id. The item_date timestamps will be added to the data_s dataframe of the data.

<pre>python data_processing/add_dates.py -i data/hdf5/train_feature_selected/ -d ./queried/patientitemid_itemdate.hdf5</pre>

## Stratifying data by timestamp

To do time series validation, we need to stratify our dataset by time. The following commands will filter the existing training, validation, and test sets to consist of the following:
<ul>
  <li>Training set: Data before the year 2011</li>
  <li>Validation set: Data in the year 2011</li>
  <li>Test set: Data after the year 2011</li>
</ul>
<pre>
python data_processing/stratify_data_by_time.py -i data/hdf5/train_feature_selected/ -o data/hdf5/train_feature_selected_time_temp/ -l 0 -g 1293840000000000000
python data_processing/stratify_data_by_time.py -i data/hdf5/dev_feature_selected/ -o data/hdf5/dev_feature_selected_time_temp/ -l 1293840000000000000 -g 1325376000000000000
python data_processing/stratify_data_by_time.py -i data/hdf5/test_feature_selected/ -o data/hdf5/test_feature_selected_time_temp/ -l 1325376000000000000 -g 99900000000000000000000
</pre>
(Notes: Use mkdir to make the output directories, specified by -o, beforehand; use -p for multiprocessing)
The 1293840000000000000 timestamp corresponds to January 1 2011 whereas the 1325376000000000000 timestamp corresponds to January 1 2012. The -l and -g options represent the lower-bound and upper-bound timestamps, respectively, for selecting data to retain (use 0 for no lower bound and use a huge number for no upper bound).

Following timestamp stratification, it is necessary to recreate the batches. See the following example (for the training set):
<pre>
mkdir data/hdf5/train_feature_selected_time_temp/
python2 data_processing/prep_batches.py -i data/hdf5/train_feature_selected_time_temp/ -o data/train_time_shuffling.pickle -b 4096</pre>

Results for these timestamp-stratified train/dev/test batches:
<ul>
  <li>Training set data: "Read 8893911 data rows in 6252 files. Created 2172 batches of size 4096."</li>
  <li>Dev set data: "Read 1208680 data rows in 1353 files. Created 296 batches of size 4096"</li>
  <li>Test set data: "Read 2443646 data rows in 1339 files. Created 597 batches of size 4096"</li>
</ul>

And then, like before, we create the batches via something like (see following example for making 100 random batches from the training set):
<pre>
mkdir data/hdf5/train_feature_selected_time/
python2 data_processing/make_batches.py -s data/train_time_shuffling.pickle -i data/hdf5/train_feature_selected_time_temp/ -o data/hdf5/train_feature_selected_time/ -b 0 -e 100</pre>

We'll also rerun statistics on these ones (but we won't do redo feature selection for simplicity's sake):

<pre>python3 data_processing/compute_stats.py -p 24 -i data/hdf5/train_feature_selected_time/ -o data/statistics/train_time/ -x patient_item_id,external_id,patient_id,clinical_item_id,encounter_id,item_date.month,item_date.month.sin,item_date.month.cos,item_date.hour,item_date.hour.sin,item_date.hour.cos -t data/tmp -n 543
</pre>
(Note: 543 files is 25% of the training data files; we mkdir the directory train_time to store these new statistics files)


## Principal Component Analysis (PCA)

To run PCA, we read in a covariance matrix and get its eigenvalues & eigenvectors (stored in an output pickle file):
<pre>python3 utils/pca.py -i data/statistics/train/covar_featureselected.hdf5 -o data/eig.pickle</pre>
Following this, we can do the analysis and create scree plots via the notebook: <b>plotPCA.ipynb</b>

Here is some of the notebook's output:
<ul>
  <li>Number of PCs selected based on Kaiser's rule (eigenvalue > 1): 4632</li>
  <li>Variance explained by PC1: 3.6%; Variance explained by PC4632: 0.00509%</li>
  <li>Cumulative variance explained for PC4632: 82.2%</li>
</ul>

## Processing the Data Matrix for Order Set Prediction

Now, we focus on the task of processing the data matrix for predicting order set usage. The following script formats the data's response variable to be whether each order set was used 1 day after each given item. You specify the input data directory, output folder (which you should create beforehand with mkdir), patient_orderset_mapping_file (HDF5 file specified via -m), and patient_itemdate_mapping_file (HDF5 file specified via -d). We can leverage multiprocessing via -p. The patient_orderset_mapping_file contains a data frame of order set items with columns being patient_id, patient_item_id, external_id (the order set ID), and item_date (the order set item date as nanoseconds since epoch). The patient_itemdate_mapping_file contains a data frame of patient items with columns being item_date (as nanoseconds since epoch) and patient_item_id. Only the data rows that have at least one post-one-day order set usage are retained unless the flag -a is used in which case all data rows will be retained.

<pre>python data_processing/make_order_set_responses.py -i data/hdf5/train/ -o data/hdf5/train2_order_set/ -m ./queried/patient_item_id_to_order_set_ID_matches.hdf5 -d ./queried/patientitemid_itemdate.hdf5</pre>

The output of the script above tells us there are 610 order sets.

Afterwards, we just proceed like we did with the other task. We shuffle the data into batches first:
<pre>python2 data_processing/prep_batches.py -i data/hdf5/train2_order_set/ -o data/train2_order_set_shuffling.pickle -b 4096</pre>
When doing this for the train, dev, and test sets, we get:
<ul>
  <li>Training set data: "Read 16961751 data rows in 360 files. Created 4142 batches of size 4096."</li>
  <li>Dev set data: "Read 3671312 data rows in 360 files. Created 897 batches of size 4096"</li>
  <li>Test set data: "Read 3657826 data rows in 360 files. Created 894 batches of size 4096"</li>
</ul>
Then, like before, we do (e.g. for training set):
<pre>python2 data_processing/make_batches.py -s data/train2_order_set_shuffling.pickle -i data/hdf5/train2_order_set/ -o data/hdf5/train2_shuffled/ -b 0 -e 100</pre>

Finally, we perform feature selection as follows (example below for training set):
<pre>python3 data_processing/feature_selection.py -i data/hdf5/train2_shuffled/ -o data/hdf5/train2_feature_selected/ -s data/statistics/train/ -t 0.01 -r patient_item_id,external_id,patient_id,clinical_item_id,encounter_id,item_date,analyze_date,item_date.month,item_date.hour</pre>
(Note: We use the same statistics file as used for the previous task since this data is still a subset of the data used for the previous task, so we'll use the same averages, standard deviations, covariances, etc. computed previously)
(Note: The item_date timestamps will be added to the data_s dataframe of the data by these scripts)

## Timestamp-Stratifying the Data for Order Set Prediction

See the previous section on timestamp stratification. We can do the same for these data files which we use for the order set prediction task, ultimately resulting in the following data batches:

<ul>
  <li>Training set data: "Read 5435590 data rows in 4142 files. Created 1328 batches of size 4096."</li>
  <li>Dev set data: "Read 821521 data rows in 897 files. Created 201 batches of size 4096"</li>
  <li>Test set data: "Read 1699164 data rows in 894 files. Created 415 batches of size 4096"</li>
</ul>

We put these files in folder named train2_feature_selected_time, dev2_feature_selected_time, and test2_feature_selected_time.

## Summarizing Dataset Composition

To summarize information about ethnicity, sex, birth year, and number of patients from a given dataset, supply the path to the directory containing the dataset's HDF5 files in the following command (example shown for the time-stratified training set):

<pre>python utils/summarize.py -i data/hdf5/train_feature_selected_time/</pre>


# Model and tuning <a name="processdatamatrix"></a>

## Data generator
Located in clinicnet_model/utils/datagenerator.py. Shuffles files, then shuffles rows within each file, then loads in batches one by one. Used for training the network.

## Training and Tuning
We use run_clinicnet.py to train and tune our models. Here you can set parameters of interest for testing purposes, and a test_mode is available if trying to test without validating on the validation set. Learning rate is decreased manually if loss appears to stop decreasing. We use train_network.sh to continue training the network from callbacks saved after every 1 million rows of data.

## Files

### Time-Stratified

Time-Stratified Individual Item prediction task:
<ul>
  <li>Data sets (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/train_feature_selected_time/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/dev_feature_selected_time/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/test_feature_selected_time/</li>
  </ul>
  </li>
  
  <li>Statistics files (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/train_time/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/dev_time/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/test_time/avg_stddev.hdf5</li>
  </ul>
  </li>
  
  <li>Cached generators (dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/dev_time_generator.sav</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/test_time_generator.sav</li>
  </ul>
  </li>
</ul>

Time-Stratified Order Set prediction task:
<ul>
  <li>Data sets (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/train2_feature_selected_time/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/dev2_feature_selected_time/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/test2_feature_selected_time/</li>
  </ul>
  </li>
  
  <li>Statistics files (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/train2_time/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/dev_time/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/test_time/avg_stddev.hdf5</li>
  </ul>
  </li>
  
  <li>Class weights file (train): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/train2_time/freq_y.hdf5</li>
  </ul>
  </li>
  
  <li>Cached generators (dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/dev2_time_generator.sav</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/test2_time_generator.sav</li>
  </ul>
  </li>
</ul>

### Non-Time-Stratified

Time-Stratified Individual Item prediction task:
<ul>
  <li>Data sets (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/train_feature_selected/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/dev_feature_selected/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/test_feature_selected/</li>
  </ul>
  </li>
  
  <li>Statistics files (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/train/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/dev/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/test/avg_stddev.hdf5</li>
  </ul>
  </li>
  
  <li>Cached generators (dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/dev_generator.sav</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/test_generator.sav</li>
  </ul>
  </li>
</ul>

Time-Stratified Order Set prediction task:
<ul>
  <li>Data sets (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/train2_feature_selected/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/dev2_feature_selected/</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/hdf5/test2_feature_selected/</li>
  </ul>
  </li>
  
  <li>Statistics files (train, dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/train2/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/dev/avg_stddev.hdf5</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/test/avg_stddev.hdf5</li>
  </ul>
  </li>
  
  <li>Class weights file (train): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/data/statistics/train2/freq_y.hdf5</li>
  </ul>
  </li>
  
  <li>Cached generators (dev, test): </li>
  <li>
    <ul>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/dev2_generator.sav</li>
  <li>/badvolume/home/ec2-user/cs230/scripts/clinicnet_model/test2_generator.sav</li>
  </ul>
  </li>
</ul>

# Evaluation
* bootstrap.py outlines how we performed the bootstrapping at patient-level for our evaluation metrics.
