#!/usr/bin/python
"""
Module for adding the change/no-change labels
for building the processed feature matrix
"""

# TODO: (raikens)
# - [ ] add error handling for negative or zero values
# - [ ] flesh out testing suite
# - [ ] add more methods


import numpy as np
import pandas as pd
from scipy.stats import norm
from medinfo.dataconversion.Util import log
from medinfo.dataconversion.FeatureMatrixTransform import FeatureMatrixTransform

class FeatureMatrixChangeLabels(FeatureMatrixTransform):

    def add_change_labels(self, method, param, feature_old, feature_new):
        # get new column value
        if method == "percent":
            change_col = self.percent_change(param, feature_old, feature_new)
        elif method == "interval":
            change_col = self.interval_change(param, feature_old, feature_new)
        else:
            raise ValueError("Must specify a supported method for change calculation")

        # add new column to matrix
        col_index = self._matrix.columns.get_loc(feature_new)
        self._matrix.insert(col_index + 1, "change_yn", change_col)

    def percent_change(self, param, feature_old, feature_new):
        f = lambda old, new: int(abs(1.0-float(old)/new) >= param)
        return self._matrix[[feature_old, feature_new]].apply(lambda x: f(*x), axis = 1)

    def interval_change(self, param, feature_old, feature_new):
        f = lambda old, new: int(abs(float(old)-new) >= param)
        return self._matrix[[feature_old, feature_new]].apply(lambda x: f(*x), axis = 1)
