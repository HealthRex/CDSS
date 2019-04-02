

'''

What:
Application main file.
Keep this file as simple as possible.

'''

import pandas as pd
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

import logging

from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.utils.validation import column_or_1d

import LabNormalityLearner_Utils as Utils
import LabNormalityLearner_Class as Cls
import LabNormalityLearner_System as syst
import LabNormalityLearner_Config as Config

from medinfo.ml.SupervisedClassifier import SupervisedClassifier

def run_one_lab_local(lab, lab_type, data_source, version, random_state=0):
    '''

    Input:

    :return:
    '''

    # X_train_raw, y_train = [[1], [2]], [1, 2]
    # X_test_raw, y_test = [[3], [4]], [3, 4]
    file_organizer = syst.FileOrganizerLocal(lab=lab,
                                             lab_type=lab_type,
                                             data_source=data_source,
                                             version=version)

    raw_matrix = file_organizer.get_raw_matrix()

    y_label = 'all_components_normal'

    '''
    TODO: later on pat_ids
    '''
    raw_matrix_train, raw_matrix_test = Utils.split_rows(raw_matrix)

    patIds_train = raw_matrix_train['pat_id'].values.tolist()

    X_train_raw, y_train = Utils.split_Xy(raw_matrix_train, ylabel=y_label)

    redundant_features = ['proc_code', 'num_components', 'num_normal_components', 'abnormal_panel']
    id_features = ['pat_id', 'order_proc_id', 'order_time']

    numeric_features = X_train_raw.columns[~X_train_raw.columns.isin([y_label]+redundant_features+id_features)]

    '''
    Check if the left features are all numeric
    '''
    assert X_train_raw[numeric_features].select_dtypes(exclude=['object']).shape == X_train_raw[numeric_features].shape

    features_by_type = {'redundant_features': redundant_features,
                    'id_features':id_features,
                    'numeric_features':numeric_features,
                    'y_label':y_label}

    '''
    (1) Feature Impute: 
    Imputation of some numerical values depend on prior stats of the same patient, 
        so certain auxiliary columns are still useful
    
    
    (2) Feature Remove:
    Remove auxiliary columns
    
    (3) Feature Selection:
    Only select from numerical columns
    
    '''
    feature_processing_pipeline = Pipeline(
        memory = None, #file_organizer.cached_pipeline_filepath,
        steps = [
             ('impute_features', Cls.FeatureImputer()),
             ('remove_features', Cls.FeatureRemover(features_to_remove=Config.features_to_remove)),
             ('select_features', Cls.Select_Features(random_state=random_state, features_by_type=features_by_type))
             ]
    )

    # feature_engineering_pipeline.set_params()
    print X_train_raw.shape
    X_train_processed = feature_processing_pipeline.fit_transform(X_train_raw, y_train)
    print X_train_processed.shape

    hyperparams = {}
    hyperparams['algorithm'] = 'random-forest'
    predictor = SupervisedClassifier(classes=[0,1], hyperparams=hyperparams)

    '''
    Automatically takes care of tuning hyperparameters via stochastic-search
    '''
    status = predictor.train(X_train_processed, column_or_1d(y_train),
                                       groups = patIds_train)
    quit()

    '''
    Test set
    '''
    X_test_raw, y_test = Utils.split_Xy(raw_matrix_test, ylabel=y_label)
    print X_test_raw.shape
    X_test_processed = feature_processing_pipeline.transform(X_test_raw)
    print X_test_processed.shape
    print X_test_processed.head()

def run_one_lab_remote(lab, lab_type, data_source, version, random_state=0):
    file_organizer = syst.FileOrganizerRemote(lab_type="panel",
                                              data_source_src="Stanford",
                                              data_source_dst="UMich",
                                              version="10000-episodes-lastnormal")
    raw_matrix_src = file_organizer.get_raw_matrix(data_tag="src")
    raw_matrix_train, _ = Utils.split_rows(raw_matrix_src)

    raw_matrix_dst = file_organizer.get_raw_matrix(data_tag="dst")
    _, raw_matrix_test = Utils.split_rows(raw_matrix_dst)

    pass

if __name__ == '__main__':
    lab = 'LABA1C'
    lab_type = 'standalone'
    data_source = 'Stanford'
    version = '10000-episodes-lastnormal'

    logging.getLogger().setLevel(logging.INFO)

    run_one_lab_local(lab=lab,
                      lab_type=lab_type,
                      data_source=data_source,
                      version=version)