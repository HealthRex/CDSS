# -*- coding: utf-8 -*-
import os
import os.path as osp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from organize_feats import explore_diag, clean_base_cohort, get_proc_labels

# TODO: remove absolute paths
data_dir = '/Users/laubravo/Documents/Rotation_Project/project/data/data_v1'

base_cohort =  pd.read_csv(osp.join(data_dir, 'baseCohort.csv'))
proc_t2 = pd.read_csv(osp.join(data_dir, 'orderedProceduresT2.csv'))
diag_t2 = pd.read_csv(osp.join(data_dir, 'diagnosisT2.csv'))

# TODO: calculate recall for gold_standard

def get_gold_standard(base_cohort, diag_t2, proc_t2):
    base_cohort = clean_base_cohort(base_cohort)
    # find the most common diagnosis at t2
    diag_codes, topn_diag = explore_diag(diag_t2, "", topn=5)
    # for each diag in t2 find the most common ordered procedures
    diag = base_cohort.merge(topn_diag, how='inner', on=['anon_id'])
    proc = base_cohort.merge(proc_t2, how='inner', on=['anon_id'])
    proc = proc.merge(diag, how='inner', on=['anon_id', 'referralOrderDateTime',
    'referringEncounterId', 'specialtyEncounterDateTime', 'specialtyEncounterId'])
    gold_standard = {code: get_proc_labels(proc[proc['cssr_code'] == code], topn_for_labs=10, topn_for_imgs=5) for code in diag_codes}
    return gold_standard

if __name__ == "__main__":
    get_gold_standard(base_cohort, diag_t2, proc_t2)