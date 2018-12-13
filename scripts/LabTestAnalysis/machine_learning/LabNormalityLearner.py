

import LocalEnv
import os
from medinfo.ml import SupervisedLearner as SL
from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)
import inspect


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


def main_pipelining_5000holdout(random_state=123456789):
    '''
    Goal:
    The purpose of this pipeline is to generate results from 5000 holdout episodes

    Procedure:
    Load processed_matrix_test, process_template, ml_models from existing results (Doing)
    Process and predict AWS holdout 5000 matrix for picking thresholds (TODO)
    Use picked thresholds to  (TODO)


    :return:
    '''

    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                               'scripts/LabTestAnalysis/machine_learning/')
    lab = 'LABA1C'


    src_folder = "data-panels-10000-episodes/"

    process_template = SL.load_process_template(lab, non_impute_features, src_folder)


    algs = ['random-forest'] #SL.get_algs()

    dst_folder = "data-panels-5000-episodes-holdout/"

    raw_matrix_holdout = SL.load_raw_matrix(lab, dst_folder)
    processed_matrix_full_holdout = SL.process_matrix(lab, raw_matrix_holdout, features_dict,
                                                 dst_folder, process_template)
    processed_matrix_holdout = processed_matrix_full_holdout.drop(info_features+leak_features, axis=1)

    processed_matrix_full_cali, processed_matrix_full_pick = SL.split_rows(processed_matrix_full_holdout,
                                                                         fraction=0.5,
                                                                         columnToSplitOn='pat_id')
    processed_matrix_cali = processed_matrix_full_cali.drop(info_features+leak_features, axis=1)
    processed_matrix_pick = processed_matrix_full_pick.drop(info_features+leak_features, axis=1)


    X_holdout, y_holdout = SL.split_Xy(processed_matrix_holdout, outcome_label=outcome_label)
    X_cali, y_cali = SL.split_Xy(processed_matrix_cali, outcome_label=outcome_label)
    X_pick, y_pick = SL.split_Xy(processed_matrix_pick, outcome_label=outcome_label)

    ml_classifiers = [] # Supervised Classifiers
    for alg in algs:
        ml_classifier = SL.load_ml_model(lab, alg, src_folder)

        '''
        calibration
        '''
        # ml_model._model = SL.calibrate_ml_model(ml_model._model, X_cali, y_cali, cali_method='isotonic')

        ml_models.append(ml_model)


    processed_matrix_eval = SL.load_processed_matrix(lab, features_dict, src_folder, tag='test') # TODO:tag
    X_eval, y_eval = SL.split_Xy(processed_matrix_eval, outcome_label=outcome_label)

    '''
    
    '''
    for ml_model in ml_models:
        y_pick_pred = ml_model.predict_probability(X_pick)[:,1]
        y_holdout_pred = ml_model.predict_probability(X_holdout)[:,1] #predict "Normal"

        results_pick = pd.DataFrame({'y_true':y_pick.values.flatten(), 'y_pred':y_pick_pred})
        results_filename = "results-pick.csv"
        results_path = os.path.join(src_folder, lab, ml_model.algorithm(), results_filename)
        results_pick.to_csv(results_path, index=False)



        # TODO: remove later
        y_pick_pred = ml_model.predict_probability(X_pick)[:,1]
        y_eval_pred = ml_model.predict_probability(X_eval)[:,1]

        threshold = SL.pick_threshold(y_holdout.values.flatten(), y_holdout_pred, target_PPV=0.95)
        confusion_metrics = SL.get_confusion_metrics(y_eval.values, y_eval_pred, threshold=threshold)
        print confusion_metrics



def main_pipelining():
    '''
    Fresh new pipeline.
    :return:
    '''
    from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS

    random_state = 123456789

    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                              'scripts/LabTestAnalysis/machine_learning')
    data_subfolder= 'data_new_learner_testing'
    data_folder = os.path.join(main_folder, data_subfolder)

    data_filename_template = '%s-normality-matrix'

    for lab in NON_PANEL_TESTS_WITH_GT_500_ORDERS:
        '''
        Feature extraction
        '''
        raw_matrix_filename = data_filename_template%lab + '-raw' + '.tab'
        raw_matrix_path = os.path.join(data_folder, lab, raw_matrix_filename)

        raw_matrix = SL.SQL_to_raw_matrix(lab=lab,
                                          data_path=raw_matrix_path)

        raw_matrix_train, raw_matrix_eval = SL.split_rows(raw_matrix,
                                                          fraction=0.75,
                                                          columnToSplitOn='pat_id',
                                                          random_state=random_state)

        '''
        Feature selection
        Here process_template is a dictionary w/ {feature: (ind, imputed value)}
        '''
        # TODO: also write this to file;
        processed_matrix_filename = data_filename_template % lab + '-processed' + '.tab'
        processed_matrix_path = os.path.join(data_folder, lab, processed_matrix_filename)
        processed_matrix_full_train, process_template = SL.process_matrix(lab=lab,
                                                         raw_matrix=raw_matrix_train,
                                                         features_dict=features_dict,
                                                         data_path=processed_matrix_path,
                                                         impute_template=None)

        processed_matrix_train = processed_matrix_full_train.drop(info_features+leak_features,
                                                                  axis=1)
        X_train, y_train = SL.split_Xy(data_matrix=processed_matrix_train,
                                       outcome_label=outcome_label)

        '''
        Baseline results
        '''
        SL.predict_baseline(lab=lab,
                            X_train=X_train,
                            y_train=y_train,
                            data_folder = data_folder)

        '''
        Training
        '''
        ml_classifiers = []
        algs = SL.get_algs()
        for alg in algs:
            # TODO: in the future, even the CV step requires splitByPatId, so carry forward this column?
            ml_classifier = SL.train_ml_model(lab=lab,
                                              alg=alg,
                                              X_train=X_train,
                                              y_train=y_train
                                              )
            ml_classifiers.append(ml_classifier)


        '''
        Training set results
        '''
        for ml_classifier in ml_classifiers:
            SL.predict(lab,
                       ml_classifier=ml_classifier,
                       X=X_train,
                       y=y_train,
                       data_folder=data_folder)

        '''
        Evaluation set feature selection
        '''

        # TODO here: make sure process_matrix works right
        processed_matrix_full_eval, _ = SL.process_matrix(lab=lab,
                                             raw_matrix=raw_matrix_eval,
                                             features_dict=features_dict,
                                             data_folder=data_folder,
                                            process_template=process_template)
        processed_matrix_eval = processed_matrix_full_eval.drop(info_features+leak_features, axis=1)
        X_eval, y_eval = SL.split_Xy(data_matrix=processed_matrix_eval,
                                       outcome_label=outcome_label)

        '''
        Evaluation results
        '''
        for ml_classifier in ml_classifiers:
            SL.predict(lab=lab,
                       ml_classifier=ml_classifier,
                       X=X_eval,
                       y=y_eval)



if __name__ == '__main__':
    main_pipelining()