

import LocalEnv
import os
from medinfo.ml import SupervisedLearner as SL
from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)
import inspect

def main_pipelining1():
    lab = 'LABA1C'
    outcome_label = 'all_components_normal'
    random_state = 123456789
    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                               'scripts/LabTestAnalysis/machine_learning/')
    print main_folder

    lab_folder = os.path.join(main_folder,
                              'data-panels/%s/' % lab)
    raw_matrix = SL.get_raw_matrix(lab, lab_folder=lab_folder)

    raw_matrix_train, raw_matrix_test = SL.train_test_split(raw_matrix,
                                                            columnToSplitOn='pat_id',
                                                            random_state=random_state)
    # print raw_matrix_train.shape, raw_matrix_test.shape
    # quit()

    processed_matrix_train, impute_template = SL.process_matrix(raw_matrix_train, output_folder=lab_folder)

    quit()


    ml_models = SL.load_ml_models()

    raw_matrix_pick = SL.load_data(datapath="")
    processed_matrix_test, _ = SL.process_matrix(raw_matrix, process_template)
    y_pick = processed_matrix.pop(outcome_label)
    X_pick = processed_matrix
    thresholds = SL.pick_threshold(X_pick, y_pick, ml_models, target_PPV=0.95)

    # SL.evaluate_ml_models(X_test, y_test, ml_models, thresholds)

def main_pipelining():
    cur_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                              'scripts/LabTestAnalysis/machine_learning')

    source_set_folder = os.path.join(cur_folder,
                                     'data-panels-5000-holdout/')

    status = SL.pipelining(source_set_folder,
                                          labs=NON_PANEL_TESTS_WITH_GT_500_ORDERS,
                                          source_type='raw-matrix',
                                          source_ids=['holdout'])
    print status

if __name__ == '__main__':
    main_pipelining1()