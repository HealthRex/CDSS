#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
from datetime import datetime;
import unittest

from .Const import RUNNER_VERBOSITY;
from .Util import log;

from medinfo.common.Const import NULL_STRING;
from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.cpoe.analysis.OrderSetUsageAnalysis import OrderSetUsageAnalysis;

class TestOrderSetUsageAnalysis(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

        log.info("Populate the database with test data")
        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        #self.purgeTestRecords();
        
        headers = ["clinical_item_category_id","default_recommend","source_table"];
        dataModels = \
            [   
                RowItemModel( [-1, 1, "Labs"], headers ),
                RowItemModel( [-2, 1, "Imaging"], headers ),
                RowItemModel( [-3, 1, "Meds"], headers ),
                RowItemModel( [-4, 1, "Nursing"], headers ),
                RowItemModel( [-5, 1, "Problems"], headers ),
                RowItemModel( [-6, 1, "Lab Results"], headers ),
                RowItemModel( [-7, 0, "No Rec Category"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );

        headers = ["clinical_item_id","clinical_item_category_id","patient_count","name","analysis_status"];
        dataModels = \
            [   
                RowItemModel( [-1, -1, 100, "CBC",1], headers ),
                RowItemModel( [-2, -1, 200, "BMP",0], headers ), # Clear analysis status, so this will be ignored unless changed
                RowItemModel( [-3, -1, 300, "Hepatic Panel",1], headers ),
                RowItemModel( [-4, -1, 400, "Cardiac Enzymes",1], headers ),
                RowItemModel( [-5, -2, 500, "CXR",1], headers ),
                RowItemModel( [-6, -2, 600, "RUQ Ultrasound",1], headers ),
                RowItemModel( [-7, -2, 700, "CT Abdomen/Pelvis",1], headers ),
                RowItemModel( [-8, -2, 800, "CT PE Thorax",1], headers ),
                RowItemModel( [-9, -3, 900, "Acetaminophen",1], headers ),
                RowItemModel( [-10, -3, 1000, "Carvedilol",1], headers ),
                RowItemModel( [-11, -3, 100, "Enoxaparin",1], headers ),
                RowItemModel( [-12, -3, 200, "Warfarin",1], headers ),
                RowItemModel( [-13, -3, 300, "Ceftriaxone",1], headers ),
                RowItemModel( [-14, -4, 400, "Foley Catheter",1], headers ),
                RowItemModel( [-15, -4, 500, "Strict I&O",1], headers ),
                RowItemModel( [-16, -4, 600, "Fall Precautions",1], headers ),
                RowItemModel( [-77, -7, 700, "No Rec Item",1], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        dataTextStr = \
"""patient_item_id;patient_id;clinical_item_id;item_date
-1;-123;-6;3/11/2012 10:57
-2;-123;-7;3/11/2012 10:57
-3;-123;-1;4/11/2012 10:57
-4;-123;-2;4/11/2012 10:57
-5;-123;-3;4/11/2012 10:57
-6;-123;-4;4/11/2012 10:57
-8;-123;-8;4/11/2012 10:57
-9;-123;-9;4/11/2012 10:57
-10;-123;-10;4/11/2012 0:00
-11;-123;-11;4/11/2012 10:57
-12;-123;-12;4/11/2012 10:57
-13;-123;-13;4/11/2012 10:57
-14;-123;-12;4/12/2012 3:57
-15;-123;-14;4/12/2012 3:57
-16;-123;-15;4/12/2012 3:57
-17;-123;-16;4/12/2012 3:57
-18;-123;-13;5/12/2012 8:57
-19;-123;-5;5/12/2012 8:57
-21;-456;-4;12/24/2013 6:50
-22;-456;-4;12/24/2013 7:50
-24;-456;-77;12/24/2013 8:50
-25;-456;-10;12/24/2013 0:00
-26;-456;-12;12/24/2013 6:50
-27;-456;-12;12/24/2013 6:55
-28;-456;-12;12/24/2013 6:59
-29;-456;-12;12/24/2013 18:50
-30;-456;-12;12/24/2013 19:50
-31;-456;-14;12/24/2013 18:50
-32;-456;-8;12/24/2013 18:50
-33;-456;-8;12/24/2013 20:50
-34;-456;-8;12/24/2013 18:30
-35;-789;-1;8/19/2011 11:12
-36;-789;-3;8/19/2011 11:12
-37;-789;-3;8/19/2011 0:12
-38;-789;-3;8/19/2011 0:52
-39;-789;-5;8/19/2011 11:12
-40;-789;-9;8/19/2011 11:12
-41;-789;-9;8/19/2011 0:12
-42;-789;-9;8/19/2011 13:12
-43;-789;-10;8/19/2011 0:00
-44;-789;-11;8/19/2011 11:12
-45;-789;-13;8/19/2011 19:12
-46;-789;-15;8/19/2011 19:12
-47;-789;-15;8/19/2011 19:14
-48;-789;-15;8/19/2011 19:22
-49;-789;-15;8/19/2011 19:32
-50;-789;-15;8/19/2011 19:42
-1001;-321;-6;3/11/2012 10:57
-1002;-321;-7;3/11/2012 10:57
-1010;-321;-10;4/11/2012 0:00
-1003;-321;-1;4/11/2012 10:57
-1004;-321;-2;4/11/2012 10:57
-1005;-321;-3;4/11/2012 10:57
-1006;-321;-4;4/11/2012 10:57
-1008;-321;-8;4/11/2012 10:57
-1009;-321;-9;4/11/2012 10:57
-1011;-321;-11;4/11/2012 10:57
-1012;-321;-12;4/11/2012 10:57
-1013;-321;-13;4/11/2012 10:57
-1014;-321;-12;4/12/2012 3:57
-1015;-321;-14;4/12/2012 3:57
-1016;-321;-15;4/12/2012 3:57
-1017;-321;-16;4/12/2012 3:57
-1018;-321;-13;4/12/2012 8:57
-1019;-321;-5;4/12/2012 8:57
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "patient_item", delim=";");


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
-9;-4;Test Order Set - 4;Ad-hoc Orders;Ad-hoc Orders
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
-74;-6;-4;4
-77;-6;-77;4
-13;-7;-5;4
-14;-7;-6;4
-15;-8;-14;4
-16;-8;-15;4
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection_item", delim=";");

        dataTextStr = \
"""patient_item_collection_link_id;patient_item_id;item_collection_item_id
-1;-3;-5
-2;-4;-6
-3;-15;-15
-4;-32;-12
-1001;-1003;-5
-1002;-1004;-6
-1003;-1015;-15
-1004;-1019;-9
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "patient_item_collection_link", delim=";");


        # Sample Prepared Validation File
        self.validationFileStr = \
"""patient_id\tqueryItemCountByIdJSON\tverifyItemCountByIdJSON\tbaseItemId\tbaseItemDate\tqueryStartTime\tqueryEndTime\tverifyEndTime\toutcome.7
-123\t{"-1": 1, "-2": 1, "-3": 1, "-4": 1, "-8": 1, "-9": 1, "-10": 1, "-11": 1, "-12": 1, "-13": 1}\t{"-12": 1, "-14": 1, "-15": 1, "-16": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-11 14:57:00\t2012-04-12 10:57:00\t0
-456\t{"-4": 2, "-77": 1, "-10": 1, "-12": 3}\t{"-12": 2, "-14": 1, "-8": 3}\t10\t2013-12-24 00:00:00\t2013-12-24 06:50:00\t2013-12-24 10:50:00\t2013-12-25 06:50:00\t1
-789\t{"-1": 1, "-3": 3, "-5": 1, "-9": 3, "-10": 1, "-11": 1}\t{"-13": 1, "-15": 5}\t10\t2011-08-19 00:00:00\t2011-08-19 11:12:00\t2011-08-19 15:12:00\t2011-08-20 11:12:00\t0
-321\t{"-1": 1, "-2": 1, "-3": 1, "-4": 1, "-8": 1, "-9": 1, "-10": 1, "-11": 1, "-12": 1, "-13": 1}\t{"-12": 1, "-14": 1, "-15": 1, "-16": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-11 14:57:00\t2012-04-12 10:57:00\t0
""" 

        # Another Sample Prepared Validation File, with key Order Set triggers
        self.orderSetValidationFileStr = \
"""patient_id\tqueryItemCountByIdJSON\tverifyItemCountByIdJSON\tbaseItemId\tbaseItemDate\tqueryStartTime\tqueryEndTime\tverifyEndTime\toutcome.7\torder_set_id
-123\t{"-10": 1}\t{"-1": 1, "-2": 1, "-3": 1, "-4": 1, "-8": 1, "-9": 1, "-11": 1, "-12": 1, "-13": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-11 10:57:00\t2012-04-11 11:57:00\t0\t-1
-456\t{"-10": 1, "-4": 2, "-77": 1, "-12": 4, "-14": 1, "-8": 1}\t{"-12": 1, "-8": 2}\t10\t2013-12-24 00:00:00\t2013-12-24 06:50:00\t2013-12-24 18:50:00\t2013-12-24 19:50:00\t1\t-2
-789\t{"-1": 1, "-3": 3, "-5": 1, "-9": 3, "-10": 1, "-11": 1}\t{"-13": 1, "-15": 5}\t10\t2011-08-19 00:00:00\t2011-08-19 11:12:00\t2011-08-19 15:12:00\t2011-08-20 11:12:00\t0\t-4
-321\t{"-10": 1}\t{"-1": 1, "-2": 1, "-3": 1, "-4": 1, "-8": 1, "-9": 1, "-11": 1, "-12": 1, "-13": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-11 10:57:00\t2012-04-11 11:57:00\t0\t-1
-321\t{"-10": 1, "-1": 1, "-2": 1, "-3": 1, "-4": 1, "-8": 1, "-9": 1, "-11": 1, "-12": 1, "-13": 1}\t{"-12": 1,"-14": 1, "-15": 1, "-16": 1}\t10\t2012-04-11 00:00:00\t2012-04-11 10:57:00\t2012-04-12 3:57:00\t2012-04-12 4:57:00\t0\t-3
""" 
        
        self.analyzer = OrderSetUsageAnalysis();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.purgeTestRecords();
        DBTestCase.tearDown(self);

    def purgeTestRecords(self):
        log.info("Purge test records from the database")
        DBUtil.execute("delete from patient_item_collection_link where patient_item_collection_link_id < 0");
        DBUtil.execute("delete from item_collection_item where item_collection_item_id < 0");
        DBUtil.execute("delete from item_collection where item_collection_id < 0");
        DBUtil.execute("delete from patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_category_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id < 0" );

    def test_OrderSetUsageAnalysis(self):
        # Run the modeling analysis against the mock test data above and verify expected stats afterwards.

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "weightF1-score", "numUsedOrderSets", "numUsedOrderSetItems", "numAvailableOrderSetItems", "numRecommendableUsedOrderSetItems", "numRecommendableQueryVerifyItems"];
        
        expectedResults = \
            [   RowItemModel([-123,  2,2,2,  0.5,   0.5,  0.5,   0.403, 0.551, 0.466, 2, 3,10,  3,13], colNames ),   # Source Items (1,2,3,4,8,9,10,11,12,13,  12,14,15,16). Order Set 1 (1,2,  10,11,12,13).  Order Set 3 (14,  5,6,15)
                RowItemModel([-456,  1,2,6,  0.333, 0.143,0.2,   0.143, 0.073, 0.096, 1, 1, 8,  1, 5], colNames ), # Source Items (4,10,12,77,  12,14,8). Order Set 2 (8,  2,3,5,6,7,  4,  77)   (Order Set includes non-recommendable item 77.  Count for usage rate, but not for recommender accuracy calculations)
                RowItemModel([-789,  0,2,0,  0.0,   None, None,  0.0,   None,  None,  0, 0, 0,  0, 8], colNames ),  # Source Items (1,3,5,9,10,11,  13,15).  No Order Sets
                RowItemModel([-321,  2,2,7,  0.5,   0.222,0.3076,0.4029,0.2075,0.2740,3, 4,15,  4,14], colNames ),   # Source Items (1,2,3,4,8,9,10,11,12,13,  12,14,15,16). Order Set 1 [Query Period not Verify] (1,2,  10,11,12,13).  Order Set 2 (8,  2,3,5,6,7,  4,  77)   Order Set 3 (14,  5,6,15)
            ];
        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OrderSetUsageAnalysis.py", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue();
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


        expectedResults = \
            [   RowItemModel([-123,  1,3,2,  0.25,  0.333,0.286, 0.179, 0.353, 0.238, 2, 3,10, 3,13], colNames ),   # Source Items (1,2,3,4,5,8,9,10,11,12,13,  12,14,15,16). Order Set 1 (1,2,  10,11,12,13).  Order Set 3 (5,15,6,  14,)
                RowItemModel([-456,  1,2,2,  0.333, 0.333,0.333, 0.143, 0.288, 0.191, 1, 1, 8, 1, 5], colNames ), # Source Items (4,10,12,77  12,14,8). Order Set 2 (6,7,8,  2,3,5,  4,  77)
                RowItemModel([-789,  0,2,0,  0.0,   None, None,  0.0,   None,  None,  0, 0, 0, 0, 8], colNames ),  # Source Items (1,3,5,9,10,11,  13,15).  No Order Sets
                RowItemModel([-321,  0,4,3,  0.0,   0.0,  0.0,   0.0,   0.0,   0.0,   3, 4,15, 4,14], colNames ),   # Source Items (1,2,3,4,8,9,10,11,12,13,  12,14,15,16). Order Set 1 (1,2,  10,11,12,13).  Order Set 2 (8,  2,3,5,6,7,  4,  77)   Order Set 3 (14,  5,6,15)
            ];
        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OrderSetUsageAnalysis.py", "-r","3", '-',"-"];   # Default Sort results by item prevalance
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue();
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


        expectedResults = \
            [   RowItemModel([-123,  2,2,1,  0.5,   0.667,0.571, 0.403, 0.730, 0.519, 2, 3,10, 3,13], colNames ),   # Source Items (1,2,3,4,5,8,9,10,11,12,13,  12,14,15,16). Order Set 1 (1,2,  10,11,12,13).  Order Set 3 (5,15,6,  14,)
                RowItemModel([-456,  0,3,3,  0.0,   0.0,  0.0,   0.0,   0.0,   0.0,   1, 1, 8, 1, 5], colNames ), # Source Items (4,10,12,77  12,14,8). Order Set 2 (6,7,8,  2,3,5,  4,  77)
                RowItemModel([-789,  0,2,0,  0.0,   None, None,  0.0,   None,  None,  0, 0, 0, 0, 8], colNames ),  # Source Items (1,3,5,9,10,11,  13,15).  No Order Sets
                RowItemModel([-321,  1,3,2,  0.25,  0.333,0.2857,0.1791,0.2857,0.2201,3, 4,15, 4,14], colNames ),   # Source Items (1,2,3,4,8,9,10,11,12,13,  12,14,15,16). Order Set 1 (1,2,  10,11,12,13).  Order Set 2 (8,  2,3,5,6,7,  4,  77)   Order Set 3 (14,  5,6,15)
            ];
        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.validationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OrderSetUsageAnalysis.py", "-r","3", "-s","name", '-',"-"];   # Sort results by item names
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue();
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


    def test_OrderSetUsageAnalysis_numRecsByOrderSet(self):
        # Only query / recommend one triggered order set at a time, instead of all that occur during the verify time period

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "weightF1-score", "numUsedOrderSets", "numUsedOrderSetItems", "numAvailableOrderSetItems", "numRecommendableUsedOrderSetItems", "numRecommendableAvailableOrderSetItems", "numRecommendableQueryVerifyItems"];
        
        expectedResults = \
            [   RowItemModel([-123,  5,4,1,  0.5555,0.833,0.6666,0.8026,0.9708,0.8787, 1, 2, 6,  2, 6,10], colNames ),   # Verify Items (1,2,3,4,8,9,11,12,13). Order Set 1 (1,2, 10,  11,12,13).
                RowItemModel([-456,  1,1,6,  0.5,   0.143,0.2222,0.2,   0.0727,0.1067, 1, 1, 8,  1, 7, 5], colNames ),   # Verify Items (12,8). Order Set 2 (2,3,5,6,7, 4,8,  77)   (Order Set includes non-recommendable item 77.  Count for usage rate, but not for recommender accuracy calculations)
                RowItemModel([-321,  5,4,1,  0.5555,0.833,0.6666,0.8026,0.9708,0.8787, 1, 2, 6,  2, 6,10], colNames ),   # Verify Items (1,2,3,4,8,9,11,12,13). Order Set 1 (1,2, 10,  11,12,13).
                RowItemModel([-321,  2,2,2,  0.5,   0.5,  0.5,   0.4029,0.5510,0.4655, 1, 1, 4,  1, 4,13], colNames ),   # Verify Items (12,14,15,16). Order Set 3 (5,15,6,  14,)
            ];
        # Analysis via prepared validation data file
        sys.stdin = StringIO(self.orderSetValidationFileStr);   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OrderSetUsageAnalysis.py","--numRecsByOrderSet", '-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        #print >> sys.stderr, sys.stdout.getvalue();
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);



def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestOrderSetUsageAnalysis('test_findOrInsertItem'));
    #suite.addTest(TestOrderSetUsageAnalysis('test_OrderSetUsageAnalysis'));
    #suite.addTest(TestOrderSetUsageAnalysis('test_OrderSetUsageAnalysis_numRecsByOrderSet'));
    suite.addTest(unittest.makeSuite(TestOrderSetUsageAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
