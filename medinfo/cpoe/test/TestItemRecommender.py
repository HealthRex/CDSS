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
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, RecommenderQuery;
from medinfo.cpoe.ItemRecommender import SIMULATED_PATIENT_COUNT;

DELTA_HOUR = timedelta(0,60*60);

class TestItemRecommender(DBTestCase):
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

        headers = \
            [   "clinical_item_id","subsequent_item_id",
                "patient_count_0","patient_count_3600","patient_count_86400","patient_count_604800","patient_count_any",
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


                RowItemModel( [ -2, -3,    0,  0,  0,  0,  0,    0.0,     0.0], headers ),  # Zero count associations, probably shouldn't even be here. If so, ignore them anyway
                RowItemModel( [ -2, -4,    0,  2,  3,  3,  3,  200.0, 50000.0], headers ),
                RowItemModel( [ -2, -6,    2,  2,  5,  5,  5,  300.0, 11990.0], headers ),
                RowItemModel( [ -3, -1,   20, 23, 23, 23, 23,  400.0, 344990.0], headers ),
                RowItemModel( [ -4, -5,    3,  3, 13, 43, 43,  340.0, 343110.0], headers ),
                RowItemModel( [ -4, -6,   23, 33, 33, 33, 63,  420.0, 245220.0], headers ),
                RowItemModel( [ -4, -7,   23, 33, 33, 33, 63,   40.0, 5420.0], headers ),
                RowItemModel( [ -5, -4,    0,  0, 20, 20, 20,  540.0, 54250.0], headers ),

                RowItemModel( [ -6, -2,    7,   7,   7,   7,   7,  1.0, 1.0], headers ),
                RowItemModel( [ -6, -4,   20,  20,  20,  20,  20,  1.0, 1.0], headers ),
            ];
        for dataModel in dataModels:
            # Add non patient_count variations (Adding 5 to values that are >5 and not for the zero time interval)
            for header in headers:
                if header.startswith("patient_count_"):
                    timeStr = header[len("patient_count_"):];
                    dataModel["count_%s" % timeStr] = dataModel[header];    # Copy over value

                    if timeStr != "0" and dataModel[header] > 5:
                        dataModel["count_%s" % timeStr] += 5;
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_association", dataModel );

        # Indicate that cache data needs to be updated
        self.dataManager = DataManager();
        self.dataManager.clearCacheData("analyzedPatientCount");
        self.dataManager.clearCacheData("clinicalItemCountsUpdated");

        self.recommender = ItemAssociationRecommender();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
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
        query.limit = 3;    # Just get top 3 ranks for simplicity
        query.maxRecommendedId = 0; # Artificial constraint to focus only on test data

        log.debug("Query with no item key input, just return ranks by general likelihood then.");
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-3], headers ),
                RowItemModel( [-6], headers ),
                RowItemModel( [-5], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("Query with key item inputs for which no data exists.  Effecitvely ignore it then, so just return ranks by general likelihood.");
        query.queryItemIds = set([-100]);
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-3], headers ),
                RowItemModel( [-6], headers ),
                RowItemModel( [-5], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("Query with category filter on recommended results.");
        query.queryItemIds = set([-100]);
        query.excludeCategoryIds = set([-1,-4,-5,-6]);
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-6], headers ),
                RowItemModel( [-5], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("Query with category filter and specific exclusion filter on recommended results.");
        query.queryItemIds = set([-100]);
        query.excludeItemIds = set([-6]);
        query.excludeCategoryIds = set([-1,-4,-5,-6]);
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-5], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );


        log.debug("General query with a couple of input clinical items + one with no association data (should effectively be ignored).");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set();
        query.excludeCategoryIds = set();
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-4], headers ),
                RowItemModel( [-6], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("General query but set a limit on time delta worth counting item associations");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set();
        query.excludeCategoryIds = set();
        query.timeDeltaMax = DELTA_HOUR;
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-6], headers ),
                RowItemModel( [-4], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("General query with category limit");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set();
        query.excludeCategoryIds = set([-2,-4,-5,-6]);
        query.timeDeltaMax = DELTA_HOUR;
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-4], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        log.debug("General query with specific exclusion");
        query.queryItemIds = set([-2,-5,-100]);
        query.excludeItemIds = set([-4,-3,-2]);
        query.excludeCategoryIds = set();
        query.timeDeltaMax = DELTA_HOUR;
        headers = ["clinical_item_id"];
        expectedData = \
            [   RowItemModel( [-6], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

    def test_recommender_aggregation(self):
        # Test different scoring aggregation methods

        query = RecommenderQuery();
        query.countPrefix = "patient_";
        query.queryItemIds = set([-2,-5]);
        #query.excludeItemIds = set();
        #query.categoryIds = set();
        #query.timeDeltaMax = None;   # If set to one of the constants (DELTA_ZERO, DELTA_HOUR, etc.), will count item associations that occurred within that time delta as co-occurrent.  If left blank, will just consider all items within a given patient as co-occurrent.
        query.limit = 3;    # Just get top 3 ranks for simplicity
        query.maxRecommendedId = 0; # Artificial constraint to focus only on test data

        headers = ["clinical_item_id","conditionalFreq","freqRatio"];

        # Default weighted aggregation method
        expectedData = \
            [   RowItemModel( [-4, 0.3,    22.5], headers ),
                RowItemModel( [-6, 0.16667, 7.142857], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        # Change to unweighted aggregation method
        query.aggregationMethod = "unweighted";
        expectedData = \
            [   RowItemModel( [-4, 0.32857, 24.64286], headers ),
                RowItemModel( [-6, 0.16667,  7.142857], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        # Change to Serial Bayes aggregation method
        query.aggregationMethod = "SerialBayes";
        expectedData = \
            [   RowItemModel( [-4, 0.89157, 66.867471], headers ),
                RowItemModel( [-6, 0.16667,  7.142857], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        # Naive Bayes aggregation
        query.aggregationMethod = "NaiveBayes";
        expectedData = \
            [   RowItemModel( [-4, 3.75,   281.25], headers ),      # Without truncating negative values
                #RowItemModel( [-4, 0.8,    58.59707], headers ),   # With truncating negative values
                RowItemModel( [-6, 0.16667, 7.142857], headers ),
            ];
        recommendedData = self.recommender( query );

        self.assertEqualRecommendedData( expectedData, recommendedData, query );

        # Apply value filter
        query.fieldFilters["freqRatio>"] = 10.0;
        expectedData = \
            [   RowItemModel( [-6, 0.16667, 7.142857], headers ),
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
            # Ensure derived statistics are populated to enable comparisons
            ItemAssociationRecommender.populateDerivedStats( recommendedItem, expectedItem.keys() );

            self.assertEqualDict(expectedItem, recommendedItem, ["clinical_item_id"]);
            for key in expectedItem.iterkeys():  # If specified, then verify a specific values
                if isinstance(expectedItem[key],float):
                    self.assertAlmostEquals(expectedItem[key], recommendedItem[key], 5);
                else:
                    self.assertEqual(expectedItem[key], recommendedItem[key]);
            if lastScore is not None:
                self.assertTrue( recommendedItem[query.sortField] <= lastScore );    # Verify descending order of scores
            lastScore = recommendedItem[query.sortField];

        self.assertEqual( len(expectedData), len(recommendedData) );

    def test_recommender_stats(self):
        # Run the recommender against the mock test data above and verify expected stats calculations

        query = RecommenderQuery();
        query.parseParams \
        (   {   "countPrefix": "patient_",
                "queryItemIds": "-6",
                "resultCount": "3",    # Just get top 3 ranks for simplicity
                "maxRecommendedId": "0", # Artificial constraint to focus only on test data
                "sortField": "P-Fisher",   # Specifically request derived expected vs. observed stats
            }
        );

        log.debug("Query with single item not perturbed by others.");
        headers = ["clinical_item_id","N","nB","nA","nAB","conditionalFreq","baselineFreq","freqRatio","P-Fisher"];
        expectedData = \
            [
                RowItemModel( [-2, SIMULATED_PATIENT_COUNT, 30.0, 70.0,  7.0,  0.1,    0.0100, 10.0,       3.7e-06], headers ),
                RowItemModel( [-4, SIMULATED_PATIENT_COUNT, 40.0, 70.0, 20.0,  0.286,  0.0133, 21.42857,   1.2e-23], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedDataStats( expectedData, recommendedData, headers );

        log.debug("Query for non-unique counts.");
        query.parseParams \
        (   {   "countPrefix": "",
                "sortField": "oddsRatio",
            }
        );
        headers = ["clinical_item_id","N","nB","nA","nAB","conditionalFreq","baselineFreq","freqRatio","oddsRatio"];
        expectedData = \
            [   RowItemModel( [-4, SIMULATED_PATIENT_COUNT, 40.0, 70.0, 25.0,  0.35714, 0.01333,  26.7857, 107.96296], headers ),
                RowItemModel( [-2, SIMULATED_PATIENT_COUNT, 30.0, 70.0, 12.0,  0.1714,  0.01,     17.1429,  33.47126], headers ),
            ];
        recommendedData = self.recommender( query );
        self.assertEqualRecommendedDataStats( expectedData, recommendedData, headers );

    def assertEqualRecommendedDataStats(self, expectedData, recommendedData, headers):
        """Run assertEqualGeneral on the key components of the contents of the recommendation data.
        In this case, we do want to verify actual score / stat values match
        """
        self.assertEqual( len(expectedData), len(recommendedData) );
        for expectedItem, recommendedItem in zip(expectedData, recommendedData):
            # Ensure the recommendedData has all fields of interest populated / calculated
            ItemAssociationRecommender.populateDerivedStats( recommendedItem, headers );
            for header in headers:
                expectedValue = expectedItem[header];
                recommendedValue = recommendedItem[header];
                msg = 'Dicts diff with key (%s).  Verify = %s, Sample = %s' % (header, expectedValue, recommendedValue);
                self.assertAlmostEquals(expectedValue, recommendedValue, 3, msg);

    def test_recommender_stats_commandline(self):
        # Run the recommender against the mock test data above and verify expected stats calculations
        log.debug("Query with single item not perturbed by others.");
        headers = ["clinical_item_id","N","nB","nA","nAB","conditionalFreq","baselineFreq","freqRatio","P-Fisher"];
        expectedData = \
            [
                RowItemModel( [-2, SIMULATED_PATIENT_COUNT, 30.0, 70.0,  7.0,  0.1,    0.0100, 10.0,       3.7e-06], headers ),
                RowItemModel( [-4, SIMULATED_PATIENT_COUNT, 40.0, 70.0, 20.0,  0.286,  0.0133, 21.42857,   1.2e-23], headers ),
            ];
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["ItemRecommender.py","maxRecommendedId=0&queryItemIds=-6&countPrefix=patient_&resultCount=3&sortField=P-Fisher","-"];
        self.recommender.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualRecommendedDataStatsTextOutput( expectedData, textOutput, headers );

        log.debug("Query for non-unique counts.");
        headers = ["clinical_item_id","N","nB","nA","nAB","conditionalFreq","baselineFreq","freqRatio","oddsRatio"];
        expectedData = \
            [   RowItemModel( [-4, SIMULATED_PATIENT_COUNT, 40.0, 70.0, 25.0,  0.35714, 0.01333,  26.7857, 107.96296], headers ),
                RowItemModel( [-2, SIMULATED_PATIENT_COUNT, 30.0, 70.0, 12.0,  0.1714,  0.01,     17.1429,  33.47126], headers ),
            ];
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["ItemRecommender.py","maxRecommendedId=0&queryItemIds=-6&countPrefix=&resultCount=3&sortField=oddsRatio","-"];
        self.recommender.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualRecommendedDataStatsTextOutput( expectedData, textOutput, headers );

    def assertEqualRecommendedDataStatsTextOutput(self, expectedData, textOutput, headers):
        """Run assertEqualGeneral on the key components of the contents of the recommendation data.
        In this case, we do want to verify actual score / stat values match
        """
        recommendedData = list();
        for dataRow in TabDictReader(textOutput):
            for key,value in dataRow.iteritems():
                if key in headers:
                    dataRow[key] = float(value);    # Parse into numerical values for comparison
            recommendedData.append(dataRow);
        self.assertEqualRecommendedDataStats( expectedData, recommendedData, headers );


    def test_dataCache(self):
        # Test that repeating queries with cache turned on will not result in extra DB queries
        query = RecommenderQuery();
        query.countPrefix = "patient_";
        query.queryItemIds = set([-2,-5]);
        #query.excludeItemIds = set();
        #query.categoryIds = set();
        #query.timeDeltaMax = None;   # If set to one of the constants (DELTA_ZERO, DELTA_HOUR, etc.), will count item associations that occurred within that time delta as co-occurrent.  If left blank, will just consider all items within a given patient as co-occurrent.
        query.limit = 3;    # Just get top 3 ranks for simplicity
        query.maxRecommendedId = 0; # Artificial constraint to focus only on test data

        headers = ["clinical_item_id","conditionalFreq","freqRatio"];

        # First query without cache
        self.recommender.dataManager.dataCache = None;
        baselineData = self.recommender( query );
        baselineQueryCount = self.recommender.dataManager.queryCount;

        # Redo query with cache
        self.recommender.dataManager.dataCache = dict();
        newData = self.recommender( query );
        newQueryCount = self.recommender.dataManager.queryCount;
        self.assertEqualRecommendedData( baselineData, newData, query );    # Ensure getting same results
        self.assertNotEqual( baselineQueryCount, newQueryCount );  # Expect needed more queries since no prior cache
        baselineQueryCount = newQueryCount;

        # Again, but should be no new query since have cached results last time
        newData = self.recommender( query );
        newQueryCount = self.recommender.dataManager.queryCount;
        self.assertEqualRecommendedData( baselineData, newData, query );
        self.assertEqual( baselineQueryCount, newQueryCount );

        # Repeat multiple times, should still have no new query activity
        # prog = ProgressDots(10,1,"repeats");
        for iRepeat in xrange(10):
            newData = self.recommender( query );
            newQueryCount = self.recommender.dataManager.queryCount;
            self.assertEqualRecommendedData( baselineData, newData, query );
            self.assertEqual( baselineQueryCount, newQueryCount );
            # prog.update();
        # prog.printStatus();

        # Query for subset should still yield no new query
        query.queryItemIds = set([-2]);
        newData = self.recommender( query );
        newQueryCount = self.recommender.dataManager.queryCount;
        baselineData = newData; # New baseline for subset
        self.assertEqual( baselineQueryCount, newQueryCount );  # Expect no queries for subsets

        # Repeat query for subset
        newData = self.recommender( query );
        newQueryCount = self.recommender.dataManager.queryCount;
        self.assertEqualRecommendedData( baselineData, newData, query );
        self.assertEqual( baselineQueryCount, newQueryCount );  # Expect no queries for subsets



        # Query for partial subset, partial new
        query.queryItemIds = set([-5,-6]);
        newData = self.recommender( query );
        newQueryCount = self.recommender.dataManager.queryCount;
        baselineData = newData; # New baseline for subset
        self.assertEqual( baselineQueryCount, newQueryCount );  # Expect now new queries for subsets, because first query should have done mass-all query

        # Repeat for partial subset, no longer new
        newData = self.recommender( query );
        newQueryCount = self.recommender.dataManager.queryCount;
        baselineData = newData; # New baseline for subset
        self.assertEqualRecommendedData( baselineData, newData, query );
        self.assertEqual( baselineQueryCount, newQueryCount );  # Expect no queries for subsets

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestItemRecommender("test_insertFile_skipErrors"));
    #suite.addTest(TestItemRecommender('test_executeIterator'));
    #suite.addTest(TestItemRecommender('test_recommender'));
    #suite.addTest(TestItemRecommender('test_recommender_aggregation'));
    #suite.addTest(TestItemRecommender('test_recommender_stats'));
    #suite.addTest(TestItemRecommender('test_recommender_stats_commandline'));
    #suite.addTest(TestItemRecommender('test_dataCache'));
    suite.addTest(unittest.makeSuite(TestItemRecommender));

    return suite;

if __name__=="__main__":
    log.setLevel(LOGGER_LEVEL)

    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
