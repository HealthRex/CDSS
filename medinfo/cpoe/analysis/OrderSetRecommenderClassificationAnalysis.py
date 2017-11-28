#!/usr/bin/env python
"""
Use OrderSetRecommender to predict future clinical items
and evaluate using RecommendationClassificationAnalysis framework.
"""

import sys, os
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;
from datetime import timedelta;

from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, loadJSONDict;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.OrderSetRecommender import OrderSetRecommender;
from Util import log;

from RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;
from BaseCPOEAnalysis import AnalysisQuery;
from PreparePatientItems import PreparePatientItems;
from RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

DEFAULT_RECOMMENDED_ITEM_COUNT = 10;    # When doing validation calculations, number of items to recommend when calculating precision and recall
DEFAULT_SORT_FIELD = "P(B|A)";

class OrderSetRecommenderClassificationAnalysis(RecommendationClassificationAnalysis):
    def __init__(self):
        RecommendationClassificationAnalysis.__init__(self);

    def __call__(self, analysisQuery):
        """Go through the validation file to test use of the model towards predicting verify items.
        """
        # Scaled / weighted scores based on item base counts, in this case, number of included order set counts
        analysisQuery.recommender.initItemLookups(analysisQuery.baseRecQuery);
        orderSetCountByItemId = dict();
        for itemId, orderSetIds in analysisQuery.recommender.orderSetIdsByItemId.iteritems():
            orderSetCountByItemId[itemId] = len(orderSetIds);

        preparer = PreparePatientItems();
        # progress = ProgressDots(50,1,"Patients");
        for patientItemData in preparer.loadPatientItemData(analysisQuery):
            patientId = patientItemData["patient_id"];
            analysisResults = \
                self.analyzePatientItems \
                (   patientItemData,
                    analysisQuery,
                    analysisQuery.baseRecQuery,
                    patientId,
                    analysisQuery.recommender,
                );

            if analysisResults is not None:
                (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData) = analysisResults;  # Unpack results
                # Start aggregating and calculating result stats
                resultsStatData = self.calculateResultStats( patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, orderSetCountByItemId, analysisQuery.baseRecQuery, recommendedData );
                if "baseItemId" in patientItemData:
                    analysisQuery.baseItemId = patientItemData["baseItemId"]; # Record something here, so know to report back in result headers
                yield resultsStatData;
            # progress.Update();
        # progress.PrintStatus();

    def analyzePatientItems(self, patientItemData, analysisQuery, recQuery, patientId, recommender):
        """Given the primary query data and clinical item list for a given test patient,
        Parse through the item list and run a query to get the top recommended IDs
        to produce the relevant verify and recommendation item ID sets for comparison
        """
        if "queryItemCountById" not in patientItemData:
            # Apparently not able to find / extract relevant data, so skip this record
            return None;
        queryItemCountById = patientItemData["queryItemCountById"];
        verifyItemCountById = patientItemData["verifyItemCountById"];

        recQuery.queryItemIds = queryItemCountById; # Have option to use as dictionary, but will also function as key set
        # recQuery.limit = analysisQuery.numRecommendations;

        # Query for recommended orders / items
        recommendedData = recommender( recQuery );

        # Distill down to just the set of recommended item IDs
        recommendedItemIds = set();
        for i, recommendationModel in enumerate(recommendedData):
            if i >= analysisQuery.numRecommendations:
                break;
            recommendedItemIds.add(recommendationModel["clinical_item_id"]);
        return (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData);

    def calculateResultStats( self, patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, baseCountByItemId, recQuery, recommendedData ):
        resultsStatData = RecommendationClassificationAnalysis.calculateResultStats( self, patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, baseCountByItemId, recQuery, recommendedData );
        # Copy elements from any item in recommended list
        resultsStatData["weightByOrderSetId"] = recommendedData[0]["weightByOrderSetId"];
        resultsStatData["numSelectedOrderSets"] = recommendedData[0]["numSelectedOrderSets"];
        return resultsStatData;

    def resultHeaders(self, analysisQuery=None):
        headers = RecommendationClassificationAnalysis.resultHeaders(self,analysisQuery);
        headers.append("weightByOrderSetId");
        headers.append("numSelectedOrderSets");
        return headers;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile>    Validation file in prepared result file format.  Predict items and compare against verify sets similar to RecommendationClassficationAnalysis. \n"+\
                    "   <outputFile>   Validation result stat summaries.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-X", "--excludeCategoryIds",  dest="excludeCategoryIds", help="For recommendation, exclude / skip any items who fall under one of these comma-separated category Ids.");
        parser.add_option("-s", "--sortField",  dest="sortField", default=DEFAULT_SORT_FIELD, help="Score field to sort top recommendations by.  Default to posterior probabilty / positive predictive value 'P(B|A)', but can also select 'lift' = 'tfidf' = 'interest' for TF*IDF style score weighting.");
        parser.add_option("-r", "--numRecs",   dest="numRecs",  default=DEFAULT_RECOMMENDED_ITEM_COUNT, help="Number of orders / items to recommend for comparison against the verification set.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) >= 1:
            query = AnalysisQuery();
            query.preparedPatientItemFile = stdOpen(args[0]);
            query.recommender = OrderSetRecommender();
            query.baseRecQuery = RecommenderQuery();
            if options.excludeCategoryIds is not None:
                query.baseRecQuery.excludeCategoryIds = set();
                for categoryIdStr in options.executeCategoryIds.split(","):
                    query.baseRecQuery.excludeCategoryIds.add(int(categoryIdStr));
            else:   # Default exclusions if none specified
                query.baseRecQuery.excludeCategoryIds = query.recommender.defaultExcludedClinicalItemCategoryIds();
                query.baseRecQuery.excludeItemIds = query.recommender.defaultExcludedClinicalItemIds();

            query.baseRecQuery.sortField = options.sortField;
            query.numRecommendations = int(options.numRecs);

            # Run the actual analysis
            analysisResults = self(query);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");

            # Print comment line with analysis arguments to allow for deconstruction later
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

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
    instance = OrderSetRecommenderClassificationAnalysis();
    instance.main(sys.argv);
