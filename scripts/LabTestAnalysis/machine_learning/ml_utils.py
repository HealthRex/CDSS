

'''

Only operational functions
Not aware of file system organization

'''
import pandas as pd
import os


BASIC_LAB_COMPONENTS = [
                'WBC',  # White Blood Cell
                'HCT',  # Hematocrit
                'PLT',  # Platelet Count
                'NA',  # Sodium, Whole Blood
                'K',  # Potassium, Whole Blood
                'CO2',  # CO2, Serum/Plasma
                'BUN',  # Blood Urea Nitrogen
                'CR',  # Creatinine
                'TBIL',  # Total Bilirubin
                'ALB',  # Albumin
                'CA',  # Calcium
                'LAC',  # Lactic Acid
                'ESR',  # Erythrocyte Sedimentation Rate
                'CRP',  # C-Reactive Protein
                'TNI',  # Troponin I
                'PHA',  # Arterial pH
                'PO2A',  # Arterial pO2
                'PCO2A',  # Arterial pCO2
                'PHV',  # Venous pH
                'PO2V',  # Venous pO2
                'PCO2V'  # Venous pCO2
            ]

map_component_from_Stanford_to_UCSF = {
'CR': 'CREAT',
'PO2A': 'PO2',
'PO2V': 'PO2',
'PCO2A': 'PCO2',
'PCO2V': 'PCO2',
'PHOS': 'PO4',
'CAION': 'CAI',
'TNI': 'TRPI',
'NA': 'NA',
'LAC': 'LACTWB',
'TBIL': 'TBILI'
}

map_cormobidity_from_Stanford_to_UCSF = {
'Malignancy': 'Cancer',
'CHF': 'CongestiveHeartFailure',
'MI': 'MyocardialInfarction',
'Cerebrovascular': 'CerebrovascularDisease',
'Diabetes': 'Diabeteswithoutcomplications'
}

map_team_from_Stanford_to_UCSF = {
'CVICU': 'ICU'
}

map_vitals_from_Stanford_to_UCSF = {
'BP_Low_Diastolic': 'DBP',
'BP_High_Systolic': 'SBP'
}

map_panel_from_Stanford_to_UCSF = {'LABMGN':'Magnesium, Serum - Plasma',
               'LABCAI':'Calcium, Ionized, serum-plasma',
                            'LABURIC':'Uric Acid, Serum - Plasma',
                            'LABALB':'Albumin, Serum - Plasma',
                            'LABTSH':'Thyroid Stimulating Hormone',
                            'LABTNI':'Troponin I',
                            'LABK':'Potassium, Serum - Plasma',
                            'LABNA':'Sodium, Serum - Plasma',
                            # 'LABBLC':'Peripheral Blood Culture', # TODO
                            'LABBLC2':'Peripheral Blood Culture',
                            'LABPHOS':'Phosphorus, Serum - Plasma',
                            'LABPT':'Prothrombin Time', # TODO
                            'LABPTT':'Activated Partial Thromboplastin Time'
                            }

def map_lab(lab, data_source, lab_type):
    import LocalEnv
    ml_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/machine_learning')
    df = pd.read_csv(os.path.join(ml_folder, 'data_conversion/map_%s_%s_raw2code.csv'%(data_source,lab_type)),
                     keep_default_na=False)
    keys = df['raw'].values.tolist()
    vals = df['lab'].values.tolist()
    my_dict = dict(zip(keys, vals))

    # print lab, my_dict[lab]

    return my_dict.get(lab, lab)

def get_patIds(data_matrix):
    return set(data_matrix['pat_id'].values.tolist())

def test_get_baseline():
    df_1 = pd.DataFrame([[123, '2014-01-01', 1, 2]], columns=['pat_id', 'order_time', 'actual', 'predict'])
    df_2 = pd.DataFrame([[456, '2015-01-01', 3]], columns=['pat_id', 'order_time', 'actual'])
    print get_baseline(df_1, df_2)
    # assert df's not changed


def get_baseline(df_train, df_test, y_label):
    print df_test[['pat_id', 'order_time', y_label]].copy().head()
    df_res = df_test[['pat_id', 'order_time', y_label]].copy().rename(columns={y_label:'actual'}) # Not change the input

    prevalence = float(df_train[y_label].values.sum()) / float(df_train.shape[0])

    df_res['predict'] = df_res['actual'].apply(lambda x: prevalence) # use any column to create an extra column

    df_res = df_res.sort_values(['pat_id', 'order_time']).reset_index()
    for i in range(1, df_res.shape[0]):
        if df_res.ix[i-1, 'pat_id'] == df_res.ix[i, 'pat_id']:
            df_res.ix[i, 'predict'] = df_res.ix[i-1, 'actual']

    return df_res[['actual', 'predict']]



if __name__ == '__main__':
    test_get_baseline()
