# TODO:
# fix shapley plots (take out all categorical/identification features)
# merge datasets
# feature engineering (use shap plots)
# figure out percent differences in ROC

###
# import packages
###
import pandas as pd
from google.cloud import bigquery
from comorbidipy import comorbidity
import lightgbm as lgb
from lightgbm import early_stopping
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score, f1_score, auc, confusion_matrix, roc_curve
from sklearn.preprocessing import OneHotEncoder
from sklearn import __version__ as sklearn_version
from packaging import version
import multiprocessing
import numpy as np
import shap
import matplotlib.pyplot as plt

###
# define features for use in model
###
categorical_features = ["female", "dialysis", "year", "vasopressor"]
numeric_features = ["age", "cci",
                     "wbch", "hgbl", "pltl",
                     "sodiuml", "bicarbl", "bunh", "creath", "glucl",
                     "asth", "alth", "bilih",
                     "albuml",  "lactateh",
                     "hrateh", "rrateh", "temph", "sysbpl", "diasbpl", "weightl",
                     "count_rx_oral", "count_rx_iv", "number_of_admissions",
                     "count_ciprofloxacin_resistance_within_6mo", "count_ciprofloxacin_resistance_before_6mo",
                     "count_oxacillin_resistance_within_6mo", "count_oxacillin_resistance_before_6mo",
                     "count_ampicillin_resistance_within_6mo", "count_ampicillin_resistance_before_6mo",
                     "count_cefazolin_resistance_within_6mo", "count_cefazolin_resistance_before_6mo",
                     "count_ceftriaxone_resistance_within_6mo", "count_ceftriaxone_resistance_before_6mo",
                     "count_cefepime_resistance_within_6mo", "count_cefepime_resistance_before_6mo",
                     "count_pip_tazo_resistance_within_6mo", "count_pip_tazo_resistance_before_6mo",
                     "count_meropenem_resistance_within_6mo", "count_meropenem_resistance_before_6mo",
                     "count_trim_sulfa_resistance_within_6mo", "count_trim_sulfa_resistance_before_6mo",
                     "count_vancomycin_resistance_within_6mo", "count_vancomycin_resistance_before_6mo",
                     "prior_year_antibiogram_ciprofloxacin",
                     "prior_year_antibiogram_oxacillin",
                     "prior_year_antibiogram_ampicillin",
                     "prior_year_antibiogram_cefazolin",
                     "prior_year_antibiogram_ceftriaxone",
                     "prior_year_antibiogram_cefepime",
                     "prior_year_antibiogram_pip_tazo",
                     "prior_year_antibiogram_meropenem",
                     "prior_year_antibiogram_trim_sulfa",
                     "prior_year_antibiogram_vancomycin",
                     "count_prior_pseudomonas_culture",
                     "count_prior_staph_aureus_culture",
                     "count_prior_enterococcus_culture"]


