#!/usr/bin/env python
"""
General preparation step whose output can be reviewed in multiple ways
    instead of directly applying RecommendationClassification or OutcomePrediction, etc.
Given set of patient IDs of interest and some query / extraction parameters,
  list out the patients along with the set of clinical_item_ids relevant for that patient's "query" period
  as well as the clinical_item_ids in their "verify" period.
  Predesignated outcomeIds of interest will be listed by their presence or abscense as well.
"""

import sys, os
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;
from datetime import timedelta;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, loadJSONDict;
from medinfo.common.IteratorFactory import FileFactory;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.ItemRecommender import RecommenderQuery, ItemAssociationRecommender;
from medinfo.cpoe.TopicModel import TopicModel;
from medinfo.cpoe.Const import AD_HOC_SECTION;
from Util import log;
from Const import MAX_BASE_ITEM_TIME_RESOLUTION;

from medinfo.analysis.Const import OUTCOME_ABSENT, OUTCOME_PRESENT, OUTCOME_IN_QUERY;
from medinfo.analysis.Const import NEGATIVE_OUTCOME_STRS;

from BaseCPOEAnalysis import AnalysisQuery;
from BaseCPOEAnalysis import BaseCPOEAnalysis;

class PreparePatientItems(BaseCPOEAnalysis):
    def __init__(self):
        BaseCPOEAnalysis.__init__(self);
        self.categoryIdByItemId = None;

    def __call__(self, analysisQuery, conn=None):
        extConn = True;
        if conn is None:
            conn = self.connFactory.connection();
            extConn = False;

        try:
            # Start building results data
            progress = ProgressDots(50,1,"Patients");

            # Query for all of the order / item data for the specified patients.  Load one patient's data at a time
            for patientItemData in self.loadPatientItemData(analysisQuery, conn=conn):
                patientId = patientItemData["patient_id"];
                if self.prepareResultModel(patientItemData, analysisQuery, patientId):
                    yield patientItemData;
                progress.update();
            # progress.printStatus();
        finally:
            if not extConn:
                conn.close();

    def loadPatientItemData(self, analysisQuery, conn=None):
        """Load up patient information based on the analysisQuery from the database
        to find query and verify subsets for subsequent analysis.
        If sourceFile is provided, then assume that the queries were previously done
        and persisted to a file as per the main call function, and just load / parse it from file
        instead of doing a big DB query and manipulation
        """
        # Preload some lookup data to facilitate subsequent checks
        self.categoryIdByItemId = dict();
        lookupTable = DBUtil.execute("select clinical_item_id, clinical_item_category_id from clinical_item", conn=conn);
        for (clinicalItemId, categoryId) in lookupTable:
            self.categoryIdByItemId[clinicalItemId] = categoryId;

        if analysisQuery.preparedPatientItemFile is None:
            for (patientId, patientItemList) in self.queryPatientClinicalItemData(analysisQuery, conn=conn):
                # Parse through the patient's item list and run a query to get the top recommended IDs for comparison
                for patientItemData in self.extractPatientItemData(analysisQuery, analysisQuery.baseRecQuery, patientId, patientItemList, self.categoryIdByItemId):
                    yield patientItemData;
        else:
            # File provided, apparently data loaded before, just read/parse off file instead
            for patientItemData in self.parsePreparedResultFile(analysisQuery.preparedPatientItemFile, analysisQuery):
                yield patientItemData;

    def queryPatientClinicalItemData(self, analysisQuery, conn):
        """Query for all of the order / item data for each patient
        noted in the analysisQuery and yield them one list of clinicalItemIds
        at a time.
        Generated iterator over 2-ples (patientId, clinicalItemList)
            - Patient ID: ID of the patient for which the currently yielded item intended for
            - Clinical Item List:
                List of all of the relevant clinical items for this patient
        """
        analysisQuery.filteredPatientIds = set(analysisQuery.patientIds);
        if analysisQuery.baseItemId is not None:
            # Do a pre-query to only check patients for whom the base item even exists,
            #   otherwise may waste a lot of time pulling up data on patients that are not relevant
            sqlQuery = SQLQuery();
            sqlQuery.addSelect("distinct pi.patient_id");
            sqlQuery.addFrom("patient_item as pi");
            sqlQuery.addWhereEqual("pi.clinical_item_id", analysisQuery.baseItemId );
            if analysisQuery.startDate is not None:
                sqlQuery.addWhereOp("pi.item_date",">=", analysisQuery.startDate );
            if analysisQuery.endDate is not None:
                sqlQuery.addWhereOp("pi.item_date","<", analysisQuery.endDate );

            patientIdTable = DBUtil.execute( sqlQuery, conn=conn );
            analysisQuery.filteredPatientIds.clear(); # Reset to just those IDs found
            for (patientId,) in patientIdTable:
                analysisQuery.filteredPatientIds.add(patientId);

        orderSetCursor = None;
        orderSetLinkRow = None;
        orderSetHeaders = ("patient_id","patient_item_id","item_collection_item_id","item_collection_id","order_set_id");
        if analysisQuery.byOrderSets:
            # Effectively want to outer join patient item query to order set linkage data, but avoid doing in SQL for inconsistent syntax
            # Depend on using the same sort order (patient ID, item date) for efficient parallel scans to join data
            orderSetQuery = SQLQuery();
            orderSetQuery.addSelect("pi.patient_id");
            orderSetQuery.addSelect("pi.patient_item_id");
            orderSetQuery.addSelect("picl.item_collection_item_id");
            orderSetQuery.addSelect("ici.item_collection_id");
            orderSetQuery.addSelect("ic.external_id as order_set_id");
            orderSetQuery.addFrom("patient_item as pi");
            orderSetQuery.addFrom("patient_item_collection_link as picl");
            orderSetQuery.addFrom("item_collection_item as ici");
            orderSetQuery.addFrom("item_collection as ic");
            orderSetQuery.addWhere("pi.patient_item_id = picl.patient_item_id");
            orderSetQuery.addWhere("picl.item_collection_item_id = ici.item_collection_item_id");
            orderSetQuery.addWhere("ici.item_collection_id = ic.item_collection_id");
            orderSetQuery.addWhereIn("pi.patient_id", analysisQuery.filteredPatientIds );
            orderSetQuery.addWhereNotEqual("ic.section", AD_HOC_SECTION );
            if analysisQuery.startDate is not None:
                orderSetQuery.addWhereOp("pi.item_date",">=", analysisQuery.startDate );
            if analysisQuery.endDate is not None:
                orderSetQuery.addWhereOp("pi.item_date","<", analysisQuery.endDate );
            orderSetQuery.addOrderBy("pi.patient_id");
            orderSetQuery.addOrderBy("pi.item_date");

            # Execute a parallel query for order set item links
            orderSetCursor = conn.cursor();
            orderSetCursor.execute( str(orderSetQuery), tuple(orderSetQuery.params) );
            orderSetLinkRow = orderSetCursor.fetchone();

        rowHeaders = ("patient_item_id","patient_id","clinical_item_id","clinical_item_category_id","analysis_status","item_date");
        sqlQuery = SQLQuery();
        sqlQuery.addSelect("pi.patient_item_id");
        sqlQuery.addSelect("pi.patient_id");
        sqlQuery.addSelect("pi.clinical_item_id");
        sqlQuery.addSelect("ci.clinical_item_category_id");
        sqlQuery.addSelect("ci.analysis_status");
        sqlQuery.addSelect("pi.item_date");
        sqlQuery.addFrom("clinical_item_category as cic");
        sqlQuery.addFrom("clinical_item as ci");
        sqlQuery.addFrom("patient_item as pi");
        sqlQuery.addWhere("cic.clinical_item_category_id = ci.clinical_item_category_id");
        sqlQuery.addWhere("ci.clinical_item_id = pi.clinical_item_id");
        # Don't use items whose default is to be excluded from analysis
        #   Unless part of specifically sought after base category id
        if analysisQuery.baseCategoryId is None and analysisQuery.baseItemId is None:
            sqlQuery.addWhere("ci.analysis_status <> 0");
        elif analysisQuery.baseCategoryId is not None:
            sqlQuery.addWhere("(ci.analysis_status <> 0 or ci.clinical_item_category_id = %s)" % analysisQuery.baseCategoryId);
        elif analysisQuery.baseItemId is not None:
            sqlQuery.addWhere("(ci.analysis_status <> 0 or ci.clinical_item_id = %s)" % analysisQuery.baseItemId);

        if analysisQuery.startDate is not None:
            # Look for items within specified date range, but accept old items from designated past categories
            sqlQuery.openWhereOrClause();
            sqlQuery.addWhereOp("pi.item_date",">=", analysisQuery.startDate );
            if analysisQuery.pastCategoryIds:
                sqlQuery.addWhereIn("ci.clinical_item_category_id", analysisQuery.pastCategoryIds);
            sqlQuery.closeWhereOrClause();
        if analysisQuery.endDate is not None:
            sqlQuery.addWhereOp("pi.item_date","<", analysisQuery.endDate );

        #sqlQuery.addWhere("cic.default_recommend <> 0");
        #sqlQuery.addWhere("ci.default_recommend <> 0");

        sqlQuery.addWhereIn("pi.patient_id", analysisQuery.filteredPatientIds );

        sqlQuery.addOrderBy("pi.patient_id");
        sqlQuery.addOrderBy("pi.item_date");

        # Execute the actual query for patient order / item data
        cursor = conn.cursor();
        cursor.execute( str(sqlQuery), tuple(sqlQuery.params) );

        currentPatientId = None;
        patientItemList = list();

        row = cursor.fetchone();
        while row is not None:
            patientItem = RowItemModel( row, rowHeaders );
            patientId = patientItem["patient_id"];

            if currentPatientId is None:
                currentPatientId = patientId;

            if patientId != currentPatientId:
                # Changed patient, yield the existing data for the previous patient after linking any order set data
                orderSetLinkRow = self.linkOrderSetData(orderSetCursor, orderSetHeaders, orderSetLinkRow, currentPatientId, patientItemList);
                yield (currentPatientId, patientItemList);
                # Update our data tracking for the current patient
                currentPatientId = patientId;
                patientItemList = list();

            patientItemList.append(patientItem);

            row = cursor.fetchone();

        # Yield / return the last patient data
        orderSetLinkRow = self.linkOrderSetData(orderSetCursor, orderSetHeaders, orderSetLinkRow, currentPatientId, patientItemList);
        yield (currentPatientId, patientItemList);

        cursor.close();

        if orderSetCursor is not None:
            orderSetCursor.close();

    def linkOrderSetData(self, orderSetCursor, orderSetHeaders, orderSetLinkRow, patientId, patientItemList):
        """Scan through order set link cursor (and keep track of last row encountered)
        to find linked items for the given patient ID (assumes the cursor is sorted in order by patient ID).
        Update the patientItems with order set link information, null/None if does not exist (i.e., outer join).
        """
        if orderSetCursor is not None:
            orderSetLinkByPatientItemId = dict();

            orderSetLinkItem = None;
            if orderSetLinkRow is not None:
                orderSetLinkItem = RowItemModel( orderSetLinkRow, orderSetHeaders );
            # Scan through cursor until encounter a later patient or end of cursor data stream
            while orderSetLinkItem is not None and orderSetLinkItem["patient_id"] <= patientId:

                if orderSetLinkItem["patient_id"] == patientId:
                    # Matched patient, store links in memory for subsequent lookup
                    orderSetLinkByPatientItemId[orderSetLinkItem["patient_item_id"]] = orderSetLinkItem;

                orderSetLinkItem = None;
                orderSetLinkRow = orderSetCursor.fetchone();
                if orderSetLinkRow is not None:
                    orderSetLinkItem = RowItemModel( orderSetLinkRow, orderSetHeaders );

            # Now pass through patient data to look for matching links
            for patientItem in patientItemList:
                patientItem["item_collection_item_id"] = None;  # Default to None to complete outer join
                patientItem["item_collection_id"] = None;
                patientItem["order_set_id"] = None;
                if patientItem["patient_item_id"] in orderSetLinkByPatientItemId:
                    orderSetLink = orderSetLinkByPatientItemId[patientItem["patient_item_id"]];
                    patientItem.update(orderSetLink);

        return orderSetLinkRow;

    def extractPatientItemData(self, analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId):
        """Given the primary query data and patient clinical item list for a given test patient,
        Parse through the item list to extract out the relevant subset information
        (items to use for query and verification, presence of target items, etc.)
        """
        # Think about making this more object-oriented (polymorphism) later, but for now just check
        #   query conditions to decide how to extract out query and validation data item sets
        extractor = None;
        if analysisQuery.byOrderSets:
            extractor = ItemsByOrderSetExtractor();
        elif (analysisQuery.baseCategoryId is not None or analysisQuery.baseItemId is not None) and analysisQuery.queryTimeSpan is not None:
            extractor = ItemsByBaseItemExtractor();
        elif analysisQuery.numQueryItems is not None and analysisQuery.numVerifyItems is not None:
            extractor = ItemsByCountExtractor();

        for patientItemData in extractor(analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, self):
            yield patientItemData;


    def prepareResultModel(self, patientItemData, analysisQuery, patientId):
        """Get patientItemData model prepared for output formatting"""
        if "queryItemCountById" not in patientItemData:
            return False;   # Apparently unable to find data for this patient.  Skip it / flag issue then and move on

        patientItemData["patient_id"] = patientId;
        patientItemData["queryItemCountByIdJSON"] = json.dumps(patientItemData["queryItemCountById"]);
        patientItemData["verifyItemCountByIdJSON"] = json.dumps(patientItemData["verifyItemCountById"]);

        # Translate outcome IDs into explicit columns / fields
        for outcomeId in analysisQuery.baseRecQuery.targetItemIds:
            patientItemData["outcome.%s" % outcomeId] = patientItemData["existsByOutcomeId"][outcomeId];
        return True;

    def resultHeaders(self, analysisQuery):
        headers = \
            [   "patient_id",
                "queryItemCountByIdJSON",
                "verifyItemCountByIdJSON",
            ];
        if analysisQuery.queryTimeSpan is not None:
            headers.extend \
                ([  "baseItemId",
                    "baseItemDate",
                    "queryStartTime",
                    "queryEndTime",
                    "verifyEndTime",
                ]);
        if analysisQuery.byOrderSets:
            headers.append("order_set_id");
        for outcomeId in analysisQuery.baseRecQuery.targetItemIds:
            headers.append("outcome.%s" % outcomeId);
        return headers;

    def parsePreparedResultFile(self, inputFile, analysisQuery=None):
        """Invert main call that generates a text output file.  Parse that text output file
        and generate data row objects, equivalent to what would have come from querying the database directly.
        """
        prog = ProgressDots();
        for i, dataRow in enumerate(TabDictReader(inputFile)):
            existsByOutcomeId = None;
            dataKeys = dataRow.keys();  # Retrieve separate from iteration, as will be modifying contents as iterate
            for key in dataKeys:
                value = dataRow[key];
                if key.endswith("id") or key.endswith("Id"):
                    dataRow[key] = int(value);
                elif key.endswith("Date") or key.endswith("Time"):
                    dataRow[key] = DBUtil.parseDateValue(dataRow[key]);
                elif key.endswith("JSON"):  # Parse as count dictionary
                    subKey = key[:-len("JSON")];    # Clip of JSON suffix
                    dataRow[subKey] = loadJSONDict(dataRow[key], int, int);

                if key.startswith("outcome."):  # Keep track of all available outcomes in specific dictionary
                    dataRow[key] = int(value);
                    outcomeId = int(key[len("outcome."):]);
                    if existsByOutcomeId is None:
                        existsByOutcomeId = dict();
                    existsByOutcomeId[outcomeId] = dataRow[key];
                    if i == 0 and analysisQuery is not None:
                        analysisQuery.baseRecQuery.targetItemIds.add(outcomeId);
            if existsByOutcomeId is not None:
                dataRow["existsByOutcomeId"] = existsByOutcomeId;

            yield dataRow;
            prog.update();
        inputFile.close();
        # prog.printStatus();

    def convertResultsFileToFeatureMatrix(self, inputFilename, incHeaders=True):
        """Convert results file from primary prepare patient items script into a (sparse) feature matrix
        to facilitate subsequent analysis.  Implemented as a generator over matrix rows to stream through data
        incHeaders:    Whether to include a header label row with result
        """
        inputFileFactory = FileFactory(inputFilename);

        itemColumnHeaders = ["queryItemCountByIdJSON", "verifyItemCountByIdJSON"];
        allItemIds = set();    # Keep track of unique set of all item IDs encountered
        allItemIdList = None;
        baseHeaders = None; # Not including item IDs
        itemIdHeaders = None;
        headers = None;
        nLines = 0;

        # First copy any column headers besides the item based ones
        inputFile = iter(inputFileFactory);
        line = COMMENT_TAG;
        while line.startswith(COMMENT_TAG): # Find the first non-comment line
            line = inputFile.readline().strip();
        headers = line.split("\t");    # Assumes tab-separated

        for itemCol in itemColumnHeaders:
            headers.remove(itemCol);
        inputFile.close();

        # First full pass through data to determine column list by pulling out the total list of query and verify items
        inputFile = iter(inputFileFactory);
        for inputDict in TabDictReader(inputFile):
            for itemCol in itemColumnHeaders:
                itemCountById = loadJSONDict(inputDict[itemCol],int,int);
                allItemIds.update(itemCountById.iterkeys());
            nLines += 1;
        inputFile.close();

        # Add sorted, unique list of item IDs to the expected column headers
        baseHeaders = list(headers);    # Copy before hitting item IDs.
        allItemIdList = list(allItemIds);
        allItemIdList.sort();
        itemIdHeaders = [str(itemId) for itemId in allItemIdList];
        headers.extend(itemIdHeaders);

        if incHeaders:
            yield headers;

        # Now do real pass through to generate one row of results at a time
        prog = ProgressDots(total=nLines);
        inputFile = iter(inputFileFactory);
        for inputDict in TabDictReader(inputFile):
            # Start with base headers not related to items
            resultRow = list();
            for header in baseHeaders:
                resultRow.append(inputDict[header]);

            # Figure out what items are included in this row
            rowItemCountById = dict();
            for itemCol in itemColumnHeaders:
                itemCountById = loadJSONDict(inputDict[itemCol],int,int);
                for itemId, itemCount in itemCountById.iteritems():
                    if itemId not in rowItemCountById:
                        rowItemCountById[itemId] = 0;
                    rowItemCountById[itemId] += itemCount;

            # Populate row values with counts
            for itemId in allItemIdList:
                if itemId in rowItemCountById:
                    value = rowItemCountById[itemId];
                else:
                    value = 0;
                resultRow.append(value);

            yield resultRow;
            prog.update();
        inputFile.close();
        # prog.printStatus();


    def convertResultsFileToBagOfWordsCorpus(self, inputFile, queryItems=True, verifyItems=True, outcomeItems=True, excludeCategoryIds=None):
        """Convert results file from primary prepare patient items script into a (sparse) "bag of words"
        format of 2-ples (itemId, itemCount) for each patient/row.
        Implemented as a generator over patient rows to stream through data

        queryItems: Whether to include query items in the results
        verifyItems: Whether to include verify items in the results
        incHeaders: Whether to include a header label row with result
        excludeCategoryIds: IDs of item categories that should be excluded / skipped during conversion
        """
        itemsById = DBUtil.loadTableAsDict("clinical_item");

        prog = ProgressDots();
        for inputDict in TabDictReader(inputFile):
            resultRow = list();
            observedIds = set();
            if outcomeItems:
                # Pull out labeled outcome values
                for key, value in inputDict.iteritems():
                    if key.startswith("outcome."):
                        value = int(value);
                        outcomeId = int(key[len("outcome."):]);
                        resultRow.append( (outcomeId, value) );
                        observedIds.add(outcomeId);

            totalCountById = dict();
            if queryItems:
                # Iterate through query items
                itemCountById = loadJSONDict(inputDict["queryItemCountByIdJSON"], int, int);
                for itemId, itemCount in itemCountById.iteritems():
                    if itemId not in totalCountById:
                        totalCountById[itemId] = 0;
                    totalCountById[itemId] += itemCount;
            if verifyItems:
                itemCountById = loadJSONDict(inputDict["verifyItemCountByIdJSON"], int, int);
                for itemId, itemCount in itemCountById.iteritems():
                    if itemId not in totalCountById:
                        totalCountById[itemId] = 0;
                    totalCountById[itemId] += itemCount;
            resultRow.extend( self.itemCountByIdToBagOfWords( totalCountById, observedIds, itemsById, excludeCategoryIds) );

            yield resultRow;
            prog.update();
        inputFile.close();
        # prog.printStatus();

    def itemCountByIdToBagOfWords(self, itemCountById, observedIds=None, itemsById=None, excludeCategoryIds=None ):
        """Return 2-ple (itemId, count) representation of item IDs, but filter out those in excluded set,
        or whose category looked up via itemsById is already observed previously or so far.
        """
        return TopicModel.itemCountByIdToBagOfWords(itemCountById, observedIds, itemsById, excludeCategoryIds );

    def bagOfWordsToCountById(self, bagOfWords):
        """Convert bag of words collection of 2-ple (itemId, count) representation into a dictionary of itemId: count mappings."""
        return TopicModel.bagOfWordsToCountById(bagOfWords);

    def parseOutcomeIdStr(self, outcomeIdStr, analysisQuery):
        """Parse the outcomeIdStr into a query targetItem or possible sequence of virtual items"""
        outcomeIdComponents = outcomeIdStr.split("=");
        outcomeId = int(outcomeIdComponents[0]);
        analysisQuery.baseRecQuery.targetItemIds.add(outcomeId);
        if len(outcomeIdComponents) > 1:
            sequenceIds = [int(seqIdStr) for seqIdStr in outcomeIdComponents[1].split(":")];
            analysisQuery.sequenceItemIdsByVirtualItemId[outcomeId] = tuple(sequenceIds);

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile>    Name of file with patient ids.  If not found, then interpret as comma-separated list of test Patient IDs to prepare analysis data for\n"+\
                    "   <outputFile>   Tab-delimited file summarizing key data for patient analysis\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-p", "--pastCategoryIds", dest="pastCategoryIds", help="Comma separated list of clinical item category IDs where past items should always be included in query items regardless of how long ago they occurred (e.g., patient demographics)'");
        parser.add_option("-c", "--baseCategoryId",  dest="baseCategoryId",  help="Instead of specifying first nQ query items, specify ID of clinical item category to look for initial items from (probably the ADMIT Dx item).");
        parser.add_option("-b", "--baseItemId",  dest="baseItemId",  help="Instead of specifying first nQ query items, specify ID of the specific clinical item to look for initial items from.");
        parser.add_option("-Q", "--queryTimeSpan",  dest="queryTimeSpan",  help="Time frame specified in seconds over which to look for initial query items (e.g., 24hrs = 86400) after the base item found from the category above.  Start the time counting from the first item time occuring after the category item above since the ADMIT Dx items are often keyed to dates only without times (defaulting to midnight of the date specified).");
        parser.add_option("-V", "--verifyTimeSpan",  dest="verifyTimeSpan",  help="Time frame specified in seconds over which to look for verify items after initial query item time.  Will ignore the query items that occur within the queryTimeSpan.");
        parser.add_option("-O", "--byOrderSets",  dest="byOrderSets",  action="store_true", help="If set, change interpretation of Query and Verify times. Look for usage of item collections / order sets within the specified Query time from the given base item time. Include all items up to order set usage as query items and then all items starting with that index order set item up to additional Verify time as verify items. Include the order_set_id used as a result column for later lookup. Yield multiple rows per patient, one for each order set used during the query time.");
        parser.add_option("-o", "--outcomeItemIds", dest="outcomeItemIds", help="Comma separated list of outcome item IDs of interest that may depend on the query items for prediction / recommendation.  Can specify virtual items representing the end of item triples (e.g., 5-Readmission being the end of any item followed by 3591-Discharge then 3671-Admit), by adding the component items in expected sequence.  For example, '5|3591:3671'");
        parser.add_option("-q", "--numQuery",  dest="numQuery",  help="Number of orders / items from each patient to use as query items to prime the recommendations.  If set to a float number in (0,1), then treat as a percentage of the patient's total orders / items");
        parser.add_option("-v", "--numVerify", dest="numVerify", help="Number of orders / items from each patient after the query items to use to validate recommendations.  If set to a float number in (0,1), then treat as a percentage of the patient's total orders / items.  If left unset, then just use all remaining orders / items for that patient");
        parser.add_option("-S", "--startDate",  dest="startDate",  help="Only look for test data occuring on or after this start date.");
        parser.add_option("-E", "--endDate",  dest="endDate",  help="Only look for test data occuring before this end date.");
        parser.add_option("-t", "--timeDeltaMax",  dest="timeDeltaMax",  help="Time delta in seconds to look for the occurrence of outcomes starting from the begining of the query time, which may be 0 seconds, 1 hour (3600), 1 day (86400), or 1 week (604800), etc.  Defaults to counting items occurring at ANY recorded time after query items.");
        parser.add_option("-M", "--featureMatrixConvert",  dest="featureMatrixConvert", action="store_true", help="If set, will ignore earlier parameters, and interpret inputFile as a prepared patient item result file and then output it back in a sparse 'feature matrix' format with a column for each clinical item and 0/1 for the binary presence of each item for each patient in the query OR verify item sets.");
        parser.add_option("-B", "--bagOfWordsConvert",  dest="bagOfWordsConvert", help="If set, instead interpret inputFile as a prepared patient item result file and then output it back in a sparse 'bag of words' format compatible with GenSim.  List of 2-ples (itemId, itemCount).  Given binary labels, counts will just be 0 or 1 for the presence of each item for each patient.  Include parameter characters 'q' and 'v' to specify which (or both) query and verify item sets to include. Include 'o' character to also include any outcome items.");
        parser.add_option("-X", "--excludeCategoryIds",  dest="excludeCategoryIds", help="For conversion, exclude / skip any items who fall under one of the comma-separated category Ids.  For extraction, will use default item and category exclusions regardless of this parameter.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            if options.bagOfWordsConvert is not None:
                # Convert results file into bag of words (sparse matrix) corpus format
                inputFilename = args[0];
                inputFile = stdOpen(inputFilename);

                # Format the results for output
                outputFilename = None;
                if len(args) > 1:
                    outputFilename = args[1];
                outputFile = stdOpen(outputFilename,"w");

                queryItems = ("q" in options.bagOfWordsConvert);
                verifyItems = ("v" in options.bagOfWordsConvert);
                outcomeItems = ("o" in options.bagOfWordsConvert);

                excludeCategoryIds = None;
                if options.excludeCategoryIds is not None:
                    excludeCategoryIds = set(int(idStr) for idStr in options.excludeCategoryIds.split(","));

                print >> outputFile, COMMENT_TAG, json.dumps({"argv":argv});    # Print comment line with analysis arguments to allow for deconstruction later

                # Run the actual analysis / data extraction
                rowGenerator = self.convertResultsFileToBagOfWordsCorpus(inputFile, queryItems, verifyItems, outcomeItems, excludeCategoryIds);
                for row in rowGenerator:
                    print >> outputFile, json.dumps(row);

            elif options.featureMatrixConvert:
                # Convert results file into full feature matrix format
                inputFilename = args[0];

                # Format the results for output
                outputFilename = None;
                if len(args) > 1:
                    outputFilename = args[1];
                outputFile = stdOpen(outputFilename,"w");

                print >> outputFile, COMMENT_TAG, json.dumps({"argv":argv});    # Print comment line with analysis arguments to allow for deconstruction later

                # Run the actual analysis / data extraction
                rowGenerator = self.convertResultsFileToFeatureMatrix(inputFilename);

                formatter = TextResultsFormatter( outputFile );
                formatter.formatResultSet( rowGenerator );

            else:   # Default item preparation from database

                # Parse out the query parameters
                query = AnalysisQuery();
                query.recommender = ItemAssociationRecommender();
                query.baseRecQuery = RecommenderQuery();
                query.baseRecQuery.excludeCategoryIds = query.recommender.defaultExcludedClinicalItemCategoryIds();
                query.baseRecQuery.excludeItemIds = query.recommender.defaultExcludedClinicalItemIds();

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
                    query.queryTimeSpan = timedelta(0,int(options.queryTimeSpan));
                    query.verifyTimeSpan = timedelta(0,int(options.verifyTimeSpan));

                query.byOrderSets = options.byOrderSets;

                if options.pastCategoryIds:
                    query.pastCategoryIds = options.pastCategoryIds.split(",");
                    for i, categoryIdStr in enumerate(query.pastCategoryIds):
                        query.pastCategoryIds[i] = int(categoryIdStr);

                # Option to specify query time span starting from a key category or item
                if options.baseCategoryId is not None or options.baseItemId is not None:
                    if options.baseCategoryId is not None:
                        query.baseCategoryId = int(options.baseCategoryId);  # Category to look for clinical item to start accruing query items from
                    if options.baseItemId is not None:
                        query.baseItemId = int(options.baseItemId);

                if options.startDate is not None:
                    query.startDate = DBUtil.parseDateValue(options.startDate);
                if options.endDate is not None:
                    query.endDate = DBUtil.parseDateValue(options.endDate);

                # Identify particular outcome items of interest
                if options.outcomeItemIds is not None:
                    outcomeIdStrList = options.outcomeItemIds.split(",");
                    for outcomeIdStr in outcomeIdStrList:
                        self.parseOutcomeIdStr(outcomeIdStr, query);

                # Track limits on when to count outcomes as being present
                if options.timeDeltaMax is not None:
                    query.baseRecQuery.timeDeltaMax = timedelta(0,int(options.timeDeltaMax));

                # Run the actual analysis / data extraction
                resultsGenerator = self(query);

                # Format the results for output
                outputFilename = None;
                if len(args) > 1:
                    outputFilename = args[1];
                outputFile = stdOpen(outputFilename,"w");

                print >> outputFile, COMMENT_TAG, json.dumps({"argv":argv});    # Print comment line with analysis arguments to allow for deconstruction later

                formatter = TextResultsFormatter( outputFile );

                colNames = self.resultHeaders(query);
                formatter.formatTuple( colNames );    # Insert a mock record to get a header / label row
                formatter.formatResultDicts( resultsGenerator, colNames );

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);


