#!/usr/bin/env python
"""
Analysis module to assess results of ItemRecommender, but framed as prediction / classification
of specific outcome items rather than general recommendations.

Rough approach
- Input patient IDs to test against
- Query recommender based on first X orders / items for each patient
- Report prediction / recommendation score for the specified target outcome items of interest
- Report whether the target outcome item of interest actually did follow for the patient (within the designated time frame)
- The paired columns of scores and actual outcome labels should feed into any ROC curve analysis program

"""

import sys, os
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;
from datetime import timedelta;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.Const import AGGREGATOR_OPTIONS, COUNT_PREFIX_OPTIONS;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender, RandomItemRecommender;
from Util import log;

from BaseCPOEAnalysis import BaseCPOEAnalysis;
from BaseCPOEAnalysis import RECOMMENDER_CLASS_LIST, RECOMMENDER_CLASS_BY_NAME, AnalysisQuery;
from PreparePatientItems import PreparePatientItems;

from medinfo.analysis.Const import OUTCOME_IN_QUERY;

# If have no information to work off of for a given target item, default prediction score
DEFAULT_SCORE = None;

class OutcomePredictionAnalysis(BaseCPOEAnalysis):
    """Driver class to review given patient data and run sample
    recommendation / prediction queries against them and collect score statistics
    between the recommended items vs. their actual presence for the patients.
    """
    def __init__(self):
        BaseCPOEAnalysis.__init__(self);

    def __call__(self, analysisQuery, conn=None):
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;

        try:
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
                (queryItemCountById, scoreByOutcomeId, existsByOutcomeId) = \
                    self.analyzePatientItems \
                    (   analysisQuery,
                        recQuery,
                        patientId,
                        patientItemData,
                        recommender,
                        conn=conn
                    );

                if existsByOutcomeId is not None:
                    # Verify that at least one of the labels is not trivial with the outcome occuring during the query period
                    nonTrivialOutcomeExists = False;
                    for outcomeResult in existsByOutcomeId.itervalues():
                        if outcomeResult != OUTCOME_IN_QUERY:
                            nonTrivialOutcomeExists = True;
                    if not analysisQuery.skipIfOutcomeInQuery or nonTrivialOutcomeExists:
                        # Start aggregating and calculating result stats
                        resultsStatData = self.prepareResultStats( patientId, queryItemCountById, scoreByOutcomeId, existsByOutcomeId);
                        resultsStatDataList.append(resultsStatData);

                progress.Update();

            # progress.PrintStatus();

            return resultsStatDataList;

        finally:
            if not extConn:
                conn.close();

    def analyzePatientItems(self, analysisQuery, recQuery, patientId, patientItemData, recommender, conn):
        """Given the primary query data and clinical item list for a given test patient,
        Parse through the item list and run a query to get the top recommended IDs
        to produce the relevant verify and recommendation item ID sets for comparison
        """
        if "existsByOutcomeId" not in patientItemData:
            # Apparently not able to extract patient item data.  Return sentinel values
            return (None,None,None);
        queryItemCountById = patientItemData["queryItemCountById"];
        existsByOutcomeId = patientItemData["existsByOutcomeId"];

        recQuery.queryItemIds = queryItemCountById.keys();
        #recQuery.targetItemIds = queryStartTime.targetItemIds;     # Already established in base construction

        # Query for recommended orders / items
        recommendedData = recommender( recQuery, conn=conn );

        """
        # Print component scores to help with debugging degenerate cases
        print >> sys.stderr, patientId, existsByOutcomeId, "%(nAB)s, %(nA)s, %(nB)s, %(N)s" % recommendedData[0]
        from medinfo.common.StatsUtil import ContingencyStats, DEGENERATE_VALUE_ADJUSTMENT;
        preProb = recommendedData[0]["nB"]/recommendedData[0]["N"];
        preOdds = preProb/(1-preProb);
        productLR = 1.0;
        product_nAB_nB = 1.0;
        product_nA_N = 1.0;
        print >> sys.stderr, "preProb/Odds: %s | %s" % (preProb, preOdds)
        for component in recommendedData[0]["componentResults"]:
            (nAB,nA,nB,N) = (component["nAB"],component["nA"],component["nB"],component["N"]);
            nAB = max(nAB,DEGENERATE_VALUE_ADJUSTMENT)
            contStats = ContingencyStats(nAB,nA,nB,N);
            productLR *= contStats["LR"];
            product_nAB_nB *= nAB/nB;
            product_nA_N *= nA/N;
            #print >> sys.stderr, ("%s\t" * 7) % (component["clinical_item_id"], nAB,nA,nB,N, contStats["LR"], productLR)
            print >> sys.stderr, ("%s\t" * 10) % (component["clinical_item_id"], nAB,nA,nB,N, nAB/nB, nA/N, product_nAB_nB*nB, product_nA_N*N, product_nAB_nB*nB /(product_nA_N*N) )
        postOdds = preOdds * productLR;
        postProb = postOdds / (1+postOdds);
        print >> sys.stderr, postOdds, postProb;

        aggregate_nAB = product_nAB_nB * recommendedData[0]["nB"];
        aggregate_nA = product_nA_N * recommendedData[0]["N"];
        print >> sys.stderr, aggregate_nAB, aggregate_nA, (aggregate_nAB/aggregate_nA);

        """

        # Record scores per outcome
        scoreByOutcomeId = dict();
        for outcomeId in recQuery.targetItemIds:
            scoreByOutcomeId[outcomeId] = DEFAULT_SCORE;
        for recommendationModel in recommendedData:
            scoreByOutcomeId[recommendationModel["clinical_item_id"]] = recommendationModel[recQuery.sortField];

        return (queryItemCountById, scoreByOutcomeId, existsByOutcomeId);

    def prepareResultStats( self, patientId, queryItemCountById, scoreByOutcomeId, existsByOutcomeId):
        """Organize query prediction stats for results viewing
        """
        stats = RowItemModel();
        stats["patient_id"] = patientId;
        stats["queryItemIds"] = queryItemCountById.keys();

        # Convert sets into more easily readable, sorted lists
        queryItemIdList = list(stats["queryItemIds"]);
        queryItemIdList.sort();
        stats["queryItemIdList"] = json.dumps(queryItemIdList);

        for outcomeId in scoreByOutcomeId.iterkeys():
            stats["score.%s" % outcomeId] = scoreByOutcomeId[outcomeId];
            stats["outcome.%s" % outcomeId] = existsByOutcomeId[outcomeId];

        return stats;

    def analysisHeaders(self, analysisQuery):
        """Column headers for stats results printing by default
        """
        colNames = list();

        outcomeIds = list(analysisQuery.baseRecQuery.targetItemIds);
        outcomeIds.sort();
        for outcomeId in outcomeIds:
            colNames.append("outcome.%s" % outcomeId );
            colNames.append("score.%s" % outcomeId );

        colNames.append("patient_id");
        colNames.append("queryItemIdList");

        return colNames;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <recommenderName> <patientIds> [<outputFile>]\n"+\
                    "   <patientIds/dataFile>    Name of file with patient ids.  If not found, then interpret as comma-separated list of test Patient IDs to prepare analysis data for.  Alternatively, provide preparedPatientItemFile generated from PreparePatientItems as input.\n"+\
                    "   <outputFile>    If query yields a result set, then that will be output\n"+\
                    "                       to the named file.  Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-c", "--baseCategoryId",  dest="baseCategoryId",  help="ID of clinical item category to look for initial items from (probably the ADMIT Dx item).");
        parser.add_option("-Q", "--queryTimeSpan",  dest="queryTimeSpan",  help="Time frame specified in seconds over which to look for initial query items (e.g., 24hrs = 86400) after the base item found from the category above.  Start the time counting from the first item time occuring after the category item above since the ADMIT Dx items are often keyed to dates only without times (defaulting to midnight of the date specified).");
        parser.add_option("-o", "--outcomeItemIds", dest="outcomeItemIds", help="Comma separated list of outcome item IDs to get prediction / recommendation scores for, as well as to label whether they actually appeared for the given patients.  Can specify virtual items representing the end of item triples (e.g., 5-Readmission being the end of any item followed by 3591-Discharge then 3671-Admit), by adding the component items in expected sequence.  For example, '5=3591:3671'");
        parser.add_option("-t", "--timeDeltaMax",  dest="timeDeltaMax",  help="Time delta in seconds maximum by which recommendations should be based on.  Defaults to recommending items that occur at ANY time after the key orders.  If provided, will apply limits to only orders placed within 0 seconds, 1 hour (3600), 1 day (86400), or 1 week (604800) of the key orders / items.  If set, will also only count presence of labeled target items if occurs within the given time delta of the first query item.");

        parser.add_option("-P", "--preparedPatientItemFile",  dest="preparedPatientItemFile", action="store_true", help="If set, will expect primary argument to instead be name of file to read input data from, instead of using above parameters to query from database.");

        parser.add_option("-R", "--recommender",  dest="recommender",  help="Name of the recommender to run the analysis against.  Options: %s" % RECOMMENDER_CLASS_BY_NAME.keys());
        parser.add_option("-S", "--scoreField",  dest="scoreField",  help="Name of (derived) field to score items by.  For example, 'conditionalFreq.'");
        parser.add_option("-p", "--countPrefix",  dest="countPrefix",  help="Which counting method to use for item associations.  Defaults to counting item occurrences, allowing for duplicates.  Additional options include: %s." % list(COUNT_PREFIX_OPTIONS) );
        parser.add_option("-a", "--aggregationMethod",  dest="aggregationMethod",  help="Aggregation method to use for recommendations based off multiple query items.  Options: %s." % list(AGGREGATOR_OPTIONS) );
        parser.add_option("-s", "--skipIfOutcomeInQuery",  dest="skipIfOutcomeInQuery",  action="store_true", help="If set, will skip patients where the outcome item occurs during the query period since that would defy the point of predicting the outcome.");
        parser.add_option("-m", "--maxRecommendedId",  dest="maxRecommendedId",  help="Specify a maximum ID value to accept for recommended items.  More used to limit output in test cases");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            # Parse out the query parameters
            query = AnalysisQuery();
            query.recommender = RECOMMENDER_CLASS_BY_NAME[options.recommender]();
            query.recommender.dataManager.dataCache = dict(); # Use local cache to speed up repeat queries

            query.baseRecQuery = RecommenderQuery();
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

                query.baseCategoryId = int(options.baseCategoryId);  # Category to look for clinical item to start accruing query items from
                query.queryTimeSpan = timedelta(0,int(options.queryTimeSpan))

                query.baseRecQuery.targetItemIds = set();

                outcomeIdStrList = options.outcomeItemIds.split(",");
                for outcomeIdStr in outcomeIdStrList:
                    outcomeIdComponents = outcomeIdStr.split("=");
                    outcomeId = int(outcomeIdComponents[0]);
                    query.baseRecQuery.targetItemIds.add(outcomeId);
                    if len(outcomeIdComponents) > 1:
                        sequenceIds = [int(seqIdStr) for seqIdStr in outcomeIdComponents[1].split(":")];
                        query.sequenceItemIdsByVirtualItemId[outcomeId] = tuple(sequenceIds);

            if options.timeDeltaMax is not None:
                query.baseRecQuery.timeDeltaMax = timedelta(0,int(options.timeDeltaMax));
            if options.scoreField is not None:
                query.baseRecQuery.sortField = options.scoreField;
            if options.countPrefix is not None:
                query.baseRecQuery.countPrefix = options.countPrefix;
            if options.aggregationMethod is not None:
                query.baseRecQuery.aggregationMethod = options.aggregationMethod;
            if options.maxRecommendedId is not None:
                query.baseRecQuery.maxRecommendedId = int(options.maxRecommendedId);

            if options.skipIfOutcomeInQuery is not None:
                query.skipIfOutcomeInQuery = options.skipIfOutcomeInQuery;

            # Run the actual analysis
            analysisResults = self(query);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");

            # Print comment line with analysis arguments to allow for deconstruction later
            print >> outputFile, COMMENT_TAG, json.dumps({"argv":argv});

            colNames = self.analysisHeaders(query);
            analysisResults.insert(0, RowItemModel(colNames,colNames) );    # Insert a mock record to get a header / label row

            formatter = TextResultsFormatter( outputFile );
            formatter.formatResultDicts( analysisResults, colNames );

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = OutcomePredictionAnalysis();
    instance.main(sys.argv);
