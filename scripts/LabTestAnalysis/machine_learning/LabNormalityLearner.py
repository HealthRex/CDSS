

import LocalEnv
import os
from medinfo.ml import SupervisedLearner as SL
from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)

from medinfo.ml.FeatureSelector import FeatureSelector

import ml_utils


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

        ml_classifiers.append(ml_classifier)


    processed_matrix_eval = SL.load_processed_matrix(lab, features_dict, src_folder, tag='test') # TODO:tag
    X_eval, y_eval = SL.split_Xy(processed_matrix_eval, outcome_label=outcome_label)

    '''
    
    '''
    for ml_classifier in ml_classifiers:
        y_pick_pred = ml_classifier.predict_probability(X_pick)[:,1]
        y_holdout_pred = ml_classifier.predict_probability(X_holdout)[:,1] #predict "Normal"

        results_pick = pd.DataFrame({'y_true':y_pick.values.flatten(), 'y_pred':y_pick_pred})
        results_filename = "results-pick.csv"
        results_path = os.path.join(src_folder, lab, ml_classifier.algorithm(), results_filename)
        results_pick.to_csv(results_path, index=False)



        # TODO: remove later
        y_pick_pred = ml_classifier.predict_probability(X_pick)[:,1]
        y_eval_pred = ml_classifier.predict_probability(X_eval)[:,1]

        threshold = SL.pick_threshold(y_holdout.values.flatten(), y_holdout_pred, target_PPV=0.95)
        confusion_metrics = SL.get_confusion_metrics(y_eval.values, y_eval_pred, threshold=threshold)
        print confusion_metrics


# TODO: Write test to make sure:
# 1.worked on all previous use cases
# 2.while writing tests you might find one of the few uses causes a bug
# 3.writing tests to be faster but more involved than the coding itself. The tests should test the intention.
# 4.The ones that do important business logic, thats where the testing is important. Test the requirements.
# 5.Keep your tests small: one test per requirement.

def main_pipelining(labs,
                    data_source = 'Stanford',
                    lab_type = 'panel',
                    num_episodes = 10000,
                    random_state=123456789):
    '''
    Fresh new pipeline.
    :return:
    '''

    from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS


    '''
    Folder organization
    '''
    project_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
    project_ml_folderpath = os.path.join(project_folderpath, 'machine_learning')

    data_set_foldername = 'data-%s-%s-%s-episodes'%(data_source, lab_type, num_episodes) # TODO: template shared by stats module
    data_set_folderpath = os.path.join(project_ml_folderpath, data_set_foldername)

    # data_subfolder= 'data_new_learner_testing'
    # data_folder = os.path.join(main_folder, data_subfolder)

     # Load

    algs = SL.get_algs()


    for lab in labs:

        data_lab_folderpath = os.path.join(data_set_folderpath, lab)  # TODO: if not exists, mkdir

        #
        '''
        Things to test:
        No overlapping pat_id. 
        Split not too imbalanced. 
        
        '''

        # raw_matrix_filename = (matrix_filename_template.replace('-matrix', '-matrix-raw')) % lab
        # raw_matrix_filepath = os.path.join(data_lab_folderpath, raw_matrix_filename)
        #
        raw_matrix_train, raw_matrix_evalu = SL.get_train_and_evalu_raw_matrices(
            lab = lab,
            data_lab_folderpath=data_lab_folderpath,
            random_state=random_state,
        )

        '''
        Baseline results on train and eval set
        Requires raw matrix info
        
        Baseline calculation is not a necessary part of a supervised learning pipeline.
        So if want to add this result, have to figure out the file system organization yourself!
        
        '''

        baseline_filepath = os.path.join(data_lab_folderpath, 'baseline_comparisons.csv')
        if not os.path.exists(baseline_filepath):
            baseline_evalu = ml_utils.get_baseline(df_train=raw_matrix_train,
                                                   df_test=raw_matrix_evalu,
                                                   y_label='all_components_normal')
            baseline_evalu.to_csv(baseline_filepath)

        '''
        Standard pipeline
        '''
        # print raw_matrix_train.head()
        features = {}
        features['remove'] = ['order_time', 'order_proc_id', # TODO: consistency w/ prev system
                'Birth.pre',
                'Male.preTimeDays', 'Female.preTimeDays',
                'RaceWhiteHispanicLatino.preTimeDays',
                'RaceWhiteNonHispanicLatino.preTimeDays',
                'RaceHispanicLatino.preTimeDays',
                'RaceAsian.preTimeDays',
                'RaceBlack.preTimeDays',
                'RacePacificIslander.preTimeDays',
                'RaceNativeAmerican.preTimeDays',
                'RaceOther.preTimeDays',
                'RaceUnknown.preTimeDays',
                'Death.post',
                'Death.postTimeDays'] # TODO: order_proc_id as info?!


        if lab_type == 'panel':
            features['remove'] += ['proc_code', 'num_components', 'num_normal_components', 'abnormal_panel']
            features['ylabel'] = 'all_components_normal'
        else:
            features['remove'] += ['base_name']
            features['ylabel'] = 'component_normal'
        features['keep'] = []

        features['info'] = ['pat_id']
        # features['id'] =

        features['select_params'] = {'selection_problem': FeatureSelector.CLASSIFICATION,
                                     'selection_algorithm': FeatureSelector.RECURSIVE_ELIMINATION,
                                     'percent_features_to_select': 0.05}

        learner_params = {'features':features}
        SL.standard_pipeline(lab=lab,
                             algs=algs,
                             learner_params=learner_params,
                             data_lab_folderpath=data_lab_folderpath,
                             random_state=random_state
                            )


        # TODO: check baseline and ml alg come from the same dataset!




if __name__ == '__main__':
    main_pipelining(labs=['LABA1C'], data_source = 'testingSupervisedLearner')