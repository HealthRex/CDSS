# TODO sum all with > 1
import csv
import numpy as np
import pandas as pd

from cStringIO import StringIO
from datetime import datetime

from medinfo.db.test.Const import RUNNER_VERBOSITY
from medinfo.db.Util import log
from medinfo.db.test.Util import DBTestCase
from medinfo.common.test.Util import MedInfoTestCase
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

import os

CLINICAL_ITEM_ID = 'clinical_item_id'
ITEM_COUNTS = 'item_counts'
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

class LabStats(object):
	def _getClinicalItemCounts(self):
		query = SQLQuery()
		# SELECT
		query.addSelect(CLINICAL_ITEM_ID)
		query.addSelect('COUNT(' + CLINICAL_ITEM_ID + ') as total')
		# FROM
		query.addFrom('patient_item')
		# OTHER
		query.addGroupBy(CLINICAL_ITEM_ID)
		query.addOrderBy('total', dir='desc')

		print query
		print query.getParams()
		DBUtil.runDBScript(self.SCRIPT_FILE, False)
		results = DBUtil.execute(str(query), query.getParams())

		pd.DataFrame(results, columns=[CLINICAL_ITEM_ID, 'count']).to_csv('data_summary_stats/item_counts.csv', index=False)


	def _getLabs(self):
		query = SQLQuery()
		# SELECT
		query.addSelect(CLINICAL_ITEM_ID)
		query.addSelect('name')
		query.addSelect('description')
		# FROM
		query.addFrom('clinical_item')
		# WHERE
		query.addWhereLike('name','LAB%')
		# OTHER
		query.addOrderBy(CLINICAL_ITEM_ID, dir='asc')

		print query
		print query.getParams()
		DBUtil.runDBScript(self.SCRIPT_FILE, False)
		results = DBUtil.execute(str(query), query.getParams())

		pd.DataFrame(results, columns=query.select).to_csv('data_summary_stats/labs.csv', index=False)


	def run(self, queryDB=False, toCSV=False):
		# Create SCRIPT_FILE
		self.SCRIPT_FILE = StringIO()
		self.SCRIPT_FILE.write('psql medinfo Shivaal')

		# Get counts of items from patient_item
		if queryDB: self._getClinicalItemCounts()
		df_item_counts = pd.read_csv(THIS_DIR + '/data_summary_stats/item_counts.csv')

		# Get labs
		if queryDB: self._getLabs()
		df_labs = pd.read_csv(THIS_DIR + '/data_summary_stats/labs.csv')

		# Join labs with counts
		df_labs = pd.merge(df_labs, df_item_counts, on=CLINICAL_ITEM_ID)

		# Get billing codes
		df_billing_codes = pd.DataFrame(pd.read_csv(THIS_DIR + '/data_summary_stats/billing_codes.csv', dtype='string'))
		df_billing_codes = df_billing_codes[['name', 'order_code_description', 'billing_code']]
		df_billing_codes['name'] = df_billing_codes['name'].apply(lambda x: 'LAB' + str(x))

		# Get prices
		df_chargemaster = pd.DataFrame(pd.read_csv(THIS_DIR + '/data_summary_stats/chargemaster.csv', dtype='string'))
		df_chargemaster = df_chargemaster[['billing_code', 'price', 'price_description']]
		df_chargemaster['price'] = df_chargemaster['price'].apply(lambda x: float(x.replace(',','')))

		# Join billing codes and prices
		df_prices = pd.merge(df_billing_codes, df_chargemaster, on='billing_code')

		# some billing codes have the exact same description and price, so we remove these here
		df_prices = df_prices.drop(['billing_code'], axis=1)
		df_prices = df_prices.drop_duplicates()

		# Join labs with prices
		df_labs = pd.merge(df_labs, df_prices, on='name')

		# Sum prices for labs with "PANEL" in the description
		df_panels = pd.DataFrame(df_labs[df_labs['description'].str.contains('PANEL')])
		df_panels = df_panels[[CLINICAL_ITEM_ID, 'price']]
		df_panels['sum_price'] = df_panels.groupby(by=CLINICAL_ITEM_ID)['price'].transform(np.sum)
		df_panels = df_panels.drop('price', axis=1)
		df_labs = pd.merge(df_labs, df_panels, how='left', on=CLINICAL_ITEM_ID)
		df_labs['price'] = df_labs['sum_price'].fillna(df_labs['price'])
		df_labs = df_labs.drop(['sum_price', 'price_description'], axis=1)
		df_labs = df_labs.drop_duplicates()

		# calculate aggregate statistics for the same name and order_code_description
		df_labs_groupby = df_labs.groupby(['name', 'order_code_description'])['price']
		df_labs['min_price'] = df_labs_groupby.transform(np.min)
		df_labs['max_price'] = df_labs_groupby.transform(np.max)
		df_labs['mean_price'] = df_labs_groupby.transform(np.mean)
		df_labs['median_price'] = df_labs_groupby.transform(np.median)
		df_labs = df_labs.drop('price', axis=1)
		df_labs = df_labs.drop_duplicates()

		# # calculate volume charges
		df_labs['min_volume_charge'] = df_labs['min_price'] * df_labs['count']
		df_labs['max_volume_charge'] = df_labs['max_price'] * df_labs['count']
		df_labs['mean_volume_charge'] = df_labs['mean_price'] * df_labs['count']
		df_labs['median_volume_charge'] = df_labs['median_price'] * df_labs['count']

		if toCSV: df_labs.to_csv('data_summary_stats/labs_charges_volumes.csv', index=False)
		return {int(x[0]): tuple(x[1:]) for x in df_labs.values}


if __name__ == '__main__':
	labs = LabStats()
	# labs.run(queryDB=True, toCSV=True)
	# labs.run(toCSV=True)
	labs.run()
