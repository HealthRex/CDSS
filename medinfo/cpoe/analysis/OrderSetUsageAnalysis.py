#!/usr/bin/env python
"""
Go through prepared patient items, query back to database to see how many order sets
were used in those cases, and the density of order set usage.
Looks at overall stats of usage during verify period (e.g., within 24 hours),
unless specify evaluation numRecsByOrderSet then only looking at one specified key order set at a time

Multiple versions of stats to get out of module:
- Overall usage rate of order sets during query+verify time span
- Precision/Recall accuracy of order sets used during the verify time span,
    including using just the "Top X" items from an order set as sorted by name or prevalence
- Precision/Recall accuracy of one key trigger order set at a time, only at the time
    the order set was initiated, evaluated against the verify time span immediately following

"""

import sys, os
import time;
import json;
from operator import itemgetter
from optparse import OptionParser
from io import StringIO;
from datetime import timedelta;

from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, loadJSONDict;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, RowItemFieldComparator;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.OrderSetRecommender import OrderSetRecommender;
from medinfo.cpoe.Const import AD_HOC_SECTION;
from .Util import log;

from .BaseCPOEAnalysis import AnalysisQuery;
from .PreparePatientItems import PreparePatientItems;
from .RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

# When doing validation calculations, number of items to recommend when calculating precision and recall
# If set to value < 1, then interpret as sentinel value, meaning just use all available order set items.
# Otherwise, choose a subset sorted by how common the top items are
DEFAULT_RECOMMENDED_ITEM_COUNT = -1;

# Default field to sort by if selecting a subset of order set items to consider
DEFAULT_SORT_FIELD = "patient_count";

