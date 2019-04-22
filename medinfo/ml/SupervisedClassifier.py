#!/usr/bin/python
"""
Generic module for supervised machine learning classification.
"""

import numpy as np
from pandas import DataFrame, Series
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import f1_score, roc_auc_score, make_scorer
from sklearn.svm import SVC
from sklearn.utils.validation import column_or_1d
from sklearn.model_selection import StratifiedKFold, cross_val_score, GroupKFold
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.exceptions import ConvergenceWarning
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
import warnings

from medinfo.common.Util import log

warnings.filterwarnings('ignore', category=ConvergenceWarning)

class SupervisedClassifier:
    # Define string constants for all supported ML algorithms so that
    # clients can define which algorithm to call.
    DECISION_TREE = 'decision-tree'
    LOGISTIC_REGRESSION = 'l1-logistic-regression-cross-validation'
    RANDOM_FOREST = 'random-forest'
    REGRESS_AND_ROUND = 'regress-and-round'
    ADABOOST = 'adaboost'
    SVM = 'svm'
    XGB = 'xgb'
    NN = 'nn'
    GAUSSIAN_NAIVE_BAYES = 'gaussian-naive-bayes'

    # TODO(sbala): Nearest Neighbors: http://scikit-learn.org/stable/modules/neighbors.html#neighbors
    # TODO(sbala): Neural Network: http://scikit-learn.org/stable/modules/neural_networks_supervised.html#neural-networks-supervised
    SUPPORTED_ALGORITHMS = [DECISION_TREE, LOGISTIC_REGRESSION, RANDOM_FOREST,
        REGRESS_AND_ROUND, ADABOOST, GAUSSIAN_NAIVE_BAYES,
        #SVM, XGB, NN
    ]

    # Hyperparam search strategies.
    EXHAUSTIVE_SEARCH = 'exhaustive-search'
    STOCHASTIC_SEARCH = 'stochastic-search'
    HYPERPARAM_STRATEGIES = [EXHAUSTIVE_SEARCH, STOCHASTIC_SEARCH]

    # Status codes.
    TRAINED = 'model-trained'
    INSUFFICIENT_SAMPLES = 'insufficient-samples-per-class'

    CV_STRATEGY = 'StratifiedKFold'#'GroupKFold' #'StratifiedKFold'

    def __init__(self, classes, hyperparams=None, groups=None):
        self._classes = classes

        # Initialize params.
        self._params = {}
        self._model = None

        '''
        Used by GroupKFold for splitting train/validation. 
        '''
        self._groups = groups

        # Initialize hyperparams.
        self._hyperparams = {} if hyperparams is None else hyperparams
        self._hyperparam_search_space = {}
        # Set algorithm.
        self._get_or_set_hyperparam('algorithm')
        # Set random state.
        self._get_or_set_hyperparam('random_state')
        # Set CV strategy.
        self._get_or_set_hyperparam('hyperparam_strategy')

    def __repr__(self):
        s = "SupervisedClassifier(%s, algorithm='%s', random_state=%s)" % \
            (self._classes, self._hyperparams['algorithm'], self._hyperparams['random_state'])
        return s

    __str__ = __repr__

    def description(self):
        if self._hyperparams['algorithm'] == SupervisedClassifier.LOGISTIC_REGRESSION:
            return self._describe_logistic_regression()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.REGRESS_AND_ROUND:
            return self._describe_regress_and_round()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.DECISION_TREE:
            return self._describe_decision_tree()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.RANDOM_FOREST:
            return self._describe_random_forest()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.ADABOOST:
            return self._describe_adaboost()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.GAUSSIAN_NAIVE_BAYES:
            return self._describe_gaussian_naive_bayes()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.SVM:
            return self._describe_svm()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.XGB:
            return self._describe_xgb()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.NN:
            return self._describe_nn()
        else:
            return 'SupervisedClassifier(%s, %s)' % (self._classes, self._hyperparams['algorithm'])

    def _describe_logistic_regression(self):
        coefs = self.coefs()
        cols = self._features
        sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
        linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
        return 'L1_LOGISTIC_REGRESSION(%s)' % linear_model

    def _describe_regress_and_round(self):
        coefs = self.coefs()
        cols = self._features
        sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
        linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
        return 'L1_REGRESS_AND_ROUND(%s)' % linear_model

    def _describe_decision_tree(self):
        params = self._params_decision_tree()
        node_list = list()
        for i in range(params['num_nodes']):
            if params['nodes'][i].get('feature') is None:
                continue
            feature = params['nodes'][i]['feature']
            threshold = params['nodes'][i]['threshold']
            node_list.append('(%s<=%s)'% (feature, threshold))
        decision_path = ', '.join(node_list)
        return 'DECISION_TREE(%s)' % decision_path

    def _describe_random_forest(self):
        params = self._params_random_forest()
        n_estimators = params['n_estimators']
        features = ', '.join(params['decision_features'])
        return 'RANDOM_FOREST(n_estimators=%s, features=[%s])' % (n_estimators, features)

    def _describe_adaboost(self):
        params = self._params_adaboost()
        n_estimators = params['n_estimators']
        features = ', '.join(params['decision_features'])
        base_estimator = params['base_estimator']
        return 'ADABOOST(base_estimator=%s, n_estimators=%s, features=[%s])' % (base_estimator, n_estimators, features)

    def _describe_gaussian_naive_bayes(self):
        params = self._params_gaussian_naive_bayes()
        return 'GAUSSIAN_NAIVE_BAYES(priors=%s)' % params['priors']

    def _describe_svm(self):
        params = self._params_svm()
        return 'SVM(params=%s)' % params

    def _describe_xgb(self):
        params = self._params_xgb()
        return 'XGB(params=%s)' % params

    def _describe_nn(self):
        params = self._params_nn()
        return 'NN(params=%s)' % params

    def algorithm(self):
        return self._hyperparams['algorithm']

    def classes(self):
        return self._classes

    def coefs(self):
        return self._model.coef_[0]

    def hyperparams(self):
        return self._hyperparams

    def _get_or_set_hyperparam(self, hyperparam, y=None):
        # If it's already set, move on.
        TUNEABLE_HYPERPARAMS = [
            'priors', 'n_estimators', 'learning_rate', 'max_depth',
            'min_samples_split', 'min_samples_leaf', 'max_features', 'C'
        ]
        if self._hyperparams.get(hyperparam):
            if hyperparam == 'algorithm':
                if self._hyperparams[hyperparam] not in SupervisedClassifier.SUPPORTED_ALGORITHMS:
                    raise ValueError('Algorithm %s not supported.' % self._hyperparams[hyperparam])
            elif hyperparam == 'hyperparam_strategy':
                if self._hyperparams[hyperparam] not in SupervisedClassifier.HYPERPARAM_STRATEGIES:
                    raise ValueError('Hyperparameter strategy %s not supported.' % self._hyperparams[hyperparam])

            # If the hyperparam has a relevant search space, set the search
            # space to the user defined value.
            if hyperparam in TUNEABLE_HYPERPARAMS:
                self._hyperparam_search_space[hyperparam] = [self._hyperparams[hyperparam]]

            return

        # Otherwise, define a decent initial value, based on algorithm.
        # If the hyperparam has a relevant search space, define it automatically.
        # Code sanitation note: please keep these conditions alphabetized =)
        if hyperparam == 'activation':
            # NN
            self._hyperparams[hyperparam] = 'relu'
            self._hyperparam_search_space[hyperparam] = [
                'logistic', 'tanh', 'relu'
            ]
        elif hyperparam == 'adaboost_algorithm':
            # ADABOOST, DECISION_TREE
            self._hyperparams[hyperparam] = 'SAMME.R'
        elif hyperparam == 'algorithm':
            # SUPPORTED_ALGORITHMS
            self._hyperparams[hyperparam] = SupervisedClassifier.LOGISTIC_REGRESSION
        elif hyperparam == 'base_estimator':
            # ADABOOST
            self._hyperparams[hyperparam] = 'DecisionTreeClassifier'
        elif hyperparam == 'bootstrap':
            # RANDOM_FOREST
            self._hyperparams[hyperparam] = True
        elif hyperparam == 'C':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = 10.0
            self._hyperparam_search_space[hyperparam] = [
                0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0
            ]
        elif hyperparam == 'class_weight':
            # ADABOOST, DECISION_TREE, LOGISTIC_REGRESSION, RANDOM_FOREST
            self._hyperparams[hyperparam] = 'balanced'
        elif hyperparam == 'colsample_bytree':
            # XGB
            self._hyperparam_search_space[hyperparam] = [0.6, 0.8, 1.0]
        elif hyperparam == 'criterion':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = 'gini'
        elif hyperparam == 'cv':
            # SUPPORTED_ALGORITHMS
            self._hyperparams['cv'] = self._build_cv_generator(y)
        elif hyperparam == 'degree':
            # SVM, when kernel='poly'. TODO: in the future, do sub-case grid search as degree is only needed for poly
            self._hyperparams[hyperparam] = 3
            self._hyperparam_search_space[hyperparam] = [
                0, 1, 2, 3, 4, 5, 6
            ]
        elif hyperparam == 'dual':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = False
        elif hyperparam == 'fit_intercept':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = True
        elif hyperparam == 'gamma':
            # SVM, when non-linear kernel 'rbf', 'poly', 'sigmoid'
            self._hyperparams[hyperparam] = 'auto'
            self._hyperparam_search_space[hyperparam] = [
                0.1, 1, 10, 100
            ]
        elif hyperparam == 'hidden_layer_sizes':
            # NN
            self._hyperparams[hyperparam] = (32,)
            self._hyperparam_search_space[hyperparam] = [
                (8,),
                (16,),
                (32,),
                (64,)
            ]
        elif hyperparam == 'hyperparam_strategy':
            # SUPPORTED_ALGORITHMS
            self._hyperparams[hyperparam] = SupervisedClassifier.STOCHASTIC_SEARCH
        elif hyperparam == 'kernel':
            # SVM
            self._hyperparams[hyperparam] = 'rbf'
            self._hyperparam_search_space[hyperparam] = [
                'linear', 'poly', 'rbf', 'sigmoid'
            ]
        elif hyperparam == 'learning_rate':
            # ADABOOST, XGB
            self._hyperparams[hyperparam] = 0.1
            self._hyperparam_search_space[hyperparam] = [
                0.001, 0.01, 0.1, 1.0, 10.0
            ]
        elif hyperparam == 'max_depth':
            # DECISION_TREE, RANDOM_FOREST, XGB (XGB does not allow 'None')
            self._hyperparams[hyperparam] = 3
            # Include 1, 2, 3 to bias towards simpler tree.
            self._hyperparam_search_space[hyperparam] = [1, 2, 3, 4, 5]
        elif hyperparam == 'max_features':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = 'sqrt'
            # Empirical good default values are max_features=n_features for
            # regression problems, and max_features=sqrt(n_features) for
            # classification tasks.
            # http://scikit-learn.org/stable/modules/ensemble.html#forest
            self._hyperparam_search_space[hyperparam] = ['sqrt', 'log2', None]
        elif hyperparam == 'max_iter':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = 100
        elif hyperparam == 'min_child_weight':
            # XGB
            self._hyperparam_search_space[hyperparam] = [1, 5, 10]
        elif hyperparam == 'min_impurity_decrease':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = 0.0
        elif hyperparam == 'max_leaf_nodes':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = None
        elif hyperparam == 'min_samples_leaf':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = 1
            self._hyperparam_search_space[hyperparam] = [0.01, 0.1, 1, 10]
        elif hyperparam == 'min_samples_split':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = 2
            # Include 20 and .02 to bias towards simpler trees.
            self._hyperparam_search_space[hyperparam] = [0.02, 0.2, 2, 20]
        elif hyperparam == 'min_weight_fraction_leaf':
            # DECISION_TREE, RANDOM_FOREST
            self._hyperparams[hyperparam] = 0.0
        elif hyperparam == 'multi_class':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = 'ovr'
        elif hyperparam == 'n_estimators':
            # ADABOOST, RANDOM_FOREST
            if self._hyperparams['algorithm'] == SupervisedClassifier.ADABOOST:
                self._hyperparams[hyperparam] = 30
                self._hyperparam_search_space[hyperparam] = [
                    10, 20, 30, 40, 50
                ]
            elif self._hyperparams['algorithm'] == SupervisedClassifier.RANDOM_FOREST:
                self._hyperparams[hyperparam] = 10
                # The larger the better, but the longer it will take to compute.
                self._hyperparam_search_space[hyperparam] = [
                    2, 5, 10, 15, 20, 25
                ]
        elif hyperparam == 'n_iter':
            # RandomizedSearchCV throws ValueError if n_iter is less than the
            # number of hyperparam options.
            num_hyperparam_settings = np.prod([len(value) for key, value in self._hyperparam_search_space.iteritems()])
            log.debug('num_hyperparam_settings: %s' % num_hyperparam_settings)
            self._hyperparams[hyperparam] = np.min([48, num_hyperparam_settings])
        elif hyperparam == 'n_jobs':
            # SUPPORTED_ALGORITHMS
            # LOGISTIC_REGRESSION parallelization causes multiarray.so to crash.
            # Automatically switch to 1 core so others can ignore this =/
            if self._hyperparams['algorithm'] == SupervisedClassifier.LOGISTIC_REGRESSION:
                self._hyperparams[hyperparam] = 1
            elif self._hyperparams['algorithm'] == SupervisedClassifier.REGRESS_AND_ROUND:
                self._hyperparams[hyperparam] = 1
            else:
                self._hyperparams[hyperparam] = -1
        elif hyperparam == 'oob_score':
            # RANDOM_FOREST
            self._hyperparams[hyperparam] = False
        elif hyperparam == 'penalty':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = 'l1'
        elif hyperparam == 'presort':
            # DECISION_TREE
            self._hyperparams[hyperparam] = False
        elif hyperparam == 'priors':
            # GAUSSIAN_NAIVE_BAYES
            self._hyperparams[hyperparam] = None
            self._hyperparam_search_space[hyperparam] = [
                [0.0001, 0.9999], [0.001, 0.999], [0.01, 0.99], [0.05, 0.95],
                [0.1, 0.9], [0.25, 0.75],
                [0.5, 0.5],
                [0.75, 0.25], [0.9, 0.1],
                [0.95, 0.05], [0.99, 0.01], [0.999, 0.001], [0.9999, 0.0001]
            ]
        elif hyperparam == 'random_state':
            # SUPPORTED_ALGORITHMS
            self._hyperparams[hyperparam] = None
        elif hyperparam == 'scoring':
            # SUPPORTED_ALGORITHMS
            # Assume unbalanced classification problems, so use roc auc.
            # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
            scorer = make_scorer(roc_auc_score, needs_threshold=True)
            self._hyperparams['scoring'] = scorer
        elif hyperparam == 'solver':
            # LOGISTIC_REGRESSION, NN
            if self._hyperparams['algorithm'] == SupervisedClassifier.LOGISTIC_REGRESSION:
                self._hyperparams[hyperparam] = 'saga'
            elif self._hyperparams['algorithm'] == SupervisedClassifier.NN:
                self._hyperparams[hyperparam] = 'adam'
                self._hyperparam_search_space[hyperparam] = [
                    'lbfgs', 'sgd', 'adam'
                ]
        elif hyperparam == 'splitter':
            # DECISION_TREE
            self._hyperparams[hyperparam] = 'best'
        elif hyperparam == 'subsample':
            # XGB
            self._hyperparam_search_space[hyperparam] = [0.6, 0.8, 1.0]
        elif hyperparam == 'tol':
            # LOGISTIC_REGRESSION
            self._hyperparams[hyperparam] = 0.0001
        elif hyperparam == 'warm_start':
            # RANDOM_FOREST
            self._hyperparams[hyperparam] = False

    def params(self):
        '''
        sx: This function is used after parameters were set.

        :return:
        '''
        if self._hyperparams['algorithm'] == SupervisedClassifier.LOGISTIC_REGRESSION:
            return self._params_regression()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.REGRESS_AND_ROUND:
            return self._params_regression()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.DECISION_TREE:
            return self._params_decision_tree()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.RANDOM_FOREST:
            return self._params_random_forest()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.ADABOOST:
            return self._params_adaboost()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.GAUSSIAN_NAIVE_BAYES:
            return self._params_gaussian_naive_bayes()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.SVM:
            return self._params_svm()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.XGB:
            return self._params_xgb()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.NN:
            return self._params_nn()

    def _params_regression(self):
        params = {}
        coefs = self.coefs()
        columns = self._features
        feature_labels = columns.values
        for feature in feature_labels:
            weight = coefs[columns.get_loc(feature)]
            params.update({feature: weight})

        return params

    def _tree_to_dict(self, tree):
        tree_dict = {'nodes': {}}
        decision_features = set()
        feature_labels = self._features.values
        # Iterate through nodes in tree.
        for i in range(tree.node_count):
            # Build data about each node.
            node = {}
            # If not a leaf node, add decision information.
            if tree.children_left[i] != tree.children_right[i]:
                node['feature'] = feature_labels[tree.feature[i]]
                decision_features.add(node['feature'])
                node['threshold'] = tree.threshold[i]
                node['left_child'] = tree.children_left[i]
                node['right_child'] = tree.children_right[i]
            class_weights = tree.value[i].tolist()[0]
            node['class_weights'] = class_weights
            node['prediction'] = self._classes[class_weights.index(np.max(class_weights))]

            tree_dict['nodes'].update({i: node})

        # Add feature important information
        num_features = len(self._features)
        importances = {}
        for i in range(num_features):
            feature = self._features[i]
            if feature in decision_features:
                importance = self._model.feature_importances_[i]
                importances.update({feature: importance})

        decision_features = sorted(list(decision_features), key=lambda x:importances[x], reverse=True)
        tree_dict['decision_features'] = ['%s (%.3f)' % (f, importances[f]) for f in decision_features]

        # Add tree-level information.
        tree_dict['depth'] = tree.max_depth
        tree_dict['num_nodes'] = tree.node_count

        return tree_dict

    def _params_decision_tree(self):
        t = self._model.tree_
        return self._tree_to_dict(t)

    def _params_random_forest(self):
        params = {'estimators': []}
        params['n_estimators'] = 0
        decision_features = set()
        for estimator in self._model.estimators_:
            tree_dict = self._tree_to_dict(estimator.tree_)
            params['estimators'].append(tree_dict)
            params['n_estimators'] += 1
            # Build list of forest-wide decision features.
            for feature in tree_dict['decision_features']:
                decision_features.add(' '.join(feature.split()[:-1]))

        num_features = self._model.n_features_
        importances = {}
        for i in range(num_features):
            feature = self._features[i]
            if feature in decision_features:
                importance = self._model.feature_importances_[i]
                importances.update({feature: importance})

        decision_features = sorted(list(decision_features), key=lambda x:importances[x], reverse=True)
        params['decision_features'] = ['%s (%.3f)' % (f, importances[f]) for f in decision_features]

        return params

    def _params_adaboost(self):
        params = {}
        params['base_estimator'] = self._hyperparams['base_estimator']
        params['n_estimators'] = self._hyperparams['n_estimators']
        decision_features = set()
        for estimator in self._model.estimators_:
            tree_dict = self._tree_to_dict(estimator.tree_)
            for feature in tree_dict['decision_features']:
                decision_features.add(' '.join(feature.split()[:-1]))

        num_features = len(self._features)
        importances = {}
        for i in range(num_features):
            feature = self._features[i]
            if feature in decision_features:
                importance = self._model.feature_importances_[i]
                importances.update({feature: importance})

        decision_features = sorted(list(decision_features), key=lambda x:importances[x], reverse=True)
        params['decision_features'] = ['%s (%.3f)' % (f, importances[f]) for f in decision_features]

        return params

    def _params_gaussian_naive_bayes(self):
        params = {}
        params['priors'] = list(self._model.class_prior_)
        params['thetas'] = list(self._model.theta_[1,:])
        params['sigmas'] = list(self._model.sigma_[1,:])
        return params

    def _params_svm(self):
        return self._model.get_params() # TODO sxu: come back later for a specific list of params?

    def _params_xgb(self):
        return self._model.get_params()

    def _params_nn(self):
        return self._model.get_params()

    def _maybe_reshape_y(self, y):
        # If necessary, reshape y from (n_samples, 1) to (n_samples, )
        try:
            num_cols = y.shape[1]
            y = column_or_1d(y)
            log.debug('Reshaped y to 1d.')
        except IndexError:
            log.debug('Did not need to reshape y to 1d.')

        return y

    def _build_cv_generator(self, y=None):
        # Use information about X to build a cross-validation split generator.
        # http://scikit-learn.org/stable/modules/cross_validation.html#cross-validation
        # There are a few general strategies for cross-validation:
        #   k-fold split: Split training set into k partitions, train using k-1,
        #       and validate using the kth. Loop through k validation partitions.
        #       Basis for all other cross-validation strategies.
        #       Assumes each sample is independent and identically distributed.
        #   shuffle split: Instead of mixing k partitions into training and
        #       validation sets, just generate a random train/validation split
        #       and do that k times. Typically efficient, but also can fail
        #       to use each sample equally, e.g. if a sample is only ever
        #       in the validation set or the training set.
        #   leave one out (LOO): k-fold CV where k = n, so each partition only
        #       has one sample in the test data. Test error across partitions
        #       typically has high variance between error is either 0 or 1.
        #       Empirically, LOO is typically worse than 5- or 10-fold CV.
        #       Can tweak to leave P out (LPO). Because (n choose p) is much
        #       greater than (n choose 1), this process tends to be
        #       computationally intensive, and perhaps not worth the effort.
        #   repetition: k-fold CV run multiple times, with different partitions
        #       for each run. Good way to get more learning from limited data.
        #   stratification: for unbalanced classification problems, enforce
        #       a constraint on either k-fold or shuffle splits to require
        #       an equal split of each class between the training and
        #       validation sets.
        #   grouping: for some classification problems, the samples are not iid.
        #       In particular, for medical applications, if there are multiple
        #       samples taken from a single patient, those samples are by
        #       definition not independent. Moreover, we typically care about
        #       whether we can accurately classify new unseen patients based
        #       on patients we saw in the past. Therefore, grouping guarantees
        #       that any particular group (e.g. a single patient_id) is only
        #       in the training set or in the validation set.
        #   time series split: data representing a time series also break the
        #       i.i.d. assumption, because samples that are near each other
        #       in time are by definition correlated (autocorrelation). To get
        #       around this, split the data into k partitions, and in each
        #       of k loops, use partions [0, i] to train and partition [i+1]
        #       for validation. Ensure that you are always training on the past
        #       and validating on the "future."
        #
        # TODO(sbala): Ideally, we'd find a way to do stratified group k-fold.
        # sklearn only provides StratifiedKFold and GroupKFold out of the box.
        # Given how unbalanced many of our classification problems are, use
        # StratifiedKFold for now, but we need something better.

        # Use information about y to determine n_splits.
        # In certain pathological cases (esp. with bifurcated classifiers)
        # there might be fewer than n examples of a given class in y.
        # If that's the case, n_splits can't be greater than n_samples.
        if y is not None:
            log.debug('y.value_counts(): %s' % Series(y).value_counts())
            max_possible_splits = np.min(Series(y).value_counts())
            log.debug('max_possible_splits: %s' % max_possible_splits)
            n_splits = np.min([10, max_possible_splits])
        else:
            n_splits = 10
        log.debug('n_splits: %s' % n_splits)

        if self.CV_STRATEGY == 'StratifiedKFold':
            return StratifiedKFold(n_splits=n_splits, shuffle=False, \
                                random_state=self._hyperparams['random_state'])
        elif self.CV_STRATEGY == 'GroupKFold':
            '''
            GroupKFold is not randomized at all. Hence the random_state=None
            '''
            return GroupKFold(n_splits=n_splits)

    def train(self, X, y, groups=None):

        self._groups = groups
        assert ('pat_id' not in X.columns)

        self._features = X.columns

        y = self._maybe_reshape_y(y)

        # Verify that there are at least 2 samples of each class.
        value_counts = Series(y).value_counts()
        log.debug('y.value_counts(): %s' % value_counts)
        for class_label in self._classes:
            # If there aren't 2+ samples of each class, exit gracefully.
            try:
                num_samples = value_counts[class_label]
                if num_samples < 10:
                    log.error('Insufficient samples (%s) of label %s.' % (num_samples, class_label))
                    return SupervisedClassifier.INSUFFICIENT_SAMPLES
            except KeyError:
                log.error('Insufficient samples (0) of label %s.' % class_label)
                return SupervisedClassifier.INSUFFICIENT_SAMPLES

        log.info('Training %s classifier...' % self._hyperparams['algorithm'])
        if self._hyperparams['algorithm'] == SupervisedClassifier.DECISION_TREE:
            self._train_decision_tree(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.LOGISTIC_REGRESSION:
            self._train_logistic_regression(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.RANDOM_FOREST:
            self._train_random_forest(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.REGRESS_AND_ROUND:
            self._train_regress_and_round(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.ADABOOST:
            self._train_adaboost(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.GAUSSIAN_NAIVE_BAYES:
            self._train_gaussian_naive_bayes(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.SVM:
            self._train_svm(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.XGB:
            self._train_xgb(X, y)
        elif self._hyperparams['algorithm'] == SupervisedClassifier.NN:
            self._train_nn(X, y)

        return SupervisedClassifier.TRAINED

    def _train_gaussian_naive_bayes(self, X, y):
        # Define hyperparams.
        # http://scikit-learn.org/stable/modules/naive_bayes.html#naive-bayes
        self._get_or_set_hyperparam('priors')
        self._get_or_set_hyperparam('n_jobs')
        self._get_or_set_hyperparam('scoring')

        # Build initial model.
        self._model = GaussianNB(priors=self._hyperparams['priors'])

        # Tune hyperparams.
        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_adaboost(self, X, y):
        # Define hyperparams.
        # http://scikit-learn.org/stable/modules/ensemble.html#adaboost
        self._get_or_set_hyperparam('base_estimator')
        self._get_or_set_hyperparam('n_estimators')
        self._get_or_set_hyperparam('learning_rate')
        self._get_or_set_hyperparam('adaboost_algorithm')
        self._get_or_set_hyperparam('n_jobs')
        self._get_or_set_hyperparam('class_weight')
        self._get_or_set_hyperparam('scoring')

        # Build initial model.
        self._model = AdaBoostClassifier(\
            base_estimator=DecisionTreeClassifier(class_weight='balanced'),
            n_estimators=self._hyperparams['n_estimators'],
            learning_rate=self._hyperparams['learning_rate'],
            algorithm=self._hyperparams['adaboost_algorithm'],
            random_state=self._hyperparams['random_state']
        )

        # Tune hyperparams.
        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_xgb(self, X, y):
        '''
        Tianqi Chen:
        Adaboost and gradboosting [XGBoost] are two different ways to derive boosters.
        Both are generic. I like gradboosting better because it works for generic loss functions,
        while adaboost is derived mainly for classification with exponential loss.

        Konrad Banachewicz:
        Adaboost is more of a meta-estimator - you can fit anything as base (although most people use trees)
        xgboost is more flexible, i.e. has more customizable parameters

        :param X:
        :param y:
        :return:
        '''
        #
        self._get_or_set_hyperparam('scoring')
        self._get_or_set_hyperparam('n_jobs')

        self._get_or_set_hyperparam('learning_rate')
        self._get_or_set_hyperparam('min_child_weight')
        self._get_or_set_hyperparam('gamma')
        self._get_or_set_hyperparam('subsample')
        self._get_or_set_hyperparam('colsample_bytree')
        self._get_or_set_hyperparam('max_depth')

        # Build initial model.
        self._model = XGBClassifier(
            random_state=self._hyperparams['random_state']
        )

        # Tune hyperparams.
        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_decision_tree(self, X, y):
        # Define hyperparameter space.
        # http://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
        self._get_or_set_hyperparam('criterion')
        self._get_or_set_hyperparam('splitter')
        self._get_or_set_hyperparam('max_depth')
        self._get_or_set_hyperparam('min_samples_split')
        self._get_or_set_hyperparam('min_samples_leaf')
        self._get_or_set_hyperparam('min_weight_fraction_leaf')
        self._get_or_set_hyperparam('max_features')
        self._get_or_set_hyperparam('max_leaf_nodes')
        self._get_or_set_hyperparam('min_impurity_decrease')
        self._get_or_set_hyperparam('class_weight')
        self._get_or_set_hyperparam('presort')
        self._get_or_set_hyperparam('scoring')
        self._get_or_set_hyperparam('n_jobs')

        # Initialize model with naive hyperparameter values.
        self._model = DecisionTreeClassifier(\
            criterion=self._hyperparams['criterion'], \
            splitter=self._hyperparams['splitter'], \
            max_depth=self._hyperparams['max_depth'], \
            min_samples_split=self._hyperparams['min_samples_split'], \
            min_samples_leaf=self._hyperparams['min_samples_leaf'], \
            min_weight_fraction_leaf=self._hyperparams['min_weight_fraction_leaf'], \
            max_features=self._hyperparams['max_features'], \
            random_state=self._hyperparams['random_state'], \
            max_leaf_nodes=self._hyperparams['max_leaf_nodes'], \
            min_impurity_decrease=self._hyperparams['min_impurity_decrease'], \
            class_weight=self._hyperparams['class_weight'], \
            presort=self._hyperparams['presort']
        )

        # Tune hyperparams.
        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_logistic_regression(self, X, y):
        # Define hyperparameter space.
        # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html
        self._get_or_set_hyperparam('C')
        self._get_or_set_hyperparam('fit_intercept')
        self._get_or_set_hyperparam('dual')
        self._get_or_set_hyperparam('penalty')
        self._get_or_set_hyperparam('scoring')
        self._get_or_set_hyperparam('solver')
        self._get_or_set_hyperparam('tol')
        self._get_or_set_hyperparam('max_iter')
        self._get_or_set_hyperparam('n_jobs')
        self._get_or_set_hyperparam('multi_class')
        self._get_or_set_hyperparam('class_weight')

        # Build initial model.
        self._model = LogisticRegression(
            penalty=self._hyperparams['penalty'],
            fit_intercept=self._hyperparams['fit_intercept'],
            dual=self._hyperparams['dual'],
            tol=self._hyperparams['tol'],
            C=self._hyperparams['C'],
            class_weight=self._hyperparams['class_weight'],
            random_state=self._hyperparams['random_state'],
            solver=self._hyperparams['solver'],
            max_iter=self._hyperparams['max_iter'],
            multi_class=self._hyperparams['multi_class'],
            n_jobs=self._hyperparams['n_jobs']
        )

        # Tune hyperparams.
        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_svm(self, X, y):
        # Define hyperparams.
        '''
        List of parameters:
        C: float, optional (default=1.0)
            Penalty parameter C of the error term.
        kernel: string, optional (default='rbf')
            must be one of 'linear', 'poly', 'rbf', 'sigmoid', 'precomputed', or a callable.
        degree : int, optional (default=3)
            Degree of the polynomial kernel function ('poly'). Ignored by all other kernels.
        gamma: float, optional (default='auto').
            Kernel coefficient for 'rbf', 'poly', 'sigmoid'.
        coef0: float, optional (default=0.)
            Independent term in kernel func.
        shrinking: boolean, optional (default=True)
            Whether to use the shrinking heuristic.
        probability: boolean, optional (default=False)
            Whether to enable probability estimates (could slow down fit).
        tol: float, optional (defualt=1e-3)
            Tolerance for stopping criterion.
        cache_size: float, optional.
            Specify the size of the kernel cache (in MB).
        class_weight: {dict, 'balanced'}, optional.
            'balanced' mode use automatically: n_samples / (n_classes * np.bincount(y))
        verbose: bool, default: False
        max_iter: int, optional (default=1)
            Hard limit on iterations within solver, or -1 for no limit.
        decision_function_shape: 'ovo', 'ovr' (default)
            Whether to return a one-vs-rest (ovr) of shape (n_samples, n_classes) as all other classes, or the original
            one-vs-one (ovo) decision func of libsvm which has shape (n_sample, n_classes * (n_classes-1)/2).
        random_state:.

        :return:
        '''
        # http://scikit-learn.org/stable/modules/svm.html#svm
        self._get_or_set_hyperparam('scoring')
        self._get_or_set_hyperparam('n_jobs')

        self._model = SVC(probability=True,
                          random_state=self._hyperparams['random_state'])

        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_random_forest(self, X, y):
        # Define hyperparams.
        # http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
        self._get_or_set_hyperparam('n_estimators')
        self._get_or_set_hyperparam('criterion')
        self._get_or_set_hyperparam('max_depth')
        self._get_or_set_hyperparam('min_samples_split')
        self._get_or_set_hyperparam('min_samples_leaf')
        self._get_or_set_hyperparam('min_weight_fraction_leaf')
        self._get_or_set_hyperparam('max_features')
        self._get_or_set_hyperparam('max_leaf_nodes')
        self._get_or_set_hyperparam('min_impurity_decrease')
        self._get_or_set_hyperparam('bootstrap')
        self._get_or_set_hyperparam('oob_score')
        self._get_or_set_hyperparam('n_jobs')
        self._get_or_set_hyperparam('warm_start')
        self._get_or_set_hyperparam('class_weight')
        self._get_or_set_hyperparam('scoring')

        # Initialize model with naive hyperparameter values.
        self._model = RandomForestClassifier( \
            n_estimators=self._hyperparams['n_estimators'],
            criterion=self._hyperparams['criterion'],
            max_depth=self._hyperparams['max_depth'],
            min_samples_split=self._hyperparams['min_samples_split'],
            min_samples_leaf=self._hyperparams['min_samples_leaf'],
            min_weight_fraction_leaf=self._hyperparams['min_weight_fraction_leaf'],
            max_features=self._hyperparams['max_features'],
            max_leaf_nodes=self._hyperparams['max_leaf_nodes'],
            min_impurity_decrease=self._hyperparams['min_impurity_decrease'],
            bootstrap=self._hyperparams['bootstrap'],
            oob_score=self._hyperparams['oob_score'],
            n_jobs=self._hyperparams['n_jobs'],
            warm_start=self._hyperparams['warm_start'],
            class_weight=self._hyperparams['class_weight'],
            random_state=self._hyperparams['random_state']
        )

        # Tune hyperparams.
        self._tune_hyperparams(self._hyperparam_search_space, X, y)

    def _train_regress_and_round(self, X, y):
        self._train_logistic_regression(X, y)
        self._tune_hyperparams_regress_and_round(X, y)

    def _train_nn(self, X, y):
        self._get_or_set_hyperparam('scoring')
        self._get_or_set_hyperparam('n_jobs')

        self._model = MLPClassifier(
            random_state=self._hyperparams['random_state']
        )

        self._tune_hyperparams(self._hyperparam_search_space, X, y)


    def _tune_hyperparams_regress_and_round(self, X, y):
        self._hyperparams['hyperparam_strategy'] = SupervisedClassifier.EXHAUSTIVE_SEARCH
        log.info('Tuning hyperparams via %s...' % self._hyperparams['hyperparam_strategy'])
        # If not provided, search for best coef_max.
        if self._hyperparams.get('coef_max') is None:
            self._hyperparams['coef_max'] = self._tune_coef_max(X, y)

        # Round linear coefficients.
        self._round_coefs(self._hyperparams['coef_max'])
        log.debug('hyperparams: %s' % self.hyperparams())
        log.debug('params: %s' % self.params())

    def _tune_coef_max(self, X, y):
        # The only way to easily compute scores is to modify the model itself.
        # Keep the unrounded coefs so it's always possible to go back.
        unrounded_coefs = self.coefs().copy()

        M_grid = [1, 2, 3, 4, 5]
        M_grid_scores = []

        # Compute roc_auc scores.
        coef_max = 0
        max_roc_auc = 0
        min_roc_auc = 1.0
        for i in range(len(M_grid)):
            # Tweak the model.
            self._round_coefs(M_grid[i])
            # Compute ROC AUC.
            scores = cross_val_score(self._model, X, y, \
                cv=self._hyperparams['cv'], \
                groups=self._groups, \
                scoring=self._hyperparams['scoring'], \
                n_jobs=self._hyperparams['n_jobs'])
            # Compute mean across K folds.
            mean_score = np.mean(scores)
            M_grid_scores.append(mean_score)

            # Conditionally change coef_max and max_roc_auc.
            if mean_score > max_roc_auc:
                coef_max = M_grid[i]
                max_roc_auc = mean_score
            if mean_score < min_roc_auc:
                min_roc_auc = mean_score

            # Reset coefs and return.
            self._model.coef_[0] = unrounded_coefs

        # The optimal M value from Jung et al. is 3.
        # https://arxiv.org/abs/1702.04690
        log.debug('tune(M): %s --> %s' % (3, coef_max))
        log.debug('tune(roc_auc): %s --> %s' % (min_roc_auc, max_roc_auc))

        return coef_max

    def _round_coefs(self, coef_max):
        # Based on Jung et al. https://arxiv.org/abs/1702.04690
        # w_j = round((M * beta_j) / (max_i|beta_i|))
        # coef_max = M = max rounded coefficient value
        # beta_max = max_i|beta_i| = largest unrounded regression coefficient
        beta_max = max([abs(c) for c in self._model.coef_[0]])
        self._model.coef_[0] = [round((coef_max * c) / (beta_max)) for c in self._model.coef_[0]]

    def _tune_hyperparams(self, hyperparam_search_space, X, y):
        log.info('Tuning hyperparameters via %s...' % self._hyperparams['hyperparam_strategy'])
        log.debug('hyperparam_search_space: %s' % str(hyperparam_search_space))
        # Log the pre-tuning score.
        self._get_or_set_hyperparam('cv', y)
        log.debug('initial hyperparams: %s' % self._hyperparams)
        pre_tuning_score = np.mean(cross_val_score(self._model, X, y, \
                                    cv=self._hyperparams['cv'], \
                                    groups=self._groups, \
                                    scoring=self._hyperparams['scoring'], \
                                    n_jobs=self._hyperparams['n_jobs']))

        # Initialize hyperparam tuner.
        # Assume the model was initialized before this function.
        if self._hyperparams['hyperparam_strategy'] == SupervisedClassifier.EXHAUSTIVE_SEARCH:
            tuner = GridSearchCV(self._model, hyperparam_search_space, \
                                    scoring=self._hyperparams['scoring'], \
                                    n_jobs=self._hyperparams['n_jobs'], \
                                    iid=False, \
                                    refit=True, \
                                    cv=self._hyperparams['cv'], \
                                    return_train_score=False)
        elif self._hyperparams['hyperparam_strategy'] == SupervisedClassifier.STOCHASTIC_SEARCH:
            self._get_or_set_hyperparam('n_iter')
            tuner = RandomizedSearchCV(self._model, hyperparam_search_space, \
                                        scoring=self._hyperparams['scoring'], \
                                        n_iter=self._hyperparams['n_iter'], \
                                        n_jobs=self._hyperparams['n_jobs'], \
                                        iid=False, \
                                        refit=True, \
                                        cv=self._hyperparams['cv'], \
                                        random_state=self._hyperparams['random_state'], \
                                        return_train_score=False)
        tuner.fit(X, y, groups=self._groups)

        # Set model and hyperparams.
        self._model = tuner.best_estimator_
        for key in tuner.best_params_.keys():
            log.debug('tune(%s): %s --> %s' % (key, self._hyperparams[key], \
                        tuner.best_params_[key]))
            self._hyperparams[key] = tuner.best_params_[key]
        log.debug('tune(%s): %s --> %s' % (self._hyperparams['scoring'],\
                    pre_tuning_score, tuner.best_score_))
        log.debug('hyperparams: %s' % self._hyperparams)
        log.debug('params: %s' % self.params())

    def predict(self, X):
        return self._model.predict(X)

    def predict_probability(self, X):
        return self._model.predict_proba(X)
