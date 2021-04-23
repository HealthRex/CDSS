import numpy as np
import pandas as pd
from scipy.sparse import load_npz
import lightgbm as lgb
import datetime
import pytz
import joblib
import os
import argparse
import json

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.preprocessing import FunctionTransformer
from random import randrange
from datetime import timedelta, datetime
from sklearn.metrics import roc_curve, auc, average_precision_score, roc_auc_score,plot_precision_recall_curve, plot_roc_curve

import pdb

def ridge(X_train, y_train, X_valid, y_valid):

    """ 1. Splits train set into k fold for hyperparameter search
        2. Refits on Train
        3. Evaluate on Val
        4. Returns Model, hyperparameters, and yhats
    """
    grid = {'C' : np.logspace(-8, 8, 17)}
    cv = StratifiedKFold(n_splits=5, random_state=42)
    ridge = LogisticRegression(penalty='l2', max_iter= 1000, solver='lbfgs')
    search = GridSearchCV(ridge, grid, scoring='roc_auc', cv=cv, verbose=2)
    result = search.fit(X_train, y_train)
    
    print("Ridge\n")
    print("Best CV Score: {score}\n".format(score=result.best_score_))
    print("Best Hyperparameters: %s\n" % result.best_params_)
    
    # Fit model with best params on full train set and get score on val set
    ridge = LogisticRegression(**result.best_params_)
    ridge.fit(X_train, y_train)
    y_predict = ridge.predict_proba(X_valid)[:, 1]
    auc = roc_auc_score(y_valid, y_predict)

    print("Validation Set AUROC: {auc}\n".format(auc=auc))

    return ridge, y_predict, auc, result.best_params_

def lasso(X_train, y_train, X_valid, y_valid):

    """ 1. Splits train set into k fold for hyperparameter search
        2. Refits on Train
        3. Evaluate on Val
        4. Returns Model, hyperparameters, and yhats
    """
    grid = {'C' : np.logspace(-8, 8, 17)}
    cv = StratifiedKFold(n_splits=5, random_state=42)
    lasso = LogisticRegression(penalty='l1', max_iter= 1000, solver='liblinear')
    search = GridSearchCV(lasso, grid, scoring='roc_auc', cv=cv, verbose=2)
    result = search.fit(X_train, y_train)
    
    print("Lasso\n")
    print("Best CV Score: {score}\n".format(score=result.best_score_))
    print("Best Hyperparameters: %s\n" % result.best_params_)
    
    # Fit model with best params on full train set and get score on val set
    lasso = LogisticRegression(**result.best_params_)
    lasso.fit(X_train, y_train)
    y_predict = lasso.predict_proba(X_valid)[:, 1]
    auc = roc_auc_score(y_valid, y_predict)

    print("Validation Set AUROC: {auc}\n".format(auc=auc))

    return lasso, y_predict, auc, result.best_params_

def elastic_net(X_train, y_train, X_valid, y_valid):
    # log_transformer = FunctionTransformer(np.log1p, validate=True)
    # X_train = log_transformer.transform(X_train)
    # X_valid = log_transformer.transform(X_valid)

    cv_history = {}

    #Fit on all values of c and then find the classifier with best AUROC 
    for l1 in [0.2, 0.4, 0.6, 0.8]:
        for c in np.logspace(-4, 4, 9): 
            elnet = LogisticRegression(penalty='elasticnet', C = c, l1_ratio= l1, max_iter= 1000, solver='saga')
            elnet.fit(X_train, y_train)

            #Predict the probability of positive class
            y_predict = elnet.predict_proba(X_valid)[:,1]
            cv_roc = roc_auc_score(y_valid, y_predict)
            print("AUC w/ C = ", c, "and l1_ratio of ", l1, " is ", cv_roc)
            cv_history[cv_roc] = elnet

    elnet_opt = cv_history[max(cv_history.keys())]
    y_opt_predict = elnet_opt.predict_proba(X_valid)[:,1]
    
    return y_opt_predict, roc_auc_score(y_valid, y_opt_predict), elnet_opt



