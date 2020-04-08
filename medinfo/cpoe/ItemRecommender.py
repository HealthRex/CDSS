#!/usr/bin/env python
"""
Primary query module, allowing caller to submit
a set of clinical items (orders, etc.) to prime with,
then this "suggestion / recommendation" module will
return with a ranked and scored list of associated
items / orders.
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

from .DataManager import DataManager;

from .Util import log;
from .Const import AGGREGATOR_OPTIONS;
from .Const import SECONDS_PER_DAY;
from .Const import CORE_FIELDS;

# List of fields that may be aggregated across results by a (weighted) average
WEIGHTED_AVERAGE_FIELDS = ["nAB","nA"];
# Derived statistics that will always be calculated for the recommendation results
DEFAULT_DERIVED_STATS = ["baselineFreq","conditionalFreq","freqRatio"];

# Test value for total patient count when simulating calculations for unit test
SIMULATED_PATIENT_COUNT = 3000.0;

class RecommenderQuery:
    """Simple struct to pass query parameters
    """
    queryItemIds = None;    # IDs of clinical items to query by
    targetItemIds = None;  # IDs of clinical items that only these should be included from any recommended set
    excludeItemIds = None;  # IDs of clinical items that should be excluded from any recommended set
    excludeCategoryIds = None;     # Returned items should be filtered to exclude those that fit into one of the included categories
    timeDeltaMax = None;    # If set to one of the constants (DELTA_ZERO, DELTA_HOUR, etc.), will count item associations that occurred within that time delta as co-occurrent.  If left blank, will just consider all items within a given patient as co-occurrent.
    sortField = None;  # Field to use as the recommendation score for rank sorting order
    sortReverse = None; # Whether to reverse the sort order, defaults to True to get descending order
    fieldFilters = None;    # Specify (score) fields and value to filter by
    limit = None;   # Maximum number of results to return
    maxRecommendedId = None;    # Set as a testing / debug utility, will ignore / not recommend, any items with ID greater than this max (set to 0 to exclude all "normal" data)
    acceptCache = None; # Whether to accept pre-cached item counts so don't have to requery for these base counts every time
    invertQuery = None; # If set, will invert query direction, based on subsequent items and then "recommend" preceding items
    countPrefix = None;    # Prefix to specify what item counts to base stats on (defaults to item counts, allowing repeats, other options include "patient_" for counting per patient or per "encounter_")
    aggregationMethod = None; # Determines what type of weighting (if any) will be used when aggregating recommendations based on multiple query items

    itemsPerCluster = None;   # When using clusters/topics to generate scores, how many top items to consider
    minClusterWeight = None;   # Minimum weight a cluster/topic/orderset contributes to consider it at all

    def __init__(self):
        self.queryItemIds = set();
        self.targetItemIds = set();
        self.excludeItemIds = set();
        self.excludeCategoryIds = set();
        self.timeDeltaMax = None;
        self.sortField = "PPV"; # Default choice
        self.sortReverse = True;    # Default to descending order
        self.fieldFilters = dict();
        self.fieldList = list();    # Keep ordered list of fields noted for display
        self.limit = None;
        self.maxRecommendedId = None;
        self.acceptCache = True;
        self.invertQuery = False;
        self.countPrefix = "";
        self.aggregationMethod = "weighted";    # Default to weighted average

        self.itemsPerCluster = None;
        self.minClusterWeight = 0;

    def sourceCol(self):
        if not self.invertQuery:
            return "clinical_item_id";
        else:
            return "subsequent_item_id";

    def targetCol(self):
        if not self.invertQuery:
            return "subsequent_item_id";
        else:
            return "clinical_item_id";

    def parseParams(self, paramDict):
        """Look through the dictionary for key-value pairs that can be parsed into query object parameters.
        Facilitates easy setup from web or command-line text interfaces.
        """

        if "queryItemIds" in paramDict and paramDict["queryItemIds"]:
            self.queryItemIds = set( [int(itemStr) for itemStr in paramDict["queryItemIds"].split(",")] );
        if "targetItemIds" in paramDict and paramDict["targetItemIds"]:
            self.targetItemIds = set( [int(itemStr) for itemStr in paramDict["targetItemIds"].split(",")] );
        else:
            # If designated specific target items, then no point in excluding any items or categories
            #   Might get overlap with confusing no results
            if "excludeItemIds" in paramDict and paramDict["excludeItemIds"]:
                self.excludeItemIds = set( [int(itemStr) for itemStr in paramDict["excludeItemIds"].split(",")] );
            if "excludeCategoryIds" in paramDict and paramDict["excludeCategoryIds"]:
                self.excludeCategoryIds = set( [int(itemStr) for itemStr in paramDict["excludeCategoryIds"].split(",")] );
        if "timeDeltaMax" in paramDict and paramDict["timeDeltaMax"]:
            self.timeDeltaMax = timedelta(0, int(paramDict["timeDeltaMax"]) );  # Convert to numerical representation (seconds) representing time delta to consider.  # If set to one of the constants (DELTA_ZERO, DELTA_HOUR, etc.), will count item associations that occurred within that time delta as co-occurrent.  If left blank, will just consider all items within a given patient as co-occurrent.
        if "invertQuery" in paramDict:
            self.invertQuery = (paramDict["invertQuery"].lower() not in FALSE_STRINGS);

        if "countPrefix" in paramDict:
            self.countPrefix = paramDict["countPrefix"];
        if "aggregationMethod" in paramDict:
            self.aggregationMethod = paramDict["aggregationMethod"];
        if "resultCount" in paramDict:
            self.limit = int(paramDict["resultCount"]);
        if "maxRecommendedId" in paramDict:
            self.maxRecommendedId = int(paramDict["maxRecommendedId"]);

        # Break out sort method into components
        if "sortField" in paramDict:
            self.sortField = paramDict["sortField"];
        if "sortReverse" in paramDict:
            self.sortReverse = (paramDict["sortReverse"].lower() not in FALSE_STRINGS);

        if "itemsPerCluster" in paramDict:
            self.itemsPerCluster = int(paramDict["itemsPerCluster"]);
        if "minClusterWeight" in paramDict:
            self.minClusterWeight = float(paramDict["minClusterWeight"]);

        # Look for any field filters, expect sequentially numbered starting from 1
        i = 1;
        fieldKey = "filterField%s" % i;
        while fieldKey in paramDict:
            (fieldOp, filterValue) = paramDict[fieldKey].split(":");
            field = fieldOp[:-1];
            parsedValue = None;
            if filterValue != "":
                parsedValue = float(filterValue);
            self.fieldFilters[fieldOp] = parsedValue;
            self.fieldList.append(field);

            i += 1;
            fieldKey = "filterField%s" % i;

    def getDisplayFields(self):
        """Infer display fields based on sort and field options.  Check for duplicates."""
        displayFields = [self.sortField];
        fieldsFound = set(displayFields);
        for field in self.fieldList:
            if field not in fieldsFound:
                displayFields.append(field);
                fieldsFound.add(field);
        return displayFields;

class BaseItemRecommender:
    """Abstract base class for item (e.g., order) recommendation.
    Only define basic interface here, to allow multiple
    concrete subclasses provide concrete implementations,
    whose performance can then be compared against each other.
    """

    def __init__(self):
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source
        self.dataManager = DataManager();

    def __call__(self, query):
        """Primary function.  Given a query object representing
        key clinical items (orders, etc.), return a set of
        clinical items, rank ordered and scored, based on
        pre-computed association strengths.
        Returns as a list of RowItemModels / dictionaries,
        keyed by respective DB column names.
          - clinical_item_id (the clinical item being recommended)
          - score (a numerical score that defines the rank ordering)
        """
        raise NotImplementedError("Abstract base class method.  Sub-class should override.");

    def defaultExcludedClinicalItemCategoryIds(self, conn=None):
        """Return the default list of clinical item categories that
        should be excluded from a recommendation list.
        (Intended to exclude / ignore common, redundant or otherwise mundane and uninteresting items)
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = """select clinical_item_category_id from clinical_item_category where default_recommend = 0""";
            resultTable = self.dataManager.executeCacheOption(query, conn=conn);
            self.dataManager.queryCount += 1;
            excludeIds = set();
            for row in resultTable:
                excludeIds.add(row[0]);
            return excludeIds;
        finally:
            if not extConn:
                conn.close();

    def defaultExcludedClinicalItemIds(self, conn=None):
        """Return the default list of clinical items / orders that
        should be excluded from an recommendation list.
        (Intended to exclude / ignore common, redundant or otherwise mundane and uninteresting items)
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            query = """select clinical_item_id from clinical_item where default_recommend = 0""";
            resultTable = self.dataManager.executeCacheOption(query, conn=conn);
            self.dataManager.queryCount += 1;
            excludeIds = set();
            for row in resultTable:
                excludeIds.add(row[0]);
            return excludeIds;
        finally:
            if not extConn:
                conn.close();

    def isItemRecommendable(clinicalItemId, queryItemIds, recQuery, categoryIdByItemId):
        """Decide if the next clinical item could even possibly appear
        in the recommendation list.  (Because if not, no point in trying to
        test recommender against it).  Typical exclusion issues include:
        - Item already in query set (redundant / repeat orders)
        - Item specifically excluded in recommenderQuery
        - Item's category specifically excluded in recommenderQuery
        """
        if (queryItemIds is not None and clinicalItemId in queryItemIds):
            return False;
        elif categoryIdByItemId is not None:
            if clinicalItemId not in categoryIdByItemId:
                return False;
            categoryId = categoryIdByItemId[clinicalItemId];
            if (recQuery.excludeItemIds is not None and clinicalItemId in recQuery.excludeItemIds) or \
                (recQuery.excludeCategoryIds is not None and categoryId in recQuery.excludeCategoryIds):
                return False;
        return True;
    isItemRecommendable = staticmethod(isItemRecommendable);

    def formatRecommenderResults(self, results, conn=None):
        """Go through the recommender results and add (formatted) columns of additional
        (normalized) information to facilitate subsequent presentation.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            itemIds = set();
            for result in results:
                itemIds.add(result["clinical_item_id"]);

            # Query out clinical item and category text based descriptions
            lookupQuery = SQLQuery();
            lookupQuery.addSelect("ci.clinical_item_id");
            lookupQuery.addSelect("ci.clinical_item_category_id");
            lookupQuery.addSelect("cic.description as category_description");
            lookupQuery.addSelect("ci.name");
            lookupQuery.addSelect("ci.description");
            lookupQuery.addFrom("clinical_item as ci");
            lookupQuery.addFrom("clinical_item_category as cic");
            lookupQuery.addWhere("ci.clinical_item_category_id = cic.clinical_item_category_id");
            lookupQuery.addWhereIn("ci.clinical_item_id", itemIds );

            lookupDataTable = DBUtil.execute( lookupQuery, includeColumnNames=True, conn=conn );
            lookupModelById = modelDictFromList( modelListFromTable(lookupDataTable), "clinical_item_id");
            self.dataManager.queryCount += 1;

            # Add back normalized data to respective result models
            for i, result in enumerate(results):
                itemId = result["clinical_item_id"];
                lookupModel = lookupModelById[itemId];

                result["name"] = lookupModel["name"];
                result["description"] = lookupModel["description"];
                result["clinical_item_category_id"] = lookupModel["clinical_item_category_id"];
                result["category_description"] = lookupModel["category_description"];
                result["rank"] = i+1;
        finally:
            if not extConn:
                conn.close();

    def populateDerivedStats(resultModel, statIds):
        """
        Calculate several derived statistics based on the component item counts in the resultModel,
        largely based on a 2x2 contingency table.

        This can include chi-square stats as well as many other items from StatsUtil.ContingencyStats

        Several good calculator examples with references:
        http://www.medcalc.org/calc/diagnostic_test.php
        """
        if "nAB" not in resultModel:    # Baseline query, so just populate with full correlations
            resultModel["nAB"] = resultModel["nB"];
            resultModel["nA"] = resultModel["N"];

        nAB = resultModel["nAB"];
        nA = resultModel["nA"];
        nB = resultModel["nB"];
        N = resultModel["N"];

        #print >> sys.stderr, nAB, nA, nB, N

        # Defer to StatsUtil for most general calculations
        contStats = ContingencyStats( nAB, nA, nB, N );
        # Adjust values to prevent abnormal stats.  Particularly, avoid divide by zero or negative counts.
        # Later consider if item count exceeds patient count, then artificially suppress that excess for the purposes of the stat calculation
        contStats.normalize(truncateNegativeValues=False);

        #print >> sys.stderr, resultModel["clinical_item_id"], nAB, nA, nB, N
        for statId in statIds:
            if statId not in resultModel:   # Skip stats that have already been populated
                resultModel[statId] = contStats[statId];
                #print >> sys.stderr, statId, resultModel[statId];

    populateDerivedStats = staticmethod(populateDerivedStats);

    def populateAggregateStats(aggregateResult, query, statIds=None):
        """Calculate and populate the aggregate result item with stats based
        on its component items (expected in item keyed by "componentResults"
        to enable subsequent sorting and filtering.

        Will look for stats named in statIds to populate, or if None, then default
        based on the query.sortField and query.fieldFields.

        Look to query.aggregationMethod when have multiple options for how to aggregate components.

        =========================================================

        Notes on NaiveBayes style aggregation below

        Can default aggregation by weighted average of recommendations from each query item.
        Weighting currently based on inverse frequency of the query item, so less
        common (but thus more specific) items will be offerred more weight.  Hopefully
        this yields more specific recommendations, though on the flip-side, means
        aggregate is based on recommendations that have less supporting data.

        Separate optional scaling should be considered to similarly scale down the recommended item
        side by the same background frequency, so that the recommended items won't always
        have very common (but very boring) recommendations
        Essentially TF*IDF (term frequency * inverse document frequency) method to demote interest in common items

        Naive Bayes aggregation
        Nice primer at
        https://www.bionicspirit.com/blog/2012/02/09/howto-build-naive-bayes-classifier.html

        P(B|A1 & A2 & A3)
        = P(A1 & A2 & A3 & B) / P(A1 & A2 & A3)
        = P(A1 & A2 & A3 | B) * P(B) / P(A1 & A2 & A3)

        Key assumption of assuming independence between query items / features (Ax),
            then joint probability is just product of component probabilities

        = P(A1|B)*P(A2|B)*P(A3|B) * P(B) / P(A1)*P(A2)*P(A3)

        Approximating P(A|B) = nAB/nB and P(B) = nB/N

        = (nA1B/nA1 / nB/N) * (nA2B/nA2 / nB/N) * (nA3B/nA3 / nB/N) * nB/N

        = ( (nA1B/nB)*(nA2B/nB)*(nA3B/nB) * nB ) / ( (nA1/N)*(nA2/N)*(nA3/N) * N )

        Above numerator and denominators can then be used to approximate the nAB and nA
        metrics needed to calculate expected vs. observed chi-square statistics.

        ===================================

        Likelihood ratios for genome medicine
        DOI: 10.1186/gm151

        Discusses concepts of using Serial Bayes estimates by compositing multiple likelihood ratios.

        In general,
        PostTestOdds = PreTestOdds * TestLikelihoodRatio

        where               Probability =        Odds / (1+Odds)
        or equivalently,           Odds = Probability / (1-Probability)

        And a test's Positive Likelihood Ratio = (Sensitivity)/(1-Specificity) (for when the test result is positive)
        and a test's Negative Likelihood Ratio = (1-Sensitivity)/(Specificity) (for when the test result is positive)

        For a single test then, can update PreTestProbability -> PostTestProbability by converting to Odds and
        applying (multiplying) the appropriate TestLikelihoodRatio.  Use this new PostTestProbability as a new
        PreTestProbability to apply subsequent TestLikelihoodRatios repeatedly.
        This should theoretically only be valid if each test's result is independent / uncorrelated with all others,
        thus making the testing order irrelevant, but can still be useful for an efficiently computable result.

        No direct equivalent, but try to produce virtual nAB and nA composite counts to facilitate other simulated contingency stats.
        Ends up similar but not identical to NaiveBayes approach.

        PreTestProb = nB/N
        PreTestOdds = nB/(N-nB)

        PositiveLikelihoodRatio(Ai) = (nAiB/nB) / ((nAi-nAiB)/(N-nB))

        PostTestOdds = PreTestOdds * Product(PositiveLikelihoodRatio(Ai))
                     = (nB/(N-nB)) * Product(nAiB/nB) / Product((nAi-nAiB)/(N-nB))
                     = nAB' / (nA'-nAB') (Estimates for conditional counts)

            Thus, estimate virtual conditional counts that will yield the appropriate PostTestProb when reuse the virtual counts:

            nAB' = Product(nAiB/nB) * nB
            (nA'-nAB') = Product((nAi-nAiB)/(N-nB)) * (N-nB)
            nA' = Product((nAi-nAiB)/(N-nB)) * (N-nB) + nAB'
        """
        if statIds is None:
            statIds = {query.sortField}
            for (fieldOp, value) in query.fieldFilters.items():
                if value is not None:
                    field = fieldOp[:-1];
                    statIds.add(field);

        if "componentResultsById" in aggregateResult:
            componentResultsById = aggregateResult["componentResultsById"];

            # Fill in baseline counts directly, as values should be identical across components
            aggregateResult["nB"] = list(componentResultsById.values())[0]["nB"];
            aggregateResult["N"] = list(componentResultsById.values())[0]["N"];

            if query.aggregationMethod in ("weighted","unweighted"):
                # Standard (weighted) average of component scores
                aggregateResult["sum(nAB*weight)"] = 0.0;
                aggregateResult["sum(nA*weight)"] = 0.0;
                aggregateResult["sum(weight)"] = 0.0;

                for componentId, component in componentResultsById.items():
                    component["weight"] = 1.0;
                    if query.aggregationMethod == "weighted":
                        # Weighted scaling of scores inversely proportional to the query item frequency,
                        #   so less common (and thus more specific) query items are paid more attention to in the aggregate recommendations
                        #   Though should beware this may give disproportionate weight to unusually rare query items
                        component["weight"] = 1.0 / component["nA"];

                    aggregateResult["sum(nAB*weight)"] += (component["nAB"] * component["weight"]);
                    aggregateResult["sum(nA*weight)"] += (component["nA"] * component["weight"]);
                    aggregateResult["sum(weight)"] += component["weight"];

                aggregateResult["nAB"] = aggregateResult["sum(nAB*weight)"] / aggregateResult["sum(weight)"];   # Complete the weighted average score calculation
                aggregateResult["nA"] = aggregateResult["sum(nA*weight)"] / aggregateResult["sum(weight)"];

            elif query.aggregationMethod in ("NaiveBayes"):
                # Naive Bayes products
                aggregateResult["product(nAB/nB)"] = 1.0;
                aggregateResult["product(nA/N)"] = 1.0;

                for componentId, component in componentResultsById.items():
                    nAB_ = max(component["nAB"],DEGENERATE_VALUE_ADJUSTMENT);   # Small adjustment to avoid zero value that will wipe out all information in product
                    nA_ = max(component["nA"],DEGENERATE_VALUE_ADJUSTMENT); # Similar check should not be necessary
                    aggregateResult["product(nAB/nB)"] *= nAB_ / component["nB"];
                    aggregateResult["product(nA/N)"] *= nA_ / component["N"];

                aggregateResult["nAB"] = aggregateResult["product(nAB/nB)"] * aggregateResult["nB"]
                aggregateResult["nA"] = aggregateResult["product(nA/N)"] * aggregateResult["N"];

            elif query.aggregationMethod in ("SerialBayes"):
                # "Serial" Bayes method with NaiveBayes assumption,
                #   but past Post-Test Odds based on Pre-Test Odds and successive products of Positive Likelihood Ratios
                """
                # Direct calculation approach
                preTestProbB = float(aggregateResult["nB"]) / aggregateResult["N"];
                preTestOddsB = preTestProbB / (1.0-preTestProbB);

                productLR = 1.0;
                for componentId, component in componentResultsById.iteritems():
                    contStats = ContingencyStats( component["nAB"], component["nA"], component["nB"], component["N"] );
                    contStats.normalize(truncateNegativeValues=True);
                    productLR *= contStats["LR+"];

                postTestOddsB = preTestOddsB * productLR;
                postTestProbB = postTestOddsB / (1+postTestOddsB);

                aggregateResult["nAB"] = postTestProbB*100.0;
                aggregateResult["nA"] = 100.0;  # Arbitrary selection?  Could have done weighted average of component nAs?
                """
                aggregateResult["Product(nAB/nB)"] = 1.0;
                aggregateResult["Product((nA-nAB)/(N-nB))"] = 1.0;

                for componentId, component in componentResultsById.items():
                    nAB_ = max(component["nAB"],DEGENERATE_VALUE_ADJUSTMENT);   # Small adjustment to avoid zero value that will wipe out all information in product
                    nA_ = component["nA"];
                    aggregateResult["Product(nAB/nB)"] *= nAB_ / component["nB"];
                    aggregateResult["Product((nA-nAB)/(N-nB))"] *= (nA_-nAB_) / (component["N"]-component["nB"]);

                aggregateResult["nAB"] = aggregateResult["Product(nAB/nB)"] * aggregateResult["nB"];
                aggregateResult["nA"] = aggregateResult["Product((nA-nAB)/(N-nB))"] * (aggregateResult["N"]-aggregateResult["nB"]) + aggregateResult["nAB"];

        # Populate derived statistics that may be used as scoring measures
        BaseItemRecommender.populateDerivedStats(aggregateResult, statIds);
        aggregateResult["score"] = aggregateResult[query.sortField];

    populateAggregateStats = staticmethod(populateAggregateStats);


    def filterAggregateResultsByQuery( self, aggregateResultsByItemId, query ):
        """Filter down the total collection of aggregateResultsByItemId into
        and ordered list of aggregateResults based on the query sort and filter options.
        Should require calculation of summary statistics for each aggregate result based on component results.
        """
        # Now collect and sort the aggregated results to return only the top relevant results
        aggregateResultsWithScore = list();
        for aggregateResult in aggregateResultsByItemId.values():
            itemId = aggregateResult["clinical_item_id"];

            # Calculate and populate the aggregate result item with stats based on its component items
            #   to enable subsequent sorting and filtering
            self.populateAggregateStats(aggregateResult, query);

            # Look for value filters
            excludeResult = False;
            for (fieldOp, value) in query.fieldFilters.items():
                if value is not None:
                    field = fieldOp[:-1];
                    op = fieldOp[-1];
                    if (aggregateResult[field] < value and op == "<") or (aggregateResult[field] > value and op == ">"):
                        excludeResult = True;
                        break;  # Don't need to look anymore

            if not excludeResult:
                aggregateResultsWithScore.append( (aggregateResult[query.sortField], aggregateResult) );

        aggregateResultsWithScore.sort(key=itemgetter(0));
        if query.sortReverse:
            aggregateResultsWithScore.reverse();    # Descending order of score to get top results

        # Pull out only the top X results to satisfy the query results
        topAggregateResults = list();
        for i, (score, aggregateResult) in enumerate(aggregateResultsWithScore):
            if query.limit is not None and i >= query.limit:
                break;  # Stop adding more results if only asked for a subset
            topAggregateResults.append(aggregateResult);

        return topAggregateResults;