###
# Calculate and add Charlson comorbidity index scores from parsed ICD9 codes
###
def add_charlson_comorbidity_index(df, index):
    # ensure that the 'icd9s' column contains strings instead of lists
    df['icd9s'] = df['icd9s'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

    # first parse/explode values of icd9s column for each patient
    icds_parsed = df.explode('icd9s')

    # rename 'index' column to 'id' temporarily if needed for comorbidity calculation
    df = df.rename(columns={index: 'id'})

    # calculate individual component comorbidity scores
    comorbidity_scores = comorbidity(df, 
                                     id = 'id', 
                                     code = "anon_id", 
                                     age = "age", 
                                     score = "charlson",
                                     icd = "icd10",
                                     variant = "shmi",
                                     weighting = "shmi",
                                     assign0 = True)
    
    # rename 'id' column back to the original name
    comorbidity_scores = comorbidity_scores.rename(columns={'id': index})
    df = df.rename(columns={'id': index})

    # merge scores onto df
    df = df.merge(comorbidity_scores[[index, 'age_adj_comorbidity_score']], on = index, how='left')

    # rename 'age_adj_comorbidity_score' to 'cci'
    df = df.rename(columns={'age_adj_comorbidity_score':'cci'})
    
    return df


###
# model training for LightGBM models
###
def train_test_lgb(df, model_antibiotic, features):
    # select data for the given antibiotic features
    df_filtered = df[df['antibiotic'] == model_antibiotic].drop_duplicates(subset=['csn'] + features)

    # split data into training (pre-2022) and testing (2022 and 2023)
    df_train = df_filtered[~df_filtered['year'].isin([2022, 2023])].drop(columns=['year'])
    df_test = df_filtered[df_filtered['year'].isin([2022, 2023])].drop(columns=['year'])

    # ensure labels are numpy arrays or pandas Series
    train_labels = df_train['resistance'].astype(np.float32).values
    test_labels = df_test['resistance'].astype(np.float32).values

    # set up lightGBM datasets
    df_lgb_train = lgb.Dataset(df_train[features].values, label= train_labels)
    df_lgb_validation = lgb.Dataset(df_test[features].values, label = test_labels)

    # set up hyperparameter grid search
    lgb_grid = pd.DataFrame ({
        'nrounds': [1000] * 4,
        'learning_rate': [0.01, 0.025, 0.05, 0.1],
        'bagging_fraction': [0.6, 0.8, 0.9, 1.0],
        'bagging_freq': [5, 10, 20, 5],
        'early_stopping_rounds': [10, 10, 10, 10]
    })

    cv_aucs = np.zeros(len(lgb_grid))

    # Iterate through hyperparameters to find the best cross-validated AUC
    for i in range(len(lgb_grid)):
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'is_unbalance': True,
            'num_threads': multiprocessing.cpu_count(),
            'learning_rate': lgb_grid.loc[i, 'learning_rate'],
            'max_depth': -1,
            'bagging_fraction': lgb_grid.loc[i, 'bagging_fraction'],
            'bagging_freq': lgb_grid.loc[i, 'bagging_freq'],
            'verbosity': -1
        }

    # cross-validate the lightGBM model
    cv_result = lgb.cv(params, df_lgb_train, nfold = 5, num_boost_round = 1000,
                       callbacks = [early_stopping(stopping_rounds=10)], metrics = 'auc', seed = 42)
    
    # handle the correct key for valid AUC mean
    valid_auc_mean = cv_result.get('valid auc-mean', None)

    if valid_auc_mean is not None:
        cv_aucs[i] = max(valid_auc_mean)
    
    # train the final model with the best hyperparameters 
    best_idx = np.argmax(cv_aucs)
    best_params = {
        'objective': 'binary',
        'metric': 'auc',
        'is_unbalance': True,
        'num_threads': multiprocessing.cpu_count(),
        'learning_rate': lgb_grid.loc[best_idx, 'learning_rate'],
        'max_depth': -1,
        'bagging_fraction': lgb_grid.loc[best_idx, 'bagging_fraction'],
        'bagging_freq': lgb_grid.loc[best_idx, 'bagging_freq'],
        'verbosity': -1
    }

    # ensure early_stopping_rounds is passed as a Python int
    early_stopping_rounds_value = int(lgb_grid.loc[best_idx, 'early_stopping_rounds'])

    model_lgb = lgb.train(best_params, df_lgb_train,
                          num_boost_round = int(lgb_grid.loc[best_idx, 'early_stopping_rounds']),
                          valid_sets = [df_lgb_validation], callbacks = [early_stopping(stopping_rounds=early_stopping_rounds_value)])
    
    # make predictions on the test set
    predictions = model_lgb.predict(df_test[features].values)

    # calculate ROC AUC
    roc_auc = roc_auc_score(df_test['resistance'], predictions)

    # generate confusion matrix
    threshold = 0.5
    predicted_classes = (predictions >= threshold).astype(int)
    cm = confusion_matrix(df_test['resistance'], predicted_classes)

    # return model, AUC, ROC, and confusion matrix
    return {
        'antibiotic': model_antibiotic.capitalize(),
        'model': model_lgb,
        'best_tune': lgb_grid.loc[best_idx],
        'df_train': df_train,
        'df_test': df_test,
        'predictions': predictions,
        'auc': roc_auc,
        'roc': roc_curve(df_test['resistance'], predictions),
        'cm':cm
    }


