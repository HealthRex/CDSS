#!/usr/bin/env python
import sys, os
import time;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;

from medinfo.db.DBUtil import DB_CONNECTOR_MODULE;
IntegrityError = DB_CONNECTOR_MODULE.IntegrityError;

from Util import log;
from Env import DATE_FORMAT;

SOURCE_TABLE = "stride_dx_list";
SUBCODE_DELIM = ".";    # Delimiter for ICD9 codes to distinguish main categorization vs. detail descriptions

class STRIDEDxListConversion:
    """Data conversion module to take STRIDE provided diagnosis / problem list
    data into the structured data tables to facilitate subsequent analysis.

    Renormalizes denormalized data back out to order types (clinical_item_category),
    orders (clinical_item), and individual elements (patient_item).

    Only count for new diagnoses with "noted" dates attached.  Historical problem
    list items and encounter diagnoses without dates attached are unclear when or
    where to assign dates.
    """
    connFactory = None; # Allow specification of alternative DB connection source

    categoryBySourceDescr = None;   # Local cache to track the clinical item category table contents
    clinicalItemByCategoryIdExtId = None;   # Local cache to track clinical item table contents

    icd9StrByCode = None;   # Local cache to facilitate rapid lookups

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

        self.categoryBySourceDescr = dict();
        self.clinicalItemByCategoryIdExtId = dict();
        self.icd9_str_by_code = None
        self.icd10_str_by_code = None

    def convertSourceItems(self, startDate=None, endDate=None):
        """Primary run function to process the contents of the source table
        and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies to avoid repeating conversion.

        startDate - If provided, only return items whose noted_date is on or after that date.
        endDate - If provided, only return items whose noted_date is before that date.
        """
        log.info("Conversion for items dated %s to %s" % (startDate, endDate));
        # progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            for sourceItem in self.querySourceItems(startDate, endDate, progress=None, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn);
        finally:
            conn.close();
        # progress.PrintStatus();


    def querySourceItems(self, startDate=None, endDate=None, progress=None, conn=None):
        """Query the database for list of all source clinical items (diagnosed probelms in this case)
        and yield the results one at a time.  If startDate provided, only return items
        whose noted_date is on or after that date.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Facilitate rapid lookup of ICD9/ICD10 codes
        if self.icd9_str_by_code is None:
            self.prepare_icd9_lookup(conn=conn)
        if self.icd10_str_by_code is None:
            self.prepare_icd10_lookup(conn=conn)

        # Column headers to query for that map to respective fields in analysis table
        headers = ["pat_id","pat_enc_csn_id","noted_date","resolved_date","dx_icd9_code","dx_icd9_code_list","dx_icd10_code_list","data_source"];

        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom("stride_dx_list as dx");
        query.addWhere("noted_date is not null");   # Only work with elements that have dates assigned for now
        if startDate is not None:
            query.addWhereOp("noted_date",">=", startDate);
        if endDate is not None:
            query.addWhereOp("noted_date","<", endDate);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            row_model = RowItemModel( row, headers );

            # 2014-2017 data does not have dx_icd9_code. Instead, has
            # both dx_icd9_code_list and dx_icd10_code_list. For these items,
            # there is a one:many mapping of source item to converted item.
            # Collect icd10 codes.
            icd10_codes = set()
            if row_model['dx_icd10_code_list'] not in ['', None]:
                codes = row_model['dx_icd10_code_list'].split(',')
                for code in codes:
                    icd10_codes.add(code)
            # Collect icd9 codes.
            icd9_codes = set()
            if row_model['dx_icd9_code'] not in ['', None]:
                icd9_codes.add(row_model['dx_icd9_code'])
            else:
                if row_model['dx_icd9_code_list'] not in ['', None]:
                    codes = row_model['dx_icd9_code_list'].split(',')
                    for code in codes:
                        icd9_codes.add(code)

            # If there are no ICD codes, skip to next row.
            if len(icd9_codes) == 0 and len(icd10_codes) == 0:
                row = cursor.fetchone()
                continue

            # Process ICD codes.
            # Build a temporary dictionary so that a single loop can take care
            # of both ICD9 and ICD10 without mixing the data.
            icd_versions = {
                'ICD9': {
                    'codes': icd9_codes,
                    'lookup': self.icd9_str_by_code
                },
                'ICD10': {
                    'codes': icd10_codes,
                    'lookup': self.icd10_str_by_code
                }
            }

            for version, info in icd_versions.iteritems():
                icd_codes = info['codes']
                icd_lookup = info['lookup']

                for icd_code in icd_codes:
                    # Look up string. Otherwise default to ICD code.
                    row_model['icd_str'] = icd_code
                    if icd_code in icd_lookup:
                        row_model['icd_str'] = icd_lookup[icd_code]
                    row_model['dx_icd_code'] = version + '.' + icd_code

                    # Yield one row worth of data at a time to avoid having to keep
                    # the whole result set in memory.
                    yield row_model

                    orig_code = icd_code
                    if SUBCODE_DELIM in orig_code:
                        # Insert copies of item for parent node codes to aggregate
                        # component diagnoses into general categories.
                        while icd_code[-1] != SUBCODE_DELIM:
                            icd_code = icd_code[:-1] # Truncate trailing digit
                            if icd_code in icd_lookup:
                                # Found a a matching parent code, so yield this
                                # version.
                                row_model['icd_str'] = icd_lookup[icd_code]
                                row_model['dx_icd_code'] = version + '.' + icd_code
                                yield row_model

                        # One more cycle to get parent node with no subcode
                        # delimiter at all.
                        icd_code = icd_code[:-1] # Truncate off SUBCODE_DELIM
                        if icd_code in icd_lookup:
                            row_model['icd_str'] = icd_lookup[icd_code]
                            row_model['dx_icd_code'] = version + '.' + icd_code

                            yield row_model

            # Process ICD10 codes.

            row = cursor.fetchone();
            # progress.Update();

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
            categoryModel = self.categoryFromSourceItem(sourceItem, conn=conn);
            clinicalItem = self.clinicalItemFromSourceItem(sourceItem, categoryModel, conn=conn);
            patientItem = self.patientItemModelFromSourceItem(sourceItem, clinicalItem, conn=conn);

        finally:
            if not extConn:
                conn.close();


    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        categoryKey = (SOURCE_TABLE, sourceItem["data_source"]);
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = \
                RowItemModel \
                (   {   "source_table":  SOURCE_TABLE,
                        "description":  "Diagnosis (%s)" % sourceItem["data_source"],
                    }
                );
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn);
            category["clinical_item_category_id"] = categoryId;
            self.categoryBySourceDescr[categoryKey] = category;
        return self.categoryBySourceDescr[categoryKey];

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem['dx_icd_code']);

        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel \
                (   {   "clinical_item_category_id": category["clinical_item_category_id"],
                        "external_id": None,
                        "name": "%s" % sourceItem['dx_icd_code'],
                        "description": "%(icd_str)s" % sourceItem,
                    }
                );
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn);
            clinicalItem["clinical_item_id"] = clinicalItemId;
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem;
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey]

    def patientItemModelFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id": None,
                    "patient_id":  sourceItem["pat_id"],
                    "encounter_id":  sourceItem["pat_enc_csn_id"],
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["noted_date"],
                }
            );
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys() );
        insertParams= patientItem.values();
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute( insertQuery, insertParams, conn=conn );
        except IntegrityError, err:
            # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
            log.info(err);
            pass;

    def prepare_icd9_lookup(self, conn):
        """
        One big query for ICD9 lookup table at one time so don't have to keep
        repeating.
        """
        query = "SELECT code, str FROM stride_icd9_cm WHERE tty IN ('HT','PT')"
        results = DBUtil.execute(query, conn=conn)

        self.icd9_str_by_code = dict()
        for (code, str) in results:
            self.icd9_str_by_code[code] = str

    def prepare_icd10_lookup(self, conn):
        """
        One big query for ICD10 lookup table at one time so don't have to keep
        repeating.
        """
        query = "SELECT icd10_code, full_description FROM stride_icd10_cm"
        results = DBUtil.execute(query, conn=conn)

        self.icd10_str_by_code = dict()
        for (code, str) in results:
            self.icd10_str_by_code[code] = str

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
    instance = STRIDEDxListConversion();
    instance.main(sys.argv);
