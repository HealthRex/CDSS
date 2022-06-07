"""
Definition of ModelTrainer, SequenceTrainer
"""
import os
import json
from typing_extensions import dataclass_transform
import pandas as pd
import pickle
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

class SequenceTrainer():
    """
    Used to train models that leverage SequenceFeaturizer.  Example model
    classes include GRUs, LSTMs, Transformers. 
    """

    def __init__(self, working_directory, model, run_name, criterion, optimizer,
        train_dataloader, val_dataloader, test_dataloader, stopping_metric,
        num_epochs=100, scheduler=None):
        self.working_directory = working_directory
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.test_dataloader = test_dataloader
        self.stopping_metric = stopping_metric
        self.num_epochs = num_epochs
        self.scheduler = scheduler
        self.writer = SummaryWriter(
            os.path.join(self.working_directory, 'runs', run_name))

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
            output = self.model(batch['X'].to(self.device))
            loss = self.criterion(output, batch['y'].to(self.device))
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
            output = self.model(batch['X'].to(self.device))
            loss = self.criterion(output, batch['y'].to(self.device))
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

class BaselineModelTrainer(object):
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