class ItemsByCountExtractor:
    """Given a patient's list of clinical item events (patient items),
    summarize them into separate query and verify sets based simply on pre-specific counts for each set size.
    """

    def __call__(self, analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, preparer):
        patientItemData = {"patient_id": patientId };

        # Get items by specified counts
        queryItemCountById = dict();
        verifyItemCountById = dict();

        # Build up counts separately to account for redundant items / orders
        numQueryItems = 0;
        numVerifyItems = 0;

        for (i, patientItem) in enumerate(patientItemList):
            if analysisQuery.pastCategoryIds and patientItem["clinical_item_category_id"] in analysisQuery.pastCategoryIds:
                # If designated past category (e.g., demographics), include regardless of past timing
                if patientItem["clinical_item_id"] not in queryItemCountById:
                    queryItemCountById[patientItem["clinical_item_id"]] = 0;
                queryItemCountById[patientItem["clinical_item_id"]] += 1;

            # Skip any items prior to base item if specified
            if "baseItemId" not in patientItemData and (analysisQuery.baseCategoryId is not None or analysisQuery.baseItemId is not None):
                if patientItem["clinical_item_category_id"] == analysisQuery.baseCategoryId or patientItem["clinical_item_id"] == analysisQuery.baseItemId:
                    patientItemData["baseItemId"] = patientItem["clinical_item_id"];
                else:
                    continue;   # Skip this item that is before the base item

            isAnalyzable = (patientItem["analysis_status"] != 0);

            clinicalItemId = patientItem["clinical_item_id"];
            if numQueryItems < analysisQuery.numQueryItems and clinicalItemId not in queryItemCountById and isAnalyzable:
                # Accumulate items until reach desired query count
                if clinicalItemId not in queryItemCountById:
                    queryItemCountById[clinicalItemId] = 0;
                queryItemCountById[clinicalItemId] += 1;
                numQueryItems += 1;
            elif numVerifyItems < analysisQuery.numVerifyItems and \
                clinicalItemId not in verifyItemCountById and \
                isAnalyzable and \
                preparer.isItemRecommendable(clinicalItemId, queryItemCountById, recQuery, categoryIdByItemId):
                # Once accumulated query items, now look for verification items
                #   Exclude any that already appeared in query set, since would not be recommending repeats
                if clinicalItemId not in verifyItemCountById:
                    verifyItemCountById[clinicalItemId] = 0;
                verifyItemCountById[clinicalItemId] += 1;
                numVerifyItems += 1;

        patientItemData["queryItemCountById"] = queryItemCountById;
        patientItemData["verifyItemCountById"] = verifyItemCountById;

        yield patientItemData;  # Generator to return a single result

