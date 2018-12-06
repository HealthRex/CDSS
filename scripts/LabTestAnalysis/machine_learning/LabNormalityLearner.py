

import LocalEnv
import os
from medinfo.ml import SupervisedLearner
from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS

if __name__ == '__main__':
    cur_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                              'scripts/LabTestAnalysis/machine_learning')

    source_set_folder = os.path.join(cur_folder,
                                     'data-panels-5000-holdout/')

    status = SupervisedLearner.pipelining(source_set_folder,
                            labs=NON_PANEL_TESTS_WITH_GT_500_ORDERS,
                            source_type='raw-matrix',
                            source_ids=['holdout'])
    print status