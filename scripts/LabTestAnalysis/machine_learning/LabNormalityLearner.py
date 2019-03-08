

import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 500)

from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

import LabNormalityLearner_Utils as Utils

class FeatureRemover(TransformerMixin):
    '''
    What: Remove specific features from a raw matrix
    '''
    def __init__(self, features_to_remove=[]):
        self.features_to_remove = features_to_remove
        pass

    def transform(self, X):
        return X.drop(self.features_to_remove, axis=1)

class FeatureImputer(TransformerMixin):
    def __init__(self, imputation_dict=None):
        self.imputation_dict = imputation_dict

    def fit(self, X, y=None):
        '''
        Learn the imputation dictionary

        Args:
            X:
            y:

        Returns:

        '''
        # self.imputation_dict = Utils.extract_imputation_dict(X)
        return self

    def transform(self, X):
        '''

        1. Dictionary-based imputation. Use self.imputation_dict.
        2. Prior-result-based imputation.

        Args:
            X:

        Returns:

        '''
        X_imputed = Utils.impute_by_carry_forward(X, self.imputation_dict)
        # X_imputed = X.fillna(0)


        return X_imputed


class Select_Features(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

def run_all():

    X_train_raw, y_train = [[1], [2]], [1, 2]
    X_test_raw, y_test = [[3], [4]], [3, 4]

    feature_engineering = Pipeline(
        [
            ('remove_features', FeatureRemover()),
            ('impute_features', FeatureImputer()),
            ('select_features', Select_Features())
        ]
    )

    machine_learning = Pipeline(
        [
            ('svc', LinearSVC())
        ]
    )

    pipeline = Pipeline(
        [
            ('feature_engineering', feature_engineering),
            ('machine_learning', machine_learning)
        ]
    )
    pipeline.set_params()
    pipeline.fit(X_train_raw, y_train)

    y_pred = pipeline.predict(X_test_raw)
    print y_pred

    print pipeline.score(X_test_raw, y_test)

def test(test_suite=[]):
    import LabNormalityLearner_Config as Config
    from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

    fm_io = FeatureMatrixIO()
    raw_matrix = fm_io.read_file_to_data_frame('LabNormalityLearner_TestData/LABA1C-normality-matrix-raw.tab')

    if 'remove' in test_suite:
        remover = FeatureRemover(Config.features_to_remove)
        processed_matrix_removed = remover.transform(raw_matrix)
        assert raw_matrix.shape[0] < processed_matrix_removed.shape[0]
        assert raw_matrix.shape[1] == processed_matrix_removed.shape[1]

    if 'impute' in test_suite:
        features_to_impute = ['TBIL.-14_0.max','TBIL.-14_0.median','TBIL.-14_0.mean','TBIL.-14_0.std']
            #('min', 'max', 'median', 'mean', 'std', 'first', 'last', 'diff', 'slope', 'proximate')
        imputation_dict = {}
        for feature in features_to_impute:
            imputation_dict[feature] = 0

        imputer = FeatureImputer(imputation_dict=imputation_dict)
        columns_to_look = ['pat_id', 'TBIL.-14_0.max','TBIL.-14_0.median','TBIL.-14_0.mean','TBIL.-14_0.std']
        print 'raw_matrix[columns_to_look].head():', raw_matrix[columns_to_look].head()

        processed_matrix_imputed = imputer.fit_transform(raw_matrix)
        print 'processed_matrix_imputed[columns_to_look].head():', processed_matrix_imputed[columns_to_look].head()

        assert processed_matrix_imputed[columns_to_look].isna().any().any() == False
        assert (raw_matrix['order_proc_id'].values == processed_matrix_imputed['order_proc_id'].values).all()


if __name__ == '__main__':
    test(test_suite=['impute'])
    pass