def random_forest(X_train, y_train, X_valid, y_valid):

    """ 1. Splits train set into k fold for hyperparameter search
        2. Refits on Train
        3. Evaluate on Val
        4. Returns Model, hyperparameters, and yhats
    """

    grid = {'min_samples_split' : [2, 10, 50, 100],
            'max_features' : ['sqrt', 'log2', None]
           }
    cv = StratifiedKFold(n_splits=5, random_state=42)
    rf = RandomForestClassifier(n_estimators=1000, random_state=42)
    search = GridSearchCV(rf, grid, scoring='roc_auc', cv=cv, verbose=2)
    result = search.fit(X_train, y_train)
    
    
    print("Random Forest\n")
    print("Best CV Score: {score}\n".format(score=result.best_score_))
    print("Best Hyperparameters: %s\n" % result.best_params_)
    
    # Fit model with best params on full train set and get score on val set
    rf = RandomForestClassifier(**result.best_params_)
    rf.fit(X_train, y_train)
    y_predict = rf.predict_proba(X_valid)[:, 1]
    auc = roc_auc_score(y_valid, y_predict)

    print("Validation Set AUROC: {auc}\n".format(auc=auc))

    return rf, y_predict, auc, result.best_params_

def lightgbm(X_train, y_train, X_valid, y_valid): 
    """ 
    1. Splits training set into k folds
    2. Splits random small 5% chunk of training data from each fold for early stopping
    3. Finds optimal hyperparameters on training set
    4. Fits on entire training set - again split 5% chunk of training data for early stopping
    5. Evaluate on Val
    6. Return model, best hyperparams, yhats
    """

    grid = {'learning_rate' : [0.01, 0.05, 0.1, 0.5],
            'num_leaves' : [2, 8, 16, 32, 64]
    }
    cv = StratifiedKFold(n_splits=5, random_state=42)

    # Instantiate dictionary of aucs
    aucs = {}
    for lr in grid['learning_rate']:
        aucs[lr] = {}
        for l in grid['num_leaves']:
            aucs[lr][l] = []
    
    ind=0
    for train_inds, val_inds in cv.split(X_train, y_train):
        # Get train, val, test for each fold.  Use 5% of train inds for early stopping
        e_stopping = int(len(train_inds) * 0.95)
        x_tr, x_v, = X_train[train_inds[:e_stopping]], X_train[train_inds[e_stopping:]]
        y_tr, y_v =  y_train[train_inds[:e_stopping]], y_train[train_inds[e_stopping:]]
        x_test, y_test = X_train[val_inds], y_train[val_inds]

        for lr in grid['learning_rate']:
            for num_leaves in grid['num_leaves']:
                # Create GBM model 
                gbm = lgb.LGBMClassifier(objective='binary',
                                         n_estimators=1000,
                                         learning_rate=lr,
                                         num_leaves=num_leaves
                )

                # Fit model with early stopping
                gbm.fit(x_tr,
                        y_tr,
                        eval_set= [(x_v, y_v)],
                        eval_metric = 'binary',
                        early_stopping_rounds = 10,
                        verbose=False
                )

                y_predict = gbm.predict_proba(x_test)[:,1]
                fold_auc = roc_auc_score(y_test, y_predict)
                estimators = gbm.best_iteration_
                out_str = "Learning Rate:{lr} Num Leaves:{num_leaves} Num Estimators:{est} Fold:{ind} AUROC:{roc}"
                print(out_str.format(lr=lr, num_leaves=num_leaves, est=estimators, ind=ind, roc=fold_auc))  
                aucs[lr][num_leaves].append(roc_auc_score(y_test, y_predict))
        ind += 1
    # Get Best Hyperparameters
    best_auc = 0.0
    best_params = {'learning_rate' : None, 'num_leaves' : None}
    for lr in aucs:
        for l in aucs[lr]:
            aucs[lr][l] = np.mean(aucs[lr][l])
            if aucs[lr][l] > best_auc:
                best_auc = aucs[lr][l]
                best_params = {'learning_rate' : lr, 'num_leaves' : num_leaves}
    print("Optimal Params")
    print(best_params)
    print("Best cross validated auroc")
    print(best_auc)

    print("Retraining on full training set...")
    # Fit on full training set
    inds = [i for i in range(len(y_train))]
    np.random.shuffle(inds)
    e_s = int(len(inds) * 0.95)
    x_tr, x_val = X_train[inds[:e_s]], X_train[inds[e_s:]]
    y_tr, y_val = y_train[inds[:e_s]], y_train[inds[e_s:]]
    gbm = lgb.LGBMClassifier(objective='binary',
                             n_estimators=1000,
                             learning_rate=best_params['learning_rate'],
                             num_leaves=best_params['num_leaves']
    )

    gbm.fit(x_tr,
            y_tr,
            eval_set = [(x_val, y_val)],
            eval_metric = 'binary',
            early_stopping_rounds = 10,
            verbose = False
    )

    best_params['boosting_rounds'] = gbm.best_iteration_ # get num boosting rounds
    y_predict = gbm.predict_proba(X_valid)[:,1]
    auc = roc_auc_score(y_valid, y_predict)
    print("Num Estimators:{est} Eval set AUROC:{roc}".format(est=gbm.best_iteration_ , roc=auc))

    return gbm, y_predict, auc, best_params

