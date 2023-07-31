import pdb
import argparse
import sys
import os
import models.ml_models as cl_ml


sys.path.append(os.getcwd())
parser = argparse.ArgumentParser()  


# === train, validation and test stationary data
parser.add_argument("--train_data_path", type=str, default='feature_matrix/train_set.csv')    
parser.add_argument("--test_data_path", type=str, default='feature_matrix/test_set.csv')    


parser.add_argument("--trained_rf_path", type=str, default= 'saved_classical_ml_models/rf_model.pkl')    
parser.add_argument("--trained_lr_path", type=str, default= 'saved_classical_ml_models/lr_model.pkl')    
parser.add_argument("--trained_xgb_path", type=str, default= 'saved_classical_ml_models/xgb_model.pkl')    


parser.add_argument("--ml_model", type=str, default='none', choices=['rf', 'lr', 'xgb']) 

parser.add_argument("--test_models", type=int, default=0, choices=[0, 1])    
parser.add_argument("--plots", type=int, default=0, choices=[0, 1])    
parser.add_argument("--table_to_exclude", type=str, default='note_nlp', choices=['diagnosis', 'drug', 'procedure', 'note_nlp'])    


# non_feature_list = ['uniq_id', 'person_id', 'drug_era_start_date', 'drug_era_end_date', 'treatment_duration_days', 'data_created_at', 'outcome']

non_feature_list = ['person_id', 'drug_exposure_start_DATE', 'TreatmentDuration', 'outcome']

args = parser.parse_args()



if  args.ml_model == 'rf':
    print('Starting to train a random forest model using:\n')
    cl_ml.random_forest_model(args.train_data_path
                            , args.test_data_path
                            , args.table_to_exclude
                            , non_feature_list
                            )

elif  args.ml_model == 'lr':
    print('Starting to train a logistic regression model using:\n')
    cl_ml.logistic_regression_model(args.train_data_path
                            ,args.test_data_path
                            , args.table_to_exclude
                            , non_feature_list
                            )

elif  args.ml_model == 'xgb':
    print('Starting to train a logistic regression model using:\n')
    cl_ml.xgboost_model(args.train_data_path
                            ,args.test_data_path
                            , args.table_to_exclude
                            , non_feature_list
                            )    
else:
    print('No ML model has been selected ... ')


if args.test_models == 1:
    cl_ml.test_with_imb(args.trained_rf_path
                        , args.trained_lr_path
                        , args.trained_xgb_path
                        , args.test_data_path
                        , args.table_to_exclude
                        , non_feature_list
                        )


if args.plots == 1:
    cl_ml.plots(args.trained_rf_path
                        , args.trained_lr_path
                        , args.trained_xgb_path
                        , args.test_data_path
                        , args.table_to_exclude
                        , non_feature_list
                        )


