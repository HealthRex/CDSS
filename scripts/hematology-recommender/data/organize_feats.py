# -*- coding: utf-8 -*-
import os
import os.path as osp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.core import base, groupby
from pandas.core.reshape.merge import merge

# TODO: remove absolute paths
data_dir = '/Users/laubravo/Documents/Rotation_Project/project/data/data_v1'
save_dir = '/Users/laubravo/Documents/Rotation_Project/project/data/cohort_stats'
os.makedirs(save_dir, exist_ok=True)

base_cohort =  pd.read_csv(osp.join(data_dir, 'baseCohort.csv')) # [4612 rows x 5 columns] w/ 3476 unique
demographic = pd.read_csv(osp.join(data_dir, 'demographicData.csv')) # [4575 rows x 6 columns]
meds_t1 = pd.read_csv(osp.join(data_dir, 'orderedMedsT1.csv')) # [165645 rows x 6 columns]
proc_t1 = pd.read_csv(osp.join(data_dir, 'orderedProceduresT1.csv')) # hist: [1240172 rows x 6 columns] # enc: [20230 rows x 6 columns]
diag_t1 = pd.read_csv(osp.join(data_dir, 'diagnosisT1.csv')) # [1448273 rows x 7 columns]
labs_t1 = pd.read_csv(osp.join(data_dir, 'labResultsT1.csv')) # [904939 rows x 8 columns]

proc_t2 = pd.read_csv(osp.join(data_dir, 'orderedProceduresT2.csv')) # (7179, 6)
diag_t2 = pd.read_csv(osp.join(data_dir, 'diagnosisT2.csv')) # (7246, 7)

save_hists = False


def save_demo_hists(demographic, save_path):
    fig = plt.figure()
    ax1 = plt.subplot(231); ax1.hist(demographic.gender); ax1.set_title('Gender')
    ax2 = plt.subplot(232); ax2.hist(demographic.age, bins=10); ax2.set_title('Birth Date')
    ax3 = plt.subplot(233); ax3.hist(demographic.race); ax3.set_title('Race')
    ax4 = plt.subplot(234); ax4.hist(demographic.ethnicity); ax4.set_title('Ethnicity')
    ax5 = plt.subplot(235); ax5.hist(demographic.bmi); ax5.set_title('BMI')
    fig.savefig(save_path)

def save_med_hists(meds_t1, save_path):
    fig = plt.figure()
    ax1 = plt.subplot(121); ax1.hist(meds_t1.thera_class_name, bins=len(meds_t1.thera_class_name.unique())); ax1.set_title('thera_class_name')
    plt.xticks(rotation=45, ha="right"); plt.xticks(size = 7); plt.tight_layout()
    ax2 = plt.subplot(122); ax2.hist(meds_t1.pharm_class_name,  bins=len(meds_t1.pharm_class_name.unique())); ax2.set_title('pharm_class_name')
    plt.xticks(rotation=45, ha="right"); plt.xticks(size = 7); plt.tight_layout()
    fig.savefig(save_path)

def save_diag_hists(diag_t1, save_path):
    fig, ax1 = plt.subplots()
    plt.hist(diag_t1.cssr_description, bins=len(diag_t1.cssr_description.unique())); ax1.set_title('CSSR description')
    plt.xticks(rotation=45, ha="right"); plt.xticks(size = 7); plt.tight_layout()
    fig.savefig(save_path)

def get_meds_feats(meds_df, topn=10, save_dir="hists"):
    """
    Calculate the features for medicine orders. Uses topn of the pharma and thera classes used
    to aggregate medicine (reduce granularity of features).
    """
    meds_df = filter_topn(meds_df, 'thera_class_abbr', topn=topn)
    meds_df = filter_topn(meds_df, 'pharm_class_abbr', topn=topn)
    pharm_feats = pivot_counts(meds_df, 'anon_id', 'pharm_class_abbr', na_fill=0)
    thera_feats = pivot_counts(meds_df, 'anon_id', 'thera_class_abbr', na_fill=0)
    med_feats = pharm_feats.join(thera_feats, on='anon_id', how='outer')
    if save_hists:
       save_med_hists(meds_df, osp.join(save_dir, "meds_t1_hists.png"))
    return med_feats

def get_diag_feats(diag_df, topn=10):
    """
    Calculate diagnostic features by taking topn diagnosis.
    """
    # TODO: remove no information feats ex: Medical examination/evaluation
    diag_df = filter_topn(diag_df, 'cssr_code', topn=topn)
    diag_feats = pivot_counts(diag_df, 'anon_id', 'cssr_code', na_fill=0)
    if save_hists:
        save_diag_hists(diag_df, osp.join(save_dir, "diag_t1_hists_enc_top{}.png".format(topn)))
    return diag_feats

