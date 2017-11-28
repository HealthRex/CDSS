#!/usr/bin/env python
import sys, os
import time;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.DBUtil import DB_CONNECTOR_MODULE;
IntegrityError = DB_CONNECTOR_MODULE.IntegrityError;
from medinfo.db.Model import SQLQuery;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;

from Util import log;
from Env import DATE_FORMAT;
from Const import COLLECTION_TYPE_ORDERSET;

SOURCE_TABLE = "stride_order_proc";

class STRIDEOrderProcConversion:
    """Data conversion module to take STRIDE provided computerized physician order entry data
    into the structured data analysis tables to facilitate subsequent analysis.

    Renormalizes denormalized data back out to order types (clinical_item_category),
    orders (clinical_item), and actual individual patient orders (patient_item).
    Ignores records with instantiated_time not null, so will only be interested
    in originally ordered parent orders, not spawned child orders.

    Consider Ignore PRN orders for now to simplify data set and focus on standing orders
        (but a small minority for these orders anyway)
    """
    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source, but Allow specification of alternative DB connection source

        self.categoryBySourceDescr = dict();    # Local cache to track the clinical item category table contents
        self.clinicalItemByCategoryIdExtId = dict(); # Local cache to track clinical item table contents
        self.itemCollectionByKeyStr = dict();   # Local cache to track item collections
        self.itemCollectionItemByCollectionIdItemId = dict();   # Local cache to track item collection items

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
        # progress.PrintStatus();


    def querySourceItems(self, startDate=None, endDate=None, progress=None, conn=None):
        """Query the database for list of all source clinical items (orders, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose order_time is on or after that date.
        Ignore entries with instantiated_time not null, as those represent child orders spawned from an original order,
        whereas we are more interested in the decision making to enter the original order.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        queryHeaders = ["op.order_proc_id", "pat_id", "pat_enc_csn_id", "op.order_type", "op.proc_id", "op.proc_code", "description", "order_time","protocol_id","protocol_name","section_name","smart_group"];
        headers = ["order_proc_id", "pat_id", "pat_enc_csn_id", "order_type", "proc_id", "proc_code", "description", "order_time","protocol_id","protocol_name","section_name","smart_group"];

        query = SQLQuery();
        for header in queryHeaders:
            query.addSelect( header );
        query.addFrom("stride_order_proc as op left outer join stride_orderset_order_proc as os on op.order_proc_id = os.order_proc_id");
        query.addWhere("order_time is not null");   # Rare cases of "comment" orders with no date/time associated
        query.addWhere("instantiated_time is null");
        query.addWhere("(stand_interval is null or stand_interval not like '%%PRN')");  # Ignore PRN orders to simplify somewhat
        if startDate is not None:
            query.addWhereOp("order_time",">=", startDate);
        if endDate is not None:
            query.addWhereOp("order_time","<", endDate);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            yield rowModel; # Yield one row worth of data at a time to avoid having to keep the whole result set in memory
            row = cursor.fetchone();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();


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
            category = self.categoryFromSourceItem(sourceItem, conn=conn);
            clinicalItem = self.clinicalItemFromSourceItem(sourceItem, category, conn=conn);
            patientItem = self.patientItemFromSourceItem(sourceItem, clinicalItem, conn=conn);

            if sourceItem["protocol_id"] is not None:
                # Similarly build up item collection (order set) hierarchy and link
                itemCollection = self.itemCollectionFromSourceItem(sourceItem, conn=conn);
                itemCollectionItem = self.itemCollectionItemFromSourceItem(sourceItem, itemCollection, clinicalItem, conn=conn);
                patientItemCollectionLink = self.patientItemCollectionLinkFromSourceItem(sourceItem, itemCollectionItem, patientItem, conn=conn);
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
                        "description":  sourceItem["order_type"],
                    }
                );
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn);
            category["clinical_item_category_id"] = categoryId;
            self.categoryBySourceDescr[categoryKey] = category;
        return self.categoryBySourceDescr[categoryKey];

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["proc_id"]);
        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel \
                (   {   "clinical_item_category_id": category["clinical_item_category_id"],
                        "external_id": sourceItem["proc_id"],
                        "name": sourceItem["proc_code"],
                        "description": sourceItem["description"],
                    }
                );
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn);
            clinicalItem["clinical_item_id"] = clinicalItemId;
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem;
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey];

    def patientItemFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id":  sourceItem["order_proc_id"],
                    "patient_id":  sourceItem["pat_id"],
                    "encounter_id":  sourceItem["pat_enc_csn_id"],
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["order_time"],
                }
            );
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys() );
        insertParams= patientItem.values();
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute( insertQuery, insertParams, conn=conn );
            patientItem["patient_item_id"] = DBUtil.execute( DBUtil.identityQuery("patient_item"), conn=conn )[0][0];
        except IntegrityError, err:
            # If turns out to be a duplicate, okay, pull out existint ID and continue to insert whatever else is possible
            log.info(err);   # Lookup just by the composite key components to avoid attempting duplicate insertion again
            searchPatientItem = \
                {   "patient_id":       patientItem["patient_id"],
                    "clinical_item_id": patientItem["clinical_item_id"],
                    "item_date":        patientItem["item_date"],
                }
            (patientItem["patient_item_id"], isNew) = DBUtil.findOrInsertItem("patient_item", searchPatientItem, conn=conn);
        return patientItem;



    def itemCollectionFromSourceItem(self, sourceItem, conn):
        # Load or produce an item_collection record model for the given sourceItem
        if sourceItem["protocol_id"] is None:
            # No order set link to this item, so nothing to return
            return None;

        collectionKey = "%(protocol_id)s-%(protocol_name)s-%(section_name)s-%(smart_group)s" % sourceItem;
        self.itemCollectionByKeyStr = dict();   # Local cache to track item collections
        if collectionKey not in self.itemCollectionByKeyStr:
            # Collection does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            collection = \
                RowItemModel \
                (   {   "external_id":  sourceItem["protocol_id"],
                        "name":  sourceItem["protocol_name"],
                        "section":  sourceItem["section_name"],
                        "subgroup":  sourceItem["smart_group"],
                    }
                );
            (collectionId, isNew) = DBUtil.findOrInsertItem("item_collection", collection, conn=conn);
            collection["item_collection_id"] = collectionId;
            self.itemCollectionByKeyStr[collectionKey] = collection;
        return self.itemCollectionByKeyStr[collectionKey];

    def itemCollectionItemFromSourceItem(self, sourceItem, itemCollection, clinicalItem, conn):
        # Load or produce an item_collection_item record model for the given sourceItem
        itemKey = (itemCollection["item_collection_id"], clinicalItem["clinical_item_id"]);
        if itemKey not in self.itemCollectionItemByCollectionIdItemId:
            # Item Collection Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            collectionItem = \
                RowItemModel \
                (   {   "item_collection_id": itemCollection["item_collection_id"],
                        "clinical_item_id": clinicalItem["clinical_item_id"],
                        "collection_type_id": COLLECTION_TYPE_ORDERSET,
                    }
                );
            (collectionItemId, isNew) = DBUtil.findOrInsertItem("item_collection_item", collectionItem, conn=conn);
            collectionItem["item_collection_item_id"] = collectionItemId;
            self.itemCollectionItemByCollectionIdItemId[itemKey] = collectionItem;
        return self.itemCollectionItemByCollectionIdItemId[itemKey];

    def patientItemCollectionLinkFromSourceItem(self, sourceItem, collectionItem, patientItem, conn):
        # Produce a patient_item_collection_link record model for the given sourceItem
        patientItemCollectionLink = \
            RowItemModel \
            (   {   "patient_item_id": patientItem["patient_item_id"],
                    "item_collection_item_id":  collectionItem["item_collection_item_id"],
                }
            );
        insertQuery = DBUtil.buildInsertQuery("patient_item_collection_link", patientItemCollectionLink.keys() );
        insertParams= patientItemCollectionLink.values();
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute( insertQuery, insertParams, conn=conn );
        except IntegrityError, err:
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
            # Parse out the end date parameter
            timeTuple = time.strptime(options.endDate, DATE_FORMAT);
            endDate = datetime(*timeTuple[0:3]);
        self.convertSourceItems(startDate,endDate);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = STRIDEOrderProcConversion();
    instance.main(sys.argv);
