# from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
import os
import numpy as np
import pdb
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
# from sklearn.svm import SVC
from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import roc_auc_score
import csv
import pandas as pd
from sklearn.model_selection import StratifiedKFold
import copy
from sklearn.utils import shuffle
import random
import pickle
import matplotlib.pyplot as plt
import shap
import xgboost as xgb
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import precision_recall_curve, auc
from sklearn.calibration import calibration_curve

from sklearn.calibration import calibration_curve

def performance_evaluation(rf_predictions
                        , test_data_for_eval
                        , best_model
                        , non_feature_list):
    labels = test_data_for_eval['outcome'].values
    rf_test_auc=roc_auc_score(test_data_for_eval['outcome'], best_model.predict_proba(test_data_for_eval.drop(non_feature_list, axis=1, inplace=False))[:,1])

    tp=0
    tn=0
    fn=0
    fp=0
    accuracy=0
    precision=0
    recall=0
    F1=0
    specificity=0
    for asses_ind in range(len(rf_predictions)):
        if(rf_predictions[asses_ind]==0 and labels[asses_ind]==0):
            tn=tn+1
        elif(rf_predictions[asses_ind]==0 and labels[asses_ind]==1):
            fn=fn+1
        elif(rf_predictions[asses_ind]==1 and labels[asses_ind]==1):
            tp=tp+1
        elif(rf_predictions[asses_ind]==1 and labels[asses_ind]==0):    
            fp=fp+1
    accuracy=(tn+tp)/(tn+tp+fn+fp)
    if(tp+fp == 0):
        precision=0
    else:
        precision=tp/(tp+fp)
    if(tp+fn==0):
        recall=0
    else:
        recall=tp/(tp+fn)
    if(precision==0 and recall==0):
        F1=0
    else:            
        F1=(2*precision*recall)/(precision+recall)
    if(tn+fp==0):
        specificity= 0
    else:
        specificity= tn/(tn+fp)    

    return tn, tp, fn, fp, accuracy, precision, recall, specificity, F1, rf_test_auc    

def write_results(tn
                , tp
                , fn
                , fp
                , accuracy
                , precision
                , recall
                , specificity
                , F1
                , rf_test_auc
                , model
                    ):
    with open('results/'+model+'_prediction_performance.csv', 'w') as f_results:
        f_results.write("Precision is: ")
        f_results.write(str(precision))
        f_results.write("\n")
        
        f_results.write("Recall is: ")
        f_results.write(str(recall))
        f_results.write("\n")
        
        f_results.write("Accuracy is: ")
        f_results.write(str(accuracy))
        f_results.write("\n") 

        f_results.write("F1 is: ")
        f_results.write(str(F1))
        f_results.write("\n")

        f_results.write("Specificity is: ")
        f_results.write(str(specificity))
        f_results.write("\n")

        f_results.write("AUC is: ")
        f_results.write(str(rf_test_auc))
        f_results.write("\n")

        f_results.write("TP is: ")
        f_results.write(str(tp))
        f_results.write("\n")

        f_results.write("TN is: ")
        f_results.write(str(tn))
        f_results.write("\n")

        f_results.write("FP is: ")
        f_results.write(str(fp))
        f_results.write("\n")

        f_results.write("FN is: ")
        f_results.write(str(fn))
        f_results.write("\n")



