#!/usr/bin/env python
"""
Alternative query module using topic models as basis.
Caller can submit a set of clinical items (orders, etc.) to query with,
then this module will return with a ranked and scored list of associated items / orders.
"""
import sys, os
import time;
from operator import itemgetter
from optparse import OptionParser;
import json;
import urllib.parse;
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
from medinfo.cpoe.TopicModel import TopicModel;
from .Util import log;

class TopicModelRecommender(BaseItemRecommender):
    """Implementation class for item (e.g., order) recommendation based on topic models 
    (LDA Latent Dirichlet Allocation or HDP Hierarchical Dirichlet Process).
    """
    def __init__(self, model, docCountByWordId=None):
        """Initialize module with prior generated model and word document counts from TopicModel module.
        """
        BaseItemRecommender.__init__(self);
        self.modeler = TopicModel();    # Utility instance to run off of

        if docCountByWordId:    # Specified both options
            self.model = model;
            self.docCountByWordId = docCountByWordId;
        else:   # If only the first one specified, interpret it as a base filename to load the objects from
            filename = model;
            (self.model, self.docCountByWordId) = self.modeler.loadModelAndDocCounts(filename);

        # Cached lookup data.  Don't repeat work for serial queries
        self.itemsById = None;
        self.categoryIdByItemId = None;
        self.candidateItemIds = None;
        self.weightByItemIdByTopicId = None;
    
    def initItemLookups(self, query):
        self.itemsById = DBUtil.loadTableAsDict("clinical_item");
        self.categoryIdByItemId = dict();
        for itemId, item in self.itemsById.items():
            self.categoryIdByItemId[itemId] = item["clinical_item_category_id"];
        self.candidateItemIds = set();
        emptyQuerySet = set();
        for itemId in list(self.docCountByWordId.keys()):
            if self.isItemRecommendable(itemId, emptyQuerySet, query, self.categoryIdByItemId):
                self.candidateItemIds.add(itemId);
    
    def __call__(self, query):
        # Given query items, use model to find related topics with relationship scores

        # Load item category lookup information
        if self.itemsById is None:
            self.initItemLookups(query);

        # Load model weight parameters once to save time on serial queries
        if self.weightByItemIdByTopicId is None:
            self.weightByItemIdByTopicId = self.modeler.generateWeightByItemIdByTopicId(self.model, query.itemsPerCluster);

        # Adapt query into bag-of-words format
        queryItemCountById = query.queryItemIds;
        if not isinstance(queryItemCountById, dict):    # Not a dictionary, probably a one dimensional list/set, then just add counts of 1
            itemIds = queryItemCountById;
            queryItemCountById = dict();
            for itemId in itemIds:
                queryItemCountById[itemId] = 1;
        observedIds = set();
        queryBag = list(self.modeler.itemCountByIdToBagOfWords(queryItemCountById, observedIds, self.itemsById, query.excludeCategoryIds));

        # Primary model execute.  Apply to query to generate scored relationship to each "topic"
        topicWeights = self.model[queryBag];
        weightByTopicId = dict();
        for (topicId, topicWeight) in topicWeights:
            weightByTopicId[topicId] = topicWeight;

        # Composite scores for (recommendable) items by taking weighted average across the top items for each topic
        recScoreByItemId = dict();
        for itemId in self.candidateItemIds:
            if self.isItemRecommendable(itemId, queryItemCountById, query, self.categoryIdByItemId):
                recScoreByItemId[itemId] = 0.0;
        for topicId, topicWeight in weightByTopicId.items():
            if topicWeight > query.minClusterWeight:    # Ignore topics with tiny contribution
                weightByItemId = self.weightByItemIdByTopicId[topicId];
                for itemId in list(recScoreByItemId.keys()):
                    itemWeight = 0.0;
                    if itemId in weightByItemId:
                        itemWeight = weightByItemId[itemId];
                    recScoreByItemId[itemId] += topicWeight*itemWeight;

        # Build 2-pls with lists to sort by score
        recommendedData = list();
        for itemId, totalItemWeight in recScoreByItemId.items():
            tfidf = 0.0;
            if itemId in self.docCountByWordId and self.docCountByWordId[itemId] > 0.0:
                tfidf = totalItemWeight * self.docCountByWordId[None] / self.docCountByWordId[itemId];    # Scale TF*IDF score based on baseline document counts to prioritize disproportionately common items
            itemModel = \
                {   "totalItemWeight": totalItemWeight, "tf": totalItemWeight, "PPV": totalItemWeight, "P(item|query)": totalItemWeight, "P(B|A)": totalItemWeight,
                    "tfidf": tfidf, "lift": tfidf, "interest": tfidf, "P(item|query)/P(item)": tfidf, "P(B|A)/P(B)": tfidf,
                    "clinical_item_id": itemId,
                    "weightByTopicId": weightByTopicId, "numSelectedTopics": len(weightByTopicId),  # Duplicate for each item, but persist here to enable retrieve by caller
                };
            itemModel["score"] = itemModel[query.sortField];
            recommendedData.append(itemModel);
        recommendedData.sort(key=itemgetter("score"), reverse=True);
        return recommendedData;

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
    instance = TopicModelRecommender();
    instance.main(sys.argv);
