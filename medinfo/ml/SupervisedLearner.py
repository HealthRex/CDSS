

from sklearn.pipeline import Pipeline
from sklearn.utils.validation import column_or_1d

import SupervisedLearner_Class as Clas
import SupervisedLearner_Utils as Utils
import SupervisedLearner_System as Syst

import logging

import pandas as pd

from medinfo.ml.SupervisedClassifier import SupervisedClassifier

class SupervisedLearner():
    def __init__(self, input_matrix, ylabel):
        ''''''

        '''Child Class should update this'''
        self.working_folderpath = ''
        self.input_matrix = input_matrix
        self.ylabel = ylabel
        pass

    def run(self):
        file_organizer = Syst.FileOrganizerLocal(working_folderpath=self.working_folderpath)

        raw_matrix_train, raw_matrix_test = Utils.split_rows(self.input_matrix)

        X_train_raw, y_train = Utils.split_Xy(raw_matrix_train, ylabel=self.ylabel)

        feature_processing_pipeline = Pipeline(
            memory=None,  # file_organizer.cached_pipeline_filepath,
            steps=[
                ('impute_features', Clas.FeatureImputer()),
                ('remove_features', Clas.FeatureRemover()),
                ('select_features', Clas.Select_Features())
            ]
        )
        X_train_processed = feature_processing_pipeline.fit_transform(X_train_raw, y_train)

        predictor = SupervisedClassifier(classes=[0, 1], hyperparams=None)

        status = predictor.train(X_train_processed, column_or_1d(y_train))

        X_test_raw, y_test = Utils.split_Xy(raw_matrix_test, ylabel=self.ylabel)
        X_test_processed = feature_processing_pipeline.transform(X_test_raw)
        y_test_pred_proba = predictor.predict_probability(X_test_processed)[:, 1]


        res_df = pd.DataFrame({'actual': y_test,
                               'predict': y_test_pred_proba})
        res_df.to_csv(file_organizer.get_output_filepath())
        return res_df


if __name__ == '__main__':
    pass

