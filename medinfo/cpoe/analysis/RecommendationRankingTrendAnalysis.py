#!/usr/bin/env python
"""
Analysis module to assess results of ItemRecommender.
Rough approach
- Input patient IDs to test against
- Query recommender for recommended item list given the first unique X orders / items
  for each patient, for X in [0,N-1] (N = number unique orders / items for the patient)
- For each query above, record the positition of the next actual order / item in that 
    recommended item rank list.

Simulates a cumulative recommendation based on more and more orders.
Should be able to chart results to get a sense of how far to progress in a
patient's (order) history to start getting good recommendations, and
in particular, how far down the recommendation list we'll have to look
to find the orders that will actually be used.
"""

import sys, os
import time;
from optparse import OptionParser
from cStringIO import StringIO;
from datetime import timedelta;
from math import sqrt;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender, RandomItemRecommender;
from Util import log;

from BaseCPOEAnalysis import BaseCPOEAnalysis;
from BaseCPOEAnalysis import RECOMMENDER_CLASS_LIST, RECOMMENDER_CLASS_BY_NAME, AnalysisQuery;
from BaseCPOEAnalysis import AGGREGATOR_OPTIONS;

class AnalysisQuery:
    """Simple struct to pass query parameters
    """
    patientIds = None;  # IDs of the patients to test / analyze against 
    recommender = None; # Instance of the recommender to test against
    baseRecQuery = None;    # Base Recommender Query to test recommender with.  
                            # Query items and return counts will be customized by analyzer dynamically, 
                            #   but allows specification of static query modifiers (e.g., excluded categories, items, timeDeltaMax)
    queryItemMax = None;    # If set, specifies a maximum number of query items to use when analyzing 
                            #   serial recommendations.  Will stop analyzing further for a patient once reach this limit
    def __init__(self):
        self.patientIds = set();
        self.recommender = None;
        self.baseRecQuery = None;
        self.queryItemMax = None;

