import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pulp import *
import os, glob
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, StratifiedKFold


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/conorcorbin/.config/gcloud/application_default_credentials.json' 
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101' 

from google.cloud import bigquery
client=bigquery.Client()

import pdb

abx_options = ["Vancomycin",
                "Ampicillin",
                "Cefazolin",
                "Ceftriaxone",
                "Cefepime",
                "Zosyn",
                "Ciprofloxacin",
                "Meropenem",
                "Vancomycin_Meropenem",
                "Vancomycin_Zosyn",
                "Vancomycin_Cefepime",
                "Vancomycin_Ceftriaxone"
                ]

abx_map = {'Ceftriaxone' : "CEFTRIAXONE",
           'Vancomycin_Zosyn' : "PIPERACILLIN-TAZOBACTAM VANCOMYCIN",
           'Zosyn' : "PIPERACILLIN-TAZOBACTAM",
           'Vancomycin_Ceftriaxone' : "CEFTRIAXONE VANCOMYCIN",
           'Vancomycin_Cefepime' : "CEFEPIME VANCOMYCIN",
           'Cefepime' : "CEFEPIME",
           'Vancomycin' :  "VANCOMYCIN",
           'Meropenem' : "MEROPENEM",
           'Vancomycin_Meropenem' : "MEROPENEM VANCOMYCIN",
           'Cefazolin' : "CEFAZOLIN",
           'Ciprofloxacin' : "CIPROFLOXACIN",
           'Ampicillin' : 'AMPICILLIN'
          }
