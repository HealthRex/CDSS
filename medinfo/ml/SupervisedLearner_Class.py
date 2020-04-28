from sklearn.base import BaseEstimator, TransformerMixin
from medinfo.ml.FeatureSelector import FeatureSelector
from sklearn.utils.validation import column_or_1d

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
    def __init__(self, feat2mean_dict={}):
        '''
        imputation_dict:
        key: feature_name
        val:
        '''
        self.feat2mean_dict = feat2mean_dict

    def fit(self, X, y=None):
        feats = X.columns.values.tolist()
        for feat in feats:
            if X[feat].dtype == type(1.) or X[feat].dtype == type(1):
                self.feat2mean_dict[feat] = X[feat].mean()
            else:
                print('Non numeric (cannot calc mean):', feat, X[feat].dtype)
        return self

    def transform(self, X):
        X_imputed = X.copy()
        for feat, imputed in self.feat2mean_dict.items():
            X_imputed[feat] = X.fillna(imputed)
        return X_imputed


class Select_Features(TransformerMixin):
    def __init__(self, random_state=0, features_by_type=None):
        pass

    def fit(self, X, y=None, features_to_keep=None, select_percent=0.05):
        return self

    def transform(self, X):
        return X