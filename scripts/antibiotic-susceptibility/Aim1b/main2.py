### packages
import pandas as pd
import lightgbm as lgb
from lightgbm import LGBMClassifier, Dataset, cv, train, early_stopping
from sklearn.metrics import roc_auc_score, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn import __version__ as sklearn_version
from packaging import version
from multiprocessing import cpu_count
import numpy as np
import shap
import matplotlib.pyplot as plt
import polars as pl
import itertools

### data preparation
# load CSVs
comorbidity_scores = pd.read_csv('microbiology_cultures_comorbidity.csv')
adi_scores = pd.read_csv('microbiology_cultures_adi_scores.csv')
labs = pd.read_csv('microbiology_cultures_labs.csv')
vitals = pd.read_csv('microbiology_cultures_vitals.csv')
prior_infecting_organisms = pd.read_csv('microbiology_cultures_prior_infecting_organism.csv')
subtype_exposure = pd.read_csv('microbiology_cultures_antibiotic_subtype_exposure.csv')
demographics = pd.read_csv('microbiology_cultures_demographics.csv')
prior_med = pd.read_csv('microbiology_cultures_prior_med.csv')
prior_procedures = pd.read_csv('microbiology_cultures_priorprocedures.csv')
ward_info = pd.read_csv('microbiology_cultures_ward_info.csv')
microbial_resistance = pd.read_csv('microbiology_cultures_microbial_resistance.csv')
cohort = pd.read_csv('microbiology_cultures_cohort.csv')
antibiotic_class_exposure = pd.read_csv('microbiology_cultures_antibiotic_class_exposure.csv')
implied_susceptibility = pd.read_csv('microbiology_cultures_implied_susceptibility.csv')
nursing_home_visits = pd.read_csv('microbiology_cultures_nursing_home_visits.csv')

### prepare dataframe
# filter cohort
cohort = cohort[cohort['antibiotic'].isin(['Cefazolin', 'Ceftriaxone', 'Cefepime', 'Piperacillin/Tazobactam', 'Ciprofloxacin'])]
cohort = cohort[cohort['was_positive'] == 1]
cohort = cohort[cohort['ordering_mode'] == 'Inpatient']
cohort = cohort.drop(columns = ['ordering_mode', 'was_positive'])
cohort['year'] = [time[:4] for time in cohort['order_time_jittered_utc']]