# === XGBoost
def xgboost_model(train_data_path
                        , test_data_path
                        , retention_cut_off
                        , non_feature_list
                        , min_treatment_duration
                        ):
    
    print('Minimum treatment duration is {} and retention threshold is {}.'.format(min_treatment_duration, retention_cut_off))
    print('Reading the data:')
    print(train_data_path)
    print(test_data_path)
    train_data = pd.read_csv(train_data_path)
    train_data = train_data[train_data['TreatmentDuration'] >= min_treatment_duration]
    train_data['outcome'] = train_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)

    test_data = pd.read_csv(test_data_path)
    test_data = test_data[test_data['TreatmentDuration'] >= min_treatment_duration]
    test_data['outcome'] = test_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)

    # if table_to_exclude != 'none':
    #     cols_to_exclude = [x for x in train_data.columns if table_to_exclude in x]
    #     train_data.drop(cols_to_exclude, axis=1, inplace=True)
    #     test_data.drop(cols_to_exclude, axis=1, inplace=True)

    print('Finished reading data...')
    n_estimators = [10, 50, 100, 150, 200, 500]#int(x) for x in np.linspace(start = 200, stop = 500, num = 10)]
    # Maximum number of levels in tree
    max_depth = [4, 8, 16, 32]#, 6, 8, 10, 12]# [int(x) for x in np.linspace(10, 110, num = 11)]
    gamma = [0.001, 0.01, 0.1, 0.5] 
    colsample_bytree = [0.1, 0.3, 0.5, 0.7]
    learning_rate = [0.0001, 0.001, 0.01, 0.1]
    # boosters = ['gbtree', 'gblinear']
    # Create the random grid
    hyperparameters = {'n_estimators': n_estimators
                   , 'max_depth': max_depth
                   , 'gamma': gamma
                   , 'colsample_bytree': colsample_bytree
                   , 'learning_rate':learning_rate
                   }

    print('Hyperparameters:')
    print(hyperparameters)
    with open('saved_classical_ml_models/xgb_hyperparameters.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in hyperparameters.items():
           writer.writerow([key, value])

    train_data_shuffled = train_data.sample(frac=1).reset_index(drop=True)  
    test_data_shuffled = test_data.sample(frac=1).reset_index(drop=True)  

    # n_to_p_ratio = len(train_data_shuffled[train_data_shuffled['outcome']==0])/len(train_data_shuffled[train_data_shuffled['outcome']==1])
    randomCV = RandomizedSearchCV(estimator=xgb.XGBClassifier(booster='gbtree', verbosity=1, n_jobs=-1, objective='binary:logistic'), param_distributions=hyperparameters, n_iter=50, cv=5,scoring='roc_auc')
    randomCV.fit(train_data_shuffled.drop(non_feature_list, axis=1, inplace=False), train_data_shuffled['outcome'])
    
    # === Save models
    with open('saved_classical_ml_models/xgb_model.pkl','wb') as f:
        pickle.dump(randomCV,f)
    
    (pd.DataFrame.from_dict(data=randomCV.best_params_, orient='index').to_csv('saved_classical_ml_models/best_params_xgb.csv', header=False))
    best_xgb_model= randomCV.best_estimator_

    xgb_predictions = best_xgb_model.predict(test_data_shuffled.drop(non_feature_list, axis=1, inplace=False))    
    np.savetxt('saved_classical_ml_models/predictions_xgb.csv', xgb_predictions, delimiter=',')

    tn, tp, fn, fp, accuracy, precision, recall, specificity, F1, xgb_test_auc = performance_evaluation(xgb_predictions
                                                                            , test_data_shuffled
                                                                            , best_xgb_model
                                                                            , non_feature_list
                                                                            )   
    write_results(tn, tp, fn, fp, 
                accuracy, precision, recall, specificity
                , F1, xgb_test_auc
                , 'xgb' )
    metrics.plot_roc_curve(best_xgb_model, test_data_shuffled.drop(non_feature_list, axis=1, inplace=False), test_data_shuffled['outcome'], name='xgboost') 
    plt.savefig('results/roc_curve_xgb.png', dpi=300)
    plt.close()

    
    print('Creating shap plots using test data ....')    
    explainer = shap.TreeExplainer(best_xgb_model)
    shap_values = explainer(test_data_shuffled.drop(non_feature_list, axis=1, inplace=False))

    f = plt.figure()
    shap.plots.beeswarm(shap_values, show = False, max_display=30)
    plt.subplots_adjust(left=0.3)  
    f.savefig('results/beeswarm_xgb_original_test.png', dpi=600)
    plt.close(f)
    

    f2 = plt.figure()
    shap.plots.bar(shap_values, show = False)
    f2.savefig('results/bar_xgb_original_test.png', dpi=600)
    plt.close(f2)


    with open('results/shap_values_uing_xgb_and_tes_data.pkl','wb') as f:
        pickle.dump(shap_values,f)

# === Logistic regression
def logistic_regression_model(train_data_path
                        ,test_data_path
                        , retention_cut_off
                        , non_feature_list
                        , min_treatment_duration
                        ):
    print('Minimum treatment duration is {} and retention threshold is {}.'.format(min_treatment_duration, retention_cut_off))
    print('Reading the data:')
    print(train_data_path)
    print(test_data_path)
    print('Finished reading data...')

    # Read train data
    train_data = pd.read_csv(train_data_path)
    # Exclude encounters with treatment duration less than min_treatment_duration days
    train_data = train_data[train_data['TreatmentDuration'] >= min_treatment_duration]    
    # Outcome (label) 1 if treatment duration is less than retention_cut_off days.
    train_data['outcome'] = train_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)

    # Read test data
    test_data = pd.read_csv(test_data_path)
    # Exclude encounters with treatment duration less than min_treatment_duration days
    test_data = test_data[test_data['TreatmentDuration'] >= min_treatment_duration]
    # Outcome (label) 1 if treatment duration is less than retention_cut_off days.
    test_data['outcome'] = test_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)

    # Check to make sure train and test do not overlap and no data leakage
    if sum(test_data['person_id'].isin(train_data['person_id']))>0:
        pdb.set_trace()
        print('Warning. Overlap between train and test set!')


    # if table_to_exclude != 'none':
    #     cols_to_exclude = [x for x in train_data.columns if table_to_exclude in x]
    #     train_data.drop(cols_to_exclude, axis=1, inplace=True)
    #     test_data.drop(cols_to_exclude, axis=1, inplace=True)
    

    # A pool of hyper-parameters to search from during model tuning
    hyperparameters = {
                        'penalty' : ['l1', 'l2'],
                        'solver' : ['liblinear', 'saga'],#'lbfgs', 'liblinear', 'newton-cg', 'newton-cholesky', 'sag', 'saga'],
                        # 'degree' : [0, 1, 2, 3, 4, 5, 6],
                        #'loss' : ['hinge', 'squared_hinge'],
                        #'dual' : [True, False],
                        'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100]#[2**-10, 2** -8, 2 ** -6, 2** -4, 2**-2, 1, 2**2, 2**4, 2**6, 2**8, 2**10]       
        }

    # Save hyper-parameter search space
    with open('saved_classical_ml_models/lr_hyperparameters.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in hyperparameters.items():
           writer.writerow([key, value])
    
    # pdb.set_trace()
    # Shuffle the date
    train_data_shuffled = train_data.sample(frac=1).reset_index(drop=True)  
    test_data_shuffled = test_data.sample(frac=1).reset_index(drop=True)  
    
    # Create and fit the model + cross validation
    randomCV = RandomizedSearchCV(estimator=LogisticRegression(n_jobs=-1, verbose=1), param_distributions=hyperparameters, n_iter=50, cv=5,scoring="roc_auc")    
    randomCV.fit(train_data_shuffled.drop(non_feature_list, axis=1, inplace=False), train_data_shuffled['outcome'])

    # === Save models
    with open('saved_classical_ml_models/lr_model.pkl','wb') as f:
        pickle.dump(randomCV,f)

    # Save optimum parameters
    (pd.DataFrame.from_dict(data=randomCV.best_params_, orient='index').to_csv('saved_classical_ml_models/best_params_lr.csv', header=False))
    
    best_lr_model= randomCV.best_estimator_

    lr_predictions = best_lr_model.predict(test_data_shuffled.drop(non_feature_list, axis=1, inplace=False))    
    np.savetxt('saved_classical_ml_models/predictions_lr.csv', lr_predictions, delimiter=',')

    tn, tp, fn, fp, accuracy, precision, recall, specificity, F1, lr_test_auc = performance_evaluation(lr_predictions, test_data_shuffled, best_lr_model, non_feature_list)   
    write_results(tn, tp, fn, fp, 
                accuracy, precision, recall, specificity
                , F1, lr_test_auc
                , 'lr')

    metrics.plot_roc_curve(best_lr_model, test_data_shuffled.drop(non_feature_list, axis=1, inplace=False), test_data_shuffled['outcome'], name='Logistic Regression') 
    plt.savefig('results/roc_curve_lr.png', dpi=300)
    plt.close()


def random_forest_model(train_data_path
                        ,test_data_path
                        , retention_cut_off
                        , non_feature_list
                        , min_treatment_duration
                        ):    
    print('Minimum treatment duration is {} and retention threshold is {}.'.format(min_treatment_duration, retention_cut_off))
    # Read train data
    print('Reading the data:')
    print(train_data_path)
    print(test_data_path)
    train_data = pd.read_csv(train_data_path)
    # Exclude encounters with treatment duration less than min_treatment_duration days    
    train_data = train_data[train_data['TreatmentDuration'] >= min_treatment_duration]
    # Outcome (label) 1 if treatment duration is less than retention_cut_off days.    
    train_data['outcome'] = train_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)

    num_p_train = train_data[train_data['outcome']==1].shape[0]
    num_n_train = train_data[train_data['outcome']==0].shape[0]

    test_data = pd.read_csv(test_data_path)
    # Exclude encounters with treatment duration less than min_treatment_duration days    
    test_data = test_data[test_data['TreatmentDuration'] >= min_treatment_duration]
    # Outcome (label) 1 if treatment duration is less than retention_cut_off days.    
    test_data['outcome'] = test_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)

    # Check to make sure train and test do not overlap and no data leakage
    if sum(test_data['person_id'].isin(train_data['person_id']))>0:
        pdb.set_trace()
        print('Warning. Overlap between train and test set!')

    # if table_to_exclude != 'none':
    #     cols_to_exclude = [x for x in train_data.columns if table_to_exclude in x]
    #     train_data.drop(cols_to_exclude, axis=1, inplace=True)
    #     test_data.drop(cols_to_exclude, axis=1, inplace=True)

    print('Finished reading data...')
    # Number of trees in random forest
    n_estimators = [10, 50, 100, 150, 200, 250, 500]#int(x) for x in np.linspace(start = 200, stop = 500, num = 10)]

    # Number of features to consider at every split
    max_features = [0.01, 0.1, 0.5, 'sqrt', 'auto']
    # Maximum number of levels in tree
    max_depth = [4, 8, 16, 32]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [0.0001, 0.001, 0.01, 0.1]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [0.0001, 0.001, 0.01, 0.1]
    # Method of selecting samples for training each tree
    bootstrap = [True, False]

    # Create the random grid
    hyperparameters = {'n_estimators': n_estimators
                   ,'max_features': max_features
                   , 'max_depth': max_depth
                   , 'min_samples_split': min_samples_split
                   , 'min_samples_leaf': min_samples_leaf
                   , 'bootstrap': bootstrap
                   }#,'ccp_alpha': ccp_alpha}

    # Save hyper-parameter search space
    with open('saved_classical_ml_models/rf_hyperparameters.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in hyperparameters.items():
           writer.writerow([key, value])
    
    # pdb.set_trace()    
    # shuffle the data 
    train_data_shuffled = train_data.sample(frac=1).reset_index(drop=True)  
    test_data_shuffled = test_data.sample(frac=1).reset_index(drop=True)  
    # Create and train the model
    randomCV = RandomizedSearchCV(estimator=RandomForestClassifier(n_jobs=-1, verbose=1), param_distributions=hyperparameters, n_iter=50, cv=5,scoring="roc_auc")
    randomCV.fit(train_data_shuffled.drop(non_feature_list, axis=1, inplace=False), train_data_shuffled['outcome'])
       
    # === Save models
    with open('saved_classical_ml_models/rf_model.pkl','wb') as f:
        pickle.dump(randomCV,f)
    
    # Save optimum parameters
    (pd.DataFrame.from_dict(data=randomCV.best_params_, orient='index').to_csv('saved_classical_ml_models/best_params_rf.csv', header=False))
    best_rf_model= randomCV.best_estimator_

    rf_predictions = best_rf_model.predict(test_data_shuffled.drop(non_feature_list, axis=1, inplace=False))    
    np.savetxt('saved_classical_ml_models/predictions_rf.csv', rf_predictions, delimiter=',')

    # metrics.f1_score(y_true=test_data_shuffled['label'], y_pred=rf_predictions)
    # metrics.precision_score(y_true=test_data_shuffled['label'], y_pred=rf_predictions)
    # metrics.recall_score(y_true=test_data_shuffled['label'], y_pred=rf_predictions)
    # pdb.set_trace()
    results_report = metrics.classification_report(y_true=test_data_shuffled['outcome'], y_pred=rf_predictions, output_dict=True)
    results_report_df = pd.DataFrame(results_report).transpose()
    results_report_df.to_csv('results/rf_results_report.csv')

    tn, tp, fn, fp, accuracy, precision, recall, specificity, F1, rf_test_auc = performance_evaluation(rf_predictions
                                                                            , test_data_shuffled
                                                                            , best_rf_model
                                                                            , non_feature_list
                                                                            )   
    write_results(tn, tp, fn, fp, 
                accuracy, precision, recall, specificity
                , F1, rf_test_auc
                , 'rf')
    
    metrics.plot_roc_curve(best_rf_model, test_data_shuffled.drop(non_feature_list, axis=1, inplace=False), test_data_shuffled['outcome'], name='Random Forest') 
    plt.savefig('results/roc_curve_rf.png', dpi=300)
    plt.close()

    

    feat_importances = pd.Series(randomCV.best_estimator_.feature_importances_, index=train_data_shuffled.drop(non_feature_list, axis=1, inplace=False).columns)
    fig = feat_importances.nlargest(30).plot(kind='barh', grid=True,figsize=(16,14))
    fig.set_xlabel("Importance Score")
    fig.set_ylabel("Features")
    fig.get_figure().savefig('results/rf_feature_importance_concept_ids.png', dpi=300)
    plt.close()



def test_with_imb(trained_rf_path
                , trained_lr_path
                , trained_xgb_path
                , test_data_path
                , retention_cut_off
                , non_feature_list
                , min_treatment_duration
                ):
    '''
    This function loads the trained models and perform repeated testing.
    '''
    print('Minimum treatment duration is {} and retention threshold is {}.'.format(min_treatment_duration, retention_cut_off))
    print('Testing using:')
    print(test_data_path)    
    test_data = pd.read_csv(test_data_path)
    test_data = test_data[test_data['TreatmentDuration'] >= min_treatment_duration]
    test_data['outcome'] = test_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)


    # if table_to_exclude != 'none':
    #     cols_to_exclude = [x for x in test_data.columns if table_to_exclude in x]
    #     test_data.drop(cols_to_exclude, axis=1, inplace=True)


    # test_data_imb = test_data
    reapeated_testing(trained_rf_path
                    , trained_lr_path
                    , trained_xgb_path
                    , test_data
                    # , table_to_exclude
                    , non_feature_list
                    )



