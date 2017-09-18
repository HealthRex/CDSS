#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
import unittest
import pandas.util.testing as pdt;

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.Model import RowItemModel;
from medinfo.db.ResultsFormatter import pandas_read_table;
from medinfo.analysis.SQLQueryDataFile import SQLQueryDataFile;

from Util import BaseTestAnalysis;

class TestSQLQueryDataFile(BaseTestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseTestAnalysis.setUp(self);
        
        # Instance to test on
        self.analyzer = SQLQueryDataFile();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        BaseTestAnalysis.tearDown(self);

    def test_main(self):
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
        sqlQuery = "select * from data where numVerifyItems = 0";
        verifyOutput = StringIO("""patient_id\tnumqueryitems\tnumverifyitems\tnumrecommendeditems\trecall\tprecision\torder_set_id\t_s\t_r\t_p
-222\t8\t0\t16\t0.9\t0.7\t4\tOR\tItemAssociationRecommender\tpatient_
-222\t8\t0\t16\t0.9\t0.1\t4\tPPV\tItemAssociationRecommender\tpatient_
-222\t8\t0\t16\t0.9\t0.1\t4\tNone\tOrderSetUsage\tNone
""");        
        self.verifyQueryResult(sqlQuery, StringIO(inputFileStr), verifyOutput );

        # Analysis via prepared validation data file
        sqlQuery = "select patient_id, sum(precision), count(distinct order_set_id) from data where numVerifyItems <> 0 group by patient_id";
        verifyOutput = StringIO("""patient_id\tsum(precision)\tcount(distinct order_set_id)
-333\t7.8\t6
-222\t9.0\t5
-111\t9.4\t6
""");        
        self.verifyQueryResult(sqlQuery, StringIO(inputFileStr), verifyOutput );

        sqlQuery = "select * from data where patient_id = -333 and numQueryItems = 11 and _s = 'OR'";
        verifyOutput = StringIO("""patient_id\tnumqueryitems\tnumverifyitems\tnumrecommendeditems\trecall\tprecision\torder_set_id\t_s\t_r\t_p
-333\t11\t10\t26\t0.8\tNone\t4\tOR\tItemAssociationRecommender\tpatient_
-333\t11\t10\t12\tNone\t0.1\t5\tOR\tItemAssociationRecommender\tpatient_
""");        
        self.verifyQueryResult(sqlQuery, StringIO(inputFileStr), verifyOutput );

    def verifyQueryResult(self, sqlQuery, inputFile, verifyOutputFile):
        verifyDF = pandas_read_table(verifyOutputFile);

        sys.stdin = inputFile;
        sys.stdout = StringIO();
        argv = ["SQLQueryDataFile.py", "-q", sqlQuery, "-","-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        sampleDF = pandas_read_table(textOutput);
        #print >> sys.stderr, sampleDF[verifyDF.columns];
        pdt.assert_frame_equal( verifyDF, sampleDF[verifyDF.columns]); # Only compare against subset of verify columns

    
def suite():
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestSQLQueryDataFile));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
