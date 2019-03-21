#!/usr/bin/env python
import sys, os
import time;
import math;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;

from Util import log;
from Env import DATE_FORMAT;

from Const import SENTINEL_RESULT_VALUE, Z_SCORE_LIMIT;
from Const import FLAG_IN_RANGE, FLAG_HIGH, FLAG_LOW, FLAG_RESULT, FLAG_ABNORMAL;

SOURCE_TABLE = "stride_order_results";

class STRIDEOrderResultsConversion:
    """Data conversion module to take STRIDE provided (lab) results data
    into the structured data tables to facilitate subsequent analysis.

    Renormalizes denormalized data back out to order types (clinical_item_category),
    orders (clinical_item), and actual individual (lab) results (patient_item).

    Separate out lab results by result_flag (High, Low, Abnormal, etc.). If no such flags available
    for this result, then just record as a generic "Result" event.
    """
    connFactory = None; # Allow specification of alternative DB connection source

    categoryBySourceDescr = None;   # Local cache to track the clinical item category table contents
    clinicalItemByCategoryIdExtId = None;   # Local cache to track clinical item table contents

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

        self.categoryBySourceDescr = dict();
        self.clinicalItemByCategoryIdExtId = dict();
        self.resultStatsByBaseName = None;

    def convertSourceItems(self, startDate=None, endDate=None):
        """Primary run function to process the contents of the stride_order_proc
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies to avoid repeating conversion.

        startDate - If provided, only return items whose ordering_date is on or after that date.
        endDate - If provided, only return items whose ordering_date is before that date.
        """
        log.info("Conversion for items dated %s to %s" % (startDate, endDate));
        progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            for sourceItem in self.querySourceItems(startDate, endDate, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn);
                progress.Update();
        finally:
            conn.close();
        progress.PrintStatus();


    def querySourceItems(self, startDate=None, endDate=None, progress=None, conn=None):
        """Query the database for list of all source clinical items (lab results in this case)
        and yield the results one at a time.  If startDate provided, only return items
        whose result_time is on or after that date.
        Only include results records where the result_flag is set to an informative value,
        to focus only on abnormal lab results (including would be a ton more relatively uninformative
        data that would greatly expend data space and subsequent computation time)
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        headers = ["sor.order_proc_id", "pat_id", "pat_enc_csn_id", "order_type", "proc_id", "proc_code", "base_name", "component_name", "common_name", "ord_num_value", "result_flag", "result_in_range_yn", "sor.result_time"];

        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom("stride_order_proc as sop");
        query.addFrom("%s as sor" % SOURCE_TABLE);
        query.addWhere("sop.order_proc_id = sor.order_proc_id");
        #query.addWhere("result_flag <> '*'");   # Will exclude nulls and the uninformative '*' values for text-based microbiology results
        if startDate is not None:
            query.addWhereOp("sor.result_time",">=", startDate);
        if endDate is not None:
            query.addWhereOp("sor.result_time","<", endDate);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            # Normalize qualified labels
            rowModel["order_proc_id"] = rowModel["sor.order_proc_id"];
            rowModel["result_time"] = rowModel["sor.result_time"];

            if rowModel['base_name'] is None:
                row = cursor.fetchone()
                continue

            self.populateResultFlag(rowModel,conn=conn);

            yield rowModel; # Yield one row worth of data at a time to avoid having to keep the whole result set in memory
            row = cursor.fetchone();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();


    def populateResultFlag(self, resultModel, conn=None):
        """If order result row model has no pre-specified result_flag, then assign one
        based on distribution of known results for this item type, or just a default "Result" flag.
        """
        if resultModel["result_flag"] is not None: # Only proceed if flag is currently null / blank
            return;
        elif resultModel["result_in_range_yn"] is not None:    # Alternative specification of normal / abnormal
            if resultModel["result_in_range_yn"] == "Y":
                resultModel["result_flag"] = FLAG_IN_RANGE;
            else: #resultModel["result_in_range_yn"] == "N":
                resultModel["result_flag"] = FLAG_ABNORMAL;
            return;
        elif resultModel["ord_num_value"] is None or resultModel["ord_num_value"] == SENTINEL_RESULT_VALUE:
            # No specific result flag or (numerical) value provided. Just record that some result was generated at all
            resultModel["result_flag"] = FLAG_RESULT;
            return;
        elif resultModel['base_name'] is None:
            # With 2014-2017 data, there are fields with a null base_name.
            # We can't build summary stats around this case, so just return
            # FLAG_RESULT.
            resultModel['result_flag'] = FLAG_RESULT
            return
        #else: # General case, no immediately available result flags

        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        if self.resultStatsByBaseName is None:
            # Ensure result stats cache is preloaded
            dataTable = DBUtil.execute("select * from order_result_stat", includeColumnNames=True, conn=conn);
            dataModels = modelListFromTable(dataTable);
            self.resultStatsByBaseName = modelDictFromList(dataModels, "base_name");

        if resultModel["base_name"] not in self.resultStatsByBaseName:
            # Result stats not already in cache.  Query from DB and store in cache for future use.
            statModel = self.calculateResultStats( resultModel["base_name"], conn=conn );

            # Store results back in cache to facilitate future lookups
            self.resultStatsByBaseName[resultModel["base_name"]] = statModel;
            DBUtil.insertRow("order_result_stat", statModel, conn=conn );
        statModel = self.resultStatsByBaseName[resultModel["base_name"]];

        if statModel["max_result_flag"] is not None or statModel["max_result_in_range"] is not None:
            # Alternative result flagging methods exist.  We should just use those and treat this as a normal "in range" result
            resultModel["result_flag"] = FLAG_IN_RANGE;
        else:
            # No values in the entire database for this item have a result flag.  Let's see if we can estimate ranges based on numerical values
            if statModel["value_count"] > 0:    # Found some values to calculate summary stats
                try:
                    mean = statModel["value_sum"] / statModel["value_count"];
                    # Std Dev = sqrt( E[x^2] - E[x]^2 )
                    var = (statModel["value_sum_squares"]/statModel["value_count"]) - (mean*mean);
                    stdev = math.sqrt(var);
                    zScore = 0;
                    if stdev > 0:
                        zScore = (resultModel["ord_num_value"] - mean)/stdev

                    if zScore < -Z_SCORE_LIMIT:
                        resultModel["result_flag"] = FLAG_LOW;
                    elif zScore> Z_SCORE_LIMIT:
                        resultModel["result_flag"] = FLAG_HIGH;
                    else:   # |zScore| < Z_SCORE_LIMIT
                        resultModel["result_flag"] = FLAG_IN_RANGE;
                except ValueError, exc:
                    # Math error, probably stdev = 0 or variance < 0, just treat as an unspecified result
                    resultModel["result_flag"] = FLAG_RESULT;
            else:   # No value distribution, just record as a non-specific result
                resultModel["result_flag"] = FLAG_RESULT;

        if not extConn:
            conn.close();

    def calculateResultStats(self, baseName, conn):
        """Query the database for lab results by the given baseName
        to calculate several summary statistics.
        """
        query = SQLQuery();
        query.addSelect("count(ord_num_value) as value_count");
        query.addSelect("sum(ord_num_value) as value_sum");
        query.addSelect("sum(ord_num_value*ord_num_value) as value_sum_squares");
        query.addSelect("max(result_flag) as max_result_flag");
        query.addSelect("max(result_in_range_yn) as max_result_in_range");
        query.addFrom("stride_order_results");
        query.addWhereOp("ord_num_value","<>", SENTINEL_RESULT_VALUE );
        query.addWhereEqual("base_name", baseName )

        dataTable = DBUtil.execute(query, includeColumnNames=True, conn=conn)
        dataModels = modelListFromTable(dataTable);
        statModel = dataModels[0];   # Assume that exactly 1 row item will exist
        statModel["base_name"] = baseName;

        return statModel;

    def convertSourceItem(self, sourceItem, conn=None):
        """Given an individual sourceItem record, produce / convert it into an equivalent
        item record in the analysis database.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        try:
            # Normalize sourceItem data into hierachical components (category -> clinical_item -> patient_item).
            #   Relatively small / finite number of categories and clinical_items, so these should only have to be instantiated
            #   in a first past, with subsequent calls just yielding back in memory cached copies
            categoryModel = self.categoryFromSourceItem(sourceItem, conn=conn);
            clinicalItemModel = self.clinicalItemFromSourceItem(sourceItem, categoryModel, conn=conn);
            patientItemModel = self.patientItemModelFromSourceItem(sourceItem, clinicalItemModel, conn=conn);

        finally:
            if not extConn:
                conn.close();


    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        categoryKey = (SOURCE_TABLE, sourceItem["order_type"]);
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = \
                RowItemModel \
                (   {   "source_table":  SOURCE_TABLE,
                        "description":  "%s Result" % sourceItem["order_type"],
                    }
                );
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn);
            category["clinical_item_category_id"] = categoryId;
            self.categoryBySourceDescr[categoryKey] = category;
        return self.categoryBySourceDescr[categoryKey];

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        # Make unique by lab component name, not by proc_id / panel, since interested in result, not which panel it came from
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["base_name"], sourceItem["result_flag"]);
        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            sourceItem["result_flag_nospace"] = sourceItem["result_flag"].replace(' ','');
            clinicalItem = \
                RowItemModel \
                (   {   "clinical_item_category_id": category["clinical_item_category_id"],
                        "external_id": None, # sourceItem["proc_id"], exclude proc_id which maps to lab panels that may not be of interesting difference, when is really result of interest
                        "name": "%(base_name)s(%(result_flag_nospace)s)" % sourceItem,
                        "description": "%(common_name)s (%(result_flag)s)" % sourceItem,
                    }
                );
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn);
            clinicalItem["clinical_item_id"] = clinicalItemId;
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem;
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey];

    def patientItemModelFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id":  sourceItem["order_proc_id"],
                    "patient_id":  sourceItem["pat_id"],
                    "encounter_id":  sourceItem["pat_enc_csn_id"],
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["result_time"],
                    "num_value": sourceItem["ord_num_value"],
                }
            );
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys() );
        insertParams= patientItem.values();
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute( insertQuery, insertParams, conn=conn );
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
            log.info(err);


    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options]\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time on or after this date.");
        parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time before this date.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        startDate = None;
        if options.startDate is not None:
            # Parse out the start date parameter
            timeTuple = time.strptime(options.startDate, DATE_FORMAT);
            startDate = datetime(*timeTuple[0:3]);
        endDate = None;
        if options.endDate is not None:
            # Parse out the start date parameter
            timeTuple = time.strptime(options.endDate, DATE_FORMAT);
            endDate = datetime(*timeTuple[0:3]);
        self.convertSourceItems(startDate,endDate);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = STRIDEOrderResultsConversion();
    instance.main(sys.argv);
