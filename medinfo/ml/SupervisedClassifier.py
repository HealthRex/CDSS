#!/usr/bin/python
"""
Generic module for supervised machine learning classification.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score, make_scorer
from sklearn.utils.validation import column_or_1d
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

from medinfo.common.Util import log

class SupervisedClassifier:
    # Define string constants for all supported ML algorithms so that
    # clients can define which algorithm to call.
    DECISION_TREE = 'decision-tree'
    LOGISTIC_REGRESSION = 'l1-logistic-regression-cross-validation'
    RANDOM_FOREST = 'random-forest'
    REGRESS_AND_ROUND = 'regress-and-round'

    # TODO(sbala): Naive Bayes: http://scikit-learn.org/stable/modules/naive_bayes.html#naive-bayes
    # TODO(sbala): Nearest Neighbors: http://scikit-learn.org/stable/modules/neighbors.html#neighbors
    # TODO(sbala): Neural Network: http://scikit-learn.org/stable/modules/neural_networks_supervised.html#neural-networks-supervised
    # TODO(sbala): SVM: http://scikit-learn.org/stable/modules/svm.html#svm
    # TODO(sbala): Nearest Neighbors: http://scikit-learn.org/stable/modules/neighbors.html#neighbors
    # TODO(sbala): Adaboost: http://scikit-learn.org/stable/modules/ensemble.html#adaboost
    SUPPORTED_ALGORITHMS = [DECISION_TREE, LOGISTIC_REGRESSION, RANDOM_FOREST, \
        REGRESS_AND_ROUND]

    EXHAUSTIVE_SEARCH = 'exhaustive-search'
    STOCHASTIC_SEARCH = 'stochastic-search'
    HYPERPARAM_STRATEGIES = [EXHAUSTIVE_SEARCH, STOCHASTIC_SEARCH]

    def __init__(self, classes, hyperparams=None):
        self._classes = classes

        # Initialize params.
        self._params = {}

        # Initialize hyperparams.
        if hyperparams is None:
            self._hyperparams = {}
        else:
            self._hyperparams = hyperparams
        # Set algorithm.
        if self._hyperparams.get('algorithm') is None:
            self._hyperparams['algorithm'] = SupervisedClassifier.LOGISTIC_REGRESSION
        elif self._hyperparams['algorithm'] not in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % self._hyperparams['algorithm'])
        self._algorithm = self._hyperparams['algorithm']
        # Set random state.
        if self._hyperparams.get('random_state') is None:
            self._hyperparams['random_state'] = None
        # Set CV strategy.
        if self._hyperparams.get('hyperparam_strategy') is None:
            self._hyperparams['hyperparam_strategy'] = SupervisedClassifier.STOCHASTIC_SEARCH
        elif self._hyperparams['hyperparam_strategy'] not in SupervisedClassifier.HYPERPARAM_STRATEGIES:
            raise ValueError('Hyperparameter strategy %s not supported.' % self._hyperparams['hyperparam_strategy'])

    def __repr__(self):
        s = "SupervisedClassifier(%s, algorithm='%s', random_state=%s)" % \
            (self._classes, self._algorithm, self._hyperparams['random_state'])
        return s

    __str__ = __repr__

    def description(self):
        if self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            coefs = self.coefs()
            cols = self._features
            sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
            linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
            return 'L1_LOGISTIC_REGRESSION(%s)' % linear_model
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            coefs = self.coefs()
            cols = self._features
            sig_features = [(coefs[cols.get_loc(f)], f) for f in cols.values if coefs[cols.get_loc(f)] > 0]
            linear_model = ' + '.join('%s*%s' % (weight, feature) for weight, feature in sig_features)
            return 'L1_REGRESS_AND_ROUND(%s)' % linear_model
        elif self._hyperparams['algorithm'] == SupervisedClassifier.DECISION_TREE:
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
        elif self._hyperparams['algorithm'] == SupervisedClassifier.RANDOM_FOREST:
            params = self._params_random_forest()
            n_estimators = params['n_estimators']
            features = ', '.join(params['decision_features'])
            return 'RANDOM_FOREST(n_estimators=%s, features=[%s])' % (n_estimators, features)
        else:
            return 'SupervisedClassifier(%s, %s)' % (self._classes, self._algorithm)

    def algorithm(self):
        return self._algorithm

    def classes(self):
        return self._classes

    def coefs(self):
        return self._model.coef_[0]

    def hyperparams(self):
        return self._hyperparams

    def params(self):
        if self._hyperparams['algorithm'] == SupervisedClassifier.LOGISTIC_REGRESSION:
            return self._params_regression()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.REGRESS_AND_ROUND:
            return self._params_regression()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.DECISION_TREE:
            return self._params_decision_tree()
        elif self._hyperparams['algorithm'] == SupervisedClassifier.RANDOM_FOREST:
            return self._params_random_forest()

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

        # Add tree-level information.
        tree_dict['decision_features'] = sorted(list(decision_features))
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
                decision_features.add(feature)
        params['decision_features'] = sorted(list(decision_features))

        return params

    def _maybe_reshape_y(self, y):
        # If necessary, reshape y from (n_samples, 1) to (n_samples, )
        try:
            num_cols = y.shape[1]
            y = column_or_1d(y)
            log.debug('Reshaped y to 1d.')
        except IndexError:
            log.debug('Did not need to reshape y to 1d.')

        return y

    def _build_cv_generator(self):
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
        return StratifiedKFold(n_splits=10, shuffle=False, \
                                random_state=self._hyperparams['random_state'])

    def train(self, X, y):
        self._features = X.columns
        y = self._maybe_reshape_y(y)
        log.info('Training %s classifier...' % self._hyperparams['algorithm'])
        if self._algorithm == SupervisedClassifier.DECISION_TREE:
            self._train_decision_tree(X, y)
        elif self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            self._train_logistic_regression(X, y)
        elif self._algorithm == SupervisedClassifier.RANDOM_FOREST:
            self._train_random_forest(X, y)
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            self._train_regress_and_round(X, y)

    def _train_decision_tree(self, X, y):
        # Define hyperparameter space.
        # http://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
        self._hyperparams['criterion'] = 'gini'
        self._hyperparams['splitter'] = 'best'
        # Include 1, 2, 3 to bias towards simpler tree.
        self._hyperparams['max_depth'] = None
        # Include 10 and .01 to bias towards simpler trees.
        self._hyperparams['min_samples_split'] = 2
        self._hyperparams['min_samples_leaf'] = 1
        self._hyperparams['min_weight_fraction_leaf'] = 0.0
        self._hyperparams['max_features'] = None
        self._hyperparams['max_leaf_nodes'] = None
        self._hyperparams['min_impurity_decrease'] = 0.0
        self._hyperparams['class_weight'] = 'balanced'
        self._hyperparams['presort'] = None
        # Assume unbalanced classification problems, so use f1_score.
        # Cannot compute an ROC curve because decision trees have no ROC.
        # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
        scorer = make_scorer(f1_score)
        self._hyperparams['scoring'] = scorer
        self._hyperparams['n_jobs'] = -1

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

        # Search hyperparameter space for better values.
        hyperparam_search_space = {
            'max_depth': [1, 2, 3, 4, 5, None],
            'min_samples_split': [2, 20, 0.02, 0.1, 0.2],
            'min_samples_leaf': [1, 10, 0.01, 0.05, 0.1],
            # Empirical good default values are max_features=n_features for
            # regression problems, and max_features=sqrt(n_features) for
            # classification tasks.
            # http://scikit-learn.org/stable/modules/ensemble.html#forest
            'max_features': ['sqrt', 'log2', None]
        }
        log.info('Tuning hyperparameters...')
        self._tune_hyperparams(hyperparam_search_space, X, y)
        log.debug('params: %s' % self.params())

    def _train_logistic_regression(self, X, y):
        # Define hyperparameter space.
        # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html
        self._hyperparams['C'] = 10.0
        self._hyperparams['hyperparam_strategy'] = SupervisedClassifier.EXHAUSTIVE_SEARCH
        self._hyperparams['fit_intercept'] = True
        self._hyperparams['dual'] = False
        self._hyperparams['penalty'] = 'l1'
        # Assume unbalanced classification problems, so use roc auc.
        # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
        scorer = make_scorer(roc_auc_score, needs_threshold=True)
        self._hyperparams['scoring'] = scorer
        self._hyperparams['solver'] = 'saga'
        self._hyperparams['tol'] = 0.0001
        self._hyperparams['max_iter'] = 10000
        self._hyperparams['class_weight'] = 'balanced'
        self._hyperparams['n_jobs'] = -1
        self._hyperparams['multi_class'] = 'ovr'

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
        hyperparam_search_space = {
            'C': [
                10000.0, 1000.0, 100.0, 10.0, 1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001
            ]
        }
        log.info('Tuning hyperparameters...')
        self._tune_hyperparams(hyperparam_search_space, X, y)
        log.debug('params: %s' % self.params())

    def _train_random_forest(self, X, y):
        # Define hyperparams.
        # http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
        self._hyperparams['n_estimators'] = 10
        self._hyperparams['criterion'] = 'gini'
        self._hyperparams['max_depth'] = None
        self._hyperparams['min_samples_split'] = 2
        self._hyperparams['min_samples_leaf'] = 1
        self._hyperparams['min_weight_fraction_leaf'] = 0.0
        self._hyperparams['max_features'] = 'sqrt'
        self._hyperparams['max_leaf_nodes'] = None
        self._hyperparams['min_impurity_decrease'] = 0.0
        self._hyperparams['bootstrap'] = True
        self._hyperparams['oob_score'] = False
        self._hyperparams['n_jobs'] = -1
        self._hyperparams['warm_start'] = False
        self._hyperparams['class_weight'] = 'balanced'
        # Assume unbalanced classification problems, so use f1_score.
        # Cannot compute an ROC curve because decision trees have no ROC.
        # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
        scorer = make_scorer(f1_score)
        self._hyperparams['scoring'] = scorer

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

        # Search hyperparameter space for better values.
        hyperparam_search_space = {
            # The larger the better, but the longer it will take to compute.
            'n_estimators': [2, 5, 10, 15, 20, 25],
            'max_depth': [1, 2, 3, 4, 5, None],
            'min_samples_split': [2, 20, 0.02, 0.1, 0.2],
            'min_samples_leaf': [1, 10, 0.01, 0.05, 0.1],
            # Empirical good default values are max_features=n_features for
            # regression problems, and max_features=sqrt(n_features) for
            # classification tasks.
            # http://scikit-learn.org/stable/modules/ensemble.html#forest
            'max_features': ['sqrt', 'log2', None]
        }
        log.info('Tuning hyperparameters...')
        self._tune_hyperparams(hyperparam_search_space, X, y)
        log.debug('hyperparams: %s' % self.hyperparams())
        log.debug('params: %s' % self.params())

    def _train_regress_and_round(self, X, y):
        self._train_logistic_regression(X, y)
        log.info('Tuning hyperparameters...')
        self._tune_hyperparams_regress_and_round(X, y)
        log.debug('params: %s' % self.params())

    def _tune_hyperparams_regress_and_round(self, X, y):
        self._hyperparams['hyperparam_strategy'] = SupervisedClassifier.EXHAUSTIVE_SEARCH
        # If not provided, search for best coef_max.
        if self._hyperparams.get('coef_max') is None:
            self._hyperparams['coef_max'] = self._tune_coef_max(X, y)

        # Round linear coefficients.
        self._round_coefs(self._hyperparams['coef_max'])

    def _round_coefs(self, coef_max):
        # Based on Jung et al. https://arxiv.org/abs/1702.04690
        # w_j = round((M * beta_j) / (max_i|beta_i|))
        # coef_max = M = max rounded coefficient value
        # beta_max = max_i|beta_i| = largest unrounded regression coefficient
        beta_max = max([abs(c) for c in self._model.coef_[0]])
        self._model.coef_[0] = [round((coef_max * c) / (beta_max)) for c in self._model.coef_[0]]

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

    def _tune_hyperparams(self, hyperparam_search_space, X, y):
        # Log the pre-tuning score.
        self._hyperparams['cv'] = self._build_cv_generator()
        pre_tuning_score = np.mean(cross_val_score(self._model, X, y, \
                                    cv=self._hyperparams['cv'], \
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
            tuner = RandomizedSearchCV(self._model, hyperparam_search_space, \
                                        scoring=self._hyperparams['scoring'], \
                                        n_jobs=self._hyperparams['n_jobs'], \
                                        iid=False, \
                                        refit=True, \
                                        cv=self._hyperparams['cv'], \
                                        random_state=self._hyperparams['random_state'], \
                                        return_train_score=False)
        tuner.fit(X, y)

        # Set model and hyperparams.
        self._model = tuner.best_estimator_
        for key in tuner.best_params_.keys():
            log.debug('tune(%s): %s --> %s' % (key, self._hyperparams[key], \
                        tuner.best_params_[key]))
            self._hyperparams[key] = tuner.best_params_[key]
        log.debug('tune(%s): %s --> %s' % (self._hyperparams['scoring'],\
                    pre_tuning_score, tuner.best_score_))

    def predict(self, X):
        return self._model.predict(X)

    def predict_probability(self, X):
        return self._model.predict_proba(X)
