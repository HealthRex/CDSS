# hematology-recommender
Implementation of a hematology recommender system for reducing treatment delays by predicting common tests a specialist would need at the first consult to diagnose the patient.

### Important notation:
- t<sub>1</sub>: the time point where the patient is referred to the hematology specialist
- t<sub>2</sub>: the time point where the patient attends a specialist visit for the first time

### Data preparation: 
The script `data/define_cohort.sql` contains the SQL code for defining the cohort and extracting the data necessary for developing features. Each of the main tables have to be downloaded locally to be later processed in subsequent python scripts. The main tables are `baseCohort`, `demographicData`, `diagnosisT1`, `orderedProceduresT1`, `orderedMedsT1`, `labResultsT1`, `diagnosisT2`, `orderedProceduresT2`. Each table should be downloaded as a .csv file.

The dataset and platform to run the querys are located in the Google Cloud Platform. To gain access follow the tutorial on the lab's github https://github.com/HealthRex/CDSS/blob/master/scripts/DevWorkshop/ReadMe.GoogleCloud-BigQuery-VPC.txt

### Feature engineering and dataset division
The functions in the `data/organize_feats.py` module prepares the data for training, they are already imported into the train.py script so the train.py script can be used directly. Currently all scripts have the data paths directly written into them but can be modified for more general use by employing `argparse` or `.config` files.

- Main function: the `organize_feats()` function organizes the data from times t1 (`organize_t1_feats()`) and t2 (`organize_t2_labels()`) by creating features and targets. Then, the function splits both features and targets into training, validation and test splits (`split_cohort`).
- Feature engineering: medicine orders, diagnosis, lab and procedure orders, and lab results are all processed individually. The topn elements are selected and the counts are binarized and used as features, that is, for example for the procedure orders the final feature would be the presence or absence of the order of a given procedure for each patient before time t1. For each table the time before t1 varies and is specified during the cohort definition.
- Label definition: multilabel multiclass problem. Each of the selected topn features at time t2 that were ordered by the specialist and the system is aiming to recommend. Because more than one procedure can be ordered the labels are binary vectors with a 1 in each of the ordered procedures for each patient.
- Dataset division: temporal and patient-wise division of the data. Can be redefined, but 2019 is the test year and 2018 the validation year. The remaining years are used for training. Remaining question on if 2008 should be included due to not enough data entries.

### Training and evaluation
Training is yet to be defined (`train.py`), but as mentioned before the connection is already made with the feature organization and data split functions. A tree-based method can be used for creating a baseline algorithm as it is intrinsically multiclass. The multilabel aspect of the problem should be handled by using the-per class scores directly (not converting them into probabilities by employing an argmax function) and by ensuring the evaluation is setup for a multilabel prediction. A skeleton base function for evaluation has been created in `utils/eval_utils.py` and the connection has been made with the training script.

### Gold standard
The `get_gold_standard()` function in the `data/get_gold_standard.py` script calculates the topn ordered procedures at t2 by diagnosis. We selected the top5 diagnosis at t2 and researched using upToDate the most common orders for diagnosing each condition. These orders can be used as the gold standard for evaluation. However, they should still be compared to the upToDate research and evaluated for their recall compared to the expected output at t2.