#!/usr/bin/env python

import sys, os
import time
from datetime import datetime
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList

from medinfo.dataconversion.Util import log
from medinfo.dataconversion.Const import COLLECTION_TYPE_ORDERSET
from medinfo.dataconversion.Env import DATE_FORMAT

from medinfo.db.bigquery import bigQueryUtil
from medinfo.dataconversion.starr_conv import STARRUtil

from google.cloud import bigquery

SOURCE_TABLE = "starr_datalake2018.order_proc"
ORDERSET_TABLE = "starr_datalake2018.proc_orderset"


class STARROrderProcConversion:
    """Data conversion module to take STRIDE provided computerized physician order entry data
    into the structured data analysis tables to facilitate subsequent analysis.

    Renormalizes denormalized data back out to order types (clinical_item_category),
    orders (clinical_item), and actual individual patient orders (patient_item).
    Ignores records with instantiated_time not null, so will only be interested
    in originally ordered parent orders, not spawned child orders.

    Consider Ignore PRN orders for now to simplify data set and focus on standing orders
        (but a small minority for these orders anyway)

    Beware of usage of this module and how it accounts for new unique clinical_items (probably applies to all the conversion scripts)
    # This should be what determines a new unique clinical_item. 
    #   Some debate about whether to distinguish by proc_id or proc_code, but there are many labs and other procs 
    #   that use different proc_ids even though they are obviously the same. Go link in STRIDE_ORDER_PROC for examples like LABA1C.
    # The self.clinicalItemByCategoryIdExtId is supposed to keep track of which clinical_items we're already aware of, 
    #   but not that it starts blank when this module runs. 
    #   So you in theory should only run this conversion process on a database once 
    #   (otherwise it will not be aware that a bunch of duplicate clinical_items already exist in the database). 
    #   Alternatively, this module should be updated, so that it initializes this key tracker with whatever is already in the database.
    """
    def __init__(self):
        """Default constructor"""
        self.bqConn = bigQueryUtil.connection()
        self.bqClient = bigQueryUtil.BigQueryClient()
        self.connFactory = DBUtil.ConnectionFactory()           # Default connection source, but Allow specification of alternative DB connection source

        self.categoryBySourceDescr = dict()                     # Local cache to track the clinical item category table contents
        self.clinicalItemByCategoryIdExtId = dict()             # Local cache to track clinical item table contents
        self.itemCollectionByKeyStr = dict()                    # Local cache to track item collections
        self.itemCollectionItemByCollectionIdItemId = dict()    # Local cache to track item collection items

    def convertAndUpload(self, startDate=None, endDate=None, tempDir='/tmp/', removeCsvs=True, target_dataset_id='starr_datalake2018'):
        """
        Wrapper around primary run function, does conversion locally and uploads to BQ
        No batching done for treatment team since converted table is small
        """
        starrUtil = STARRUtil.StarrCommonUtils(self.bqClient)
        self.convertSourceItems(startDate, endDate)

        batchCounter = 99999    # TODO (nodir) why not 0?
        self.bqClient.reconnect_client()  # refresh bq client connection
        starrUtil.dumpPatientItemCollectionLinkToCsv(tempDir, batchCounter)
        starrUtil.uploadPatientItemCollectionLinkCsvToBQ(tempDir, target_dataset_id, batchCounter)
        if removeCsvs:
            starrUtil.removePatientItemCollectionLinkCsv(tempDir, batchCounter)
        starrUtil.removePatientItemCollectionLinkAddedLines()

        # For now keep the clinical_* tables, upload them them once all tables have been converted
        starrUtil.dumpItemCollectionTablesToCsv(tempDir)
        starrUtil.uploadItemCollectionTablesCsvToBQ(tempDir, target_dataset_id)
        if removeCsvs:
            starrUtil.removeItemCollectionTablesCsv(tempDir)
        starrUtil.removeItemCollectionTablesAddedLines()

        starrUtil.dumpPatientItemToCsv(tempDir, batchCounter)
        starrUtil.uploadPatientItemCsvToBQ(tempDir, target_dataset_id, batchCounter)
        if removeCsvs:
            starrUtil.removePatientItemCsv(tempDir, batchCounter)
        starrUtil.removePatientItemAddedLines(SOURCE_TABLE)

        # For now keep the clinical_* tables, upload them them once all tables have been converted
        starrUtil.dumpClinicalTablesToCsv(tempDir)
        starrUtil.uploadClinicalTablesCsvToBQ(tempDir, target_dataset_id)
        if removeCsvs:
            starrUtil.removeClinicalTablesCsv(tempDir)
        starrUtil.removeClinicalTablesAddedLines(SOURCE_TABLE)

    def convertSourceItems(self, startDate=None, endDate=None):
        """Primary run function to process the contents of the stride_order_proc
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies to avoid repeating conversion.

        startDate - If provided, only return items whose ordering_date is on or after that date.
        endDate - If provided, only return items whose ordering_date is before that date.
        """
        log.info("Conversion for items dated {} to {}".format(startDate, endDate))
        progress = ProgressDots()
        conn = self.connFactory.connection()
        try:
            for sourceItem in self.querySourceItems(startDate, endDate, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn)
                progress.Update()
        finally:
            conn.close()
        progress.PrintStatus()

    def querySourceItems(self, startDate=None, endDate=None, progress=None, conn=None):
        """Query the database for list of all source clinical items (orders, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose order_time is on or after that date.
        Ignore entries with instantiated_time not null, as those represent child orders spawned from an original order,
        whereas we are more interested in the decision making to enter the original order.
        """
        extConn = conn is not None
        if not extConn:
            conn = self.connFactory.connection()

        # Column headers to query for that map to respective fields in analysis table
        queryHeaders = ["op.order_proc_id_coded", "jc_uid", "op.pat_enc_csn_id_coded", "op.order_type", "op.proc_id",
                        "op.proc_code", "description", "order_time_jittered", "ordering_mode", "protocol_id",
                        "protocol_name", "ss_section_id", "ss_section_name", "ss_sg_key", "ss_sg_name"]
        headers = ["order_proc_id_coded", "jc_uid", "pat_enc_csn_id_coded", "order_type", "proc_id",
                   "proc_code", "description", "order_time_jittered", "ordering_mode", "protocol_id",
                   "protocol_name", "ss_section_id", "ss_section_name", "ss_sg_key", "ss_sg_name"]

        # TODO original query - need to figure out how to pass date to query in BQ using SQLQuery object
        # query = SQLQuery()
        # for header in queryHeaders:
        #     query.addSelect(header)
        # query.addFrom("stride_order_proc as op left outer join stride_orderset_order_proc as os on op.order_proc_id = os.order_proc_id")
        # query.addWhere("order_time is not null")    # Rare cases of "comment" orders with no date/time associated
        # query.addWhere("instantiated_time is null")
        # query.addWhere("(stand_interval is null or stand_interval not like '%%PRN')")   # Ignore PRN orders to simplify somewhat
        # if startDate is not None:
        #     query.addWhereOp("order_time", ">=", startDate)
        # if endDate is not None:
        #     query.addWhereOp("order_time", "<", endDate)

        query = "SELECT {} FROM {} as op left outer join {} as os on op.order_proc_id_coded = os.order_proc_id_coded" \
            .format(', '.join(queryHeaders), SOURCE_TABLE, ORDERSET_TABLE)

        query += " where order_time_jittered is not null"    # Rare cases of "comment" orders with no date/time associated
        query += " and (stand_interval is NULL or stand_interval not like '%PRN')"    # Ignore PRN orders to simplify somewhat
        if startDate is not None:
            query += " and order_time_jittered >= @startDate"
        if endDate is not None:
            query += " and order_time_jittered < @endDate"
        # query += " order by op.order_proc_id_coded, jc_uid, op.pat_enc_csn_id_coded, op.proc_id"
        query += ';'

        query_params = [
            bigquery.ScalarQueryParameter(
                'startDate',
                'DATETIME',
                startDate,
            ),
            bigquery.ScalarQueryParameter(
                'endDate',
                'DATETIME',
                endDate,
            )
        ]

        # TODO Query to get an estimate of how long the process will be
        # if progress is not None:
        #     progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0]

        query_job = self.bqClient.queryBQ(query, query_params=query_params, verbose=True)

        for row in query_job:  # API request - fetches results
            rowModel = RowItemModel(row.values(), headers)
            log.debug("rowModel: {}".format(rowModel))
            yield rowModel  # Yield one row worth of data at a time to avoid having to keep the whole result set in memory

        if not extConn:
            conn.close()

    def convertSourceItem(self, sourceItem, conn=None):
        """Given an individual sourceItem record, produce / convert it into an equivalent
        item record in the analysis database.
        """
        extConn = conn is not None
        if not extConn:
            conn = self.connFactory.connection()
        try:
            if sourceItem["proc_code"] is None:
                # Some 10000 rows don't have proc_code given, so the clinical_item can't be created out of them.
                # We could use description column, but the same description can have multiple proc_codes,
                # so we'll just ignore those records.
                return

            # Normalize sourceItem data into hierarchical components (category -> clinical_item -> patient_item).
            #   Relatively small / finite number of categories and clinical_items, so these should only have to be instantiated
            #   in a first past, with subsequent calls just yielding back in memory cached copies
            category = self.categoryFromSourceItem(sourceItem, conn=conn)
            clinicalItem = self.clinicalItemFromSourceItem(sourceItem, category, conn=conn)
            patientItem = self.patientItemFromSourceItem(sourceItem, clinicalItem, conn=conn)

            if sourceItem["protocol_id"] is not None \
                    and (sourceItem["ss_section_id"] is not None or sourceItem["ss_section_name"] is not None) \
                    and sourceItem["ss_sg_key"] is not None:
                # Similarly build up item collection (order set) hierarchy and link
                itemCollection = self.itemCollectionFromSourceItem(sourceItem, conn=conn)
                itemCollectionItem = self.itemCollectionItemFromSourceItem(sourceItem, itemCollection, clinicalItem, conn=conn)
                patientItemCollectionLink = self.patientItemCollectionLinkFromSourceItem(sourceItem, itemCollectionItem, patientItem, conn=conn)
        finally:
            if not extConn:
                conn.close()

    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        categoryKey = (SOURCE_TABLE, sourceItem["order_type"], sourceItem["ordering_mode"])
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = RowItemModel(
                {
                    "source_table":  SOURCE_TABLE,
                    "description":  "{} ({})".format(sourceItem["order_type"], sourceItem["ordering_mode"])
                }
            )
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn)
            category["clinical_item_category_id"] = categoryId
            self.categoryBySourceDescr[categoryKey] = category
        return self.categoryBySourceDescr[categoryKey]

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["proc_code"])
        # This should be what determines a new unique clinical_item. 
        #   Some debate about whether to distinguish by proc_id or proc_code, but there are many labs and other procs 
        #   that use different proc_ids even though they are obviously the same. Go link in STRIDE_ORDER_PROC for examples like LABA1C.
        # The self.clinicalItemByCategoryIdExtId is supposed to keep track of which clinical_items we're already aware of, 
        #   but not that it starts blank when this module runs. 
        #   So you in theory should only run this conversion process on a database once 
        #   (otherwise it will not be aware that a bunch of duplicate clinical_items already exist in the database). 
        #   Alternatively, this module should be updated, so that it initializes this key tracker with whatever is already in the database.
        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = RowItemModel(
                {
                    "clinical_item_category_id": category["clinical_item_category_id"],
                    "external_id":               sourceItem["proc_id"],
                    "name":                      sourceItem["proc_code"],
                    "description":               sourceItem["description"],
                }
            )
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn)
            clinicalItem["clinical_item_id"] = clinicalItemId
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey]

    def patientItemFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = RowItemModel(
            {
                "external_id":      sourceItem["order_proc_id_coded"],
                "patient_id":       int(sourceItem["jc_uid"][2:], 16),
                "encounter_id":     sourceItem["pat_enc_csn_id_coded"],
                "clinical_item_id": clinicalItem["clinical_item_id"],
                "item_date":        sourceItem["order_time_jittered"],
            }
        )
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys())
        insertParams = patientItem.values()
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute(insertQuery, insertParams, conn=conn)
            patientItem["patient_item_id"] = DBUtil.execute(DBUtil.identityQuery("patient_item"), conn=conn)[0][0]
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, pull out existint ID and continue to insert whatever else is possible
            log.info(err)   # Lookup just by the composite key components to avoid attempting duplicate insertion again
            searchPatientItem = {
                "patient_id":       patientItem["patient_id"],
                "clinical_item_id": patientItem["clinical_item_id"],
                "item_date":        patientItem["item_date"],
            }
            (patientItem["patient_item_id"], isNew) = DBUtil.findOrInsertItem("patient_item", searchPatientItem, conn=conn)
        return patientItem

    def itemCollectionFromSourceItem(self, sourceItem, conn):
        sourceItem["ss_section_identifier"] = sourceItem["ss_section_id"] if sourceItem["ss_section_id"] is not None \
                                                                          else sourceItem["ss_section_name"].lower()

        collectionKey = "%(protocol_id)d-%(ss_section_identifier)s-%(ss_sg_key)s" % sourceItem
        if collectionKey not in self.itemCollectionByKeyStr:
            # Collection does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            collection = RowItemModel(
                {
                    "external_id": sourceItem["protocol_id"],
                    "name":        sourceItem["protocol_name"],
                    "section":     sourceItem["ss_section_name"],
                    "subgroup":    sourceItem["ss_sg_name"],
                }
            )
            (collectionId, isNew) = DBUtil.findOrInsertItem("item_collection", collection, conn=conn)
            collection["item_collection_id"] = collectionId
            self.itemCollectionByKeyStr[collectionKey] = collection
        return self.itemCollectionByKeyStr[collectionKey]

    def itemCollectionItemFromSourceItem(self, sourceItem, itemCollection, clinicalItem, conn):
        # Load or produce an item_collection_item record model for the given sourceItem
        itemKey = (itemCollection["item_collection_id"], clinicalItem["clinical_item_id"])
        if itemKey not in self.itemCollectionItemByCollectionIdItemId:
            # Item Collection Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            collectionItem = RowItemModel(
                {
                    "item_collection_id": itemCollection["item_collection_id"],
                    "clinical_item_id": clinicalItem["clinical_item_id"],
                    "collection_type_id": COLLECTION_TYPE_ORDERSET,
                }
            )
            (collectionItemId, isNew) = DBUtil.findOrInsertItem("item_collection_item", collectionItem, conn=conn)
            collectionItem["item_collection_item_id"] = collectionItemId
            self.itemCollectionItemByCollectionIdItemId[itemKey] = collectionItem
        return self.itemCollectionItemByCollectionIdItemId[itemKey]

    def patientItemCollectionLinkFromSourceItem(self, sourceItem, collectionItem, patientItem, conn):
        # Produce a patient_item_collection_link record model for the given sourceItem
        patientItemCollectionLink = RowItemModel(
            {
                "patient_item_id": patientItem["patient_item_id"],
                "item_collection_item_id":  collectionItem["item_collection_item_id"],
            }
        )
        insertQuery = DBUtil.buildInsertQuery("patient_item_collection_link", patientItemCollectionLink.keys())
        insertParams= patientItemCollectionLink.values()
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute(insertQuery, insertParams, conn=conn)
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
            log.info(err)

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr = "usage: %prog [options]\n" + \
            "Beware that this module is intended to be run only ONCE ever on a database. Currently will end up with duplicate clinical item keys if you try to run it in parallel or even serially."
        parser = OptionParser(usage=usageStr)
        parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time on or after this date.")
        parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time before this date.")
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: " + str.join(" ", argv))
        timer = time.time()
        startDate = None
        if options.startDate is not None:
            # Parse out the start date parameter
            timeTuple = time.strptime(options.startDate, DATE_FORMAT)
            startDate = datetime(*timeTuple[0:3])
        endDate = None
        if options.endDate is not None:
            # Parse out the end date parameter
            timeTuple = time.strptime(options.endDate, DATE_FORMAT)
            endDate = datetime(*timeTuple[0:3])
        self.convertSourceItems(startDate, endDate)

        timer = time.time() - timer
        log.info("%.3f seconds to complete", timer)


if __name__ == "__main__":
    instance = STARROrderProcConversion()
    instance.main(sys.argv)
