import pandas as pd
import numpy as np
import os
from sklearn.metrics import roc_auc_score
from random import random, randint

from UtilityModel import UtilityModel

import pdb

test_year = 2013


def read_model_outputs(data, model_dir):
    """ Read in coverage predictions output by each of our models
        and attaches them to dataframe appropriately. 
    """
    drugs = ['ceftriaxone', 'cefepime',
             'piptazo', 'vancomycin', 'meropenem',
             'vanc_meropenem', 'vanc_piptazo',
             'vanc_cefepime', 'vanc_ceftriaxone']

    for drug in drugs:
        prediction_file = os.path.join(model_dir, drug, 'predictions.csv')
        with open(prediction_file, 'r') as f:
            data['p_of_c_' + drug] = np.array([float(prob.split(',')[1].rstrip())  +  random() / 1000
                                                     for prob in f])
    # 
    return data

def sanity_check_aurocs(data):
    """ Once we've attached model probabilites, generate aurocs
        and make sure they are the same as what we got before """

    drugs = ['ceftriaxone', 'cefepime',
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
    data = data[(data['med'].str.contains('ceftriaxone')) | \
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
        if med == 'ceftriaxone':
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
        if med == 'ceftriaxone':
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

def get_presciption_profile(data, alg=True):
    """ After medications chosen, return a dataframe that counts number of times each
        treatment given """
    if alg:
        col = 'alg_meds'
    else:
        col = 'med'
    p_profile = data.groupby(col).count()['pat_enc_csn_id_coded'].reset_index(
        ).rename(columns = {'pat_enc_csn_id_coded' : 'count'})
    return p_profile

def floor_single_drug_probabilites(data):
    """ Function that makes sure p_of_vanco never exceeds p_of_vanc_zosyn 
        and similar logic """

    def vanc_combos(x):
        min_num = np.min([x.p_of_c_vanc_piptazo, x.p_of_c_vanc_cefepime,
                          x.p_of_c_vanc_meropenem, x.p_of_c_vanc_ceftriaxone])
        if x.p_of_c_vancomycin > min_num:
            return min_num
        else:
            return x.p_of_c_vancomycin

    data['p_of_c_vancomycin'] = data.apply(vanc_combos, axis=1)
    data['p_of_c_meropenem'] = data.apply(lambda x: x.p_of_c_meropenem if x.p_of_c_meropenem <
                                x.p_of_c_vanc_meropenem else x.p_of_c_vanc_meropenem, axis=1)
    data['p_of_c_piptazo'] = data.apply(lambda x: x.p_of_c_piptazo if x.p_of_c_piptazo <
                                x.p_of_c_vanc_piptazo else x.p_of_c_vanc_piptazo, axis=1)
    data['p_of_c_ceftriaxone'] = data.apply(lambda x: x.p_of_c_ceftriaxone if x.p_of_c_ceftriaxone <
                                x.p_of_c_vanc_ceftriaxone else x.p_of_c_vanc_ceftriaxone, axis=1)
    data['p_of_c_cefepime'] = data.apply(lambda x: x.p_of_c_cefepime if x.p_of_c_cefepime <
                                x.p_of_c_vanc_cefepime else x.p_of_c_vanc_cefepime, axis=1)
    return data

if __name__ == '__main__':

    data = pd.read_csv("./data/labels.csv")
    data_unchanged = data
    data = data[data['year'] == test_year]
    data = read_model_outputs(data, './baseline_models')
    data['med'] = data['med'].apply(lambda x: x.lower()) 

    # Filter encounters by what meds were ordered
    data = filter_encounters_by_med_order(data)

    # Test this out
    # data['p_of_c_cefazolin'] = data.apply(lambda x: x.p_of_c_cefazolin if x.p_of_c_cefazolin <= \
    #                                 x.p_of_c_ceftriaxone else x.p_of_c_ceftriaxone, axis=1)
    # data['p_of_c_ceftriaxone'] = data.apply(lambda x: x.p_of_c_ceftriaxone if x.p_of_c_ceftriaxone <= \
    #                                 x.p_of_c_cefepime else x.p_of_c_cefepime, axis=1)

    # Get Flag For Whether patients were adequately covered 
    data['clin_covered'] = data.apply(compute_clin_covered_flag, axis=1)

    # data = data.head(1530)

    umodel = UtilityModel(data=data,
                          C_meropenem = -1,
                          C_vancomycin = -1,
                          C_piptazo = -1,
                          C_cefepime = -1,
                          C_ceftriaxone = 1,
                          C_cefazolin = -1,
                          C_vanc_meropenem = 0,
                          C_vanc_piptazo = -1,
                          C_vanc_cefepime = -1,
                          C_vanc_ceftriaxone = -1)

    # data = floor_single_drug_probabilites(data)

    data['alg_meds'] = data.apply(umodel.compute_best_action, axis=1)

    # Get Flag for Whether alg covered pateints adequately 
    data['alg_covered'] = data.apply(compute_alg_covered_flag, axis=1)


    # # Profile
    # alg_profile = get_presciption_profile(data)
    # clin_profile = get_presciption_profile(data, alg=False)
    # alg_profile.to_csv("./data/no_weights_profile.csv", index=None)
    # clin_profile.to_csv('./data/clin_profile.csv', index=False)

    n = {}
    n['vancomycin meropenem'] = 14
    n['vancomycin piperacillin-tazobactam'] = 513
    n['vancomycin'] = 94
    n['piperacillin-tazobactam'] = 174
    n['cefepime'] = 35
    n['ceftriaxone'] = 561
    n['cefazolin'] = 0
    n['vancomycin cefepime'] = 57
    n['vancomycin ceftriaxone'] = 45
    n['meropenem'] = 13

    data = umodel.fit_drug_parameters(n)

    with open('./data/model_util_vals.txt', 'w') as w:
        for key in umodel.drug_cost:
            w.write("%s,%.2f\n" % (key, umodel.drug_cost[key]))


    data['alg_covered'] = data.apply(compute_alg_covered_flag, axis=1)

    print("Number of mismatches %d" % len(data[data['alg_covered'] == 0]))

    