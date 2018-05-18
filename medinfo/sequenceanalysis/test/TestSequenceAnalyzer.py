import datetime
import pandas as pd
import unittest
from collections import defaultdict

from scripts.LabTestAnalysis.lab_statistics.repeat_component_descriptive import RepeatComponents
from medinfo.sequenceanalysis.SequenceAnalyzer import SequenceAnalyzer

class TestSequenceAnalyzer(unittest.TestCase):

  def setUp(self):
    """Prepare state for test cases"""
    # Create temp (SQLite) database file to work with
    # self.conn = sqlite3.connect(TEMP_DATABASE_FILENAME);

    # Application instance to test on
    self.maxDiff = None

  def tearDown(self):
    """Restore state from any setUp or test steps"""
    # Close DB connection
    # self.conn.close()
    pass

  def testSequenceAnalyzerBulk(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    # expectedResults = defaultdict(int)
    # expectedResults[2] += 1
    # print(expectedResults)
    # actualResults = {2: 1}
    # print(actualResults)
    data = [
      [-11380099600907L, '11210R(InRange)', datetime.datetime(2012, 9, 10, 7, 25)],
      [-11380099600907L, '11210R(InRange)', datetime.datetime(2012, 9, 24, 9, 24)],
      [-10226028839621L, '11210R(Result)', datetime.datetime(2012, 3, 16, 14, 24)],
      [-10226028839621L, '11210R(InRange)', datetime.datetime(2012, 3, 24, 8, 2)],
      [-9834093246550L, '11210R(Result)', datetime.datetime(2013, 10, 1, 15, 24)],
      [-9834093246550L, '11210R(InRange)', datetime.datetime(2013, 10, 9, 7, 10)],
      [-8443896915633L, '11210R(InRange)', datetime.datetime(2013, 5, 1, 6, 55)],
      [-8443896915633L, '11210R(InRange)', datetime.datetime(2013, 5, 5, 8, 5)],
      [-5023114876861L, '11210R(InRange)', datetime.datetime(2011, 10, 16, 13, 37)],
      [-5023114876861L, '11210R(InRange)', datetime.datetime(2011, 10, 20, 15, 25)],
      [-4423981885898L, '11210R(InRange)', datetime.datetime(2012, 11, 17, 8, 11)],
      [-4423981885898L, '11210R(InRange)', datetime.datetime(2012, 11, 25, 9, 29)],
      [-3908850479087L, '11210R(InRange)', datetime.datetime(2010, 9, 9, 16, 43)],
      [-3908850479087L, '11210R(InRange)', datetime.datetime(2010, 9, 13, 15, 11)],
      [-1872296128547L, '11210R(Result)', datetime.datetime(2013, 12, 1, 21, 39)],
      [-1872296128547L, '11210R(InRange)', datetime.datetime(2013, 12, 10, 13, 34)],
      [-1378995679303L, '11210R(Result)', datetime.datetime(2010, 3, 9, 14, 17)],
      [-1378995679303L, '11210R(InRange)', datetime.datetime(2010, 3, 11, 9, 31)],
      [8662609401678L, '11210R(InRange)', datetime.datetime(2012, 7, 6, 12, 19)],
      [8662609401678L, '11210R(InRange)', datetime.datetime(2012, 7, 11, 8, 48)],
      [8848376950672L, '11210R(Result)', datetime.datetime(2013, 10, 30, 14, 56)],
      [8848376950672L, '11210R(InRange)', datetime.datetime(2013, 11, 6, 6, 50)],
      [9472424502184L, '11210R(InRange)', datetime.datetime(2011, 1, 13, 6, 55)],
      [9472424502184L, '11210R(InRange)', datetime.datetime(2013, 2, 2, 9, 40)],
      [9592401025493L, '11210R(Result)', datetime.datetime(2013, 1, 29, 1, 3)],
      [9592401025493L, '11210R(InRange)', datetime.datetime(2013, 2, 11, 9, 1)],
      [9924214318080L, '11210R(Result)', datetime.datetime(2012, 6, 8, 8, 32)],
      [9924214318080L, '11210R(InRange)', datetime.datetime(2012, 6, 16, 10, 20)],
      [11286739503688L, '11210R(InRange)', datetime.datetime(2011, 8, 10, 13, 56)],
      [11286739503688L, '11210R(High)', datetime.datetime(2011, 11, 19, 12, 23)],
      [-11380099600907L, '11211R(InRange)', datetime.datetime(2012, 9, 10, 7, 25)],
      [-11380099600907L, '11211R(InRange)', datetime.datetime(2012, 9, 24, 9, 24)],
      [-10226028839621L, '11211R(Result)', datetime.datetime(2012, 3, 16, 14, 24)],
      [-10226028839621L, '11211R(InRange)', datetime.datetime(2012, 3, 24, 8, 2)],
      [-9834093246550L, '11211R(Result)', datetime.datetime(2013, 10, 1, 15, 24)],
      [-9834093246550L, '11211R(InRange)', datetime.datetime(2013, 10, 9, 7, 10)],
      [-8443896915633L, '11211R(InRange)', datetime.datetime(2013, 5, 1, 6, 55)],
      [-8443896915633L, '11211R(InRange)', datetime.datetime(2013, 5, 5, 8, 5)],
      [-5023114876861L, '11211R(InRange)', datetime.datetime(2011, 10, 16, 13, 37)],
      [-5023114876861L, '11211R(InRange)', datetime.datetime(2011, 10, 20, 15, 25)],
      [-4423981885898L, '11211R(InRange)', datetime.datetime(2012, 11, 17, 8, 11)],
      [-4423981885898L, '11211R(InRange)', datetime.datetime(2012, 11, 25, 9, 29)],
      [-3908850479087L, '11211R(InRange)', datetime.datetime(2010, 9, 9, 16, 43)],
      [-3908850479087L, '11211R(InRange)', datetime.datetime(2010, 9, 13, 15, 11)],
      [-1872296128547L, '11211R(Result)', datetime.datetime(2013, 12, 1, 21, 39)],
      [-1872296128547L, '11211R(InRange)', datetime.datetime(2013, 12, 10, 13, 34)],
      [-1378995679303L, '11211R(Result)', datetime.datetime(2010, 3, 9, 14, 17)],
      [-1378995679303L, '11211R(InRange)', datetime.datetime(2010, 3, 11, 9, 31)],
      [8662609401678L, '11211R(InRange)', datetime.datetime(2012, 7, 6, 12, 19)],
      [8662609401678L, '11211R(InRange)', datetime.datetime(2012, 7, 11, 8, 48)],
      [8848376950672L, '11211R(Result)', datetime.datetime(2013, 10, 30, 14, 56)],
      [8848376950672L, '11211R(InRange)', datetime.datetime(2013, 11, 6, 6, 50)],
      [9472424502184L, '11211R(InRange)', datetime.datetime(2011, 1, 13, 6, 55)],
      [9472424502184L, '11211R(InRange)', datetime.datetime(2013, 2, 2, 9, 40)],
      [9592401025493L, '11211R(Result)', datetime.datetime(2013, 1, 29, 1, 3)],
      [9592401025493L, '11211R(InRange)', datetime.datetime(2013, 2, 11, 9, 1)],
      [9924214318080L, '11211R(Result)', datetime.datetime(2012, 6, 8, 8, 32)],
      [9924214318080L, '11211R(InRange)', datetime.datetime(2012, 6, 16, 10, 20)],
      [11286739503688L, '11211R(InRange)', datetime.datetime(2011, 8, 10, 13, 56)],
      [11286739503688L, '11211R(InRange)', datetime.datetime(2011, 11, 19, 12, 23)],
      [-11380099600907L, '11212R(InRange)', datetime.datetime(2012, 9, 10, 7, 25)],
      [-11380099600907L, '11212R(InRange)', datetime.datetime(2012, 9, 24, 9, 24)],
      [-10226028839621L, '11212R(Result)', datetime.datetime(2012, 3, 16, 14, 24)],
      [-10226028839621L, '11212R(InRange)', datetime.datetime(2012, 3, 24, 8, 2)],
      [-9834093246550L, '11212R(Result)', datetime.datetime(2013, 10, 1, 15, 24)],
      [-9834093246550L, '11212R(InRange)', datetime.datetime(2013, 10, 9, 7, 10)],
      [-8443896915633L, '11212R(InRange)', datetime.datetime(2013, 5, 1, 6, 55)],
      [-8443896915633L, '11212R(InRange)', datetime.datetime(2013, 5, 5, 8, 5)],
      [-5023114876861L, '11212R(InRange)', datetime.datetime(2011, 10, 16, 13, 37)],
      [-5023114876861L, '11212R(InRange)', datetime.datetime(2011, 10, 20, 15, 25)],
      [-4423981885898L, '11212R(InRange)', datetime.datetime(2012, 11, 17, 8, 11)],
      [-4423981885898L, '11212R(InRange)', datetime.datetime(2012, 11, 25, 9, 29)],
      [-3908850479087L, '11212R(InRange)', datetime.datetime(2010, 9, 9, 16, 43)],
      [-3908850479087L, '11212R(InRange)', datetime.datetime(2010, 9, 13, 15, 11)],
      [-1872296128547L, '11212R(Result)', datetime.datetime(2013, 12, 1, 21, 39)],
      [-1872296128547L, '11212R(InRange)', datetime.datetime(2013, 12, 10, 13, 34)],
      [-1378995679303L, '11212R(Result)', datetime.datetime(2010, 3, 9, 14, 17)],
      [-1378995679303L, '11212R(InRange)', datetime.datetime(2010, 3, 11, 9, 31)],
      [8662609401678L, '11212R(InRange)', datetime.datetime(2012, 7, 6, 12, 19)],
      [8662609401678L, '11212R(InRange)', datetime.datetime(2012, 7, 11, 8, 48)],
      [8848376950672L, '11212R(Result)', datetime.datetime(2013, 10, 30, 14, 56)],
      [8848376950672L, '11212R(InRange)', datetime.datetime(2013, 11, 6, 6, 50)],
      [9472424502184L, '11212R(High)', datetime.datetime(2011, 1, 13, 6, 55)],
      [9472424502184L, '11212R(High)', datetime.datetime(2013, 2, 2, 9, 40)],
      [9592401025493L, '11212R(Result)', datetime.datetime(2013, 1, 29, 1, 3)],
      [9592401025493L, '11212R(InRange)', datetime.datetime(2013, 2, 11, 9, 1)],
      [9924214318080L, '11212R(Result)', datetime.datetime(2012, 6, 8, 8, 32)],
      [9924214318080L, '11212R(InRange)', datetime.datetime(2012, 6, 16, 10, 20)],
      [11286739503688L, '11212R(InRange)', datetime.datetime(2011, 8, 10, 13, 56)],
      [11286739503688L, '11212R(InRange)', datetime.datetime(2011, 11, 19, 12, 23)],
      [-11380099600907L, '11213R(InRange)', datetime.datetime(2012, 9, 10, 7, 25)],
      [-11380099600907L, '11213R(InRange)', datetime.datetime(2012, 9, 24, 9, 24)],
      [-10226028839621L, '11213R(Result)', datetime.datetime(2012, 3, 16, 14, 24)],
      [-10226028839621L, '11213R(InRange)', datetime.datetime(2012, 3, 24, 8, 2)],
      [-9834093246550L, '11213R(Result)', datetime.datetime(2013, 10, 1, 15, 24)],
      [-9834093246550L, '11213R(InRange)', datetime.datetime(2013, 10, 9, 7, 10)],
      [-8443896915633L, '11213R(InRange)', datetime.datetime(2013, 5, 1, 6, 55)],
      [-8443896915633L, '11213R(InRange)', datetime.datetime(2013, 5, 5, 8, 5)],
      [-5023114876861L, '11213R(InRange)', datetime.datetime(2011, 10, 16, 13, 37)],
      [-5023114876861L, '11213R(InRange)', datetime.datetime(2011, 10, 20, 15, 25)],
      [-4423981885898L, '11213R(InRange)', datetime.datetime(2012, 11, 17, 8, 11)],
      [-4423981885898L, '11213R(InRange)', datetime.datetime(2012, 11, 25, 9, 29)],
      [-3908850479087L, '11213R(InRange)', datetime.datetime(2010, 9, 9, 16, 43)],
      [-3908850479087L, '11213R(InRange)', datetime.datetime(2010, 9, 13, 15, 11)],
      [-1872296128547L, '11213R(Result)', datetime.datetime(2013, 12, 1, 21, 39)],
      [-1872296128547L, '11213R(High)', datetime.datetime(2013, 12, 10, 13, 34)],
      [-1378995679303L, '11213R(Result)', datetime.datetime(2010, 3, 9, 14, 17)],
      [-1378995679303L, '11213R(InRange)', datetime.datetime(2010, 3, 11, 9, 31)],
      [8662609401678L, '11213R(InRange)', datetime.datetime(2012, 7, 6, 12, 19)],
      [8662609401678L, '11213R(InRange)', datetime.datetime(2012, 7, 11, 8, 48)],
      [8848376950672L, '11213R(Result)', datetime.datetime(2013, 10, 30, 14, 56)],
      [8848376950672L, '11213R(InRange)', datetime.datetime(2013, 11, 6, 6, 50)],
      [9472424502184L, '11213R(InRange)', datetime.datetime(2011, 1, 13, 6, 55)],
      [9472424502184L, '11213R(InRange)', datetime.datetime(2013, 2, 2, 9, 40)],
      [9592401025493L, '11213R(Result)', datetime.datetime(2013, 1, 29, 1, 3)],
      [9592401025493L, '11213R(InRange)', datetime.datetime(2013, 2, 11, 9, 1)],
      [9924214318080L, '11213R(Result)', datetime.datetime(2012, 6, 8, 8, 32)],
      [9924214318080L, '11213R(InRange)', datetime.datetime(2012, 6, 16, 10, 20)],
      [11286739503688L, '11213R(InRange)', datetime.datetime(2011, 8, 10, 13, 56)],
      [11286739503688L, '11213R(InRange)', datetime.datetime(2011, 11, 19, 12, 23)]]

    def handle_sentinel_queue_fn(window_size, queue, vars_dict, row):
      vars_dict['prior_history'] = bool(RepeatComponents.getDayDifference(row, queue[0]) <= window_size)

    def filter_queue_fn(window_size, queue, vars_dict, row):
      return RepeatComponents.getDayDifference(row, queue[0]) > window_size

    def emptied_queue_handler_fn(window_size, vars_dict, row):
      vars_dict['prior_history'] = False

    def set_number_consecutive_normals_fn(window_size, queue, vars_dict, row):
      return len(queue) if vars_dict['prior_history'] else None

    sequence_analyzer = SequenceAnalyzer()

    sequence_analyzer.split_data(lambda current_split, row: row[0] != current_split[-1][0])
    sequence_analyzer.initialize_vars({'prior_history': False})
    # sequence_analyzer.filter_row(filter_row_fn, use_vars)
    sequence_analyzer.handle_sentinel_queue(handle_sentinel_queue_fn)
    sequence_analyzer.filter_queue(filter_queue_fn, emptied_queue_handler_fn)

    #     filter_if_fn=filter_if_fn,
    #     filter_else_handler_fn=filter_else_handler_fn,
    #     filter_sentinel_fn=filter_sentinel_fn)

    sequence_analyzer.set_var('number_consecutive_normals', set_number_consecutive_normals_fn)

    # sequence_analyzer.filter_sentinel(filter_sentinel_fn, use_vars)
    # sequence_analyzer.add_row()
    # sequence_analyzer.select_window(select_window_fn, use_vars)
    # sequence_analyzer.compute_stats(compute_stats_fn, use_vars)
    # sequence_analyzer.clear_queue(clear_window_fn, use_vars)

    sequence_analyzer.build()

    sequence_analyzer.run(data, [1])
    # for window in sequence_analyzer.run(labTests):
    #     pass

    # actualResults = RepeatComponents.getStats(
    #     labTests, RepeatComponents.isNormal, bins=[1])
    expectedResults = {
      '11213R': {
        (90, None): [30, 22],
        (30, 1): [6, 6],
        (30, None): [30, 22],
        (7, None): [30, 22],
        (90, 1): [6, 6],
        (7, 1): [4, 4],
        (90, 0): [17, 10],
        (4, None): [30, 22],
        (30, 0): [17, 10],
        (1, None): [30, 22],
        (2, 0): [29, 21],
        (2, None): [30, 22],
        (7, 0): [24, 16],
        (1, 0): [30, 22],
        (4, 1): [1, 1],
        (4, 0): [28, 20]},
      '11210R': {
        (90, None): [30, 22],
        (30, 1): [6, 6],
        (30, None): [30, 22],
        (7, None): [30, 22],
        (90, 1): [6, 6],
        (7, 1): [4, 4],
        (90, 0): [17,  9],
        (4, None): [30, 22],
        (30, 0): [17,  9],
        (1, None): [30, 22],
        (2, 0): [29, 21],
        (2, None): [30, 22],
        (7, 0): [24, 16],
        (1, 0): [30, 22],
        (4, 1): [1, 1],
        (4, 0): [28, 20]},
      '11212R': {
        (90, None): [30, 21],
        (30, 1): [6, 6],
        (30, None): [30, 21],
        (7, None): [30, 21],
        (90, 1): [6, 6],
        (7, 1): [4, 4],
        (90, 0): [17,  8],
        (4, None): [30, 21],
        (30, 0): [17,  8],
        (1, None): [30, 21],
        (2, 0): [29, 20],
        (2, None): [30, 21],
        (7, 0): [24, 15],
        (1, 0): [30, 21],
        (4, 1): [1, 1],
        (4, 0): [28, 19]},
      '11211R': {
        (90, None): [30, 23],
        (30, 1): [6, 6],
        (30, None): [30, 23],
        (7, None): [30, 23],
        (90, 1): [6, 6],
        (7, 1): [4, 4],
        (90, 0): [17, 10],
        (4, None): [30, 23],
        (30, 0): [17, 10],
        (1, None): [30, 23],
        (2, 0): [29, 22],
        (2, None): [30, 23],
        (7, 0): [24, 17],
        (1, 0): [30, 23],
        (4, 1): [1, 1],
        (4, 0): [28, 21]}
      }
    # actualResults = {k: list(v) for k, v in actualResults.iteritems()}
    # self.assertEqual(expectedResults, actualResults)

def suite():
  """Returns the suite of tests to run for this test class / module.
  Use unittest.makeSuite methods which simply extracts all of the
  methods for the given class whose name starts with "test"
  """
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSequenceAnalyzer))
  return suite


if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())
