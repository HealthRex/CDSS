
from sklearn.base import BaseEstimator, TransformerMixin
import LabNormalityLearner_Utils as Utils



class FeatureRemover(BaseEstimator, TransformerMixin):
    '''
    What: Remove specific features from a raw matrix
    '''
    def __init__(self, features_to_remove=[]):
        self.features_to_remove = features_to_remove
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(self.features_to_remove, axis=1)



class FeatureImputer(BaseEstimator, TransformerMixin):
    def __init__(self, imputation_dict=None):
        self.imputation_dict = imputation_dict

    def fit(self, X, y=None):
        '''
        Learn the imputation dictionary
        (1) Use population mean (prevalence) to impute:
            Need store the prevalence in the training set
        (2) Carrying forward the most recent non-missing value
            Using training/testing data's own feature
        (3) Using the previous + time difference if available; otherwise -infinite
            Using posi/nega infinities to impute times

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