class ItemsByBaseItemExtractor:
    """Given a patient's list of clinical item events (patient items),
    summarize them into separate query and verify sets based on time spans
    relative to a base time indicated by the presence of a base item (usually admission diagnosis).
    Note that the base item itself may not have the base time, since diagnoses may be recorded at date level precision,
    but we want the first item that occurs that day at a specific time, representing the initiation of the
    actual medical encounter.
    """

    def __call__(self, analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, preparer):
        patientItemData = {"patient_id": patientId };

        # First pass through old items until find base/index item
        self.identifyBaseItem(analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, preparer, patientItemData);

        baseItemId = patientItemData["baseItemId"];  # Item ID of base item found
        baseItemDate = patientItemData["baseItemDate"];    # Date to start accumulating queries based on first baseItemId or baseCategoryId recognized item
        queryStartTime = patientItemData["queryStartTime"];   # Date to start counting queryTimeSpan.  Will NOT be the same as baseItemDate, because actual timed orders tend to have specific times recorded AFTER the base category data's general date (but not time) recording
        queryEndTime = patientItemData["queryEndTime"];    # Date to stop counting queryTimeSpan = queryStartTime + queryTimeSpan
        verifyEndTime = patientItemData["verifyEndTime"];   # Date to stop counting items for verify set
        outcomeEndTime = patientItemData["outcomeEndTime"];  # Latest date for an outcome item to be present and count as existing for the prediction

        queryItemCountById = {};
        verifyItemCountById = {};

        if queryEndTime is None:
            # Means was not able to find usuable items.  Skip this record;
            log.warning("Unable to find adequate patient items for patient: %s" % patientId );
        else:
            # Track whether the target outcome IDs exist for the patient
            existsByOutcomeId = dict();
            for outcomeId in recQuery.targetItemIds:
                existsByOutcomeId[outcomeId] = OUTCOME_ABSENT;   # Default to not found

            # Option to track sequences of multiple items as a single virtual target item
            midSequenceItemDatesByItemId = dict();
            for virtualItemId, sequenceIds in analysisQuery.sequenceItemIdsByVirtualItemId.iteritems():
                midSequenceId = sequenceIds[0];
                for patientItem in patientItemList:
                    if patientItem["clinical_item_id"] == midSequenceId:
                        if midSequenceId not in midSequenceItemDatesByItemId:
                            midSequenceItemDatesByItemId[midSequenceId] = set();
                        midSequenceItemDatesByItemId[midSequenceId].add(patientItem["item_date"]);
                existsByOutcomeId[virtualItemId] = OUTCOME_ABSENT;  # Default to not found

            for (i, patientItem) in enumerate(patientItemList):
                itemId = patientItem["clinical_item_id"];
                isOutcomeItem = (itemId in recQuery.targetItemIds);
                isAnalyzable = (patientItem["analysis_status"] != 0);
                inQueryTimeSpan = False;
                inVerifyTimeSpan = False;
                inOutcomeTimeSpan = False;

                # Determine if this represents a virtual outcome item
                virtualOutcomeId = None;
                for virtualItemId, sequenceIds in analysisQuery.sequenceItemIdsByVirtualItemId.iteritems():
                    midSequenceId = sequenceIds[0];
                    endSequenceId = sequenceIds[-1];
                    isVirtualOutcome = itemId == endSequenceId;
                    isVirtualOutcome = isVirtualOutcome and midSequenceId in midSequenceItemDatesByItemId;
                    if isVirtualOutcome:
                        foundSequence = False;
                        for midSeqDate in midSequenceItemDatesByItemId[midSequenceId]:
                            if queryStartTime <= midSeqDate and midSeqDate <= patientItem["item_date"]:
                                foundSequence = True;
                                break;
                        isVirtualOutcome = isVirtualOutcome and foundSequence;
                    if isVirtualOutcome:
                        virtualOutcomeId = virtualItemId;

                itemDate = patientItem["item_date"];

                if itemDate < baseItemDate and analysisQuery.pastCategoryIds and patientItem["clinical_item_category_id"] in analysisQuery.pastCategoryIds:
                    # If designated past category (e.g., demographics), include regardless of *past* timing
                    if itemId not in queryItemCountById:
                        queryItemCountById[itemId] = 0;
                    queryItemCountById[itemId] += 1;

                if itemDate >= baseItemDate:    # Means base item will be included in query, not just subsequent query time
                    inQueryTimeSpan = (itemDate < queryEndTime);
                    inVerifyTimeSpan = (verifyEndTime is not None and itemDate >= queryEndTime and itemDate < verifyEndTime);
                    inOutcomeTimeSpan = (outcomeEndTime is None or itemDate < outcomeEndTime);

                # Item within acceptable time frame, can use as query item
                if inQueryTimeSpan and isAnalyzable:
                    if itemId not in queryItemCountById:
                        queryItemCountById[itemId] = 0;
                    queryItemCountById[itemId] += 1;

                # Item within time frame, see if usable as verify item
                if inVerifyTimeSpan and preparer.isItemRecommendable(itemId, queryItemCountById, recQuery, categoryIdByItemId):
                    if itemId not in verifyItemCountById:
                        verifyItemCountById[itemId] = 0;
                    verifyItemCountById[itemId] += 1;

                # Outcome items label depending on whether found and within or outside query period
                if isOutcomeItem:
                    if inQueryTimeSpan:
                        existsByOutcomeId[itemId] = OUTCOME_IN_QUERY;

                    if inOutcomeTimeSpan and (existsByOutcomeId[itemId] == OUTCOME_ABSENT):
                        # Found a target outcome and not yet labeled as present or within a query
                        existsByOutcomeId[itemId] = OUTCOME_PRESENT;

                # Virtual outcome result with similar checks
                if virtualOutcomeId is not None:
                    if inQueryTimeSpan:
                        existsByOutcomeId[virtualOutcomeId] = OUTCOME_IN_QUERY;

                    if inOutcomeTimeSpan and (existsByOutcomeId[virtualOutcomeId] == OUTCOME_ABSENT):
                        # Found a target outcome and not yet labeled as present or within a query
                        existsByOutcomeId[virtualOutcomeId] = OUTCOME_PRESENT;

            patientItemData["queryItemCountById"] = queryItemCountById;
            patientItemData["verifyItemCountById"] = verifyItemCountById;
            patientItemData["existsByOutcomeId"] = existsByOutcomeId;

        yield patientItemData; # Generator to return a single result


    def identifyBaseItem(self, analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, preparer, patientItemData):
        # Look for the first item to trigger the base category
        baseItemId = None;  # Item ID of base item found
        baseItemDate = None;    # Date to start accumulating queries based on first baseItemId or baseCategoryId recognized item
        queryStartTime = None;   # Date to start counting queryTimeSpan.  Will NOT be the same as baseItemDate, because actual timed orders tend to have specific times recorded AFTER the base category data's general date (but not time) recording
        queryEndTime = None;    # Date to stop counting queryEndTime = queryStartTime + queryTimeSpan
        verifyEndTime = None;   # Date to stop counting items for verify set
        outcomeEndTime = None;  # Latest date for an outcome item to be present and count as existing for the prediction

        # Front scan through old items until find base/index item
        for patientItem in patientItemList:
            if baseItemDate is None:
                # Still looking for base item
                if patientItem["clinical_item_category_id"] == analysisQuery.baseCategoryId or patientItem["clinical_item_id"] == analysisQuery.baseItemId:
                    baseItemId = patientItem["clinical_item_id"];
                    baseItemDate = patientItem["item_date"];
            elif queryStartTime is None:
                # Found the base item by category, find the next item to figure out the proper query time frame.
                #   Note that admit diagnosis category generally recorded with date level resolution vs. orders
                #   recorded with time resolution.  Means Admit Dx will look like it occurs at midnight, even though
                #   orders may not show up until 5pm.  If looking for "first 4 hours" of orders then,
                #   will only # look from midnight-4am and find nothing.  So look for the NEXT item to define the admission start time.
                # Exception if next item >=1 day away, suggesting that items themselves are recorded with day level precision instead of time.
                if patientItem["item_date"] != baseItemDate:
                    if (patientItem["item_date"] - baseItemDate) < MAX_BASE_ITEM_TIME_RESOLUTION:
                        queryStartTime = patientItem["item_date"];
                    else:
                        queryStartTime = baseItemDate;
                    queryEndTime = queryStartTime + analysisQuery.queryTimeSpan;
                    if analysisQuery.verifyTimeSpan is not None:
                        verifyEndTime = queryStartTime + analysisQuery.verifyTimeSpan;
                    if recQuery.timeDeltaMax is not None:
                        outcomeEndTime = queryStartTime + recQuery.timeDeltaMax;
            else:
                # Have the base information, no need to look further for now
                break;

        patientItemData["baseItemId" ] = baseItemId;
        patientItemData["baseItemDate"] = baseItemDate;
        patientItemData["queryStartTime"] = queryStartTime;
        patientItemData["queryEndTime"] = queryEndTime;
        patientItemData["verifyEndTime"] = verifyEndTime;
        patientItemData["outcomeEndTime"] = outcomeEndTime;

