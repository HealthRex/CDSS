"""
Definition of ModelTrainer
"""
import os
import json
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from scipy.sparse import load_npz

from constants import DEFAULT_LAB_COMPONENT_IDS
from constants import DEFAULT_FLOWSHEET_FEATURES


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
        bin_map = pd.read_csv(os.path.join(self.working_dir, 'bin_lup.csv'),
                              na_filter=False)
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
