import pdb
import argparse
import sys
import os
import models.ml_models as cl_ml


sys.path.append(os.getcwd())
parser = argparse.ArgumentParser()  


# === Path to your train and test set. 
# Create a feature_matrix directory and copy your train and test set under feature_matrix folder.
parser.add_argument("--train_data_path", type=str, default='feature_matrix/train_set.csv')    
parser.add_argument("--test_data_path", type=str, default='feature_matrix/test_set.csv')    
parser.add_argument("--common_dict_path", type=str, default='Random Files/Stanford_Feature_Dictionary_Mapped.csv')    

# This code will save the trained models under "saved_classical_ml_models" folder
# Create a folder "saved_classical_ml_models"
parser.add_argument("--trained_rf_path", type=str, default= 'saved_classical_ml_models/rf_model.pkl')    
parser.add_argument("--trained_lr_path", type=str, default= 'saved_classical_ml_models/lr_model.pkl')    
parser.add_argument("--trained_xgb_path", type=str, default= 'saved_classical_ml_models/xgb_model.pkl')    

# ml_model argument help you choose what model to use
# rf is random forest, lr is logistic regression, and xgb is xgboost
parser.add_argument("--ml_model", type=str, default='none', choices=['rf', 'lr', 'xgb']) 

# test_models: if 1 means load the models and only do testing. 
parser.add_argument("--test_models", type=int, default=0, choices=[0, 1])    

# plots: for visualization
parser.add_argument("--plots", type=int, default=0, choices=[0, 1])    

# table_to_exclude: help you exclide data streams. For example, if table_to_exclude=='note_nlp', the note features will not be used.
# parser.add_argument("--table_to_exclude", type=str, default='note_nlp', choices=['diagnosis', 'drug', 'procedure', 'note_nlp'])    

# Threshold to use for deviding samples to retention vs attrition. Default is 180, meaning that treatment duration less than 180 days will be labeled with 1 and otherwise 0
parser.add_argument("--retention_cut_off", type=int, default=180)    

# min_treatment_duration of 2 means only include encounters with treatment duration more than equal to 2 
parser.add_argument("--min_treatment_duration", type=int, default=2)    

parser.add_argument("--external_testing", type=str, default= '', choices=['', '_external_testing'])    


# A list of meta-data features to be excluded.
# List variables that are not predictors or targets here.
# These variables will be removed from the feature matrix 
non_feature_list = ['person_id', 'drug_exposure_start_DATE', 'TreatmentDuration', 'outcome']

# We manually browsed our feature set and decided to exclude the following features
excluding_features = ['2514413', '42627954', '2514404', '2514405', '2514403', '42536500', '2108209', '2514407', '2514414', '2314291', 
'2514408', '4304341', '2514406', '4019497', '42628094', '2314216', '4078224', '4056973', '2514409', '2314217', '2314208', '2314213',
'4322380', '2108115', '2108190', '2314264', '2110766', '4213288', '2314262', '2314319', '2314284']
# Hospital discharge day management; 30 minutes or less
# Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An 
# Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of 
# Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination
# Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination 
# Insertion of catheter into peripheral vein
# Insertion of peripherally inserted central venous catheter (PICC), without subcutaneous port or pump, without imaging guidance; age 5 years or older
# Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Medical decision making that is straightforward or o
# Hospital discharge day management; more than 30 minutes
# Therapeutic procedure(s), group (2 or more individuals)
# Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of moder

demog_features = ['age_from_exposure_start_date','gender_8532', 'gender_8507'
,'race_2000039212', 'race_8515', 'race_2000039205', 'race_8527'
, 'race_2000039200', 'race_2000039207', 'race_8516', 'race_8657'
, 'race_8557', 'race_2000039206', 'race_2000039211', 'race_2000039201']
args = parser.parse_args()


if  args.ml_model == 'rf':
    print('Starting to train a random forest model using:\n')
    cl_ml.random_forest_model(args.train_data_path
                            , args.test_data_path
                            , args.common_dict_path
                            , args.retention_cut_off
                            , non_feature_list
                            , demog_features
                            , excluding_features
                            , args.min_treatment_duration
                            )

elif  args.ml_model == 'lr':
    print('Starting to train a logistic regression model using:\n')
    cl_ml.logistic_regression_model(args.train_data_path
                            ,args.test_data_path
                            , args.common_dict_path
                            , args.retention_cut_off
                            , non_feature_list
                            , demog_features
                            , excluding_features
                            , args.min_treatment_duration
                            )

elif  args.ml_model == 'xgb':
    print('Starting to train a logistic regression model using:\n')
    cl_ml.xgboost_model(args.train_data_path
                            ,args.test_data_path
                            , args.common_dict_path
                            , args.retention_cut_off
                            , non_feature_list
                            , demog_features
                            , excluding_features
                            , args.min_treatment_duration
                            )    
else:
    print('No ML model has been selected ... ')


if args.test_models == 1:
    cl_ml.test_with_imb(args.trained_rf_path
                        , args.trained_lr_path
                        , args.trained_xgb_path
                        , args.test_data_path
                        , args.common_dict_path
                        , args.retention_cut_off
                        , non_feature_list
                        , demog_features
                        , excluding_features
                        , args.min_treatment_duration
                        , args.external_testing
                        )


if args.plots == 1:
    cl_ml.plots(args.trained_rf_path
                        , args.trained_lr_path
                        , args.trained_xgb_path
                        , args.test_data_path
                        , args.common_dict_path
                        , args.retention_cut_off
                        , non_feature_list
                        , demog_features
                        , excluding_features
                        , args.min_treatment_duration
                        )


