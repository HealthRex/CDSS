#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
import unittest

from .Const import RUNNER_VERBOSITY;
from .Util import log;

from medinfo.db.Model import RowItemModel;
from medinfo.analysis.BatchTTests import BatchTTests;

from .Util import BaseTestAnalysis;


class TestBatchTTests(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = BatchTTests();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

    def test_ttests(self):
        # Simulate data files
        inputFileStr = \
            """# {"argv": ["medinfo\\\\ConcatenateDataFiles.py", "test.out"]}
patient_id\tnumQueryItems\tnumVerifyItems\tnumRecommendedItems\trecall\tprecision\torder_set_id\t-s\t-R\t-p
-111\t8\t10\t20\t0.3\t0.6\t0\tOR\tItemAssociationRecommender\tpatient_
-111\t13\t15\t13\t0.6\t0.6\t1\tOR\tItemAssociationRecommender\tpatient_
-111\t8\t13\t11\t0.3\t0.9\t2\tOR\tItemAssociationRecommender\tpatient_
-111\t7\t13\t28\t0.8\t0\t3\tOR\tItemAssociationRecommender\tpatient_
-111\t15\t15\t12\t0.6\t0.9\t4\tOR\tItemAssociationRecommender\tpatient_
-111\t5\t13\t23\t0.6\t0.4\t5\tOR\tItemAssociationRecommender\tpatient_
-222\t15\t7\t19\t0.7\t0.9\t0\tOR\tItemAssociationRecommender\tpatient_
-222\t7\t6\t28\t0.2\t0.5\t1\tOR\tItemAssociationRecommender\tpatient_
-222\t10\t5\t20\t0.1\t0.5\t2\tOR\tItemAssociationRecommender\tpatient_
-222\t5\t5\t0\t0.7\t0.9\t3\tOR\tItemAssociationRecommender\tpatient_
-222\t8\t0\t16\t0.9\t0.7\t4\tOR\tItemAssociationRecommender\tpatient_
-222\t0\t6\t19\t0\t0.9\t5\tOR\tItemAssociationRecommender\tpatient_
-333\t12\t10\t28\t0.1\t0.7\t0\tOR\tItemAssociationRecommender\tpatient_
-333\t7\t10\t24\t0.3\t0.4\t1\tOR\tItemAssociationRecommender\tpatient_
-333\t15\t7\t21\t0\t0.8\t2\tOR\tItemAssociationRecommender\tpatient_
-333\t9\t10\t11\t0.9\t0.7\t3\tOR\tItemAssociationRecommender\tpatient_
-333\t11\t10\t26\t0.8\tNone\t4\tOR\tItemAssociationRecommender\tpatient_
-333\t11\t10\t12\tNone\t0.1\t5\tOR\tItemAssociationRecommender\tpatient_
-111\t8\t10\t20\t0.4\t0.2\t0\tPPV\tItemAssociationRecommender\tpatient_
-111\t13\t15\t13\t0.9\t0.5\t1\tPPV\tItemAssociationRecommender\tpatient_
-111\t8\t13\t11\t0.4\t0.9\t2\tPPV\tItemAssociationRecommender\tpatient_
-111\t7\t13\t28\t0.3\t0.1\t3\tPPV\tItemAssociationRecommender\tpatient_
-111\t15\t15\t12\t0.7\t0\t4\tPPV\tItemAssociationRecommender\tpatient_
-111\t5\t13\t23\t0.1\t0.3\t5\tPPV\tItemAssociationRecommender\tpatient_
-222\t15\t7\t19\t0.9\t0.9\t0\tPPV\tItemAssociationRecommender\tpatient_
-222\t7\t6\t28\t0.6\t0.4\t1\tPPV\tItemAssociationRecommender\tpatient_
-222\t10\t5\t20\t0.1\t0.3\t2\tPPV\tItemAssociationRecommender\tpatient_
-222\t5\t5\t0\t0.9\t0.9\t3\tPPV\tItemAssociationRecommender\tpatient_
-222\t8\t0\t16\t0.9\t0.1\t4\tPPV\tItemAssociationRecommender\tpatient_
-222\t0\t6\t19\t0.4\t0.6\t5\tPPV\tItemAssociationRecommender\tpatient_
-333\t12\t10\t28\t0.8\t0.5\t0\tPPV\tItemAssociationRecommender\tpatient_
-333\t7\t10\t24\t0\t0\t1\tPPV\tItemAssociationRecommender\tpatient_
-333\t15\t7\t21\t0.3\t0.7\t2\tPPV\tItemAssociationRecommender\tpatient_
-333\t9\t10\t11\t0.9\t0.5\t3\tPPV\tItemAssociationRecommender\tpatient_
-333\t11\t10\t26\t0.3\t0.9\t4\tPPV\tItemAssociationRecommender\tpatient_
-333\t11\t10\t12\t0.4\t0.1\t5\tPPV\tItemAssociationRecommender\tpatient_
-111\t7\t13\t28\t0\t0.7\t3\tNone\tOrderSetUsage\tNone
-111\t15\t15\t12\t0.1\t0.8\t4\tNone\tOrderSetUsage\tNone
-111\t5\t13\t23\t0.9\t0.1\t5\tNone\tOrderSetUsage\tNone
-111\t8\t10\t20\t0.7\t0.9\t0\tNone\tOrderSetUsage\tNone
-111\t13\t15\t13\t0.3\t0.8\t1\tNone\tOrderSetUsage\tNone
-111\t8\t13\t11\t0.5\t0.7\t2\tNone\tOrderSetUsage\tNone
-222\t5\t5\t0\t0.2\t0.5\t3\tNone\tOrderSetUsage\tNone
-222\t8\t0\t16\t0.9\t0.1\t4\tNone\tOrderSetUsage\tNone
-222\t0\t6\t19\t0.5\t0.9\t5\tNone\tOrderSetUsage\tNone
-222\t15\t7\t19\t0.7\t0.3\t0\tNone\tOrderSetUsage\tNone
-222\t7\t6\t28\t0.1\t0.1\t1\tNone\tOrderSetUsage\tNone
-222\t10\t5\t20\t0.6\t0.4\t2\tNone\tOrderSetUsage\tNone
-333\t12\t10\t28\t0.4\t0\t0\tNone\tOrderSetUsage\tNone
-333\t7\t10\t24\t0.1\t0.7\t1\tNone\tOrderSetUsage\tNone
-333\t15\t7\t21\t0.9\t0.8\t2\tNone\tOrderSetUsage\tNone
-333\t9\t10\t11\t0.7\t0.2\t3\tNone\tOrderSetUsage\tNone
-333\t11\t10\t26\t0.5\t0\t4\tNone\tOrderSetUsage\tNone
-333\t11\t10\t12\t0.7\t0.7\t5\tNone\tOrderSetUsage\tNone
""";         
        # Analysis via prepared validation data file
        sys.stdin = StringIO(inputFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["BatchTTests.py", "-l","-s,-R", "-b","None,OrderSetUsage", "-v","precision,recall", "-m","patient_id,order_set_id", "-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        # print(sys.stdout.getvalue(), file=sys.stderr)

        # Expected data
        colNames = \
            [   "Group0.-s",
                "Group1.-s",
                "Group0.-R",
                "Group1.-R",
                "Group0.precision.len",
                "Group1.precision.len",
                "Group0.precision.mean",
                "Group1.precision.mean",
                "Group0.precision.std",
                "Group1.precision.std",
                "Group0.precision.median",
                "Group1.precision.median",
                "Group0.precision.percentile25",
                "Group1.precision.percentile25",
                "Group0.precision.percentile75",
                "Group1.precision.percentile75",
                "Group0.recall.len",
                "Group1.recall.len",
                "Group0.recall.mean",
                "Group1.recall.mean",
                "Group0.recall.std",
                "Group1.recall.std",
                "Group0.recall.median",
                "Group1.recall.median",
                "Group0.recall.percentile25",
                "Group1.recall.percentile25",
                "Group0.recall.percentile75",
                "Group1.recall.percentile75",
                "ttest_ind.precision",
                "ttest_ind.recall",
                "ttest_rel.precision",
                "ttest_rel.recall"
            ];
        expectedResults = [
            RowItemModel([None, "OR",  "OrderSetUsage", "ItemAssociationRecommender", 17, 17, 0.511764705882, 0.617647058824, 0.308473190638, 0.268405518742, 0.7, 0.7, 0.2, 0.5, 0.8, 0.9, 17, 17, 0.476470588235, 0.464705882353, 0.294117647059, 0.30858534232, 0.5, 0.6, 0.2, 0.2, 0.7, 0.7, 0.30806740457, 0.912789941607, 0.312974093324, 0.913587910288], colNames ),
            RowItemModel([None, "PPV", "OrderSetUsage", "ItemAssociationRecommender", 18, 18, 0.483333333333, 0.438888888889, 0.321886798597, 0.314711311962, 0.6, 0.45, 0.125, 0.125, 0.775, 0.675, 18, 18, 0.488888888889, 0.516666666667, 0.29038076323, 0.304138126515, 0.5, 0.4, 0.225, 0.3, 0.7, 0.875, 0.686511526989, 0.786986894926, 0.713757104768, 0.791576162848], colNames ),
            RowItemModel([None, None, "OrderSetUsage", "OrderSetUsage", 18, 18, 0.483333333333, 0.483333333333, 0.321886798597, 0.321886798597, 0.6, 0.6, 0.125, 0.125, 0.775, 0.775, 18, 18, 0.488888888889, 0.488888888889, 0.29038076323, 0.29038076323, 0.5, 0.5, 0.225, 0.225, 0.7, 0.7, 1.0, 1.0, None, None], colNames),
        ]
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


        
        # Do again, but without specific base columns or paired t-testing
        sys.stdin = StringIO(inputFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["BatchTTests.py", "-l","-s,-R", "-v","precision,recall", "-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue();

        # Expected data
        expectedResults = \
            [
                RowItemModel(['OR', 'OR', 'ItemAssociationRecommender', 'ItemAssociationRecommender', 17, 17, 0.617647058824, 0.617647058824, 0.268405518742, 0.268405518742, 0.7, 0.7, 0.5, 0.5, 0.9, 0.9, 17, 17, 0.464705882353, 0.464705882353, 0.30858534232, 0.30858534232, 0.6, 0.6, 0.2, 0.2, 0.7, 0.7, 1.0, 1.0, None, None], colNames ),
                RowItemModel(['OR', 'PPV', 'ItemAssociationRecommender', 'ItemAssociationRecommender', 17, 17, 0.617647058824, 0.411764705882, 0.268405518742, 0.302698360712, 0.7, 0.4, 0.5, 0.1, 0.9, 0.6, 17, 17, 0.464705882353, 0.523529411765, 0.30858534232, 0.311598179721, 0.6, 0.4, 0.2, 0.3, 0.7, 0.9, 0.050138882624, 0.59529734676, 0.00409620577776, 0.489537980441], colNames ),
                RowItemModel(['OR', None, 'ItemAssociationRecommender', 'OrderSetUsage', 17, 17, 0.617647058824, 0.511764705882, 0.268405518742, 0.308473190638, 0.7, 0.7, 0.5, 0.2, 0.9, 0.8, 17, 17, 0.464705882353, 0.476470588235, 0.30858534232, 0.294117647059, 0.6, 0.5, 0.2, 0.2, 0.7, 0.7, 0.30806740457, 0.912789941607, 0.398341057085, 0.921720561974], colNames ),
                RowItemModel(['PPV', 'OR', 'ItemAssociationRecommender', 'ItemAssociationRecommender', 17, 17, 0.411764705882, 0.617647058824, 0.302698360712, 0.268405518742, 0.4, 0.7, 0.1, 0.5, 0.6, 0.9, 17, 17, 0.523529411765, 0.464705882353, 0.311598179721, 0.30858534232, 0.4, 0.6, 0.3, 0.2, 0.9, 0.7, 0.050138882624, 0.59529734676, 0.00409620577776, 0.489537980441], colNames ),
                RowItemModel(['PPV', 'PPV', 'ItemAssociationRecommender', 'ItemAssociationRecommender', 18, 18, 0.438888888889, 0.438888888889, 0.314711311962, 0.314711311962, 0.45, 0.45, 0.125, 0.125, 0.675, 0.675, 18, 18, 0.516666666667, 0.516666666667, 0.304138126515, 0.304138126515, 0.4, 0.4, 0.3, 0.3, 0.875, 0.875, 1.0, 1.0, None, None], colNames ),
                RowItemModel(
                    ['PPV', None, 'ItemAssociationRecommender', 'OrderSetUsage', 18, 18, 0.438888888889, 0.483333333333,
                     0.314711311962, 0.321886798597, 0.45, 0.6, 0.125, 0.125, 0.675, 0.775, 18, 18, 0.516666666667,
                     0.488888888889, 0.304138126515, 0.29038076323, 0.4, 0.5, 0.3, 0.225, 0.875, 0.7, 0.686511526989,
                     0.786986894926, 0.742147103681, 0.802972782098], colNames),

                RowItemModel(
                    [None, "OR", "OrderSetUsage", "ItemAssociationRecommender", 17, 17, 0.511764705882, 0.617647058824,
                     0.308473190638, 0.268405518742, 0.7, 0.7, 0.2, 0.5, 0.8, 0.9, 17, 17, 0.476470588235,
                     0.464705882353, 0.294117647059, 0.30858534232, 0.5, 0.6, 0.2, 0.2, 0.7, 0.7, 0.30806740457,
                     0.912789941607, 0.398341057058, 0.921720561974], colNames),
                RowItemModel(
                    [None, "PPV", "OrderSetUsage", "ItemAssociationRecommender", 18, 18, 0.483333333333, 0.438888888889,
                     0.321886798597, 0.314711311962, 0.6, 0.45, 0.125, 0.125, 0.775, 0.675, 18, 18, 0.488888888889,
                     0.516666666667, 0.29038076323, 0.304138126515, 0.5, 0.4, 0.225, 0.3, 0.7, 0.875, 0.686511526989,
                     0.786986894926, 0.742147103681, 0.802972782098], colNames),
                RowItemModel([None, None, "OrderSetUsage", "OrderSetUsage", 18, 18, 0.483333333333, 0.483333333333,
                              0.321886798597, 0.321886798597, 0.6, 0.6, 0.125, 0.125, 0.775, 0.775, 18, 18,
                              0.488888888889, 0.488888888889, 0.29038076323, 0.29038076323, 0.5, 0.5, 0.225, 0.225, 0.7,
                              0.7, 1.0, 1.0, None, None], colNames),
            ];
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

    
def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestBatchTTests));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