###
# calculate Shapely values and plot feature importance
###
def plot_shap_importance(model):
    X = model['df_train'].drop(['csn', 'resistance'], axis = 1)

    explainer = shap.TreeExplainer(model['model'])

    shap_values = explainer.shap_values(X)

    shap.summary_plot(shap_values, X, plot_type="dot", show = False)

    plt.title(f"SHAP Feature Analysis for {model['antibiotic']} Model")

    plt.show()

###
# plot antibiotic orders saved in next 24 hours
###
def antibiotics_24h_saved(model, df_all_antibiotics_24h, antibiotic24h):
    # load test data and predictions from model
    df_test = model['df_test'].copy()
    df_test['predictions'] = model['predictions']

    # merge with 24h antibiotic order df with df_test
    df_all_antibiotics_24h = pd.merge(df_test, df_all_antibiotics_24h[['csn', 'antibiotic_24h']].drop_duplicates(), on = "csn", how = "left")

    # check that antibiotic 24h contains only 1 or 2 antibiotics
    if len(antibiotic24h) > 2:
        raise ValueError("Antibiotic24h must only contain max 2 antibiotics")
    
    # filter for the antibiotic of interest
    if len(antibiotic24h) == 1:
        specific_antibiotics_24h = df_all_antibiotics_24h[df_all_antibiotics_24h['antibiotic_24h'].str.upper() == antibiotic24h[0].upper()].drop(
            columns = ['antibiotic_24h']
        ).drop_duplicates()
    else:
        # if there are two antibiotics, find common CSNs
        csn1 = df_all_antibiotics_24h[df_all_antibiotics_24h['antibiotic_24h'].str.upper() == antibiotic24h[0].upper()]['csn']
        csn2 = df_all_antibiotics_24h[df_all_antibiotics_24h['antibiotic_24h'].str.upper() == antibiotic24h[1].upper()]['csn']
        csns = np.intersect1d(csn1, csn2)

        specific_antibiotics_24h = df_all_antibiotics_24h[df_all_antibiotics_24h['csn'].isin(csns)].drop(columns=['antibiotic_24h']).drop_duplicates()

    # create a sequence of thresholds to test NPV
    thresholds = np.arange(0.00, 1.01, 0.01)
    excess = pd.DataFrame(columns=["threshold", "npv", "excess", "relative_excess", "true_excess", "perc_saved"])
    excess["threshold"] = thresholds

    # true excess is the number of orders that were not resistant on culture (gold standard)
    true_excess = len(specific_antibiotics_24h[specific_antibiotics_24h['resistance'] == 0])

    # iterate through thresholds and calculate NPV and excess antibiotic prescriptions
    for threshold in thresholds:
        specific_antibiotics_24h['predicted_resistance'] = np.where(specific_antibiotics_24h['predictions'] >= threshold, 1, 0)

        # calculate confusion matrix for NPV
        cm = confusion_matrix(specific_antibiotics_24h['resistance'], specific_antibiotics_24h['predicted_resistance'])
        tn, fp, fn, tp = cm.ravel()
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0

        # calculate number of excess antibiotic orders (predicted resistance = 0, true resistance = 0)
        excess_antibiotics = len(specific_antibiotics_24h[(specific_antibiotics_24h['predicted_resistance'] == 0) & (specific_antibiotics_24h['resistance'] == 0)])

        # fill in the DataFrame
        excess.loc[excess['threshold'] == threshold, 'npv'] = npv
        excess.loc[excess['threshold'] == threshold, 'excess'] = excess_antibiotics
        excess.loc[excess['threshold'] == threshold, 'relative_excess'] = true_excess - excess_antibiotics
        excess.loc[excess['threshold'] == threshold, 'true_excess'] = true_excess
        excess.loc[excess['threshold'] == threshold, 'perc_saved'] = round(100 * excess_antibiotics / true_excess, 2) if true_excess > 0 else 0
    
    # plot excess antibiotic orders saved vs NPV
    excess_grouped = excess.groupby(pd.cut(excess['npv'], np.arange(0, 1.025, 0.025))).agg({
        'npv': 'mean',
        'perc_saved': 'mean'
    }).dropna()

    print(excess_grouped)
    print(excess_grouped.dtypes)

    excess_grouped['npv'] = pd.to_numeric(excess_grouped['npv'], errors = 'coerce')
    excess_grouped['perc_saved'] = pd.to_numeric(excess_grouped['perc_saved'], errors = 'coerce')
    excess_grouped = excess_grouped.dropna()

    if not excess_grouped.empty:
        plt.plot(excess_grouped['npv'], excess_grouped['perc_saved'], label = "Percent saved")
        plt.axvline(x = 0.8, color = "r", linestyle = "dotted", label = "NPV = 0.8")
        plt.fill_between(excess_grouped['npv'], 0, excess_grouped['perc_saved'], color = "red", alpha = 0.2)
        plt.xlabel("Negative predictive value")
        plt.ylabel("Potentional excess antibiotic orders saved (%)")
        plt.title(f"{'/'.join([x.title() for x in antibiotic24h])} -> {model['antibiotic']}")
        plt.gca().invert_xaxis()
        plt.legend()
        plt.show()
    else:
        print("No valid data to plot.")

    return excess