class RecommendationRankingTrendAnalysis(BaseCPOEAnalysis):
    """Driver class to review given patient data and run sample recommendation queries against
    them serially based on accumulating initial orders / items and record recommendation
    ranks of each next order / item as they occur.
    
    Report as a relational table with columns
    - patientId:    ID of the patient to which the analysis data applies
    - iItem:    Index of the next order / item for the patient in chronological order
    - iRecItem: Index of the next order / item, which should be the same as iItem, 
                except this only counts items / orders for which recommendations can / will be made.
                For example, recommendations will not be offerred for repeat orders.
                Recommendations will often only be offerred for orders and not other informational
                items (e.g., abnormal lab results).
    - recRank: For the next order / item, its rank position in the list of recommended items
    - recScore: For the next order / item, its score that placed it in the list of recommended items
    """
    connFactory = None;

    def __init__(self):
        BaseCPOEAnalysis.__init__(self);
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

    def __call__(self, analysisQuery, conn=None):
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        
        try:
            # Preload some lookup data to facilitate subsequent checks
            categoryIdByItemId = dict();
            lookupTable = DBUtil.execute("select clinical_item_id, clinical_item_category_id from clinical_item", conn=conn);
            for (clinicalItemId, categoryId) in lookupTable:
                categoryIdByItemId[clinicalItemId] = categoryId;

            # Recommender to test with
            recommender = analysisQuery.recommender;

            # Start building basic recommendation query to use for testing
            recQuery = analysisQuery.baseRecQuery;

            # Start building results data
            resultsTable = list();
            progress = ProgressDots(50,1,"Item Recommendations");
            
            # Query for all of the order / item data for the test patients.  Load one patient's data at a time
            for (patientId, clinicalItemIdList) in self.queryPatientClinicalItemData(analysisQuery, conn=conn):
                # Parse through the patient's item list and run serial recommendation queries 
                #   to find each item's accumulated recommendation rank
                serialRecDataGen = \
                    self.reviewSerialRecommendations \
                    (   patientId, 
                        clinicalItemIdList,
                        analysisQuery, 
                        recQuery, 
                        recommender, 
                        categoryIdByItemId,
                        progress=progress,
                        conn=conn
                    );

                for (clinicalItemId, iItem, iRecItem, recRank, recScore) in serialRecDataGen:
                    resultsRow = (patientId, clinicalItemId, iItem, iRecItem, recRank, recScore);
                    resultsTable.append(resultsRow);

            progress.PrintStatus();

            #print resultsTable
            return resultsTable;

        finally:
            if not extConn:
                conn.close();


    def queryPatientClinicalItemData(self, analysisQuery, conn):
        """Query for all of the order / item data for each patient
        noted in the analysisQuery and yield them one list of clinicalItemIds
        at a time.
        Generated iterator over 2-ples (patientId, clinicalItemIdList)
            - Patient ID: ID of the patient for which the currently yielded item intended for
            - Clinical Item ID List: 
                List of all of the clinical items / orders for this patient
                ordered by item date (currently excluding those that are off the "default_recommend" / on the "default exclusion" list).
        """
        sqlQuery = SQLQuery();
        sqlQuery.addSelect("pi.patient_id");
        sqlQuery.addSelect("pi.clinical_item_id");
        #sqlQuery.addSelect("pi.item_date");
        sqlQuery.addFrom("clinical_item_category as cic");
        sqlQuery.addFrom("clinical_item as ci");
        sqlQuery.addFrom("patient_item as pi");
        sqlQuery.addWhere("cic.clinical_item_category_id = ci.clinical_item_category_id");
        sqlQuery.addWhere("ci.clinical_item_id = pi.clinical_item_id");

        sqlQuery.addWhereIn("pi.patient_id", analysisQuery.patientIds );

        sqlQuery.addOrderBy("pi.patient_id");
        sqlQuery.addOrderBy("pi.item_date");

        # Execute the actual query for patient order / item data
        cursor = conn.cursor();
        cursor.execute( str(sqlQuery), tuple(sqlQuery.params) );

        currentPatientId = None;
        clinicalItemIdList = list();

        row = cursor.fetchone();
        while row is not None:
            (patientId, clinicalItemId) = row;
            if currentPatientId is None:
                currentPatientId = patientId;

            if patientId != currentPatientId:
                # Changed patient, yield the existing data for the previous patient
                yield (currentPatientId, clinicalItemIdList);
                # Update our data tracking for the current patient
                currentPatientId = patientId;
                clinicalItemIdList = list();

            clinicalItemIdList.append(clinicalItemId);

            row = cursor.fetchone();
        
        # Yield / return the last patient data
        yield (currentPatientId, clinicalItemIdList);
        
        cursor.close();


    def reviewSerialRecommendations(self, patientId, clinicalItemIdList, analysisQuery,  recQuery,  recommender,  categoryIdByItemId, progress, conn ):
        """Serially and cumulatively go through the
        clinical items and perform recommendation queries using the accumulated keyset
        to determine the relative rank and score for each successive item.
        Account for / skip redundant and otherwise excluded items.
        """
        clinicalItemIdSet = set(clinicalItemIdList);
        numPatientItems = len(clinicalItemIdSet);

        numQueryItems = 0;
        queryItemIds = set();

        iRecItem = 0;   # Separately track number of items that can actually be recommended (skip repeats and other exclusions)
        for (iItem, clinicalItemId) in enumerate(clinicalItemIdList):
            if self.isItemRecommendable(clinicalItemId, queryItemIds, recQuery, categoryIdByItemId):
                # Query based on accumulated key data thus far, 
                #   to see how well able to predict / rank / score this next clinical item
                recQuery.queryItemIds = queryItemIds;
                recQuery.limit = None;  # No limitation because trying to find the next item whereever it may be in the list
                
                recommendedData = recommender( recQuery, conn=conn );

                # Find the next clinical item in the recommended list
                recRank = 0;
                recScore = None;
                for iRec, recommendationModel in enumerate(recommendedData):
                    recRank = iRec+1;   # Start rankings at 1, not 0
                    if recommendationModel["clinical_item_id"] == clinicalItemId:
                        # Found the match, note the respective recommendation statistics
                        recScore = recommendationModel["score"];
                        break;  # Don't need to look anymore

                yield (clinicalItemId, iItem, iRecItem, recRank, recScore);

                iRecItem += 1;  # Track that we recorded information on one more recommended item
                progress.Update();
            
            queryItemIds.add(clinicalItemId);   # Accumulate initial query set as progress
            
            if analysisQuery.queryItemMax is not None and iRecItem >= analysisQuery.queryItemMax:
                # Option to break early if wish to avoid excessive analysis that is unnecessary 
                #   or even potentially damaging to execution memory
                break;

    def isItemRecommendable(self, clinicalItemId, queryItemIds, recQuery, categoryIdByItemId):
        """Decide if the next clinical item could even possibly appear
        in the recommendation list.  (Because if not, no point in trying to
        test recommender against it).  Typical exclusion issues include:
        - Item already in query set (redundant / repeat orders)
        - Item specifically excluded in recommenderQuery
        - Item's category specifically excluded in recommenderQuery
        """
        categoryId = categoryIdByItemId[clinicalItemId];
        if (clinicalItemId in queryItemIds) or \
            (recQuery.excludeItemIds is not None and clinicalItemId in recQuery.excludeItemIds) or \
            (recQuery.excludeCategoryIds is not None and categoryId in recQuery.excludeCategoryIds):
            return False;
        else:
            return True;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <patientIds> [<outputFile>]\n"+\
                    "   <patientIds>    Patient ID file or Comma-separated list of test Patient IDs to run analysis against\n"+\
                    "   <outputFile>    If query yields a result set, then that will be output\n"+\
                    "                       to the named file.  Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-R", "--recommender",  dest="recommender",  help="Name of the recommender to run the analysis against.  Options: %s" % RECOMMENDER_CLASS_BY_NAME.keys());
        parser.add_option("-s", "--sortField",  dest="sortField",  help="Allow overriding of default sort field when returning ranked results");
        parser.add_option("-f", "--fieldFilters",  dest="fieldFilters",  help="Filters to exclude results.  Comma-separated separated list of field-op:value exclusions where op is either < or > like, conditionalFreq<:0.1,frqeRatio<:1");
        parser.add_option("-t", "--timeDeltaMax",  dest="timeDeltaMax",  help="If set, represents a time delta in seconds maximum by which recommendations should be based on.  Defaults to recommending items that occur at ANY time after the key orders.  If provided, will apply limits to only orders placed within 0 seconds, 1 hour (3600), 1 day (86400), or 1 week (604800) of the key orders / items.");
        parser.add_option("-a", "--aggregationMethod",  dest="aggregationMethod",  help="Aggregation method to use for recommendations based off multiple query items.  Options: %s." % list(AGGREGATOR_OPTIONS) );
        parser.add_option("-p", "--countPrefix",  dest="countPrefix",  help="Prefix for how to do counts.  Blank for default item counting allowing repeats, otherwise ignore repeats for patient_ or encounter_");
        parser.add_option("-q", "--queryItemMax",  dest="queryItemMax",  help="If set, specifies a maximum number of query items to use when analyzing serial recommendations.  Will stop analyzing further for a patient once reach this limit.");
        (options, args) = parser.parse_args(argv[1:])
    
        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            # Parse out the query parameters
            query = AnalysisQuery();
            query.recommender = RECOMMENDER_CLASS_BY_NAME[options.recommender]();
            query.recommender.dataManager.dataCache = dict();   # Use a local cahce to speed up repeat queries

            patientIdsParam = args[0];
            try:
                # Try to open patient IDs as a file
                patientIdFile = stdOpen(patientIdsParam);
                query.patientIds = set( patientIdFile.read().split() );
            except IOError:
                # Unable to open as a filename, then interpret as simple comma-separated list
                query.patientIds = set(patientIdsParam.split(","));

        
            query.baseRecQuery = RecommenderQuery();
            query.baseRecQuery.excludeCategoryIds = query.recommender.defaultExcludedClinicalItemCategoryIds();
            query.baseRecQuery.excludeItemIds = query.recommender.defaultExcludedClinicalItemIds();
            if options.sortField is not None:
                query.baseRecQuery.sortField = options.sortField;
            if options.fieldFilters is not None:
                for fieldFilterStr in options.fieldFilters.split(","):
                    (fieldOp, valueStr) = fieldFilterStr.split(":");
                    query.baseRecQuery.fieldFilters[fieldOp] = float(valueStr);
            if options.timeDeltaMax is not None and len(options.timeDeltaMax) > 0:
                query.baseRecQuery.timeDeltaMax = timedelta(0,int(options.timeDeltaMax));
            if options.aggregationMethod is not None:
                query.baseRecQuery.aggregationMethod = options.aggregationMethod;
            if options.countPrefix is not None:
                query.baseRecQuery.countPrefix = options.countPrefix;

            if options.queryItemMax is not None:
                query.queryItemMax = int(options.queryItemMax);
            
            # Run the actual analysis
            analysisResults = self(query);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");
            
            print >> outputFile, "#", argv;  # Print comment line with analysis arguments to allow for deconstruction later

            colNames = ["patientId", "clinicalItemId", "iItem", "iRecItem", "recRank", "recScore"];
            analysisResults.insert(0, colNames);    # Insert a mock record to get a header / label row
            
            formatter = TextResultsFormatter( outputFile );
            formatter.formatResultSet( analysisResults );

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = RecommendationRankingTrendAnalysis();
    instance.main(sys.argv);
