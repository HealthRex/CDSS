

import LocalEnv
import os
from medinfo.ml import SupervisedLearner as SL
from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)
import inspect

def main_pipelining1():
    '''
    Goal:
    Load process_template and ml_models from existing results (Doing)
    Process and predict AWS holdout 5000 matrix (TODO)
    Get (calibrated?) threshold from AWS holdout set (TODO)


    :return:
    '''

    lab = 'LABA1C'
    outcome_label = 'all_components_normal'
    random_state = 123456789

    info_features = ['pat_id', 'order_proc_id', 'proc_code', 'order_time']
    leak_features = ['abnormal_panel', 'num_components', 'num_normal_components']



    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                               'scripts/LabTestAnalysis/machine_learning/')
    print main_folder

    lab_folder = os.path.join(main_folder,
                              'data-panels/%s/' % lab)
    raw_matrix = SL.get_raw_matrix(lab, lab_folder=lab_folder)


    raw_features_all = raw_matrix.columns.values.tolist()
    non_impute_features = info_features + leak_features + [outcome_label]
    numeric_features = [x for x in raw_features_all if x not in non_impute_features]

    raw_matrix_train, raw_matrix_test = SL.train_test_split(raw_matrix,
                                                            columnToSplitOn='pat_id',
                                                            random_state=random_state)
    # print raw_matrix_train.shape, raw_matrix_test.shape
    # quit()

    # processed_matrix_train, impute_template = SL.process_matrix(raw_matrix_train,
    #                                                             lab=lab,
    #                                                             output_folder=lab_folder,
    #                                                             use_cached_data=True)
    #
    # algs = SL.get_algs()
    #
    # X_train, y_train = processed_matrix_train # TODO
    # ml_models = SL.train_ml_models(X_train, y_train, lab, algs)

    impute_template = SL.get_process_template(lab, numeric_features,
                                              data_folder='data-panels/')
    print impute_template
    quit()

    raw_matrix_pick = SL.get_raw_matrix(lab, lab_folder='data-panels-5000-holdout/%s'%lab,
                                        file_name='%s-normality-matrix-5000-episodes-raw-holdout.tab'%lab)

    processed_matrix_pick = SL.process_matrix(raw_matrix_train, impute_template=impute_template,
                                                                output_folder=lab_folder)
    # X_pick, y_pick = processed_matrix_train  # TODO
    # for model in ml_models:
    #     y_pred_pick = SL.predict(X_pick, model)
    # threshold = SL.pick_threshold(y_pick, y_pred_pick, target_PPV=0.95)
    quit()


    ml_models = SL.load_ml_models()


    processed_matrix_test, _ = SL.process_matrix(raw_matrix, process_template)
    y_pick = processed_matrix.pop(outcome_label)
    X_pick = processed_matrix


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