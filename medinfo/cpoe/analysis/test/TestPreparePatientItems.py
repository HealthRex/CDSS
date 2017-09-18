#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os;
from cStringIO import StringIO;
import json;
from datetime import datetime, timedelta;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import loadJSONDict;
from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.analysis.PreparePatientItems import PreparePatientItems, AnalysisQuery;

from Util import BaseCPOETestAnalysis;

class TestPreparePatientItems(BaseCPOETestAnalysis):
    def setUp(self):
        """Prepare state for test cases"""
        BaseCPOETestAnalysis.setUp(self);
        self.purgeTestRecords();
        log.info("Populate the database with test data")
        
        self.clinicalItemCategoryIdStrList = list();
        headers = ["clinical_item_category_id","default_recommend","source_table"];
        dataModels = \
            [   
                RowItemModel( [-1, 1, "Labs"], headers ),
                RowItemModel( [-2, 1, "Imaging"], headers ),
                RowItemModel( [-3, 1, "Meds"], headers ),
                RowItemModel( [-4, 1, "Nursing"], headers ),
                RowItemModel( [-5, 0, "Problems"], headers ),
                RowItemModel( [-6, 1, "Lab Results"], headers ),
                RowItemModel( [-7, 1, "Admit Dx"], headers ),
                RowItemModel( [-8, 0, "Demographics"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );
            self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

        headers = ["clinical_item_id","clinical_item_category_id","analysis_status","default_recommend","name"];
        dataModels = \
            [   
                RowItemModel( [-1, -1, 1, 1, "CBC"], headers ),
                RowItemModel( [-2, -1, 1, 1, "BMP"], headers ),
                RowItemModel( [-3, -1, 1, 1, "Hepatic Panel"], headers ),
                RowItemModel( [-4, -1, 1, 1, "Cardiac Enzymes"], headers ),
                RowItemModel( [-5, -2, 1, 1, "CXR"], headers ),
                RowItemModel( [-6, -2, 1, 1, "RUQ Ultrasound"], headers ),
                RowItemModel( [-7, -2, 1, 1, "CT Abdomen/Pelvis"], headers ),
                RowItemModel( [-8, -2, 1, 1, "CT PE Thorax"], headers ),
                RowItemModel( [-9, -3, 1, 1, "Acetaminophen"], headers ),
                RowItemModel( [-10, -3, 1, 1, "Carvedilol"], headers ),
                RowItemModel( [-11, -3, 1, 1, "Enoxaparin"], headers ),
                RowItemModel( [-12, -3, 1, 1, "Warfarin"], headers ),
                RowItemModel( [-13, -3, 1, 0, "Ceftriaxone"], headers ),
                RowItemModel( [-14, -4, 1, 1, "Foley Catheter"], headers ),
                RowItemModel( [-15, -4, 1, 1, "Strict I&O"], headers ),
                RowItemModel( [-16, -4, 1, 1, "Fall Precautions"], headers ),
                
                RowItemModel( [-22, -5, 1, 1, "Diagnosis 2"], headers ),
                RowItemModel( [-23, -5, 1, 1, "Diagnosis 3"], headers ),
                RowItemModel( [-24, -5, 1, 1, "Diagnosis 4"], headers ),
                
                RowItemModel( [-21, -7, 0, 1, "Diagnosis 1 (Admit)"], headers ),
                RowItemModel( [-25, -7, 1, 1, "Diagnosis 2 (Admit)"], headers ),

                RowItemModel( [-30, -6, 1, 1, "Troponin (High)"], headers ),
                RowItemModel( [-31, -6, 1, 1, "BNP (High)"], headers ),
                RowItemModel( [-32, -6, 1, 1, "Creatinine (High)"], headers ),
                RowItemModel( [-33, -6, 1, 1, "ESR (High)"], headers ), # Default exclude from recommendations

                RowItemModel( [-41, -8, 1, 1, "Male"], headers ),
                RowItemModel( [-42, -8, 1, 1, "Female"], headers ),
                RowItemModel( [-43, -8, 1, 1, "Birth"], headers ),
                RowItemModel( [-44, -8, 1, 1, "Birth1980s"], headers ),
                RowItemModel( [-45, -8, 1, 1, "Birth1970s"], headers ),
                RowItemModel( [-46, -8, 1, 1, "RaceWhite"], headers ),
                RowItemModel( [-47, -8, 1, 1, "RaceBlack"], headers ),
                RowItemModel( [-49, -8, 1, 1, "Death"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        headers = ["patient_item_id","patient_id","clinical_item_id","item_date","analyze_date"];
        dataModels = \
            [   
                RowItemModel( [-101,-11111, -43, datetime(1972, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-102,-11111, -45, datetime(1972, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-103,-11111, -41, datetime(1972, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-104,-11111, -46, datetime(1972, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-52, -11111, -23, datetime(1999, 9, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-51, -11111, -21, datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-1,  -11111, -4,  datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-2,  -11111, -10, datetime(2000, 1, 1, 1), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-3,  -11111, -8,  datetime(2000, 1, 1, 2), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-4,  -11111, -4,  datetime(2000, 1, 1, 3), datetime(2010, 1, 1, 0)], headers ),  # Repeat item

                RowItemModel( [-60, -11111, -32, datetime(2000, 1, 1, 4), datetime(2010, 1, 1, 0)], headers ),  # Within query time
                RowItemModel( [-61, -11111, -30, datetime(2000, 1, 4, 0), datetime(2010, 1, 1, 0)], headers ),  # Within 1 week
                RowItemModel( [-63, -11111, -13, datetime(2000, 1, 4, 5), datetime(2010, 1, 1, 0)], headers ),  # Exclude item
                RowItemModel( [-64, -11111, -24, datetime(2000, 1, 4,10), datetime(2010, 1, 1, 0)], headers ),  # Exclude category
                RowItemModel( [-62, -11111, -31, datetime(2000, 1,10, 0), datetime(2010, 1, 1, 0)], headers ),  # Beyond 1 week

                RowItemModel( [-71,  -11111, -8,  datetime(2000, 1, 4, 1), datetime(2010, 1, 1, 0)], headers ), # Repeat query item within 1 week verify period, don't use as a verify item

                RowItemModel( [-201, -11111,-49,  datetime(2009, 1, 1, 1), datetime(2010, 1, 1, 0)], headers ), # Death date in far future

                RowItemModel( [-5,  -11111, -12, datetime(2000, 2, 1, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-121,-22222, -43, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-122,-22222, -44, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-123,-22222, -42, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-124,-22222, -47, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                
                RowItemModel( [-10, -22222, -7,  datetime(2000, 1, 5, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-12, -22222, -6,  datetime(2000, 1, 9, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-13, -22222, -11, datetime(2000, 1, 9, 0), datetime(2010, 1, 1, 0)], headers ),


                RowItemModel( [-131,-33333, -43, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-132,-33333, -44, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-133,-33333, -42, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-134,-33333, -46, datetime(1983, 5, 1, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-14, -33333, -6,  datetime(2000, 2, 9, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-15, -33333, -2,  datetime(2000, 2,11, 0), datetime(2010, 1, 1, 0)], headers ),


                RowItemModel( [-141,-44444, -43, datetime(1975, 3, 3, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-142,-44444, -45, datetime(1975, 3, 3, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-143,-44444, -42, datetime(1975, 3, 3, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-144,-44444, -46, datetime(1975, 3, 3, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-20, -44444, -21, datetime(2000, 1, 5, 0), datetime(2010, 1, 1, 0)], headers ),  # Admit diagnosis
                RowItemModel( [-22, -44444, -6,  datetime(2000, 1, 5, 0), datetime(2010, 1, 1, 0)], headers ),  # Items recorded with date level precision, not time
                RowItemModel( [-23, -44444, -12, datetime(2000, 1, 5, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-24, -44444, -11, datetime(2000, 1, 6, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-25, -44444, -8,  datetime(2000, 1, 6, 0), datetime(2010, 1, 1, 0)], headers ),

                RowItemModel( [-204,-44444,-49,  datetime(2000, 2, 1, 1), datetime(2010, 1, 1, 0)], headers ), # Death date within 1 month


                # Order Set Usage example
                RowItemModel( [-5002,-55555, -3,  datetime(2000,10, 1, 0, 0), datetime(2010, 1, 1, 0)], headers ), # Very old item, not relevant to current query
                RowItemModel( [-5040,-55555, -25, datetime(2000,10,10, 0, 0), datetime(2010, 1, 1, 0)], headers ), # Admit diagnosis (coded at date level precision before time-level order data)
                RowItemModel( [-5005,-55555, -2,  datetime(2000,10,10,10, 0), datetime(2010, 1, 1, 0)], headers ), # Non-order set item before
                RowItemModel( [-5010,-55555, -1,  datetime(2000,10,10,10, 5), datetime(2010, 1, 1, 0)], headers ), # Order Set 1
                RowItemModel( [-5020,-55555, -9,  datetime(2000,10,10,10, 5), datetime(2010, 1, 1, 0)], headers ), # Order Set 1
                RowItemModel( [-5030,-55555, -5,  datetime(2000,10,10,10,10), datetime(2010, 1, 1, 0)], headers ), # Ad-hoc within 1 hour
                RowItemModel( [-5050,-55555, -8,  datetime(2000,10,10,10,30), datetime(2010, 1, 1, 0)], headers ), # Order Set 2
                RowItemModel( [-5060,-55555, -11, datetime(2000,10,10,10,30), datetime(2010, 1, 1, 0)], headers ), # Order Set 2
                RowItemModel( [-5070,-55555, -12, datetime(2000,10,10,10,30), datetime(2010, 1, 1, 0)], headers ), # Ad-hoc Within 1 hour
                RowItemModel( [-5080,-55555, -10, datetime(2000,10,10,20, 0), datetime(2010, 1, 1, 0)], headers ), # Ad-hoc 10 hours later
                RowItemModel( [-5090,-55555, -1,  datetime(2000,10,10,20, 0), datetime(2010, 1, 1, 0)], headers ), # Order Set 1 again (ignore repeats)
                RowItemModel( [-5100,-55555, -2,  datetime(2000,10,10,20, 0), datetime(2010, 1, 1, 0)], headers ), # Order Set 1 again
                RowItemModel( [-5110,-55555, -3,  datetime(2000,10,10,20, 0), datetime(2010, 1, 1, 0)], headers ), # Ad-hoc 10 hours later
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
-1;-1;-11;4
-2;-1;-12;4
-3;-1;-13;4
-4;-2;-9;4
-5;-2;-10;4
-6;-3;-1;4
-7;-3;-2;4
-8;-3;-3;4
-100;-3;-4;4
-9;-4;-1;4
-10;-4;-2;4
-11;-4;-3;4
-101;-4;-11;4
-12;-5;-5;4
-74;-6;-6;4
-77;-6;-7;4
-13;-6;-8;4
-14;-7;-5;4
-15;-7;-6;4
-16;-7;-7;4
-17;-7;-8;4
-18;-8;-14;4
-19;-8;-15;4
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection_item", delim=";");

        dataTextStr = \
"""patient_item_collection_link_id;patient_item_id;item_collection_item_id
-1;-5010;-6
-2;-5020;-4
-3;-5050;-13
-4;-5060;-101
-5;-5090;-6
-6;-5100;-7
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "patient_item_collection_link", delim=";");


        # Instance to test on
        self.analyzer = PreparePatientItems();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.purgeTestRecords();
        BaseCPOETestAnalysis.tearDown(self);

    def purgeTestRecords(self):
        log.info("Purge test records from the database")
        DBUtil.execute("delete from patient_item_collection_link where patient_item_collection_link_id < 0");
        DBUtil.execute("delete from item_collection_item where item_collection_item_id < 0");
        DBUtil.execute("delete from item_collection where item_collection_id < 0");

        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
        DBUtil.execute("delete from patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id < 0");


    def test_analysisPreparation(self):
        # Run the analysis preparer against the mock test data above and verify expected data afterwards.
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-11111]);
        analysisQuery.baseCategoryId = -7;
        analysisQuery.queryTimeSpan = timedelta(0,86400);
        analysisQuery.verifyTimeSpan = timedelta(0,604800);
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.targetItemIds = set([-33,-32,-31,-30]);
        analysisQuery.baseRecQuery.excludeItemIds = [-13];
        analysisQuery.baseRecQuery.excludeCategoryIds = [-5];
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data

        # Initial run without time limits on outcome measure
        colNames = ["patient_id","baseItemId","queryItemCountById","verifyItemCountById","outcome.-33","outcome.-32", "outcome.-31","outcome.-30"];
        expectedResults = [ RowItemModel([-11111, -21, {-4:2,-10:1,-8:1,-32:1}, {-30:1}, +0,  +2,  +1,  +1], colNames ) ];
        analysisResults = list(self.analyzer(analysisQuery));
        self.assertEqualResultDicts( expectedResults, analysisResults, colNames );

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-c","-7","-Q","86400","-V","604800","-o","-33,-32,-31,-30",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualTextOutput(expectedResults, textOutput, colNames);
        
        # Now try with time limitation on outcome measure
        analysisQuery.baseRecQuery.timeDeltaMax = timedelta(0,604800);   # 1 week
        colNames = ["patient_id","queryItemCountById","verifyItemCountById","outcome.-33","outcome.-32", "outcome.-30"];
        expectedResults = [ RowItemModel([-11111, {-4:2,-10:1,-8:1,-32:1}, {-30:1}, +0,  +2,  +1], colNames ) ];
        analysisResults = list(self.analyzer(analysisQuery));
        self.assertEqualResultDicts( expectedResults, analysisResults, colNames );

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-c","-7","-Q","86400","-V","604800","-t","604800","-o","-33,-32,-31,-30",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualTextOutput(expectedResults, textOutput, colNames);


        # Now include all historical (demographic) data items
        analysisQuery.pastCategoryIds = [-8];
        colNames = ["patient_id","queryItemCountById","verifyItemCountById","outcome.-33","outcome.-32", "outcome.-30"];
        expectedResults = [ RowItemModel([-11111, {-43:1, -45:1, -41:1, -46:1, -4:2,-10:1,-8:1,-32:1}, {-30:1}, +0,  +2,  +1], colNames ) ];
        analysisResults = list(self.analyzer(analysisQuery));
        self.assertEqualResultDicts( expectedResults, analysisResults, colNames );

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-p","-8","-c","-7","-Q","86400","-V","604800","-t","604800","-o","-33,-32,-31,-30",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualTextOutput(expectedResults, textOutput, colNames);



        # Different search where items are recorded with date level instead of time level precision
        # Note that use a verify time threshold of (1 day + 1 second) so can just capture the next day of of data instead of just missing it
        colNames = ["patient_id","baseItemId","queryItemCountById","verifyItemCountById","outcome.-33","outcome.-32", "outcome.-31","outcome.-30"];
        expectedResults = [ RowItemModel([-44444, -21, {-6:1,-12:1}, {-11:1,-8:1}, +0,  +0,  +0,  +0], colNames ) ];

        # Run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-c","-7","-Q","14400","-V","86401","-o","-33,-32,-31,-30",'0,-44444',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualTextOutput(expectedResults, textOutput, colNames);

        # Include background demographics category
        colNames = ["patient_id","baseItemId","queryItemCountById","verifyItemCountById","outcome.-33","outcome.-32", "outcome.-31","outcome.-30"];
        expectedResults = [ RowItemModel([-44444, -21, {-43:1, -45:1, -42:1, -46:1, -6:1,-12:1}, {-11:1,-8:1}, +0,  +0,  +0,  +0], colNames ) ];

        # Run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-p","-8","-c","-7","-Q","14400","-V","86401","-o","-33,-32,-31,-30",'0,-44444',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualTextOutput(expectedResults, textOutput, colNames);


    def test_orderSetAnalysisPreparer(self):
        # Run the analysis preparer against the mock test data above and verify expected data afterwards.
        # Use existing order set usage as reference points
        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-O","-c","-7","-Q","86400","-V","3600",'0,-55555,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        colNames = ["patient_id","baseItemId","queryItemCountById","verifyItemCountById","order_set_id"];
        expectedResults = \
            [   RowItemModel([-55555, -25, {-25:1,-2:1}, {-1:1,-9:1,-5:1,-8:1,-11:1,-12:1}, -1], colNames ), # Diagnosis not in verify items
                RowItemModel([-55555, -25, {-25:1,-2:1,-1:1,-9:1,-5:1}, {-8:1,-11:1,-12:1}, -2], colNames ) # Diagnosis okay to be in query items  
            ];
        self.assertEqualTextOutput(expectedResults, textOutput, colNames);

    def assertEqualResultDicts(self, expectedResults, analysisResults, colNames ):
        self.assertEquals( len(expectedResults), len(analysisResults) );
        for expectedResult, analysisResult in zip(expectedResults,analysisResults):
            self.assertEqualDict(expectedResult, analysisResult, colNames);
    
    def assertEqualTextOutput(self, expectedResults, textOutput, colNames):
        """Convenience function to verify text output from a program to match the provided symbolic expected results,
        by parsing the text into structured fields."""

        headerLine = None;
        while headerLine is None:
            nextLine = textOutput.readline();
            if not nextLine.startswith(COMMENT_TAG):
                headerLine = nextLine;
        headers = headerLine.strip().split("\t");
        
        analysisResults = list();
        for line in textOutput:
            dataChunks = line.strip().split("\t");
            resultModel = RowItemModel( dataChunks, headers );
            # Convert the target elements of interest into numerical values
            for col in colNames:
                if col not in resultModel:
                    # Look for a JSON encoded version
                    jsonCol = "%sJSON" % col;
                    if jsonCol in resultModel:
                        resultModel[col] = loadJSONDict(resultModel[jsonCol], int, int);
                else:
                    resultModel[col] = int(resultModel[col]);
            analysisResults.append(resultModel);        
        
        #for col in colNames:
        #    print >> sys.stderr, col, expectedResults[0][col], analysisResults[0][col]
        
        self.assertEqualStatResults( expectedResults, analysisResults, colNames );


    def test_parsePreparedResultFile(self):
        # Run the analysis preparer against the mock test data above and verify can parse back text file into original object form.

        # Key columns to verify
        colNames = \
            [   "patient_id", 
                "baseItemId",
                "baseItemDate",
                "queryStartTime",
                "queryEndTime",
                "verifyEndTime",
                "queryItemCountById", 
                "verifyItemCountById", 
                "outcome.-33","outcome.-32", "outcome.-31","outcome.-30"
            ];
        
        # Initial run without time limits on outcome measure
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-11111,-44444]);
        analysisQuery.baseCategoryId = -7;
        analysisQuery.queryTimeSpan = timedelta(0,86400);
        analysisQuery.verifyTimeSpan = timedelta(0,604800);
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.targetItemIds = set([-33,-32,-31,-30]);
        analysisQuery.baseRecQuery.excludeItemIds = [-13];
        analysisQuery.baseRecQuery.excludeCategoryIds = [-5];
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data
        directResults = list(self.analyzer(analysisQuery));

        # Redo but run through command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["PreparePatientItems.py","-c","-7","-Q","86400","-V","604800","-o","-33,-32,-31,-30",'0,-11111,-44444',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        textBasedResults = list(self.analyzer.parsePreparedResultFile(textOutput));

        self.assertEqualResultDicts( directResults, textBasedResults, colNames );


    def test_convertResultsFileToFeatureMatrix(self):
        inputFile = StringIO ( \
"""# {"argv": ["medinfo\\cpoe\\analysis\\PreparePatientItems.py", "-c", "2", "-Q", "14400", "-V", "86401", "-o", "27427", "-t", "2592000", "temp\\patientIds.test.tab", "test.out"]}
patient_id\tbaseItemId\tbaseItemDate\tqueryStartTime\tqueryEndTime\tverifyEndTime\tqueryItemCountByIdJSON\tverifyItemCountByIdJSON\toutcome.-1
50559\t-21\t2010-02-04 00:00:00\t2010-02-04 00:00:00\t2010-02-04 04:00:00\t2010-02-05 00:00:01\t{"20449":1, "132":2, "133":3}\t{"19596":1, "19694":1}\t0
52137\t-21\t2013-03-18 00:00:00\t2013-03-18 00:00:00\t2013-03-18 04:00:00\t2013-03-19 00:00:01\t{"20388":1, "19766":10}\t{"19622":4, "19766":7}\t1
35141\t-21\t2012-07-17 00:00:00\t2012-07-17 00:00:00\t2012-07-17 04:00:00\t2012-07-18 00:00:01\t{"13326":1, "5778":1, "13589":1}\t{"19810":1, "19724":1, "13474":1}\t0
19347\t-21\t2010-11-26 00:00:00\t2010-11-26 00:00:00\t2010-11-26 04:00:00\t2010-11-27 00:00:01\t{"13312":1, "19840":1, "13318":1}\t{}\t0
""");
        expectedResults = \
            [   ["patient_id","baseItemId","baseItemDate","queryStartTime","queryEndTime","verifyEndTime",           "outcome.-1",   "132","133","5778","13312","13318","13326","13474","13589","19596","19622","19694","19724","19766","19810","19840","20388","20449"],
                ["50559","-21","2010-02-04 00:00:00","2010-02-04 00:00:00","2010-02-04 04:00:00","2010-02-05 00:00:01","0",    2,      3,     0,      0,      0,      0,      0,      0,      1,      0,      1,      0,      0,      0,      0,      0,      1],
                ["52137","-21","2013-03-18 00:00:00","2013-03-18 00:00:00","2013-03-18 04:00:00","2013-03-19 00:00:01","1",    0,      0,     0,      0,      0,      0,      0,      0,      0,      4,      0,      0,     17,      0,      0,      1,      0],
                ["35141","-21","2012-07-17 00:00:00","2012-07-17 00:00:00","2012-07-17 04:00:00","2012-07-18 00:00:01","0",    0,      0,     1,      0,      0,      1,      1,      1,      0,      0,      0,      1,      0,      1,      0,      0,      0],
                ["19347","-21","2010-11-26 00:00:00","2010-11-26 00:00:00","2010-11-26 04:00:00","2010-11-27 00:00:01","0",    0,      0,     0,      1,      1,      0,      0,      0,      0,      0,      0,      0,      0,      0,      1,      0,      0],
            ];
        
        results = list(self.analyzer.convertResultsFileToFeatureMatrix(inputFile,incHeaders=True) );
        self.assertEqualList(expectedResults,results);

    def test_convertResultsFileToBagOfWordsCorpus(self):
        inputFileStr = \
"""# {"argv": ["medinfo\\cpoe\\analysis\\PreparePatientItems.py", "-c", "2", "-Q", "14400", "-V", "86401", "-o", "27427", "-t", "2592000", "temp\\patientIds.test.tab", "test.out"]}
patient_id\tbaseItemId\tbaseItemDate\tqueryStartTime\tqueryEndTime\tverifyEndTime\tqueryItemCountByIdJSON\tverifyItemCountByIdJSON\toutcome.-1
50559\t-21\t2010-02-04 00:00:00\t2010-02-04 00:00:00\t2010-02-04 04:00:00\t2010-02-05 00:00:01\t{"20449":1, "132":2, "133":3}\t{"19596":1, "19694":1}\t0
52137\t-21\t2013-03-18 00:00:00\t2013-03-18 00:00:00\t2013-03-18 04:00:00\t2013-03-19 00:00:01\t{"20388":1, "19766":10}\t{"19622":4, "19766":7}\t1
35141\t-21\t2012-07-17 00:00:00\t2012-07-17 00:00:00\t2012-07-17 04:00:00\t2012-07-18 00:00:01\t{"13326":1, "5778":1, "13589":1}\t{"19810":1, "19724":1, "13474":1}\t0
19347\t-21\t2010-11-26 00:00:00\t2010-11-26 00:00:00\t2010-11-26 04:00:00\t2010-11-27 00:00:01\t{"13312":1, "19840":1, "13318":1}\t{}\t0
""";
        expectedResults = \
            [   [(-1,0),(20449,1),(132,2),(133,3),(19596,1),(19694,1)],
                [(-1,1),(20388,1),(19766,17),(19622,4)],
                [(-1,0),(13326,1),(5778,1),(13589,1),(19810,1),(19724,1),(13474,1)],
                [(-1,0),(13312,1),(19840,1),(13318,1)],
            ];
        results = list(self.analyzer.convertResultsFileToBagOfWordsCorpus(StringIO(inputFileStr),queryItems=True,verifyItems=True,outcomeItems=True) );
        self.assertEqualBagOfWordsList(expectedResults,results);

        expectedResults = \
            [   [(20449,1),(132,2),(133,3)],
                [(20388,1),(19766,10)],
                [(13326,1),(5778,1),(13589,1)],
                [(13312,1),(19840,1),(13318,1)],
            ];
        results = list(self.analyzer.convertResultsFileToBagOfWordsCorpus(StringIO(inputFileStr),queryItems=True,verifyItems=False,outcomeItems=False) );
        self.assertEqualBagOfWordsList(expectedResults,results);

        expectedResults = \
            [   [(19596,1),(19694,1)],
                [(19622,4),(19766,7)],
                [(19810,1),(19724,1),(13474,1)],
                [],
            ];
        results = list(self.analyzer.convertResultsFileToBagOfWordsCorpus(StringIO(inputFileStr),queryItems=False,verifyItems=True,outcomeItems=False) );
        self.assertEqualBagOfWordsList(expectedResults,results);

    def assertEqualBagOfWordsList(self, expectedResults, results ):
        """Convert random order Bag of Words items into consistent dictionaries for comparison"""
        for i, result in enumerate(expectedResults):
            expectedResults[i] = self.analyzer.bagOfWordsToCountById(result);
        for i, result in enumerate(results):
            results[i] = self.analyzer.bagOfWordsToCountById(result);
        self.assertEqualList(expectedResults, results);
    
def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestItemRecommender("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestItemRecommender("test_insertFile_skipErrors"));
    #suite.addTest(TestItemRecommender('test_executeIterator'));
    #suite.addTest(TestPreparePatientItems('test_analysisPreparation'));
    #suite.addTest(TestPreparePatientItems('test_parsePreparedResultFile'));
    #suite.addTest(TestPreparePatientItems('test_convertResultsFileToBagOfWordsCorpus'));
    #suite.addTest(TestPreparePatientItems('test_analysisPreparation'));
    #suite.addTest(TestPreparePatientItems('test_orderSetAnalysisPreparer'));
    suite.addTest(unittest.makeSuite(TestPreparePatientItems));
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
