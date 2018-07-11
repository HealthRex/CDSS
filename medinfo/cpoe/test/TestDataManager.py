#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import LOGGER_LEVEL, RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.cpoe.DataManager import DataManager;

class TestDataManager(DBTestCase):
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
        self.clinicalItemQuery = \
            """
            select
                clinical_item_id, name, analysis_status, default_recommend
            from
                clinical_item
            where
                clinical_item_id < 0
            order by
                clinical_item_id  desc
            """;

        headers = ["patient_item_id","patient_id","clinical_item_id","item_date","analyze_date"];
        dataModels = \
            [
                RowItemModel( [-1,  -11111, -4,  datetime(2000, 1, 1, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-2,  -11111, -10, datetime(2000, 1, 1, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-3,  -11111, -8,  datetime(2000, 1, 1, 2), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-4,  -11111, -10, datetime(2000, 1, 2, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-5,  -11111, -12, datetime(2000, 2, 1, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-10, -22222, -7,  datetime(2000, 1, 5, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-12, -22222, -6,  datetime(2000, 1, 9, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-13, -22222, -11, datetime(2000, 1, 9, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-14, -33333, -6,  datetime(2000, 2, 9, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-15, -33333, -2,  datetime(2000, 2,11, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-16, -33333, -11,  datetime(2000, 2,11, 0), datetime(2100, 1, 1, 0)], headers ),
                RowItemModel( [-17, -33333, -11,  datetime(2001, 1, 1, 0), datetime(2100, 1, 1, 0)], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("patient_item", dataModel );
        self.patientItemQuery = \
            """
            select
                patient_item_id, patient_id, clinical_item_id, item_date, analyze_date
            from
                patient_item
            where
                clinical_item_id < 0
            order by
                patient_id desc, item_date, patient_item_id desc
            """;


        headers = [ "clinical_item_id","subsequent_item_id",\
                    "count_0","count_3600","count_86400","count_604800","count_any",
                    "time_diff_sum","time_diff_sum_squares",
                    "patient_count_0","patient_count_3600","patient_count_86400","patient_count_604800","patient_count_any",
                    "patient_time_diff_sum","patient_time_diff_sum_squares",
                    "patient_count_0","encounter_count_0",
                  ];
        dataModels = \
            [
                RowItemModel( [-11,-11,   3, 3, 3, 3, 4,  999.0, 9999.0,   2, 2, 2, 2, 2,  999.0, 9999.0, 2,2], headers ),
                RowItemModel( [-11, -7,   0, 0, 0, 0, 0,  0.0, 0.0,   0, 0, 0, 0, 0,  0.0, 0.0, 0,0], headers ),
                RowItemModel( [-11, -6,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0, 1,1], headers ),
                RowItemModel( [-11, -2,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0, 1,1], headers ),
                RowItemModel( [ -7,-11,   0, 0, 0, 1, 1,  345600.0, 119439360000.0,   0, 0, 0, 1, 1,  345600.0, 119439360000.0, 0,0], headers ),
                RowItemModel( [ -7, -7,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0, 1,1], headers ),
                RowItemModel( [ -7, -6,   0, 0, 0, 1, 1,  345600.0, 119439360000.0,   0, 0, 0, 1, 1,  345600.0, 119439360000.0, 0,0], headers ),

                RowItemModel( [ -6,-11,   1, 1, 1, 2, 2, 172800.0, 29859840000.0,   1, 1, 1, 2, 2, 172800.0, 29859840000.0, 1,1], headers ),
                RowItemModel( [ -6, -7,   0, 0, 0, 0, 0,  0.0, 0.0,   0, 0, 0, 0, 0,  0.0, 0.0, 0,0], headers ),
                RowItemModel( [ -6, -6,   2, 2, 2, 2, 2,  0.0, 0.0,   2, 2, 2, 2, 2,  0.0, 0.0, 2,2], headers ),
                RowItemModel( [ -6, -2,   0, 0, 0, 1, 1,  172800.0, 29859840000.0,   0, 0, 0, 1, 1,  172800.0, 29859840000.0, 0,0], headers ),

                RowItemModel( [ -2,-11,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0, 1,1], headers ),
                RowItemModel( [ -2, -7,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0, 1,1], headers ),
                RowItemModel( [ -2, -6,   0, 0, 0, 0, 0,  0.0, 0.0,   0, 0, 0, 0, 0,  0.0, 0.0, 0,0], headers ),
                RowItemModel( [ -2, -2,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0, 1,1], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_association", dataModel );
        self.clinicalItemAssociationQuery = \
            """
            select
                clinical_item_id, subsequent_item_id,
                count_0,count_3600,count_86400,count_604800,count_any,
                time_diff_sum,time_diff_sum_squares,
                patient_count_0,patient_count_3600,patient_count_86400,patient_count_604800,patient_count_any,
                patient_time_diff_sum, patient_time_diff_sum_squares
            from
                clinical_item_association
            where
                clinical_item_id < 0
            order by
                clinical_item_id, subsequent_item_id
            """;

        self.analyzer = DataManager();  # Instance to test on
        self.analyzer.maxClinicalItemId = 0;    # Avoid testing on "real" data

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute("delete from clinical_item_link where clinical_item_id < 0");
        DBUtil.execute("delete from backup_link_patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
        DBUtil.execute("delete from patient_item where patient_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );

        DBTestCase.tearDown(self);

    def test_deactivateAnalysis(self):
        clinicalItemIds = set([-6,-11]);
        self.analyzer.deactivateAnalysis(clinicalItemIds);

        expectedClinicalItemStatus = \
            [
                [-1, "CBC",1, 1],
                [-2, "BMP",0, 1],
                [-3, "Hepatic Panel",1, 1],
                [-4, "Cardiac Enzymes",1, 1],
                [-5, "CXR",1, 1],
                [-6, "RUQ Ultrasound",0, 1],
                [-7, "CT Abdomen/Pelvis",1, 1],
                [-8, "CT PE Thorax",1, 1],
                [-9, "Acetaminophen",1, 1],
                [-10, "Carvedilol",1, 1],
                [-11, "Enoxaparin",0, 1],
                [-12, "Warfarin",1, 1],
                [-13, "Ceftriaxone",1, 1],
                [-14, "Foley Catheter",1, 1],
                [-15, "Strict I&O",1, 1],
                [-16, "Fall Precautions",1, 1],
            ];
        clinicalItemStatus = DBUtil.execute(self.clinicalItemQuery);
        self.assertEqualTable( expectedClinicalItemStatus, clinicalItemStatus );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), "*"],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), "*"],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [-10, -22222, -7,  datetime(2000, 1, 5, 0), "*"],
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), None],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), None],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), None],
                [-15, -33333, -2,  datetime(2000, 2,11, 0), "*"],
                [-16, -33333, -11,  datetime(2000, 2,11, 0), None],
                [-17, -33333, -11,  datetime(2001, 1, 1, 0), None],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        expectedAssociationStats = \
            [
                [ -7, -7,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],
                [ -2, -7,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],
                [ -2, -2,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],
            ];
        associationStats = DBUtil.execute(self.clinicalItemAssociationQuery);
        self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

    def test_deactivateAnalysisByCount(self):
        thresholdInstanceCount = 1;
        categoryIds = [-1,-2];
        self.analyzer.deactivateAnalysisByCount(thresholdInstanceCount, categoryIds);

        expectedClinicalItemStatus = \
            [
                [-1, "CBC",0, 1],
                [-2, "BMP",0, 1],
                [-3, "Hepatic Panel",0, 1],
                [-4, "Cardiac Enzymes",0, 1],
                [-5, "CXR",0, 1],
                [-6, "RUQ Ultrasound",1, 1],
                [-7, "CT Abdomen/Pelvis",0, 1],
                [-8, "CT PE Thorax",0, 1],
                [-9, "Acetaminophen",1, 1], # Different category, so should be left alone
                [-10, "Carvedilol",1, 1],
                [-11, "Enoxaparin",1, 1],
                [-12, "Warfarin",1, 1],
                [-13, "Ceftriaxone",1, 1],
                [-14, "Foley Catheter",1, 1],
                [-15, "Strict I&O",1, 1],
                [-16, "Fall Precautions",1, 1],
            ];
        clinicalItemStatus = DBUtil.execute(self.clinicalItemQuery);
        self.assertEqualTable( expectedClinicalItemStatus, clinicalItemStatus );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), None],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), None],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [-10, -22222, -7,  datetime(2000, 1, 5, 0), None],
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), "*"],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), "*"],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), "*"],
                [-15, -33333, -2,  datetime(2000, 2,11, 0), None],
                [-16, -33333, -11, datetime(2000, 2,11, 0), "*"],
                [-17, -33333, -11, datetime(2001, 1, 1, 0), "*"],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        expectedAssociationStats = \
            [
                [-11,-11,   3, 3, 3, 3, 4,  999.0, 9999.0,   2, 2, 2, 2, 2,  999.0, 9999.0],
                [-11, -6,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],
                [ -6,-11,   1, 1, 1, 2, 2, 172800.0, 29859840000.0,   1, 1, 1, 2, 2, 172800.0, 29859840000.0],
                [ -6, -6,   2, 2, 2, 2, 2,  0.0, 0.0,   2, 2, 2, 2, 2,  0.0, 0.0],
            ];
        associationStats = DBUtil.execute(self.clinicalItemAssociationQuery);
        self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

    def test_compositeRelated(self):
        # Simulate command-line execution
        self.analyzer.main(["medinfo/cpoe/DataManager.py","-c","-2,-4,-8|NewComposite|New Composite Item|-1|-100" ]);
        #compositeId = self.analyzer.compositeRelated( (-2,-4,-8), "NewComposite","New Composite Item", -1, -100 );

        # Revise the new item ID to a sentinel test value
        expectedClinicalItemStatus = \
            [
                [-1, "CBC",1, 1],
                [-2, "BMP",0, 1],
                [-3, "Hepatic Panel",1, 1],
                [-4, "Cardiac Enzymes",1, 1],
                [-5, "CXR",1, 1],
                [-6, "RUQ Ultrasound",1, 1],
                [-7, "CT Abdomen/Pelvis",1, 1],
                [-8, "CT PE Thorax",1, 1],
                [-9, "Acetaminophen",1, 1],
                [-10, "Carvedilol",1, 1],
                [-11, "Enoxaparin",1, 1],
                [-12, "Warfarin",1, 1],
                [-13, "Ceftriaxone",1, 1],
                [-14, "Foley Catheter",1, 1],
                [-15, "Strict I&O",1, 1],
                [-16, "Fall Precautions",1, 1],

                [-100,"NewComposite", 1, 0],    # Remove from default recommend list
            ];
        clinicalItemStatus = DBUtil.execute(self.clinicalItemQuery);
        self.assertEqualTable( expectedClinicalItemStatus, clinicalItemStatus );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                # Likewise, use None for primary ID key whose specific value is unimportant
                [None,-11111,-100, datetime(2000, 1, 1, 0), None],
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), "*"],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [None,-11111,-100, datetime(2000, 1, 1, 2), None],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), "*"],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [-10, -22222, -7,  datetime(2000, 1, 5, 0), "*"],
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), "*"],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), "*"],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), "*"],
                [None,-33333,-100, datetime(2000, 2,11, 0), None],
                [-15, -33333, -2,  datetime(2000, 2,11, 0), "*"],
                [-16, -33333, -11, datetime(2000, 2,11, 0), "*"],
                [-17, -33333, -11, datetime(2001, 1, 1, 0), "*"],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        # Check for tracking link records
        linkQuery = \
            """
            select
                clinical_item_id,  linked_item_id
            from
                clinical_item_link
            where
                clinical_item_id < 0
            order by
                clinical_item_id desc, linked_item_id desc
            """;
        expectedItems = \
            [
                [-100,-2],
                [-100,-4],
                [-100,-8],
            ];
        actualItems = DBUtil.execute( linkQuery );
        self.assertEqualTable( expectedItems, actualItems );



        log.debug("Test incremental update via command-line");
        self.analyzer.main(["medinfo/cpoe/DataManager.py","-g","-6|-100" ]);
        #self.analyzer.generatePatientItemsForCompositeId( (-6,), -100 );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                # Likewise, use None for primary ID key whose specific value is unimportant
                [None,-11111,-100, datetime(2000, 1, 1, 0), None],
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), "*"],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [None,-11111,-100, datetime(2000, 1, 1, 2), None],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), "*"],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [-10, -22222, -7,  datetime(2000, 1, 5, 0), "*"],
                [None,-22222,-100, datetime(2000, 1, 9, 0), None],
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), "*"],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), "*"],
                [None,-33333,-100, datetime(2000, 2, 9, 0), None],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), "*"],
                [None,-33333,-100, datetime(2000, 2,11, 0), None],
                [-15, -33333, -2,  datetime(2000, 2,11, 0), "*"],
                [-16, -33333, -11, datetime(2000, 2,11, 0), "*"],
                [-17, -33333, -11, datetime(2001, 1, 1, 0), "*"],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        # Check for tracking link records
        expectedItems = \
            [
                [-100,-2],
                [-100,-4],
                [-100,-6],
                [-100,-8],
            ];
        actualItems = DBUtil.execute( linkQuery );
        self.assertEqualTable( expectedItems, actualItems );



        log.debug("Test inherited update");
        self.analyzer.main(["medinfo/cpoe/DataManager.py","-c","-7,-100|InheritingComposite|Inheriting Composite Item|-1|-101" ]);
        #compositeId = self.analyzer.compositeRelated( (-7,-100), "InheritingComposite","Inheriting Composite Item", -1, -101 );
        # Revise the new item ID to a sentinel test value
        expectedClinicalItemStatus = \
            [
                [-1, "CBC",1, 1],
                [-2, "BMP",0, 1],
                [-3, "Hepatic Panel",1, 1],
                [-4, "Cardiac Enzymes",1, 1],
                [-5, "CXR",1, 1],
                [-6, "RUQ Ultrasound",1, 1],
                [-7, "CT Abdomen/Pelvis",1, 1],
                [-8, "CT PE Thorax",1, 1],
                [-9, "Acetaminophen",1, 1],
                [-10, "Carvedilol",1, 1],
                [-11, "Enoxaparin",1, 1],
                [-12, "Warfarin",1, 1],
                [-13, "Ceftriaxone",1, 1],
                [-14, "Foley Catheter",1, 1],
                [-15, "Strict I&O",1, 1],
                [-16, "Fall Precautions",1, 1],

                [-100,"NewComposite", 1, 0],
                [-101,"InheritingComposite", 1, 0],
            ];
        clinicalItemStatus = DBUtil.execute(self.clinicalItemQuery);
        self.assertEqualTable( expectedClinicalItemStatus, clinicalItemStatus );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                # Likewise, use None for primary ID key whose specific value is unimportant
                [None,-11111,-101, datetime(2000, 1, 1, 0), None],
                [None,-11111,-100, datetime(2000, 1, 1, 0), None],
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), "*"],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [None,-11111,-101, datetime(2000, 1, 1, 2), None],
                [None,-11111,-100, datetime(2000, 1, 1, 2), None],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), "*"],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [None,-22222,-101, datetime(2000, 1, 5, 0), None],
                [-10, -22222, -7,  datetime(2000, 1, 5, 0), "*"],
                [None,-22222,-101, datetime(2000, 1, 9, 0), None],
                [None,-22222,-100, datetime(2000, 1, 9, 0), None],
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), "*"],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), "*"],
                [None,-33333,-101, datetime(2000, 2, 9, 0), None],
                [None,-33333,-100, datetime(2000, 2, 9, 0), None],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), "*"],
                [None,-33333,-101, datetime(2000, 2,11, 0), None],
                [None,-33333,-100, datetime(2000, 2,11, 0), None],
                [-15, -33333, -2,  datetime(2000, 2,11, 0), "*"],
                [-16, -33333, -11, datetime(2000, 2,11, 0), "*"],
                [-17, -33333, -11, datetime(2001, 1, 1, 0), "*"],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        # Check for tracking link records
        expectedItems = \
            [
                [-100,-2],
                [-100,-4],
                [-100,-6],
                [-100,-8],
                [-101,-7],
                [-101,-100],
            ];
        actualItems = DBUtil.execute( linkQuery );
        self.assertEqualTable( expectedItems, actualItems );

    def test_mergeRelated(self):
        self.analyzer.mergeRelated(-6, (-7,-2) );

        expectedClinicalItemStatus = \
            [
                [-1, "CBC",1, 1],
                [-2, "BMP",0, 1],
                [-3, "Hepatic Panel",1, 1],
                [-4, "Cardiac Enzymes",1, 1],
                [-5, "CXR",1, 1],
                [-6, "RUQ Ultrasound+BMP+CT Abdomen/Pelvis",1, 1],
                [-7, "CT Abdomen/Pelvis",0, 1],
                [-8, "CT PE Thorax",1, 1],
                [-9, "Acetaminophen",1, 1],
                [-10, "Carvedilol",1, 1],
                [-11, "Enoxaparin",1, 1],
                [-12, "Warfarin",1, 1],
                [-13, "Ceftriaxone",1, 1],
                [-14, "Foley Catheter",1, 1],
                [-15, "Strict I&O",1, 1],
                [-16, "Fall Precautions",1, 1],
            ];
        clinicalItemStatus = DBUtil.execute(self.clinicalItemQuery);
        self.assertEqualTable( expectedClinicalItemStatus, clinicalItemStatus );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), "*"],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), "*"],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [-10, -22222, -6,  datetime(2000, 1, 5, 0), None],  # Reassign
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), "*"],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), "*"],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), "*"],
                [-15, -33333, -6,  datetime(2000, 2,11, 0), None],  # Reassign
                [-16, -33333, -11, datetime(2000, 2,11, 0), "*"],
                [-17, -33333, -11, datetime(2001, 1, 1, 0), "*"],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        expectedAssociationStats = \
            [
                [-11,-11,   3, 3, 3, 3, 4,  999.0, 9999.0,   2, 2, 2, 2, 2,  999.0, 9999.0],
                [-11, -6,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],

                [ -6,-11,   1, 1, 1, 2, 2, 172800.0, 29859840000.0,   1, 1, 1, 2, 2, 172800.0, 29859840000.0],
                [ -6, -6,   2, 2, 2, 2, 2,  0.0, 0.0,   2, 2, 2, 2, 2,  0.0, 0.0],
            ];
        associationStats = DBUtil.execute(self.clinicalItemAssociationQuery);
        self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

        # Check for backup of lost data
        backupQuery = \
            """
            select
                patient_item_id, clinical_item_id
            from
                backup_link_patient_item
            where
                clinical_item_id < 0
            order by
                patient_item_id desc, clinical_item_id
            """;
        expectedBackupItems = \
            [
                [-10,-7],
                [-15,-2],
            ];
        backupItems = DBUtil.execute( backupQuery );
        self.assertEqualTable( expectedBackupItems, backupItems );


    def test_unifyRedundant(self):
        self.analyzer.unifyRedundant( -7, (-7,-2) );

        expectedClinicalItemStatus = \
            [
                [-1, "CBC",1, 1],
                [-2, "BMP",0, 1],
                [-3, "Hepatic Panel",1, 1],
                [-4, "Cardiac Enzymes",1, 1],
                [-5, "CXR",1, 1],
                [-6, "RUQ Ultrasound",1, 1],
                [-7, "CT Abdomen/Pelvis+BMP",1, 1],
                [-8, "CT PE Thorax",1, 1],
                [-9, "Acetaminophen",1, 1],
                [-10, "Carvedilol",1, 1],
                [-11, "Enoxaparin",1, 1],
                [-12, "Warfarin",1, 1],
                [-13, "Ceftriaxone",1, 1],
                [-14, "Foley Catheter",1, 1],
                [-15, "Strict I&O",1, 1],
                [-16, "Fall Precautions",1, 1],
            ];
        clinicalItemStatus = DBUtil.execute(self.clinicalItemQuery);
        self.assertEqualTable( expectedClinicalItemStatus, clinicalItemStatus );

        expectedPatientItems = \
            [   # Use placeholder "*" for analyze date, just verify that it exists and is consistent.  Actual value is not important
                [-1,  -11111, -4,  datetime(2000, 1, 1, 0), "*"],
                [-2,  -11111, -10, datetime(2000, 1, 1, 0), "*"],
                [-3,  -11111, -8,  datetime(2000, 1, 1, 2), "*"],
                [-4,  -11111, -10, datetime(2000, 1, 2, 0), "*"],
                [-5,  -11111, -12, datetime(2000, 2, 1, 0), "*"],
                [-10, -22222, -7,  datetime(2000, 1, 5, 0), "*"],
                [-12, -22222, -6,  datetime(2000, 1, 9, 0), "*"],
                [-13, -22222, -11, datetime(2000, 1, 9, 0), "*"],
                [-14, -33333, -6,  datetime(2000, 2, 9, 0), "*"],
                [-15, -33333, -2,  datetime(2000, 2,11, 0), None],
                [-16, -33333, -11, datetime(2000, 2,11, 0), "*"],
                [-17, -33333, -11, datetime(2001, 1, 1, 0), "*"],
            ];
        patientItems = DBUtil.execute(self.patientItemQuery);
        self.assertEqualPatientItems( expectedPatientItems, patientItems );

        expectedAssociationStats = \
            [
                [-11,-11,   3, 3, 3, 3, 4,  999.0, 9999.0,   2, 2, 2, 2, 2,  999.0, 9999.0],
                [-11, -7,   0, 0, 0, 0, 0,  0.0, 0.0,   0, 0, 0, 0, 0,  0.0, 0.0],
                [-11, -6,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],
                [ -7,-11,   0, 0, 0, 1, 1,  345600.0, 119439360000.0,   0, 0, 0, 1, 1,  345600.0, 119439360000.0],
                [ -7, -7,   1, 1, 1, 1, 1,  0.0, 0.0,   1, 1, 1, 1, 1,  0.0, 0.0],
                [ -7, -6,   0, 0, 0, 1, 1,  345600.0, 119439360000.0,   0, 0, 0, 1, 1,  345600.0, 119439360000.0],

                [ -6,-11,   1, 1, 1, 2, 2, 172800.0, 29859840000.0,   1, 1, 1, 2, 2, 172800.0, 29859840000.0],
                [ -6, -7,   0, 0, 0, 0, 0,  0.0, 0.0,   0, 0, 0, 0, 0,  0.0, 0.0],
                [ -6, -6,   2, 2, 2, 2, 2,  0.0, 0.0,   2, 2, 2, 2, 2,  0.0, 0.0],
            ];
        associationStats = DBUtil.execute(self.clinicalItemAssociationQuery);
        self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

    def assertEqualPatientItems( self, expectedPatientItems, patientItems ):
        """Patch the expected items to look for whatever is the set analyze_date,
        and just adjust so expect will be present and consistent.  Don't care about specific value.
        Likewise, don't care about primary key patient_item_id new values
        """
        expectedAnalyzeDate = None;
        for row in patientItems:
            analyzeDate = row[-1];
            if analyzeDate is not None:
                expectedAnalyzeDate = analyzeDate;
                break;
        for row in expectedPatientItems:
            if expectedAnalyzeDate is not None and row[-1] is not None:
                row[-1] = expectedAnalyzeDate;

        for (expectedRow, actualRow) in zip(expectedPatientItems, patientItems):
            if expectedRow[0] is None:
                expectedRow[0] = actualRow[0];

        self.assertEqualTable( expectedPatientItems, patientItems );

    def test_updateClinicalItemCounts(self):
        self.analyzer.updateClinicalItemCounts();

        clinicalItemQueryClinicalCounts = \
            """
            select
                clinical_item_id, name, analysis_status, item_count, patient_count, patient_count, encounter_count
            from
                clinical_item
            where
                clinical_item_id < 0
            order by
                clinical_item_id  desc
            """;
        # Expect counts to default to zero if no values known
        expectedClinicalItemCounts = \
            [
                [-1, "CBC",1, 0, 0, 0, 0],
                [-2, "BMP",0, 1, 1, 1, 1],
                [-3, "Hepatic Panel",1, 0, 0, 0, 0],
                [-4, "Cardiac Enzymes",1, 0, 0, 0, 0],
                [-5, "CXR",1, 0, 0, 0, 0],
                [-6, "RUQ Ultrasound",1, 2, 2, 2, 2],
                [-7, "CT Abdomen/Pelvis",1, 1, 1, 1, 1],
                [-8, "CT PE Thorax",1, 0, 0, 0, 0],
                [-9, "Acetaminophen",1, 0, 0, 0, 0],
                [-10, "Carvedilol",1, 0, 0, 0, 0],
                [-11, "Enoxaparin",1, 3, 2, 2, 2], # Two instances occur for the same patient
                [-12, "Warfarin",1, 0, 0, 0, 0],
                [-13, "Ceftriaxone",1, 0, 0, 0, 0],
                [-14, "Foley Catheter",1, 0, 0, 0, 0],
                [-15, "Strict I&O",1, 0, 0, 0, 0],
                [-16, "Fall Precautions",1, 0, 0, 0, 0],
            ];
        clinicalItemCounts = DBUtil.execute(clinicalItemQueryClinicalCounts) #Queries test DB to see what is stored in there
        self.assertEqualTable(expectedClinicalItemCounts, clinicalItemCounts)


    def test_resetAssociationModel(self):

        self.analyzer.updateClinicalItemCounts();	# Generate clinical item counts based on patient item data

        ciaCount = DBUtil.execute("select count(*) from clinical_item_association")[0][0];
        piCount = DBUtil.execute("select count(*) from patient_item")[0][0];
        piAnalyzedCount = DBUtil.execute("select count(*) from patient_item where analyze_date is not null")[0][0];
        cacheCount = DBUtil.execute("select count(*) from data_cache where data_key in ('analyzedPatientCount')")[0][0];
        itemCountSummary = DBUtil.execute("select sum(item_count) from clinical_item")[0][0];

        self.assertTrue(ciaCount > 0);
        self.assertTrue(piCount > 0);
        self.assertTrue(piAnalyzedCount > 0);
        #self.assertTrue(cacheCount > 0);
        self.assertTrue(itemCountSummary > 0);

        self.analyzer.resetAssociationModel();

        ciaCount2 = DBUtil.execute("select count(*) from clinical_item_association")[0][0];
        piCount2 = DBUtil.execute("select count(*) from patient_item")[0][0];
        piAnalyzedCount2 = DBUtil.execute("select count(*) from patient_item where analyze_date is not null")[0][0];
        cacheCount2 = DBUtil.execute("select count(*) from data_cache where data_key in ('analyzedPatientCount')")[0][0];
        itemCountSummary2 = DBUtil.execute("select sum(item_count) from clinical_item")[0][0];

        self.assertEqual(0, ciaCount2);
        self.assertEqual(piCount, piCount2);
        self.assertEqual(0, piAnalyzedCount2);
        self.assertEqual(0, cacheCount2);
        self.assertEqual(0, itemCountSummary2);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestDataManager("test_compositeRelated"));
    #suite.addTest(TestDataManager("test_updateClinicalItemCounts"));
    #suite.addTest(TestDataManager('test_executeIterator'));
    #suite.addTest(TestDataManager('test_resetAssociationModel'));
    suite.addTest(unittest.makeSuite(TestDataManager));

    return suite;

if __name__=="__main__":
    log.setLevel(LOGGER_LEVEL)
    
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
