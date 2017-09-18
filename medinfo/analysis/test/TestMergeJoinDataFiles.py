#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.ResultsFormatter import TabDictReader;
from medinfo.analysis.MergeJoinDataFiles import MergeJoinDataFiles;

from Util import BaseTestAnalysis;

class TestMergeJoinDataFiles(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = MergeJoinDataFiles();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

            
    def test_merge(self):
        # Simulate data files
        inputFiles = \
            [   # JSON style header
                StringIO \
                ("""# {"argv": ["medinfo\\\\Score.py", "-R", "ItemAssociationRecommender", "-c", "135", "-Q", "14400", "-V", "86400", "-r", "10", "-a", "unweighted", "177340", "test.out"]}
id\toutcome\tscore
1\t0\t0.01
2\t0\t0.02
3\t1\t0.13
"""),
                # Simple list style header
                StringIO \
                ("""# ["medinfo\\\\Score.py", "-R", "ItemAssociationRecommender", "-c", "135", "-Q", "14400", "-V", "86400", "-r", "10", "-a", "weighted", "-s", "PPV", "177340", "test2.out"]
id\toutcome\tscore2
1\t0\t0.15
3\t1\t0.31
4\t1\t0.23
"""),
                # Extra comment
                StringIO \
                ("""# Generic extra comment + True/False option
# ["medinfo\\\\Score.py", "-X", "-R", "ItemAssociationRecommender", "-c", "135", "-Q", "14400", "-V", "86400", "-r", "10", "-a", "weighted", "-s", "prevalence", "141", "test3.out"]
id\toutcome\tscore2
5\t2\t0.15
1\t0\t0.22
3\t1\t0.42
"""),
                # No header comment
                StringIO \
                ("""id\toutcome\tscore
5\t2\t0.25
6\t3\t0.52
4\t1\t0.82
"""),
            ];
        
        # Call application
        keyCol = ["id","outcome"];  # Key columns to expect to be the same
        suffixList = [".A",".B",".C",".D"]; # Force suffixes to be added to all other columns
        colNames = ["id", "outcome","score.A","score2.B","score2.C","score.D"];
        outFile = StringIO();
        self.analyzer( inputFiles, keyCol, suffixList, outFile );
        
        # Read output back into structured objects, and validate matches expected
        testResults = list(TabDictReader(StringIO(outFile.getvalue())));
        expectedResults = \
            [   dict( zip(colNames, ["1","0","0.01","0.15","0.22", "nan"]) ),
                dict( zip(colNames, ["2","0","0.02", "nan", "nan", "nan"]) ),
                dict( zip(colNames, ["3","1","0.13","0.31","0.42", "nan"]) ),
                dict( zip(colNames, ["4","1", "nan","0.23", "nan","0.82"]) ),
                dict( zip(colNames, ["5","2", "nan", "nan","0.15","0.25"]) ),
                dict( zip(colNames, ["6","3", "nan", "nan", "nan","0.52"]) ),
            ];
        self.assertEqualList( expectedResults, testResults );
    
def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestMergeJoinDataFiles));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
