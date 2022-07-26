import os
import sys
import argparse
sys.path.insert(1, '../../medinfo/dataconversion/')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/conorcorbin/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'mining-clinical-decisions'
import pandas as pd
import cohorts
import trainers
import featurizers


cohort_table_id = 'mining-clinical-decisions.conor_db.20220630_hemestamp_cohort_copy'
feature_table_id = 'mining-clinical-decisions.conor_db.20220630_hemestamp_features'
project_id='som-nero-phi-jonc101'
dataset = 'shc_core_2021'

parser = argparse.ArgumentParser(description='Pipeline to train Hemestamp models')
parser.add_argument(
    '--cohort',
    action='store_true',
    help='whether to build cohort'
)
parser.add_argument(
    '--featurize',
    action='store_true',
    help='whether to featurize'
)
parser.add_argument(
    '--train',
    action='store_true',
    help='whether to train'
)

args = parser.parse_args()


cb = cohorts.CohortBuilder(
    dataset_name='conor_db',
    table_name='20220630_hemestamp_cohort_copy',
    label_columns=['label_WBC', 'label_HCT', 'label_PLT'])

query =f"""
"""

# Executes query, and stores cohort in a pandas dataframe in the `df` attribute
if args.cohort:
    cb.build_cohort(query)
    schema = [{'name': 'anon_id', 'type': 'STRING'},
            {'name': 'observation_id', 'type': 'INTEGER'}]
    # Writes the cohort to bigquery
    cb.write_cohort_table(overwrite='True', schema=schema)

if args.featurize:
    featurizer = featurizers.BagOfWordsFeaturizerLight(
        cohort_table_id=cohort_table_id,
        feature_table_id=feature_table_id,
        outpath='./20220630_hemestamp_model_info/'
    )
    featurizer()
    # featurizer = featurizers.SequenceFeaturizer(
    #     cohort_table_id=cohort_table_id,
    #     feature_table_id=feature_table_id,
    #     train_years=['2015', '2016', '2017', '2018'],
    #     val_years=['2019'],
    #     test_years=['2020'],
    #     label_columns=['label_WBC', 'label_PLT', 'label_HCT'],
    #     outpath='./20220607_model_info_seq/'
    # )

if args.train:
    working_dir = './20220630_hemestamp_model_info/'
    trainer = trainers.BaselineModelTrainer(working_dir)
    trainer(task='label')
    # run_name = 'test_run'
    # TODO where are your feature matrices stored?
    # trainer = trainers.BaselineModelTrainer(path)

    # Component 1 - Predict Hematocrit
    # trainer(task='label_HCT')
