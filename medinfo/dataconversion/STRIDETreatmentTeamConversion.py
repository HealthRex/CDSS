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
from Const import TEMPLATE_MEDICATION_ID, TEMPLATE_MEDICATION_PREFIX;
from Const import COLLECTION_TYPE_ORDERSET;
from Env import DATE_FORMAT;

SOURCE_TABLE = "stride_treatment_team";
CATEGORY_TEMPLATE = "Treatment Team";
KEY_PROVIDER_PREFIXES = ("TT ","CON "); # Name Prefixes indicating a special (team) provider

TEAM_PREFIXES = ("Primary", "Consulting");
ADDITIONAL_PRIMARY_PROVIDERS = ("Nurse Practitioner","Physician's Assistant");  # Provider types to also count as "Primary" team

# Words to discard from team labels, such as pager and phones
DISCARD_WORDS = ("PAGER","PGR","PRG","SPECTRAS");

# Words to identify as some kind of sublabel to ignore for aggregation purposes
SUB_LABEL_WORDS = ("GOLD","RED","WHITE","BLUE","GREEN","ATTENDING","ONLY","INTERN","RESIDENT","RES","NP","NON","RESI");

class STRIDETreatmentTeamConversion:
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
        """Query the database for list of all source clinical items (medications, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose
        occurence date is on or after that date.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        headers = ["stride_treatment_team_id","pat_id","pat_enc_csn_id","trtmnt_tm_begin_date","trtmnt_tm_end_date","treatment_team","prov_name"];

        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom("stride_treatment_team");
        if convOptions.startDate is not None:
            query.addWhereOp("trtmnt_tm_begin_date",">=", convOptions.startDate);
        if convOptions.endDate is not None:
            query.addWhereOp("trtmnt_tm_begin_date","<", convOptions.endDate);  # Still use begin date as common filter value

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            yield self.normalizeRowModel(rowModel, convOptions)  # Yield one row worth of data at a time to avoid having to keep the whole result set in memory
            row = cursor.fetchone();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();

    def normalizeRowModel(self, rowModel, convOptions):
        """Given a rowModel of data, normalize it further.
        Specifically, look for aggregate data items (e.g., multiple Gen Med treatment teams, report as one)
        """
        (teamAcronym, teamName) = self.cleanName(rowModel["treatment_team"], convOptions);
        (provAcronym, provName) = self.cleanName(rowModel["prov_name"], convOptions, keyPrefixes=KEY_PROVIDER_PREFIXES);
        provName = provName.title();

        if provAcronym != "":
            rowModel["code"] = "%s (%s)" % (provAcronym, teamAcronym);
            rowModel["description"] = "%s (%s)" % (provName, teamName);
        else:
            rowModel["code"] = teamAcronym;
            rowModel["description"] = teamName;

        if rowModel["trtmnt_tm_begin_date"] is None:
            # Don't know how to use event information with a timestamp
            pass;

        return rowModel;

    def cleanName(self, inputName, convOptions, keyPrefixes=None):
        """Given an input name (e.g., treatment team or provider)
        Return a 2-ple (acronym, cleaned) with an acronym version
        and a cleaned up version (discard extra punctuation, phone/pager numbers, etc.)
        If keyPrefixes specified, then only accept input names that start with one of them
        (e.g., "TT" or "CON" for provider names, to only look at team names instead of named individuals.
        """
        isPrefixAcceptable = True;
        if keyPrefixes is not None:
            isPrefixAcceptable = False;
            for keyPrefix in keyPrefixes:
                if inputName is not None and inputName.startswith(keyPrefix):
                    isPrefixAcceptable = True;

        # Default to blanks
        acronym = "";
        cleanedName = "";

        if isPrefixAcceptable and inputName is not None:
            acronymList = list();
            wordList = list();
            chunks = inputName.split();
            for i, chunk in enumerate(chunks):
                if chunk[-1] == ",":    # Strip any commass
                    chunk = chunk[:-1];

                if convOptions.aggregate and i == 0 and chunk in TEAM_PREFIXES:
                    # Aggregating mixed records, so just use batch team prefix if exists
                    acronymList.append(chunk[0]);
                    wordList.append(chunk);
                    break
                elif convOptions.aggregate and chunk.upper() in SUB_LABEL_WORDS:
                    # Sub label word not interested when aggregating data, so just ignore it
                    continue
                elif convOptions.aggregate and len(chunk) == 1:
                    # A short number or letter sub-label, ignore if aggregating
                    continue
                elif convOptions.aggregate and len(chunk) <= 2 and (chunk[0].isdigit() or chunk[-1].isdigit()):
                    # A short number or letter sub-label, ignore if aggregating
                    continue
                elif len(chunk) <= 2 and not chunk[0].isalnum() and not chunk[-1].isalnum():
                    # Short non-alphanumeric sequence, probably punctuation
                    continue
                elif not chunk[0].isalnum() and len(chunk) >1 and chunk[1].isdigit():
                    # Probably just a pager/phone number
                    continue
                elif len(chunk) > 1 and chunk[0].isdigit() and chunk[-1].isdigit():
                    # Looks like a number, probably pager or phone.  Don't include
                    continue
                elif chunk in DISCARD_WORDS:
                    # Probably just pager link, not interested
                    continue
                else:
                    if chunk[0].isalnum():
                        acronymList.append(chunk[0])
                    else:   # Get the next character if first was not alphanumeric, probably an open parantheses "("
                        acronymList.append(chunk[1])
                    wordList.append(chunk);
            acronym = str.join("", acronymList );
            cleanedName = str.join(" ", wordList );

            if convOptions.aggregate and inputName in ADDITIONAL_PRIMARY_PROVIDERS:
                # Override specific provider names as generic primary team members
                (acronym, cleanedName) = ("P","Primary");

        return (acronym, cleanedName);



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
                        "name": sourceItem["code"],
                        "description": sourceItem["description"],
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
            (   {   "external_id":  sourceItem["stride_treatment_team_id"],
                    "patient_id":  sourceItem["pat_id"],
                    "encounter_id":  sourceItem["pat_enc_csn_id"],
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["trtmnt_tm_begin_date"],
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
        parser.add_option("-a", "--aggregate", dest="aggregate", action="store_true",  help="If set, will try to aggregate data so Med Univ A1, A2, A3 will all be counted as Med Univ and Primary Team, Intern, Resident will all just be counted as Primary.");
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
        self.aggregate = False;

    def extractParserOptions(self, options):
        if options.startDate is not None:
            # Parse out the start date parameter
            timeTuple = time.strptime(options.startDate, DATE_FORMAT);
            self.startDate = datetime(*timeTuple[0:3]);

        if options.endDate is not None:
            # Parse out the end date parameter
            timeTuple = time.strptime(options.endDate, DATE_FORMAT);
            self.endDate = datetime(*timeTuple[0:3]);

        self.aggregate = options.aggregate;

if __name__ == "__main__":
    instance = STRIDETreatmentTeamConversion();
    instance.main(sys.argv);
