#!/usr/bin/env python
"""
Analysis module to assess results of ItemRecommender.
Rough approach
- Input patient IDs to test against
- Query recommender based on first X orders / items for each patient
- Compare recommended items against the remaining items for each patient
- Calculate and report stats based on above (precision, recall, etc.)

"""

import sys, os
import time;
from optparse import OptionParser;
import json;
from io import StringIO;
from math import sqrt;
from datetime import timedelta;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, loadJSONDict;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.analysis.ROCPlot import ROCPlot;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender, RandomItemRecommender;
from medinfo.cpoe.OrderSetRecommender import OrderSetRecommender;
from .Util import log;

from .BaseCPOEAnalysis import BaseCPOEAnalysis;
from .BaseCPOEAnalysis import RECOMMENDER_CLASS_LIST, RECOMMENDER_CLASS_BY_NAME, AnalysisQuery;
from .BaseCPOEAnalysis import AGGREGATOR_OPTIONS;

from .PreparePatientItems import PreparePatientItems;

class RecommendationClassificationAnalysis(BaseCPOEAnalysis):
    """Driver class to review given patient data and run sample recommendation queries against
    them and collect comparison statistics between the recommended items vs. the patients'
    actual subsequent orders / items.
    """
    def __init__(self):
        BaseCPOEAnalysis.__init__(self);
        self.supportRecommender = OrderSetRecommender();

    def __call__(self, analysisQuery, conn=None):
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;

        try:
            # Preload some lookup data to facilitate subsequent checks
            baseCountByItemId = self.dataManager.loadClinicalItemBaseCountByItemId(conn=conn);

            # Recommender to test with
            recommender = analysisQuery.recommender;

            # Start building basic recommendation query to use for testing
            recQuery = analysisQuery.baseRecQuery;

            # Start building results data
            resultsStatDataList = list();
            progress = ProgressDots(50,1,"Patients");

            # Query for all of the order / item data for the test patients.  Load one patient's data at a time
            preparer = PreparePatientItems();
            for patientItemData in preparer.loadPatientItemData(analysisQuery, conn=conn):
                patientId = patientItemData["patient_id"];

                analysisResults = \
                    self.analyzePatientItems \
                    (   patientItemData,
                        analysisQuery,
                        recQuery,
                        patientId,
                        recommender,
                        preparer,
                        conn=conn
                    );

                if analysisResults is not None:
                    (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData) = analysisResults;  # Unpack results
                    # Start aggregating and calculating result stats
                    resultsStatData = self.calculateResultStats( patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, baseCountByItemId, recQuery, recommendedData );
                    if "baseItemId" in patientItemData:
                        analysisQuery.baseItemId = patientItemData["baseItemId"]; # Record something here, so know to report back in result headers
                    resultsStatDataList.append(resultsStatData);

                progress.Update();
            # progress.PrintStatus();

            return resultsStatDataList;

        finally:
            if not extConn:
                conn.close();


    def analyzePatientItems(self, patientItemData, analysisQuery, recQuery, patientId, recommender, preparer, conn):
        """Given the primary query data and clinical item list for a given test patient,
        Parse through the item list and run a query to get the top recommended IDs
        to produce the relevant verify and recommendation item ID sets for comparison
        """

        if "queryItemCountById" not in patientItemData:
            # Apparently not able to find / extract relevant data, so skip this record
            return None;
        queryItemCountById = patientItemData["queryItemCountById"];
        verifyItemCountById = patientItemData["verifyItemCountById"];

        recQuery.queryItemIds = list(queryItemCountById.keys());
        recQuery.targetItemIds = set(); # Ensure not restricted to some specified outcome target

        # Query for recommended orders / items
        recommendedData = recommender( recQuery, conn=conn );

        # Customize number of recommendations if comparing against specific order set usage
        self.customizeNumRecommendations(patientItemData, analysisQuery, recQuery, preparer);

        # Distill down to just the set of recommended item IDs
        recommendedItemIds = set();
        for i, recommendationModel in enumerate(recommendedData):
            if i >= analysisQuery.numRecommendations:
                break;
            recommendedItemIds.add(recommendationModel["clinical_item_id"]);

        return (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData);

    def customizeNumRecommendations(self, patientItemData, analysisQuery, recQuery, preparer):
        """If option set, customize number of recommendations to consider
        to match the number available in order sets being used at the given evaluation point.
        """
        if analysisQuery.numRecsByOrderSet:
            # Pre-cache order set item data
            if self.supportRecommender.itemIdsByOrderSetId is None:
                self.supportRecommender.initItemLookups(analysisQuery.baseRecQuery);
            orderSetId = patientItemData["order_set_id"];
            analysisQuery.numRecommendations = 0;
            for itemId in self.supportRecommender.itemIdsByOrderSetId[orderSetId]:
                if preparer.isItemRecommendable(itemId, None, recQuery, preparer.categoryIdByItemId):
                    analysisQuery.numRecommendations += 1;


    def calculateResultStats( self, patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, baseCountByItemId, recQuery, recommendedData ):
        """Given the summarized item ID lists for a given patient:
            - queryItemIds: Clinical item IDs from patient's initial data to query recommendations based on
            - verifyItemIds: Subsequent item IDs from patient after query to verify recommendations against
            - recommendedItemIds: Item IDs that were actually offerred by recommendation system based on query set
            - baseCountByItemId: Lookup table to quickly find baseline counts for each clinical item to facilitate weighted scoring
            - recQuery: Query object used to generate recommendations so can trace back some parameters
            - recommendedData: Full list of all possible item recommendation data models to allow for ROC AUC calculation
        Return results in a dictionary structure while also calculating additional summary statistics:
            - numQueryItems: Count of queryItemIds
            - numVerifyItems: Count of verifyItemIds
            - numRecommendedItems: Count of recommendedItemIds

            - TP: Number of True Positives (items in both the recommended and verify sets)
            - FN: Number of False Negatives (items in verify set, but not recommended)
            - FP: Number of False Positives (items recommended, but not in verify set)
                (Note TN: True Negatives not recorded since this would generally be a much larger number representing all of the possible >2000 orders/items that are neither used in the verify set or recommended in the recommendation set)
            - recall = sensitivity: TP / (TP + FN)
            - precision = PPV (positive predictive value): TP / (TP + FP)
            - F1-score:  2*precision*recall / (precision+recall)

            - ROC-AUC: ROC area-under-curve

        Additional result stat set that provides weighted scores to correct predictions / classifications.
            Instead of getting "1 point" for correctly classifying an item, get a weighted point inversely
            proportional to the baseline frequency of the item.  In this way, give more credit
            for correctly classifying rare items, and not so much credit for common items.
            Would expect items weighted by likelihood ratio (freqRatio) to do better in this circumstance.
        """
        stats = RowItemModel();
        stats["patient_id"] = patientItemData["patient_id"];
        if "baseItemId" in patientItemData:
            stats["baseItemId"] = patientItemData["baseItemId"];
        if "order_set_id" in patientItemData:
            stats["order_set_id"] = patientItemData["order_set_id"];
        stats["queryItemIds"] = list(queryItemCountById.keys());
        stats["verifyItemIds"] = list(verifyItemCountById.keys());
        stats["recommendedItemIds"] = recommendedItemIds;
        stats["numQueryItems"] = len(queryItemCountById);
        stats["numVerifyItems"] = len(verifyItemCountById);
        stats["numRecommendedItems"] = len(recommendedItemIds);

        verifyItemIds = set(stats["verifyItemIds"]);    # Convenience reference in set form for set operators (intersection)

        stats["TP"] = len(verifyItemIds.intersection(recommendedItemIds));
        stats["FN"] = stats["numVerifyItems"] - stats["TP"];
        stats["FP"] = stats["numRecommendedItems"] - stats["TP"];

        stats["recall"] = stats["sensitivity"] = None;
        if (stats["TP"]+stats["FN"]) > 0:
            stats["recall"] = stats["sensitivity"] = float(stats["TP"]) / (stats["TP"]+stats["FN"]);
        stats["precision"] = stats["PPV"] = None;
        if (stats["TP"]+stats["FP"]) > 0:
            stats["precision"] = stats["PPV"] = float(stats["TP"]) / (stats["TP"]+stats["FP"]);

        stats["F1-score"] = None;
        if stats["precision"] is not None and stats["recall"] is not None:
            stats["F1-score"] = 0.0;
            if (stats["precision"]+stats["recall"]) > 0:
                stats["F1-score"] = 2*stats["precision"]*stats["recall"] / (stats["precision"]+stats["recall"]);

        # Normalized scores (comparable to normalized discounted cumulative gain NDCG) relative to max possible values given sizes of query, verify, and recommended sets
        # Normalized Precision and Normalized Recall should end up being numerically equal to: TP / min(numVerifyItems,numRecommendedItems)
        stats["idealPrecision"] = 1.0;
        stats["idealRecall"] = 1.0;
        stats["normalPrecision"] = None;
        stats["normalRecall"] = None;
        if stats["numRecommendedItems"] > 0:
            stats["idealPrecision"] = min(1.0, float(stats["numVerifyItems"])/stats["numRecommendedItems"] );   # Best possible precision
        if stats["numVerifyItems"] > 0:
            stats["idealRecall"] = min(1.0, float(stats["numRecommendedItems"])/stats["numVerifyItems"] );   # Best possible recall
        if stats["idealPrecision"]>0 and stats["precision"] is not None:
            stats["normalPrecision"] = stats["precision"] / stats["idealPrecision"];
        if stats["idealRecall"] >0 and stats["recall"] is not None:
            stats["normalRecall"] = stats["recall"] / stats["idealRecall"];
        #stats["normalPrecision"] = float(stats["TP"]) / min(stats["numVerifyItems"],stats["numRecommendedItems"]);
        #stats["normalRecall"] = stats["normalPrecision"];

        # Calculated weighted scores
        weightByVerifyItemId = dict();
        for itemId in verifyItemIds:
            baseCount = 0;
            if itemId in baseCountByItemId:
                baseCount = baseCountByItemId[itemId];
            if baseCount <= 0: baseCount = 0.5; # Normalization to avoid possible divide by zero
            weightByVerifyItemId[itemId] = 1.0/baseCount;
        stats["weightVerifyItems"] = sum(weightByVerifyItemId.values());

        weightByRecommendedItemId = dict();
        for itemId in recommendedItemIds:
            baseCount = 0;
            if itemId in baseCountByItemId:
                baseCount = baseCountByItemId[itemId];
            if baseCount <= 0: baseCount = 0.5; # Normalization to avoid possible divide by zero
            weightByRecommendedItemId[itemId] = 1.0/baseCount;
        stats["weightRecommendedItems"] = sum(weightByRecommendedItemId.values());

        stats["weightTP"] = 0.0;
        for itemId in verifyItemIds.intersection(recommendedItemIds):
            baseCount = 0;
            if itemId in baseCountByItemId:
                baseCount = baseCountByItemId[itemId];
            if baseCount <= 0: baseCount = 0.5; # Normalization to avoid possible divide by zero
            stats["weightTP"] += 1.0/baseCount;

        stats["weightFN"] = stats["weightVerifyItems"] - stats["weightTP"];
        stats["weightFP"] = stats["weightRecommendedItems"] - stats["weightTP"];

        stats["weightRecall"] = stats["weightSensitivity"] = None;
        if (stats["weightTP"]+stats["weightFN"]) > 0:
            stats["weightRecall"] = stats["weightSensitivity"] = float(stats["weightTP"]) / (stats["weightTP"]+stats["weightFN"]);
        stats["weightPrecision"] = stats["weightPPV"] = None;
        if (stats["weightTP"]+stats["weightFP"]) > 0:
            stats["weightPrecision"] = stats["weightPPV"] = float(stats["weightTP"]) / (stats["weightTP"]+stats["weightFP"]);

        stats["weightF1-score"] = None;
        if stats["weightPrecision"] is not None and stats["weightRecall"] is not None:
            stats["weightF1-score"] = 0.0;
            if (stats["weightPrecision"]+stats["weightRecall"]) > 0:
                stats["weightF1-score"] = 2*stats["weightPrecision"]*stats["weightRecall"] / (stats["weightPrecision"]+stats["weightRecall"]);

        # Convert sets into more easily readable, sorted tuples
        stats["queryItemIdTuple"] = list(stats["queryItemIds"]);
        stats["queryItemIdTuple"].sort();
        stats["queryItemIdTuple"] = tuple(stats["queryItemIdTuple"]);

        stats["verifyItemIdTuple"] = list(stats["verifyItemIds"]);
        stats["verifyItemIdTuple"].sort();
        stats["verifyItemIdTuple"] = tuple(stats["verifyItemIdTuple"]);

        stats["recommendedItemIdTuple"] = list(stats["recommendedItemIds"]);
        stats["recommendedItemIdTuple"].sort();
        stats["recommendedItemIdTuple"] = tuple(stats["recommendedItemIdTuple"]);

        try:
            # Build list of outcome results and scores to generate ROC curve analysis
            outcomes = list();
            scores = list();
            for recommendedItemModel in recommendedData:
                score = 0.0;
                if recQuery.sortField in recommendedItemModel:
                    score = recommendedItemModel[recQuery.sortField];
                else:
                    score = recommendedItemModel["score"];
                outcomes.append( recommendedItemModel["clinical_item_id"] in verifyItemIds );
                scores.append( score );

            stats["ROC-AUC"] = ROCPlot.aucScore(outcomes,scores);
        except ValueError:
            # Undefined ROC score when all outcomes of same value (i.e., no verify items, so all recommendations are false)
            stats["ROC-AUC"] = None;

        return stats;

    def resultHeaders(self, analysisQuery=None):
        headers = \
            [   "patient_id",
                "queryItemIdTuple",
                "verifyItemIdTuple",
                "recommendedItemIdTuple",
                "numQueryItems",
                "numVerifyItems",
                "numRecommendedItems",
                "TP", "FN", "FP",
                "recall", "precision", "F1-score",
                "weightRecall", "weightPrecision", "weightF1-score",
                "normalRecall","normalPrecision",
                "ROC-AUC",
            ];
        if analysisQuery is not None and (analysisQuery.baseCategoryId is not None or analysisQuery.baseItemId is not None):
            headers.append("baseItemId");
        if analysisQuery is not None and analysisQuery.numRecsByOrderSet:
            headers.append("order_set_id");
        return headers;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <patientIds/dataFile> [<outputFile>]\n"+\
                    "   <patientIds/dataFile>    Name of file with patient ids.  If not found, then interpret as comma-separated list of test Patient IDs to prepare analysis data for.  Alternatively, provide preparedPatientItemFile generated from PreparePatientItems as input.\n"+\
                    "   <outputFile>    If query yields a result set, then that will be output\n"+\
                    "                       to the named file.  Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-q", "--numQuery",  dest="numQuery",  help="Number of orders / items from each patient to use as query items to prime the recommendations.  If set to a float number in (0,1), then treat as a percentage of the patient's total orders / items");
        parser.add_option("-v", "--numVerify", dest="numVerify", help="Number of orders / items from each patient after the query items to use to validate recommendations.  If set to a float number in (0,1), then treat as a percentage of the patient's total orders / items.  If left unset, then just use all remaining orders / items for that patient");
        parser.add_option("-c", "--baseCategoryId",  dest="baseCategoryId",  help="Instead of specifying first nQ query items, specify ID of clinical item category to look for initial items from (probably the ADMIT Dx item).");
        parser.add_option("-b", "--baseItemId",  dest="baseItemId",  help="Instead of specifying first nQ query items, specify ID of the specific clinical item to look for initial items from.");
        parser.add_option("-S", "--startDate",  dest="startDate",  help="Only look for test data occuring on or after this start date.");
        parser.add_option("-E", "--endDate",  dest="endDate",  help="Only look for test data occuring before this end date.");
        parser.add_option("-Q", "--queryTimeSpan",  dest="queryTimeSpan",  help="Time frame specified in seconds over which to look for initial query items (e.g., 24hrs = 86400) after the base item found from the category above.  Start the time counting from the first item time occuring after the category item above since the ADMIT Dx items are often keyed to dates only without times (defaulting to midnight of the date specified).");
        parser.add_option("-V", "--verifyTimeSpan",  dest="verifyTimeSpan",  help="Time frame specified in seconds over which to look for verify items after initial query item time.  Will ignore the query items that occur within the queryTimeSpan.");

        parser.add_option("-P", "--preparedPatientItemFile",  dest="preparedPatientItemFile", action="store_true", help="If set, will expect primary argument to instead be name of file to read input data from, instead of using above parameters to query from database.");

        parser.add_option("-R", "--recommender",  dest="recommender",  help="Name of the recommender to run the analysis against.  Options: %s" % list(RECOMMENDER_CLASS_BY_NAME.keys()));
        parser.add_option("-r", "--numRecs",   dest="numRecs",  help="Number of orders / items to recommend for comparison against the verification set. Alternative set option numRecsByOrderSet to look for key order set usage and size.");
        parser.add_option("-O", "--numRecsByOrderSet",   dest="numRecsByOrderSet", action="store_true", help="If set, then look for an order_set_id column to find the key order set that triggered the evaluation time point to determine number of recommendations to consider.");
        parser.add_option("-s", "--sortField",  dest="sortField",  help="Allow overriding of default sort field when returning ranked results");
        parser.add_option("-f", "--fieldFilters",  dest="fieldFilters",  help="Filters to exclude results.  Comma-separated separated list of field-op:value exclusions where op is either < or > like, conditionalFreq<:0.1,frqeRatio<:1");
        parser.add_option("-t", "--timeDeltaMax",  dest="timeDeltaMax",  help="If set, represents a time delta in seconds maximum by which recommendations should be based on.  Defaults to recommending items that occur at ANY time after the key orders.  If provided, will apply limits to only orders placed within 0 seconds, 1 hour (3600), 1 day (86400), or 1 week (604800) of the key orders / items.");
        parser.add_option("-a", "--aggregationMethod",  dest="aggregationMethod",  help="Aggregation method to use for recommendations based off multiple query items.  Options: %s." % list(AGGREGATOR_OPTIONS) );
        parser.add_option("-p", "--countPrefix",  dest="countPrefix",  help="Prefix for how to do counts.  Blank for default item counting allowing repeats, otherwise ignore repeats for patient_ or encounter_");
        parser.add_option("-m", "--maxRecommendedId",  dest="maxRecommendedId",  help="Specify a maximum ID value to accept for recommended items.  More used to limit output in test cases");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) >= 1:
            # Parse out the query parameters
            query = AnalysisQuery();
            query.recommender = RECOMMENDER_CLASS_BY_NAME[options.recommender]();
            query.recommender.dataManager.dataCache = dict();   # Use a dataCache to facilitate repeat queries

            if options.preparedPatientItemFile:
                # Don't reconstruct validation data through database, just read off validation file
                query.preparedPatientItemFile = stdOpen(args[0]);
            else:
                patientIdsParam = args[0];
                try:
                    # Try to open patient IDs as a file
                    patientIdFile = stdOpen(patientIdsParam);
                    query.patientIds = set( patientIdFile.read().split() );
                except IOError:
                    # Unable to open as a filename, then interpret as simple comma-separated list
                    query.patientIds = set(patientIdsParam.split(","));

                if options.numQuery is not None:
                    query.numQueryItems = int(options.numQuery);
                    query.numVerifyItems = int(options.numVerify);
                else:
                    # Alternative to specify query time span starting from a key category
                    query.queryTimeSpan = timedelta(0,int(options.queryTimeSpan));
                    query.verifyTimeSpan = timedelta(0,int(options.verifyTimeSpan));

                if options.baseCategoryId is not None or options.baseItemId is not None:
                    if options.baseCategoryId is not None:
                        query.baseCategoryId = int(options.baseCategoryId);  # Category to look for clinical item to start accruing query items from
                    if options.baseItemId is not None:
                        query.baseItemId = int(options.baseItemId);

                if options.startDate is not None:
                    query.startDate = DBUtil.parseDateValue(options.startDate);
                if options.endDate is not None:
                    query.endDate = DBUtil.parseDateValue(options.endDate);

            query.baseRecQuery = RecommenderQuery();
            query.baseRecQuery.excludeCategoryIds = query.recommender.defaultExcludedClinicalItemCategoryIds();
            query.baseRecQuery.excludeItemIds = query.recommender.defaultExcludedClinicalItemIds();
            if options.timeDeltaMax is not None and len(options.timeDeltaMax) > 0:
                query.baseRecQuery.timeDeltaMax = timedelta(0,int(options.timeDeltaMax));
            if options.aggregationMethod is not None:
                query.baseRecQuery.aggregationMethod = options.aggregationMethod;
            if options.countPrefix is not None:
                query.baseRecQuery.countPrefix = options.countPrefix;
            if options.maxRecommendedId is not None:
                query.baseRecQuery.maxRecommendedId = int(options.maxRecommendedId);
            if options.sortField is not None:
                query.baseRecQuery.sortField = options.sortField;
            if options.fieldFilters is not None:
                for fieldFilterStr in options.fieldFilters.split(","):
                    (fieldOp, valueStr) = fieldFilterStr.split(":");
                    query.baseRecQuery.fieldFilters[fieldOp] = float(valueStr);

            if options.numRecs is not None:
                query.numRecommendations = int(options.numRecs);
            else:
                # No recommendation count specified, then just use the same as the verify number
                query.numRecommendations = query.numVerifyItems;
            query.numRecsByOrderSet = options.numRecsByOrderSet;


            # Run the actual analysis
            analysisResults = self(query);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");

            # Print comment line with analysis arguments to allow for deconstruction later
            summaryData = {"argv": argv};
            print(COMMENT_TAG, json.dumps(summaryData), file=outputFile);

            formatter = TextResultsFormatter( outputFile );
            colNames = self.resultHeaders(query);
            formatter.formatTuple( colNames );  # Insert a mock record to get a header / label row
            formatter.formatResultDicts( analysisResults, colNames );

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = RecommendationClassificationAnalysis();
    instance.main(sys.argv);
