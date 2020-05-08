import itertools
import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.calibration import calibration_curve

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
# look into xgboost
from sklearn.naive_bayes import GaussianNB

'''
go to http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html for reference
'''


class ClassifierPipeline(object):
	def __init__(self, X_train, y_train, X_validation, y_validation, X_test, y_test, data_name, base_output_folder, output_folder):
		self.X_train = X_train
		self.y_train = y_train
		self.X_validation = X_validation
		self.y_validation = y_validation
		self.X_test = X_test
		self.y_test = y_test

		self.data_name = data_name

		self.BASE_OUTPUT_FOLDER = base_output_folder
		self.OUTPUT_FOLDER = output_folder

		self.outputs = {}

		print('train_size', self.y_train.shape[0])
		print('validation_size', self.y_validation.shape[0])
		print('test_size', self.y_test.shape[0])

	def set_classifiers(self, knn=None, naive_bayes=False, logistic_regression=None, svm=None, decision_tree=None, random_forest=None, ada_boost=None, additional_classifiers=None):
		'''Takes in parameters for each classifier and adds the classifier to the self.classifiers list
		Args:
			knn: [:int] (list of ints) for n_neighbors
			naive_bayes: boolean
			logistic_regression: [:float] for C values
			svm: 2D list - svm[0] is a [:string] specifying kernels (linear, rbf, poly, sigmoid), and svm[1] is a [:float] specifying C values
			decision_tree: [:int] for max_depth
			random_forest: 2D list - random_forest[0] is a [:int] for n_estimators, and random_forest[1] is a [:int] for max_depth
			ada_boost: 2D list - ada_boost[0] is a [:int] for n_estimators, and ada_boost[1] is a [:float] for learning_rate
			additional_classifiers: list of tuples - each tuple is of the form (name, classifier_instance)

		'''
		self.classifier_names = []
		self.classifiers = []
		if knn is not None:
			self.classifier_names.extend(['K Nearest Neighbors n_neighbors={}'.format(hp) for hp in knn])
			self.classifiers.extend([KNeighborsClassifier(n_neighbors=hp) for hp in knn])

		if naive_bayes:
			self.classifier_names.append('Gaussian Naive Bayes')
			self.classifiers.append(GaussianNB())

		if logistic_regression is not None:
			self.classifier_names.extend(['Logistic Regression C={:.1f}'.format(hp) for hp in logistic_regression])
			self.classifiers.extend([LogisticRegression(C=hp) for hp in logistic_regression])

		if svm is not None:
			self.classifier_names.extend(['SVM kernel={}, C={:.1f}'.format(*hp) for hp in itertools.product(*svm)])
			self.classifiers.extend([SVC(kernel=hp[0], C=hp[1]) for hp in itertools.product(*svm)])

		if decision_tree is not None:
			self.classifier_names.extend(['Decision Tree max_depth={}'.format(hp) for hp in decision_tree])
			self.classifiers.extend([DecisionTreeClassifier(max_depth=hp) for hp in decision_tree])

		if random_forest is not None:
			self.classifier_names.extend(['Random Forest n_estimators={}, max_depth={}'.format(*hp) for hp in itertools.product(*random_forest)])
			self.classifiers.extend([RandomForestClassifier(n_estimators=hp[0], max_depth=hp[1]) for hp in itertools.product(*random_forest)])

		if ada_boost is not None:
			self.classifier_names.extend(['Ada Boost n_estimators={}, learning_rate={:.1f}'.format(*hp) for hp in itertools.product(*ada_boost)])
			self.classifiers.extend([AdaBoostClassifier(n_estimators=hp[0], learning_rate=hp[1]) for hp in itertools.product(*ada_boost)])

		if additional_classifiers is not None:
			for name, classifier in additional_classifiers:
				self.classifier_names.append(name)
				self.classifiers.append(classifier)

	def train(self, log_to_stdout=True, log_to_csv=False):
		log = ['"classifier_name","train_accuracy","validation_accuracy","validation_precision","validation_recall","validation_f1","validation_roc-auc"']
		print('TRAIN')
		if log_to_stdout: print(log[-1])
		for classifier_name, classifier in zip(self.classifier_names, self.classifiers):
			classifier.fit(self.X_train, self.y_train)
			validation_predictions = classifier.predict(self.X_validation)
			validation_prediction_probs = classifier.predict_proba(self.X_validation)[:,1]

			train_score = classifier.score(self.X_train, self.y_train)
			validation_score = classifier.score(self.X_validation, self.y_validation)
			validation_precision = precision_score(self.y_validation, validation_predictions)
			validation_recall = recall_score(self.y_validation, validation_predictions)
			validation_f1 = f1_score(self.y_validation, validation_predictions)
			validation_roc_auc = roc_auc_score(self.y_validation, validation_prediction_probs)
			log.append('"%s","%0.3f","%0.3f","%0.3f","%0.3f","%0.3f","%0.3f"' %
				(classifier_name, train_score, validation_score, validation_precision,
					validation_recall, validation_f1, validation_roc_auc))
			if log_to_stdout: print(log[-1])

		if log_to_csv:
			if not os.path.exists('/'.join([self.BASE_OUTPUT_FOLDER, self.OUTPUT_FOLDER])):
				os.makedirs('/'.join([self.BASE_OUTPUT_FOLDER, self.OUTPUT_FOLDER]))
			with open('/'.join([self.BASE_OUTPUT_FOLDER, self.OUTPUT_FOLDER, self.data_name + '_log_train.csv']), 'w') as file:
				for line in log:
					print(line, file=file)

	def test(self, log_to_stdout=True, output_matrix=None):
		log = ['"classifier_name","test_accuracy","test_precision","test_recall","test_f1","test_roc-auc"']
		print('TEST')
		if log_to_stdout: print(log[-1])
		for i, (classifier_name, classifier) in enumerate(zip(self.classifier_names, self.classifiers)):
			test_predictions = classifier.predict(self.X_test)
			test_prediction_probs = classifier.predict_proba(self.X_test)[:,1]

			test_score = classifier.score(self.X_test, self.y_test)
			test_precision = precision_score(self.y_test, test_predictions)
			test_recall = recall_score(self.y_test, test_predictions)
			test_f1 = f1_score(self.y_test, test_predictions)
			test_roc_auc = roc_auc_score(self.y_test, test_prediction_probs)
			log.append('"%s","%0.3f","%0.3f","%0.3f","%0.3f","%0.3f"' %
				(classifier_name, test_score, test_precision, test_recall, test_f1, test_roc_auc))
			if log_to_stdout: print(log[-1])

			self.outputs[self._get_column_name(classifier_name)] = test_prediction_probs
			if output_matrix is not None:
				output_matrix[self._get_column_name(classifier_name)] = test_prediction_probs

		if output_matrix is not None:
			if not os.path.exists('/'.join([self.BASE_OUTPUT_FOLDER, self.OUTPUT_FOLDER])):
				os.makedirs('/'.join([self.BASE_OUTPUT_FOLDER, self.OUTPUT_FOLDER]))
			output_matrix.to_csv('/'.join([self.BASE_OUTPUT_FOLDER, self.OUTPUT_FOLDER, self.data_name + '_outputs.csv']), index=False)

	def plot(self):
		for i, classifier_name in enumerate(self.classifier_names):
			test_prediction_probs = self.outputs[self._get_column_name(classifier_name)]
			prob_true, prob_pred = calibration_curve(self.y_test, test_prediction_probs, n_bins=20)
			fig = plt.figure(figsize=(6, 4))
			plt.plot(prob_pred, prob_true, 's-')
			plt.title(classifier_name)
			plt.savefig('/'.join([self.BASE_EXPORT_FOLDER, self.data_name + '_' + classifier_name.lower().replace(' ', '_') + '.eps']), format='eps')
			plt.close(fig)

	@staticmethod
	def _get_column_name(classifier_name):
		return 'predicted.' + classifier_name.lower().replace(' ', '_')
