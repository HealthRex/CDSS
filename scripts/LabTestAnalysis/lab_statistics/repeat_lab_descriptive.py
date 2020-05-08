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
# from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME
from .repeat_component_descriptive import RepeatComponents

CLINICAL_ITEM_ID = 'clinical_item_id'
DATA_FOLDER = 'data_repeat_lab_descriptive/'


class RepeatLabs(object):

  def _getNonNullLabs(self):
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

    df = pd.DataFrame(results, columns=query.select).to_csv(
        DATA_FOLDER + 'proc_codes.csv', index=False)
    # df[df['proc_code'].str.startswith('LAB')].to_csv(DATA_FOLDER + 'proc_codes.csv', index=False)

  def _getPatientsLabsHistories(self, proc_codes):
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

  @staticmethod
  def isNormal(abnormal_yn):
    return abnormal_yn is None

  def run(self, queryDB=False, batch_size=10):
    if queryDB:
      self._getNonNullLabs()
    df_proc_codes = pd.read_csv(
        DATA_FOLDER + 'proc_codes.csv', dtype='string', na_filter=False)

    times = []

    global_stats = defaultdict(lambda: defaultdict(lambda: np.array([0, 0])))
    proc_codes = df_proc_codes['proc_code'].tolist()
    for batch_i in range(int(np.ceil(1.0*len(proc_codes) / batch_size))):
      print(batch_i, proc_codes[batch_i * batch_size])
      timer = time.time()
      batch = proc_codes[batch_i * batch_size:(batch_i + 1) * batch_size]
      results = self._getPatientsLabsHistories(batch)
      for patient_results in RepeatComponents.splitByPatient(results):
        proc_code = patient_results[0][3]
        for k, v in RepeatComponents.getStats(patient_results, RepeatLabs.isNormal).items():
          global_stats[proc_code][k] += v
      times.append(time.time() - timer)

    RepeatComponents.createGlobalStatsDf(global_stats).to_csv(
        DATA_FOLDER + 'global_stats.csv', index=False)

    print([round(x, 2) for x in times])

if __name__ == '__main__':
  descriptive_stats = RepeatLabs()
  descriptive_stats.run(queryDB=True, batch_size=100)
  # descriptive_stats.run(batch_size=100)
