
from sklearn.base import TransformerMixin
import LabNormalityLearner_Utils as Utils



class FeatureRemover(TransformerMixin):
    '''
    What: Remove specific features from a raw matrix
    '''
    def __init__(self, features_to_remove=[]):
        self.features_to_remove = features_to_remove
        pass

    def fit(self):
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