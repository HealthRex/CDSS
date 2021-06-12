import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score

import sys, argparse, os, json
sys.path.insert(1, '/Users/conorcorbin/repos/CDSS/scripts/ER_Infection/notebooks/modeling/')
from train_model import (
    ridge, lasso,
    lightgbm, random_forest
)

import pdb

def gbm(X_train, y_train, X_test, y_test):
    """
    Trains a gbm with standard hyperparamters and returns AUROC on test set. 
    Uses test set for model selection
    """

    grid = {'learning_rate' : [0.01, 0.05, 0.1, 0.5],
            'num_leaves' : [2, 8, 16, 32, 64]
    }

    # Instantiate GBM
    gbm = lgb.LGBMClassifier(objective='binary',
                             n_estimators=1000,
                             learning_rate=0.1,
                             num_leaves=2)

    
    # Fit model with early stopping
    gbm.fit(X_train,
            y_train,
            eval_set= [(X_test, y_test)],
            eval_metric = 'binary',
            early_stopping_rounds = 20,
            verbose=False)
    
    boosting_rounds = gbm.best_iteration_
    preds = gbm.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    print(f"Num Boosting Rounds: {boosting_rounds} AUC: {round(auc, 2)}")
    return gbm, preds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_class', default=None,
                        type=str,
                        help='ridge/lasso/lightgbm/random_forest/ffnn')
    parser.add_argument('--label', default="NIT",
                        type=str,
                        help='NIT SXT CIP LVX')
    parser.add_argument('--output_path', default="",
                        type=str,
                        help='directory to save outputs')
    args = parser.parse_args()

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
    # df_train = df_train.sample(n=1000).reset_index(drop=True)

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
    f_auroc = os.path.join(args.output_path, 'auroc.txt')
    with open(f_auroc, 'w') as w:
        w.write(str(round(roc, 5)))

    # Write optimal hyerparameters to file
    f_params = os.path.join(args.output_path, f'{args.model_class}_best_params.json')
    with open(f_params, 'w') as w:
        json.dump(params, w) 

    ## Save predictions
    df_yhats = pd.DataFrame(data={
        'label' : y_test,
        'predictions' : predictions
    })
    df_yhats.to_csv(
        os.path.join(args.output_path, f"{args.model_class}_predictions.csv")
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
        os.path.join(args.output_path, f"{args.model_class}_feature_importances.csv"),
        index=None
    )


if __name__ == '__main__':
    main()
 

