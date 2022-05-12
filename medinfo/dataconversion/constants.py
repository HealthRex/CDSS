# Constants to import 

DEFAULT_DEPLOY_CONFIG = {
    'Categorical': {
        'Sex': [{'look_back' : None}],
        'Race': [{'look_back' : None}],
        'Diagnoses': [{'look_back' : None}],
        'Medications': [{'look_back' : 28}]
    },
    'Numerical': {
        'Age': [{'look_back': None, 'num_bins': 5}],
        'LabResults': [{'look_back': 14, 'num_bins': 5}],
        #'Vitals': [{'look_back': 3, 'num_bins': 5}]
    }
}

DEFAULT_LAB_COMPONENT_IDS = [
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


DEFAULT_FLOWSHEET_FEATURES = [
    "Heart Rate",
    "Temp",
    "Resp",
    "SpO2",
    'BP_High_Systolic',
    "BP_Low_Diastolic"
]
