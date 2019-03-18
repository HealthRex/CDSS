
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
    def __init__(self, feat2mean_dict={}):
        '''
        imputation_dict:
        key: feature_name
        val:
        '''
        self.feat2mean_dict = feat2mean_dict

    def fit(self, X, y=None):
        '''
        Regardless of whether to use the means later,
        extract them here.

        Args:
            X:
            y:

        Returns:

        '''
        feats = X.columns.values.tolist()
        for feat in feats:
            if X[feat].dtype == type(1.) or X[feat].dtype == type(1):
                self.feat2mean_dict[feat] = X[feat].mean()
            else:
                print 'Non numeric (cannot calc mean):', feat, X[feat].dtype
        return self

    def transform(self, X):
        '''
        Imputation strategies:
        (1) Use train population level to impute
        e.g. population mean

        (2) Use local patient level to impute
        e.g. most recent WBC stats carrying forward
        e.g. most recent order time carrying forward + time lapse

        (3) Use constants to impute
        e.g. -inf for non-existing order time

        For each feature, could use a mixture of multiple imputation strategies:
        e.g.
        <1>

        Args:
            X:
            y:

        Returns:

        '''
        # X_imputed = Utils.impute_by_carry_forward(X, self.feat2mean_dict)
        # X_imputed = X.fillna(0)

        X_imputed = Utils.do_impute_sx(X, self.feat2mean_dict)
        return X_imputed


class Select_Features(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X