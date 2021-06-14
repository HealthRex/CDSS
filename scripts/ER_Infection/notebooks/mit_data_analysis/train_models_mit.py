import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    cross_val_predict,
    StratifiedKFold
)

import sys, argparse, os, json
from tqdm import tqdm
import pdb

def lasso(X_train, y_train, X_test, y_test):
    """
    Trains an l2 penalized logistic regression sweeping over reg strength
    Uses test set for model selection
    """
    grid = {'C' : np.logspace(-8, 8, 17)}

    best_auc = 0.5
    best_params = {key: None for key in grid}
    best_preds = None

    for c in tqdm(grid['C']):
        clf = LogisticRegression(penalty='l1', C=c, solver='liblinear')
        clf.fit(X_train, y_train)
        preds = clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, preds)
        if auc > best_auc:
            best_auc = auc
            best_params['C'] = c
            best_preds = [p for p in preds]
                
    print(f"AUC: {round(best_auc, 2)}")
    return clf, best_preds, best_auc, best_params 


def ridge(X_train, y_train, X_test, y_test):
    """
    Trains an l2 penalized logistic regression sweeping over reg strength
    Uses test set for model selection
    """
    grid = {'C' : np.logspace(-8, 8, 17)}

    best_auc = 0.5
    best_params = {key: None for key in grid}
    best_preds = None

    for c in tqdm(grid['C']):
        clf = LogisticRegression(penalty='l2', C=c)
        clf.fit(X_train, y_train)
        preds = clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, preds)
        if auc > best_auc:
            best_auc = auc
            best_params['C'] = c
            best_preds = [p for p in preds]
                
    print(f"AUC: {round(best_auc, 2)}")
    return clf, best_preds, best_auc, best_params 


def random_forest(X_train, y_train, X_test, y_test):
    """
    Trains a random forest, sweeps over a few hyperparams
    Uses test set for model selection
    """
    grid = {
        'min_samples_split' : [2, 10, 50, 100],
        'max_features' : ['sqrt', 'log2', None]
    }

    best_auc = 0.5
    best_params = {key: None for key in grid}
    best_preds = None

    for mss in tqdm(grid['min_samples_split']):
        for mf in grid['max_features']:
            clf = RandomForestClassifier(
                n_estimators=1000,
                min_samples_split=mss,
                max_features=mf
            )
            clf.fit(X_train, y_train)
            preds = clf.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, preds)
            if auc > best_auc:
                best_auc = auc
                best_params['min_samples_split'] = mss
                best_params['max_features'] = mf
                best_preds = [p for p in preds]

    print(f"AUC: {round(best_auc, 2)}")
    return clf, best_preds, best_auc, best_params 

def lightgbm(X_train, y_train, X_test, y_test):
    """
    Trains a gbm with standard hyperparamters and returns AUROC on test set. 
    Uses test set for model selection
    """

    grid = {'learning_rate' : [0.01, 0.05, 0.1, 0.5],
            'num_leaves' : [2, 8, 16, 32, 64]
    }

    best_auc = 0.5
    best_lr, best_num_leaves, best_iter = None, None, None
    best_preds = None

    for lr in tqdm(grid['learning_rate']):
        for n in grid['num_leaves']:
            # Instantiate GBM
            clf = lgb.LGBMClassifier(
                objective='binary',
                n_estimators=1000,
                learning_rate=lr,
                num_leaves=n
            )
            
            # Fit model with early stopping
            clf.fit(
                X_train,
                y_train,
                eval_set= [(X_test, y_test)],
                eval_metric = 'binary',
                early_stopping_rounds = 20,
                verbose=False
            )
            
            boosting_rounds = clf.best_iteration_
            preds = clf.predict_proba(X_test)[:, 1]
            auc = roc_auc_score(y_test, preds)

            if auc > best_auc:
                best_auc = auc
                best_lr, best_num_leaves = lr, n
                best_preds = [p for p in preds]
                best_iter = clf.best_iteration_
        
    print(f"Num Boosting Rounds: {best_iter} AUC: {round(best_auc, 2)}")
    best_params = {
        'boosting_rounds' : best_iter,
        'num_leaves' : best_num_leaves,
        'learning_rate' : best_lr
    }
    return clf, best_preds, best_auc, best_params 

