from google.cloud import bigquery
import os
import numpy as np
import pandas as pd
import sys
import yaml

# Edit to point to yours
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

 # your sunet id
suid='grolleau'
EXPERIMENT_NAME = f"20240604_costvariability_{suid}"
RUN_NAME = "baseline_inpatientmortality"

from healthrex_ml.cohorts import LongLengthOfStayCohort2023  

cohort = LongLengthOfStayCohort2023(
    client=client,
    dataset_name='francois_db',
    working_project_id='som-nero-phi-jonc101',
    table_name=f"{EXPERIMENT_NAME}_{RUN_NAME}_cohort"
)
cohort()

from healthrex_ml.extractors import (
    AgeExtractor,
    RaceExtractor,
    SexExtractor,
    EthnicityExtractor,
    ProcedureExtractor,
    PatientProblemExtractor,
    #PatientProblemGroupExtractor,
    MedicationExtractor,
    #MedicationGroupExtractor,
    LabOrderExtractor,
    LabResultBinsExtractor,
    #LabResultNumericalExtractor,
    FlowsheetBinsExtractor,
    DummyExtractor
)

USED_EXTRACTORS = [
    AgeExtractor,
    RaceExtractor,
    SexExtractor,
    EthnicityExtractor,
    ProcedureExtractor,
    PatientProblemExtractor,
    #PatientProblemGroupExtractor,
    MedicationExtractor,
    #MedicationGroupExtractor,
    LabOrderExtractor,
    LabResultBinsExtractor,
    #LabResultNumericalExtractor,
    FlowsheetBinsExtractor,
    DummyExtractor
]

cohort_table=f"{cohort.project_id}.{cohort.dataset_name}.{cohort.table_name}"
feature_table=f"{cohort.project_id}.{cohort.dataset_name}.{RUN_NAME}_feature_matrix"

extractors = [
    ext(cohort_table_id=cohort_table, feature_table_id=feature_table)
    for ext in USED_EXTRACTORS]

from healthrex_ml.featurizers import BagOfWordsFeaturizer

featurizer = BagOfWordsFeaturizer(
        cohort_table_id=cohort_table,
        feature_table_id=feature_table,
        extractors=extractors,
        outpath=f"./{RUN_NAME}_artifacts",
        tfidf=True
)

# Run the featurizer
featurizer()