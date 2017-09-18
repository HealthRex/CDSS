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

CLINICAL_ITEM_ID = 'clinical_item_id'
DATA_FOLDER = 'data_repeat_lab_descriptive/'


class RepeatResults(object):
	def __init__(self):
		self._max_consecutive = 5

	def _getNonNullResults(self):
		query = SQLQuery()
		# SELECT
		query.addSelect('proc_code')
		# FROM
		query.addFrom('stride_order_proc')
		# WHERE
		query.addWhereLike('proc_code', 'LAB%')
		query.addWhere('abnormal_yn is not null')

		query.addGroupBy('proc_code')
		query.addOrderBy('proc_code')

		results = DBUtil.execute(query)

		df = pd.DataFrame(results, columns=query.select).to_csv(DATA_FOLDER + 'proc_codes.csv', index=False)
		# df[df['proc_code'].str.startswith('LAB')].to_csv(DATA_FOLDER + 'proc_codes.csv', index=False)

	def _getPatientsResultsHistories(self, proc_codes):
		query = SQLQuery()
		# SELECT
		query.addSelect('pat_id')
		query.addSelect('abnormal_yn')
		query.addSelect('result_time')
		query.addSelect('proc_code')
		# FROM
		query.addFrom('stride_order_proc')
		# query.addFrom('patient_item as pi')
		# WHERE
		query.addWhereEqual('lab_status', 'Final result')
		# query.addWhereEqual('proc_code', proc_code)
		query.addWhereIn('proc_code', proc_codes)

		query.addOrderBy('proc_code')
		query.addOrderBy('pat_id')
		query.addOrderBy('result_time')

		return customDBUtil.execute(query)

	def _splitByPatient(self, results):
		currentSplit = [results.next()]
		for result in results:
			if result[0] != currentSplit[-1][0]:
				yield currentSplit
				currentSplit = []
			currentSplit.append(result)
		yield currentSplit

	def _isNormal(self, abnormal_yn):
		return abnormal_yn is None

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

	def run(self, queryDB=False, batch_size=10):
		if queryDB: self._getNonNullResults()
		df_proc_codes = pd.read_csv(DATA_FOLDER + 'proc_codes.csv', dtype='string', na_filter=False)

		times = []

		global_stats = defaultdict(lambda: defaultdict(lambda: np.array([0,0])))
		proc_codes = df_proc_codes['proc_code'].tolist()
		for batch_i in xrange(len(proc_codes) / batch_size + 1):
			print batch_i, proc_codes[batch_i]
			timer = time.time()
			batch = proc_codes[batch_i*batch_size:(batch_i+1)*batch_size]
			results = self._getPatientsResultsHistories(batch)
			for patient_results in self._splitByPatient(results):
				proc_code = patient_results[0][3]
				for k, v in self._getStats(patient_results).iteritems():
					global_stats[proc_code][k] += v
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
	descriptive_stats.run(batch_size=100)
