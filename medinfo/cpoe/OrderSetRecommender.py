#!/usr/bin/env python
"""
Alternative query module using existing Order Sets as basis.
Caller can submit a set of clinical items (orders, etc.) to query with,
then this module will return with a ranked and scored list of associated items / orders.
"""
import sys, os
import time;
from optparse import OptionParser;
import json;
import urlparse;
import math;
from datetime import datetime, timedelta;
from medinfo.common.Const import FALSE_STRINGS, COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.common.StatsUtil import ContingencyStats, UnrecognizedStatException, DEGENERATE_VALUE_ADJUSTMENT;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import RowItemFieldComparator;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.cpoe.ItemRecommender import BaseItemRecommender;
from medinfo.cpoe.Const import COLLECTION_TYPE_ORDER_SET;
from Util import log;
from Const import AD_HOC_SECTION;

class OrderSetRecommender(BaseItemRecommender):
    """Implementation class for item (e.g., order) recommendation based on existing order sets.
    Given query clinical items (orders), look for existing order sets that include them.
    Recommend the remaining order set contents that are not already ordered.
    If multiple order sets match base on initial orders (likely),
    then weight/rank suggestions based on apparent relevance of each order set
    as suggested by the ratio of order set items already in the query divided by the total number of items in the order set.
    
    End up ranking items by P(item|queryItems) = Sum_j[ P(item|OrderSet_j)*P(OrderSet_j|queryItems) ]
    Estimate P(item|OrderSet) = |Insersect(item,OrderSet)| / |OrderSet|
        Above intersection is simply 1 or 0 depending on if item is present in the given OrderSet
    Estimate P(OrderSet|queryItems) = |Intersect(OrderSet,queryItems)| / |queryItems in Any OrderSet|
        Consider the contrary: P(queryItems|OrderSet) = |Intersect(queryItems,OrderSet)| / |OrderSet|
        Previous don't directly scale by size of order set.  Bigger order set more likely to be relevant, but proportionally more likely to hit an intersection by chance
   
    If blank query provided, then use adapt estimates 
        P(OrderSet|queryItems) -> P(OrderSet) = |OrderSet| / |Items in Any OrderSet|
        
    Estimate P(item) = |OrderSets containing item| / |Items in Any Order Set|
        Can derive this by summing over all order sets for P(item|OrderSet_j)*P(OrderSet_j);
    Use above to generate TF*IDF, lift estimates with P(item|query) / P(item)    
    """
    def __init__(self):
        """Initialize module with prior generated model and word document counts from TopicModel module.
        """
        BaseItemRecommender.__init__(self);

        # Cached lookup data.  Don't repeat work for serial queries
        self.itemsById = None;
        self.patientCountByItemId = None;
        self.categoryIdByItemId = None;
        self.candidateItemIds = None;
        
        self.itemIdsByOrderSetId = None;
        self.orderSetIdsByItemId = None;
    
    def initItemLookups(self, query):
        """Load lookup info and save into local member variables for reuse later
        so don't have to do wasteful repeat DB lookups for serial queries
        """
        # Build mutual lookup tables for all order sets and clinical items contained
        self.itemIdsByOrderSetId = dict();
        self.orderSetIdsByItemId = dict();
        results = DBUtil.execute \
            ("""select ic.external_id, ici.clinical_item_id
                from item_collection_item as ici, item_collection as ic
                where ic.item_collection_id = ici.item_collection_id
                and ic.section <> %(p)s
                and ici.collection_type_id = %(p)s
                """ % {"p": DBUtil.SQL_PLACEHOLDER},
                (AD_HOC_SECTION, COLLECTION_TYPE_ORDER_SET)
            );
        for orderSetId, itemId in results:
            if orderSetId not in self.itemIdsByOrderSetId:
                self.itemIdsByOrderSetId[orderSetId] = set();
            self.itemIdsByOrderSetId[orderSetId].add(itemId);
            
            if itemId not in self.orderSetIdsByItemId:
                self.orderSetIdsByItemId[itemId] = set();
            self.orderSetIdsByItemId[itemId].add(orderSetId);

        self.itemsById = DBUtil.loadTableAsDict("clinical_item");
        self.categoryIdByItemId = dict();
        self.patientCountByItemId = dict();
        for itemId, item in self.itemsById.iteritems():
            self.categoryIdByItemId[itemId] = item["clinical_item_category_id"];
            self.patientCountByItemId[itemId] = item["patient_count"];
        self.candidateItemIds = set();
        emptyQuerySet = set();
        for itemId in self.orderSetIdsByItemId.keys():
            if self.isItemRecommendable(itemId, emptyQuerySet, query, self.categoryIdByItemId):
                self.candidateItemIds.add(itemId);
        
    def __call__(self, query):
        # Given query items, lookup existing order sets to find and score related items

        # Load item lookup information
        if self.itemsById is None:
            self.initItemLookups(query);

        # Adapt query into dictionary format
        queryItemCountById = query.queryItemIds;
        if not isinstance(queryItemCountById, dict):    # Not a dictionary, probably a one dimensional list/set, then just add counts of 1
            itemIds = queryItemCountById;
            queryItemCountById = dict();
            for itemId in itemIds:
                queryItemCountById[itemId] = 1;

        # Primary execution.  Apply query to generate scored relationship to each order set.
        weightByOrderSetId = self.estimateOrderSetWeights(queryItemCountById, self.itemIdsByOrderSetId, self.orderSetIdsByItemId);

        # Composite scores for (recommendable) items by taking weighted average across the top items for each topic
        recScoreByItemId = dict();
        for itemId in self.candidateItemIds:
            if self.isItemRecommendable(itemId, queryItemCountById, query, self.categoryIdByItemId):
                recScoreByItemId[itemId] = 0.0;
        for orderSetId, orderSetWeight in weightByOrderSetId.iteritems():
            for itemId in recScoreByItemId.keys():
                itemWeight = self.itemOrderSetWeight(itemId, orderSetId, self.itemIdsByOrderSetId);
                recScoreByItemId[itemId] += orderSetWeight*itemWeight;

        # Build 2-pls with lists to sort by score
        recommendedData = list();
        numItemsInAnyOrderSet = len(self.orderSetIdsByItemId);
        for itemId, totalItemWeight in recScoreByItemId.iteritems():
            tfidf = 0.0;

            if itemId in self.orderSetIdsByItemId:
                numOrderSetsWithItem = len(self.orderSetIdsByItemId[itemId]);
                tfidf = totalItemWeight * numItemsInAnyOrderSet / numOrderSetsWithItem;    # Scale TF*IDF score based on baseline order set counts to prioritize disproportionately common items
            itemModel = \
                {   "totalItemWeight": totalItemWeight, "tf": totalItemWeight, "PPV": totalItemWeight, "P(item|query)": totalItemWeight, "P(B|A)": totalItemWeight,
                    "tfidf": tfidf, "lift": tfidf, "interest": tfidf, "P(item|query)/P(item)": tfidf, "P(B|A)/P(B)": tfidf,
                    "clinical_item_id": itemId,
                    "weightByOrderSetId": weightByOrderSetId, "numSelectedOrderSets": len(weightByOrderSetId),  # Duplicate for each item, but persist here to enable retrieve by caller
                };
            itemModel["score"] = itemModel[query.sortField];
            recommendedData.append(itemModel);
        recommendedData.sort( RowItemFieldComparator(["score","clinical_item_id"]), reverse=True);
        return recommendedData;

    def estimateOrderSetWeights(self, queryItemIds, itemIdsByOrderSetId, orderSetIdsByItemId):
        """
        Estimate each P(OrderSet|queryItems) = |Intersect(OrderSet,queryItems)| / |queryItems in Any OrderSets|

        If blank query or no order set matches found, then use alternative estimate for 
            P(OrderSet|queryItems) -> P(OrderSet), based on the size of the OrderSet relative to the size of all OrderSets combined
        """
        numItemsInAnyOrderSet = float(len(orderSetIdsByItemId));

        queryItemsInAnyOrderSet = set();
        for orderSetId, itemIds in itemIdsByOrderSetId.iteritems():
            queryItemsInAnyOrderSet.update( itemIds.intersection(queryItemIds) );
        numQueryItemsInAnyOrderSet = float(len(queryItemsInAnyOrderSet));
        if numQueryItemsInAnyOrderSet < 1:  # Blank query or otherwise searching for things we have no data.  
            # Treat as if effectively querying for all possible query items equally
            queryItemIds = queryItemsInAnyOrderSet = set(orderSetIdsByItemId.keys());
            numQueryItemsInAnyOrderSet = float(len(queryItemsInAnyOrderSet));
        
        weightByOrderSetId = dict();
        for orderSetId, itemIds in itemIdsByOrderSetId.iteritems():
            numQueryItemsInOrderSet = len(itemIds.intersection(queryItemIds));
            weightByOrderSetId[orderSetId] = numQueryItemsInOrderSet / numQueryItemsInAnyOrderSet;
        return weightByOrderSetId;

    def itemOrderSetWeight(self, itemId, orderSetId, itemIdsByOrderSetId):
        """Estimate P(item|OrderSet) = |Insersect(item,OrderSet)| / |OrderSet|
        Above intersection is simply 1 or 0 depending on if item is present in the given OrderSet
        """
        orderSetItemIds = itemIdsByOrderSetId[orderSetId];
        queryIntersectionSize = len(orderSetItemIds.intersection([itemId]));
        orderSetSize = float(len(orderSetItemIds));
        itemWeight = queryIntersectionSize / orderSetSize;
        return itemWeight;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <queryStr> [<outputFile>]\n"+\
                    "   <queryStr> Query string to specify what recommendation items to retrieve.\n"+\
                    "       Refer to RecommenderQuery or HTML example code for elaboration of options\n"+\
                    "       Expect formatting like a URL query string: queryItemIds=1,2&resultCount=10&sortField=conditionalFreq&filterField0=baselineFreq<0.01...\n"+\
                    "       The sortField and filterFields will be used to determine what numerical / score columns to dislpay\n"+\
                    "   <outputFile>    Tab-delimited table of recommender results..\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)

        (options, args) = parser.parse_args(argv[1:])

        """
        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            queryStr = args[0];
            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            # Parse out query parameters
            paramDict = dict(urlparse.parse_qsl(queryStr,True));
            query = RecommenderQuery();
            query.parseParams(paramDict);
            displayFields = query.getDisplayFields();

            # Core recommender query
            recommendedData = self( query );
            if recommendedData:
                # Denormalize results with links to clinical item descriptions
                self.formatRecommenderResults(recommendedData);
                # Ensure derived fields are populated if selected for display
                for resultModel in recommendedData:
                    self.populateDerivedStats(resultModel, displayFields);

            colNames = ["rank","clinical_item_id","name","description","category_description"];
            colNames.extend(displayFields);
            colNames.extend(CORE_FIELDS);   # Always include the core fields

            recommendedData.insert(0, RowItemModel(colNames,colNames) );    # Insert a mock record to get a header / label row
            formatter = TextResultsFormatter(outputFile);
            formatter.formatResultDicts( recommendedData, colNames );
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);
    """

if __name__ == "__main__":
    instance = OrderSetRecommender();
    instance.main(sys.argv);
