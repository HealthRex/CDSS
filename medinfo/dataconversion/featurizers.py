"""
Definition of BagOfWordsFeaturizer
TODO: Definition of SummaryStatsFeaturizer
TODO: Definition of TimelineFeaturizer
"""
import json
import os
from re import S
from typing_extensions import Self
import pandas as pd
import pickle
from google.cloud import bigquery
import numpy as np
from tqdm import tqdm
from scipy.sparse import csr_matrix
from scipy.sparse import save_npz

from constants import DEFAULT_DEPLOY_CONFIG
from constants import DEFAULT_LAB_COMPONENT_IDS
from constants import DEFAULT_FLOWSHEET_FEATURES
import FeatureExtractor as fextractors

import pdb

class SequenceFeaturizer():
    """
    Uses FeatureExtractors to generate a set of variable lengh sequences
    for each observation. Saves these sequences as invididual numpy arrays in 
    npz format. The npz contains the following data elements
    NPZ structure:
         sequence: array of tokens - continuous features must be binned
         time_deltas: array with same length as sequence, hours to index time
         label: list of labels corresponding to seq (len=1 if only one label). 
    """

    def __init__(self, cohort_table_id, feature_table_id, train_years,
                 val_years, test_years, label_columns, outpath='./features',
                 project='som-nero-phi-jonc101', dataset='shc_core_2021',
                 feature_config=None):
        """
        Args:
            cohort_table_id: ex 'mining-clinical-decisions.conor_db.table_name'
            feature_table_id: ex
                'mining-clinical-decisions.conor_db.feature_table'
            train_years: list of years to include in training set
            val_years: list of years to include in validation set
            test_years: list of years to include in the test set
            label_columns: list of columns desingated as labels in cohort table
            outpath: path to dump feature matrices
            project: bq project id to extract data from
            dataset: bq dataset with project to extract data from
            feature_config: dictionary with feature types, bins and look back
                windows.
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.outpath = outpath
        self.project = project
        self.dataset = dataset
        if feature_config is None:
            self.feature_config = DEFAULT_DEPLOY_CONFIG
        else:
            self.feature_config = feature_config
        self.client = bigquery.Client()
        self.train_years = [int(y) for y in train_years]
        self.val_years = [int(y) for y in val_years]
        self.test_years = [int(y) for y in test_years]
        self.label_columns = label_columns

    def __call__(self):
        """
        Generates sequence feature vectors and saves to outpath
        """
        label_cols = ', '.join([f"c.{l}" for l in self.label_columns])
        self.construct_feature_timeline()
        query = f"""
        SELECT
            f.*, {label_cols}
        FROM
            {self.feature_table_id} f
        INNER JOIN
            {self.cohort_table_id} c
        USING
            (observation_id)
        ORDER BY
            observation_id, feature_time
        """
        df = pd.read_gbq(query, progress_bar_type='tqdm')

        # Get time deltas in hours from index time
        df = df.assign(time_deltas=lambda x: 
            (x.index_time - x.feature_time).astype('timedelta64[D]')
        )
        
        # Split into train, val and test and ensure only terms in train are used
        train_seqs = df[df['index_time'].dt.year.isin(
            self.train_years)]
        vocab = train_seqs.feature.unique()
        vocab_set = set([s for s in vocab])
        val_seqs = df[df['index_time'].dt.year.isin(
            self.val_years)].query("feature in @vocab_set", engine='python')
        test_seqs = df[df['index_time'].dt.year.isin(
            self.test_years)].query("feature in @vocab_set", engine='python')
        seq_dict = {'train' : train_seqs, 'val' :  val_seqs, 'test' : test_seqs}

        # Create working directory if does not already exist and save features
        for dataset, seqs in seq_dict.items():
            os.makedirs(os.path.join(self.outpath, dataset), exist_ok=True)
            for obs in seqs.observation_id.unique():
                example = seqs[seqs['observation_id']==obs]
                sequence = example.feature.values
                time_deltas = example.time_deltas.values
                labels = example[self.label_columns].values
                np.savez(os.path.join(self.outpath, dataset, f"{obs}.npz"),
                         sequence=sequence,
                         time_deltas=time_deltas,
                         labels=labels)
                
        # Save feature vocab
        np.savez(os.path.join(self.outpath, dataset, 'feature_vocab.npz'),
                 vocab=vocab)
                
        # Save bin thresholds if they exist
        self.df_lup = pd.DataFrame()
        for lup in self.lups:
            if lup is not None:
                self.df_lup = pd.concat([self.df_lup, lup])
        if not self.df_lup.empty:
            self.df_lup.to_csv(os.path.join(self.outpath, 'bin_lup.csv'),
                               index=None)

        # Save feature_config
        with open(os.path.join(self.outpath, 'feature_config.json'), 'w') as f:
            json.dump(self.feature_config, f)

    def construct_feature_timeline(self):
        """
        Executes all logic to iteratively append rows to the biq query long form
        feature matrix destination table.  Does this by iteratively joining
        cohort table to tables with desired features, filtering for events
        that occur within each look up range, and then transforming into bag of
        words style representations.  Features with numerical values are binned
        into buckets to enable bag of words repsesentation. 
        """
        extractors = []
        # Get categorical features
        if 'Sex' in self.feature_config['Categorical']:
            se = fextractors.SexExtractor(
                self.cohort_table_id, self.feature_table_id)
            extractors.append(se)
        if 'Race' in self.feature_config['Categorical']:
            re = fextractors.RaceExtractor(self.cohort_table_id,
                                           self.feature_table_id)
            extractors.append(re)
        if 'Diagnoses' in self.feature_config['Categorical']:
            pe = fextractors.PatientProblemExtractor(
                self.cohort_table_id, self.feature_table_id)
            extractors.append(pe)
        if 'Medications' in self.feature_config['Categorical']:
            me = fextractors.MedicationExtractor(
                self.cohort_table_id, self.feature_table_id)
            extractors.append(me)

        # Get numerical features
        if 'Age' in self.feature_config['Numerical']:
            ae = fextractors.AgeExtractor(
                self.cohort_table_id,
                self.feature_table_id,
                bins=self.feature_config['Numerical']['Age'][0]['num_bins'])
            extractors.append(ae)
        if 'LabResults' in self.feature_config['Numerical']:
            lre = fextractors.LabResultBinsExtractor(
                self.cohort_table_id,
                self.feature_table_id,
                bins=self.feature_config['Numerical']
                ['LabResults'][0]['num_bins'],
                base_names=DEFAULT_LAB_COMPONENT_IDS)
            extractors.append(lre)
        if 'Vitals' in self.feature_config['Numerical']:
            fbe = fextractors.FlowsheetBinsExtractor(
                self.cohort_table_id,
                self.feature_table_id,
                bins=self.feature_config['Numerical']['Vitals'][0]['num_bins'],
                base_names=DEFAULT_FLOWSHEET_FEATURES)
            extractors.append(fbe)

        # Call extractors and collect any look up tables
        self.lups = []
        for extractor in tqdm(extractors):
            self.lups.append(extractor())


class BagOfWordsFeaturizerLight():
    """
    Bag of words but uses FeatureExtractors instead of burying all SQL logic
    as in implementation below. 
    """

    def __init__(self, cohort_table_id, feature_table_id, outpath='./features',
                 project='som-nero-phi-jonc101', dataset='shc_core_2021',
                 feature_config=None):
        """
        Args:
            cohort_table_id: ex 'mining-clinical-decisions.conor_db.table_name'
            feature_table_id: ex 
                'mining-clinical-decisions.conor_db.feature_table'
            outpath: path to dump feature matrices
            project: bq project id to extract data from
            dataset: bq dataset with project to extract data from
            feature_config: dictionary with feature types, bins and look back
                windows. 
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.outpath = outpath
        self.project = project
        self.dataset = dataset
        if feature_config is None:
            self.feature_config = DEFAULT_DEPLOY_CONFIG
        else:
            self.feature_config = feature_config
        self.client = bigquery.Client()
        # Get data splits (default last year of data held out as test set)
        split_query = f"""
            SELECT DISTINCT
                EXTRACT(YEAR FROM index_time) year
            FROM
                {self.cohort_table_id}
        """
        df = pd.read_gbq(split_query).sort_values('year')
        self.train_years = df.year.values[:-1]
        self.test_years = [df.year.values[-1]]
        self.replace_table = True

    def __call__(self):
        """
        Executes all logic to construct features and labels and saves all info
        user specified working directory.
        """
        self.construct_feature_timeline()
        self.construct_bag_of_words_rep()
        query = f"""
        SELECT
            *
        FROM
            {self.feature_table_id}_bow
        ORDER BY
            observation_id
        """
        df = pd.read_gbq(query, progress_bar_type='tqdm')
        train_features = df[df['index_time'].dt.year.isin(self.train_years)]
        apply_features = df[~df['index_time'].dt.year.isin(self.train_years)]
        train_csr, train_ids, train_vocab = self.construct_sparse_matrix(
            train_features, train_features)
        test_csr, test_ids, test_vocab = self.construct_sparse_matrix(
            train_features, apply_features)

        # Query cohort table for labels
        q_cohort = f"""
            SELECT
                *
            FROM
               {self.cohort_table_id}
            ORDER BY
                observation_id
        """
        df_cohort = pd.read_gbq(q_cohort, progress_bar_type='tqdm')
        train_labels = df_cohort[df_cohort['index_time'].dt.year.isin(
            self.train_years)]
        test_labels = df_cohort[~df_cohort['index_time'].dt.year.isin(
            self.train_years)]

        # Sanity check - make sure ids from labels and features in same order
        for a, b in zip(train_labels['observation_id'].values, train_ids):
            try:
                assert a == b
            except:
                pdb.set_trace()
        for a, b in zip(test_labels['observation_id'].values, test_ids):
            assert a == b

        # Create working directory if does not already exist and save features
        os.makedirs(self.outpath, exist_ok=True)
        save_npz(os.path.join(self.outpath, 'train_features.npz'), train_csr)
        save_npz(os.path.join(self.outpath, 'test_features.npz'), test_csr)
        print(f"Feature matrix generated with {train_csr.shape[1]} features")

        # Save labels
        train_labels.to_csv(os.path.join(self.outpath, 'train_labels.csv'),
                            index=None)
        test_labels.to_csv(os.path.join(self.outpath, 'test_labels.csv'),
                           index=None)

        # Save feature order
        df_vocab = pd.DataFrame(data={
            'features': [t for t in train_vocab],
            'indices': [train_vocab[t] for t in train_vocab]
        })
        df_vocab.to_csv(os.path.join(self.outpath, 'feature_order.csv'),
                        index=None)

        # Save bin thresholds if they exist
        self.df_lup = pd.DataFrame()
        for lup in self.lups:
            if lup is not None:
                self.df_lup = pd.concat([self.df_lup, lup])
        if not self.df_lup.empty:
            self.df_lup.to_csv(os.path.join(self.outpath, 'bin_lup.csv'),
                            index=None)

        # Save feature_config
        with open(os.path.join(self.outpath, 'feature_config.json'), 'w') as f:
            json.dump(self.feature_config, f)

    def construct_feature_timeline(self):
        """
        Executes all logic to iteratively append rows to the biq query long form
        feature matrix destination table.  Does this by iteratively joining
        cohort table to tables with desired features, filtering for events
        that occur within each look up range, and then transforming into bag of
        words style representations.  Features with numerical values are binned
        into buckets to enable bag of words repsesentation. 
        """
        extractors = []
        # Get categorical features
        if 'Sex' in self.feature_config['Categorical']:
            se = fextractors.SexExtractor(
                self.cohort_table_id, self.feature_table_id)
            extractors.append(se)
        if 'Race' in self.feature_config['Categorical']:
            re = fextractors.RaceExtractor(self.cohort_table_id,
                self.feature_table_id)
            extractors.append(re)
        if 'Diagnoses' in self.feature_config['Categorical']:
            pe = fextractors.PatientProblemExtractor(
                self.cohort_table_id, self.feature_table_id)
            extractors.append(pe)
        if 'Medications' in self.feature_config['Categorical']:
            me = fextractors.MedicationExtractor(
                self.cohort_table_id, self.feature_table_id)
            extractors.append(me)

        # Get numerical features
        if 'Age' in self.feature_config['Numerical']:
            ae = fextractors.AgeExtractor(
                self.cohort_table_id,
                self.feature_table_id,
                bins=self.feature_config['Numerical']['Age'][0]['num_bins'])
            extractors.append(ae)
        if 'LabResults' in self.feature_config['Numerical']:
            lre = fextractors.LabResultBinsExtractor(self.cohort_table_id,
                                         self.feature_table_id,
                                         bins=self.feature_config['Numerical']
                                         ['LabResults'][0]['num_bins'],
                                         base_names=DEFAULT_LAB_COMPONENT_IDS)
            extractors.append(lre)
        if 'Vitals' in self.feature_config['Numerical']:
            fbe = fextractors.FlowsheetBinsExtractor(
                self.cohort_table_id,
                self.feature_table_id,
                bins=self.feature_config['Numerical']['Vitals'][0]['num_bins'],
                base_names=DEFAULT_FLOWSHEET_FEATURES)
            extractors.append(fbe)

        # Call extractors and collect any look up tables
        self.lups = []
        for extractor in tqdm(extractors):
            self.lups.append(extractor())

        # Call extractors and collect any look up tables
        self.lups = []
        for extractor in tqdm(extractors):
            self.lups.append(extractor())
    
    def construct_bag_of_words_rep(self):
        """
        Transforms long form feature timeline into a bag of words feature
        matrix. Stores as a new table in the given bigquery database but also
        constructs local sparse matrices that can be fed into various sklearn
        style classifiers. 
        """

        # Go from timeline to counts
        query = f"""
        CREATE OR REPLACE TABLE {self.feature_table_id}_bow AS (
        SELECT 
            observation_id, index_time, feature_type, feature, COUNT(*) value 
        FROM 
            {self.feature_table_id}
        WHERE 
            feature_type IS NOT NULL
        AND
            feature IS NOT NULL
        GROUP BY 
            observation_id, index_time, feature_type, feature
        )
        """
        query_job = self.client.query(query)
        query_job.result()

    def construct_sparse_matrix(self, train_features, apply_features):
        """
        Takes long form feature timeline matrix and builds up a scipy csr
        matrix without the costly pivot operation. 
        """
        train_features = (train_features
                          .groupby('observation_id')
                          .agg({'feature': lambda x: list(x),
                                'value': lambda x: list(x)})
                          .reset_index()
                          )
        train_feature_names = [doc for doc in train_features.feature.values]
        train_feature_values = [doc for doc in train_features['value'].values]
        train_obs_id = [id_ for id_ in train_features.observation_id.values]

        apply_features = (apply_features
                          .groupby('observation_id')
                          .agg({'feature': lambda x: list(x),
                                'value': lambda x: list(x)})
                          .reset_index()
                          )
        apply_features_names = [doc for doc in apply_features.feature.values]
        apply_features_values = [doc for doc in apply_features['value'].values]
        apply_obs_id = [id_ for id_ in apply_features.observation_id.values]

        vocabulary = self._build_vocab(train_feature_names)
        indptr = [0]
        indices = []
        data = []
        for i, d in enumerate(apply_features_names):
            for j, term in enumerate(d):
                if term not in vocabulary:
                    continue
                else:
                    indices.append(vocabulary[term])
                    data.append(apply_features_values[i][j])
                if j == 0:
                    # Add zero to data and max index in vocabulary to indices in
                    # case max feature indice isn't in apply features.
                    indices.append(len(vocabulary)-1)
                    data.append(0)
            indptr.append(len(indices))

        csr_data = csr_matrix((data, indices, indptr), dtype=float)

        return csr_data, apply_obs_id, vocabulary

    def _build_vocab(self, data):
        """
        Builds vocabulary of terms from the data. Assigns each unique term
        to a monotonically increasing integer
        """
        vocabulary = {}
        for i, d in enumerate(data):
            for j, term in enumerate(d):
                vocabulary.setdefault(term, len(vocabulary))
        return vocabulary