def train_ensembled_model():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', default="NIT",
                        type=str,
                        help='NIT SXT CIP LVX')
    parser.add_argument('--output_path',
                        default="/Users/conorcorbin/data/mit_abx_model_results/",
                        type=str,
                        help='directory to save outputs')
    parser.add_argument('--model_classes',
                        nargs='+',
                        default=['ridge', 'lasso', 'gbm', 'random_forest'],
                        help='models to ensemble')
    args = parser.parse_args()

    df = pd.DataFrame()
    for model in args.model_classes:
        path = os.path.join(
            args.output_path, args.label, model,
            f"{model}_predictions.csv"
        )
        df_preds = pd.read_csv(path)
        df_preds = df_preds.assign(
            model=lambda x: [model for i in range(len(df_preds))],
            pred_id = lambda x: [i for i in range(len(df_preds))]
        )
        df = pd.concat([df, df_preds])
    
    df_wide = (df
        .pivot(index='pred_id', columns='model', values='predictions')
        .reset_index()
        .merge(df[['pred_id', 'label']], how='inner', on='pred_id')
        .drop_duplicates()
    )

    cv = StratifiedKFold(n_splits=10)
    clf = LogisticRegression(penalty='none')
    X, y = df_wide[args.model_classes], df_wide['label']
    predictions = cross_val_predict(clf, X, y, cv=cv, method='predict_proba')[:, 1]
    auc = roc_auc_score(y, predictions)
    print(f"{args.label} ensembled AUC: {round(auc, 3)}")

    df_ens_preds = pd.DataFrame(data={
        'labels' : y,
        'predictions' : predictions
    })

    df_ens_preds.to_csv(f"{args.label}_ensembled_preds.csv", index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_class', default=None,
                        type=str,
                        help='ridge/lasso/lightgbm/random_forest/ffnn')
    parser.add_argument('--label', default="NIT",
                        type=str,
                        help='NIT SXT CIP LVX')
    parser.add_argument('--output_path',
                        default="/Users/conorcorbin/data/mit_abx_model_results/",
                        type=str,
                        help='directory to save outputs')
    args = parser.parse_args()

    output_path = os.path.join(args.output_path, args.label, args.model_class)
    os.makedirs(output_path, exist_ok=True)
    
    df_features = pd.read_csv('./data/all_uti_features.csv')
    df_labels = pd.read_csv('./data/all_uti_resist_labels.csv')

    feature_cols = [col for col in df_features.columns 
                    if col not in ('example_id', 'is_train', 'uncomplicated')]

    df = (df_labels
        .merge(df_features, how='inner', on=['example_id', 'is_train', 'uncomplicated'])
        .query("uncomplicated == 1", engine='python')
    )

    df_train = df.query("is_train == 1", engine='python')
    df_test = df.query("is_train == 0", engine='python')

    # DEBUG
    # df_train = df_train.sample(n=500).reset_index(drop=True)

    model_dict = {
        'gbm' : lightgbm,
        'random_forest' : random_forest,
        'lasso' : lasso,
        'ridge' : ridge
    }

    X_train, y_train = df_train[feature_cols], df_train[args.label]
    X_test, y_test = df_test[feature_cols], df_test[args.label]

    clf, predictions, roc, params = model_dict[args.model_class](
        X_train.values, y_train.values,
        X_test.values, y_test.values
    )

    print("%s AUROC %s: " % (args.model_class, roc))

    # Write AUROC to file so we can read it in later if this is val
    f_auroc = os.path.join(output_path, 'auroc.txt')
    with open(f_auroc, 'w') as w:
        w.write(str(round(roc, 5)))

    # Write optimal hyerparameters to file
    f_params = os.path.join(output_path, f'{args.model_class}_best_params.json')
    with open(f_params, 'w') as w:
        json.dump(params, w) 

    ## Save predictions
    df_yhats = pd.DataFrame(data={
        'label' : y_test,
        'predictions' : predictions
    })
    df_yhats.to_csv(
        os.path.join(output_path, f"{args.model_class}_predictions.csv")
    )

    # If testing, save top 50 features
    if args.model_class in ['ridge', 'lasso']:
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
    df_features_top_50.to_csv(
        os.path.join(output_path, f"{args.model_class}_feature_importances.csv"),
        index=False
    )


if __name__ == '__main__':
    train_ensembled_model()
 