def write_params_to_json(clf, output_path, model, TAB):

    json_path = output_path + model + TAB + '_params.json'
    print("Saving hyperparameters to ", json_path)

    if model in ["lasso", "ridge", "elastic_net", "random_forest"]: 
        json.dump(clf.get_params(), open(json_path, 'w'))
    else: # lightgbm
        params = clf.get_params()
        params["n_estimators"] = clf.best_iteration_ # Add in early stopping round 
        json.dump(params, open(json_path, 'w'))

def read_from_json(json_file, model):

    with open(json_file) as file:
        params = json.load(file)

    if model in ["ridge","lasso","elastic_net"]:
        clf = LogisticRegression(**params)
    elif model == "random_forest":
        clf = RandomForestClassifier(**params)
    elif model == "lightgbm":
        clf = lgb.LGBMClassifier(**params)
    elif model == "ffnn":
        json_file = open(json_file, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        clf = model_from_json(loaded_model_json)
    
    return clf

def retrain_from_model(X_train, y_train, X_test, y_test, clf, model):
    # Fit with specified hyperparameters
    clf.fit(X_train, y_train)
    y_predict = clf.predict_proba(X_test)[:,1]
    roc = roc_auc_score(y_test, y_predict)
        
    return y_predict, roc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_class', default=None, type=str, help='ridge/lasso/lightgbm/random_forest/ffnn')
    parser.add_argument('--data_dir', default="", type=str, help='directory with sparce matrices train val test')
    parser.add_argument('--label', default="", type=str, help='the column name for label in traige_TE.triage_cohort_final_with_labels_complete1vs')
    parser.add_argument('--output_dir', default="", type=str, help='directory to save outputs')
    parser.add_argument('--val', action='store_true', help='True if performing validation (i.e. not using test data)')

    args = parser.parse_args()
    model = args.model_class

    command_str = """python train_model.py --model_class {model_class}
                                           --data_dir {data_dir}
                                           --label {label}
                                           --output_dir {output_dir}
                                           --val {val}
                  """
    command_str = command_str.format(model_class=args.model_class,
                                     data_dir=args.data_dir,
                                     label=args.label,
                                     output_dir=args.output_dir,
                                     val=args.val == True)
    print(command_str)

    # features = args.feature_types
    output_path = args.output_dir
    val_flag = args.val

    if args.val and model == None:
        print("No model entered.")
        exit()

    if not args.val and args.label == "":
        print("If testing must specify which antibiotic(s)")

    TAB = "_validation" if val_flag else "_test"

    os.makedirs(output_path, exist_ok=True)

    print("Using MODEL: ", model)
    
    print("Loading data...")
    
    if val_flag:
        X_train = load_npz(os.path.join(args.data_dir, 'training_examples_round_validation.npz'))
        y_train = pd.read_csv(os.path.join(args.data_dir, 'training_labels_round_validation.csv'))
        y_train = y_train[args.label].values

        X_test = load_npz(os.path.join(args.data_dir, 'test_examples_round_validation.npz'))
        y_test_df = pd.read_csv(os.path.join(args.data_dir, 'test_labels_round_validation.csv'))
        y_test = y_test_df[args.label].values
    else:
        X_train = load_npz(os.path.join(args.data_dir, 'training_examples_round_testing.npz'))
        y_train = pd.read_csv(os.path.join(args.data_dir, 'training_labels_round_testing.csv'))
        y_train = y_train[args.label].values

        X_test = load_npz(os.path.join(args.data_dir, 'test_examples_round_testing.npz'))
        y_test_df = pd.read_csv(os.path.join(args.data_dir, 'test_labels_round_testing.csv'))
        y_test = y_test_df[args.label].values
        
    print("Starting training...")
    if args.val: # then we manually specify model type

        if model == "ridge":
            clf, predict, roc, clf_opt = ridge(X_train, y_train, X_test, y_test)
        elif model == "lasso":
            clf, predict, roc, clf_opt = lasso(X_train,y_train, X_test, y_test) 
        elif model == "elastic_net":
            clf, predict, roc, clf_opt = elastic_net(X_train, y_train, X_test, y_test)
        elif model == "random_forest":
            clf, predict, roc, clf_opt = random_forest(X_train, y_train, X_test, y_test)
        elif model == "lightgbm":
            clf, predict, roc, clf_opt = lightgbm(X_train, y_train, X_test, y_test)
        else:
            print("Model not recognized!")
    else: # otherwise we use the best model class from validation experiment

        path = '/home/conorcorbin/repos/er_infection/results/ast_models/validation/{model}/{abx}' # hardcoded
        best_auroc = 0.0
        best_model_class = None
        for model in ['lasso', 'ridge', 'lightgbm', 'random_forest']:
            auroc_path = os.path.join(path.format(model=model, abx=args.label), 'auroc.txt')
            with open(auroc_path, 'r') as f:
                auroc = float(f.read())
                print("Model: {model} Val AUROC:{auc}".format(model=model,auc=str(auroc)))
            if auroc > best_auroc:
                best_model_class = model
                best_auroc = auroc
        print("Best Model: {model}".format(model=best_model_class))
        model = best_model_class
        if model == "ridge":
            clf, predict, roc, clf_opt = ridge(X_train, y_train, X_test, y_test)
        elif model == "lasso":
            clf, predict, roc, clf_opt = lasso(X_train,y_train, X_test, y_test) 
        elif model == "elastic_net":
            clf, predict, roc, clf_opt = elastic_net(X_train, y_train, X_test, y_test)
        elif model == "random_forest":
            clf, predict, roc, clf_opt = random_forest(X_train, y_train, X_test, y_test)
        elif model == "lightgbm":
            clf, predict, roc, clf_opt = lightgbm(X_train, y_train, X_test, y_test)
        else:  
            print("Model not recognized!")


    print("%s AUROC %s: " % (model, roc))
    # Write AUROC to file so we can read it in later if this is val
    f_auroc = os.path.join(output_path, 'auroc.txt')
    with open(f_auroc, 'w') as w:
        w.write(str(round(roc, 5)))

    # Write optimal hyerparameters to file
    f_params = os.path.join(output_path, '%s_best_params.json' % model)
    with open(f_params, 'w') as w:
        json.dump(clf_opt, w) 

    ## Save predictions
    print("Saving predictions to: " + output_path + "/%s_predictions.csv" % model)
    y_test_df["label"] = y_test
    y_test_df["predictions"] = predict
    y_test_df.to_csv(os.path.join(output_path, "%s_predictions.csv" % model))

    # If testing, save top 50 features
    if model in ['ridge', 'lasso']:
        # use coeff parameter and sort by absolute value to get top features
        inds = [i for i in range(len(clf.coef_))]
        feature_imps = [abs(c) for c in clf.coef_]
    else:
        inds = [i for i in range(len(clf.feature_importances_))]
        feature_imps = clf.feature_importances_
    df_features = pd.DataFrame()
    df_features['feature_indices'] = inds
    df_features['feature_importances'] = feature_imps
    df_features_top_50 = (df_features
        .sort_values('feature_importances', ascending=False)
        .head(50)
    )
    print("Saving feature importances to: " + output_path + "/%s_feature_importances.csv" % model)
    df_features_top_50.to_csv(os.path.join(output_path, "%s_feature_importances.csv" % model), index=None)


if __name__ == "__main__":
    main()