class ItemAssociationRecommender(BaseItemRecommender):
    """Concrete implementation class for item (e.g., order) recommendation.
    Based on simple item-associations, similar to Amazon recommendations.
    That is, prior analysis module should have pre-computed and stored
    association strengths between all items (e.g., orders), and this
    recommender will query just to find those most related items given
    the query set and return them in a rank listed order.

    Score Interpretation:  Average number of times that order is placed for a patient
    given the query set.  Values >1 reflect orders that are typically
    entered multiple times for individual patients (though does not mean 100% of all
    patients get that order).  Thus, values < 1 can be roughly interpreted as a percentage
    of patients who get that order.

    If default is set, will just return whatever are the most common
    clinical items overall as recommendations.  Useful for "cold starts"
    when don't have much initial information to key recommendations from.
    """

    def __call__(self, query, default=False, conn=None):
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;

        try:
            # Determine sorting / scoring field based on time limit parameters
            countField = "count_any";
            if query.timeDeltaMax is not None:
                timeDeltaSeconds = (query.timeDeltaMax.days*SECONDS_PER_DAY + query.timeDeltaMax.seconds);
                countField = "count_%d" % timeDeltaSeconds;
            countField = query.countPrefix+countField;

            sqlQuery = SQLQuery();
            sqlQuery.addSelect("cia."+query.sourceCol()+"");
            sqlQuery.addSelect("cia."+query.targetCol()+"");
            sqlQuery.addSelect("cia."+query.countPrefix+"count_0");
            sqlQuery.addSelect("cia."+countField );
            sqlQuery.addFrom("clinical_item_association as cia");
            sqlQuery.addWhere("count_any > 0"); # Don't bother pulling no association counts (even better if these sparse records were not stored in the first place)

            # Test / Debug case, want to put an artificial limit on items recommended
            if query.maxRecommendedId is not None:
                sqlQuery.addWhere("cia."+query.targetCol()+" <= %s" % query.maxRecommendedId );

            # Caller may want to filter recommendations to exclude certain category of items
            if query.excludeCategoryIds:
                sqlQuery.addFrom("clinical_item as ci");
                sqlQuery.addWhere("cia."+query.targetCol()+" = ci.clinical_item_id");
                sqlQuery.addWhereNotIn("ci.clinical_item_category_id", query.excludeCategoryIds );

            if default:
                # Just query for most common items overall, no particular associations / key item priming
                sqlQuery.addWhere("cia."+query.sourceCol()+" = cia."+query.targetCol()+"");
                sqlQuery.addOrderBy("cia."+query.countPrefix+"count_0 desc");
                sqlQuery.addOrderBy("cia."+query.sourceCol()+"");    # Ensure a stable ordering in case of equal scores
                sqlQuery.limit = query.limit;

                #print >> sys.stderr, "DEFAULT Query:", sqlQuery, sqlQuery.params
                resultTable = self.dataManager.executeCacheOption( sqlQuery, includeColumnNames=True, conn=conn );
                resultModels = modelListFromTable( resultTable );
                resultModels = self.filterResultItems(resultModels, query);

                # Direct DB query results will basically work, just add a score column
                #   Use total number of patient records as a denominator as theoretical number of distinct times an order could be made
                #   Technically not perfectly accurate, since a single patient can have the same order entered in multiple times.
                totalPatients = self.totalPatientCount(query, conn);

                for result in resultModels:
                    nB = result["nB"] = result[query.countPrefix+"count_0"];
                    N = result["N"] = totalPatients;

                    self.populateDerivedStats(result, [query.sortField]);
                    result["score"] = result[query.sortField];
                return resultModels;

            nQueryItems = len(query.queryItemIds);
            if nQueryItems < 1:
                # Special case of an empty query set, just look for the most commonly used items in general
                return self( query, default=True, conn=conn );
            else:
                # Determine sorting / scoring field based on time limit parameters
                countField = "count_any";
                if query.timeDeltaMax is not None:
                    timeDeltaSeconds = (query.timeDeltaMax.days*SECONDS_PER_DAY + query.timeDeltaMax.seconds);
                    countField = "count_%d" % timeDeltaSeconds;
                countField = query.countPrefix+countField;

                #if query.limit is not None:
                    # Don't need to return whole data table?  Maybe just get enough to fulfill query quantity?
                    # But need to expand by query item count however, since aggregating across multiple queries
                    # Could probably incorporate heuristic to query for less than X*n given n query items
                    #   since most likely expect some overlap, or other weighting based on prominence of query items
                #    sqlQuery.limit = query.limit * nQueryItems;
                #   # Above will not work however, since single query is pulling data for all query items,
                #   # and really should be applying cut-off limit to each "sub-query"
                #print >> sys.stderr, "AssocQuery:", sqlQuery, sqlQuery.params;
                resultModels = self.loadResultModels( query, sqlQuery, conn=conn );

                if len(resultModels) < 1:
                    # Not able to find any recommendations based on this query data.  Just return default recommendations then.
                    return self( query, default=True, conn=conn );
                else:
                    aggregateRecs = self.aggregateRecommendations( resultModels, query, countField, conn=conn );
                    return aggregateRecs;
        finally:
            if not extConn:
                conn.close();

    def loadResultModels( self, query, sqlQuery, conn ):
        """Query for the results from the SQL query, but if the dataCache is set on this instance,
        see if this can be retrieved/stored from there as well, to minimize repetitive database hits.
        Instead of serial small DB queries, just do one massive DB query for all possible query items
        and store in memory (few GB for upto 100K items) and return select subsets as requested for much more rapid serial queries.
        """
        simpleSQLQuery = str(sqlQuery).replace(",%s" % DBUtil.SQL_PLACEHOLDER,"");   # Strip down multiple consecutive placeholders

        # Populate a cache if it has not already been so
        dataCache = self.dataManager.dataCache;
        if dataCache is None: dataCache = dict();
        if simpleSQLQuery not in dataCache:
            dataCache[simpleSQLQuery] = dict();

            #print >> sys.stderr, sqlQuery;

            newResultsTable = DBUtil.execute( sqlQuery, includeColumnNames=True, conn=conn );
            newResultModels = modelListFromTable(newResultsTable);
            self.dataManager.queryCount += 1;

            for result in newResultModels:
                #print >> sys.stderr, "CACHE IT:", (result);
                sourceItemId = result[query.sourceCol()];
                if sourceItemId not in dataCache[simpleSQLQuery]:
                    dataCache[simpleSQLQuery][sourceItemId] = list();
                resultCopy = dict(result);
                dataCache[simpleSQLQuery][sourceItemId].append(resultCopy);

        # Pull out the relevant results of interest
        resultModels = list();
        # See if can find what we want from the previously cached results
        for queryItemId in query.queryItemIds:
            if queryItemId in dataCache[simpleSQLQuery]:
                for result in dataCache[simpleSQLQuery][queryItemId]:
                    resultCopy = dict(result);
                    resultModels.append( resultCopy );
                    #print >> sys.stderr, "PULL IT", resultCopy;

        resultModels = self.filterResultItems(resultModels, query);
        return resultModels;


    def filterResultItems(self,resultModels,query):
        """Application level item filtering so get more DB results that can be cached in local memory
        for rapid retrieval again, but retaining filtering options.
        """
        #print >> sys.stderr, "PreFilter", len(resultModels), query.targetCol(), query.queryItemIds, query.targetItemIds, query.excludeItemIds
        filteredModels = list();
        for result in resultModels:
            if query.targetItemIds:
                if result[query.targetCol()] not in query.targetItemIds:
                    continue;   # Skip this itme as caller only interested in certain target items
            elif result[query.targetCol()] in query.queryItemIds:
                continue; # Query items generally have no reason to be in recommended set, but only apply if not already specifying targets

            if query.excludeItemIds and result[query.targetCol()] in query.excludeItemIds:
                continue; # Caller does not want these to be among the suggested items (explicitly excluded ones)

            filteredModels.append(result);
        return filteredModels;

    def aggregateRecommendations( self, resultModels, query, countField, conn=None ):
        """Given all of the resultModels from an association query from multiple
        key clinical items, aggregate them into a single recommendation list
        (with option of link back to component results).

        Should be sorted and filtered by any sort and filter options as specified in the query.
        """
        if len(resultModels) < 1:
            # Not able to find any recommendations based on this query data.  Just return default recommendations then.
            return self( query, default=True, conn=conn );

        # Ensure core association count statistics are available for each result
        self.populateResultCounts( resultModels, query, countField, conn=conn );

        # Organize all possible results by target item ID, with component results as sub items
        aggregateResultsByItemId = self.collateAggregateResuls( resultModels, query );

        # Now filter down the total list based on the query sort and filter options
        filteredAggregateResults = self.filterAggregateResultsByQuery( aggregateResultsByItemId, query );

        return filteredAggregateResults;

    def populateResultCounts( self, resultModels, query, countField, conn=None ):
        """Ensure core association counts are populated for each result model.
        Assume ordering of A as source-query item and B as target-recommended item.  Then,
        nAB = Number of occurrences of item B occuring after A (within a timeframe specified in the query)
        nA = Number of occurrences of item A
        nB = Number of occurrences of item B
        N = Total number of occurrences

        N is usually based on total number of patients, whereas the item n values are based on total orders,
        which may supercede the patient count, resulting in degenerate 2x2 table analyses, but can provide
        meaning such as the average number of item B ordered per patient, instead of the probability.

        Query options should be available to specify preference for n counts to be based on patient occurrences
        ("Number of patients where item B occurs after item A") to fill a properly scaled 2x2 table.
        """
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            # Ensure the summary count cache is up-to-date before using it to query
            self.dataManager.updateClinicalItemCounts(acceptCache=query.acceptCache, conn=conn);

            # Collect baseline relative prevalence / frequency of query and target items to allow subsequent scaling
            countPrefix = query.countPrefix;
            if countPrefix == "":
                countPrefix = "item_";
            baseCountQuery = SQLQuery();
            baseCountQuery.addSelect("ci.clinical_item_id");
            baseCountQuery.addSelect(countPrefix+"count");
            baseCountQuery.addFrom("clinical_item as ci");
            baseCountQuery.addWhere("analysis_status <> 0");    # Will need all records fit for analysis to scale any suggested item
            baseCountResultTable = self.dataManager.executeCacheOption( baseCountQuery, includeColumnNames=True, conn=conn );

            baseCountResultsByItemId = modelDictFromList( modelListFromTable(baseCountResultTable), "clinical_item_id");
            # Count up total number of patients to turn counts into per patient frequency
            totalPatients = self.totalPatientCount(query, conn);

            for result in resultModels:
                queryItemId = result[""+query.sourceCol()+""];
                targetItemId = result[""+query.targetCol()+""];
                baseCountResultsByItemId[queryItemId][countPrefix+"count"]

                # Ensure component items have core association counts.  Convert to floats to facilitate calculations
                nAB = result["nAB"] = float(result[countField]);
                nA = result["nA"] = float(baseCountResultsByItemId[queryItemId][countPrefix+"count"]);
                nB = result["nB"] = float(baseCountResultsByItemId[targetItemId][countPrefix+"count"]);
                N = result["N"] = float(totalPatients);

        finally:
            if not extConn:
                conn.close();

    def collateAggregateResuls( self, resultModels, query ):
        """Organize result models into a new set per target item ID,
        with links back to the component result models.
        """
        aggregateResultsByItemId = dict();
        for result in resultModels:
            targetItemId = result[query.targetCol()];

            if targetItemId not in aggregateResultsByItemId:
                aggregateResultsByItemId[targetItemId] = RowItemModel();
                aggregateResultsByItemId[targetItemId]["clinical_item_id"] = targetItemId;

                # Keep references to original results to allow reconstruction and summary stats later
                aggregateResultsByItemId[targetItemId]["componentResultsById"] = dict();
            aggregateResultsByItemId[targetItemId]["componentResultsById"][result[query.sourceCol()]] = result;
        return aggregateResultsByItemId;

    def organizeByCategory(self, resultModels):
        """Given a collection of recommendation result models,
        reorder them by category, but do so by which categories overall
        score best amongst the results.
        """
        cumulativeScoreByCategoryId = dict();
        for resultModel in resultModels:
            categoryId = resultModel["clinical_item_category_id"];
            if categoryId not in cumulativeScoreByCategoryId:
                cumulativeScoreByCategoryId[categoryId] = 0.0;
            cumulativeScoreByCategoryId[categoryId] += resultModel["score"];

        # Assign category score to each result for sorting
        for resultModel in resultModels:
            categoryId = resultModel["clinical_item_category_id"];
            resultModel["categoryScore"] = cumulativeScoreByCategoryId[categoryId];

        # Re-sort result models first by category (score) then individual item score (descending order)
        resultModels.sort(RowItemFieldComparator(["categoryScore","score"]), reverse=True);

        return resultModels;


    def totalPatientCount(self, query, conn):
        """DB Query for total patient count to use to scale data.
        Option to filter essentially to only test data
        Should only count patients for which association analysis has been done,
        otherwise will be trying to scale against all patients even when only
        a small subset has been analyzed.

        ??? Should probably revise this to total number of encounters rather than patients
        since individual patients may have multiple encounters that each play out differently ???

        Return result as float as most callers will be using in floating point arithmetic (ratios)
        """
        # Check if test query working on simulated data
        isSpecializedQuery = (query.maxRecommendedId is not None);
        if isSpecializedQuery:
            return SIMULATED_PATIENT_COUNT;

        # First do optimistic check that results will already be in database result cache
        dataStr = self.dataManager.getCacheData("analyzedPatientCount", conn=conn);
        if dataStr is not None:
            totalPatients = float(dataStr);
            return totalPatients;

        # No result returned from cache, so do raw query
        totalPatientQuery = SQLQuery();
        totalPatientQuery.addSelect("count(distinct patient_id)")
        totalPatientQuery.addFrom("patient_item");
        totalPatientQuery.addWhere("analyze_date is not null");
        if query.maxRecommendedId is not None:  # Artificial filter to facilitate calculating only on test data
            totalPatientQuery.addWhere(""+query.sourceCol()+" <= %s" % query.maxRecommendedId );
        totalPatients = float(self.dataManager.executeCacheOption(totalPatientQuery, conn=conn)[0][0]);

        # Store the results in the data cache to expedite future repeat queries
        self.dataManager.setCacheData("analyzedPatientCount", str(totalPatients), conn=conn);

        return totalPatients;

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
            print(COMMENT_TAG, json.dumps(summaryData), file=outputFile);

            # Parse out query parameters
            paramDict = dict(urllib.parse.parse_qsl(queryStr,True));
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