class ItemsByOrderSetExtractor(ItemsByBaseItemExtractor):
    """Given a patient's list of clinical item events (patient items),
    search for orders that derived from clinical order sets.
    For each order set used within the specified query time relative to a base item (typically admission diagnosis).
    Generate a result for each unique order set usage with query items from the base time up to the order set,
    with a matching verify set of orders actually used (including ones coming from the order set) within
    the additional verify time specified.
    """
    def __call__(self, analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, preparer):
        patientItemData = {"patient_id": patientId };

        # First pass through old items until find base/index item
        self.identifyBaseItem(analysisQuery, recQuery, patientId, patientItemList, categoryIdByItemId, preparer, patientItemData);

        baseItemId = patientItemData["baseItemId"];  # Item ID of base item found
        baseItemDate = patientItemData["baseItemDate"];    # Date to start accumulating queries based on first baseItemId or baseCategoryId recognized item
        searchStartTime = patientItemData["queryStartTime"];   # Date to start looking for order sets.  Will NOT be the same as baseItemDate, because actual timed orders tend to have specific times recorded AFTER the base category data's general date (but not time) recording
        searchEndTime = patientItemData["queryEndTime"];    # Date to stop looking for order sets,  searchEndTime = queryStartTime + queryTimeSpan. Note this will be CHANGING the definition of queryEndTime which will depend on the timing order sets appearing

        if searchEndTime is None:
            # Means was not able to find usuable items.  Skip this record;
            log.warning("Unable to find adequate patient items for patient: %s" % patientId );
        else:
            # Assumes items are pre-sorted by item date
            # Another pass to pull out the order set index items (first item for each order set used)
            #   that occurs within the search timeframe
            foundOrderSetIds = set();   # Don't use a dictionary to items here, because want to retain chronological sort
            firstOrderSetItems = list();
            for (i, patientItem) in enumerate(patientItemList):
                if "order_set_id" in patientItem and patientItem["order_set_id"] is not None:
                    orderSetId = patientItem["order_set_id"];
                    itemDate = patientItem["item_date"];
                    if itemDate >= searchStartTime and itemDate < searchEndTime and orderSetId not in foundOrderSetIds:
                        # First item in an order set not encountered before, occuring within the search time of interest
                        foundOrderSetIds.add(orderSetId);
                        firstOrderSetItems.append(patientItem);

            # Now do pass throughs to yield a query / verify item set based on each order set index time
            for firstOrderSetItem in firstOrderSetItems:
                orderSetId = firstOrderSetItem["order_set_id"];
                queryStartTime = searchStartTime;   # Date to start counting queryTimeSpan.
                queryEndTime = firstOrderSetItem["item_date"];    # Date to stop counting (up to the use of the order set)
                verifyEndTime = firstOrderSetItem["item_date"]+analysisQuery.verifyTimeSpan;   # Date to stop counting items for verify set

                # Store parameters for output results
                patientItemData["queryStartTime"] = queryStartTime;
                patientItemData["queryEndTime"] = queryEndTime;
                patientItemData["verifyEndTime"] = verifyEndTime;
                patientItemData["order_set_id"] = orderSetId;

                queryItemCountById = {};
                verifyItemCountById = {};

                for (i, patientItem) in enumerate(patientItemList):
                    itemId = patientItem["clinical_item_id"];
                    isAnalyzable = (patientItem["analysis_status"] != 0);
                    inQueryTimeSpan = False;
                    inVerifyTimeSpan = False;

                    itemDate = patientItem["item_date"];
                    if itemDate >= baseItemDate:    # Means base item will be included in query, not just subsequent query time
                        inQueryTimeSpan = (itemDate < queryEndTime);
                        inVerifyTimeSpan = (itemDate >= queryEndTime and itemDate < verifyEndTime);

                    # Item within acceptable time frame, can use as query item
                    if inQueryTimeSpan and isAnalyzable:
                        if itemId not in queryItemCountById:
                            queryItemCountById[itemId] = 0;
                        queryItemCountById[itemId] += 1;

                    # Item within time frame, see if usable as verify item
                    if inVerifyTimeSpan and preparer.isItemRecommendable(itemId, queryItemCountById, recQuery, categoryIdByItemId):
                        if itemId not in verifyItemCountById:
                            verifyItemCountById[itemId] = 0;
                        verifyItemCountById[itemId] += 1;

                patientItemData["queryItemCountById"] = queryItemCountById;
                patientItemData["verifyItemCountById"] = verifyItemCountById;

                yield patientItemData;

if __name__ == "__main__":
    instance = PreparePatientItems();
    instance.main(sys.argv);
