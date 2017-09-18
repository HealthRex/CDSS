# import sys, os
# from cStringIO import StringIO
from datetime import datetime
import unittest

from repeat_result_descriptive import RepeatResults

class TestRepeatResults(unittest.TestCase):
    def setUp(self):
        """Prepare state for test cases"""
        # Create temp (SQLite) database file to work with
        # self.conn = sqlite3.connect(TEMP_DATABASE_FILENAME);

        # Application instance to test on
        self.maxDiff = None;
        self.app = RepeatResults();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        # Close DB connection
        # self.conn.close();

    def test__getStats(self):
        """Lab test counting normal and abnormal consecutive lab tests"""
        labTests = [['6385739673941', '12078R(InRange)',    datetime(2000, 1, 1)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 2)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1, 3)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 4)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1, 8)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 9)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 12)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 13)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1, 18)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 19)]]
        actualResults = self.app._getStats(labTests)
        expectedResults = { 
                            (1, 0): [7, 5],
                            (1, 1): [3, 2],
                            (2, 0): [7, 5],
                            (2, 1): [2, 2],
                            (2, 2): [1, 0],
                            (4, 0): [5, 4],
                            (4, 1): [3, 2],
                            (4, 2): [2, 1],
                            (7, 0): [4, 4],
                            (7, 1): [3, 2],
                            (7, 2): [3, 1],
                            (7, 0): [4, 4],
                            (7, 1): [3, 2],
                            (7, 2): [2, 1],
                            (7, 3): [1, 0],
                            (90, 0): [4,4],
                            (90, 1): [3, 2],
                            (90, 2): [2, 1],
                            (90, 3): [1, 0],
                        }
        actualResults = {k:list(v) for k, v in actualResults.iteritems()}
        self.assertEqual(expectedResults, actualResults)

    def test_calculateConsecutiveNormalStats(self):
        """Revised test cased based on revised definition of normal rate stats to extract.
        RepeatResults.getStats expect it to process:
            - Inputs
                - Window Sizes / Bins: How far back to look for each lab test ordered for prior results
                - Maximum number of consecutive normals to assess
            - Outputs
                For each window size + consective normal count (0 up to max count)
                - Number of results in the sequence that occurred where preceded 
                    by the consecutive number of normal results within the window period
                - Number of the results above that were themselves "normal"
                - Additional result for consecutive normal count is NULL,
                    to count results where no prior result existed within the window period
        """
        labTests = [['6385739673941', '12078R(InRange)',    datetime(2000, 1, 1)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 2)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1, 3)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1, 4)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1, 8)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1, 9)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1,10)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1,11)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1,12)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1,13)],
                    ['6385739673941', '12078R(High)',       datetime(2000, 1,18)],
                    ['6385739673941', '12078R(InRange)',    datetime(2000, 1,19)]]
        actualResults = self.app.calculateConsecutiveNormalStats(labTests, bins=[1,7], maxConsecutive=2);
        expectedResults = \
            { 
                (1, None):  {"totalCount":2, "normalCount":1},
                (1, 0):     {"totalCount":5, "normalCount":3},
                (1, 1):     {"totalCount":6, "normalCount":4},
                (1, 2):     {"totalCount":0, "normalCount":0},
                (7, None):  {"totalCount":1, "normalCount":1},
                (7, 0):     {"totalCount":5, "normalCount":3},
                (7, 1):     {"totalCount":6, "normalCount":4},
                (7, 2):     {"totalCount":3, "normalCount":1},
            };
        #actualResults = {k:list(v) for k, v in actualResults.iteritems()}
        self.assertEqual(expectedResults, actualResults)



def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRepeatResults))
    return suite


if __name__=="__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
