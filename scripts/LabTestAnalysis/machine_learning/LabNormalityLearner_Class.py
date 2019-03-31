
from sklearn.base import BaseEstimator, TransformerMixin
import LabNormalityLearner_Utils as Utils
from medinfo.ml.FeatureSelector import FeatureSelector


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
        X_imputed = X.fillna(0)

        # X_imputed = Utils.do_impute_sx(X, self.feat2mean_dict)
        return X_imputed


class Select_Features(TransformerMixin):
    def __init__(self, random_state=0):
        self.fs = FeatureSelector(problem=FeatureSelector.CLASSIFICATION,
                                  algorithm=FeatureSelector.RECURSIVE_ELIMINATION,
                                  random_state=random_state)
        self.feat2imputeValOrder_dict = {}

    def fit(self, X, y=None, features_to_keep=[], select_percent=0.05):
        '''
        TODO: Does this "select_percent" include those pre-set to keep?
        features_to_keep includes both features wanted to keep + non-numeric features

        Args:
            X:
            y:
            features_to_keep:
            select_percent:

        Returns:

        '''
        self.fs.set_input_matrix(X, y)

        num_features_to_select = select_percent * len(X.columns.values)
        self.fs.select(k=num_features_to_select)

        feature_ranks = self.fs.compute_ranks()
        for i in range(len(feature_ranks)):
            if feature_ranks[i] <= num_features_to_select:
                # If in features_to_keep, pretend it wasn't eliminated.
                features_to_keep.append(X.columns[i])



        return self

    def transform(self, X):
        return X