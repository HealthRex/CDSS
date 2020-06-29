'''
Look for all base_names in order_result_stat that have a non-null max_result_flag (indicates lab results where we have labels to distinguish normal from abnormal).
Use the LabResultMap to trace back all of the lab orders where we can expect to find normal vs. abnormal lab results

We'll then go back to the full data (e.g., patient_item) and find every instance of one of those lab results (normal or abnormal).
Go back in time to the respective lab order that generated that lab result
Collect the clinical information up to that point in time (e.g., presence vs. absence of certain orders, diagnosis codes, prior lab results, time in hospital, treatment team patient is on, number of orders and abnormal lab results previously, etc.)
Feed those in to a handful of machine learning algorithms to predict whether the subsequent lab result will be normal or not (e.g., multi-var logistic regression with L1 or L2 regularization, random forest, Naive Bayes, AdaBoost or any other ones you can easily run with scikit or other framework).
On a separate (preferably future) validation set of patient cases, use the above predictive models to predict whether a lab order will generate all normal results.
See at what threshold you can get extremely high (99%?) positive predictive value for predicting normal results. That indicates a subset of cases (hopefully a lot) where we could largely eliminate the need for the lab test and then translate that into dollars saved through the charges
Go back to the models that generated those predictions, and pull out the features that were predictive of normal results so that you can also report an interpretable model of when lab orders are likely to be a waste of time.
'''
import csv
import numpy as np
import pandas as pd

from io import StringIO
# from datetime import datetime

# from medinfo.db.test.Const import RUNNER_VERBOSITY
# from medinfo.db.Util import log
from medinfo.db.test.Util import DBTestCase
# from medinfo.common.test.Util import MedInfoTestCase
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

BASE_NAME = 'base_name'
CLINICAL_ITEM_ID = 'clinical_item_id'


class ClinicalData(object):
	def _getNonNullBaseNames(self):
		query = SQLQuery()
		# SELECT
		query.addSelect(BASE_NAME)
		query.addSelect('max_result_flag')
		# FROM
		query.addFrom('order_result_stat')
		# WHERE
		query.addWhere('max_result_flag is not null')

		print(query)
		print(query.getParams())
		DBUtil.runDBScript(self.SCRIPT_FILE, False)
		results = DBUtil.execute(str(query), query.getParams())

		pd.DataFrame(results, columns=query.select).to_csv('base_names.csv', index=False)

	def _getClinicalItems(self):
		query = SQLQuery()
		# SELECT
		query.addSelect(CLINICAL_ITEM_ID)
		query.addSelect('name')
		# FROM
		query.addFrom('clinical_item')

		print(query)
		print(query.getParams())
		DBUtil.runDBScript(self.SCRIPT_FILE, False)
		results = DBUtil.execute(str(query), query.getParams())

		pd.DataFrame(results, columns=query.select).to_csv('clinical_items.csv', index=False)

	def getClinicalData(self, queryDB=False):
		# Create SCRIPT_FILE
		self.SCRIPT_FILE = StringIO()
		self.SCRIPT_FILE.write('psql medinfo Shivaal')

		if queryDB: self._getNonNullBaseNames()
		df_base_names = pd.read_csv('base_names.csv')

		df_lab_result_map = pd.read_csv('LabResultMap.csv')

		df_lab_orders = pd.merge(df_lab_result_map, df_base_names, on=BASE_NAME)\
							.drop(['base_name'], axis=1)\
							.rename(columns={'proc_code': 'name'})

		if queryDB: self._getClinicalItems()
		df_clinical_items = pd.read_csv('clinical_items.csv')

		df_lab_orders = pd.merge(df_lab_orders, df_clinical_items, on='name')
		df_lab_orders = df_lab_orders[['name', 'description', 'clinical_item_id']]\
							.drop_duplicates()


		print(df_lab_orders.head())


if __name__ == '__main__':
	data = ClinicalData()
	# data.getClinicalData(queryDB=True)
	data.getClinicalData()