def reapeated_testing(trained_rf_path
                , trained_lr_path
                , trained_xgb_path
                , test_data_imb
                # , table_to_exclude
                , non_feature_list               
                ):

    # pdb.set_trace()

    randomCV_rf = pickle.load(open(trained_rf_path[:-4]+'.pkl', 'rb'))
    best_model_rf= randomCV_rf.best_estimator_

    randomCV_lr = pickle.load(open(trained_lr_path[:-4]+'.pkl', 'rb'))
    best_model_lr= randomCV_lr.best_estimator_    
    
    randomCV_xgb = pickle.load(open(trained_xgb_path[:-4]+'.pkl', 'rb'))    
    best_model_xgb= randomCV_xgb.best_estimator_    

    if sum(best_model_rf.feature_names_in_ != test_data_imb.drop(non_feature_list, axis=1, inplace=False).columns)>0:
        pdb.set_trace()
        print('Warning')    


    if sum(best_model_lr.feature_names_in_ != test_data_imb.drop(non_feature_list, axis=1, inplace=False).columns)>0:
        pdb.set_trace()
        print('Warning')

    if sum(best_model_xgb.get_booster().feature_names != test_data_imb.drop(non_feature_list, axis=1, inplace=False).columns)>0:
        pdb.set_trace()
        print('Warning')    

    with open('results/reapeated_testing/reapeated_testing_rf.csv', 'w') as rf_res_file, open('results/reapeated_testing/reapeated_testing_precisions_recalls_rf.csv', 'w') as rf_res_file_pr, open('results/reapeated_testing/reapeated_testing_lr.csv', 'w') as lr_res_file, open('results/reapeated_testing/reapeated_testing_precisions_recalls_lr.csv', 'w') as lr_res_file_pr, open('results/reapeated_testing/reapeated_testing_xgb.csv', 'w') as xgb_res_file, open('results/reapeated_testing/reapeated_testing_precisions_recalls_xgb.csv', 'w') as xgb_res_file_pr:       
        rf_res_file.write('Precision, Recall, F1, AUC, TP, TN, FP, FN\n')
        lr_res_file.write('Precision, Recall, F1, AUC, TP, TN, FP, FN\n')
        xgb_res_file.write('Precision, Recall, F1, AUC, TP, TN, FP, FN\n')

        test_data_imb_pos = test_data_imb[test_data_imb.outcome == 1]
        test_data_imb_neg = test_data_imb[test_data_imb.outcome == 0]

        fold_counter=0 
        for i in range(50):    
            temp_test_fold_pos = test_data_imb_pos.sample(frac=1, replace=True)
            temp_test_fold_neg = test_data_imb_neg.sample(frac=1, replace=True)

            temp_test_fold = pd.concat([temp_test_fold_pos, temp_test_fold_neg])
            temp_test_fold.to_csv('results/reapeated_testing/test_fold_rf'+str(fold_counter)+'.csv', index=False)
            fold_counter +=1
            
            # pdb.set_trace()
            precisions_all_rf, recall_all_rf, thresholds_all_rf = precision_recall_curve( temp_test_fold['outcome'].values, best_model_rf.predict_proba(temp_test_fold.drop(non_feature_list, axis=1, inplace=False))[:,1])
            rf_res_file_pr.write('precisions ' +str(i)+', ')
            rf_res_file_pr.write(','.join(map(repr, precisions_all_rf)))
            rf_res_file_pr.write('\n')

            rf_res_file_pr.write('Recalls ' +str(i)+', ')
            rf_res_file_pr.write(','.join(map(repr, recall_all_rf)))
            rf_res_file_pr.write('\n')

            rf_res_file_pr.write('Thresholds ' +str(i)+', ')
            rf_res_file_pr.write(','.join(map(repr, thresholds_all_rf)))
            rf_res_file_pr.write('\n')

            
            predictions_rf = best_model_rf.predict(temp_test_fold.drop(non_feature_list, axis=1, inplace=False))        
            
            tn_rf, tp_rf, fn_rf, fp_rf, accuracy_rf, precision_rf, recall_rf, specificity_rf, F1_rf, test_auc_rf = performance_evaluation(predictions_rf, temp_test_fold, best_model_rf, non_feature_list)   
            
            rf_res_file.write(str(precision_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(recall_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(F1_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(test_auc_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(tp_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(tn_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(fp_rf))
            rf_res_file.write(',')
            rf_res_file.write(str(fn_rf))
            rf_res_file.write('\n')
           
    
            precisions_all_lr, recall_all_lr, thresholds_all_lr = precision_recall_curve( temp_test_fold['outcome'].values, best_model_lr.predict_proba(temp_test_fold.drop(non_feature_list, axis=1, inplace=False))[:,1])
            lr_res_file_pr.write('precisions ' +str(i)+', ')
            lr_res_file_pr.write(','.join(map(repr, precisions_all_lr)))
            lr_res_file_pr.write('\n')

            lr_res_file_pr.write('Recalls ' +str(i)+', ')
            lr_res_file_pr.write(','.join(map(repr, recall_all_lr)))
            lr_res_file_pr.write('\n')

            lr_res_file_pr.write('Thresholds ' +str(i)+', ')
            lr_res_file_pr.write(','.join(map(repr, thresholds_all_lr)))
            lr_res_file_pr.write('\n')

            predictions_lr = best_model_lr.predict(temp_test_fold.drop(non_feature_list, axis=1, inplace=False))        
            tn_lr, tp_lr, fn_lr, fp_lr, accuracy_lr, precision_lr, recall_lr, specificity_lr, F1_lr, test_auc_lr = performance_evaluation(predictions_lr, temp_test_fold, best_model_lr, non_feature_list)   
            lr_res_file.write(str(precision_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(recall_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(F1_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(test_auc_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(tp_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(tn_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(fp_lr))
            lr_res_file.write(',')
            lr_res_file.write(str(fn_lr))
            lr_res_file.write('\n')            
    

            precisions_all_xgb, recall_all_xgb, thresholds_all_xgb = precision_recall_curve( temp_test_fold['outcome'].values, best_model_xgb.predict_proba(temp_test_fold.drop(non_feature_list, axis=1, inplace=False))[:,1])
            xgb_res_file_pr.write('precisions ' +str(i)+', ')
            xgb_res_file_pr.write(','.join(map(repr, precisions_all_xgb)))
            xgb_res_file_pr.write('\n')

            xgb_res_file_pr.write('Recalls ' +str(i)+', ')
            xgb_res_file_pr.write(','.join(map(repr, recall_all_xgb)))
            xgb_res_file_pr.write('\n')

            xgb_res_file_pr.write('Thresholds ' +str(i)+', ')
            xgb_res_file_pr.write(','.join(map(repr, thresholds_all_xgb)))
            xgb_res_file_pr.write('\n')

            predictions_xgb = best_model_xgb.predict(temp_test_fold.drop(non_feature_list, axis=1, inplace=False))        
            tn_xgb, tp_xgb, fn_xgb, fp_xgb, accuracy_xgb, precision_xgb, recall_xgb, specificity_xgb, F1_xgb, test_auc_xgb = performance_evaluation(predictions_xgb, temp_test_fold, best_model_xgb, non_feature_list)   
            xgb_res_file.write(str(precision_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(recall_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(F1_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(test_auc_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(tp_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(tn_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(fp_xgb))
            xgb_res_file.write(',')
            xgb_res_file.write(str(fn_xgb))
            xgb_res_file.write('\n')                 


def plots(trained_rf_path
                , trained_lr_path
                , trained_xgb_path
                , test_data_path
                , retention_cut_off
                , non_feature_list
                , min_treatment_duration
                ):
    # pdb.set_trace()
    print('Testing using imbalance test sets. ')
    print(test_data_path)
    
    test_data = pd.read_csv(test_data_path)
    test_data = test_data[test_data['TreatmentDuration'] >= min_treatment_duration]
    test_data['outcome'] = test_data['TreatmentDuration'].apply(lambda x: 0 if x >= retention_cut_off else 1)


    # if table_to_exclude != 'none':
    #     cols_to_exclude = [x for x in test_data.columns if table_to_exclude in x]
    #     test_data.drop(cols_to_exclude, axis=1, inplace=True)



    randomCV_rf = pickle.load(open(trained_rf_path[:-4]+'.pkl', 'rb'))
    best_model_rf= randomCV_rf.best_estimator_

    randomCV_lr = pickle.load(open(trained_lr_path[:-4]+'.pkl', 'rb'))
    best_model_lr= randomCV_lr.best_estimator_    
    
    randomCV_xgb = pickle.load(open(trained_xgb_path[:-4]+'.pkl', 'rb'))    
    best_model_xgb= randomCV_xgb.best_estimator_    

    if sum(best_model_rf.feature_names_in_ != test_data.drop(non_feature_list, axis=1, inplace=False).columns)>0:
        pdb.set_trace()
        print('Warning')    


    if sum(best_model_lr.feature_names_in_ != test_data.drop(non_feature_list, axis=1, inplace=False).columns)>0:
        pdb.set_trace()
        print('Warning')

    if sum(best_model_xgb.get_booster().feature_names != test_data.drop(non_feature_list, axis=1, inplace=False).columns)>0:
        pdb.set_trace()
        print('Warning')    

    # pdb.set_trace()
    precisions_all_lr, recall_all_lr, thresholds_all_lr = precision_recall_curve( test_data['outcome'].values, best_model_lr.predict_proba(test_data.drop(non_feature_list, axis=1, inplace=False))[:,1])
    auc_pr_lr = auc(recall_all_lr, precisions_all_lr)

    precisions_all_rf, recall_all_rf, thresholds_all_rf = precision_recall_curve( test_data['outcome'].values, best_model_rf.predict_proba(test_data.drop(non_feature_list, axis=1, inplace=False))[:,1])
    auc_pr_rf = auc(recall_all_rf, precisions_all_rf)

    precisions_all_xgb, recall_all_xgb, thresholds_all_xgb = precision_recall_curve( test_data['outcome'].values, best_model_xgb.predict_proba(test_data.drop(non_feature_list, axis=1, inplace=False))[:,1])
    auc_pr_xgb = auc(recall_all_xgb, precisions_all_xgb)

    plt.plot(recall_all_lr, precisions_all_lr, label='LR (AUC-PR = {:.3f})'.format(auc_pr_lr))
    plt.plot(recall_all_rf, precisions_all_rf, label='RF (AUC-PR = {:.3f})'.format(auc_pr_rf))
    plt.plot(recall_all_xgb, precisions_all_xgb, label='XGB (AUC-PR = {:.3f})'.format(auc_pr_xgb))

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curves')
    plt.legend()
    plt.xlim([0, 1])
    plt.ylim([0, 1])

    plt.savefig('results/pr_curve.png',dpi=600)
    plt.close()

    # Calibration
    prob_lr = best_model_lr.predict_proba(test_data.drop(non_feature_list, axis=1, inplace=False))[:,1]
    prob_rf = best_model_rf.predict_proba(test_data.drop(non_feature_list, axis=1, inplace=False))[:,1]
    prob_xgb = best_model_xgb.predict_proba(test_data.drop(non_feature_list, axis=1, inplace=False))[:,1]

    fraction_of_positives_lr, mean_predicted_value_lr = calibration_curve(test_data['outcome'].values, prob_lr, n_bins=10)
    fraction_of_positives_rf, mean_predicted_value_rf = calibration_curve(test_data['outcome'].values, prob_rf, n_bins=10)
    fraction_of_positives_xgb, mean_predicted_value_xgb = calibration_curve(test_data['outcome'].values, prob_xgb, n_bins=10)

    plt.plot(mean_predicted_value_lr, fraction_of_positives_lr, 's-', label='LR')
    plt.plot(mean_predicted_value_rf, fraction_of_positives_rf, 'o-', label='RF')
    plt.plot(mean_predicted_value_xgb, fraction_of_positives_xgb, '^-', label='XGB')

    # Perfectly calibrated line
    plt.plot([0, 1], [0, 1], '--', color='gray', label='Perfectly Calibrated')

    plt.xlabel('Mean Predicted Value')
    plt.ylabel('Fraction of Positives')
    plt.title('Calibration Curves')
    plt.legend()
    plt.savefig('results/calibration_curve.png',dpi=600)
    plt.close()
