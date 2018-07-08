#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

import numpy as np;

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.Const import NULL_STRING;
from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.cpoe.TopicModel import TopicModel;
from medinfo.cpoe.analysis.TopicModelAnalysis import TopicModelAnalysis;

# Look for test files by module location
import medinfo.cpoe.analysis.test;
TEST_DIR = os.path.dirname(medinfo.cpoe.analysis.test.__file__);
TEST_FILE_PREFIX = "TestTopicModel.model";

class TestTopicModelAnalysis(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        #self.purgeTestRecords();
        
        headers = ["clinical_item_category_id","source_table"];
        dataModels = \
            [   
                RowItemModel( [-1, "Labs"], headers ),
                RowItemModel( [-2, "Imaging"], headers ),
                RowItemModel( [-3, "Meds"], headers ),
                RowItemModel( [-4, "Nursing"], headers ),
                RowItemModel( [-5, "Problems"], headers ),
                RowItemModel( [-6, "Lab Results"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );

        headers = ["clinical_item_id","clinical_item_category_id","name","analysis_status"];
        dataModels = \
            [   
                RowItemModel( [1, -1, "CBC",1], headers ),
                RowItemModel( [2, -1, "BMP",0], headers ), # Clear analysis status, so this will be ignored unless changed
                RowItemModel( [3, -1, "Hepatic Panel",1], headers ),
                RowItemModel( [4, -1, "Cardiac Enzymes",1], headers ),
                RowItemModel( [5, -2, "CXR",1], headers ),
                RowItemModel( [6, -2, "RUQ Ultrasound",1], headers ),
                RowItemModel( [7, -2, "CT Abdomen/Pelvis",1], headers ),
                RowItemModel( [8, -2, "CT PE Thorax",1], headers ),
                RowItemModel( [9, -3, "Acetaminophen",1], headers ),
                RowItemModel( [10, -3, "Carvedilol",1], headers ),
                RowItemModel( [11, -3, "Enoxaparin",1], headers ),
                RowItemModel( [12, -3, "Warfarin",1], headers ),
                RowItemModel( [13, -3, "Ceftriaxone",1], headers ),
                RowItemModel( [14, -4, "Foley Catheter",1], headers ),
                RowItemModel( [15, -4, "Strict I&O",1], headers ),
                RowItemModel( [16, -4, "Fall Precautions",1], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        dataTextStr = \
"""item_collection_id;external_id;name;section;subgroup
-1;-1;Test Order Set - 1;Meds;TreatmentMeds
-2;-51;Test Order Set - 1;Meds;SymptomsMeds
-3;-51;Test Order Set - 1;Labs;GeneralLabs
-4;-52;Test Order Set - 2;Labs;GeneralLabs
-5;-52;Test Order Set - 2;Imaging;Xrays
-6;-2;Test Order Set - 2;Imaging;AdvancedImaging
-7;-3;Test Order Set - 3;Imaging;GeneralImaging
-8;-53;Test Order Set - 3;Nursing;GeneralNursing
-9;-53;Test Order Set - 3;Meds;RandomMeds
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection", delim=";");

        dataTextStr = \
"""item_collection_item_id;item_collection_id;clinical_item_id;collection_type_id
-1;-1;11;4
-2;-1;12;4
-3;-1;13;4
-4;-2;9;4
-5;-2;10;4
-6;-3;1;4
-7;-3;2;4
-8;-3;3;4
-100;-3;4;4
-9;-4;1;4
-10;-4;2;4
-11;-4;3;4
-101;-4;11;4
-12;-5;5;4
-74;-6;6;4
-77;-6;7;4
-13;-6;8;4
-14;-7;5;4
-15;-7;6;4
-16;-7;7;4
-17;-7;8;4
-18;-8;14;4
-19;-8;15;4
-20;-9;11;4
-21;-9;12;4
-22;-9;13;4
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection_item", delim=";");


        # Input file contents in Bag-of-Words formats from which can build Topic Models while avoiding binary versions that become obsolete in later versions
        self.inputBOWFileStr = \
"""[[1,1],[2,2],[3,1],[4,4],[5,10],[8,5]]
[[3,4],[4,4],[9,3],[10,2],[12,6],[13,3],[15,5],[16,8]]
[[1,1],[2,2],[3,1],[4,4],[5,10],[8,5],[9,1],[10,2],[11,1],[12,4],[13,10],[14,1],[15,3],[16,5]]
[[1,4],[2,9],[9,1],[10,2],[11,7],[12,4],[13,2],[16,6]]
[[4,3],[5,31],[8,5],[12,6],[13,8],[16,5]]
"""
        self.instance = TopicModel();  # Instance to test on
        self.instance.randomState = np.random.RandomState(1);  # Start with a fixed random state so that topic model generating process will be consistent for regression testing

        # Build typical LDA model and store in temp files
        sys.stdin = StringIO(self.inputBOWFileStr);
        subargv = ["TopicModel", "-n", "3", "-i", "5", "-", os.path.join(TEST_DIR,TEST_FILE_PREFIX)];
        self.instance.main(subargv);
        self.ldaModel = self.instance.loadModel( os.path.join(TEST_DIR,TEST_FILE_PREFIX) );

        # Build HDP model in separate temp files
        sys.stdin = StringIO(self.inputBOWFileStr);
        subargv = ["TopicModel", "-n", "0", "-i", "5", "-", os.path.join(TEST_DIR,"HDP"+TEST_FILE_PREFIX)];
        self.instance.main(subargv);
        self.hdpModel = self.instance.loadModel( os.path.join(TEST_DIR,"HDP"+TEST_FILE_PREFIX) );

        self.docCountByWordId = self.instance.loadDocCountByWordId( os.path.join(TEST_DIR,self.instance.topTopicFilename(TEST_FILE_PREFIX)) );
        
        # Sample Prepared Validation File
        self.validationFileStr = \
"""patient_id\tqueryItemCountByIdJSON\tverifyItemCountByIdJSON\tbaseItemId\tbaseItemDate\tqueryStartTime\tqueryEndTime\tverifyEndTime\toutcome.7\torder_set_id
123\t{"1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "8": 1, "9": 1, "10": 1, "11": 1, "12": 1, "13": 1}\t{"12": 1, "14": 1, "15": 1, "16": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-11 14:57:00\t2012-04-12 10:57:00\t0\t-1
456\t{"2": 1, "4": 2, "8": 4, "10": 1, "12": 6}\t{"12": 6, "14": 7, "16": 8}\t10\t2013-12-24 00:00:00\t2013-12-24 06:50:00\t2013-12-24 10:50:00\t2013-12-25 06:50:00\t1\t-2
789\t{"1": 1, "3": 3, "5": 5, "9": 9, "10": 1, "11": 11}\t{"13": 13, "15": 15}\t10\t2011-08-19 00:00:00\t2011-08-19 11:12:00\t2011-08-19 15:12:00\t2011-08-20 11:12:00\t0\t-3
""" 
        
        self.analyzer = TopicModelAnalysis();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.purgeTestRecords();

        # Remove Topic Model temp files
        for filename in os.listdir(TEST_DIR):
            if filename.startswith(TEST_FILE_PREFIX):
                os.remove(os.path.join(TEST_DIR,filename));
            elif filename.startswith("HDP"+TEST_FILE_PREFIX):
                os.remove(os.path.join(TEST_DIR,filename));

        DBTestCase.tearDown(self);

    def purgeTestRecords(self):
        log.info("Purge test records from the database")
        DBUtil.execute("delete from patient_item_collection_link where patient_item_collection_link_id < 0");
        DBUtil.execute("delete from item_collection_item where item_collection_item_id < 0");
        DBUtil.execute("delete from item_collection where item_collection_id < 0");

        DBUtil.execute("delete from clinical_item where clinical_item_category_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id < 0");

    def test_topicModelAnalysis(self):
        # Run the modeling analysis against the mock test data above and verify expected stats afterwards.

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "weightF1-score", "ROC-AUC"];
        
        expectedResults = \
            [   RowItemModel([123, 3,1,0, 0.75,  1.0,  0.857, 0.875, 1.0,   0.933, None], colNames ),   # ROC undefined when all recommended items are verify items (perfect precision)
                RowItemModel([456, 1,2,3, 0.333, 0.25, 0.286, 0.167, 0.1875,0.176, 0.357], colNames ),
                RowItemModel([789, 1,1,3, 0.5,   0.25, 0.333, 0.333, 0.231, 0.273, 0.417], colNames ),
            ];

        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["TopicModelAnalysis.py", "-M",os.path.join(TEST_DIR,TEST_FILE_PREFIX), "-r","4", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo with HdpModel
        expectedResults = \
            [   RowItemModel([123,  3,1,0,  0.75,  1.0,  0.857, 0.875, 1.0,   0.933, None,], colNames ),
                RowItemModel([456,  1,2,3,  0.333, 0.25, 0.286, 0.167, 0.176, 0.171, 0.571,], colNames ),
                RowItemModel([789,  1,1,3,  0.5,   0.25, 0.333, 0.667, 0.24,  0.353, 0.417,], colNames ),
            ];

        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["TopicModelAnalysis.py", "-M",os.path.join(TEST_DIR,"HDP"+TEST_FILE_PREFIX), "-r","4", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        ##### Redo with TF*IDF score weighting
        expectedResults = \
            [   RowItemModel([123,  3,1,0,  0.75,  1.0,  0.857, 0.875, 1.0,   0.933, None,], colNames ),    # ROC undefined when all recommended items are verify items (perfect precision)
                RowItemModel([456,  1,2,3,  0.333, 0.25, 0.286, 0.167, 0.1875,0.176, 0.357,], colNames ),
                RowItemModel([789,  1,1,3,  0.5,   0.25, 0.333, 0.667, 0.375, 0.48,  0.5,], colNames ),
            ];

        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["TopicModelAnalysis.py", "-M",os.path.join(TEST_DIR,TEST_FILE_PREFIX), "-r","4", "-s","lift", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo with HdpModel
        expectedResults = \
            [   RowItemModel([123,  3,1,0,  0.75,  1.0,  0.857, 0.875, 1.0,   0.933, None,], colNames ),
                RowItemModel([456,  1,2,3,  0.333, 0.25, 0.286, 0.667, 0.462, 0.545, 0.571,], colNames ),
                RowItemModel([789,  1,1,3,  0.5,   0.25, 0.333, 0.667, 0.24,  0.353, 0.333,], colNames ),
            ];

        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["TopicModelAnalysis.py", "-M",os.path.join(TEST_DIR,"HDP"+TEST_FILE_PREFIX), "-r","4", "-s","lift", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

    def test_topicModelAnalysis_numRecsByOrderSet(self):
        # Run the modeling analysis against the mock test data above and verify expected stats afterwards.

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "weightF1-score", "ROC-AUC"];
        
        expectedResults = \
            [   RowItemModel([123,  3,1,0,  0.75,  1.0,  0.857, 0.875, 1.0,   0.933, None,], colNames ),    # Order set with 3 recs
                RowItemModel([456,  1,2,2,  0.333, 0.333, 0.333, 0.167, 0.3, 0.214, 0.357,], colNames ),   # Order set size 3 recs
                RowItemModel([789,  1,1,3,  0.5,   0.25, 0.333, 0.333, 0.231, 0.273, 0.417,], colNames ),   # Order set size 4 recs
            ];

        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["TopicModelAnalysis.py", "-M",os.path.join(TEST_DIR,TEST_FILE_PREFIX), "--numRecsByOrderSet", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        #for row in TabDictReader(StringIO(sys.stdout.getvalue())):
        #    for col in colNames:
        #        print >> sys.stderr, row[col],
        #    print >> sys.stderr
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestTopicModelAnalysis("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestTopicModelAnalysis("test_insertFile_skipErrors"));
    #suite.addTest(TestTopicModelAnalysis('test_executeIterator'));
    #suite.addTest(TestTopicModelAnalysis('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestTopicModelAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
