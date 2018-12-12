

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
    Load processed_matrix_test, process_template, ml_models from existing results (Doing)
    Process and predict AWS holdout 5000 matrix for picking thresholds (TODO)
    Use picked thresholds to  (TODO)


    :return:
    '''


    lab = 'LABA1C'
    outcome_label = 'all_components_normal'

    info_features = ['pat_id', 'order_proc_id', 'proc_code', 'order_time']
    leak_features = ['abnormal_panel', 'num_components', 'num_normal_components']

    non_impute_features = info_features + leak_features + [outcome_label]

    features_dict = {
        'non_impute_features':non_impute_features,
        'outcome_label':outcome_label,
        'info_features':info_features,
        'leak_features':leak_features
    }

    src_folder = "data-panels-10000-episodes/"

    process_template = SL.load_process_template(lab, non_impute_features, src_folder)

    algs = ['random-forest'] #SL.get_algs()

    ml_models = []
    for alg in algs:
        ml_model = SL.load_ml_model(lab, alg, src_folder)
        ml_models.append(ml_model)

    dst_folder = "data-panels-5000-episodes-holdout/"

    raw_matrix_pick = SL.load_raw_matrix(lab, dst_folder)
    processed_matrix_pick = SL.process_matrix(lab, raw_matrix_pick, features_dict,
                                              dst_folder, process_template)

    X_pick, y_pick = SL.split_Xy(processed_matrix_pick, outcome_label=outcome_label)


    processed_matrix_test = SL.load_processed_matrix(lab, features_dict, src_folder, tag='test')
    X_test, y_test = SL.split_Xy(processed_matrix_test, outcome_label=outcome_label)

    for ml_model in ml_models:
        y_pick_pred = ml_model.predict_probability(X_pick)[:,1]

        # print y_pick_pred
        threshold = SL.pick_threshold(y_pick.values, y_pick_pred, target_PPV=0.95)


        y_test_pred = ml_model.predict_probability(X_test)[:,1]

        confusion_metrics = SL.get_confusion_metrics(y_test.values, y_test_pred, threshold=threshold)
        print confusion_metrics
        quit()

        # SL.evaluate(lab, y_test_pred, y_test, threshold=threshold)




    #
    # # TODO: Assume different folder name, but same file names!
    #
    #
    # threshold = SL.pick_threshold(processed_matrix_pick, target_PPV=0.95)
    #
    #
    #








    random_state = 123456789




    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                               'scripts/LabTestAnalysis/machine_learning/')
    print main_folder

    lab_folder = os.path.join(main_folder,
                              'data-panels/%s/' % lab)





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