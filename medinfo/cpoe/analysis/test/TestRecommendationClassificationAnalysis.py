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
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;

from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender;
from medinfo.cpoe.analysis.RecommendationClassificationAnalysis import RecommendationClassificationAnalysis, AnalysisQuery;
from medinfo.cpoe.analysis.PreparePatientItems import PreparePatientItems;

TEST_ORDERSET_ID = -3;

class TestRecommendationClassificationAnalysis(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        
        self.clinicalItemCategoryIdStrList = list();
        headers = ["clinical_item_category_id","default_recommend","source_table"];
        dataModels = \
            [   
                RowItemModel( [-1, 1, "Labs"], headers ),
                RowItemModel( [-2, 1, "Imaging"], headers ),
                RowItemModel( [-3, 1, "Meds"], headers ),
                RowItemModel( [-4, 0, "Nursing"], headers ),    # Disable default recommend to allow for checks
                RowItemModel( [-5, 0, "Problems"], headers ),
                RowItemModel( [-6, 1, "Lab Results"], headers ),
                RowItemModel( [-7, 1, "Admit Dx"], headers ),
                RowItemModel( [-8, 0, "Demographics"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );
            self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

        headers = ["clinical_item_id","clinical_item_category_id","default_recommend","item_count","name"];
        dataModels = \
            [   
                RowItemModel( [-1, -1, 1, 30, "CBC"], headers ),
                RowItemModel( [-2, -1, 1, 30, "BMP"], headers ),
                RowItemModel( [-3, -1, 1, 95, "Hepatic Panel"], headers ),
                RowItemModel( [-4, -1, 1, 40, "Cardiac Enzymes"], headers ),
                RowItemModel( [-5, -2, 1, 40, "CXR"], headers ),
                RowItemModel( [-6, -2, 1, 70, "RUQ Ultrasound"], headers ),
                RowItemModel( [-7, -2, 1, 70, "CT Abdomen/Pelvis"], headers ),
                RowItemModel( [-8, -2, 1, 35, "CT PE Thorax"], headers ),   
                RowItemModel( [-9, -3,  1, 0, "Acetaminophen"], headers ),
                RowItemModel( [-10, -3, 1, 45, "Carvedilol"], headers ),
                RowItemModel( [-11, -3, 1, 50, "Enoxaparin"], headers ),
                RowItemModel( [-12, -3, 1, 75, "Warfarin"], headers ),
                RowItemModel( [-13, -3, 0,  0, "Ceftriaxone"], headers ),   # Disable default recommend to allow for checks
                RowItemModel( [-14, -4, 1,  0, "Foley Catheter"], headers ),
                RowItemModel( [-15, -4, 1,  0, "Strict I&O"], headers ),
                RowItemModel( [-16, -4, 1,  0, "Fall Precautions"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

        headers = ["patient_item_id","patient_id","clinical_item_id","item_date","analyze_date"];
        dataModels = \
            [   
                RowItemModel( [-1,  -11111, -4,  datetime(2000, 1, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-2,  -11111, -10, datetime(2000, 1, 1, 1), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-3,  -11111, -8,  datetime(2000, 1, 1, 2), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-5,  -11111, -12, datetime(2000, 2, 1, 0), datetime(2010, 1, 1, 0)], headers ),
                RowItemModel( [-6,  -11111, -6,  datetime(2000, 2, 1, 1), datetime(2010, 1, 1, 0)], headers ),
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
                RowItemModel( [ -4, -4,   40, 40, 40, 40, 40,  0.0, 0.0], headers ),
                RowItemModel( [ -5, -5,   40, 40, 50, 50, 50,  0.0, 0.0], headers ),
                RowItemModel( [ -6, -6,   70, 70, 70, 70, 70,  0.0, 0.0], headers ),
                RowItemModel( [ -7, -7,   70, 70, 70, 70, 70,  0.0, 0.0], headers ),
                RowItemModel( [ -8, -8,   35, 35, 35, 50, 80,  0.0, 0.0], headers ),
                RowItemModel( [-10,-10,   45, 45, 55, 60, 90,  0.0, 0.0], headers ),
                RowItemModel( [-11,-11,   50, 50, 50, 80, 90,  0.0, 0.0], headers ),
                RowItemModel( [-12,-12,   75, 75, 75, 80, 90,  0.0, 0.0], headers ),

                RowItemModel( [ -2, -4,    0,  2,  3,  3,  3,  200.0, 50000.0], headers ),
                RowItemModel( [ -2, -6,    2,  2,  5,  5,  5,  300.0, 11990.0], headers ),
                RowItemModel( [ -3, -1,   20, 23, 23, 23, 23,  400.0, 344990.0], headers ),
                RowItemModel( [ -4, -5,    3,  3, 13, 43, 43,  340.0, 343110.0], headers ),
                RowItemModel( [ -4, -6,   23, 33, 33, 33, 63,  420.0, 245220.0], headers ),
                RowItemModel( [ -4, -7,   27, 33, 33, 33, 63,   40.0, 5420.0], headers ),
                RowItemModel( [ -4,-10,   25, 35, 40, 45, 63,   47.0, 5420.0], headers ),
                RowItemModel( [ -5, -4,    0,  0, 20, 20, 20,  540.0, 54250.0], headers ),
                RowItemModel( [ -8,-12,    15,15, 15, 15, 15,   25.0,  520.0], headers ),
                RowItemModel( [ -10,-11,   12,12, 16, 16, 20,   20.0,  220.0], headers ),
                RowItemModel( [ -10,-12,   10,10, 10, 10, 10,   20.0,  120.0], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_association", dataModel );

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
-9;-3;Test Order Set - 3;Meds;RandomMeds
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
-20;-9;-11;4
-21;-9;-12;4
-22;-9;-13;4
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "item_collection_item", delim=";");

        # Instance to test on
        self.analyzer = RecommendationClassificationAnalysis();
        self.preparer = PreparePatientItems();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute("delete from patient_item_collection_link where patient_item_collection_link_id < 0");
        DBUtil.execute("delete from item_collection_item where item_collection_item_id < 0");
        DBUtil.execute("delete from item_collection where item_collection_id < 0");

        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
        DBUtil.execute("delete from patient_item where patient_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );
        
        DBTestCase.tearDown(self);

    def test_recommenderAnalysis(self):
        # Run the recommender against the mock test data above and verify expected stats afterwards.
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-11111]);
        analysisQuery.numQueryItems = 1;
        analysisQuery.numVerifyItems = 3;
        analysisQuery.numRecommendations = 4;
        analysisQuery.recommender = BaselineFrequencyRecommender();
        #analysisQuery.recommender = ItemAssociationRecommender();
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data

        # Don't use items whose default is to be excluded from recommendations
        analysisQuery.baseRecQuery.excludeCategoryIds = analysisQuery.recommender.defaultExcludedClinicalItemCategoryIds();
        analysisQuery.baseRecQuery.excludeItemIds = analysisQuery.recommender.defaultExcludedClinicalItemIds();
        #recQuery.timeDeltaMax = timedelta(0, int(self.requestData["timeDeltaMax"]) );  # Time delta to use for queries, otherwise just default to all times

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "normalRecall","normalPrecision", "ROC-AUC"];
        
        # Start with default recommender
        expectedResults = [ RowItemModel([-11111,  1,2,3,  0.333, 0.25, 0.286,  0.208, 0.254, 0.333/1.0, 0.25/0.75, 0.524], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line interface
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-q","1","-v","3","-r","4","-m","0","-R","BaselineFrequencyRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","1","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","BaselineFrequencyRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


        
       
        # Now try targeted recommender
        analysisQuery.recommender = ItemAssociationRecommender();
        expectedResults = [ RowItemModel([-11111,  1,2,3,  0.333, 0.25, 0.286,  0.347, 0.293, 0.333, 0.25/0.75, 0.6666], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-q","1","-v","3","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","1","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);




        # Now try multiple query items targeted recommender
        analysisQuery.numQueryItems = 2;
        expectedResults = [ RowItemModel([-11111, 1, 2, 3,  0.333, 0.25, 0.286,  0.254, 0.194, 0.333, 0.25/0.75, 0.4167], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-q","2","-v","3","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","2","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);



        # More query items with aggregation options
        analysisQuery.numQueryItems = 3;
        expectedResults = [ RowItemModel([-11111, 1, 1, 3,   0.5, 0.25, 0.333,  0.517, 0.194, 0.5, 0.25/0.5, 0.4166], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-q","3","-v","3","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","3","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);






        # Value filters
        analysisQuery.baseRecQuery.sortField= "freqRatio";
        analysisQuery.baseRecQuery.fieldFilters["freqRatio>"] = 70;
        expectedResults = [ RowItemModel([-11111, 2, 0, 2,   1.0, 0.5, 0.6666,  1.0, 0.446, 1.0, 0.5/0.5, 0.375], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);
        del analysisQuery.baseRecQuery.fieldFilters["freqRatio>"];  # Undo to not affect subsequent queries

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-s","freqRatio","-f","freqRatio>:70.0","-q","3","-v","3","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","3","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender","-s","freqRatio","-f","freqRatio>:70.0",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);





        # Unweighted aggregation
        analysisQuery.baseRecQuery.weightingMethod = "unweighted";
        expectedResults = [ RowItemModel([-11111, 1, 1, 3,   0.5, 0.25, 0.3333,  0.517, 0.194, 0.5, 0.25/0.5, 0.25], colNames ) ];
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-s","freqRatio","-q","3","-v","3","-r","4","-m","0","-R","ItemAssociationRecommender","-a","unweighted",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","3","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-s","freqRatio","-P","-r","4","-m","0","-R","ItemAssociationRecommender","-a","unweighted",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);




        # Run by equivalent query time span selection rather than explicit counts
        colNames = ["patient_id", "baseItemId", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "ROC-AUC"];
        expectedResults = [ RowItemModel([-11111, -4, 1, 1, 3,   0.5, 0.25, 0.333,  0.517, 0.194, 0.4167], colNames ) ];

        analysisQuery.baseRecQuery.sortField= "conditionalFreq";
        analysisQuery.numQueryItems = None;
        analysisQuery.numVerifyItems = None;
        analysisQuery.baseCategoryId = -1;
        analysisQuery.queryTimeSpan = timedelta(0,3*60*60);
        analysisQuery.verifyTimeSpan = timedelta(50,0);
        analysisQuery.numRecommendations = 4;
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-c","-1","-Q","5400","-V","4320000","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-c","-1","-Q","5400","-V","4320000",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);



        # Run by query time span by identifying base clinical item, rather than a general category
        analysisQuery.numQueryItems = None;
        analysisQuery.numVerifyItems = None;
        analysisQuery.baseCategoryId = None;    # Clear prior setting
        analysisQuery.baseItemId = -4;
        analysisQuery.queryTimeSpan = timedelta(0,3*60*60);
        analysisQuery.verifyTimeSpan = timedelta(50,0);
        analysisQuery.numRecommendations = 4;
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-b","-4","-Q","5400","-V","4320000","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-b","-4","-Q","5400","-V","4320000",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);




        # Basic then Filter test data date range
        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "ROC-AUC"];
        expectedResults = [ RowItemModel([-11111, 1, 1, 3,   0.5, 0.25, 0.33333,  0.4375, 0.29319, 0.66667], colNames ) ];
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-11111]);
        analysisQuery.numQueryItems = 1;
        analysisQuery.numVerifyItems = 2;
        analysisQuery.numRecommendations = 4;
        analysisQuery.recommender = ItemAssociationRecommender();
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-q","1","-v","2","-r","4","-m","0","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","1","-v","2",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);



        # Date Filters
        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "ROC-AUC"];
        expectedResults = [ RowItemModel([-11111, 0, 1, 2,   0.0, 0.0, 0.0,  0.0, 0.0, None], colNames ) ];
        analysisQuery = AnalysisQuery();
        analysisQuery.patientIds = set([-11111]);
        analysisQuery.numQueryItems = 1;
        analysisQuery.numVerifyItems = 2;
        analysisQuery.numRecommendations = 4;
        analysisQuery.recommender = ItemAssociationRecommender();
        analysisQuery.baseRecQuery = RecommenderQuery();
        analysisQuery.baseRecQuery.maxRecommendedId = 0; # Restrict to test data
        analysisQuery.startDate = datetime(2000,1,1,1);
        analysisQuery.endDate = datetime(2000,1,10);
        analysisResults = self.analyzer(analysisQuery);
        self.assertEqualStatResults(expectedResults, analysisResults, colNames);

        # Redo with command-line
        sys.stdout = StringIO();    # Redirect stdout output to collect test results
        argv = ["RecommendationClassificationAnalysis.py","-q","1","-v","2","-r","4","-m","0","-S","2000-01-01 01:00:00","-E","2000-01-10","-R","ItemAssociationRecommender",'0,-11111',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);

        # Redo through prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","1","-v","2","-S","2000-01-01 01:00:00","-E","2000-01-10",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        argv = ["RecommendationClassificationAnalysis.py","-P","-r","4","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);


    def test_numRecsByOrderSet(self):
        # Designate number of recommendations indirectly via linked order set id 

        DBUtil.execute("update clinical_item set default_recommend = 0 where clinical_item_id = -8");   # Disable default recommend on one item to shift results

        colNames = ["patient_id", "TP", "FN", "FP",  "recall", "precision", "F1-score", "weightRecall","weightPrecision", "ROC-AUC"];
        expectedResults = [ RowItemModel([-11111, 2, 0, 3, 1.0, 0.4, 0.571,  1.0, 0.3178, 0.4167], colNames ) ];

        # Do through fabricated prepared file intermediary
        sys.stdout = StringIO();    
        argv = ["PreparePatientItems.py","-q","2","-v","3",'0,-11111',"-"];
        self.preparer.main(argv);
        preparedDataFile = StringIO(sys.stdout.getvalue());
        
        # Artificially add a key order set ID for the fabricated data
        modFile = StringIO();
        formatter = TextResultsFormatter(modFile);
        dataCols = None;
        for i, dataRow in enumerate(TabDictReader(preparedDataFile)):
            dataRow["order_set_id"] = TEST_ORDERSET_ID;
            if i <= 0:
                dataCols = list(dataRow.keys());
                formatter.formatTuple(dataCols);    # Insert a mock record to get a header / label row
            formatter.formatResultDict(dataRow, dataCols);
        preparedDataFile = StringIO(modFile.getvalue());

        sys.stdin = preparedDataFile;   # Read prepared data file from redirected stdin
        sys.stdout = StringIO();
        #argv = ["RecommendationClassificationAnalysis.py","-P","-r","5","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        argv = ["RecommendationClassificationAnalysis.py","-P","--numRecsByOrderSet","-m","0","-R","ItemAssociationRecommender",'-',"-"];
        self.analyzer.main(argv);
        textOutput = StringIO(sys.stdout.getvalue());
        self.assertEqualStatResultsTextOutput(expectedResults, textOutput, colNames);






def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestRecommendationClassificationAnalysis("test_numRecsByOrderSet"));
    #suite.addTest(TestRecommendationClassificationAnalysis("test_recommenderAnalysis"));
    #suite.addTest(TestRecommendationClassificationAnalysis('test_executeIterator'));
    #suite.addTest(TestRecommendationClassificationAnalysis('test_recommenderAnalysis_commandLine'));
    suite.addTest(unittest.makeSuite(TestRecommendationClassificationAnalysis));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
