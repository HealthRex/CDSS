#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db.Model import RowItemModel;

from medinfo.analysis.AccuracyPerTopItems import AccuracyPerTopItems;

from Util import BaseTestAnalysis;

class TestAccuracyPerTopItems(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = AccuracyPerTopItems();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

    def test_analysis(self):
        # Simulate command_line
        inputFileStr = \
            """# Comment header to ignore
            outcome\tscore\tscore2
            0\t0.01\t1
            0\t0.02\t2
            0\t0.03\t3
            0\t0.04\t4
            0\t0.05\t5
            0\t0.11\t6
            1\t0.12\t7
            1\t0.13\t8
            0\t0.14\t9.1
            0\t0.15\t10.1
            0\t0.20\t11.5
            0\t0.21\t10.2
            1\t0.22\t9.2
            1\t0.23\t8
            0\t0.24\t7
            1\t0.31\t8
            1\t0.32\t9.3
            1\t0.33\t10.3
            1\t0.33\t11
            1\t0.34\t12
            1\t0.35\t13
            """
        headers = ["ItemsConsidered","recall:score", "precision:score", "F1:score"];
        expectedData = \
            [   [1, 0.1,    1.0,    0.18181],
                [2, 0.2,    1.0,    0.33333],
                [3, 0.3,    1.0,    0.46154],
                [4, 0.4,    1.0,    0.57143],
                [5, 0.5,    1.0,    0.66667],
                [6, 0.6,    1.0,    0.75],
                [7, 0.6,    0.85714,0.70588],
                [8, 0.7,    0.875,  0.77778],
                [9, 0.8,    0.88889,0.84211],
                [10,0.8,    0.8,    0.8],
            ];
        expectedResults = [RowItemModel(dataRow,headers) for dataRow in expectedData];  # Convert to dictionaries
        sys.stdin = StringIO(inputFileStr); # Simulate stdin input
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["AccuracyPerTopItems.py","-m","10","-o","outcome","-x","recall:score,precision:score,F1:score","-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, headers);
        
        # Repeat when comparising across multiple score columns
        headers = ["ItemsConsidered","recall:score", "recall:score2"];
        expectedData = \
            [   [1, 0.1,    0.1],
                [2, 0.2,    0.2],
                [3, 0.3,    0.2],
                [4, 0.4,    0.3],
                [5, 0.5,    0.4],
                [6, 0.6,    0.4],
                [7, 0.6,    0.4],
                [8, 0.7,    0.5],
                [9, 0.8,    0.6],
                [10,0.8,    0.6],
            ];
        expectedResults = [RowItemModel(dataRow,headers) for dataRow in expectedData];  # Convert to dictionaries
        sys.stdin = StringIO(inputFileStr); # Simulate stdin input
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["AccuracyPerTopItems.py","-m","10","-o","outcome","-x","recall:score,recall:score2","-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, headers);

def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestAccuracyPerTopItems));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