###
# Download and prep the data for modeling
###
# TODO: figure out how to upload following queries: microbial resistance, ab class exposure, specific medication exposure, previous infecting organisms, prior procedures

# Download the data from BigQuery (custom query)
client = bigquery.Client()
query = """
    SELECT * 
    FROM `som-nero-phi-jonc101.mvm_abx.encounter_culture_labels_features_inpatient_24h_with_inference`
"""
query_job = client.query(query)
df = query_job.result().to_dataframe()

print(df)

# download previous nursing home visits data 
query = """
    SELECT * 
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.nursing_home_visits_temp`
"""
query_job = client.query(query)
df_nursing_visits = query_job.result().to_dataframe()

print(df_nursing_visits.columns)

# download ward data 
query = """
    SELECT * 
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_icu_info_adt`
"""
query_job = client.query(query)
df_ward = query_job.result().to_dataframe()

print(df_ward.columns)

# download ADI scores data
query = """
    SELECT * 
    FROM `som-nero-phi-jonc101.antimicrobial_stewardship.cohort_adi`
"""
query_job = client.query(query)
df_adi_scores = query_job.result().to_dataframe()

print(df_adi_scores.columns)

# merge datasets
merged_df = pd.merge(df, df_nursing_visits, on='anon_id', how = 'inner')

df_ward['pat_enc_csn_id_coded'] = df_ward['pat_enc_csn_id_coded'].astype(object)
merged_df = pd.merge(merged_df, df_ward, on=['anon_id', 'pat_enc_csn_id_coded'],
                     how = "inner")

merged_df = pd.merge(merged_df, df_adi_scores, on = ['anon_id', 'pat_enc_csn_id_coded'], how = 'inner')


print(merged_df)
print(merged_df.columns)

# add Charlson comorbidity index scores
df = add_charlson_comorbidity_index(df, "csn")

# clean data frame (remove missing labels, set feature types, etc)
df = (
    df[df['resistance'].notna()]
    .query('year != "2024"')
    .query('age >= 18')
    .assign(**{col: df[col].astype('category') for col in ["antibiotic"] + categorical_features})
    .assign(**{col: pd.to_numeric(df[col], errors='coerce') for col in numeric_features})
    .drop_duplicates()
)

# feature list
all_features = list(set(numeric_features + categorical_features) - set(["year"]))
print(all_features)

###
# fit models for 5 different antibiotics
###
model_features = [feature for feature in (categorical_features) + numeric_features if feature != 'year']

model_cefazolin = train_test_lgb(df, "CEFAZOLIN", model_features)
model_ceftriaxone = train_test_lgb(df, "CEFTRIAXONE", model_features)
model_cefepime = train_test_lgb(df, "CEFTRIAXONE", model_features)
model_piptazo = train_test_lgb(df, "PIPERACILLIN_TAZOBACTAM", model_features)
model_ciprofloxacin = train_test_lgb(df, "CIPROFLOXACIN", model_features)