class OrderSetUsageAnalysis(RecommendationClassificationAnalysis):
    def __init__(self):
        RecommendationClassificationAnalysis.__init__(self);

    def __call__(self, analysisQuery, conn=None):
        """Go through the validation file to assess order set usage amongst test cases
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;

        try:
            conn = DBUtil.connection();

            preparer = PreparePatientItems();
            progress = ProgressDots(50,1,"Patients");
            for patientItemData in preparer.loadPatientItemData(analysisQuery):
                patientId = patientItemData["patient_id"];
                analysisResults = \
                    self.analyzePatientItems \
                    (   patientItemData,
                        analysisQuery,
                        analysisQuery.baseRecQuery,
                        patientId,
                        analysisQuery.recommender,
                        conn=conn
                    );
                if analysisResults is not None:
                    (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData, orderSetItemData) = analysisResults;  # Unpack results

                    # Start aggregating and calculating result stats
                    resultsStatData = self.calculateResultStats( patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, self.supportRecommender.patientCountByItemId, analysisQuery.baseRecQuery, recommendedData );
                    resultsStatData["usedOrderSetIds"] = orderSetItemData["allUsedOrderSetIds"];
                    resultsStatData["numUsedOrderSets"] = len(orderSetItemData["allUsedOrderSetIds"]);
                    resultsStatData["numUsedOrderSetItems"] = len(orderSetItemData["allUsedOrderSetItemIds"]);
                    resultsStatData["numAvailableOrderSetItems"] = len(orderSetItemData["allAvailableOrderSetItemIds"]);
                    resultsStatData["numRecommendableUsedOrderSetItems"] = len(orderSetItemData["recommendableUsedOrderSetItemIds"]);
                    resultsStatData["numRecommendableAvailableOrderSetItems"] = len(orderSetItemData["recommendableAvailableOrderSetItemIds"]);
                    resultsStatData["numRecommendableQueryItems"] = len(orderSetItemData["recommendableQueryItemIds"]);
                    resultsStatData["numRecommendableVerifyItems"] = len(orderSetItemData["recommendableVerifyItemIds"]);
                    resultsStatData["numRecommendableQueryVerifyItems"] = len(orderSetItemData["recommendableQueryItemIds"] | orderSetItemData["recommendableVerifyItemIds"]);  # Union of two sets
                    resultsStatData["orderSetItemUsageRate"] = 0.0;
                    if resultsStatData["numAvailableOrderSetItems"] > 0:
                        resultsStatData["orderSetItemUsageRate"] = float(resultsStatData["numUsedOrderSetItems"]) / resultsStatData["numAvailableOrderSetItems"];
                    resultsStatData["recommendableQueryVerifyItemFromOrderSetRate"] = 0.0;
                    if resultsStatData["numRecommendableQueryVerifyItems"] > 0:
                        resultsStatData["recommendableQueryVerifyItemFromOrderSetRate"] = float(resultsStatData["numRecommendableUsedOrderSetItems"]) / resultsStatData["numRecommendableQueryVerifyItems"];
                    yield resultsStatData;
                progress.Update();
            # progress.PrintStatus();
        finally:
            if not extConn:
                conn.close();

    def analyzePatientItems(self, patientItemData, analysisQuery, recQuery, patientId, recommender, conn):
        """Given the primary query data and clinical item list for a given test patient,
        Parse through the item list and run a query to get the top recommended IDs
        to produce the relevant verify and recommendation item ID sets for comparison
        """
        if "queryItemCountById" not in patientItemData:
            # Apparently not able to find / extract relevant data, so skip this record
            return None;
        queryItemCountById = patientItemData["queryItemCountById"];
        verifyItemCountById = patientItemData["verifyItemCountById"];

        ## Query for orderset linked items
        orderSetQuery = \
            """
            select ic.external_id, pi.clinical_item_id, pi.item_date >= %(p)s as is_verify_item
            from
               patient_item as pi,
               patient_item_collection_link as picl,
               item_collection_item as ici,
               item_collection as ic
            where patient_id = %(p)s
            and pi.patient_item_id = picl.patient_item_id
            and picl.item_collection_item_id = ici.item_collection_item_id
            and ici.item_collection_id = ic.item_collection_id
            and ic.section <> %(p)s
            and item_date >= %(p)s and item_date < %(p)s
            """ % {"p": DBUtil.SQL_PLACEHOLDER}
        orderSetParams = ( patientItemData["queryEndTime"], patientItemData["patient_id"], AD_HOC_SECTION, patientItemData["baseItemDate"], patientItemData["verifyEndTime"],);
        resultTable = DBUtil.execute(orderSetQuery, orderSetParams, includeColumnNames=True, conn=conn);
        allOrderSetItems = modelListFromTable(resultTable);
        orderSetItemsByOrderSetId = dict();
        for orderSetItem in allOrderSetItems:
            orderSetId = orderSetItem["external_id"];
            if orderSetId not in orderSetItemsByOrderSetId:
                orderSetItemsByOrderSetId[orderSetId] = list();
            orderSetItemsByOrderSetId[orderSetId].append(orderSetItem);

        keyOrderSetIds = list(orderSetItemsByOrderSetId.keys());
        if analysisQuery.numRecsByOrderSet:
            # Only use the specified key order set for each set of patient data
            orderSetId = patientItemData["order_set_id"];
            if orderSetId not in keyOrderSetIds:
                # No valid order set orders to use in this setting. Skip this case
                return None;
            keyOrderSetIds = [orderSetId];

        # Pre-cache order set item data
        if self.supportRecommender.itemIdsByOrderSetId is None:
            self.supportRecommender.initItemLookups(analysisQuery.baseRecQuery);

        # For each order set, count up how many order set linked items used.
        #   Count up how many items used indirectly that would have been within order set.
        # Organize by whether the item occurred during the "verify" vs. "query" time period
        usedItemIdsByOrderSetIdByIsVerifyItem = {True:dict(), False:dict()};
        for keyOrderSetId in keyOrderSetIds:
            orderSetItems = orderSetItemsByOrderSetId[keyOrderSetId];
            for orderSetItem in orderSetItems:
                isVerifyItem = orderSetItem["is_verify_item"];
                orderSetId = orderSetItem["external_id"];
                itemId = orderSetItem["clinical_item_id"];

                usedItemIdsByOrderSetId = usedItemIdsByOrderSetIdByIsVerifyItem[isVerifyItem];
                if orderSetId not in usedItemIdsByOrderSetId:
                    usedItemIdsByOrderSetId[orderSetId] = set();
                usedItemIdsByOrderSetId[orderSetId].add(itemId);

        # Summarize into total number of (unique) items available from used order sets, and which of those items were actually used from the order set
        allUsedOrderSetItemIds = set();
        allUsedOrderSetIds = set();
        recommendableUsedOrderSetItemIds = set();
        allAvailableOrderSetItemIds = set();
        allAvailableVerifyOrderSetItemIds = set();
        recommendableAvailableOrderSetItemIds = set();
        for isVerifyItem, usedItemIdsByOrderSetId in usedItemIdsByOrderSetIdByIsVerifyItem.items():
            for orderSetId, usedItemIds in usedItemIdsByOrderSetId.items():
                allUsedOrderSetIds.add(orderSetId);
                if isVerifyItem:
                    allAvailableVerifyOrderSetItemIds.update(self.supportRecommender.itemIdsByOrderSetId[orderSetId]);

                for itemId in usedItemIds:
                    if self.supportRecommender.isItemRecommendable(itemId, None, recQuery, self.supportRecommender.categoryIdByItemId):
                        recommendableUsedOrderSetItemIds.add(itemId);
                allUsedOrderSetItemIds.update(usedItemIds);

                for itemId in self.supportRecommender.itemIdsByOrderSetId[orderSetId]:
                    if self.supportRecommender.isItemRecommendable(itemId, None, recQuery, self.supportRecommender.categoryIdByItemId):
                        recommendableAvailableOrderSetItemIds.add(itemId);
                allAvailableOrderSetItemIds.update(self.supportRecommender.itemIdsByOrderSetId[orderSetId]);

        # Treat available order set items from the verify time period like "recommended data"
        recommendedData = list();
        for itemId in allAvailableVerifyOrderSetItemIds:
            if not self.supportRecommender.isItemRecommendable(itemId, None, recQuery, self.supportRecommender.categoryIdByItemId):
                continue;   # Skip items that do not fit recommendable criteria (i.e., excluded categories) for fair comparison

            recItemModel = dict(self.supportRecommender.itemsById[itemId]);
            recItemModel["score"] = recItemModel[recQuery.sortField];
            recommendedData.append(recItemModel);
        recommendedData.sort(key=itemgetter(recQuery.sortField), reverse=True)

        # Distill down to just the set of recommended item IDs
        recommendedItemIds = set();
        for i, recommendationModel in enumerate(recommendedData):
            if analysisQuery.numRecommendations > 0 and i >= analysisQuery.numRecommendations:
                break;
            recommendedItemIds.add(recommendationModel["clinical_item_id"]);

        # Summary metrics on how many order items in query and verify periods are recommendable
        # Outer join query for order set items should work same way, but maybe simpler to follow as second query
        itemQuery = \
            """
            select pi.clinical_item_id, pi.item_date >= %(p)s as is_verify_item
            from
               patient_item as pi
            where patient_id = %(p)s
            and item_date >= %(p)s and item_date < %(p)s
            """ % {"p": DBUtil.SQL_PLACEHOLDER}
        itemParams = ( patientItemData["queryEndTime"], patientItemData["patient_id"], patientItemData["baseItemDate"], patientItemData["verifyEndTime"],);
        resultTable = DBUtil.execute(itemQuery, itemParams, conn=conn);

        recommendableQueryItemIds = set();
        recommendableVerifyItemIds = set();
        for itemId, isVerifyItem in resultTable:
            if self.supportRecommender.isItemRecommendable(itemId, None, recQuery, self.supportRecommender.categoryIdByItemId):
                if not isVerifyItem:
                    recommendableQueryItemIds.add(itemId);
                else:
                    recommendableVerifyItemIds.add(itemId);

        # Order Set Usage Summary Data
        orderSetItemData = \
            {   "allUsedOrderSetIds": allUsedOrderSetIds,
                "allUsedOrderSetItemIds": allUsedOrderSetItemIds,
                "allAvailableOrderSetItemIds": allAvailableOrderSetItemIds,
                "recommendableUsedOrderSetItemIds": recommendableUsedOrderSetItemIds,
                "recommendableAvailableOrderSetItemIds": recommendableAvailableOrderSetItemIds,
                "recommendableQueryItemIds": recommendableQueryItemIds,
                "recommendableVerifyItemIds": recommendableVerifyItemIds,
            };
        return (queryItemCountById, verifyItemCountById, recommendedItemIds, recommendedData, orderSetItemData);

    def calculateResultStats( self, patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, baseCountByItemId, recQuery, recommendedData ):
        resultsStatData = RecommendationClassificationAnalysis.calculateResultStats( self, patientItemData, queryItemCountById, verifyItemCountById, recommendedItemIds, baseCountByItemId, recQuery, recommendedData );
        # Copy elements from patient data
        #resultsStatData["weightByOrderSetId"] = recommendedData[0]["weightByOrderSetId"];
        #resultsStatData["numSelectedOrderSets"] = recommendedData[0]["numSelectedOrderSets"];
        return resultsStatData;

    def resultHeaders(self, analysisQuery=None):
        headers = RecommendationClassificationAnalysis.resultHeaders(self,analysisQuery);
        headers.append("usedOrderSetIds");
        headers.append("numUsedOrderSets");
        headers.append("numUsedOrderSetItems");
        headers.append("numAvailableOrderSetItems");
        headers.append("orderSetItemUsageRate");

        headers.append("numRecommendableUsedOrderSetItems");
        headers.append("numRecommendableAvailableOrderSetItems");
        headers.append("numRecommendableQueryItems");
        headers.append("numRecommendableVerifyItems");
        headers.append("numRecommendableQueryVerifyItems");
        headers.append("recommendableQueryVerifyItemFromOrderSetRate");

        return headers;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile>    Validation file in prepared result file format.  Predict items and compare against verify sets similar to RecommendationClassficationAnalysis. \n"+\
                    "   <outputFile>   Validation result stat summaries.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-r", "--numRecs",   dest="numRecs",  default=DEFAULT_RECOMMENDED_ITEM_COUNT, help="Number of orders / items to recommend for comparison against the verification set, sorted in prevalence order.  If skip or set <1, then will use all order set items found.");
        parser.add_option("-O", "--numRecsByOrderSet",   dest="numRecsByOrderSet", action="store_true", help="If set, then look for an order_set_id column to find the key order set that triggered the evaluation time point to determine number of recommendations to consider.");
        parser.add_option("-s", "--sortField",  dest="sortField",  default=DEFAULT_SORT_FIELD, help="Allow overriding of default sort field when returning ranked results (patient_count, name, description, etc.)");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) >= 1:
            query = AnalysisQuery();
            query.preparedPatientItemFile = stdOpen(args[0]);
            query.recommender = OrderSetRecommender();
            query.baseRecQuery = RecommenderQuery();
            # Default exclusions if none specified
            query.baseRecQuery.excludeCategoryIds = query.recommender.defaultExcludedClinicalItemCategoryIds();
            query.baseRecQuery.excludeItemIds = query.recommender.defaultExcludedClinicalItemIds();
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
    instance = OrderSetUsageAnalysis();
    instance.main(sys.argv);
