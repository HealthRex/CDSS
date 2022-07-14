import argparse
from google.cloud import bigquery
import os
import pandas as pd
import sys

from cohort_definitions import *
from trainers import *
from featurizers import *

import pdb

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/conorcorbin/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'
client = bigquery.Client()

parser = argparse.ArgumentParser(description='Pipeline to train CBC models')
parser.add_argument(
    '--run_name',
    required=True,
    help='Ex date of execution and cohort def'
)
parser.add_argument(
    '--cohort_table_name',
    default='cohort_table',
    help='Bigquery cohort table name'
)
parser.add_argument(
    '--feature_table_name',
    default='feature_matrix',
    help='Bigquery feature table name'
)
parser.add_argument(
    '--outpath',
    default='model_info',
    help='Out directory to write files to'
)
parser.add_argument(
    '--cohort', # note can add choices with choices= parameter
    default=None,
    help='Cohort to build'
)
parser.add_argument(
    '--featurizer',
    default=None,
    help='Featurizer to use'
)
parser.add_argument(
    '--trainer',
    default=None,
    help='Trainer to use'
)
parser.add_argument(
    "--tasks",
    default=[],  # set of tasks (name of label column)
    nargs="*",
)
parser.add_argument(
    '--working_dataset_name',
    default='conor_db',
    help='Bigquery dataset name where we store cohorts and features'
)
parser.add_argument(
    '--working_project_id',
    default='mining-clinical-decisions',
    help='Project id for temp tables'
)
parser.add_argument(
    '--project_id',
    default='som-nero-phi-jonc101',
    help='project id that holds dataset used to create cohort and features'
)
parser.add_argument(
    '--dataset',
    default='shc_core_2021',
    help='dataset used to create cohort and features'
)
parser.add_argument(
    '--tfidf',
    action='store_true',
    help='whether to transform bow with tfidf'
)
args = parser.parse_args()

# Dictionary lookup for arguments
cohort_builders = {
    'CBCWithDifferentialCohort': CBCWithDifferentialCohort,
    'MetabolicComprehensiveCohort': MetabolicComprehensiveCohort,
    'MagnesiumCohort': MagnesiumCohort,
    'BloodCultureCohort': BloodCultureCohort,
    'UrineCultureCohort': UrineCultureCohort
}
featurizers = {
    'BagOfWordsFeaturizerLight': BagOfWordsFeaturizerLight
}
trainers = {
    'BoostingTrainer': BoostingTrainer,
    'BaselineModelTrainer': BaselineModelTrainer
}

# Build cohort
if args.cohort is not None:
    cohort_builder = cohort_builders[args.cohort](
        client=client,
        dataset_name=args.working_dataset_name,
        table_name=f"{args.run_name}_{args.cohort_table_name}"
    )
    cohort_builder() # Call to build cohort

# Perform feature extraction
cohort_table = (f"{args.working_project_id}.{args.working_dataset_name}."
                f"{args.run_name}_{args.cohort_table_name}")
feature_table = (f"{args.working_project_id}.{args.working_dataset_name}."
                 f"{args.run_name}_{args.feature_table_name}")
if args.featurizer is not None:
    featurizer = featurizers[args.featurizer](
        cohort_table_id=cohort_table,
        feature_table_id=feature_table,
        outpath=f"./{args.run_name}_{args.outpath}",
        project=args.project_id,
        dataset=args.dataset,
        tfidf=args.tfidf
    )
    featurizer() # Call to featurizer

# Train model
if args.trainer is not None:
    trainer = trainers[args.trainer](
        working_dir=f"./{args.run_name}_{args.outpath}"
    )
    for task in args.tasks:
        trainer(task)
