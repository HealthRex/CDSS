
import warnings
warnings.filterwarnings("ignore")

import os
import LocalEnv

import matplotlib.pyplot as plt

from sklearn import metrics

import pandas as pd
import numpy as np
from scripts.LabTestAnalysis.lab_statistics import stats_utils
from scripts.LabTestAnalysis.machine_learning.ml_utils import map_lab




curr_version = '10000-episodes-lastnormal'
inverse01 = True # Setting 'True' to interpret 'Normal' as 'Negative'

inverse_maker = '_inversed01' if inverse01 else ''

project_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis')
stats_folderpath = os.path.join(project_folderpath, 'lab_statistics')
ML_folderpath = os.path.join(project_folderpath, 'machine_learning')