class BaselineFrequencyRecommender(ItemAssociationRecommender):
    """Concrete implementation class for item (e.g., order) recommendation.
    Simple default recommender that just recomds items
    based on their baseline frequency, regardless of input query items.
    """
    def __call__(self, query, conn=None):
        return ItemAssociationRecommender.__call__(self,query,default=True,conn=conn);

class RandomItemRecommender(BaseItemRecommender):
    """Absolute baseline for comparison.
    Recommender that just randomly scores and recommends items regardless of input.
    """
    def __call__(self, query, conn=None):

        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;
        try:
            sqlQuery = SQLQuery();
            sqlQuery.addSelect("cia.*");
            sqlQuery.addFrom("clinical_item_association as cia");

            # Caller does not want these to be among the suggested items (explicitly excluded ones, and query items have no reason to be in recommended set)
            if query.excludeItemIds or query.queryItemIds:
                sqlQuery.addWhereNotIn("cia."+query.targetCol()+"", query.excludeItemIds.union(query.queryItemIds) );

            # Test / Debug case, want to put an artificial limit on items recommended
            if query.maxRecommendedId is not None:
                sqlQuery.addWhere("cia."+query.targetCol()+" <= %s" % query.maxRecommendedId );

            # Caller may want to filter recommendations to exclude certain category of items
            if query.excludeCategoryIds:
                sqlQuery.addFrom("clinical_item as ci");
                sqlQuery.addWhere("cia."+query.targetCol()+" = ci."+query.sourceCol()+"");
                sqlQuery.addWhereNotIn("ci.clinical_item_category_id", query.excludeCategoryIds );

            # Just query for individual items, no particular associations / key item priming
            sqlQuery.addWhere("cia."+query.sourceCol()+" = cia."+query.targetCol()+"");

            # Randomize scoring and ordering
            sqlQuery.addSelect("rand() as random");
            sqlQuery.addOrderBy("rand() desc");

            sqlQuery.limit = query.limit;

            resultTable = DBUtil.execute( sqlQuery, includeColumnNames=True, conn=conn );
            resultModels = modelListFromTable( resultTable );

            # Use random number as ranking score
            for result in resultModels:
                result["score"] = result["random"];

            return resultModels;

        finally:
            if not extConn:
                conn.close();

if __name__ == "__main__":
    instance = ItemAssociationRecommender();
    instance.main(sys.argv);
