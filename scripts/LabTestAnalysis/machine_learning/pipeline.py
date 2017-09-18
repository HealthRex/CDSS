import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
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
	def __init__(self, X_train, y_train, X_validation, y_validation,
				X_test, y_test, output, name):

		self.EXPORT_FOLDER = 'pipelineResults/'

		self.X_train = X_train
		self.y_train = y_train
		self.X_validation = X_validation
		self.y_validation = y_validation
		self.X_test = X_test
		self.y_test = y_test

		print 'train_size', self.y_train.shape[0]
		print 'validation_size', self.y_validation.shape[0]
		print 'test_size', self.y_test.shape[0]

		self.output = output
		self.name = name

		classifiersDict = {
			'K Nearest Neighbors': KNeighborsClassifier(n_neighbors=3),

			'Linear SVM C=0.1': SVC(C=0.1, kernel='linear'),
			'Linear SVM C=1.0': SVC(C=1.0, kernel='linear'),
			'Linear SVM C=10.0': SVC(C=10.0, kernel='linear'),
			'Poly SVM C=0.1': SVC(C=0.1, kernel='poly'),
			'Poly SVM C=1.0': SVC(C=1.0, kernel='poly'),
			'Poly SVM C=10.0': SVC(C=10.0, kernel='poly'),
			'RBF SVM C=0.1': SVC(C=0.1),
			'RBF SVM C=1.0': SVC(C=1.0),
			'RBF SVM C=10.0': SVC(C=10.0),
			'Sigmoid SVM C=0.1': SVC(C=0.1, kernel='sigmoid'),
			'Sigmoid SVM C=1.0': SVC(C=1.0, kernel='sigmoid'),
			'Sigmoid SVM C=10.0': SVC(C=10.0, kernel='sigmoid'),

			'Decision Tree max_depth=5': DecisionTreeClassifier(max_depth=5),
			'Decision Tree max_depth=20': DecisionTreeClassifier(max_depth=20),
			'Decision Tree max_depth=50': DecisionTreeClassifier(max_depth=50),

			'Random Forest n_estimators=5, max_depth=5': RandomForestClassifier(n_estimators=5, max_depth=5),
			'Random Forest n_estimators=10, max_depth=5': RandomForestClassifier(n_estimators=10, max_depth=5),
			'Random Forest n_estimators=30, max_depth=5': RandomForestClassifier(n_estimators=30, max_depth=5),
			'Random Forest n_estimators=5, max_depth=10': RandomForestClassifier(n_estimators=5, max_depth=10),
			'Random Forest n_estimators=10, max_depth=10': RandomForestClassifier(n_estimators=10, max_depth=10),
			'Random Forest n_estimators=30, max_depth=10': RandomForestClassifier(n_estimators=30, max_depth=10),
			'Random Forest n_estimators=5, max_depth=15': RandomForestClassifier(n_estimators=5, max_depth=15),
			'Random Forest n_estimators=10, max_depth=15': RandomForestClassifier(n_estimators=10, max_depth=15),
			'Random Forest n_estimators=30, max_depth=15': RandomForestClassifier(n_estimators=30, max_depth=15),

			'Ada Boost n_estimators=10, learning_rate=0.01': AdaBoostClassifier(n_estimators=10, learning_rate=0.01),
			'Ada Boost n_estimators=50, learning_rate=0.01': AdaBoostClassifier(n_estimators=50, learning_rate=0.01),
			'Ada Boost n_estimators=100, learning_rate=0.01': AdaBoostClassifier(n_estimators=100, learning_rate=0.01),
			'Ada Boost n_estimators=10, learning_rate=0.1': AdaBoostClassifier(n_estimators=10, learning_rate=0.1),
			'Ada Boost n_estimators=50, learning_rate=0.1': AdaBoostClassifier(n_estimators=50, learning_rate=0.1),
			'Ada Boost n_estimators=100, learning_rate=0.1': AdaBoostClassifier(n_estimators=100, learning_rate=0.1),
			'Ada Boost n_estimators=10, learning_rate=1': AdaBoostClassifier(n_estimators=10, learning_rate=1),
			'Ada Boost n_estimators=50, learning_rate=1': AdaBoostClassifier(n_estimators=50, learning_rate=1),
			'Ada Boost n_estimators=100, learning_rate=1': AdaBoostClassifier(n_estimators=100, learning_rate=1),

			'Logistic Regression C=0.1': LogisticRegression(C=0.1),
			'Logistic Regression C=1.0': LogisticRegression(C=1.0),
			'Logistic Regression C=10.0': LogisticRegression(C=10.0),
			'Gaussian Naive Bayes': GaussianNB()
		}

		self.names = [
			# 'K Nearest Neighbors',

			# 'Linear SVM C=0.1',
			# 'Linear SVM C=1.0',
			# 'Linear SVM C=10.0',
			# 'Poly SVM C=0.1',
			# 'Poly SVM C=1.0',
			# 'Poly SVM C=10.0',
			# 'RBF SVM C=0.1',
			# 'RBF SVM C=1.0',
			# 'RBF SVM C=10.0',
			# 'Sigmoid SVM C=0.1',
			# 'Sigmoid SVM C=1.0',
			# 'Sigmoid SVM C=10.0',

			'Decision Tree max_depth=5',
			'Decision Tree max_depth=20',
			'Decision Tree max_depth=50',

			'Random Forest n_estimators=5, max_depth=5',
			'Random Forest n_estimators=10, max_depth=5',
			'Random Forest n_estimators=30, max_depth=5',
			'Random Forest n_estimators=5, max_depth=10',
			'Random Forest n_estimators=10, max_depth=10',
			'Random Forest n_estimators=30, max_depth=10',
			'Random Forest n_estimators=5, max_depth=15',
			'Random Forest n_estimators=10, max_depth=15',
			'Random Forest n_estimators=30, max_depth=15',

			'Ada Boost n_estimators=10, learning_rate=0.01',
			'Ada Boost n_estimators=50, learning_rate=0.01',
			'Ada Boost n_estimators=100, learning_rate=0.01',
			'Ada Boost n_estimators=10, learning_rate=0.1',
			'Ada Boost n_estimators=50, learning_rate=0.1',
			'Ada Boost n_estimators=100, learning_rate=0.1',
			'Ada Boost n_estimators=10, learning_rate=1',
			'Ada Boost n_estimators=50, learning_rate=1',
			'Ada Boost n_estimators=100, learning_rate=1',

			'Logistic Regression C=0.1',
			'Logistic Regression C=1.0',
			'Logistic Regression C=10.0',
			'Gaussian Naive Bayes'
		]
		self.classifiers = [classifiersDict[name] for name in self.names]

	def train(self):
		# iterate over classifiers
		print 'TRAIN'
		print('"name","train_accuracy","validation_accuracy",'
			'"validation_precision","validation_recall","validation_f1",'
			'"validation_roc-auc"')
		for name, clf in zip(self.names, self.classifiers):
			clf.fit(self.X_train, self.y_train)
			validation_predictions = clf.predict(self.X_validation)
			validation_prediction_probs = clf.predict_proba(self.X_validation)[:,1]

			train_score = clf.score(self.X_train, self.y_train)
			validation_score = clf.score(self.X_validation, self.y_validation)
			validation_precision = precision_score(self.y_validation, validation_predictions)
			validation_recall = recall_score(self.y_validation, validation_predictions)
			validation_f1 = f1_score(self.y_validation, validation_predictions)
			validation_roc_auc = roc_auc_score(self.y_validation, validation_prediction_probs)
			print '"%s","%0.3f","%0.3f","%0.3f","%0.3f","%0.3f","%0.3f"' % \
				(name, train_score, validation_score, validation_precision,
					validation_recall, validation_f1, validation_roc_auc)

	def test(self):
		# iterate over classifiers
		print 'TEST'
		print('"name","test_accuracy","test_precision","test_recall","test_f1",'
			'"test_roc-auc"')
		for i, (name, clf) in enumerate(zip(self.names, self.classifiers)):
			test_predictions = clf.predict(self.X_test)
			test_prediction_probs = clf.predict_proba(self.X_test)[:,1]

			test_score = clf.score(self.X_test, self.y_test)
			test_precision = precision_score(self.y_test, test_predictions)
			test_recall = recall_score(self.y_test, test_predictions)
			test_f1 = f1_score(self.y_test, test_predictions)
			test_roc_auc = roc_auc_score(self.y_test, test_prediction_probs)
			print '"%s","%0.3f","%0.3f","%0.3f","%0.3f","%0.3f"' % \
				(name, test_score, test_precision, test_recall, test_f1, test_roc_auc)

			prob_true, prob_pred = calibration_curve(self.y_test, test_prediction_probs, n_bins=20)
			fig = plt.figure(figsize=(6, 4))
			plt.plot(prob_pred, prob_true, 's-')
			plt.title(name)
			plt.savefig(self.EXPORT_FOLDER + self.name + '_' + name.lower().replace(' ', '_') + '.eps', format='eps')
			plt.close(fig)
			self.output['predictedTest.' + name.lower().replace(' ', '_')] = test_prediction_probs


