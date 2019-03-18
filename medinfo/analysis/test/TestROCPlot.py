#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db.Model import RowItemModel;

from medinfo.analysis.ROCPlot import ROCPlot;

from Util import BaseTestAnalysis;

class TestROCPlot(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = ROCPlot();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

    def test_rocAnalysis(self):
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
0\t0.14\t9
0\t0.15\t10
0\t0.21\t11
0\t0.22\t10
1\t0.22\t9
1\t0.23\t8
0\t0.23\t7
1\t0.31\t8
1\t0.32\t9
1\t0.33\t10
1\t0.33\t11
1\t0.34\t12
1\t0.35\t13
"""
        expectedStatsByNameByScoreId = \
            {   "score":
                {   "ROC-AUC":  0.890909,
                    "pairsCorrect": 98.0,
                    "pairsChecked": 110,
                    "ROC-AUC-0.95-CI": (0.71, 1.00),
                }   
            }
        colNames = ["score.FPR","score.TPR"];
        expectedResults = \
            [   # Some variability in scikit learn roc_curve implementation on whether have redundant co-linear data points on the curve
                # Makes it harder to verify individual data points. Maybe well enough to just verify summary stats in JSON content
                RowItemModel([0.0, 0.1], colNames ),
                RowItemModel([0.0, 0.2], colNames ),
                RowItemModel([0.0, 0.4], colNames ),
                #RowItemModel([0.0, 0.5], colNames ),
                RowItemModel([0.0, 0.6], colNames ),
                #RowItemModel([0.0909090909091, 0.7], colNames ),
                RowItemModel([0.181818181818, 0.8], colNames ),
                #RowItemModel([0.272727272727, 0.8], colNames ),
                #RowItemModel([0.363636363636, 0.8], colNames ),
                RowItemModel([0.454545454545, 0.8], colNames ),
                #RowItemModel([0.454545454545, 0.9], colNames ),
                RowItemModel([0.454545454545, 1.0], colNames ),
                #RowItemModel([0.545454545455, 1.0], colNames ),
                #RowItemModel([0.636363636364, 1.0], colNames ),
                #RowItemModel([0.727272727273, 1.0], colNames ),
                #RowItemModel([0.818181818182, 1.0], colNames ),
                #RowItemModel([0.909090909091, 1.0], colNames ),
                RowItemModel([1.0, 1.0], colNames ),
            ];
        sys.stdin = StringIO(inputFileStr); # Simulate stdin input
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["ROCPlot.py","-n","1000","-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        jsonData = self.extractJSONComment(textOutput);
        
        self.verifyJSONData( expectedStatsByNameByScoreId, jsonData );
        #self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Repeat, but now with analysis of multiple score columns simultaneously
        expectedAUCbyId = {"score":0.890909, "score2":0.763636}
        expectedAUC95CIbyId = {"score":(0.71, 1.0), "score2": (0.50555,0.94545)}
        colNames = ["score.FPR","score.TPR","score2.FPR","score2.TPR"];

        expectedStatsByNameByScoreId = \
            {   "score":
                {   "ROC-AUC":  0.890909,
                    "pairsCorrect": 98.0,
                    "pairsChecked": 110,
                    "ROC-AUC-0.95-CI": (0.71, 1.00),
                },
                "score2":
                {   "ROC-AUC":  0.763636,
                    "pairsCorrect": 84.0,
                    "pairsChecked": 110,
                    "ROC-AUC-0.95-CI": (0.505,0.945),
                    "P-Chi2.score": 0.012526, # P-values in comparison to first scoring method
                    "P-YatesChi2.score": 0.020416, 
                    "P-Fisher.score": 0.019568, 
                }   
            }

        expectedResults = \
            [   # Some variability in scikit learn roc_curve implementation on whether have redundant co-linear data points on the curve
                RowItemModel([0.0, 0.1, 0.0, 0.1], colNames ),
                RowItemModel([0.0, 0.2, 0.0, 0.2], colNames ),
                RowItemModel([0.0, 0.4, 0.0909090909091, 0.3], colNames ),
                RowItemModel([0.0, 0.6, 0.272727272727, 0.4], colNames ),
                RowItemModel([0.181818181818, 0.8, 0.363636363636, 0.6], colNames ),
                RowItemModel([0.454545454545, 0.8, 0.363636363636, 0.9], colNames ),
                RowItemModel([0.454545454545, 1.0, 0.454545454545, 1.0], colNames ),
                RowItemModel([1.0, 1.0, 1.0, 1.0], colNames ),
            ];
        sys.stdin = StringIO(inputFileStr); # Simulate stdin input
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["ROCPlot.py","-n","1000","-s","score,score2","-b","score","-c","P-Chi2,P-YatesChi2,P-Fisher","-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        jsonData = self.extractJSONComment(textOutput);
        
        self.verifyJSONData( expectedStatsByNameByScoreId, jsonData );
        #self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

    def verifyJSONData( self, expectedStatsByNameByScoreId, jsonData ):
        """Pull out JSON data components and verify equals where expected"""

        for scoreId, expectedStatsByName in expectedStatsByNameByScoreId.iteritems():
            for statName, expectedValue in expectedStatsByName.iteritems():
                dataKey = "%s.%s" % (scoreId, statName);
                if isinstance( jsonData[dataKey], list ):
                    for (expected,sample) in zip( expectedValue, jsonData[dataKey] ):
                        self.assertAlmostEquals(expected,sample,2);
                else:
                    self.assertAlmostEquals( expectedValue, jsonData[dataKey], 5);
    
def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestROCPlot));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
