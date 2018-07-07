#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.cpoe.TripleAssociationAnalysis import TripleAssociationAnalysis;

class TestTripleAssociationAnalysis(DBTestCase):
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
                RowItemModel( [-14, -4, "Admit",1], headers ),  # Look for sequences of these
                RowItemModel( [-15, -4, "Discharge",1], headers ),
                RowItemModel( [-16, -4, "Readmit",1], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        headers = ["patient_item_id","encounter_id","patient_id","clinical_item_id","item_date"];
        dataModels = \
            [   
                RowItemModel( [-2,  -111,   -11111, -10, datetime(2000, 1, 1, 0)], headers ),
                RowItemModel( [-3,  -111,   -11111, -8,  datetime(2000, 1, 1, 2)], headers ),
                RowItemModel( [-1,  -111,   -11111, -14, datetime(2000, 1, 1,10)], headers ),   # Admit
                RowItemModel( [-4,  -111,   -11111, -10, datetime(2000, 1, 2, 0)], headers ),
                RowItemModel( [-5,  -111,   -11111, -12, datetime(2000, 2, 1, 0)], headers ),
                RowItemModel( [-6,  -111,   -11111, -15, datetime(2000, 2, 2, 0)], headers ),   # Discharge
                RowItemModel( [-10, -111,   -11111, -11, datetime(2000, 2, 2, 0)], headers ),
                RowItemModel( [-13, -111,   -11111, -10, datetime(2000, 2, 2,10)], headers ),

                RowItemModel( [-7,  -112,   -11111, -9,  datetime(2000, 3, 1, 0)], headers ),
                RowItemModel( [-8,  -112,   -11111, -14, datetime(2000, 3, 1, 1)], headers ),   # Admit
                RowItemModel( [-9,  -112,   -11111, -8,  datetime(2000, 3, 1, 1)], headers ),
                RowItemModel( [-11, -112,   -11111, -15, datetime(2000, 3, 2, 0)], headers ),   # Discharge
                RowItemModel( [-12, -112,   -11111, -7,  datetime(2000, 3, 2, 0)], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("patient_item", dataModel );

        self.analyzer = TripleAssociationAnalysis();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute("delete from clinical_item_link where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
        DBUtil.execute("delete from patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );
        
        DBTestCase.tearDown(self);

    def test_analyzePatientItems(self):
        # Run the association analysis against the mock test data above and verify
        #   expected stats afterwards.
        
        associationQuery = \
            """
            select 
                clinical_item_id, subsequent_item_id, 
                count_0, count_3600, count_86400, count_604800, 
                count_2592000, count_7776000, count_31536000,
                count_any, 
                time_diff_sum, time_diff_sum_squares
            from
                clinical_item_association
            where
                clinical_item_id < 0 and
                count_any > 0
            order by
                clinical_item_id, subsequent_item_id
            """;

        log.debug("Use incremental update, only doing the update based on a part of the data.");
        self.analyzer.analyzePatientItems( [-11111], (-15,-14), -16 );    # Count associations that result in given sequence of items
        
        expectedAssociationStats = \
            [
                [-16,-16,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],  # Need virtual item base counts as well
                [-12,-16,   0, 0, 0, 0, 1, 1, 1, 1,  2509200.0, 2509200.0**2],
                [-11,-16,   0, 0, 0, 0, 1, 1, 1, 1,  2422800.0, 2422800.0**2],
                [-10,-16,   0, 0, 0, 0, 0, 2, 2, 2,  5101200.0+5187600.0, 5101200.0**2+5187600.0**2],
                [ -8,-16,   0, 0, 0, 0, 0, 1, 1, 1,  5180400.0, 5180400.0**2],
            ];
        associationStats = DBUtil.execute(associationQuery);
        self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

        
        # Should record links between surrogate triple items and the sequential items it is based upon
        itemLinkQuery = \
            """
            select 
                clinical_item_id, linked_item_id
            from
                clinical_item_link
            where
                clinical_item_id < 0
            order by
                clinical_item_id, linked_item_id
            """;
        expectedItemLinks = \
            [   [-16, -15],
                [-16, -14],
            ];
        itemLinks = DBUtil.execute(itemLinkQuery);
        self.assertEqualTable( expectedItemLinks, itemLinks );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestTripleAssociationAnalysis("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestTripleAssociationAnalysis("test_insertFile_skipErrors"));
    #suite.addTest(TestTripleAssociationAnalysis('test_executeIterator'));
    #suite.addTest(TestTripleAssociationAnalysis('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestTripleAssociationAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