if __name__ == '__main__':
	INPUT_FOLDER = 'processedFeatureMatrixData/processed_'

	# imp_method = 'zero'
	imp_method = 'median'

	for filepath in glob.glob(INPUT_FOLDER + imp_method + '*labFeatureMatrix*.csv'):
		print filepath

		df = pd.read_csv(filepath)

		X = df
		y = ((df['abnormal'] == 0) * 1).as_matrix()

		# preprocess dataset, split into training, validation and test part
		X_train, X_valid_test, y_train, y_valid_test = \
			train_test_split(X, y, test_size=0.3, random_state=42)
		X_validation, X_test, y_validation, y_test = \
			train_test_split(X_valid_test, y_valid_test, test_size=0.5, random_state=137)

		identifierCols = [
			'patient_id',
			'encounter_id',
			'order_proc_id',
			'proc_code',
			'order_time',
			'abnormal',
			'result_normal_count',
			'result_total_count',
			'all_result_normal']

		output = X_test.filter(items=identifierCols)

		X_train = X_train.drop(identifierCols, axis=1).as_matrix()
		X_validation = X_validation.drop(identifierCols, axis=1).as_matrix()
		X_test = X_test.drop(identifierCols, axis=1).as_matrix()

		scaler = StandardScaler()
		X_train = scaler.fit_transform(X_train)
		X_validation = scaler.transform(X_validation)
		X_test = scaler.transform(X_test)

		name = filepath.split('.')[-2]

		pipeline = ClassifierPipeline(X_train, y_train,
				X_validation, y_validation,
				X_test, y_test, output, name)
		pipeline.train()
		pipeline.test()
		pipeline.output.to_csv('pipelineResults/' + name + '_outputs.csv', index=False)
		print