class BagOfWordsFeaturizer(object):
    """
    A class containing all logic to construct a bag of words feature matrix
    given a cohort and user provided feature configurations. 

    This featurizer supports the construction of a bag of words style feature
    matrix where each column in the resulting matrix is the number of times a 
    certain event (ex lab order, diagnosis code, medication order) occurs
    in the patients timeline in a given time window prior to index time. 

    Categorical variables are trivial to represent in bag of words style.
    Numerical variables (ie lab results, vital signs, age) are first binned into
    user specified number of buckets so that they can be represented in similar 
    fashion.

    Feature matrices are constructed as csr matrices (sparse matrices) to allow
    for feature representations that would otherwise use ungodly amounts of
    RAM.  Sparse matrices are constructed directly from a long form feature
    matrix representation to avoid the costly pivot operation. 

    The user is able to specify various desired feature types and their look
    back windows in a provided configuration dictionary. 
    """

    def __init__(self, cohort_table, label_columns, working_dataset_name, 
                 table_name, project_id='mining-clinical-decisions',
                 outpath='./features', dataset='shc_core_2021',
                 working_project_id='mining-clinical-decisions',
                 feature_config=None):
        """
        Initializes featurizer
        Args:
            cohort_table: location of cohort table {dataset_name}.{table_name}
            label_columns: which columns in cohort table used as labels
            dataset_name: big query dataset name - where to save long form
                feature matrix.
            table_name: big query table name - where to save long form feature
                matrix
            project_id: id of big query project
            feature_config: configure which features types to extract and their
                look back windows. If none uses default defined below
        """
        self.df_lup = pd.DataFrame()
        self.outpath = outpath
        self.cohort_table = cohort_table
        self.label_columns = label_columns
        self.dataset_name = working_dataset_name
        self.dataset = dataset
        self.table_name = table_name
        self.project_id = project_id
        self.working_proj_id = working_project_id
        self.client = bigquery.Client()
        self.create_table = True  # starts true then append
        if feature_config is None:
            self.feature_config = DEFAULT_DEPLOY_CONFIG
        else:
            self.feature_config = feature_config
            ### TODO : write code to test whether user specified config is
            ### adequate

        # Get data splits (default last year of data held out as test set)
        split_query = f"""
            SELECT DISTINCT
                EXTRACT(YEAR FROM index_time) year
            FROM
                {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
        """
        df = pd.read_gbq(split_query).sort_values('year')
        self.train_years = df.year.values[:-1]
        self.test_years = [df.year.values[-1]]

        self.feature_timeline_schema = [
            {'name': 'observation_id', 'type': 'INTEGER'},
            {'name': 'index_time', 'type': 'TIMESTAMP'},
            {'name': 'feature_type', 'type': 'STRING'},
            {'name': 'feature_time', 'type': 'TIMESTAMP'},
            {'name': 'feature_id', 'type': 'INTEGER'},
            {'name': 'feature', 'type': 'STRING'},
            {'name': 'value', 'type': 'INTEGER'}
        ]

    def __call__(self):
        """
        Executes all logic to construct features and labels and saves all info
        user specified working directory. 
        """
        self.construct_feature_timeline()
        self.construct_bag_of_words_rep()
        query = f"""
        SELECT 
            * 
        FROM 
            {self.working_proj_id}.{self.dataset_name}.{self.table_name}_bow
        ORDER BY
            observation_id
        """
        df = pd.read_gbq(query, progress_bar_type='tqdm')
        train_features = df[df['index_time'].dt.year.isin(self.train_years)]
        apply_features = df[~df['index_time'].dt.year.isin(self.train_years)]
        train_csr, train_ids, train_vocab = self.construct_sparse_matrix(
            train_features, train_features)
        test_csr, test_ids, test_vocab = self.construct_sparse_matrix(
            train_features, apply_features)

        # Query cohort table for labels
        q_cohort = f"""
            SELECT 
                * 
            FROM 
                {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            ORDER BY
                observation_id
        """
        df_cohort = pd.read_gbq(q_cohort, progress_bar_type='tqdm')
        train_labels = df_cohort[df_cohort['index_time'].dt.year.isin(
            self.train_years)]
        test_labels = df_cohort[~df_cohort['index_time'].dt.year.isin(
            self.train_years)]

        # Sanity check - make sure ids from labels and features in same order
        for a, b in zip(train_labels['observation_id'].values, train_ids):
            try:
                assert a == b
            except:
                pdb.set_trace()
        for a, b in zip(test_labels['observation_id'].values, test_ids):
            assert a == b

        # Create working directory if does not already exist and save features
        os.makedirs(self.outpath, exist_ok=True)
        save_npz(os.path.join(self.outpath, 'train_features.npz'), train_csr)
        save_npz(os.path.join(self.outpath, 'test_features.npz'), test_csr)
        print(f"Feature matrix generated with {train_csr.shape[1]} features")

        # Save labels
        train_labels.to_csv(os.path.join(self.outpath, 'train_labels.csv'),
                            index=None)
        test_labels.to_csv(os.path.join(self.outpath, 'test_labels.csv'),
                           index=None)

        # Save feature order
        df_vocab = pd.DataFrame(data={
            'features': [t for t in train_vocab],
            'indices': [train_vocab[t] for t in train_vocab]
        })
        df_vocab.to_csv(os.path.join(self.outpath, 'feature_order.csv'),
                        index=None)

        # Save bin thresholds if they exist
        if not self.df_lup.empty:
            self.df_lup.to_csv(os.path.join(self.outpath, 'bin_lup.csv'),
                            index=None)

        # Save feature_config
        with open(os.path.join(self.outpath, 'feature_config.json'), 'w') as f:
            json.dump(self.feature_config, f)

    def construct_feature_timeline(self):
        """
        Executes all logic to iteratively append rows to the biq query long form
        feature matrix destination table.  Does this by iteratively joining
        cohort table to tables with desired features, filtering for events
        that occur within each look up range, and then transforming into bag of
        words style representations.  Features with numerical values are binned
        into buckets to enable bag of words repsesentation. 
        """

        # Get categorical features
        if 'Sex' in self.feature_config['Categorical']:
            self._get_sex_features()
        if 'Race' in self.feature_config['Categorical']:
            self._get_race_features()
        if 'Diagnoses' in self.feature_config['Categorical']:
            self._get_diagnoses_features()
        if 'Medications' in self.feature_config['Categorical']:
            self._get_medication_features()

        # Get numerical features
        if 'Age' in self.feature_config['Numerical']:
            self._get_age_features()
        if 'LabResults' in self.feature_config['Numerical']:
            self._get_lab_results_features()
        if 'Vitals' in self.feature_config['Numerical']:
            self._get_vital_sign_features()

        # Add token which is one if no features are present for a patient
        self._get_missingness_features()

    def construct_bag_of_words_rep(self):
        """
        Transforms long form feature timeline into a bag of words feature
        matrix. Stores as a new table in the given bigquery database but also
        constructs local sparse matrices that can be fed into various sklearn
        style classifiers. 
        """

        # Go from timeline to counts
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.working_proj_id}.{self.dataset_name}.{self.table_name}_bow AS (

        SELECT 
            observation_id, index_time, feature_type, feature, COUNT(*) value 
        FROM 
            {self.working_proj_id}.{self.dataset_name}.{self.table_name}
        WHERE 
            feature_type IS NOT NULL
        AND
            feature IS NOT NULL
        GROUP BY 
            observation_id, index_time, feature_type, feature
        )
        """
        query_job = self.client.query(query)
        query_job.result()

    def construct_sparse_matrix(self, train_features, apply_features):
        """
        Takes long form feature timeline matrix and builds up a scipy csr
        matrix without the costly pivot operation. 
        """
        train_features = (train_features
                          .groupby('observation_id')
                          .agg({'feature': lambda x: list(x),
                                'value': lambda x: list(x)})
                          .reset_index()
                          )
        train_feature_names = [doc for doc in train_features.feature.values]
        train_feature_values = [doc for doc in train_features['value'].values]
        train_obs_id = [id_ for id_ in train_features.observation_id.values]

        apply_features = (apply_features
                          .groupby('observation_id')
                          .agg({'feature': lambda x: list(x),
                                'value': lambda x: list(x)})
                          .reset_index()
                          )
        apply_features_names = [doc for doc in apply_features.feature.values]
        apply_features_values = [doc for doc in apply_features['value'].values]
        apply_obs_id = [id_ for id_ in apply_features.observation_id.values]

        vocabulary = self._build_vocab(train_feature_names)
        indptr = [0]
        indices = []
        data = []
        for i, d in enumerate(apply_features_names):
            for j, term in enumerate(d):
                if term not in vocabulary:
                    continue
                else:
                    indices.append(vocabulary[term])
                    data.append(apply_features_values[i][j])
                if j == 0:
                    # Add zero to data and max index in vocabulary to indices in
                    # case max feature indice isn't in apply features.
                    indices.append(len(vocabulary)-1)
                    data.append(0)
            indptr.append(len(indices))

        csr_data = csr_matrix((data, indices, indptr), dtype=float)

        return csr_data, apply_obs_id, vocabulary

    def _build_vocab(self, data):
        """
        Builds vocabulary of terms from the data. Assigns each unique term
        to a monotonically increasing integer
        """
        vocabulary = {}
        for i, d in enumerate(data):
            for j, term in enumerate(d):
                vocabulary.setdefault(term, len(vocabulary))
        return vocabulary

    def get_binned_features(self, df_train, df_apply, num_bins):
        """
        Bins numerical features into specified number of bins based on
        percentile values.  Uses training set to define cutoffs values across
        each bin. 

        Args:
            df_train: dataframe of long form feature timeline for numerical
                features for observations in the training set
            df_apply: dataframe of long form feature timeline for numerical
                features for osbervations in th test set
        Returns:
            df_binned : dataframe of long form feature timeline where the bin
                associated with feature is specified in feature name and the
                value is 1
        """
        def _get_appropriate_bin(feature, val, lut):
            """
            Helper to map value to bin
            """
            try:
                mins = lut[feature]['min']
            except:  # feature not found in training set
                return 0  # removed in downstream processing
            for i in range(len(mins)-1):
                if i == 0 and val < mins[i]:
                    return i
                if val >= mins[i] and val < mins[i+1]:
                    return i
            return len(mins) - 1  # in last bin

        ranks = df_train.groupby('feature')['value'].rank(pct=True).values
        df_train = (df_train
                    .assign(bins=[int(r * num_bins) for r in ranks])
                    )
        df_lup = (df_train
                  .groupby(['feature', 'bins'])
                  .agg(bin_min=('value', 'min'), bin_max=('value', 'max'))
                  .reset_index()
                  )

        # Append to look up table we'll save later
        self.df_lup = pd.concat([self.df_lup, df_lup])

        # Convert df_lup to dictionary for faster bin look up.
        lut_dict = {}
        for feature in df_lup.feature.unique():
            df_lup_feature = df_lup[df_lup['feature'] == feature]
            for bin in df_lup_feature.bins.unique():
                if feature not in lut_dict:
                    lut_dict[feature] = {}
                    lut_dict[feature]['min'] = []
                    lut_dict[feature]['max'] = []
                lut_dict[feature]['min'].append(df_lup_feature
                    .query("bins == @bin", engine='python')
                    ['bin_min'].values[0]
                )
                lut_dict[feature]['max'].append(df_lup_feature
                    .query("bins == @bin", engine='python')
                    ['bin_max'].values[0]
                )

        df_binned = (df_apply
                     .assign(bins=lambda x:
                             [_get_appropriate_bin(a, b, lut_dict)
                              for a, b in zip(x.feature, x.value)]
                             )
                     .assign(feature=lambda x:
                             [f"{a}_{b}" for a, b in zip(x.feature, x.bins)],
                             value=1
                             )
                     .drop('bins', axis=1)
                     )

        return df_binned

    def _get_missingness_features(self):
        """
        Finds patients that exist in cohort but not current feature matrix,
        adds token 'missing' feature which takes value 1. 
        """
        query=f"""
        INSERT INTO 
            {self.working_proj_id}.{self.dataset_name}.{self.table_name}
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            "Missing indicator" feature_type,
            labels.index_time feature_time,
            UNIX_DATE(CAST(labels.index_time as DATE)) as feature_id,
            'no features' as feature,
            1 as value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            labels
        LEFT JOIN
            {self.working_proj_id}.{self.dataset_name}.{self.table_name} feats
        USING
            (observation_id)
        WHERE 
            feats.observation_id IS NULL
        """
        query_job = self.client.query(query)
        query_job.result()

    def _get_sex_features(self):
        """
        Get's sex demographic features for patients in cohort and appends to
        long form feature matrix on bigquery.
        """
        if self.create_table:
            prefix = (
                f"CREATE OR REPLACE TABLE {self.working_proj_id}."
                f"{self.dataset_name}.{self.table_name} AS("
            )
            suffix = ")"
        else:
            prefix = (
                f"INSERT INTO {self.working_proj_id}.{self.dataset_name}"
                f".{self.table_name}"
            )
            suffix = ""

        query = f"""
        {prefix}
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            1 as feature_id,
            CASE WHEN demo.GENDER is NULL then 'sex_missing'
            ELSE CONCAT('sex_', demo.GENDER) END feature,
            1 value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        {suffix}
        """
        print("Featurizing sex")
        query_job = self.client.query(query)
        query_job.result()
        self.create_table = False

    def _get_race_features(self):
        """
        Get's race demographic features for each patient in cohort and appends
        to long form feature matrix on bigquery. 
        """
        if self.create_table:
            prefix = (
                f"CREATE OR REPLACE TABLE {self.working_proj_id}."
                f"{self.dataset_name}.{self.table_name} AS("
            )
            suffix = ")"
        else:
            prefix = (
                f"INSERT INTO {self.working_proj_id}.{self.dataset_name}"
                f".{self.table_name}"
            )
            suffix = ""

        query = f"""
        {prefix}
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            1 as feature_id,
            CASE WHEN demo.CANONICAL_RACE is NULL then 'race_missing'
            ELSE CONCAT('race_', demo.CANONICAL_RACE) END feature,
            1 value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        {suffix}
        """
        print("Featurizing race")
        query_job = self.client.query(query)
        query_job.result()
        self.create_table = False

    def _get_diagnoses_features(self):
        """
        Gets diagnosis code features for patients in cohort table and appends to
        long form bigquery table. Only selects diagnosis codes on the patient's
        problem list -- ie source = 2. 
        """
        if self.create_table:
            prefix = (
                f"CREATE OR REPLACE TABLE {self.working_proj_id}."
                f"{self.dataset_name}.{self.table_name} AS("
            )
            suffix = ")"
        else:
            prefix = (
                f"INSERT INTO {self.working_proj_id}.{self.dataset_name}"
                f".{self.table_name}"
            )
            suffix = ""

        query = f"""
        {prefix}
        SELECT
            labels.observation_id,
            labels.index_time,
            'Diagnoses' as feature_type,
            CAST(dx.start_date_utc as TIMESTAMP) as feature_time,
            UNIX_DATE(CAST(dx.start_date_utc as DATE)) as feature_id,
            dx.icd10 as feature,
            1 value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.diagnosis dx
        ON
            labels.anon_id = dx.anon_id
        WHERE 
            CAST(dx.start_date_utc as TIMESTAMP) < labels.index_time
        AND
            source = 2
        {suffix}
        """
        print("Featurizing diagnosis codes")
        query_job = self.client.query(query)
        query_job.result()
        self.create_table = False

    def _get_medication_features(self):
        """
        Gets medication order features for patients in cohort table and appends
        to long form bigquery table
        """
        max_look_back_time = 0
        for lb in DEFAULT_DEPLOY_CONFIG['Categorical']['Medications']:
            max_look_back_time = max(
                lb['look_back'], max_look_back_time)

        if self.create_table:
            prefix = (
                f"CREATE OR REPLACE TABLE {self.working_proj_id}."
                f"{self.dataset_name}.{self.table_name} AS("
            )
            suffix = ")"
        else:
            prefix = (
                f"INSERT INTO {self.working_proj_id}.{self.dataset_name}"
                f".{self.table_name}"
            )
            suffix = ""

        query = f"""
        {prefix}
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Medications' as feature_type,
            meds.order_inst_utc as feature_time,
            meds.order_med_id_coded as feature_id,
            meds.med_description as feature,
            1 as value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.order_med meds
        ON
            labels.anon_id = meds.anon_id
        WHERE 
            CAST(meds.order_inst_utc as TIMESTAMP) < labels.index_time
        AND
            TIMESTAMP_ADD(meds.order_inst_utc,
                          INTERVAL 24*{max_look_back_time} HOUR)
                          >= labels.index_time
        {suffix}
        """
        print("Featurizing medication orders")
        query_job = self.client.query(query)
        query_job.result()
        self.create_table = False

    def _get_age_features(self):
        """
        Get's age features for patients in cohort table, bins them and puts
        them in feature timeline table. 
        """
        query = f"""
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            1 as feature_id,
            'Age' as feature,
            DATE_DIFF(
                CAST(labels.index_time AS date), demo.BIRTH_DATE_JITTERED, YEAR)
            as value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
            labels
        INNER JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        """
        print("Featurizing age")
        df = pd.read_gbq(query)
        df_train = df[df['index_time'].dt.year.isin(self.train_years)]
        num_bins = self.feature_config['Numerical']['Age'][0]['num_bins']
        df_binned = self.get_binned_features(df_train, df, num_bins)

        # Write feature timeline in long form to bigquery dataset.table_name
        df_binned.to_gbq(
            destination_table=f"{self.dataset_name}.{self.table_name}",
            project_id=self.working_proj_id,
            if_exists='append',
            table_schema=self.feature_timeline_schema
        )
        self.create_table = False

    def _get_lab_results_features(self):
        """
        Collects lab result features for patients in cohort for select lab
        components. 
        """
        # Format list of lab component ids to grab
        base_name_string = "("
        for i, base_name in enumerate(DEFAULT_LAB_COMPONENT_IDS):
            if i == len(DEFAULT_LAB_COMPONENT_IDS) - 1:
                base_name_string += f"'{base_name}')"
            else:
                base_name_string += f"'{base_name}', "

        # Get max look back time
        max_look_back_time = 0
        for look_back in DEFAULT_DEPLOY_CONFIG['Numerical']['LabResults']:
            max_look_back_time = max(
                look_back['look_back'], max_look_back_time)

        query = f"""
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Lab Results' as feature_type,
            lr.result_time_utc as feature_time,
            CAST(lr.order_id_coded AS INTEGER) as feature_id,
            lr.base_name as feature,
            lr.ord_num_value as value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
             labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.lab_result lr
        ON
            labels.anon_id = lr.anon_id
        WHERE
            lr.result_time_utc < labels.index_time
        AND
            TIMESTAMP_ADD(lr.result_time_utc,
                          INTERVAL 24*{max_look_back_time} HOUR)
                          >= labels.index_time
        AND
            lr.base_name in {base_name_string}
        AND
            lr.ord_num_value IS NOT NULL
        """
        print("Featurizing lab results")
        df = pd.read_gbq(query, progress_bar_type='tqdm')
        df = df.astype({'value': float})
        df_train = df[df['index_time'].dt.year.isin(self.train_years)]
        num_bins = self.feature_config['Numerical']['LabResults'][0]['num_bins']
        df_binned = self.get_binned_features(df_train, df, num_bins)

        # Write feature matrix in long form to bigquery dataset.table_name
        df_binned.to_gbq(
            destination_table=f"{self.dataset_name}.{self.table_name}",
            project_id=self.working_proj_id,
            if_exists='append',
            table_schema=self.feature_timeline_schema
        )
        self.create_table = False

    def _get_vital_sign_features(self):
        """
        Collects flowsheet features for patients in cohort.
        """
        # Format list of lab component ids to grab
        base_name_string = "("
        for i, base_name in enumerate(DEFAULT_FLOWSHEET_FEATURES):
            if i == len(DEFAULT_FLOWSHEET_FEATURES) - 1:
                base_name_string += f"'{base_name}')"
            else:
                base_name_string += f"'{base_name}', "

        # Get max look back time
        max_look_back_time = 0
        for look_back in DEFAULT_DEPLOY_CONFIG['Numerical']['Vitals']:
            max_look_back_time = max(
                look_back['look_back'], max_look_back_time)

        query = f"""
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Vitals' as feature_type,
            f.recorded_time_utc as feature_time,
            UNIX_SECONDS(f.recorded_time_utc) as feature_id,
            f.row_disp_name as feature,
            f.numerical_val_1 as value
        FROM
            {self.working_proj_id}.{self.dataset_name}.{self.cohort_table}
             labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.flowsheet f
        ON
            labels.anon_id = f.anon_id
        WHERE
            f.recorded_time_utc < labels.index_time
        AND
            TIMESTAMP_ADD(f.recorded_time_utc,
                          INTERVAL 24*{max_look_back_time} HOUR)
                          >= labels.index_time
        AND
            f.row_disp_name in {base_name_string}
        AND
            f.numerical_val_1 IS NOT NULL
        """
        print("Featurizing Vitals")
        df = pd.read_gbq(query, progress_bar_type='tqdm')
        df = df.astype({'value': float})
        df_train = df[df['index_time'].dt.year.isin(self.train_years)]
        num_bins = self.feature_config['Numerical']['Vitals'][0]['num_bins']
        df_binned = self.get_binned_features(df_train, df, num_bins)

        # Write feature matrix in long form to bigquery dataset.table_name
        df_binned.to_gbq(
            destination_table=f"{self.dataset_name}.{self.table_name}",
            project_id=self.working_proj_id,
            if_exists='append',
            table_schema=self.feature_timeline_schema
        )
        self.create_table = False
