#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.Const import NULL_STRING;
from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.cpoe.analysis.OrderSetRecommenderClassificationAnalysis import OrderSetRecommenderClassificationAnalysis;

from Util import BaseCPOETestAnalysis;


class TestOrderSetRecommenderClassificationAnalysis(BaseCPOETestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        
        self.clinicalItemCategoryIdStrList = list();
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
            self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

        headers = ["clinical_item_id","clinical_item_category_id","name","analysis_status"];
        dataModels = \
            [   
                RowItemModel( [-1, -1, "CBC",1], headers ),
                RowItemModel( [-2, -1, "BMP",0], headers ), # Clear analysis status, so this will be ignored unless changed
                RowItemModel( [-3, -1, "Hepatic Panel",1], headers ),
                RowItemModel( [-4, -1, "Cardiac Enzymes",1], headers ),
                RowItemModel( [-5, -2, "CXR",1], headers ),
                RowItemModel( [-6, -2, "RUQ Ultrasound",1], headers ),
                RowItemModel( [-7, -2, "CT Abdomen/Pelvis",1], headers ),
                RowItemModel( [-8, -2, "CT PE Thorax",1], headers ),
                RowItemModel( [-9, -3, "Acetaminophen",1], headers ),
                RowItemModel( [-10, -3, "Carvedilol",1], headers ),
                RowItemModel( [-11, -3, "Enoxaparin",1], headers ),
                RowItemModel( [-12, -3, "Warfarin",1], headers ),
                RowItemModel( [-13, -3, "Ceftriaxone",1], headers ),
                RowItemModel( [-14, -4, "Foley Catheter",1], headers ),
                RowItemModel( [-15, -4, "Strict I&O",1], headers ),
                RowItemModel( [-16, -4, "Fall Precautions",1], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );


        dataTextStr = \
"""item_collection_id;external_id;name;section;subgroup
-1;-1;Test Order Set - 1;Meds;TreatmentMeds
-2;-1;Test Order Set - 1;Meds;SymptomsMeds
-3;-1;Test Order Set - 1;Labs;GeneralLabs
-4;-2;Test Order Set - 2;Labs;GeneralLabs
-5;-2;Test Order Set - 2;Imaging;Xrays
-6;-2;Test Order Set - 2;Imaging;AdvancedImaging
-7;-3;Test Order Set - 3;Imaging;GeneralImaging
-8;-3;Test Order Set - 3;Nursing;GeneralNursing
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection", delim=";");

        dataTextStr = \
"""item_collection_item_id;item_collection_id;clinical_item_id;collection_type_id
-1;-1;-12;4
-2;-1;-13;4
-3;-2;-11;4
-4;-2;-10;4
-5;-3;-1;4
-6;-3;-2;4
-7;-4;-2;4
-8;-4;-3;4
-9;-5;-5;4
-10;-6;-6;4
-11;-6;-7;4
-12;-6;-8;4
-13;-7;-5;4
-14;-7;-6;4
-15;-8;-14;4
-16;-8;-15;4
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection_item", delim=";");


        # Sample Prepared Validation File
        self.validationFileStr = \
"""patient_id\tqueryItemCountByIdJSON\tverifyItemCountByIdJSON\tbaseItemId\tbaseItemDate\tqueryStartTime\tqueryEndTime\tverifyEndTime\toutcome.7
123\t{"-1": 1, "-2": 1, "-3": 1, "-4": 1, "-5": 1, "-8": 1, "-9": 1, "-10": 1, "-11": 1, "-12": 1, "-13": 1}\t{"-12": 1, "-14": 1, "-15": 1, "-16": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-11 14:57:00\t2012-04-12 10:57:00\t0
456\t{"-2": 1, "-4": 2, "-8": 4, "-10": 1, "-12": 6}\t{"-12": 6, "-14": 7, "-16": 8}\t10\t2013-12-24 00:00:00\t2013-12-24 06:50:00\t2013-12-24 10:50:00\t2013-12-25 06:50:00\t1
789\t{"-1": 1, "-3": 3, "-5": 5, "-9": 9, "-10": 1, "-11": 11}\t{"-13": 13, "-15": 15}\t10\t2011-08-19 00:00:00\t2011-08-19 11:12:00\t2011-08-19 15:12:00\t2011-08-20 11:12:00\t0
""" 
        
        self.analyzer = OrderSetRecommenderClassificationAnalysis();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")
        DBUtil.execute("delete from item_collection_item where item_collection_item_id < 0");
        DBUtil.execute("delete from item_collection where item_collection_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_category_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );
        
        DBTestCase.tearDown(self);

    def test_orderSetRecommenderClassificationAnalysis(self):
        # Run the modeling analysis against the mock test data above and verify expected stats afterwards.

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "weightF1-score", "ROC-AUC"];
        
        expectedResults = \
            [   RowItemModel([123,  2,2,2,  0.5,   0.5,  0.5,   0.4,   0.571, 0.471, 0.0,], colNames ),    # ROC < 0.5 means prediction is so bad, it's getting opposite predictions right
                RowItemModel([456,  0,3,4,  0.0,   0.0,  0.0,   0.0,   0.0,   0.0,   0.0625,], colNames ),
                RowItemModel([789,  1,1,3,  0.5,   0.25, 0.333, 0.5,   0.333, 0.4,   0.333,], colNames ),
            ];
        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OrderSetRecommenderClassificationAnalysis.py", "-r","4", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


        expectedResults = \
            [   RowItemModel([123,  2,2,2,  0.5,   0.5,  0.5,   0.4,   0.571, 0.471, 0.0,], colNames ),    # ROC < 0.5 means prediction is so bad, it's getting opposite predictions right
                RowItemModel([456,  0,3,4,  0.0,   0.0,  0.0,   0.0,   0.0,   0.0,   0.0625,], colNames ),
                RowItemModel([789,  1,1,3,  0.5,   0.25, 0.333, 0.5,   0.286, 0.364, 0.5,], colNames ),
            ];
        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OrderSetRecommenderClassificationAnalysis.py", "-s","tfidf", "-r","4", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue()
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestOrderSetRecommenderClassificationAnalysis('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestOrderSetRecommenderClassificationAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
