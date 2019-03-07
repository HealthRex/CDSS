

import pandas

from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

class FeatureRemover(TransformerMixin):
    '''
    What: Remove specific features from a raw matrix
    '''
    def __init__(self, features_to_remove=[]):
        self.features_to_remove = features_to_remove
        pass

    def fit(self):
        return self

    def transform(self, X):
        return X.drop(self.features_to_remove, axis=1)

class Impute_Features(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

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
            ('impute_features', Impute_Features()),
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


if __name__ == '__main__':
    run_all()
    pass