abx_map_inverse = {abx_map[key] : key for key in abx_map}
abx_map_inverse['CEFTRIAXONE PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Zosyn'
# abx_map_inverse['LEVOFLOXACIN PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Zosyn'
abx_map_inverse['AZITHROMYCIN PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Zosyn'
# abx_map_inverse['MEROPENEM PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Meropenem'
abx_map_inverse['AZITHROMYCIN CEFTRIAXONE'] = 'Ceftriaxone'



from sklearn.base import BaseEstimator

class IdentityEstimator(LogisticRegression):
    def __init__(self):
        LogisticRegression.__init__(self)
            
    def predict_proba(self, input_array):   
        return input_array*1

    def decision_function(self, input_array):
        return input_array*1


def load_predictions():
    """Helper function that loads predictions from AST classifiers for test set data"""
    
    base_path="/Users/conorcorbin/repos/er_infection/results/ast_models/testing/{abx}"
    df = pd.DataFrame()
    for i, abx in enumerate(abx_options):
        path = base_path.format(abx=abx)
        f_path = glob.glob(os.path.join(path, '*predictions.csv'))[0]
        if i == 0:
            df = pd.read_csv(f_path)
            df = df[['anon_id', 'pat_enc_csn_id_coded', 'label', 'predictions']]
            df = df.rename(columns={'label' : '%s_label' % abx,
                                    'predictions' : '%s_predictions' % abx})
        else:
            df_preds = pd.read_csv(f_path)
            df_preds = df_preds[['anon_id', 'pat_enc_csn_id_coded', 'label', 'predictions']]
            df_preds = df_preds.rename(columns={'label' : '%s_label' % abx,
                                                'predictions' : '%s_predictions' % abx})
            df = df.merge(df_preds, how='left', on=['anon_id', 'pat_enc_csn_id_coded'])
    
    return df

def simulate_improved_auroc(df, auroc_floor):
    """
    Takes in the predictions dataframe and uses the labels to simualate improved auroc. Loops through negative
    label predicted probabilites and iteratively swaps them with positive label probability if the postive
    label probability is lower than the negative label probability. Does this until desired auroc is reached.   
    """
    for abx in abx_options:
        predictions = df['%s_predictions' % abx].values
        labels = df['%s_label' % abx]
        auc = roc_auc_score(labels, predictions)

        if auc >= auroc_floor:
            continue

        neg_inds = [i for i in range(len(labels)) if labels[i] == 0]
        pos_inds = [i for i in range(len(labels)) if labels[i] == 1]
        for n_ind in neg_inds: 
            # find a positive ind that is ranked lower than neg ind and flip probabilities
            for p_ind in pos_inds:
                if predictions[n_ind] > predictions[p_ind]:
                    temp = predictions[n_ind]
                    predictions[n_ind] = predictions[p_ind]
                    predictions[p_ind] = temp

            auc = roc_auc_score(labels, predictions)
            if auc >= auroc_floor:
                df['%s_predictions' % abx] = predictions
                break
    return df


def calibrate_probabilities(df):
    """ 
    Takes in test set probabilites and does a k-fold cross fitting procedure to recalibrate each model
    """
    est = IdentityEstimator()
    for abx in abx_options:

        X = df['%s_predictions' % abx].values.reshape(-1, 1)
        y = df['%s_label' % abx]
        isotonic_calibrated_predictions = np.array([float(i) for i in range(len(y))])
        sigmoid_calibrated_predictions = np.array([float(i) for i in range(len(y))])

        # Fit base estimator
        est.fit(X, y) # because we've overloaded predict_proba and decision function this doesn't matter

        # Calibrated with isotonic calibration
        isotonic = CalibratedClassifierCV(est, cv='prefit', method='isotonic')

        # Calibrated with sigmoid calibration
        sigmoid = CalibratedClassifierCV(est, cv='prefit', method='sigmoid')

        cv = StratifiedKFold(n_splits=10)
        for train_inds, val_inds in cv.split(X, y):
            X_train, y_train = X[train_inds], y[train_inds]
            X_val, y_val = X[val_inds], y[val_inds]
            isotonic.fit(X_train, y_train)
            isotonic_predictions = isotonic.predict_proba(X_val)
            isotonic_calibrated_predictions[val_inds] = isotonic_predictions[:, 1]

            sigmoid.fit(X_train, y_train)
            sigmoid_predictions = sigmoid.predict_proba(X_val)
            sigmoid_calibrated_predictions[val_inds] = sigmoid_predictions[:, 1]


        df['%s_predictions_isotonic' % abx] = isotonic_calibrated_predictions
        df['%s_predictions_sigmoid' % abx] = sigmoid_calibrated_predictions
    
    return df


def get_calibration_plots(df):
    """ Plots a 4x3 subplot of calibration curves """ 
    fig, ax = plt.subplots(4, 3, figsize=(24, 32))
    row, col = 0, 0
    df = calibrate_probabilities(df)

    for abx in abx_options:
        ax[row, col].plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        for name in ['', '_isotonic', '_sigmoid']:

            prob_pos = df['%s_predictions%s' % (abx, name)]
            clf_score = brier_score_loss(df['%s_label' % abx], prob_pos)
            print("%s:" % name)
            print("\tBrier: %1.3f" % (clf_score))

            fraction_of_positives, mean_predicted_value = \
                calibration_curve(df['%s_label' % abx], prob_pos, n_bins=10)

            ax[row, col].plot(mean_predicted_value, fraction_of_positives, "s-",
                    label="%s (%1.3f)" % (name, clf_score))

        
        ax[row, col].set_ylabel("Fraction of positives")
        ax[row, col].set_ylim([-0.05, 1.05])
        ax[row, col].legend(loc="lower right")
        ax[row, col].set_title('Calibration plots  (reliability curve)')

        if col == 2:
            col = 0
            row +=1
        else:
            col += 1


    plt.tight_layout()

    plt.savefig('./test2.jpg')

def get_clinician_prescribing_patterns():
    """
    Queries med orders actually administered to each patient and filters for CSNs where
    only abx regimens in our abx_options list were administered
    """

    query = """
    SELECT
        om.anon_id, om.pat_enc_csn_id_coded, om.order_med_id_coded, l.index_time, om.med_description,
        l.Ampicillin, l.Ciprofloxacin, l.Cefazolin, l.Ceftriaxone, l.Cefepime, l.Zosyn, l.Vancomycin,
        l.Meropenem, l.Vancomycin_Meropenem, l.Vancomycin_Zosyn, l.Vancomycin_Cefepime, l.Vancomycin_Ceftriaxone
    FROM
        `mining-clinical-decisions.abx.abx_orders_given_and_stopped` om
    INNER JOIN 
        `mining-clinical-decisions.abx.final_ast_labels` l
    USING
        (pat_enc_csn_id_coded)
    WHERE
        om.was_given = 1
    ORDER BY 
        om.anon_id, om.pat_enc_csn_id_coded, om.order_time
    """
    query_job = client.query(query)
    df_abx = query_job.result().to_dataframe()
    df_abx.head()

    # Lambda that aggregate Antibiotic orders after we've grouped by CSN
    concat_abx = lambda x : ' '.join(np.unique(sorted([a for a in x])))

    # Aggregate abx orders
    df_drugs = (df_abx
        .assign(med_description=lambda x: [a.split(' ')[0] for a in x.med_description]) # Only Take first word (abx)
        .assign(med_description=lambda x: [(a.replace('PIPERACILLIN-TAZOBACTAM-DEXTRS','PIPERACILLIN-TAZOBACTAM')
                                            .replace('VANCOMYCIN-WATER', 'VANCOMYCIN'))
                                        for a in x.med_description])
        .assign(year=lambda x: x.index_time.dt.year) # get year of each CSN - used to filter later on
        .groupby('pat_enc_csn_id_coded')
        .agg({'med_description' : concat_abx,
            'year' : 'first',
            'Ampicillin' : 'first',
            'Ciprofloxacin' : 'first',
            'Cefazolin' : 'first',
            'Ceftriaxone' : 'first',
            'Cefepime' : 'first',
            'Zosyn' : 'first',
            'Vancomycin' : 'first',
            'Meropenem' : 'first',
            'Vancomycin_Ceftriaxone' : 'first',
            'Vancomycin_Cefepime' : 'first',
            'Vancomycin_Zosyn' : 'first',
            'Vancomycin_Meropenem' : 'first'})
        .reset_index()
        # Only look at test set data and CSNs where allowed antibiotic selection was administered
        .query("year == 2019 and med_description in @abx_map_inverse", engine='python') 
        .assign(med_description=lambda x: [abx_map_inverse[a] for a in x.med_description])
    )

    # Roughly 700 of the 1300 original CSNs in the test set
    return df_drugs


def get_optimized_abx_selections(df, calibration=None):

    # Predictions string
    if calibration == None:
        predictions_string = '%s_predictions'
    else:
        predictions_string = '%s_predictions_isotonic'
    
    abx_model = LpProblem("Antibiotics", LpMaximize)

    # Create binary indicators for whether treatment is used
    drug_inds = {}
    for abx in abx_options:
        drug_inds[abx] = [LpVariable('%s_%d' % (abx, i), lowBound=0, upBound=1, cat='Binary')
                        for i in range(len(df))]

    # Add objective function to model
    per_csn_sum = []
    for i in range(len(df)):
        _sum = 0
        for abx in abx_options:
            _sum += drug_inds[abx][i] * df[predictions_string % abx].values[i]
        per_csn_sum.append(_sum)
        
    abx_model += lpSum(per_csn_sum)

    # Add one selection constraint
    for i in range(len(df)):
        selections = []
        for abx in abx_options:
            selections.append(drug_inds[abx][i])
        abx_model += lpSum(selections) == 1

    # Add max assignment constraints
    abx_assignment_constraints = {"Vancomycin" : 13,
                                "Ampicillin" : 0,
                                "Cefazolin" : 8,
                                "Ceftriaxone" : 367,
                                "Cefepime" : 14,
                                "Zosyn" : 102,
                                "Ciprofloxacin" : 8,
                                "Meropenem" : 9,
                                "Vancomycin_Meropenem" : 9,
                                "Vancomycin_Zosyn" :  113,
                                "Vancomycin_Cefepime" : 23,
                                "Vancomycin_Ceftriaxone" : 31
                                }

    for drug in drug_inds:
        abx_model += lpSum([drug_inds[drug][i] for i in range(len(df))]) == abx_assignment_constraints[drug]

    # Solve model
    abx_model.solve()
    # print("Status:", LpStatus[abx_model.status])

    # Save selected antibiotic to df
    abx_decisions = []
    for i in range(len(df)):
        abx_decision = None
        for abx in abx_options:
            if drug_inds[abx][i].value() == 1:
                abx_decision = abx_map[abx]
        assert abx_decision is not None
        abx_decisions.append(abx_decision)
    df['IP_med_description'] = abx_decisions

    return df

# Ugly helper function that just does some string mapping
def compute_was_covered(x, decision_column='med_description'):
    """
    Given med description, find appropriate label column and return whether patient was covered during CSN
    Returns "Not in abx options" if abx regimen isn't in our set of 12 options - useful for filtering later
    """
    if decision_column == 'med_description':
        med_description = x.med_description
    elif decision_column == 'random_med_description':
        med_description = x.random_med_description
    elif decision_column == 'IP_med_description':
        med_description = x.IP_med_description

    return x[med_description]
        
    # if med_description == "CEFTRIAXONE":
    #     return x.Ceftriaxone
    # elif med_description == "PIPERACILLIN-TAZOBACTAM VANCOMYCIN":
    #     return x.Vancomycin_Zosyn
    # elif med_description == "PIPERACILLIN-TAZOBACTAM":
    #     return x.Zosyn
    # elif med_description == "CEFTRIAXONE VANCOMYCIN":
    #     return x.Vancomycin_Ceftriaxone
    # elif med_description == "CEFEPIME VANCOMYCIN":
    #     return x.Vancomycin_Cefepime
    # elif med_description == "CEFEPIME":
    #     return x.Cefepime
    # elif med_description == "VANCOMYCIN":
    #     return x.Vancomycin
    # elif med_description == "MEROPENEM":
    #     return x.Meropenem
    # elif med_description == "MEROPENEM VANCOMYCIN":
    #     return x.Vancomycin_Meropenem
    # elif med_description == "CEFAZOLIN":
    #     return x.Cefazolin
    # elif med_description == "CIPROFLOXACIN":
    #     return x.Ciprofloxacin
    # elif med_description == "AMPICILLIN":
    #     return x.Ampicillin
    # else:
    #     return "Not in abx options"

def get_coverage_rates(df):
    """
    Create flag for whether clinicians covered the patient during the csn, whether a random assignemnt
    covered patient CSN, and whether optimized assignment covered the patient CSN
    """

    df = (df
        .assign(random_med_description=lambda x: np.random.choice(x.med_description, size=len(x.med_description), replace=False))
    )
    df = (df
        .assign(was_covered_dr=df.apply(lambda x: compute_was_covered(x), axis=1))
        .assign(was_covered_random=df.apply(lambda x: compute_was_covered(x, 
                                            decision_column='random_med_description'),
                                            axis=1))
        .assign(was_covered_IP=df.apply(lambda x: compute_was_covered(x, 
                                        decision_column='IP_med_description'),
                                        axis=1))
    )

    clin_covered_rate = df['was_covered_dr'].sum() / len(df)
    random_covered_rate = df['was_covered_random'].sum() / len(df)
    ip_covered_rate = df['was_covered_IP'].sum() / len(df)

    # print(random_covered_rate)
    # print(clin_covered_rate)
    # print(ip_covered_rate)

    return random_covered_rate, clin_covered_rate, ip_covered_rate

def main():
    from tqdm import tqdm
    df_drugs = get_clinician_prescribing_patterns()
    ip_covered_rates, ip_covered_rates_isotonic = [], []
    for i in tqdm(range(62, 100, 1)):
        df = load_predictions()
        auc = float(i) / 100
    # get_calibration_plots(df) 
        df = simulate_improved_auroc(df, auroc_floor=auc)
        df = calibrate_probabilities(df)    
        df = (df
            .merge(df_drugs, how='inner', on='pat_enc_csn_id_coded')
        )

        # Uncalibrated predictions
        df = get_optimized_abx_selections(df)
        random_covered_rate, clin_covered_rate, ip_covered_rate = get_coverage_rates(df)
        ip_covered_rates.append(ip_covered_rate)
        
        # Calibrated predictions
        df = get_optimized_abx_selections(df, calibration='isotonic')
        random_covered_rate, clin_covered_rate, ip_covered_rate = get_coverage_rates(df)
        ip_covered_rates_isotonic.append(ip_covered_rate)

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    plt.plot([i for i in range(62, 100, 1)], ip_covered_rates, label='IP Selections')
    plt.plot([i for i in range(62, 100, 1)], ip_covered_rates_isotonic, label='IP Selections Isotonic Calib')
    plt.plot([i for i in range(62, 100, 1)], [clin_covered_rate for i in range(62, 100, 1)], label='Clin Covered Rate')
    plt.plot([i for i in range(62, 100, 1)], [random_covered_rate for i in range(62, 100, 1)], label='Random Covered Rate')
    plt.legend()
    plt.savefig('./simulated_auroc_improvement_2.jpg')

if __name__ == '__main__':
    main()