def get_lab_feats(labs_df, topn=10):
    """
    Calculate lab results by binning according to normal and abnormal values.
    TODO: expand features by including presence/absence and bin results by low, normal, high
    """
    breakpoint()
    # TODO: update lab bining for feats
    # remove Manual Differential/Slide Review , Slide Review (LAB230, LAB327)? 
    labs_df = labs_df[~labs_df['proc_code'].isin(['LAB230', 'LAB327'])]
    # TODO: merge CBCs (LABCBCD = LAB373) and merge (LABLPDC = LABLPD)
    # labs_df.loc[labs_df['proc_code'] == 'LAB373']['proc_code'] = 'LABCBCD'
    # result_flag [nan, 'High', 'Low', 'High Panic', 'Abnormal', '*', 'Low Panic','Low Off-Scale', 'Positive', 'High Off-Scale', 'Panic']
    labs_df = labs_df[labs_df['order_type'].isin(['Lab', 'ECG', 'Lab Panel'])]
    labs_df = filter_topn(labs_df, 'proc_code', topn=topn)
    labs_df['abnormal'] = ~labs_df.result_flag.isnull()
    labs_df = labs_df.sort_values('labResultDateTime').groupby(['anon_id', 'base_name']).head(1)
    lab_feats = labs_df.pivot(index='anon_id', columns='base_name', values='abnormal').fillna(-1) #true for abnormal, false for normal, -1 for N/A
    return lab_feats

def get_proc_feats(proc_df, topn=10):
    """
    Calculate ordered procedures. Get topn for labs and non labs separately.
    """
    # keep only the proc types we're interested in
    # relevant_procs = ["Lab", "Outpatient Referral", "Imaging", "Lab Panel"]
    # proc_df[proc_df.order_type.isin relevant_procs]
    # remove all the references to referral to hematology we already know this
    proc_df = proc_df[proc_df.proc_id != 34352]
    # merge all CBC synonyms into the same code (WITH DIFF AND SLIDE REVIEW, W/O DIFF, WITH DIFFERENTIAL & SLIDE REVIEW, CBC WITH DIFFERENTIAL)
    proc_df.loc[proc_df["description"].str.contains("CBC"), "proc_id"] = 474
    proc_df.loc[proc_df["description"].str.contains("CBC"), "description"] = "CBC"
    # create feats for lab and non lab procedures
    lab_proc = proc_df[proc_df.order_type.str.contains("Lab")]
    lab_proc = filter_topn(lab_proc, 'proc_id', topn=topn)
    lab_proc = lab_proc[['anon_id', 'proc_id']]
    other_proc = proc_df[~proc_df.order_type.str.contains("Lab")]
    other_proc = filter_topn(other_proc, 'proc_id', topn=topn)
    other_proc = other_proc[['anon_id', 'proc_id']]
    all_proc = pd.merge(lab_proc, other_proc, on=['anon_id', 'proc_id'], how='outer')
    proc_feats = pivot_counts(all_proc, 'anon_id', 'proc_id', na_fill=0)
    return proc_feats

def get_demo_feats(demo_df, eth_race=False):
    """
    Calculate demographic features.
    """
    if not eth_race:
        demo_df.drop(['race', 'ethnicity'], axis=1, inplace=True)
    # change Gender column to binary
    demo_df['gender'] = (demo_df['gender'] == 'Female')
    demo_df['age'] = (pd.to_datetime(demo_df['referralOrderDateTime']) - pd.to_datetime(demo_df['birthDate']))/np.timedelta64(1,'Y')
    # remove outliers
    demo_df = remove_outliers(demo_df, 'bmi')
    demo_df = remove_outliers(demo_df, 'age')
    # normalize age so it's not such a big number
    demo_df['age'] = (demo_df['age'] - demo_df['age'].mean()) / (demo_df['age'].std())
    demo_df.drop(['birthDate'], axis=1, inplace=True)
    # take first entry for each patient
    demo_feats = demo_df.sort_values('referralOrderDateTime').groupby('anon_id').head(1)
    if save_hists:
        save_demo_hists(demo_feats, osp.join(save_dir, "demographic_hists.png"))
    return demo_feats

def explore_diag(diag_t2, save_dir, topn=5, save_fig=False):
    """
    Function for finding the topn diagnosis given by specialists at t2.
    """
    # 1672/3476 patients have diagnosis
    diag_t2 = diag_t2.sort_values('diagDate').groupby(['anon_id', 'icd10']).head(1) # remove repeated diags
    # remove diag that don't say anything [Medical examination/evaluation, Personal/family history of disease]
    unimportant_diag = ['FAC014', 'FAC021'] #FAC025? Other specified status
    diag_t2 = diag_t2[~diag_t2['cssr_code'].isin(unimportant_diag)]
    # get topn diagnosis
    topn_codes = list(diag_t2.groupby(['cssr_code']).size().sort_values(ascending=False)[:topn].to_dict().keys())
    topn_diag = diag_t2[diag_t2['cssr_code'].isin(topn_codes)]
    if save_fig:
        fig = plt.hist(topn_diag['cssr_description'])
        plt.xticks(rotation=45, ha="right"); plt.xticks(size = 9); plt.tight_layout()
        fig.savefig(osp.join(save_dir, "diag_t2_{}.png".format(topn)))
    return topn_codes, topn_diag

