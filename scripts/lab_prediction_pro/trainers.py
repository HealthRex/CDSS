"""
Definition of ModelTrainer, SequenceTrainer
"""
import os
import json
import pandas as pd
import pickle
import lightgbm as lgb
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from scipy.sparse import load_npz
import torch
from torch.optim import Adam    
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from constants import DEFAULT_LAB_COMPONENT_IDS
from constants import DEFAULT_FLOWSHEET_FEATURES

import pdb

class SequenceTrainer():
    """
    Used to train models that leverage SequenceFeaturizer.  Example model
    classes include GRUs, LSTMs, Transformers. 
    """

    def __init__(self, outpath, model, criterion, optimizer,
        train_dataloader, val_dataloader, test_dataloader, stopping_metric,
        num_epochs=100, scheduler=None):
        self.outpath = outpath
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.test_dataloader = test_dataloader
        self.stopping_metric = stopping_metric
        self.num_epochs = num_epochs
        self.scheduler = scheduler
        self.writer = SummaryWriter(self.outpath)

    def __call__(self):
        best_stopping_metric = 0
        tolerance_counter = 0
        for epoch in range(self.num_epochs):
            train_metrics = self.train()
            val_metrics = self.evaluate()
            self.writer.add_scalar('Loss/train', train_metrics['loss'], epoch)
            self.writer.add_scalar('Loss/val', val_metrics['loss'], epoch)
            self.writer.add_scalar('AUC/train', train_metrics['auc'], epoch)
            self.writer.add_scalar('AUC/val', val_metrics['auc'], epoch)

            if tolerance_counter == self.stopping_tolerance:
                break

            if epoch == 0:
                best_stopping_metric = val_metrics[self.stopping_metric]
                torch.save(self.model.state_dict(), 
                    os.path.join(self.working_directory, f'model_{epoch}.pt'))
            elif val_metrics[self.stopping_metric] > best_stopping_metric:
                best_stopping_metric = val_metrics[self.stopping_metric]
                tolerance_counter = 0
                torch.save(self.model.state_dict(),
                    os.path.join(self.working_directory, f'model_{epoch}.pt'))
            else:
                tolerance_counter += 1

    def train(self):
        self.model.train()
        train_loss = 0
        predictions, labels = [], []
        for batch in tqdm(self.train_dataloader):
            self.model.zero_grad()
            sequence = batch['sequence'].to(self.device)
            time_deltas = batch['time_deltas'].to(self.device)
            output = self.model(sequence, time_deltas)
            loss = self.criterion(output, batch['label'].to(self.device))
            train_loss += loss.item()
            loss.backward()
            self.optimizer.step()
            predictions.append(output.cpu().detach().numpy())
            labels.append(batch['y'].cpu().detach().numpy())

        train_loss /= len(self.train_dataloader)
        predictions = np.asarray(predictions)
        labels = np.asarray(labels)
        auc = roc_auc_score(labels, predictions)

        train_metrics = {
            'loss' : train_loss,
            'auc' : auc
        }
        return train_metrics

    def evaluate(self, test=False):
        self.model.eval()
        total_loss = 0
        if test:
            dataloader = self.test_dataloader
        else:
            dataloader = self.val_dataloader
        predictions, labels = [], []
        for batch in tqdm(dataloader):
            pdb.set_trace()
            sequence = batch['sequence'].to(self.device)
            time_deltas = batch['time_deltas'].to(self.device)
            output = self.model(sequence, time_deltas)
            loss = self.criterion(output, batch['label'].to(self.device))
            total_loss += loss.item()
            predictions.append(output.cpu().detach().numpy())
            labels.append(batch['y'].cpu().detach().numpy())
        total_loss /= len(dataloader)
        predictions = np.asarray(predictions)
        labels = np.asarray(labels)
        auc = roc_auc_score(labels, predictions)
        metrics = {
            'loss' : total_loss,
            'auc' : auc
        }
        return metrics

