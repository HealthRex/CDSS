#!/usr/bin/python
"""
Generic module for supervised machine learning classification.
"""

from sklearn.linear_model import LogisticRegressionCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, make_scorer
from sklearn.utils.validation import column_or_1d
from sklearn.model_selection import StratifiedKFold

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

    def __init__(self, classes, algorithm=None, random_state=None):
        self._classes = classes
        if algorithm is None:
            self._algorithm = SupervisedClassifier.LOGISTIC_REGRESSION
        elif algorithm not in SupervisedClassifier.SUPPORTED_ALGORITHMS:
            raise ValueError('Algorithm %s not supported.' % algorithm)
        else:
            self._algorithm = algorithm
        self._params = {}
        self._hyperparams = {}
        self._hyperparams['algorithm'] = algorithm
        self._hyperparams['random_state'] = random_state

    def __repr__(self):
        s = 'SupervisedClassifier(%s, algorithm=%s, random_state=%s)' % \
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

    def train(self, X, y, coef_max=None):
        self._features = X.columns

        y = self._maybe_reshape_y(y)

        if self._algorithm == SupervisedClassifier.DECISION_TREE:
            self._train_decision_tree(X, y)
        elif self._algorithm == SupervisedClassifier.LOGISTIC_REGRESSION:
            self._train_logistic_regression(X, y)
        elif self._algorithm == SupervisedClassifier.RANDOM_FOREST:
            self._train_random_forest(X, y)
        elif self._algorithm == SupervisedClassifier.REGRESS_AND_ROUND:
            self._train_regress_and_round(X, y, coef_max=coef_max)

    def _train_decision_tree(self, X, y):
        self._model = DecisionTreeClassifier()
        self._model.fit(X, y)

    def _train_logistic_regression(self, X, y):
        # Define hyperparameters.
        # Cs: Each C describes the inverse of regularization strength.
        # If Cs is as an int, then a grid of Cs values are chosen in a
        # logarithmic scale between 1e-4 and 1e4.
        # Smaller values = stronger regularization.
        self._hyperparams['Cs'] = 10
        # fit_intercept: Specifies if a constant (a.k.a. bias or intercept)
        # should be added to the decision function.
        self._hyperparams['fit_intercept'] = True
        # cv: generator for splitting training data into training and
        # validation data sets for cross validation.
        self._hyperparams['cv'] = self._build_cv_generator()
        # dual: Dual or primal formulation.
        # Prefer dual=False when n_samples > n_features.
        self._hyperparams['dual'] = False
        # penalty: norm used for penalization ('l1' or 'l2').
        # 'l1' more aggressively prunes features.
        self._hyperparams['penalty'] = 'l1'
        # scoring: scoring function used to evaluate hyperparameters during
        # cross-validation. Assume unbalanced classification problems, so
        # use roc auc.
        # http://scikit-learn.org/stable/modules/grid_search.html#specifying-an-objective-metric
        scorer = make_scorer(roc_auc_score, needs_threshold=True)
        self._hyperparams['scoring'] = scorer
        # solver: algorithm used for the optimization problem.
        # Only 'liblinear' and 'saga' handle L1 penalty.
        # 'liblinear' good for small datasets, 'saga' faster for large ones.
        self._hyperparams['solver'] = 'saga'
        # tol: tolerance for stopping criteria. Default: 0.0001
        self._hyperparams['tol'] = 0.0001
        # max_iter: Maximum number of iterations for the optimization problem.
        self._hyperparams['max_iter'] = 1000
        # class_weight: {class_1: 0.3, class_2: 0.7} tells scorer how to weight
        # classes in calculating error. Assume unbalanced classification, so
        # use parameter which automatically reweights inversely proportional
        # to class frequencies in X.
        self._hyperparams['class_weight'] = 'balanced'
        # n_jobs: num CPU cores used during CV (-1 = all cores)
        self._hyperparams['n_jobs'] = -1
        # refit: Use hyperparameters from best fold. If False, average
        # hyperparameters from all folds.
        self._hyperparams['refit'] = True
        # multi_class: If 'ovr', a binary problem is fit for each label.
        # Else minimizes is the multinomial loss fit across the entire
        # probability distribution.
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

    def _train_regress_and_round(self, X, y, coef_max=None):
        self._train_logistic_regression(X, y)

        if coef_max is None:
            # This is the optimal M value from Jung et al.
            # The choice here is completely arbitrary, but we need something.
            # https://arxiv.org/abs/1702.04690
            coef_max = 3

        # Based on Jung et al. https://arxiv.org/abs/1702.04690
        # w_j = round((M * beta_j) / (max_i|beta_i|))
        # coef_max = M = max rounded coefficient value
        # beta_max = max_i|beta_i| = largest unrounded regression coefficient
        beta_max = max([abs(c) for c in self._model.coef_[0]])
        self._model.coef_[0] = [round((coef_max * c) / (beta_max)) for c in self._model.coef_[0]]

    def predict(self, X):
        return self._model.predict(X)

    def predict_probability(self, X):
        return self._model.predict_proba(X)

    def compute_accuracy(self, X, y):
        return self._model.score(X, y)

    def compute_roc_auc(self, X, y):
        y_predicted = self.predict_probability(X)
        return roc_auc_score(y, y_predicted[:,1])
