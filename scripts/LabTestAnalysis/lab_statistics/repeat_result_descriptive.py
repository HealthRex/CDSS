import time
from os import path

import customDBUtil
import numpy as np
import pandas as pd

from collections import defaultdict, deque
from cStringIO import StringIO
from datetime import datetime

# from medinfo.db.test.Const import RUNNER_VERBOSITY
# from medinfo.db.Util import log
from medinfo.db.test.Util import DBTestCase
# from medinfo.common.test.Util import MedInfoTestCase
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
# from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME

BASE_NAME = 'base_name'
CLINICAL_ITEM_ID = 'clinical_item_id'
DATA_FOLDER = 'data_repeat_result_descriptive/'


class RepeatResults(object):
	def __init__(self):
		self._max_consecutive = 5

	def _getNonNullResults(self):
		query = SQLQuery()
		# SELECT
		query.addSelect(BASE_NAME)
		# query.addSelect('max_result_flag')
		# FROM
		query.addFrom('order_result_stat')
		# WHERE
		query.addWhere('max_result_flag is not null')

		results = DBUtil.execute(query)

		pd.DataFrame(results, columns=query.select).to_csv(DATA_FOLDER + 'base_names.csv', index=False)

	def _getResultItemIds(self):
		query = SQLQuery()
		# SELECT
		query.addSelect(CLINICAL_ITEM_ID)
		query.addSelect('name')
		# FROM
		query.addFrom('clinical_item')
		# WHERE
		query.addWhere('clinical_item_category_id = 58')
		query.addOrderBy('name')

		results = DBUtil.execute(query)

		df = pd.DataFrame(results, columns=query.select)
		df['base_name'] = df['name'].str.replace('\([a-z]*\)', '', case=False).str.strip()
		df.to_csv(DATA_FOLDER + 'result_ids.csv', index=False)

	def _getPatientsResultsHistories(self, item_ids):
		query = SQLQuery()
		# SELECT
		query.addSelect('patient_id')
		query.addSelect('name')
		query.addSelect('item_date')
		# FROM
		query.addFrom('clinical_item as ci')
		query.addFrom('patient_item as pi')
		# WHERE
		query.addWhere('ci.clinical_item_id = pi.clinical_item_id')
		query.addWhereIn('ci.clinical_item_id', item_ids)

		query.addOrderBy('patient_id')
		query.addOrderBy('item_date')

		# print query
		# print query.getParams()
		return customDBUtil.execute(query)

	def _splitByPatient(self, results):
		currentSplit = [results.next()]
		for result in results:
			if result[0] != currentSplit[-1][0]:
				yield currentSplit
				currentSplit = []
			currentSplit.append(result)
		yield currentSplit


	def _isNormal(self,result_name):
		return 'InRange' in result_name
		# return 'InRange' in result_name or 'Result' in result_name

	def _consec(self, q):
		return min(self._max_consecutive, len(q)-1)

	def _getStats(self, results):
		bins = [1,2,4,7,30,90]
		counts = [deque() for _ in bins]
		# k = (days back, consecutive), val = (total, next_normal)
		stats = defaultdict(lambda: np.array([0,0]))
		for result in results:
			for size, queue in zip(bins, counts):
				# only keep whats relevant to the current result
				queue.append(result)
				while (queue[-1][2] - queue[0][2]).total_seconds()/86400 > size:
					queue.popleft()
				# increment total_count
				stats[(size, self._consec(queue))][0] += 1
				# if normal, increment normal_count
				if self._isNormal(result[1]):
					stats[(size, self._consec(queue))][1] += 1
				else:
					queue.clear()
		return {k:v for k, v in stats.iteritems()}

	def run(self, queryDB=False):
		if queryDB: self._getNonNullResults()
		df_base_names = pd.read_csv(DATA_FOLDER + 'base_names.csv', dtype='string', na_filter=False)

		if queryDB: self._getResultItemIds()
		df_result_ids = pd.read_csv(DATA_FOLDER + 'result_ids.csv', dtype='string', na_filter=False)

		df_result_ids = pd.merge(df_result_ids, df_base_names, on='base_name')

		times = []

		global_stats = defaultdict(lambda: defaultdict(lambda: np.array([0,0])))
		for result_i, base_name in enumerate(df_result_ids['base_name'].drop_duplicates().tolist()):
			print result_i, base_name
			timer = time.time()
			item_ids = df_result_ids[df_result_ids['base_name'] == base_name]['clinical_item_id'].tolist()
			results = self._getPatientsResultsHistories(item_ids)
			for patient_results in self._splitByPatient(results):
				for k, v in self._getStats(patient_results).iteritems():
					global_stats[base_name][k] += v
			times.append(time.time() - timer)

		df_global_stats = pd.DataFrame()
		for base_name, d in dict(global_stats).iteritems():
			to_df = []
			for k, v in d.iteritems():
				to_df.append([base_name] + list(k) + list(v))
			df_global_stats = pd.concat([df_global_stats, pd.DataFrame(to_df)])
		df_global_stats = df_global_stats.rename(columns={0:'base_name',
															1:'window',
															2:'consecutive',
															3:'total',
															4:'normal'})

		df_global_stats = df_global_stats.sort_values(['base_name','window','consecutive'])
		df_global_stats.to_csv(DATA_FOLDER + 'global_stats.csv', index=False)

		print map(lambda x:round(x,2), times)

if __name__ == '__main__':
	descriptive_stats = RepeatResults()
	# descriptive_stats.run(queryDB=True)
	descriptive_stats.run()