def get_proc_labels(proc_t2, topn_for_labs=100, topn_for_imgs=10):
    """
    Calculate labels for time t2. Use different topn for labs and images.
    """
    # remove nursing orders
    proc_t2 = proc_t2[~proc_t2['order_type'].isin(['Nursing'])]
    # 202 people (not a lot) were referred to other specialties (192) or returned to primary care (10)
    # top 5 referrals are 64/202 referrals
    # proc_t2[proc_t2['order_type'].isin(['Outpatient Referral'])].groupby(['proc_id']).size().sort_values(ascending=False)
    # proc_t2[proc_t2['proc_id'].isin([34280, 48200, 34384, 506207])].sort_values(by='description')
    # top10 labs are 1825/7179 procedures top100 labs 5254/7179
    topn_labs = proc_t2[proc_t2['order_type'] == 'Lab'].groupby('proc_id').size().sort_values(ascending=False)[:topn_for_labs].index.tolist()
    # print(proc_t2[proc_t2['proc_id'].isin(topn_labs)]['description'].unique())
    # ['LDH TOTAL, SERUM / PLASMA', 'CBC WITH DIFF', 'PROTEIN IMMUNOFIX ELECTROPHORESIS, SERUM', 'METABOLIC PANEL, COMPREHENSIVE',
    # 'TRANSFERRIN SATURATION', 'RETICULOCYTE COUNT', 'VITAMIN B12', 'FERRITIN', 'HAPTOGLOBIN', 'ANTI CARDIOLIPIN AB']
    # top10 imgs are 215/7179 procedures top100 imgs are 326/1000
    topn_imgs = proc_t2[proc_t2['order_type'] == 'Imaging'].groupby('proc_id').size().sort_values(ascending=False)[:topn_for_imgs].index.tolist()
    # print(proc_t2[proc_t2['proc_id'].isin(topn_imgs)]['description'].unique())
     
    # create targets
    ordered_labs = filter_topn(proc_t2[proc_t2['order_type'] == 'Lab'], 'proc_id', topn=topn_for_labs)
    count_labs = pivot_counts(ordered_labs, 'anon_id', 'proc_id', na_fill=0)
    ordered_imgs = filter_topn(proc_t2[proc_t2['order_type'] == 'Imaging'], 'proc_id', topn=topn_for_imgs)
    count_imgs = pivot_counts(ordered_imgs, 'anon_id', 'proc_id', na_fill=0)
    targets = pd.merge(count_labs, count_imgs, on='anon_id', how='outer').fillna(0)
    return targets

def filter_topn(df, col_name, topn=10):
    # TODO: change selection of top n by lift or interest method
    top_n_vals = df[col_name].value_counts()[:topn].index.tolist()
    filtered_df = df[df[col_name].isin(top_n_vals)]
    return filtered_df

def pivot_counts(df, id_col, key_col, na_fill=0):
    count_df = df.groupby([id_col, key_col]).agg(counts=pd.NamedAgg(column=key_col, aggfunc="count")).reset_index()
    feats = count_df.pivot(index=id_col, columns=key_col, values='counts').fillna(na_fill)
    # binarize counts
    feats = feats > 0
    return feats

def clean_base_cohort(base_cohort):
    # handle repeated patient entries (692 anon_ids with repeats), take first referral
    base_cohort = base_cohort.sort_values('referralOrderDateTime').groupby('anon_id').head(1)
    # remove cases where speciality datetime < referral datetime (t2 <= t1)
    base_cohort = base_cohort[base_cohort['specialtyEncounterDateTime'] > base_cohort['referralOrderDateTime']]
    return base_cohort

def remove_outliers(df, col_name):
    limit = df[col_name].std()*3
    df = df[df[col_name] <= limit]
    df = df[df[col_name] >= -limit]
    return df

