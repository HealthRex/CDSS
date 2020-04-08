import time
from os import path

from . import customDBUtil
import numpy as np
import pandas as pd

from collections import defaultdict, deque
from io import StringIO
from datetime import datetime

# from medinfo.db.test.Const import RUNNER_VERBOSITY
# from medinfo.db.Util import log
from medinfo.db.test.Util import DBTestCase
# from medinfo.common.test.Util import MedInfoTestCase
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

BASE_NAME = 'base_name'
CLINICAL_ITEM_ID = 'clinical_item_id'
DATA_FOLDER = 'data_repeat_component_descriptive/'
NUMBER_SECONDS_IN_A_DAY = 86400


class RepeatComponents(object):

  def _getNonNullComponents(self):
    query = SQLQuery()
    # SELECT
    query.addSelect(BASE_NAME)
    # query.addSelect('max_result_flag')
    # FROM
    query.addFrom('order_result_stat')
    # WHERE
    query.addWhere('max_result_flag is not null')

    results = DBUtil.execute(query)

    pd.DataFrame(results, columns=query.select).to_csv(
        DATA_FOLDER + 'base_names.csv', index=False)

  def _getComponentItemIds(self):
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
    df['base_name'] = df['name'].str.replace(
        '\([a-z]*\)', '', case=False).str.strip()
    df.to_csv(DATA_FOLDER + 'result_ids.csv', index=False)

  def _getPatientsComponentsHistories(self, item_ids):
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

  @staticmethod
  def splitByPatient(results):
    currentSplit = [next(results)]
    for result in results:
      if result[0] != currentSplit[-1][0]:
        yield currentSplit
        currentSplit = []
      currentSplit.append(result)
    yield currentSplit

  @staticmethod
  def getDayDifference(current_result, first_result):
    return (current_result[2] - first_result[2]).total_seconds() / NUMBER_SECONDS_IN_A_DAY

  @staticmethod
  def isNormal(result_name):
    return 'InRange' in result_name

  @staticmethod
  def getStats(results, isNormalFn, max_consecutive=5, bins=[1, 2, 4, 7, 30, 90]):
    """Given a list/generator of lab/component results, returns a dictionary where the keys are (window_size, number of prior consecutive normal results) tuples, and the values are tuples (total number of occurrences, number of occurrences that are normal)
      - Inputs
        - Window Sizes / Bins: How far back to look for each lab test ordered for prior results
        - Maximum number of consecutive normals to assess
      - Outputs
        For each window size + consective normal count (0 up to max count)
        - Number of results in the sequence that occurred where preceded
          by the EXACT number of consecutive number of normal results within the window period
          (So if counting 2 prior consecutive normal results, even if see 3+ consecutive normal results,
          don't count that in this instance, since those can be counted in higher order instances)
        - Number of the results above that were themselves "normal"
        - Consecutive normal count of 0 means that there is no result within the window
        - Additional result for consecutive normal count is NULL,
          to count the total number of results and the total number of normal results
    """
    counts = [deque() for _ in range(len(bins))]
    # key: (days back, consecutive), value: (total, next_normal)
    stats = defaultdict(lambda: np.array([0, 0]))
    prior_histories = [[False] for _ in range(len(bins))]
    for result in results:
      for window_size, queue, prior_history in zip(bins, counts, prior_histories):
        # only keep whats relevant to the current result
        poppedQueue = False
        if queue:
          if queue[0][0] is not None:
            while queue and RepeatComponents.getDayDifference(result, queue[0]) > window_size:
              poppedQueue = True
              queue.popleft()
          else:
            prior_history[0] = bool(
                RepeatComponents.getDayDifference(result, queue[0]) <= window_size)
            queue.clear()

        # if the queue was filtered and is now empty, prior_history is false
        if poppedQueue and not queue:
          prior_history[0] = False

        if prior_history[0]:
          # if there is prior_history, set number_consecutive_normals as usual
          number_consecutive_normals = len(queue)
        else:
          # else set number_consecutive_normals as None
          number_consecutive_normals = None

        # increment total_count
        stats[(window_size, number_consecutive_normals)][0] += 1

        if isNormalFn(result[1]):
          # if normal, increment normal_count
          queue.append(result)
          stats[(window_size, number_consecutive_normals)][1] += 1
        else:
          # else clear the queue and add a sentinel value with the date of the
          # most recent result
          queue.clear()
          queue.append((None, None, result[2]))
        prior_history[0] = True
    # filter out windows that have more consecutive normal results than
    # max_consecutive

    # calculate a new None by summing everything else up with the same 0th index key
    # loop over keys and get the sum and create a new dict
    total_counts = defaultdict(lambda: np.array([0, 0]))
    for k, v in stats.items():
      total_counts[k[0]] += v
    for window_size in bins:
      # then set 1,0 to 1,None
      stats[(window_size, 0)] = stats[(window_size, None)]
      # set window_size,None to the sum of calculated above
      stats[(window_size, None)] = total_counts[window_size]

    return {k: v for k, v in stats.items() if k[1] is None or k[1] <= max_consecutive}

  @staticmethod
  def createGlobalStatsDf(global_stats):
    df_global_stats = pd.DataFrame()
    for base_name, d in dict(global_stats).items():
      to_df = []
      for k, v in d.items():
        to_df.append([base_name] + list(k) + list(v))
      df_global_stats = pd.concat(
          [df_global_stats, pd.DataFrame(to_df, dtype='object').fillna('NULL')])
    df_global_stats = df_global_stats.rename(columns={0: 'base_name',
                                                      1: 'window',
                                                      2: 'consecutive',
                                                      3: 'total',
                                                      4: 'normal'})

    return df_global_stats.sort_values(['base_name', 'window', 'consecutive'])

  def run(self, queryDB=False):
    if queryDB:
      self._getNonNullComponents()
    df_base_names = pd.read_csv(
        DATA_FOLDER + 'base_names.csv', dtype='string', na_filter=False)

    if queryDB:
      self._getComponentItemIds()
    df_result_ids = pd.read_csv(
        DATA_FOLDER + 'result_ids.csv', dtype='string', na_filter=False)

    df_result_ids = pd.merge(df_result_ids, df_base_names, on='base_name')

    times = []

    global_stats = defaultdict(lambda: defaultdict(lambda: np.array([0, 0])))
    for result_i, base_name in enumerate(df_result_ids['base_name'].drop_duplicates().tolist()):
      print(result_i, base_name)
      timer = time.time()
      item_ids = df_result_ids[df_result_ids['base_name'] == base_name][
          'clinical_item_id'].tolist()
      results = self._getPatientsComponentsHistories(item_ids)
      for patient_results in RepeatComponents.splitByPatient(results):
        for k, v in RepeatComponents.getStats(patient_results, RepeatComponents.isNormal).items():
          global_stats[base_name][k] += v
      times.append(time.time() - timer)

    RepeatComponents.createGlobalStatsDf(global_stats).to_csv(
        DATA_FOLDER + 'global_stats.csv', index=False)

    print([round(x, 2) for x in times])

if __name__ == '__main__':
  descriptive_stats = RepeatComponents()
  descriptive_stats.run(queryDB=True)
  # descriptive_stats.run()
