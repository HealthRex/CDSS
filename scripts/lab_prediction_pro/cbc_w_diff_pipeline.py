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


cohort_table_id = 'mining-clinical-decisions.conor_db.20220607_cbc_diff_cohort_small'
feature_table_id = 'mining-clinical-decisions.conor_db.20220607_cbc_features'
project_id='som-nero-phi-jonc101'
dataset = 'shc_core_2021'

parser = argparse.ArgumentParser(description='Pipeline to train CBC models')
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
    table_name='20220607_cbc_diff_cohort_small',
    label_columns=['label_WBC', 'label_HCT', 'label_PLT'])

query =f"""
WITH cbcd_lab_results as (
    SELECT DISTINCT
        anon_id,
        order_id_coded,
        order_time_utc as index_time,
        ordering_mode,
        base_name,
        CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
        ELSE 1
        END label
    FROM 
        {project_id}.{dataset}.lab_result
    WHERE 
        # Note no inpatient results where proc code was LABCBCD
        UPPER(group_lab_name) = 'CBC WITH DIFFERENTIAL'
    AND
        base_name in ('WBC', 'PLT', 'HCT')
    AND 
        EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2020
),

# Pivot lab result to wide
cohort_wide as (
    SELECT 
        * 
    FROM 
        cbcd_lab_results
    PIVOT (
        MAX(label) as label -- should be max of one value or no value 
        FOR base_name in ('WBC', 'PLT', 'HCT')
    )
    WHERE 
        -- only keep labs where all three components we care about result
        label_WBC is not NULL AND
        label_PLT is not NULL AND
        label_HCT is not NULL
)

### 2000 observations randomly sampled per year
SELECT 
    anon_id, order_id_coded as observation_id, index_time, ordering_mode,
    label_WBC, label_PLT, label_HCT
FROM 
     (SELECT *,
                ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                    ORDER BY RAND()) 
                AS seqnum
      FROM cohort_wide 
     ) 
WHERE 
    seqnum <= 100
"""

# Executes query, and stores cohort in a pandas dataframe in the `df` attribute
if args.cohort:
    cb.build_cohort(query)
    schema = [{'name': 'anon_id', 'type': 'STRING'},
            {'name': 'observation_id', 'type': 'INTEGER'}]
    # Writes the cohort to bigquery
    cb.write_cohort_table(overwrite='True', schema=schema)

if args.featurize:
    # featurizer = featurizers.BagOfWordsFeaturizerLight(
    #     cohort_table_id=cohort_table_id,
    #     feature_table_id=feature_table_id,
    #     outpath='./20220601_model_info/'
    # )
    # featurizer()
    featurizer = featurizers.SequenceFeaturizer(
        cohort_table_id=cohort_table_id,
        feature_table_id=feature_table_id,
        train_years=['2015', '2016', '2017', '2018'],
        val_years=['2019'],
        test_years=['2020'],
        label_columns=['label_WBC', 'label_PLT', 'label_HCT'],
        outpath='./20220607_model_info_seq/'
    )
    featurizer()

if args.train:
    working_dir = './20220607_model_info_seq/'
    run_name = 'test_run'

    
    # TODO where are your feature matrices stored?
    # trainer = trainers.BaselineModelTrainer(path)

    # Component 1 - Predict Hematocrit
    trainer(task='label_HCT')