# prepare and return the feats
def organize_t1_feats(base_cohort, demographic, meds_t1, proc_t1, diag_t1, labs_t1, topn = 10):
    """
    Organize all features for t1 and merge them to base cohort
    """
    # 1. Create demographic feats
    base_cohort = clean_base_cohort(base_cohort)
    demo_df = pd.merge(base_cohort, demographic, on='anon_id', how='left')
    demo_feats = get_demo_feats(demo_df, eth_race=False) # don't include ethnicity/race info for training
    # 2. Create medicine feats.
    med_feats = get_meds_feats(meds_t1, topn=topn, save_dir=save_dir)
    # 3. Create diagnostic feats
    diag_feats = get_diag_feats(diag_t1, topn=topn)
    # 4. Create Lab result feats
    lab_feats = get_lab_feats(labs_t1, topn=topn)
    # 5. Create procedure feats
    proc_feats = get_proc_feats(proc_t1, topn=topn)
    #6. join all the features together
    # here demo_feats already has been merged w/ the base_cohort
    all_feats = pd.merge(demo_feats, med_feats, on='anon_id', how='left')
    all_feats.fillna(0, inplace=True)
    all_feats = pd.merge(all_feats, diag_feats, on='anon_id', how='left')
    all_feats.fillna(0, inplace=True)
    all_feats = pd.merge(all_feats, lab_feats, on='anon_id', how='left')
    all_feats.fillna(-1, inplace=True)
    all_feats = pd.merge(all_feats, proc_feats, on='anon_id', how='left')
    all_feats.fillna(0, inplace=True)
    # is there any way to vis if these are ok?
    return all_feats, base_cohort

def organize_t2_labels(base_cohort, proc_t2, diag_t2, topn=10, save_hists=False):
    """
    Calculate labels for t2 according to the ordered procedures at t2.
    save_hists option for exploring the diagnosis.
    """
    # 0. Explore diagnosis
    if save_hists:
       topn_diag_codes = explore_diag(diag_t2, save_dir)
    # 1. Create targets from orders
    targets = get_proc_labels(proc_t2)
    # 2. join targets to cohort
    # t = pd.merge(base_cohort['anon_id'], targets, on='anon_id', how='left').fillna(0)
    # only 1410/3476 have a non zero target 1426 if we add ref targets
    targets = pd.merge(base_cohort[['anon_id', 'referralOrderDateTime']], targets, on='anon_id', how='left')
    targets.fillna(0, inplace=True)
    return targets

def split_dfs(df1, df2, keep_ids, col_name, remove_col=True):
    df1 = df1[df1[col_name].isin(keep_ids)]
    df2 = df2[df2[col_name].isin(keep_ids)]
    if remove_col:
        df1.drop(col_name, axis=1, inplace=True)
        df2.drop(col_name, axis=1, inplace=True)
    return df1, df2

def split_cohort(base_cohort, feats, targets, test_year=2019, val_year=2018):
    """
    Split cohort (features and targets) into train, val and test using temporal and patient-wise splits.
    """
    # TODO: include 2020? only 69 pats, include 2008? only 57 pats
    # 2019 test = 412, trainval 2008-2018+2020 = 3064, 2018 val = 474, train remaining = 2590
    # create year col for easy comparisons
    base_cohort['year'] = pd.DatetimeIndex(base_cohort['specialtyEncounterDateTime']).year
    # remove zero targets
    nonzero_ids = targets[targets.sum(axis=1) > 0]['anon_id']
    base_cohort = base_cohort[base_cohort['anon_id'].isin(nonzero_ids)] # [1927 rows x 6 columns]
    # LB: include 2020? only 40 pats, include 2008? only 15 pats
    # 2019 test = 254, trainval 2008-2018+2020 = 1673, 2018 val = 252, train remaining = 1421

    test_ids = base_cohort['anon_id'][base_cohort['year'] == test_year]
    val_ids = base_cohort['anon_id'][base_cohort['year'] == val_year]
    train_ids = base_cohort['anon_id'][~base_cohort['year'].isin([val_year, test_year])]

    # remove datetime and other non-trainable columns
    remove_cols = ['referralOrderDateTime', 'referringEncounterId', 'specialtyEncounterDateTime', 'specialtyEncounterId']
    feats = feats[feats.columns[~feats.columns.isin(remove_cols)]]
    targets = targets[targets.columns[~targets.columns.isin(remove_cols)]]
    
    train_feats, train_targets = split_dfs(feats, targets, train_ids, 'anon_id')
    val_feats, val_targets = split_dfs(feats, targets, val_ids, 'anon_id')
    test_feats, test_targets = split_dfs(feats, targets, test_ids, 'anon_id')

    return train_feats, val_feats, test_feats, train_targets, val_targets, test_targets

def organize_feats():
    """
    Main function for preparing the features, labels and spliting the cohort for training and evaluation.
    """
    feats, bc = organize_t1_feats(base_cohort, demographic, meds_t1, proc_t1, diag_t1, labs_t1)
    targets = organize_t2_labels(bc, proc_t2, diag_t2)
    train_feats, val_feats, test_feats, train_targets, val_targets, test_targets = split_cohort(bc, feats, targets)
    return train_feats, val_feats, test_feats, train_targets, val_targets, test_targets
