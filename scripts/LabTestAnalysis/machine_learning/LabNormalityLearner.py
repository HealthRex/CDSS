

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

def run_one_lab_local(lab, lab_type, data_source, version):
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

    raw_matrix_train, raw_matrix_test = Utils.split_rows(raw_matrix)
    X_train_raw, y_train = Utils.split_Xy(raw_matrix_train,
                                          ylabel='all_components_normal')

    '''
    (1) Feature Impute: 
    Imputation of some numerical values depend on prior stats of the same patient, 
        so certain auxiliary columns are still useful
    (2) Feature Remove:
    Remove auxiliary columns
    (3) Feature Selection:
    
    '''
    feature_engineering_pipeline = Pipeline(
        memory = file_organizer.cached_pipeline_filepath,
        steps = [
             ('impute_features', Cls.FeatureImputer()),
             ('remove_features', Cls.FeatureRemover(features_to_remove=Config.features_to_remove)),
             # ('select_features', Cls.Select_Features())
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