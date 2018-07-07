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

from medinfo.cpoe.TopicModel import TopicModel;

TEST_FILE_PREFIX = "TestTopicModel.model";
ITEMS_PER_TOPIC = 5;

class TestTopicModel(DBTestCase):
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
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );
            self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

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

        # Input file contents in Bag-of-Words formats
        # Specifically avoid the use of items 6 or 7 in the training data
        self.inputBOWFileStr = \
"""[[1,1],[2,2],[3,1],[4,4],[5,10],[8,5]]
[[3,4],[4,4],[9,3],[10,2],[12,6],[13,3],[15,5],[16,8]]
[[1,1],[2,2],[3,1],[4,4],[5,10],[8,5],[9,1],[10,2],[11,1],[12,4],[13,10],[14,1],[15,3],[16,5]]
[[1,4],[2,9],[9,1],[10,2],[11,7],[12,4],[13,2],[16,6]]
[[4,3],[5,31],[8,5],[12,6],[13,8],[16,5]]
"""
        self.instance = TopicModel();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")
        DBUtil.execute("delete from clinical_item where clinical_item_category_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );
        
        for filename in os.listdir("."):
            if filename.startswith(TEST_FILE_PREFIX) or filename.startswith("HDP"+TEST_FILE_PREFIX):
                os.remove(filename);
        
        DBTestCase.tearDown(self);

    def test_topicModel(self):
        # Run the modeling analysis against the mock test data above and verify expected stats afterwards.

        numTopics = 3;
        sys.stdin = StringIO(self.inputBOWFileStr);
        subargv = ["TopicModel", "-n", str(numTopics), "-i",str(ITEMS_PER_TOPIC), "-", TEST_FILE_PREFIX];
        self.instance.main(subargv);
        
        model = self.instance.loadModel(TEST_FILE_PREFIX);
        topTopicFile = open(self.instance.topTopicFilename(TEST_FILE_PREFIX));

        expectedDocCountByWordId = \
                {1:3, 2:3, 3:3, 4:4, 5:3, None:5, 9:3, 10:3, 11:2, 12:4, 13:4, 14:1, 15:2, 16:4, 8:3}
        self.assertExpectedTopItems( expectedDocCountByWordId, model, topTopicFile );
        
        
        # Do again but with HDP non-parametric model
        numTopics = 0;
        sys.stdin = StringIO(self.inputBOWFileStr);
        subargv = ["TopicModel", "-n", str(numTopics), "-i",str(ITEMS_PER_TOPIC), "-", "HDP"+TEST_FILE_PREFIX];
        self.instance.main(subargv);
        
        model = self.instance.loadModel("HDP"+TEST_FILE_PREFIX);
        topTopicFile = open(self.instance.topTopicFilename("HDP"+TEST_FILE_PREFIX));

        expectedDocCountByWordId = \
                {1:3, 2:3, 3:3, 4:4, 5:3, None:5, 9:3, 10:3, 11:2, 12:4, 13:4, 14:1, 15:2, 16:4, 8:3}
        self.assertExpectedTopItems( expectedDocCountByWordId, model, topTopicFile );

    def assertExpectedTopItems(self, expectedDocCountByWordId, model, topTopicFile):
        # With randomized optimization algorithm, cannot depend on stable
        # Test results with each run.  Instead make sure internally consistent,
        #   and that raw count data is consistent
        
        # Values from model topic parameters
        scoreByItemIdByTopicId = dict();
        for (topicId, topicItems) in self.instance.enumerateTopics(model, ITEMS_PER_TOPIC):
            scoreByItemIdByTopicId[topicId] = dict();
            for (itemId, score) in topicItems:
                scoreByItemIdByTopicId[topicId][itemId] = score;
        # Add expected word document counts under the "None" topic
        scoreByItemIdByTopicId[None] = expectedDocCountByWordId;
        
        # Verify Top Topic Files match
        topScoreByItemIdByTopicId = dict();
        itemsChecked = 0;
        reader = TabDictReader(topTopicFile);
        for topicItem in reader:
            topicId = None;
            if topicItem["topic_id"] != NULL_STRING:
                topicId = int(topicItem["topic_id"])
            itemId = None;
            if topicItem["item_id"] != NULL_STRING:
                itemId = int(topicItem["item_id"]);
            score = float(topicItem["score"]);
            tfidf = float(topicItem["tfidf"]);
            
            expectedTFIDF = 0.0;
            if itemId in expectedDocCountByWordId and expectedDocCountByWordId[itemId] > 0:
                expectedTFIDF = score * expectedDocCountByWordId[None] / expectedDocCountByWordId[itemId];
            
            #print >> sys.stderr, topicId, itemId, score, tfidf, expectedDocCountByWordId[itemId]
            self.assertAlmostEqual(expectedTFIDF, tfidf);
                
            if topicId not in topScoreByItemIdByTopicId:
                topScoreByItemIdByTopicId[topicId] = dict();
            topScoreByItemIdByTopicId[topicId][itemId] = score;
            itemsChecked += 1;
        self.assertTrue( itemsChecked > 0 );    # Make sure an actual test happened

        for topicId, topScoreByItemId in topScoreByItemIdByTopicId.iteritems():
            scoreByItemId = scoreByItemIdByTopicId[topicId];
            self.assertAlmostEqualsDict( topScoreByItemId, scoreByItemId );

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestTopicModel("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestTopicModel("test_insertFile_skipErrors"));
    #suite.addTest(TestTopicModel('test_executeIterator'));
    #suite.addTest(TestTopicModel('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestTopicModel));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
