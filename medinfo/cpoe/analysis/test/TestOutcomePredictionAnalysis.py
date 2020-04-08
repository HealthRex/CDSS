#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
from datetime import datetime, timedelta;
import unittest

from .Const import RUNNER_VERBOSITY;
from .Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.cpoe.DataManager import DataManager;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender;
from medinfo.cpoe.analysis.OutcomePredictionAnalysis import OutcomePredictionAnalysis, AnalysisQuery;
from medinfo.cpoe.analysis.PreparePatientItems import PreparePatientItems;

class TestOutcomePredictionAnalysis(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        
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
                RowItemModel( [-7, "Admit Dx"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );
            self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

        headers = ["clinical_item_id","clinical_item_category_id","analysis_status","name"];
        dataModels = \
            [   
                RowItemModel( [-1, -1, 1, "CBC"], headers ),
                RowItemModel( [-2, -1, 1, "BMP"], headers ),
                RowItemModel( [-3, -1, 1, "Hepatic Panel"], headers ),
                RowItemModel( [-4, -1, 1, "Cardiac Enzymes"], headers ),
                RowItemModel( [-5, -2, 1, "CXR"], headers ),
                RowItemModel( [-6, -2, 1, "RUQ Ultrasound"], headers ),
                RowItemModel( [-7, -2, 1, "CT Abdomen/Pelvis"], headers ),
                RowItemModel( [-8, -2, 1, "CT PE Thorax"], headers ),
                RowItemModel( [-9, -3, 1, "Acetaminophen"], headers ),
                RowItemModel( [-10, -3, 1, "Carvedilol"], headers ),
                RowItemModel( [-11, -3, 1, "Enoxaparin"], headers ),
                RowItemModel( [-12, -3, 1, "Warfarin"], headers ),
                RowItemModel( [-13, -3, 1, "Ceftriaxone"], headers ),
                RowItemModel( [-14, -4, 1, "Admit"], headers ),
                RowItemModel( [-15, -4, 1, "Discharge"], headers ),
                RowItemModel( [-16, -4, 1, "Readmit"], headers ),
                
                RowItemModel( [-22, -5, 1, "Diagnosis 2"], headers ),
                RowItemModel( [-23, -5, 1, "Diagnosis 3"], headers ),
                RowItemModel( [-24, -5, 1, "Diagnosis 4"], headers ),
                
                RowItemModel( [-30, -6, 1, "Troponin (High)"], headers ),
                RowItemModel( [-31, -6, 1, "BNP (High)"], headers ),
                RowItemModel( [-32, -6, 1, "Creatinine (High)"], headers ),
                RowItemModel( [-33, -6, 1, "ESR (High)"], headers ),

                RowItemModel( [-21, -7, 0, "Diagnosis 1"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        headers = ["patient_item_id","patient_id","clinical_item_id","item_date","analyze_date"];
        dataModels = \
            [   
                RowItemModel( [-52, -11111, -23, datetime(1999, 9, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-51, -11111, -21, datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-1,  -11111, -4,  datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-2,  -11111, -10, datetime(2000, 1, 1, 1), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-3,  -11111, -8,  datetime(2000, 1, 1, 2), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-5,  -11111, -12, datetime(2000, 2, 1, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-60, -11111, -32, datetime(2000, 1, 1, 4), datetime(2010, 1, 1, 0)], headers ),  # Within query time
                RowItemModel( [-61, -11111, -30, datetime(2000, 1, 4, 0), datetime(2010, 1, 1, 0)], headers ),  # Within 1 week
                RowItemModel( [-62, -11111, -31, datetime(2000, 1,10, 0), datetime(2010, 1, 1, 0)], headers ),  # Past 1 week
                
                RowItemModel( [-55, -22222, -21, datetime(2000, 1, 8, 0), datetime(2010, 1, 1, 0)], headers ),  # Admit Dx
                RowItemModel( [-12, -22222, -6,  datetime(2000, 1, 8, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-13, -22222, -14, datetime(2000, 1, 8, 1), datetime(2010, 1, 1, 0)], headers ),  # Admit
                RowItemModel( [-14, -22222, -7,  datetime(2000, 1, 8, 2), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-15, -22222, -8,  datetime(2000, 1, 8, 3), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-16, -22222, -15, datetime(2000, 1, 9, 0), datetime(2010, 1, 1, 0)], headers ),   # Discharge
                RowItemModel( [-56, -22222, -21, datetime(2000, 1,13, 0), datetime(2010, 1, 1, 0)], headers ),  # Admit Dx
                RowItemModel( [-17, -22222, -9,  datetime(2000, 1,13, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-19, -22222, -14, datetime(2000, 1,13, 1), datetime(2010, 1, 1, 0)], headers ),   # Admit (Readmit)
                RowItemModel( [-20, -22222, -10, datetime(2000, 1,13, 2), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-21, -22222, -11, datetime(2000, 1,13, 3), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-22, -22222, -15, datetime(2000, 1,18, 0), datetime(2010, 1, 1, 0)], headers ),   # Discharge
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("patient_item", dataModel );

        headers = \
            [   "clinical_item_id","subsequent_item_id", 
                "count_0","count_3600","count_86400","count_604800","count_any",
                "time_diff_sum", "time_diff_sum_squares",
            ];
        dataModels = \
            [   
                RowItemModel( [ -1, -1,   30, 30, 30, 30, 30,  0.0, 0.0], headers ),
                RowItemModel( [ -2, -2,   30, 30, 30, 30, 30,  0.0, 0.0], headers ),
                RowItemModel( [ -3, -3,   95, 95, 97, 97, 97,  0.0, 0.0], headers ),
                RowItemModel( [ -4, -4,   40, 40, 40, 40, 40,  0.0, 0.0], headers ),
                RowItemModel( [ -5, -5,   40, 40, 50, 50, 50,  0.0, 0.0], headers ),
                RowItemModel( [ -6, -6,   70, 70, 70, 70, 70,  0.0, 0.0], headers ),
                RowItemModel( [ -7, -7,   70, 70, 70, 70, 70,  0.0, 0.0], headers ),
                RowItemModel( [ -8, -8,   35, 35, 35, 50, 80,  0.0, 0.0], headers ),
                RowItemModel( [-10,-10,   45, 45, 55, 60, 90,  0.0, 0.0], headers ),
                RowItemModel( [-12,-12,   75, 75, 75, 80, 90,  0.0, 0.0], headers ),

                RowItemModel( [-14,-14,    100,  100,  100,  100,  100,  0.0, 0.0], headers ),
                RowItemModel( [-15,-15,    100,  100,  100,  100,  100,  0.0, 0.0], headers ),
                RowItemModel( [-16,-16,    30,  30,  30,  30,  30,  0.0, 0.0], headers ),

                RowItemModel( [-30,-30,    3,  3,  3,  3,  3,  0.0, 0.0], headers ),
                RowItemModel( [-31,-31,    4,  4,  4,  4,  4,  0.0, 0.0], headers ),
                RowItemModel( [-32,-32,    4,  4,  4,  4,  4,  0.0, 0.0], headers ),
                RowItemModel( [-33,-33,    5,  5,  5,  5,  5,  0.0, 0.0], headers ),
               
                
                RowItemModel( [ -2, -4,    0,  2,  3,  3,  3,  200.0, 50000.0], headers ),
                RowItemModel( [ -2, -6,    2,  2,  5,  5,  5,  300.0, 11990.0], headers ),
                RowItemModel( [ -3, -1,   20, 23, 23, 23, 23,  400.0, 344990.0], headers ),
                RowItemModel( [ -4, -5,    3,  3, 13, 43, 43,  340.0, 343110.0], headers ),
                RowItemModel( [ -4, -6,   23, 33, 33, 33, 63,  420.0, 245220.0], headers ),
                RowItemModel( [ -4, -7,   27, 33, 33, 33, 63,   40.0, 5420.0], headers ),
                RowItemModel( [ -4,-10,   25, 35, 40, 45, 63,   47.0, 5420.0], headers ),
                RowItemModel( [ -5, -4,    0,  0, 20, 20, 20,  540.0, 54250.0], headers ),

                RowItemModel( [ -6,-16,   10, 10, 10, 10, 10,  0.0, 0.0], headers ),
                RowItemModel( [ -8,-16,   5, 5, 5, 5, 5,  0.0, 0.0], headers ),
                RowItemModel( [-10,-16,   8, 8, 8, 8, 8,  0.0, 0.0], headers ),

                RowItemModel( [-10,-30,   10, 10, 10, 10, 10,  0.0, 0.0], headers ),
                RowItemModel( [-10,-31,   10, 10, 10, 10, 10,  0.0, 0.0], headers ),
                RowItemModel( [-12,-30,   20, 20, 20, 20, 20,  0.0, 0.0], headers ),
                RowItemModel( [-12,-31,   20, 20, 20, 20, 20,  0.0, 0.0], headers ),
                RowItemModel( [-10,-32,   10, 10, 10, 10, 10,  0.0, 0.0], headers ),
                RowItemModel( [-10,-33,   10, 10, 10, 10, 10,  0.0, 0.0], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_association", dataModel );

        # Indicate that cache data needs to be updated
        self.dataManager = DataManager();
        self.dataManager.clearCacheData("analyzedPatientCount");
        self.dataManager.clearCacheData("clinicalItemCountsUpdated");
        
        # Instance to test on
        self.analyzer = OutcomePredictionAnalysis();
        self.preparer = PreparePatientItems();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
        DBUtil.execute("delete from patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );
        
        DBTestCase.tearDown(self);

    def test_recommenderAnalysis(self):
        # Run the recommender against the mock test data above and verify expected stats afterwards.
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-11111]);
        analysisQuery.baseCategoryId = -7;
        analysisQuery.queryTimeSpan = timedelta(0,86400);
        #analysisQuery.recommender = BaselineFrequencyRecommender();
        analysisQuery.recommender = ItemAssociationRecommender();
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.targetItemIds = set([-33,-32,-31,-30]);
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data

        # Initial run without time limits on outcome measure
        colNames = ["patient_id","outcome.-33", "score.-33","outcome.-32", "score.-32","outcome.-31", "score.-31","outcome.-30", "score.-30"];
        expectedResults = [ RowItemModel([-11111,  +0,  0.222,  +2,  0.611,  +1,  0.222, +1, 0.222], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["OutcomePredictionAnalysis.py","-c","-7","-Q","86400","-o","-33,-32,-31,-30","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);
        
        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-c","-7","-Q","86400","-V","86400","-o","-33,-32,-31,-30",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());
        
        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OutcomePredictionAnalysis.py","-P","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);
        
        
        
        
        # Now try with time limitation on outcome measure
        analysisQuery.baseRecQuery.timeDeltaMax = timedelta(0,604800);   # 1 week
        colNames = ["patient_id","outcome.-33", "score.-33","outcome.-32", "score.-32","outcome.-31", "score.-31","outcome.-30", "score.-30"];
        expectedResults = [ RowItemModel([-11111,  +0,  0.222,  +2,  0.611,  +0,  0.222, +1, 0.222], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["OutcomePredictionAnalysis.py","-c","-7","-Q","86400","-t","604800","-o","-33,-32,-31,-30","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-c","-7","-Q","86400","-V","86400","-t","604800","-o","-33,-32,-31,-30",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());
        
        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OutcomePredictionAnalysis.py","-P","-m","0","-R","ItemAssociationRecommender","-t","604800",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);



        # Again, but with much stricter time limit (negative test case)
        analysisQuery.baseRecQuery.timeDeltaMax = timedelta(0,172800);   # 2 day
        colNames = ["patient_id","outcome.-33", "score.-33","outcome.-32", "score.-32","outcome.-31", "score.-31","outcome.-30", "score.-30"];
        expectedResults = [ RowItemModel([-11111, 0, 0.0109, 2, 0.0600, 0, 0.0109, 0, 0.0109], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["OutcomePredictionAnalysis.py","-c","-7","-Q","86400","-t","172800","-o","-33,-32,-31,-30","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-c","-7","-Q","86400","-V","86400","-t","172800","-o","-33,-32,-31,-30",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());
        
        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["OutcomePredictionAnalysis.py","-P","-m","0","-R","ItemAssociationRecommender","-t","172800",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


    def test_tripleSequence_virtualItem(self):
        # Test outcome assessment when the target is a virtual item based on the presence of a triple (instead of double) sequence of items
        # Run the recommender against the mock test data above and verify expected stats afterwards.
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-22222]);
        analysisQuery.baseCategoryId = -7;
        analysisQuery.queryTimeSpan = timedelta(0,86400);
        analysisQuery.sequenceItemIdsByVirtualItemId[-16] = (-15,-14);
        #analysisQuery.recommender = BaselineFrequencyRecommender();
        analysisQuery.recommender = ItemAssociationRecommender();
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.targetItemIds = set([-16]);
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data

        # Initial run without time limits on outcome measure
        colNames = ["patient_id","outcome.-16", "score.-16"];
        expectedResults = [ RowItemModel([-22222,  +1,  0.14286], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);
        
        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["OutcomePredictionAnalysis.py","-c","-7","-Q","86400","-o","-16=-15:-14","-m","0","-R","ItemAssociationRecommender",'0,-22222',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestItemRecommender("test_insertFile_skipErrors"));
    #suite.addTest(TestItemRecommender('test_executeIterator'));
    suite.addTest(TestOutcomePredictionAnalysis('test_recommenderAnalysis'));
    #suite.addTest(unittest.makeSuite(TestOutcomePredictionAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
