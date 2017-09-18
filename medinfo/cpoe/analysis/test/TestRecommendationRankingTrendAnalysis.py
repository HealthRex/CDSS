#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.test.Const import SENTINEL_ANY_FLOAT;
from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender;
from medinfo.cpoe.analysis.RecommendationRankingTrendAnalysis import RecommendationRankingTrendAnalysis, AnalysisQuery;
from medinfo.cpoe.DataManager import DataManager;

class TestRecommendationRankingTrendAnalysis(DBTestCase):
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

        headers = ["clinical_item_id","clinical_item_category_id","name"];
        dataModels = \
            [   
                RowItemModel( [-1, -1, "CBC"], headers ),
                RowItemModel( [-2, -1, "BMP"], headers ),
                RowItemModel( [-3, -1, "Hepatic Panel"], headers ),
                RowItemModel( [-4, -1, "Cardiac Enzymes"], headers ),
                RowItemModel( [-5, -2, "CXR"], headers ),
                RowItemModel( [-6, -2, "RUQ Ultrasound"], headers ),
                RowItemModel( [-7, -2, "CT Abdomen/Pelvis"], headers ),
                RowItemModel( [-8, -2, "CT PE Thorax"], headers ),
                RowItemModel( [-9, -3, "Acetaminophen"], headers ),
                RowItemModel( [-10, -3, "Carvedilol"], headers ),
                RowItemModel( [-11, -3, "Enoxaparin"], headers ),
                RowItemModel( [-12, -3, "Warfarin"], headers ),
                RowItemModel( [-13, -3, "Ceftriaxone"], headers ),
                RowItemModel( [-14, -4, "Foley Catheter"], headers ),
                RowItemModel( [-15, -4, "Strict I&O"], headers ),
                RowItemModel( [-16, -4, "Fall Precautions"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        headers = ["patient_item_id","patient_id","clinical_item_id","item_date","analyze_date"];
        dataModels = \
            [   
                RowItemModel( [-1,  -11111, -4,  datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-2,  -11111, -10, datetime(2000, 1, 1, 1), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-3,  -11111, -8,  datetime(2000, 1, 1, 2), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-4,  -11111, -10, datetime(2000, 1, 2, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-5,  -11111, -12, datetime(2000, 2, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-10, -22222, -7,  datetime(2000, 1, 5, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-12, -22222, -6,  datetime(2000, 1, 9, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-13, -22222, -11, datetime(2000, 1, 9, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-14, -33333, -6,  datetime(2000, 2, 9, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-15, -33333, -2,  datetime(2000, 2,11, 0), datetime(2010, 1, 1, 0)], headers ),
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
                RowItemModel( [ -4, -4,  240,240,240,240,240,  0.0, 0.0], headers ),
                RowItemModel( [ -5, -5,   40, 40, 50, 50, 50,  0.0, 0.0], headers ),
                RowItemModel( [ -6, -6,   70, 70, 70, 70, 70,  0.0, 0.0], headers ),
                RowItemModel( [ -7, -7,   35, 35, 35, 50, 80,  0.0, 0.0], headers ),
                RowItemModel( [ -8, -8,   35, 35, 35, 50, 80,  0.0, 0.0], headers ),
                RowItemModel( [-10,-10,   45, 45, 55, 60, 90,  0.0, 0.0], headers ),
                RowItemModel( [-12,-12,   75, 75, 75, 80, 90,  0.0, 0.0], headers ),

               
                
                RowItemModel( [ -2, -4,    0,  2,  3,  3,  3,  200.0, 50000.0], headers ),
                RowItemModel( [ -2, -6,    2,  2,  5,  5,  5,  300.0, 11990.0], headers ),
                RowItemModel( [ -3, -1,   20, 23, 23, 23, 23,  400.0, 344990.0], headers ),
                RowItemModel( [ -4, -5,    3,  3, 13, 43, 43,  340.0, 343110.0], headers ),
                RowItemModel( [ -4, -6,   23, 33, 33, 33, 63,  420.0, 245220.0], headers ),
                RowItemModel( [ -4, -7,   27, 33, 33, 33, 83,   40.0, 5420.0], headers ),
                RowItemModel( [ -4, -8,    1,  2,  3,  4,  5,   40.0, 5420.0], headers ),
                RowItemModel( [ -4,-10,   25, 35, 40, 45, 73,   47.0, 5420.0], headers ),
                RowItemModel( [ -5, -4,    0,  0, 20, 20, 20,  540.0, 54250.0], headers ),
                RowItemModel( [-10, -8,    2,  4,  6,  8, 10,   47.0, 5420.0], headers ),
                RowItemModel( [-10, -12,  12, 14, 16, 18, 20,   47.0, 5420.0], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_association", dataModel );

        # Indicate that cache data needs tobe updated
        self.dataManager = DataManager();
        self.dataManager.clearCacheData("analyzedPatientCount");
        self.dataManager.clearCacheData("clinicalItemCountsUpdated");

        # Instance to test on
        self.analyzer = RecommendationRankingTrendAnalysis();

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
        analysisQuery.recommender = BaselineFrequencyRecommender();
        #analysisQuery.recommender = ItemAssociationRecommender();
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data

        # Don't use items whose default is to be excluded from recommendations
        #recQuery.excludeCategoryIds = recommender.defaultExcludedClinicalItemCategoryIds(conn=conn);
        #recQuery.excludeItemIds = recommender.defaultExcludedClinicalItemIds(conn=conn);
        #recQuery.timeDeltaMax = timedelta(0, int(self.requestData["timeDeltaMax"]) );  # Time delta to use for queries, otherwise just default to all times

        colNames = ["patient_id", "clinical_item_id", "iItem", "iRecItem", "recRank", "recScore"];
        
        # Start with default recommender
        expectedResults = \
            [
                (-11111, -4, 0, 0, 1, SENTINEL_ANY_FLOAT),    #0.170),    Don't care about specific scores, as long as ranks are correct
                (-11111,-10, 1, 1, 4, SENTINEL_ANY_FLOAT),    #0.032),
                (-11111, -8, 2, 2, 5, SENTINEL_ANY_FLOAT),    #0.025),
                (-11111,-12, 4, 3, 2, SENTINEL_ANY_FLOAT),    #0.053),
            ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualTable(expectedResults, analysisResults, 3);

        # Now try targeted recommender
        analysisQuery.recommender = ItemAssociationRecommender();
        expectedResults = \
            [   (-11111, -4, 0, 0, 1, SENTINEL_ANY_FLOAT),    #0.167),
                (-11111,-10, 1, 1, 2, SENTINEL_ANY_FLOAT),    #0.304),
                (-11111, -8, 2, 2, 5, SENTINEL_ANY_FLOAT),    #0.190),
                (-11111,-12, 4, 3, 1, SENTINEL_ANY_FLOAT),    #0.444),
            ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualTable(expectedResults, analysisResults, 3);

        # Repeat, but put a limit on maximum number of query items and recommendations we want analyzed
        analysisQuery.queryItemMax = 2;
        expectedResults = \
            [   (-11111, -4, 0, 0, 1, SENTINEL_ANY_FLOAT),    #0.167),
                (-11111,-10, 1, 1, 2, SENTINEL_ANY_FLOAT),    #0.304),
            ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualTable(expectedResults, analysisResults, 3);


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestItemRecommender("test_insertFile_skipErrors"));
    #suite.addTest(TestItemRecommender('test_executeIterator'));
    #suite.addTest(TestItemRecommender('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestRecommendationRankingTrendAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
