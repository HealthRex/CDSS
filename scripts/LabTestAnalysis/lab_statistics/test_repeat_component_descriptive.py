import pandas as pd
import unittest

# import sys, os
# from cStringIO import StringIO
from datetime import datetime

from repeat_component_descriptive import RepeatComponents


class TestRepeatComponents(unittest.TestCase):

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

  def testWindowSize1Day(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    labTests = [
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 1)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 2)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 3)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 4)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 5)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 6)],

        ['6385739673941', '12078R(High)',       datetime(2000, 1, 8)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 9)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 10)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 11)]]
    actualResults = RepeatComponents.getStats(
        labTests, RepeatComponents.isNormal, bins=[1])
    expectedResults = {
        (1, None): [2, 1],
        (1, 0): [5, 3],
        (1, 1): [3, 1]
    }
    actualResults = {k: list(v) for k, v in actualResults.iteritems()}
    self.assertEqual(expectedResults, actualResults)

  def testWindowSize30Day(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    labTests = [
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 1)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 2)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 3)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 4)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 5)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 6)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 8)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 9)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 10)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 11)]]
    actualResults = RepeatComponents.getStats(
        labTests, RepeatComponents.isNormal, bins=[30])
    expectedResults = {
        (30, None): [1, 0],
        (30, 0): [5, 3],
        (30, 1): [2, 1],
        (30, 2): [1, 1],
        (30, 3): [1, 0]
    }
    actualResults = {k: list(v) for k, v in actualResults.iteritems()}
    self.assertEqual(expectedResults, actualResults)

  def testWindowSizes1And30Day(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    labTests = [
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 1)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 2)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 3)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 4)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 5)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 6)],

        ['6385739673941', '12078R(High)',       datetime(2000, 1, 8)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 9)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 10)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 11)]]
    actualResults = RepeatComponents.getStats(
        labTests, RepeatComponents.isNormal, bins=[1, 30])
    expectedResults = {
        (1, None): [2, 0],
        (1, 0): [5, 3],
        (1, 1): [3, 2],
        (30, None): [1, 0],
        (30, 0): [5, 3],
        (30, 1): [2, 1],
        (30, 2): [1, 1],
        (30, 3): [1, 0]
    }
    actualResults = {k: list(v) for k, v in actualResults.iteritems()}
    self.assertEqual(expectedResults, actualResults)

  def testMaxConsecutiveFilter(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    labTests = [
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 1)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 2)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 3)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 4)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 5)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 6)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 11)]]
    actualResults = RepeatComponents.getStats(
        labTests, RepeatComponents.isNormal, max_consecutive=2, bins=[30])
    expectedResults = {
        (30, None): [1, 1],
        (30, 0): [1, 1],
        (30, 1): [2, 2],
        (30, 2): [1, 1]
    }
    actualResults = {k: list(v) for k, v in actualResults.iteritems()}
    self.assertEqual(expectedResults, actualResults)

  def testAbnormalResultFollowedByOutOfWindow(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    labTests = [
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 1)],
        ['6385739673941', '12078R(High)',       datetime(2000, 1, 2)],

        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 7)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 8)],
        ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 10)]]
    actualResults = RepeatComponents.getStats(
        labTests, RepeatComponents.isNormal, bins=[4])
    expectedResults = {
        (4, None): [2, 2],
        (4, 1): [2, 1],
        (4, 2): [1, 1]
    }
    actualResults = {k: list(v) for k, v in actualResults.iteritems()}
    self.assertEqual(expectedResults, actualResults)

  def testCreateGlobalStatsDf(self):
    """Lab test counting normal and abnormal consecutive lab tests"""
    global_stats = {
      'lab': {
        (4, None): [2, 2],
        (4, 1): [2, 1],
        (4, 2): [1, 1]
      }
    }
    actualResults = RepeatComponents.createGlobalStatsDf(global_stats).reset_index(drop=True)
    expectedResults = pd.DataFrame(data=[['lab', 4, 1, 2, 1], ['lab', 4, 2, 1, 1], ['lab', 4, 'NULL', 2, 2]], columns=['base_name', 'window', 'consecutive', 'total', 'normal']).reset_index(drop=True)
    self.assertTrue(expectedResults.equals(actualResults))


def suite():
  """Returns the suite of tests to run for this test class / module.
  Use unittest.makeSuite methods which simply extracts all of the
  methods for the given class whose name starts with "test"
  """
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRepeatComponents))
  return suite


if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())