class BoostingTrainer():
    """
    Trains a gradient boosted tree (LightGBM) and performs appropriate model
    selection.  Currently supporting binary classification
    """
    def __init__(self, working_dir):
        self.working_dir = working_dir

    def __call__(self, task):
        """
        Trains a model against label defined by task
        Args:
            task: column that has label of interest
        """
        self.task = task
        self.clf = lgb.LGBMClassifier(
            objective='binary',
            n_estimators=1000,
            learning_rate=0.1,
            num_leaves=64
        )

        # Read in train data
        X_train = load_npz(os.path.join(
            self.working_dir, 'train_features.npz'))
        y_train = pd.read_csv(
            os.path.join(self.working_dir, 'train_labels.csv'))

        # Create val data
        val_size = int(len(y_train) * 0.1) # 10 % of training set
        val_inds = y_train.sort_values('index_time', ascending=False).head(
            val_size).index.values
        X_val = X_train[val_inds]
        y_val = y_train.iloc[val_inds]

        # Remove val inds from training set
        train_inds = [idx for idx in y_train.index.values 
                      if idx not in val_inds]
        X_train = X_train[train_inds]
        y_train = y_train.iloc[train_inds]

        # Assert val observation ids not in training set
        y_val_obs = set([a for a in y_val.observation_id.values])
        y_train_obs = set([a for a in y_train.observation_id.values])
        assert len(y_val_obs.intersection(y_train_obs)) == 0

        # Read in test data
        X_test = load_npz(os.path.join(self.working_dir, 'test_features.npz'))
        y_test = pd.read_csv(
            os.path.join(self.working_dir, 'test_labels.csv'))

        # Fit model with early stopping
        self.clf.fit(X_train,
                     y_train[self.task].values,
                     eval_set= [(X_val, y_val[self.task].values)],
                     eval_metric=['binary', 'auc'],
                     early_stopping_rounds = 25,
                     verbose=1)
        
        # Predictions
        predictions = self.clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test[self.task], predictions)
        print(f"{self.task} AUC: {round(auc, 2)}")

        df_yhats = pd.DataFrame(data={
            'labels': y_test[self.task].values,
            'predictions': predictions
        })
        yhats_path = f"{self.task}_yhats.csv"
        df_yhats.to_csv(os.path.join(self.working_dir, yhats_path), index=None)

        # Generate config file for DEPLOYR
        self.generate_deploy_config()

    def generate_deploy_config(self):
        """
        Generates the config file used by the deployment module.  Contains
        all information needed for deployment module to create feature vectors
        compatible with the model using EPIC and FHIR APIs. This includes
            1. model: the model itself
            2. feature_order: order of features in feature vector
            3. bin_map: numerical features and min value for each bin
            4. feature_config: dictionary containing which features types used
               in model and their corresponding look back windows. 
            5. tfidf_transform: if tfidf used to transform feature matrix

        """
        deploy = {}
        deploy['model'] = self.clf
        feature_order = pd.read_csv(os.path.join(self.working_dir,
                                                 'feature_order.csv'))
        deploy['feature_order'] = [f for f in feature_order.features]
        if os.path.exists(os.path.join(self.working_dir, 'bin_lup.csv')):
            bin_map = pd.read_csv(os.path.join(self.working_dir, 'bin_lup.csv'),
                                  na_filter=False)
        else:
            bin_map = None
        deploy['bin_map'] = bin_map

        # TFIDF transform 
        transform_path = os.path.join(self.working_dir, 'tfidf_transform.pkl')
        if os.path.exists(transform_path):
            with open(transform_path, 'rb') as f:
                transform = pickle.load(f)
        else:
            transform = None
        deploy['transform'] = transform

        with open(os.path.join(self.working_dir, 'feature_config.json'),
                  'r') as f:
            feature_config = json.load(f)
        deploy['feature_config'] = feature_config
        deploy['lab_base_names'] = DEFAULT_LAB_COMPONENT_IDS
        deploy['vital_base_names'] = DEFAULT_FLOWSHEET_FEATURES

        # Dump pickle for DEPLOYR
        with open(os.path.join(self.working_dir, f'{self.task}_deploy.pkl'),
                  'wb') as w:
            pickle.dump(deploy, w)

class BaselineModelTrainer():
    """
    Implements the most basic ML pipeline imagineable. Trains a random forest
    with default hyperparameters using features and labels saved in working
    directory from a Featurizer in featurizers.py

    Generates a deployment config file used in deploy.py that tells us which
    EPIC/FHIR APIs to call, how to construct and order features, and saves
    the model itself. 
    """

    def __init__(self, working_dir):
        self.working_dir = working_dir
        self.task = None # useful in multilable scenario

    def __call__(self, task):
        """
        Trains a model, saves predictions, saves a config file.
        Args:
            task : column for the binary label
        """
        self.task = task
        self.clf = RandomForestClassifier()
        X_train = load_npz(os.path.join(
            self.working_dir, 'train_features.npz'))
        X_test = load_npz(os.path.join(self.working_dir, 'test_features.npz'))
        y_train = pd.read_csv(
            os.path.join(self.working_dir, 'train_labels.csv'))
        y_test = pd.read_csv(
            os.path.join(self.working_dir, 'test_labels.csv'))

        self.clf.fit(X_train, y_train[self.task])
        predictions = self.clf.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test[self.task], predictions)
        print(f"AUC: {round(auc, 2)}")

        df_yhats = pd.DataFrame(data={
            'labels': y_test[self.task].values,
            'predictions': predictions
        })
        yhats_path = f"{self.task}_yhats"
        df_yhats.to_csv(os.path.join(self.working_dir, yhats_path), index=None)
        self.generate_deploy_config()

    def generate_deploy_config(self, tfidf=True):
        """
        Generates the config file used by the deployment module.  Contains
        all information needed for deployment module to create feature vectors
        compatible with the model using EPIC and FHIR APIs. This includes
            1. model: the model itself
            2. feature_order: order of features in feature vector
            3. bin_map: numerical features and min value for each bin
            4. feature_config: dictionary containing which features types used
               in model and their corresponding look back windows. 
        """
        deploy = {}
        deploy['model'] = self.clf
        feature_order = pd.read_csv(os.path.join(self.working_dir,
                                                 'feature_order.csv'))
        deploy['feature_order'] = [f for f in feature_order.features]
        if os.path.exists(os.path.join(self.working_dir, 'bin_lup.csv')):
            bin_map = pd.read_csv(os.path.join(self.working_dir, 'bin_lup.csv'),
                                na_filter=False)
        else:
            bin_map = None
        deploy['bin_map'] = bin_map
        with open(os.path.join(self.working_dir, 'feature_config.json'),
                  'r') as f:
            feature_config = json.load(f)
        deploy['feature_config'] = feature_config
        deploy['lab_base_names'] = DEFAULT_LAB_COMPONENT_IDS
        deploy['vital_base_names'] = DEFAULT_FLOWSHEET_FEATURES
        with open(os.path.join(self.working_dir, f'{self.task}_deploy.pkl'),
                  'wb') as w:
            pickle.dump(deploy, w)