# add implied susceptibilities
implied_susceptibility = implied_susceptibility[implied_susceptibility['antibiotic'].isin(['Cefazolin', 'Ceftriaxone', 'Cefepime', 'Piperacillin/Tazobactam', 'Ciprofloxacin'])]
df = cohort.merge(implied_susceptibility, on = ['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'organism', 'antibiotic', 'susceptibility'], how = 'left')
df['susceptibility'] = df['implied_susceptibility'].fillna(df['susceptibility'])
df = df.drop(columns=['implied_susceptibility'])
df = df[df['susceptibility'].isin(['Susceptible', 'Resistant'])]

# add demographic features
df = df.merge(demographics, on = ['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded'], how = 'left')

# add ward info (not too helpful)
df = df.merge(ward_info, on = ['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'order_time_jittered_utc'], how = 'left')

# add adi scores (only score, not state rank)
df = df.merge(adi_scores, on = ['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'order_time_jittered_utc'], how = 'left')

# add vitals (useless)
df = df.merge(vitals, on = ['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded'], how = 'left')

# add nursing home visits (only within 6 months helps)
nursing_home_visits.loc[nursing_home_visits['nursing_home_visit_culture'] == 0, 'nursing_home_visit_culture'] += 1
nursing_home_visits['nursing_home_visit_culture'] = nursing_home_visits['nursing_home_visit_culture'].fillna(0)
# make six month columns
six_months = 6 * 30
nursing_home_visits['nursing_visits_within_6mo'] = nursing_home_visits['nursing_home_visit_culture'].apply(lambda x: 1 if 0 < x <= six_months else 0)
nursing_home_visits['nursing_visits_before_6mo'] = nursing_home_visits['nursing_home_visit_culture'].apply(lambda x: 1 if x > six_months else 0)

nursing_home_visits = nursing_home_visits.groupby('anon_id').agg(
    nursing_visits_within_6mo =('nursing_visits_within_6mo', sum),
    nursing_visits_before_6mo =('nursing_visits_before_6mo', sum)
).reset_index()

df = df.merge(nursing_home_visits, on = 'anon_id', how = 'left')

# add prior procedures
prior_procedures.loc[prior_procedures['procedure_time_to_cultureTime'] == 0, 'procedure_time_to_cultureTime'] += 1
prior_procedures.loc['procedure_time_to_cultureTime'] = prior_procedures['procedure_time_to_cultureTime'].fillna(0)
# make six month columns
six_months = 6 * 30
procedures = prior_procedures['procedure_description'][pd.notna(prior_procedures['procedure_description'])].unique()
for procedure in procedures:
    prior_procedures[f"{procedure}_within_6mo"] = prior_procedures[prior_procedures['procedure_description'] == procedure]['procedure_time_to_cultureTime'].apply(lambda x: 1 if 0 < x <= six_months else 0)
    prior_procedures[f"{procedure}_before_6mo"] = prior_procedures[prior_procedures['procedure_description'] == procedure]['procedure_time_to_cultureTime'].apply(lambda x: 1 if x > six_months else 0)

columns_to_sum = prior_procedures.columns[6:].tolist()
agg_dict = {col: (col, 'sum') for col in columns_to_sum}
prior_procedures = prior_procedures.groupby('anon_id').agg(**agg_dict).reset_index() # one patient has 711 dialysis procedures within 6 months...also has 2633 entries in original df

df = df.merge(prior_procedures, on = 'anon_id', how = 'left')

# microbial resistance (game changer)
microbial_resistance = microbial_resistance[microbial_resistance['antibiotic'].isin(['Cefazolin', 'Ceftriaxone', 'Cefepime', 'Piperacillin/Tazobactam', 'Ciprofloxacin'])]
# filter for top 10 most common microbes
microbial_resistance = microbial_resistance[microbial_resistance['organism'].isin(['ESCHERICHIA COLI', 'PSEUDOMONAS AERUGINOSA', 'MUCOID PSEUDOMONAS AERUGINOSA', 
                                                                                   'KLEBSIELLA PNEUMONIAE', 'ACHROMOBACTER XYLOSOXIDANS', 'STAPHYLOCOCCUS AUREUS', 
                                                                                   'PSEUDOMONAS AERUGINOSA (NON-MUCOID CF)', 'ENTEROCOCCUS SPECIES', 'ENTEROBACTER CLOACAE COMPLEX', 'PROTEUS MIRABILIS'])]

microbial_resistance.loc[microbial_resistance['resistant_time_to_cultureTime'] == 0, 'resistant_time_to_cultureTime'] += 1
microbial_resistance.loc['resistant_time_to_cultureTime'] = microbial_resistance['resistant_time_to_cultureTime'].fillna(0)
# make six month columns
six_months = 6 * 30
microbes = microbial_resistance['organism'][pd.notna(microbial_resistance['organism'])].unique()
for microbe in microbes:
    microbial_resistance[f"{microbe}_within_6mo"] = microbial_resistance[microbial_resistance['organism'] == microbe]['resistant_time_to_cultureTime'].apply(lambda x: 1 if 0 < x <= six_months else 0)
    microbial_resistance[f"{microbe}_before_6mo"] = microbial_resistance[microbial_resistance['organism'] == microbe]['resistant_time_to_cultureTime'].apply(lambda x: 1 if x > six_months else 0)

columns_to_sum = microbial_resistance.columns[7:].tolist()
agg_dict = {col: (col, 'sum') for col in columns_to_sum}
microbial_resistance = microbial_resistance.groupby('anon_id').agg(**agg_dict).reset_index() 

df = df.merge(microbial_resistance, on = 'anon_id', how = 'left')

# add prior infecting organisms
# filter for top ten most common infecting organisms
prior_infecting_organisms = prior_infecting_organisms[prior_infecting_organisms['prior_organism'].isin(['Escherichia', 'Staphylococcus', 'Pseudomonas', 
                                                                                                        'Enterococcus', 'Klebsiella', 'Streptococcus', 
                                                                                                        'Proteus', 'CONS', 'Stenotrophomonas', 'Enterobacter'])]

prior_infecting_organisms.loc[prior_infecting_organisms['prior_infecting_organism_days_to_culutre'] == 0, 'prior_infecting_organism_days_to_culutre'] += 1
prior_infecting_organisms.loc['prior_infecting_organism_day_to_culutre'] = prior_infecting_organisms['prior_infecting_organism_days_to_culutre'].fillna(0)
# make six month columns
six_months = 6 * 30
organisms = prior_infecting_organisms['prior_organism'][pd.notna(prior_infecting_organisms['prior_organism'])].unique()
for organism in organisms:
    prior_infecting_organisms[f"prior_infecting_{organism}_within_6mo"] = prior_infecting_organisms[prior_infecting_organisms['prior_organism'] == organism]['prior_infecting_organism_days_to_culutre'].apply(lambda x: 1 if 0 < x <= six_months else 0)
    prior_infecting_organisms[f"prior_infecting_{organism}_before_6mo"] = prior_infecting_organisms[prior_infecting_organisms['prior_organism'] == organism]['prior_infecting_organism_days_to_culutre'].apply(lambda x: 1 if x > six_months else 0)

columns_to_sum = prior_infecting_organisms.columns[6:].tolist()
agg_dict = {col: (col, 'sum') for col in columns_to_sum}
prior_infecting_organisms = prior_infecting_organisms.groupby('anon_id').agg(**agg_dict).reset_index() 

df = df.merge(prior_infecting_organisms, on = 'anon_id', how = 'left')

# add comorbidities
# filter for top ten most common comorbidities
comorbidity_scores = comorbidity_scores[comorbidity_scores['comorbidity_component'].isin(['Congestive heart failure', 'Other specified status', 'Abnormal findings without diagnosis', 
                                                                                          'Organ transplant status', 'Personal/family history of disease', 'Renal failure', 
                                                                                          'Abdominal pain and other digestive/abdomen signs and symptoms', 'Solid tumor without metastasis', 
                                                                                          'Disorders of lipid metabolism', 'Musculoskeletal pain, not low back pain'])]

comorbidity_scores['comorbidity_component_end_days_culture'] = comorbidity_scores['comorbidity_component_end_days_culture'].abs()
comorbidity_scores.loc[comorbidity_scores['comorbidity_component_end_days_culture'] == 0, 'comorbidity_component_end_days_culture'] += 1
comorbidity_scores.loc['comorbidity_component_end_days_culture'] = comorbidity_scores['comorbidity_component_end_days_culture'].fillna(0)
# make six month columns
six_months = 6 * 30
comorbidities = comorbidity_scores['comorbidity_component'][pd.notna(comorbidity_scores['comorbidity_component'])].unique()
for comorbidity in comorbidities:
    comorbidity_scores[f"{comorbidity}_within_6mo"] = comorbidity_scores[comorbidity_scores['comorbidity_component'] == comorbidity]['comorbidity_component_end_days_culture'].apply(lambda x: 1 if 0 < x <= six_months else 0)
    comorbidity_scores[f"{comorbidity}_before_6mo"] = comorbidity_scores[comorbidity_scores['comorbidity_component'] == comorbidity]['comorbidity_component_end_days_culture'].apply(lambda x: 1 if x > six_months else 0)

columns_to_sum = comorbidity_scores.columns[7:].tolist()
agg_dict = {col: (col, 'sum') for col in columns_to_sum}
comorbidity_scores = comorbidity_scores.groupby('anon_id').agg(**agg_dict).reset_index() 
comorbidity_scores.columns = comorbidity_scores.columns.str.replace(r'[^a-zA-Z0-9_]', '', regex = True)

comorbidity_scores.to_csv('comorbidities_cleaned.csv', index = False)

comorbidities = pd.read_csv('comorbidities_cleaned.csv')

df = df.merge(comorbidities, on = 'anon_id', how = 'left')

# add prior med features
# filtering for positive times
prior_med = prior_med[prior_med['medication_time_to_cultureTime'] >= 0]
# filter for top ten most common infecting organisms
prior_med = prior_med[prior_med['medication_name'].isin(['Cefazolin', 'Levofloxacin', 'Metronidazole',
                                                         'Vancomycin', 'Ciprofloxacin', 'Ceftriaxone', 
                                                         'Gentamicin', 'Colistin', 'Cefepime', 'Ertapenem'])]

prior_med.loc[prior_med['medication_time_to_cultureTime'] == 0, 'medication_time_to_cultureTime'] += 1
prior_med.loc['medication_time_to_cultureTime'] = prior_med['medication_time_to_cultureTime'].fillna(0)
# make six month columns
six_months = 6 * 30
medications = prior_med['medication_name'][pd.notna(prior_med['medication_name'])].unique()
for medication in medications:
    prior_med[f"{medication}_within_6mo"] = prior_med[prior_med['medication_name'] == medication]['medication_time_to_cultureTime'].apply(lambda x: 1 if 0 < x <= six_months else 0)
    prior_med[f"{medication}_before_6mo"] = prior_med[prior_med['medication_name'] == medication]['medication_time_to_cultureTime'].apply(lambda x: 1 if x > six_months else 0)

columns_to_sum = prior_med.columns[7:].tolist()
agg_dict = {col: (col, 'sum') for col in columns_to_sum}
prior_med = prior_med.groupby('anon_id').agg(**agg_dict).reset_index() 

df = df.merge(prior_med, on = 'anon_id', how = 'left')

# antibiotic class exposure
# filtering for positive times
antibiotic_class_exposure = antibiotic_class_exposure[antibiotic_class_exposure['time_to_cultureTime'] >= 0]
# filter for top ten most common infecting organisms
antibiotic_class_exposure = antibiotic_class_exposure[antibiotic_class_exposure['antibiotic_class'].isin(['Beta Lactam', 'Fluoroquinolone', 'Macrolide Lincosamide', 
                                                                                                         'Combination Antibiotic', 'Nitrofuran', 'Nitroimidazole', 
                                                                                                         'Glycopeptide', 'Tetracycline', 'Ansamycin', 'Aminoglycoside'])]

antibiotic_class_exposure.loc[antibiotic_class_exposure['time_to_cultureTime'] == 0, 'time_to_cultureTime'] += 1
antibiotic_class_exposure.loc['time_to_cultureTime'] = antibiotic_class_exposure['time_to_cultureTime'].fillna(0)
# make six month columns
six_months = 6 * 30
antibiotics = antibiotic_class_exposure['antibiotic_class'][pd.notna(antibiotic_class_exposure['antibiotic_class'])].unique()
for antibiotic in antibiotics:
    antibiotic_class_exposure[f"{antibiotic}_within_6mo"] = antibiotic_class_exposure[antibiotic_class_exposure['antibiotic_class'] == antibiotic]['time_to_cultureTime'].apply(lambda x: 1 if 0 < x <= six_months else 0)
    antibiotic_class_exposure[f"{antibiotic}_before_6mo"] = antibiotic_class_exposure[antibiotic_class_exposure['antibiotic_class'] == antibiotic]['time_to_cultureTime'].apply(lambda x: 1 if x > six_months else 0)

columns_to_sum = antibiotic_class_exposure.columns[8:].tolist()
agg_dict = {col: (col, 'sum') for col in columns_to_sum}
antibiotic_class_exposure = antibiotic_class_exposure.groupby('anon_id').agg(**agg_dict).reset_index() 

df = df.merge(antibiotic_class_exposure, on = 'anon_id', how = 'left')


# labs
labs = labs[['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'Period_Day', 'median_wbc', 'median_neutrophils', 'median_lymphocytes', 'median_hgb',
             'median_plt', 'median_na', 'median_hco3', 'median_bun', 'median_cr', 'median_lactate',
             'median_procalcitonin']]

df = df.merge(labs, on = ['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded'], how = 'left')

### define features for use in model
categorical_features = ['organism', 'gender', 'culture_description']
numeric_features = ['age', 'adi_score', 'nursing_visits_within_6mo', 'urethral_catheter_within_6mo',
                    'urethral_catheter_before_6mo', 'surgical_procedure_within_6mo', 'surgical_procedure_before_6mo', 
                    'cvc_within_6mo', 'cvc_before_6mo', 'mechvent_within_6mo', 'mechvent_before_6mo', 'parenteral_nutrition_within_6mo', 
                    'parenteral_nutrition_before_6mo', 'dialysis_within_6mo', 'dialysis_before_6mo', 
                    'PSEUDOMONAS AERUGINOSA (NON-MUCOID CF)_within_6mo', 'PSEUDOMONAS AERUGINOSA (NON-MUCOID CF)_before_6mo', 
                    'MUCOID PSEUDOMONAS AERUGINOSA_within_6mo', 'MUCOID PSEUDOMONAS AERUGINOSA_before_6mo', 'PSEUDOMONAS AERUGINOSA_within_6mo', 
                    'PSEUDOMONAS AERUGINOSA_before_6mo', 
                    'ACHROMOBACTER XYLOSOXIDANS_within_6mo', 'ACHROMOBACTER XYLOSOXIDANS_before_6mo', 
                    'ESCHERICHIA COLI_within_6mo', 'ESCHERICHIA COLI_before_6mo', 'KLEBSIELLA PNEUMONIAE_within_6mo', 'KLEBSIELLA PNEUMONIAE_before_6mo', 
                    'PROTEUS MIRABILIS_within_6mo', 'PROTEUS MIRABILIS_before_6mo', 'ENTEROBACTER CLOACAE COMPLEX_within_6mo', 'ENTEROBACTER CLOACAE COMPLEX_before_6mo', 
                    'STAPHYLOCOCCUS AUREUS_within_6mo', 'STAPHYLOCOCCUS AUREUS_before_6mo', 'ENTEROCOCCUS SPECIES_within_6mo', 'ENTEROCOCCUS SPECIES_before_6mo', 
                    'prior_infecting_Escherichia_within_6mo', 'prior_infecting_Escherichia_before_6mo', 'prior_infecting_Enterobacter_within_6mo', 
                    'prior_infecting_Enterobacter_before_6mo', 'prior_infecting_Klebsiella_within_6mo', 'prior_infecting_Klebsiella_before_6mo', 
                    'prior_infecting_Proteus_within_6mo', 'prior_infecting_Proteus_before_6mo', 'prior_infecting_Staphylococcus_within_6mo', 
                    'prior_infecting_Staphylococcus_before_6mo', 'prior_infecting_Enterococcus_within_6mo', 'prior_infecting_Enterococcus_before_6mo', 
                    'prior_infecting_Pseudomonas_within_6mo', 'prior_infecting_Pseudomonas_before_6mo', 'prior_infecting_Streptococcus_within_6mo', 
                    'prior_infecting_Streptococcus_before_6mo', 'prior_infecting_CONS_within_6mo', 'prior_infecting_CONS_before_6mo', 'prior_infecting_Stenotrophomonas_within_6mo', 
                    'prior_infecting_Stenotrophomonas_before_6mo', 'Renalfailure_within_6mo', 'Renalfailure_before_6mo', 'Otherspecifiedstatus_within_6mo', 
                    'Otherspecifiedstatus_before_6mo', 'Organtransplantstatus_within_6mo', 'Organtransplantstatus_before_6mo',
                    'Congestiveheartfailure_within_6mo', 'Congestiveheartfailure_before_6mo', 'Disordersoflipidmetabolism_within_6mo',
                    'Disordersoflipidmetabolism_before_6mo', 'Solidtumorwithoutmetastasis_within_6mo', 'Solidtumorwithoutmetastasis_before_6mo',
                    'Personalorfamilyhistoryofdisease_within_6mo', 'Personalorfamilyhistoryofdisease_before_6mo',
                    'Abnormalfindingswithoutdiagnosis_within_6mo', 'Abnormalfindingswithoutdiagnosis_before_6mo', 'Musculoskeletalpainnotlowbackpain_within_6mo',
                    'Musculoskeletalpainnotlowbackpain_before_6mo', 'Abdominalpainandotherdigestiveorabdomensignsandsymptoms_within_6mo', 'Abdominalpainandotherdigestiveorabdomensignsandsymptoms_before_6mo',
                    'Period_Day', 
                    'median_wbc', 'median_neutrophils', 'median_lymphocytes', 'median_hgb', 'median_plt', 'median_na', 'median_hco3', 'median_bun', 'median_cr', 
                    'median_lactate', 'median_procalcitonin', 'Cefepime_within_6mo', 'Cefepime_before_6mo', 'Colistin_within_6mo', 'Colistin_before_6mo', 'Cefazolin_within_6mo', 'Cefazolin_before_6mo',
                    'Ertapenem_within_6mo', 'Ertapenem_before_6mo','Gentamicin_within_6mo', 'Gentamicin_before_6mo', 'Vancomycin_within_6mo', 'Vancomycin_before_6mo', 
                    'Ceftriaxone_within_6mo', 'Ceftriaxone_before_6mo', 'Levofloxacin_within_6mo', 'Levofloxacin_before_6mo', 
                    'Ciprofloxacin_within_6mo', 'Ciprofloxacin_before_6mo', 'Metronidazole_within_6mo', 'Metronidazole_before_6mo', 'Macrolide Lincosamide_within_6mo', 'Macrolide Lincosamide_before_6mo', 
                    'Beta Lactam_within_6mo', 'Beta Lactam_before_6mo', 'Tetracycline_within_6mo', 'Tetracycline_before_6mo', 'Combination Antibiotic_within_6mo', 
                    'Combination Antibiotic_before_6mo', 'Aminoglycoside_within_6mo', 'Aminoglycoside_before_6mo', 'Fluoroquinolone_within_6mo', 
                    'Fluoroquinolone_before_6mo', 'Ansamycin_within_6mo', 'Ansamycin_before_6mo', 'Nitrofuran_within_6mo',
                    'Nitrofuran_before_6mo', 'Nitroimidazole_within_6mo', 'Nitroimidazole_before_6mo', 'Glycopeptide_within_6mo','Glycopeptide_before_6mo']

# convert categorical features to category type
for col in categorical_features:
    df[col] = df[col].astype('category')

# convert numeric features to numeric type
df[numeric_features] = df[numeric_features].apply(pd.to_numeric, errors = 'coerce')

### model training with lightGBM model
def train_test_lgb(df, model_antibiotic, features):
    # Filter and select data for the given antibiotic and features
    df = (
        df[df['antibiotic'] == model_antibiotic]
        .drop_duplicates(subset=['anon_id', 'pat_enc_csn_id_coded', 'order_proc_id_coded', 'order_time_jittered_utc', 'susceptibility'] + features)
        .reset_index(drop=True)
    )

    # convert susceptibility to numeric
    label_enc = LabelEncoder()
    df['susceptibility'] = label_enc.fit_transform(df['susceptibility'])

    # Split data into training (pre-2022) and testing (2022 and 2023)
    df_train = df[~df['year'].isin(["2022", "2023"])].drop(columns=['year'])
    df_test = df[df['year'].isin(["2022", "2023"])].drop(columns=['year'])

    # pre-process categorical variables
    for col in categorical_features:
        encoder = LabelEncoder()
        combined = pd.concat([df_train[col], df_test[col]], axis=0)
        encoder.fit(combined)
        df_train[col] = encoder.transform(df_train[col])
        df_test[col] = encoder.transform(df_test[col])

    # Prepare LightGBM datasets
    X_train = df_train[features]
    y_train = df_train['susceptibility']
    X_test = df_test[features]
    y_test = df_test['susceptibility']

    df_lgb_train = Dataset(X_train, label=y_train)
    df_lgb_validation = Dataset(X_test, label=y_test)

    # Set up hyperparameter grid
    param_grid = {
        'learning_rate': [0.01, 0.025, 0.05, 0.1],
        'bagging_fraction': [0.6, 0.8, 0.9, 1],
        'bagging_freq': [5, 10, 20]
    }
    param_combinations = list(itertools.product(*param_grid.values()))

    best_auc = -np.inf
    best_params = None
    best_iter = None

    # Perform grid search for hyperparameter tuning
    for params in param_combinations:
        params_dict = {
            'objective': 'binary',
            'metric': 'auc',
            'is_unbalance': True,
            'num_threads': cpu_count(),
            'verbosity': -1,
            'learning_rate': params[0],
            'bagging_fraction': params[1],
            'bagging_freq': params[2]
        }

        cv_results = cv(
            params=params_dict,
            train_set=df_lgb_train,
            num_boost_round=100,
            nfold=5,
            callbacks=[early_stopping(stopping_rounds=10)]
        )

        if cv_results['valid auc-mean'][-1] > best_auc:
            best_auc = cv_results['valid auc-mean'][-1]
            best_params = params_dict
            best_iter = len(cv_results['valid auc-mean'])

    # Train final model with the best parameters
    best_params['verbosity'] = -1
    model = train(
        params=best_params,
        train_set=df_lgb_train,
        num_boost_round=best_iter,
        valid_sets=[df_lgb_validation],
        valid_names=['validation'],
        callbacks=[early_stopping(stopping_rounds=10)]
    )

    # Make predictions
    predictions = model.predict(X_test)

    # Calculate AUC
    auc = roc_auc_score(y_test, predictions)

    # Generate ROC curve
    fpr, tpr, _ = roc_curve(y_test, predictions)

    # Generate confusion matrix
    threshold = 0.5
    predicted_classes = (predictions >= threshold).astype(int)
    cm = confusion_matrix(y_test, predicted_classes)

    # Return results
    return {
        'antibiotic': model_antibiotic.title(),
        'model': model,
        'best_tune': best_params,
        'df_train': df_train,
        'df_test': df_test,
        'predictions': predictions,
        'auc': auc,
        'roc': {'fpr': fpr, 'tpr': tpr},
        'cm': cm
    }

### fit models
model_features = categorical_features + numeric_features

model_ciprofloxacin = train_test_lgb(df, "Ciprofloxacin", model_features)
model_piperacillin = train_test_lgb(df, "Piperacillin/Tazobactam", model_features)
model_cefazolin = train_test_lgb(df, "Cefazolin", model_features)
model_ceftriaxone = train_test_lgb(df, "Ceftriaxone", model_features)
model_cefepime = train_test_lgb(df, "Cefepime", model_features)

### shap feature importance plot
def plot_shap_importance(model):
    X_train = model['df_train'][model_features]
    X_test = model['df_test'][model_features]

    X_train = pd.get_dummies(X_train)
    X_test = pd.get_dummies(X_test)

    X_test = X_test.reindex(columns = X_train.columns, fill_value=0)
    
    explainer = shap.Explainer(model['model'], X_test)

    shap_values = explainer(X_test)

    shap_importance = pd.DataFrame({
        "Feature": X_test.columns,
        "Mean SHAP Value": np.abs(shap_values.values).mean(axis=0)
    })

    shap_importance = shap_importance.sort_values(by="Mean SHAP Value", ascending=False)

    print(shap_importance)

    # shap.plots.bar(shap_values)

    # explainer = shap.Explainer(model['model'])

    # shap_values = explainer.shap_values(X_train)

    # shap.summary_plot(shap_values, X_train)

plot_shap_importance(model_ciprofloxacin)

### plot model metrics
fpr1, tpr1 = model_ciprofloxacin['roc']['fpr'], model_ciprofloxacin['roc']['tpr']
fpr2, tpr2 = model_piperacillin['roc']['fpr'], model_piperacillin['roc']['tpr']
fpr3, tpr3 = model_cefazolin['roc']['fpr'], model_cefazolin['roc']['tpr']
fpr4, tpr4 = model_ceftriaxone['roc']['fpr'], model_ceftriaxone['roc']['tpr']
fpr5, tpr5 = model_cefepime['roc']['fpr'], model_cefepime['roc']['tpr']

roc_auc1 = auc(fpr1, tpr1)
roc_auc2 = auc(fpr2, tpr2)
roc_auc3 = auc(fpr3, tpr3)
roc_auc4 = auc(fpr4, tpr4)
roc_auc5 = auc(fpr5, tpr5)

plt.figure()

# plot ciprofloxacin model
plt.plot(fpr1, tpr1, color='red', label=f'Ciprofloxacin (AUC = {roc_auc1:.2f})')

# plot piperacillin model
plt.plot(fpr2, tpr2, color='blue', label=f'Piperacillin (AUC = {roc_auc2:.2f})')

# plot cefazolin model
plt.plot(fpr3, tpr3, color='green', label=f'Cefazolin (AUC = {roc_auc3:.2f})')

# plot ceftriaxone model
plt.plot(fpr4, tpr4, color='orange', label=f'Ceftriaxone (AUC = {roc_auc4:.2f})')

# plot cefepime model
plt.plot(fpr5, tpr5, color='purple', label=f'Cefepime (AUC = {roc_auc5:.2f})')

plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Diagonal line (no discrimination)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc='lower right')
plt.show()



### plot antibiotic orders saved in next 24 hours
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

# make df of 24h antibiotics
df_all_antibiotics_24h = []

#plot
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

