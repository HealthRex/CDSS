import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import scipy
import os
import numpy as np
from sklearn.externals import joblib
import pdb

up_to_year = 2014

def fit_baseline_models(x_train, labels_train,
                        x_test, labels_test):
    """
    Fits first pass random forest models to each drug combo
    No hyperparamter tuning (trees == 100, features = sqrt)
    Prints AUROC with CIs
    Saves y_hats and trained model to output directory 
    """

    drugs = ['cefazolin', 'ceftriaxone', 'cefepime',
             'piptazo', 'vancomycin', 'meropenem',
             'vanc_meropenem', 'vanc_piptazo',
             'vanc_cefepime', 'vanc_ceftriaxone']
    

    for drug in drugs:
        
        out_dir = './baseline_models/'
        y_train = labels_train[drug]
        y_test = labels_test[drug]

        rf = RandomForestClassifier(n_estimators=1000, random_state=42)
        rf.fit(x_train, y_train)
    
        predictions = rf.predict_proba(x_test)
        auroc = roc_auc_score(y_test, predictions[:, 1])
        
        out_dir = os.path.join(out_dir, drug)
        os.makedirs(out_dir, exist_ok=True)

        np.savetxt(os.path.join(out_dir, "predictions.csv"), predictions, delimiter=",")
        joblib.dump(rf, os.path.join(out_dir, 'model.pkl')) 
        
        p_res = 1 - float(labels_small[drug].sum())/len(labels_small[drug])
        print(drug)
        print("Percent Resistant %.4f" % p_res)
        print("AUROC: %.2f" % auroc)


if __name__ == '__main__':
    labels = pd.read_csv('./data/labels.csv')
    labels_small = labels[labels['year'] < up_to_year]

    # Load in feature matrix, pivot, and join
    features = pd.read_csv('./data/feature_matrix.csv')
    features = features.pivot(index='pat_enc_csn_id_coded',
                              columns='features',
                              values='values').fillna(0.0).reset_index()
    data = pd.merge(labels_small,
                    features,
                    on='pat_enc_csn_id_coded',
                    how='left')

    data = data.drop(['pat_enc_csn_id_coded',
                      'jc_uid',
                      'med',
                      'order_time_jittered_utc',
                      'med_sens',
                      'organism'], axis=1)

    data_train = data[data['year'] < 2013]
    data_test = data[data['year'] == 2013]

    labels_train = data_train[['cefazolin', 'ceftriaxone', 'cefepime',
                               'piptazo', 'vancomycin', 'meropenem',
                               'vanc_meropenem', 'vanc_piptazo',
                               'vanc_cefepime', 'vanc_ceftriaxone']]

    labels_test = data_test[['cefazolin', 'ceftriaxone', 'cefepime',
                             'piptazo', 'vancomycin', 'meropenem',
                             'vanc_meropenem', 'vanc_piptazo',
                             'vanc_cefepime', 'vanc_ceftriaxone']]

    data_train = data_train.drop(['cefazolin', 'ceftriaxone', 'cefepime',
                               'piptazo', 'vancomycin', 'meropenem',
                               'vanc_meropenem', 'vanc_piptazo',
                               'vanc_cefepime', 'vanc_ceftriaxone'], axis=1)

    data_test = data_test.drop(['cefazolin', 'ceftriaxone', 'cefepime',
                                'piptazo', 'vancomycin', 'meropenem',
                                'vanc_meropenem', 'vanc_piptazo',
                                'vanc_cefepime', 'vanc_ceftriaxone'], axis=1)

    data_train = scipy.sparse.csr_matrix(data_train.values)
    data_test = scipy.sparse.csr_matrix(data_test.values)

    pdb.set_trace()
    fit_baseline_models(data_train, labels_train,
                        data_test, labels_test)


