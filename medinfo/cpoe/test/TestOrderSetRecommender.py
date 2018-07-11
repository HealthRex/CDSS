#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta;
import unittest

from Const import LOGGER_LEVEL, RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.Util import ProgressDots;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.cpoe.DataManager import DataManager;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.OrderSetRecommender import OrderSetRecommender;

DELTA_HOUR = timedelta(0,60*60);

class TestOrderSetRecommender(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();

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
                RowItemModel( [-2,  -11111, -10, datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
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

        self.recommender = OrderSetRecommender();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute("delete from item_collection_item where item_collection_item_id < 0");
        DBUtil.execute("delete from item_collection where item_collection_id < 0");
        DBUtil.execute("delete from patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );

        DBTestCase.tearDown(self);

    def test_recommender(self):
        # Run the recommender against the mock test data above and verify expected stats afterwards.

        query = RecommenderQuery();
        #query.queryItemIds = set();
        #query.excludeItemIds = set();
        #query.categoryIds = set();
        #query.timeDeltaMax = None;   # If set to one of the constants (DELTA_ZERO, DELTA_HOUR, etc.), will count item associations that occurred within that time delta as co-occurrent.  If left blank, will just consider all items within a given patient as co-occurrent.
        query.sortField = "tf";
        query.limit = 16;    # Go ahead and query for all since short list and can get expected calculation results for all
        query.maxRecommendedId = 0; # Artificial constraint to focus only on test data

        log.debug("Query with no item key input, just return ranks by general likelihood then.");
        headers = ["clinical_item_id","score"];
        expectedData = \
            [   RowItemModel( [-2, 2.0/13], headers ),
                RowItemModel( [-5, 2.0/13], headers ),
                RowItemModel( [-6, 2.0/13], headers ),
                RowItemModel( [-1, 1.0/13], headers ),
                RowItemModel( [-3, 1.0/13], headers ),
                RowItemModel( [-7, 1.0/13], headers ),
                RowItemModel( [-8, 1.0/13], headers ),
                RowItemModel( [-10,1.0/13], headers ),
                RowItemModel( [-11,1.0/13], headers ),
                RowItemModel( [-12,1.0/13], headers ),
                RowItemModel( [-13,1.0/13], headers ),
                RowItemModel( [-14,1.0/13], headers ),
                RowItemModel( [-15,1.0/13], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("Query with key item inputs for which no data exists.  Effecitvely ignore it then, so just return ranks by general likelihood.");
        query.queryItemIds = set([-100]);
        expectedData = \
            [   RowItemModel( [-2, 2.0/13], headers ),
                RowItemModel( [-5, 2.0/13], headers ),
                RowItemModel( [-6, 2.0/13], headers ),
                RowItemModel( [-1, 1.0/13], headers ),
                RowItemModel( [-3, 1.0/13], headers ),
                RowItemModel( [-7, 1.0/13], headers ),
                RowItemModel( [-8, 1.0/13], headers ),
                RowItemModel( [-10,1.0/13], headers ),
                RowItemModel( [-11,1.0/13], headers ),
                RowItemModel( [-12,1.0/13], headers ),
                RowItemModel( [-13,1.0/13], headers ),
                RowItemModel( [-14,1.0/13], headers ),
                RowItemModel( [-15,1.0/13], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("Query with category filter on recommended results.");
        query.queryItemIds = set([-100]);
        query.excludeCategoryIds = set([-1,-4,-5,-6]);
        expectedData = \
            [   #RowItemModel( [-2, 2.0/13], headers ),
                RowItemModel( [-5, 2.0/13], headers ),
                RowItemModel( [-6, 2.0/13], headers ),
                #RowItemModel( [-1, 1.0/13], headers ),
                #RowItemModel( [-3, 1.0/13], headers ),
                RowItemModel( [-7, 1.0/13], headers ),
                RowItemModel( [-8, 1.0/13], headers ),
                RowItemModel( [-10,1.0/13], headers ),
                RowItemModel( [-11,1.0/13], headers ),
                RowItemModel( [-12,1.0/13], headers ),
                RowItemModel( [-13,1.0/13], headers ),
                #RowItemModel( [-14,1.0/13], headers ),
                #RowItemModel( [-15,1.0/13], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("Query with category filter and specific exclusion filter on recommended results.");
        query.queryItemIds = set([-100]);
        query.excludeItemIds = set([-6,-10]);
        query.excludeCategoryIds = set([-1,-4,-5,-6]);
        expectedData = \
            [   #RowItemModel( [-2, 2.0/13], headers ),
                RowItemModel( [-5, 2.0/13], headers ),
                #RowItemModel( [-6, 2.0/13], headers ),
                #RowItemModel( [-1, 1.0/13], headers ),
                #RowItemModel( [-3, 1.0/13], headers ),
                RowItemModel( [-7, 1.0/13], headers ),
                RowItemModel( [-8, 1.0/13], headers ),
                #RowItemModel( [-10,1.0/13], headers ),
                RowItemModel( [-11,1.0/13], headers ),
                RowItemModel( [-12,1.0/13], headers ),
                RowItemModel( [-13,1.0/13], headers ),
                #RowItemModel( [-14,1.0/13], headers ),
                #RowItemModel( [-15,1.0/13], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );


        log.debug("General query with a couple of input clinical items + one with no association data (should effectively be ignored).");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set();
        query.excludeCategoryIds = set();
        expectedData = \
            [   RowItemModel( [-6, (1.0/6)*(2.0/2)+(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-5, (1.0/6)*(2.0/2)+(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-2, (1.0/6)*(1.0/2)+(1.0/6)*(2.0/2)], headers ),

                RowItemModel( [-3, (1.0/6)*(2.0/2)], headers ),
                RowItemModel( [-7, (1.0/6)*(2.0/2)], headers ),
                RowItemModel( [-8, (1.0/6)*(2.0/2)], headers ),

                RowItemModel( [-14,(1.0/4)*(1.0/2)], headers ),
                RowItemModel( [-15,(1.0/4)*(1.0/2)], headers ),

                RowItemModel( [-1, (1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-10,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-11,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-12,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-13,(1.0/6)*(1.0/2)], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("General query with category limit");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set();
        query.excludeCategoryIds = set([-2,-4,-5,-6]);
        expectedData = \
            [   #RowItemModel( [-6, (1.0/6)*(2.0/2)+(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-5, (1.0/6)*(2.0/2)+(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-2, (1.0/6)*(1.0/2)+(1.0/6)*(2.0/2)], headers ),

                RowItemModel( [-3, (1.0/6)*(2.0/2)], headers ),
                #RowItemModel( [-7, (1.0/6)*(2.0/2)], headers ),
                #RowItemModel( [-8, (1.0/6)*(2.0/2)], headers ),

                #RowItemModel( [-14,(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-15,(1.0/4)*(1.0/2)], headers ),

                RowItemModel( [-1, (1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-10,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-11,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-12,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-13,(1.0/6)*(1.0/2)], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("General query with specific exclusion");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set([-4,-3,-2]);
        query.excludeCategoryIds = set();
        expectedData = \
            [   RowItemModel( [-6, (1.0/6)*(2.0/2)+(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-5, (1.0/6)*(2.0/2)+(1.0/4)*(1.0/2)], headers ),
                #RowItemModel( [-2, (1.0/6)*(1.0/2)+(1.0/6)*(2.0/2)], headers ),

                #RowItemModel( [-3, (1.0/6)*(2.0/2)], headers ),
                RowItemModel( [-7, (1.0/6)*(2.0/2)], headers ),
                RowItemModel( [-8, (1.0/6)*(2.0/2)], headers ),

                RowItemModel( [-14,(1.0/4)*(1.0/2)], headers ),
                RowItemModel( [-15,(1.0/4)*(1.0/2)], headers ),

                RowItemModel( [-1, (1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-10,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-11,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-12,(1.0/6)*(1.0/2)], headers ),
                RowItemModel( [-13,(1.0/6)*(1.0/2)], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );



        log.debug("General query, sort by TF*IDF lift.");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set();
        query.excludeCategoryIds = set();
        query.sortField = "lift";
        expectedData = \
            [   #RowItemModel( [-5, (13.0/2)*((1.0/6)*(2.0/2)+(1.0/4)*(1.0/2))], headers ),
                #RowItemModel( [-2, (13.0/2)*((1.0/6)*(1.0/2)+(1.0/6)*(2.0/2))], headers ),

                RowItemModel( [-3, (13.0/1)*((1.0/6)*(2.0/2))], headers ),
                RowItemModel( [-7, (13.0/1)*((1.0/6)*(2.0/2))], headers ),
                RowItemModel( [-8, (13.0/1)*((1.0/6)*(2.0/2))], headers ),

                RowItemModel( [-6, (13.0/2)*((1.0/6)*(2.0/2)+(1.0/4)*(1.0/2))], headers ),

                RowItemModel( [-14,(13.0/1)*((1.0/4)*(1.0/2))], headers ),
                RowItemModel( [-15,(13.0/1)*((1.0/4)*(1.0/2))], headers ),

                RowItemModel( [-1, (13.0/1)*((1.0/6)*(1.0/2))], headers ),
                RowItemModel( [-10,(13.0/1)*((1.0/6)*(1.0/2))], headers ),
                RowItemModel( [-11,(13.0/1)*((1.0/6)*(1.0/2))], headers ),
                RowItemModel( [-12,(13.0/1)*((1.0/6)*(1.0/2))], headers ),
                RowItemModel( [-13,(13.0/1)*((1.0/6)*(1.0/2))], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

    def assertEqualRecommendedData(self, expectedData, recommendedData, query):
        """Run assertEqualGeneral on the key components of the contents of the recommendation data.
        Don't necessarily care about the specific numbers that come out of the recommendations,
        but do care about consistency in rankings and relative order by the query.sortField
        """
        lastScore = None;
        for expectedItem, recommendedItem in zip(expectedData, recommendedData):
            for key in expectedItem.iterkeys():  # If specified, then verify a specific values
                if isinstance(expectedItem[key],float):
                    self.assertAlmostEquals(expectedItem[key], recommendedItem[key], 5);
                else:
                    self.assertEqual(expectedItem[key], recommendedItem[key]);
            if lastScore is not None:
                self.assertTrue( recommendedItem[query.sortField] <= lastScore );    # Verify descending order of scores
            lastScore = recommendedItem[query.sortField];
        self.assertEqual( len(expectedData), len(recommendedData) );



def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestOrderSetRecommender('test_recommender'));
    suite.addTest(unittest.makeSuite(TestOrderSetRecommender));

    return suite;

if __name__=="__main__":
    log.setLevel(LOGGER_LEVEL)
    
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
