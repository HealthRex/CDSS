#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
import unittest

from .Const import RUNNER_VERBOSITY;
from .Util import log;

from medinfo.db.Model import RowItemModel;
from medinfo.analysis.ConcatenateDataFiles import ConcatenateDataFiles;

from .Util import BaseTestAnalysis;

class TestConcatenateDataFiles(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = ConcatenateDataFiles();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

            
    def test_concatenate(self):
        # Simulate data files
        inputFiles = \
            [   # JSON style header
                StringIO \
                ("""# {"argv": ["medinfo\\\\Score.py", "-R", "ItemAssociationRecommender", "-c", "135", "-Q", "14400", "-V", "86400", "-r", "10", "-a", "unweighted", "177340", "test.out"]}
outcome\tscore
0\t0.01
0\t0.02
1\t0.13
"""),
                # Simple list style header
                StringIO \
                ("""# ["medinfo\\\\Score.py", "-R", "ItemAssociationRecommender", "-c", "135", "-Q", "14400", "-V", "86400", "-r", "10", "-a", "weighted", "-s", "PPV", "177340", "test2.out"]
outcome\tscore2
0\t0.15
1\t0.23
1\t0.31
"""),
                # Extra comment
                StringIO \
                ("""# Generic extra comment + True/False option
# ["medinfo\\\\Score.py", "-X", "-R", "ItemAssociationRecommender", "-c", "135", "-Q", "14400", "-V", "86400", "-r", "10", "-a", "weighted", "-s", "prevalence", "141", "test3.out"]
outcome\tscore2
2\t0.15
0\t0.22
1\t0.42
"""),
                # No header comment
                StringIO \
                ("""outcome\tscore
2\t0.25
3\t0.52
1\t0.82
"""),
            ];
        
        # Expected concatenated data
        colNames = ["outcome","score","score2","argv[0]","-R","-c","-Q","-V","-r","-a","-s","-X","args[0]","args[1]"];
        expectedResults = \
            [   
                RowItemModel(["0", "0.01", None,"medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","unweighted",None,None,"177340","test.out"], colNames ),
                RowItemModel(["0", "0.02", None,"medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","unweighted",None,None,"177340","test.out"], colNames ),
                RowItemModel(["1", "0.13", None,"medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","unweighted",None,None,"177340","test.out"], colNames ),

                RowItemModel(["0", None, "0.15", "medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","weighted","PPV",None,"177340","test2.out"], colNames ),
                RowItemModel(["1", None, "0.23", "medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","weighted","PPV",None,"177340","test2.out"], colNames ),
                RowItemModel(["1", None, "0.31", "medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","weighted","PPV",None,"177340","test2.out"], colNames ),

                RowItemModel(["2", None, "0.15", "medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","weighted","prevalence","-X","141","test3.out"], colNames ),
                RowItemModel(["0", None, "0.22", "medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","weighted","prevalence","-X","141","test3.out"], colNames ),
                RowItemModel(["1", None, "0.42", "medinfo\\Score.py","ItemAssociationRecommender","135","14400","86400","10","weighted","prevalence","-X","141","test3.out"], colNames ),

                RowItemModel(["2", "0.25", None, None, None, None, None, None, None, None, None,None, None, None], colNames ),
                RowItemModel(["3", "0.52", None, None, None, None, None, None, None, None, None,None, None, None], colNames ),
                RowItemModel(["1", "0.82", None, None, None, None, None, None, None, None, None,None, None, None], colNames ),
            ];
        testResults = list();
        for result in self.analyzer( inputFiles ):
            testResults.append(result);
        
        self.assertEqual( set(colNames), set(self.analyzer.resultHeaders()) );
        self.assertEqualList( expectedResults, testResults );
    
def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestConcatenateDataFiles));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
