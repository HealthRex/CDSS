#!/usr/bin/env python
"""
Use a Latent Dirichlet Allocation (LDA) model to predict future clinical items
and evaluate using RecommendationClassificationAnalysis framework.
"""

import sys, os
import time;
import json;
from optparse import OptionParser
from io import StringIO;
from datetime import timedelta;
from pprint import pprint;

import gensim;

from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, loadJSONDict;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.TopicModelRecommender import TopicModelRecommender;
from .Util import log;

from .RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;
from .BaseCPOEAnalysis import AnalysisQuery;
from .PreparePatientItems import PreparePatientItems;
from .RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

DEFAULT_TOPIC_ITEM_COUNT = 1000; # When using or printing out topic information, number of top scored items to consider
DEFAULT_RECOMMENDED_ITEM_COUNT = 10;    # When doing validation calculations, number of items to recommend when calculating precision and recall
DEFAULT_MIN_TOPIC_WEIGHT = 0.001; # When using topic models, ignore topics that contribute less than this score to avoid wasting time on low value items
DEFAULT_SORT_FIELD = "totalItemWeight";

class TopicModelAnalysis(RecommendationClassificationAnalysis):
    def __init__(self):
        RecommendationClassificationAnalysis.__init__(self);

    def __call__(self, analysisQuery):
        """Go through the validation file to test use of the model towards predicting verify items.
        """
        preparer = PreparePatientItems();

        # Keep ID indexes for simplicity for now
        id2word = analysisQuery.recommender.model.id2word;
        id2id = dict();
        for id in id2word:
            id2id[id] = id;
        analysisQuery.recommender.model.id2word = id2id;

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
                    preparer
                );

            if analysisResults is not None:
                (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData) = analysisResults;  # Unpack results
                # Start aggregating and calculating result stats
                resultsStatData = self.calculateResultStats( patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, analysisQuery.recommender.docCountByWordId, analysisQuery.baseRecQuery, recommendedData );
                if "baseItemId" in patientItemData:
                    analysisQuery.baseItemId = patientItemData["baseItemId"]; # Record something here, so know to report back in result headers
                yield resultsStatData;

            # progress.Update();

        # progress.PrintStatus();

    def analyzePatientItems(self, patientItemData, analysisQuery, recQuery, patientId, recommender, preparer):
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

        # Customize number of recommendations if comparing against specific order set usage
        self.customizeNumRecommendations(patientItemData, analysisQuery, recQuery, preparer);

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
        resultsStatData["weightByTopicId"] = recommendedData[0]["weightByTopicId"];
        resultsStatData["numSelectedTopics"] = recommendedData[0]["numSelectedTopics"];
        return resultsStatData;

    def resultHeaders(self, analysisQuery=None):
        headers = RecommendationClassificationAnalysis.resultHeaders(self,analysisQuery);
        headers.append("weightByTopicId");
        headers.append("numSelectedTopics");
        return headers;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile>    Validation file in prepared result file format use generated LDA models to predict items and compare against verify sets similar to RecommendationClassficationAnalysis. \n"+\
                    "   <outputFile>   Validation result stat summaries.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-M", "--modelFile",  dest="modelFile", help="Name of the file to load an LDA or HDP model and topic word document counts from.");
        parser.add_option("-X", "--excludeCategoryIds",  dest="excludeCategoryIds", help="For recommendation, exclude / skip any items who fall under one of these comma-separated category Ids.");
        parser.add_option("-i", "--itemsPerCluster",  dest="itemsPerCluster", default=DEFAULT_TOPIC_ITEM_COUNT, help="Specify number of top topic items to consider when scoring recommendations.");
        parser.add_option("-m", "--minClusterWeight",  dest="minClusterWeight", default=DEFAULT_MIN_TOPIC_WEIGHT, help="When scoring recommendations, skip any topics with less than this relation weight (effectively scores as zero, but can avoid a lot of low yield calculations).");
        parser.add_option("-s", "--sortField",  dest="sortField", default=DEFAULT_SORT_FIELD, help="Score field to sort top recommendations by.  Default to posterior probabilty 'totelItemWeight', but can also select 'lift' = 'tfidf' = 'interest' for TF*IDF style score weighting.");
        parser.add_option("-r", "--numRecs",   dest="numRecs",  default=DEFAULT_RECOMMENDED_ITEM_COUNT, help="Number of orders / items to recommend for comparison against the verification set. Alternative set option numRecsByOrderSet to look for key order set usage and size.");
        parser.add_option("-O", "--numRecsByOrderSet",   dest="numRecsByOrderSet", action="store_true", help="If set, then look for an order_set_id column to find the key order set that triggered the evaluation time point to determine number of recommendations to consider.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) >= 1:
            query = AnalysisQuery();
            query.preparedPatientItemFile = stdOpen(args[0]);
            query.recommender = TopicModelRecommender(options.modelFile);
            query.baseRecQuery = RecommenderQuery();
            if options.excludeCategoryIds is not None:
                query.baseRecQuery.excludeCategoryIds = set();
                for categoryIdStr in options.executeCategoryIds.split(","):
                    query.baseRecQuery.excludeCategoryIds.add(int(categoryIdStr));
            else:   # Default exclusions if none specified
                query.baseRecQuery.excludeCategoryIds = query.recommender.defaultExcludedClinicalItemCategoryIds();
                query.baseRecQuery.excludeItemIds = query.recommender.defaultExcludedClinicalItemIds();
            query.baseRecQuery.itemsPerCluster = int(options.itemsPerCluster);
            query.baseRecQuery.minClusterWeight = float(options.minClusterWeight);

            query.baseRecQuery.sortField = options.sortField;
            query.numRecommendations = int(options.numRecs);
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
    instance = TopicModelAnalysis();
    instance.main(sys.argv);
