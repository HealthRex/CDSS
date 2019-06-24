# glucose-control
_Prediction and classification (low, normal, high) of glucose levels based on information extracted from EHR data_

## directory tree and file usage
* data
  - bq --queried EHR data in CSV files
  - preprocessed -- filtered and preocessed data, feature matrix
  - plots -- output plots for dataset
    * patients -- output plots for specific patients
* code
  - queries.sql -- BigQuery commands to extract EHR data from datalake
  - 1filterPatient.py -- filtering patients with usable EHR data
  - 2constructFeatures.py -- feature engineering
  - 3regression.py -- prediction of glucose levels
  - 4classification.py -- classification (low, normal, high) of glucose levels

## project report (draft)
[project report (draft) 190608](project-report-draft.pdf)
