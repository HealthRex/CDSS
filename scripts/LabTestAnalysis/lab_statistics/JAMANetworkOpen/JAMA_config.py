
import os
import LocalEnv

curr_version = '10000-episodes-lastnormal'
inverse01 = True # Setting 'True' to interpret 'Normal' as 'Negative'

inverse_maker = '_inversed01' if inverse01 else ''

project_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis')
stats_folderpath = os.path.join(project_folderpath, 'lab_statistics')
ML_folderpath = os.path.join(project_folderpath, 'machine_learning')