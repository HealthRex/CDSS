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


# A list of meta-data features to be excluded.
# List variables that are not predictors or targets here.
# These variables will be removed from the feature matrix 
non_feature_list = ['person_id', 'drug_exposure_start_DATE', 'TreatmentDuration', 'outcome']

args = parser.parse_args()


if  args.ml_model == 'rf':
    print('Starting to train a random forest model using:\n')
    cl_ml.random_forest_model(args.train_data_path
                            , args.test_data_path
                            # , args.table_to_exclude
                            , non_feature_list
                            )

elif  args.ml_model == 'lr':
    print('Starting to train a logistic regression model using:\n')
    cl_ml.logistic_regression_model(args.train_data_path
                            ,args.test_data_path
                            # , args.table_to_exclude
                            , non_feature_list
                            )

elif  args.ml_model == 'xgb':
    print('Starting to train a logistic regression model using:\n')
    cl_ml.xgboost_model(args.train_data_path
                            ,args.test_data_path
                            # , args.table_to_exclude
                            , non_feature_list
                            )    
else:
    print('No ML model has been selected ... ')


if args.test_models == 1:
    cl_ml.test_with_imb(args.trained_rf_path
                        , args.trained_lr_path
                        , args.trained_xgb_path
                        , args.test_data_path
                        # , args.table_to_exclude
                        , non_feature_list
                        )


if args.plots == 1:
    cl_ml.plots(args.trained_rf_path
                        , args.trained_lr_path
                        , args.trained_xgb_path
                        , args.test_data_path
                        # , args.table_to_exclude
                        , non_feature_list
                        )