###
# Present model performance metrics for all models
###
models = [model_cefazolin, model_ceftriaxone, model_cefepime, model_piptazo, model_ciprofloxacin]

# create empty DataFrame to store model metrics
metrics = pd.DataFrame(columns=["Antibiotic Model", "AUC", "Accuracy", "Sensitivity", "Specificity", "F1"])

rocs = {}
for model in models:
   predictions = model['predictions']
   true_labels = model['df_test']['resistance']

   fpr, tpr, _ = roc_curve(true_labels, predictions)
   roc_auc = auc(fpr, tpr)
   auc_ci = [roc_auc -0.05, roc_auc, roc_auc + 0.05] # placeholder CIs
   auc_text = f"{round(auc_ci[1], 2)} ({round(auc_ci[0], 2)}-{round(auc_ci[2], 2)})"

   threshold = 0.5
   predicted_classes = (predictions >= threshold).astype(int)
   cm = confusion_matrix(true_labels, predicted_classes)
   tn, fp, fn, tp = cm.ravel()

   accuracy = accuracy_score(true_labels, predicted_classes)
   sensitivity = recall_score(true_labels, predicted_classes)
   specificity = tn / (tn + fp)
   f1 = f1_score(true_labels, predicted_classes)

   new_row = pd.DataFrame({
       "Antibiotic Model": [model['antibiotic']],
       "AUC": [auc_text],
       "Accuracy": [round(accuracy, 2)],
       "Sensitivity": [round(sensitivity, 2)],
       "Specificity": [round(specificity, 2)],
       "F1": [round(f1, 2)]
   })
   metrics = pd.concat([metrics, new_row], ignore_index = True)

   rocs[f"{model['antibiotic']} AUC: {auc_text}"] = (fpr, tpr)

print(metrics)

plt.figure()
for label, (fpr, tpr) in rocs.items():
    plt.plot(fpr, tpr, label = label)

plt.plot([0, 1], [0, 1], color = 'navy', linestyle = '--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.show()

###
# Plot Shapley feature importance for all models
###
plot_shap_importance(model_cefazolin)
plot_shap_importance(model_ceftriaxone)
plot_shap_importance(model_cefepime)
plot_shap_importance(model_piptazo)
plot_shap_importance(model_ciprofloxacin)

###
# Plot excess antibiotic orders saved within 24 hours
###
# download 24 hour antibiotic data from BigQuery
client = bigquery.Client()

query = """
    SELECT * 
    FROM `som-nero-phi-jonc101.mvm_abx.antibiotics_24h_after_culture_order`
"""

query_job = client.query(query)

df_all_antibiotics_24h = query_job.result().to_dataframe()

# switching to ceftriaxone
antibiotics_24h_saved(model_ceftriaxone, df_all_antibiotics_24h, ["VANCOMYCIN", "CEFTRIAXONE"])
antibiotics_24h_saved(model_ceftriaxone, df_all_antibiotics_24h, ["CEFEPIME"])
antibiotics_24h_saved(model_ceftriaxone, df_all_antibiotics_24h, ["VANCOMYCIN", "CEFEPIME"])
antibiotics_24h_saved(model_ceftriaxone, df_all_antibiotics_24h, ["PIPERACILLIN_TAZOBACTAM"])
antibiotics_24h_saved(model_ceftriaxone, df_all_antibiotics_24h, ["VANCOMYCIN", "PIPERACILLIN_TAZOBACTAM"])

# switching to cefazolin
antibiotics_24h_saved(model_cefazolin, df_all_antibiotics_24h, ["CEFTRIAXONE"])
antibiotics_24h_saved(model_cefazolin, df_all_antibiotics_24h, ["VANCOMYCIN", "CEFTRIAXONE"])

# switching to cefepime
antibiotics_24h_saved(model_cefepime, df_all_antibiotics_24h, ["VANCOMYCIN", "CEFEPIME"])
antibiotics_24h_saved(model_cefepime, df_all_antibiotics_24h, ["PIPERACILLIN_TAZOBACTAM"])
antibiotics_24h_saved(model_cefepime, df_all_antibiotics_24h, ["VANCOMYCIN", "PIPERACILLIN_TAZOBACTAM"])