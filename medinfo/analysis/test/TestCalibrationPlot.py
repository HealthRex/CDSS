#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db.Model import RowItemModel;

from medinfo.analysis.CalibrationPlot import CalibrationPlot;

from Util import BaseTestAnalysis;

class TestCalibrationPlot(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = CalibrationPlot();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

    def test_calibrationAnalysis(self):
        # Simulate command_line
        inputFileStr = \
"""# Comment header to ignore
outcome\tscore
0\t0.01
0\t0.02
0\t0.03
0\t0.04
0\t0.05
0\t0.10
0\t0.11
1\t0.12
1\t0.13
0\t0.15
0\t0.21
0\t0.22
1\t0.22
0\t0.23
1\t0.23
1\t0.31
1\t0.32
1\t0.33
1\t0.33
1\t0.34
1\t0.35
"""
        expectedHLP = 0.000218;
        colNames = ["scoreMin","scoreMax", "totalInstances","observedOutcomes", "predictedOutcomes", "observedRate", "predictedRate"];
        expectedResults = \
            [   
                RowItemModel([0.01, 0.05, 5, 0, 0.15, 0.0, 0.030], colNames ),
                RowItemModel([0.10, 0.15, 5, 2, 0.61, 0.4, 0.122], colNames ),
                RowItemModel([0.21, 0.23, 5, 2, 1.11, 0.4, 0.222], colNames ),
                RowItemModel([0.31, 0.35, 6, 6, 1.98, 1.0, 0.330], colNames ),
            ];
        sys.stdin = StringIO(inputFileStr); # Simulate stdin input
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["CalibrationPlot.py","-b","4","-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        jsonData = self.extractJSONComment(textOutput);

        self.assertAlmostEquals(expectedHLP, jsonData["P-HosmerLemeshow"], 5);
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);
    
def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestCalibrationPlot));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
