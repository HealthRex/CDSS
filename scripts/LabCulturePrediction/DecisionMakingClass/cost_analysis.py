import pandas as pd
import numpy as np
import os
from sklearn.metrics import roc_auc_score
from random import random

from UtilityModel import UtilityModel

import pdb

test_year = 2013


def read_model_outputs(data, model_dir):
    """ Read in coverage predictions output by each of our models
        and attaches them to dataframe appropriately. 
    """
    drugs = ['cefazolin', 'ceftriaxone', 'cefepime',
             'piptazo', 'vancomycin', 'meropenem',
             'vanc_meropenem', 'vanc_piptazo',
             'vanc_cefepime', 'vanc_ceftriaxone']

    for drug in drugs:
        prediction_file = os.path.join(model_dir, drug, 'predictions.csv')
        with open(prediction_file, 'r') as f:
            data['p_of_c_' + drug] = np.array([float(prob.split(',')[1].rstrip()) + random() / 1000
                                                     for prob in f])
    return data

def sanity_check_aurocs(data):
    """ Once we've attached model probabilites, generate aurocs
        and make sure they are the same as what we got before """

    drugs = ['cefazolin', 'ceftriaxone', 'cefepime',
             'piptazo', 'vancomycin', 'meropenem',
             'vanc_meropenem', 'vanc_piptazo',
             'vanc_cefepime', 'vanc_ceftriaxone']

    for drug in drugs:
        labels = data[drug]
        predictions = data['p_of_c_' + drug]
        auroc = roc_auc_score(labels, predictions)
        print(drug)
        print(auroc)

def _assume_med_orders(meds):
    if meds == 'piperacillin-tazobactam vancomycin levofloxacin':
        return "vancomycin piperacillin-tazobactam"
    if meds == 'ceftriaxone vancomycin piperacillin-tazobactam': 
        return "vancomycin piperacillin-tazobactam"
    if meds == 'vancomycin cefepime levofloxacin':
        return 'vancomycin cefepime'
    if meds == 'ceftriaxone piperacillin-tazobactam':
        return 'piperacillin-tazobactam'
    if meds == 'vancomycin ciprofloxacin piperacillin-tazobactam':
        return 'vancomycin piperacillin-tazobactam'
    
    return meds

def _filter_admits_by_med_orders(data):
    data['med'] = data['med'].apply(lambda x: _assume_med_orders(x))
    data = data[(data['med'] == 'ceftriaxone') | \
                (data['med'] == 'vancomycin piperacillin-tazobactam') | \
                (data['med'] == 'piperacillin-tazobactam') | \
                (data['med'] == 'vancomycin') | \
                (data['med'] == 'vancomycin cefepime') | \
                (data['med'] == 'ceftriaxone vancomycin') | \
                (data['med'] == 'cefepime') | \
                (data['med'] == 'cefazolin') | \
                (data['med'] == 'vancomycin meropenem') | \
                (data['med'] == 'meropenem')]
    return data
    

def filter_encounters_by_med_order(data):
    """ We only want to analyze patient encounters where one of the ten forms 
        of empiric treatment are actually administered. We will also make some
        assumptions to reassign drug orders for example ceftriaxone, pip tazo 
        and vancomycin order we'll assume was physician orginally going on ceftriaxone
        and immediatley upping to zosyn. Refers to two helper functions provided above.
    """
    original_number_of_encounters = len(data)
    data = data[(data['med'].str.contains('cefazolin')) | \
                (data['med'].str.contains('ceftriaxone')) | \
                (data['med'].str.contains('cefepime')) | \
                (data['med'].str.contains('piperacillin-tazobactam')) | \
                (data['med'].str.contains('vancomycin')) | \
                (data['med'].str.contains('meropenem'))]

    data = _filter_admits_by_med_orders(data)
    new_number_of_encounters = len(data)

    print("Originally had %d encounters" % original_number_of_encounters)
    print("Now have %d encounters" % new_number_of_encounters)

    return data

def compute_clin_covered_flag(x):
    """ Returns flag as to whether patient was covered adequately """
    meds = x.med.split()
    covered = 0
    for med in meds:
        if med == 'cefazolin':
            if x.cefazolin == 1:
                covered = 1
        elif med == 'ceftriaxone':
            if x.ceftriaxone == 1:
                covered = 1
        elif med == 'cefepime':
            if x.cefepime == 1:
                covered = 1
        elif med == 'piperacillin-tazobactam':
            if x.piptazo == 1:
                covered = 1
        elif med == 'vancomycin':
            if x.vancomycin == 1:
                covered = 1
        elif med == 'meropenem':
            if x.meropenem == 1:
                covered = 1
    return covered

def compute_alg_covered_flag(x):
    meds = x.alg_meds.split()
    covered = 0
    for med in meds:
        if med == 'cefazolin':
            if x.cefazolin == 1:
                covered = 1
        elif med == 'ceftriaxone':
            if x.ceftriaxone == 1:
                covered = 1
        elif med == 'cefepime':
            if x.cefepime == 1:
                covered = 1
        elif med == 'piperacillin-tazobactam':
            if x.piptazo == 1:
                covered = 1
        elif med == 'vancomycin':
            if x.vancomycin == 1:
                covered = 1
        elif med == 'meropenem':
            if x.meropenem == 1:
                covered = 1
    return covered

if __name__ == '__main__':

    data = pd.read_csv("./data/labels.csv")
    data_unchanged = data
    data = data[data['year'] == test_year]
    data = read_model_outputs(data, './baseline_models')
    data['med'] = data['med'].apply(lambda x: x.lower()) 

    # Filter encounters by what meds were ordered
    data = filter_encounters_by_med_order(data)

    # Get Flag For Whether patients were adequately covered 
    data['clin_covered'] = data.apply(compute_clin_covered_flag, axis=1)

    data = data.head(18)
    umodel = UtilityModel(data=data,
                          C_meropenem = 0,
                          C_vancomycin= 0,
                          C_piptazo= 0,
                          C_cefepime= 0,
                          C_ceftriaxone= 0,
                          C_cefazolin= 0)
    data['alg_meds'] = data.apply(umodel.compute_best_action, axis=1)

    # Get Flag for Whether alg covered pateints adequately 
    data['alg_covered'] = data.apply(compute_alg_covered_flag, axis=1)
    
    umodel.fit_drug_parameters()