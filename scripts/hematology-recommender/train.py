# -*- coding: utf-8 -*-
import os
import os.path as osp
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.model_selection import GridSearchCV

from data.organize_feats import organize_feats
from utils.eval_utils import evaluate

np.random.seed(11111)

train_feats, val_feats, test_feats, train_targets, val_targets, test_targets = organize_feats()

# names = [
#     "Nearest Neighbors",
#     "Linear SVM",
#     "RBF SVM",
#     "Gaussian Process",
#     "Decision Tree",
#     "Random Forest",
#     "AdaBoost",
# ]

# classifiers = [
#     KNeighborsClassifier(3),
#     SVC(kernel="linear", C=0.025),
#     SVC(gamma=2, C=1),
#     GaussianProcessClassifier(1.0 * RBF(1.0)),
#     DecisionTreeClassifier(max_depth=5),
#     RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
#     AdaBoostClassifier()]

# names = ["Decision Tree"]
# classifiers = [DecisionTreeClassifier()]
# param_grid = { 'max_features': ['auto', 'sqrt'],
#                'max_depth': [int(x) for x in np.linspace(10, 110, num = 11)],
#                'min_samples_split': [2, 5, 10],
#                'min_samples_leaf': [1, 2, 4],
#                'bootstrap': [True, False]}


# # iterate over classifiers
# for name, model, param_grid in zip(names, classifiers, param_grids):

#     grid_model = GridSearchCV(model, param_grid, cv=4)             
#     grid_model.fit(train_feats, train_targets)
#     val_preds = clf.predict(val_feats)
    
model = DecisionTreeClassifier(max_depth= 10)
model.fit(train_feats, train_targets)
val_preds = model.predict_proba(val_feats)
