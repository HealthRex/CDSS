#!/usr/bin/env python
import sys, os
import time;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList, RowItemFieldComparator;

from Util import log;
from Env import DATE_FORMAT;

SOURCE_TABLE = "stride_culture_micro";
CATEGORY_TEMPLATE = "Culture Susceptibility";

class STRIDECultureMicroConversion:
    """Data conversion module to take STRIDE data
    into the structured data analysis tables to facilitate subsequent analysis.
    """

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source, but Allow specification of alternative DB connection source

        self.categoryBySourceDescr = dict();    # Local cache to track the clinical item category table contents
        self.clinicalItemByCompositeKey = dict(); # Local cache to track clinical item table contents

    def convertSourceItems(self, convOptions):
        """Primary run function to process the contents of the raw source
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies after the fact to catch repeated conversions.

        startDate - If provided, only return items whose ordering_date is on or after that date.
        endDate - If provided, only return items whose ordering_date is before that date.
        """
        log.info("Conversion for items dated %s to %s" % (convOptions.startDate, convOptions.endDate));
        progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            # Next round for medications directly from order_med table not addressed in medmix
            for sourceItem in self.querySourceItems(convOptions, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn);
                progress.Update();

        finally:
            conn.close();
        progress.PrintStatus();


    def querySourceItems(self, convOptions, progress=None, conn=None):
        """Query the database for list of all source clinical items (culture results, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose
        occurence date is on or after that date.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table

        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        headers = ["stride_treatment_team_id","pat_id","pat_enc_csn_id","trtmnt_tm_begin_date","trtmnt_tm_end_date","treatment_team","prov_name"];
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################


        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom("stride_culture_micro");
        if convOptions.startDate is not None:
            query.addWhereOp("trtmnt_tm_begin_date",">=", convOptions.startDate);
        if convOptions.endDate is not None:
            query.addWhereOp("trtmnt_tm_begin_date","<", convOptions.endDate);  # Still use begin date as common filter value
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################
        ############ TO DO: Fix this to match the actual data of interest ##################


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
            #   in a first pass, with subsequent calls just yielding back in memory cached copies
            category = self.categoryFromSourceItem(sourceItem, conn=conn);
            clinicalItem = self.clinicalItemFromSourceItem(sourceItem, category, conn=conn);
            patientItem = self.patientItemFromSourceItem(sourceItem, clinicalItem, conn=conn);

        finally:
            if not extConn:
                conn.close();



    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        #   In this case, always Medication
        categoryDescription = CATEGORY_TEMPLATE;
        categoryKey = (SOURCE_TABLE, categoryDescription);
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = \
                RowItemModel \
                (   {   "source_table":  SOURCE_TABLE,
                        "description":  categoryDescription,
                    }
                );
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn);
            category["clinical_item_category_id"] = categoryId;
            self.categoryBySourceDescr[categoryKey] = category;
        return self.categoryBySourceDescr[categoryKey];

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["description"]);
        if clinicalItemKey not in self.clinicalItemByCompositeKey:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel \
                (   {   "clinical_item_category_id": category["clinical_item_category_id"],
                        "external_id": None,
                        "name": "%(proc_code)s;%(antibiotic)s;%(suscibility)s" % sourceItem, ############FIX THIS TO BE WHATEVER from source data
                        "description": "%(proc_code)s;%(antibiotic)s;%(suscibility)s" % sourceItem,   ############FIX THIS TO BE WHATEVER from source data
                    }
                );
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn);
            clinicalItem["clinical_item_id"] = clinicalItemId;
            self.clinicalItemByCompositeKey[clinicalItemKey] = clinicalItem;
        return self.clinicalItemByCompositeKey[clinicalItemKey];

    def patientItemFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id":  sourceItem["order_proc_anon_id"],      #### Or whatever was the most unique source ID?
                    "patient_id":  sourceItem["pat_id"],                ### Fix reference
                    "encounter_id":  sourceItem["pat_enc_csn_id"],          ### Fix reference
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["XXXX_date"],       ### Whatever is the result timestamp???
                }
            );
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys() );
        insertParams= patientItem.values();
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute( insertQuery, insertParams, conn=conn );
            patientItem["patient_item_id"] = DBUtil.execute( DBUtil.identityQuery("patient_item"), conn=conn )[0][0];
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, pull out existing ID and continue to insert whatever else is possible
            log.info(err);   # Lookup just by the composite key components to avoid attempting duplicate insertion again
            searchPatientItem = \
                {   "patient_id":       patientItem["patient_id"],
                    "clinical_item_id": patientItem["clinical_item_id"],
                    "item_date":        patientItem["item_date"],
                }
            (patientItem["patient_item_id"], isNew) = DBUtil.findOrInsertItem("patient_item", searchPatientItem, conn=conn);
        return patientItem;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options]\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with start time on or after this date.");
        parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with start time before this date.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        convOptions = ConversionOptions();
        convOptions.extractParserOptions(options);

        self.convertSourceItems(convOptions);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

class ConversionOptions:
    """Simple struct to contain multiple program options"""
    def __init__(self):
        self.startDate = None;
        self.endDate = None;

    def extractParserOptions(self, options):
        if options.startDate is not None:
            # Parse out the start date parameter
            timeTuple = time.strptime(options.startDate, DATE_FORMAT);
            self.startDate = datetime(*timeTuple[0:3]);

        if options.endDate is not None:
            # Parse out the end date parameter
            timeTuple = time.strptime(options.endDate, DATE_FORMAT);
            self.endDate = datetime(*timeTuple[0:3]);

if __name__ == "__main__":
    instance = STRIDECultureMicroConversion();
    instance.main(sys.argv);
