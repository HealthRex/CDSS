

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
import LabNormalityLearner_System as LNL_sys

def run_one_lab_local(lab, lab_type, data_source, version):
    '''

    Input:

    :return:
    '''

    # X_train_raw, y_train = [[1], [2]], [1, 2]
    # X_test_raw, y_test = [[3], [4]], [3, 4]
    file_organizer = LNL_sys.FileOrganizerLocal(lab=lab,
                                                lab_type=lab_type,
                                                data_source=data_source,
                                                version=version)

    raw_matrix = file_organizer.get_raw_matrix()

    X_train_raw, y_train = Utils.Split_Xy(raw_matrix)

    pipeline = Pipeline(memory = file_organizer.cached_pipeline_filepath,
                        steps = [
                                    ('feature_engineering', Pipeline
                                        (
                                            [
                                                ('remove_features', Cls.FeatureRemover()),
                                                ('impute_features', Cls.FeatureImputer()),
                                                ('select_features', Cls.Select_Features())
                                            ]
                                        )
                                     ),
                                    ('machine_learning', Pipeline
                                        (
                                             [
                                                 ('svc', LinearSVC())
                                             ]
                                        )
                                     )
                                ]
    )

    pipeline.set_params()
    pipeline.fit(X_train_raw, y_train)

    Xy_test_raw = LNL_sys.get_raw_matrix(lab_type=lab_type,
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