

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

import LabNormalityLearner_Utils as Utils
import LabNormalityLearner_Class as Cls
import LabNormalityLearner_System as syst
import LabNormalityLearner_Config as Config

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

    raw_matrix_train, raw_matrix_test = Utils.split_rows(raw_matrix)
    X_train_raw, y_train = Utils.split_Xy(raw_matrix_train, ylabel=y_label)

    redundant_features = ['proc_code', 'num_components', 'num_normal_components', 'abnormal_panel']
    id_features = ['pat_id', 'order_proc_id', 'order_time']

    numeric_features = X_train_raw.columns[~X_train_raw.columns.isin([y_label]+redundant_features+id_features)]

    '''
    Check if the left features are all numeric
    '''
    assert X_train_raw[numeric_features].select_dtypes(exclude=['object']).shape == X_train_raw[numeric_features].shape
    quit()
    print X_train_raw[numeric_features].head()

    quit()

    '''
    (1) Feature Impute: 
    Imputation of some numerical values depend on prior stats of the same patient, 
        so certain auxiliary columns are still useful
    
    
    (2) Feature Remove:
    Remove auxiliary columns
    
    (3) Feature Selection:
    Only select from numerical columns
    
    '''
    feature_engineering_pipeline = Pipeline(
        memory = None,#file_organizer.cached_pipeline_filepath,
        steps = [
             ('impute_features', Cls.FeatureImputer()),
             ('remove_features', Cls.FeatureRemover(features_to_remove=Config.features_to_remove)),
             ('select_features', Cls.Select_Features(random_state=random_state))
             ]
    )

    # feature_engineering_pipeline.set_params()
    print X_train_raw.shape
    X_train_processed = feature_engineering_pipeline.fit_transform(X_train_raw, y_train)
    print X_train_processed.shape
    quit()

    Xy_test_raw = syst.get_raw_matrix(lab_type=lab_type,
                                         data_source=data_source_test,
                                         version=version
                                         )
    X_test_raw, y_test = Utils.Split_Xy(Xy_test_raw)

    y_pred = pipeline.predict(X_test_raw)

    print y_pred


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