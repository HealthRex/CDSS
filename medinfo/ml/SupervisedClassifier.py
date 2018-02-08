#!/usr/bin/python
"""
Generic module for supervised machine learning classification.
"""

import numpy as np
from sklearn.linear_model import LogisticRegressionCV
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

    SUPPORTED_ALGORITHMS = [DECISION_TREE, LOGISTIC_REGRESSION, RANDOM_FOREST, \
        REGRESS_AND_ROUND]

    EXHAUSTIVE_SEARCH = 'exhaustive-search'
    STOCHASTIC_SEARCH = 'stochastic-search'
    HYPEPARAM_STRATEGIES = [EXHAUSTIVE_SEARCH, STOCHASTIC_SEARCH]

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
        if self._hyperparams.get('cv_strategy') is None:
            self._hyperparams['cv_strategy'] = SupervisedClassifier.STOCHASTIC_SEARCH
        elif self._hyperparams['cv_strategy'] not in SupervisedClassifier.HYPERPARAM_STRATEGIES:
            raise ValueError('CV strategy %s not supported.' % self._hyperparams['hyperparam_strategy'])

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

    def _regression_params(self):
        parameters = {}
        coefs = self.coefs()
        columns = self._features
        feature_labels = columns.values
        for feature in feature_labels:
            weight = coefs[columns.get_loc(feature)]
            parameters.update({feature: weight})

        return parameters

    def params(self):
        if self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            return self._regression_params()
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            return self._regression_params()

    def _maybe_reshape_y(self, y):
        # If necessary, reshape y from (n_samples, 1) to (n_samples, )
        try:
            num_cols = y.shape[1]
            y = column_or_1d(y)
            log.info('Reshaped y to 1d.')
        except IndexError:
            log.info('Did not need to reshape y to 1d.')

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
        self._hyperparams['max_depth'] = [1, 2, 3, None]
        # Include 10 and .01 to bias towards simpler trees.
        self._hyperparams['min_samples_split'] = [2, 10, 0.01, 0.05]
        self._hyperparams['min_samples_leaf'] = [1, 10, 0.01, 0.05]
        self._hyperparams['min_weight_fraction_leaf'] = 0.0
        self._hyperparams['max_features'] = None
        self._hyperparams['max_leaf_nodes'] = None
        self._hyperparams['min_impurity_decrease'] = None
        self._hyperparams['class_weight'] = 'balanced'
        self._hyperparams['presort'] = None
        # Assume unbalanced classification problems, so use f1_score.
        # Cannot compute an ROC curve because decision trees have no ROC.
        # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
        scorer = make_scorer(f1_score)
        self._hyperparams['scoring'] = scorer

        # Initialize model with naive hyperparameter values.
        self._model = DecisionTreeClassifier(\
            criterion=self._hyperparams['criterion'], \
            splitter=self._hyperparams['splitter'], \
            max_depth=self._hyperparams['max_depth'][0], \
            min_samples_split=self._hyperparams['min_samples_split'][0], \
            min_samples_leaf=self._hyperparams['min_samples_leaf'][0], \
            min_weight_fraction_leaf=self._hyperparams['min_weight_fraction_leaf'][0], \
            max_features=self._hyperparams['max_features'], \
            random_state=self._hyperparams['random_state'], \
            max_leaf_nodes=self._hyperparams['max_leaf_nodes'], \
            min_impurity_decrease=self._hyperparams['min_impurity_decrease'], \
            class_weight=self._hyperparams['class_weight'], \
            presort=self._hyperparams['presort']
        )

        # Search hyperparameter space for better values.
        hyperparam_search_space = {
            'max_depth': [1, 2, 3, None],
            'min_samples_split': [2, 10, 0.01, 0.05],
            'min_samples_leaf': [1, 10, 0.01, 0.05]
        }
        self._tune_hyperparams(hyperparam_search_space)

        self._model.fit(X, y)

    def _train_logistic_regression(self, X, y):
        # Define hyperparameter space.
        # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegressionCV.html
        self._hyperparams['Cs'] = 10
        self._hyperparams['hyperparam_strategy'] = SupervisedClassifier.EXHAUSTIVE_SEARCH
        self._hyperparams['fit_intercept'] = True
        self._hyperparams['cv'] = self._build_cv_generator()
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
        self._hyperparams['refit'] = True
        self._hyperparams['multi_class'] = 'ovr'

        # Build model.
        self._model = LogisticRegressionCV(\
            Cs=self._hyperparams['Cs'], \
            fit_intercept=self._hyperparams['fit_intercept'], \
            cv=self._hyperparams['cv'], \
            dual=self._hyperparams['dual'], \
            penalty=self._hyperparams['penalty'], \
            scoring=self._hyperparams['scoring'], \
            solver=self._hyperparams['solver'], \
            tol=self._hyperparams['tol'], \
            max_iter=self._hyperparams['max_iter'], \
            class_weight=self._hyperparams['class_weight'], \
            n_jobs=self._hyperparams['n_jobs'], \
            refit=self._hyperparams['refit'], \
            multi_class=self._hyperparams['multi_class'], \
            random_state=self._hyperparams['random_state']
        )
        self._model.fit(X, y)

    def _train_random_forest(self, X, y):
        self._model = RandomForestClassifier()
        self._model.fit(X, y)

    def _train_regress_and_round(self, X, y):
        log.info('Rounding logistic regression coefficients...')
        self._train_logistic_regression(X, y)
        self._tune_hyperparams_regress_and_round(X, y)

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
        log.debug('unrounded_coefs: %s' % self.coefs())
        self._model.coef_[0] = [round((coef_max * c) / (beta_max)) for c in self._model.coef_[0]]
        log.debug('rounded_coefs(M=%s): %s' % (coef_max, self.coefs()))

    def _tune_coef_max(self, X, y):
        # The only way to easily compute scores is to modify the model itself.
        # Keep the unrounded coefs so it's always possible to go back.
        unrounded_coefs = self.coefs().copy()

        # The optimal M value from Jung et al. is 3.
        # https://arxiv.org/abs/1702.04690
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
            log.debug('roc_auc(M=%s) = %s' % (M_grid[i], mean_score))

            # Conditionally change coef_max and max_roc_auc.
            if mean_score > max_roc_auc:
                coef_max = M_grid[i]
                max_roc_auc = mean_score
            if mean_score < min_roc_auc:
                min_roc_auc = mean_score

            # Reset coefs and return.
            self._model.coef_[0] = unrounded_coefs

        log.info('RANGE(roc_auc | M) = [%s, %s]' % (min_roc_auc, max_roc_auc))

        return coef_max

    def _tune_hyperparams(self, hyperparam_space):
        # Don't use sklearn utilities for REGRESS_AND_ROUND.
        if self._hyperparams['algorithm'] == SupervisedClassifier.REGRESS_AND_ROUND:
            self._tune_hyperparams_regress_and_round()
        else:
            if self._hyperparams['hyperparam_strategy'] == SupervisedClassifier.EXHAUSTIVE_SEARCH:
                self._tune_hyperparams_exhaustively(hyperparam_space)
            elif self._hyperparams['hyperparam_strategy'] == SupervisedClassifier.STOCHASTIC_SEARCH:
                self._tune_hyperparams_stochastically(hyperparam_space)

    def _tune_hyperparams_exhaustively(self, hyperparam_space):
        # grid search
        pass

    def _tune_hyperparams_stochastically(self):
        # random search

        pass

    def predict(self, X):
        return self._model.predict(X)

    def predict_probability(self, X):
        return self._model.predict_proba(X)
