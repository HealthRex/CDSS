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
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList, RowItemFieldComparator;

from Util import log;
from Const import TEMPLATE_MEDICATION_ID, TEMPLATE_MEDICATION_PREFIX;
from Const import COLLECTION_TYPE_ORDERSET;
from Env import DATE_FORMAT;

SOURCE_TABLE = "stride_preadmit_med";
CATEGORY_TEMPLATE = "Preadmit Med";    # For this data source, item category will be a Preadmission Medication
GENERIC_CODE_TEMPLATE = "MED%s";   # Template for generic medication code reference if detailed RXCUI values not available
RXCUI_CODE_TEMPLATE = "RXCUI%s";    # Template for medication code references when detailed RXCUI values available

class STRIDEPreAdmitMedConversion:
    """Data conversion module to take STRIDE data
    into the structured data analysis tables to facilitate subsequent analysis.
    """

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source, but Allow specification of alternative DB connection source

        self.categoryBySourceDescr = dict();    # Local cache to track the clinical item category table contents
        self.clinicalItemByCategoryIdCode = dict(); # Local cache to track clinical item table contents

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
            # Load up the medication mapping table to facilitate subsequent conversions
            rxcuiDataByMedId = self.loadRXCUIData(conn=conn);

            # Next round for medications directly from order_med table not addressed in medmix
            i = 1
            for sourceItem in self.querySourceItems(rxcuiDataByMedId, convOptions, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn);
                print i
                i = i + 1
                progress.Update();

        finally:
            conn.close();
        # progress.PrintStatus();


    def loadRXCUIData(self, conn=None):
        """Load up the full contents of the stride_mapped_meds table into
        memory (only a few thousand records) to facilitate rapid lookup resolution
        of common medication ingredient data.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        try:
            rxcuiDataByMedId = dict();

            # thera_class, pharm_class, and pharm_subclass are not originally
            # provided by STARR data set. Given it is only imputed to
            # starr_mapped_meds here, add the column if it does not exist.
            query = \
                """
                ALTER TABLE
                    stride_mapped_meds
                ADD COLUMN IF NOT EXISTS
                    thera_class TEXT;
                """
            DBUtil.execute(query)
            query = \
                """
                ALTER TABLE
                    stride_mapped_meds
                ADD COLUMN IF NOT EXISTS
                    pharm_class TEXT;
                """
            DBUtil.execute(query)
            query = \
                """
                ALTER TABLE
                    stride_mapped_meds
                ADD COLUMN IF NOT EXISTS
                    pharm_subclass TEXT;
                """
            DBUtil.execute(query)

            query = \
                """select medication_id, rxcui, active_ingredient, thera_class
                from stride_mapped_meds
                """;

            cursor = conn.cursor();
            cursor.execute( query );

            row = cursor.fetchone();
            while row is not None:
                (medId, rxcui, ingredient, theraClass) = row;   # Unpack the data tuple
                if medId not in rxcuiDataByMedId:
                    rxcuiDataByMedId[medId] = dict();
                rxcuiDataByMedId[medId][rxcui] = (ingredient, theraClass);

                row = cursor.fetchone();

            return rxcuiDataByMedId;

        finally:
            if not extConn:
                conn.close();

    def querySourceItems(self, rxcuiDataByMedId, convOptions, progress=None, conn=None):
        """Query the database for list of all source clinical items (medications, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose
        occurence date is on or after that date.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        headers = ["medication_id","pat_anon_id","contact_date","medication_id","description","thera_class","pharm_class","pharm_subclass"];

        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom("stride_preadmit_med");
        if convOptions.startDate is not None:
            query.addWhereOp("contact_date",">=", convOptions.startDate);
        if convOptions.endDate is not None:
            query.addWhereOp("contact_date","<", convOptions.endDate);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            for normalizedModel in self.normalizeMedIngredients(rxcuiDataByMedId, rowModel, convOptions, conn=conn):
                yield normalizedModel; # Yield one row worth of data at a time to avoid having to keep the whole result set in memory
            row = cursor.fetchone();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();

    def normalizeMedIngredients(self, rxcuiDataByMedId, rowModel, convOptions, conn=None):
        """Given a rowModel of medication data, normalize it further.
        Specifically, look for common active ingredients to simplify the data.
        If the medication is actually a compound of multiple active ingredients,
        then break out into active ingredients.

        If normalizeMixtures set, then will yield out multiple items to reflect each active ingredient.
        If normalizeMixtures not set, will yield a single item with name being a composite of the active ingredients.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        medId = rowModel["medication_id"]

        if medId not in rxcuiDataByMedId:
            # No mapping entry found, just use the available generic medication data then
            rowModel["code"] = GENERIC_CODE_TEMPLATE % rowModel["medication_id"];
            yield rowModel;

        else:
            # Mapping entry found, yield a normalized model for each active ingredient found
            #   (will usually be a 1-to-1 relation, but sometimes multiple
            ingredientTheraClassByRxcui = rxcuiDataByMedId[medId];
            if len(ingredientTheraClassByRxcui) <= 1 or convOptions.normalizeMixtures:

                # Single ingredient or want component active ingredients to each have one record
                for (rxcui, (ingredient, theraClass)) in ingredientTheraClassByRxcui.iteritems():
                    # ~250/15000 RxCUI's don't have a defined active ingredient.
                    if ingredient is None:
                        continue

                    normalizedModel = RowItemModel(rowModel);
                    normalizedModel["medication_id"] = rxcui;
                    normalizedModel["code"] = RXCUI_CODE_TEMPLATE % rxcui;
                    normalizedModel["description"] = ingredient.title();

                    yield normalizedModel;
            elif convOptions.maxMixtureCount is not None and len(ingredientTheraClassByRxcui) > convOptions.maxMixtureCount:
                # Plan to denormalize, but excessively large mixture.  Forget it.
                rowModel["code"] = GENERIC_CODE_TEMPLATE % rowModel["medication_id"];
                yield rowModel;
            else:
                # Mixture of multiple ingredients and want to keep denormalized
                # Extract out the active ingredient names to make a composite based only on that unique combination
                ingredientRxcuiList = [ (ingredient, rxcui) for (rxcui, (ingredient, theraClass)) in ingredientTheraClassByRxcui.iteritems()];
                ingredientRxcuiList.sort();   # Ensure consistent order

                rxcuiStrList = list();
                ingredientList = list();
                for (ingredient, rxcui) in ingredientRxcuiList:
                    # ~250/15000 RxCUI's don't have a defined active ingredient.
                    if ingredient is None:
                        continue
                        
                    rxcuiStrList.append(str(rxcui));
                    ingredientList.append(ingredient.title());
                rxcuiComposite = str.join(",", rxcuiStrList );
                ingredientComposite = str.join("-",ingredientList );

                #rowModel["medication_id"] = hash(rxcuiComposite);    # No, just stick to existing medication ID
                rowModel["code"] = GENERIC_CODE_TEMPLATE % medId;
                rowModel["description"] = ingredientComposite;
                yield rowModel;

            # Do some extra work here to see if we can figure out therapeutic / pharaceutical class labels based on available data
            if rowModel["thera_class"] is not None:
                theraClassNeedsPopulation = False;
                for (rxcui, (ingredient, theraClass)) in ingredientTheraClassByRxcui.iteritems():
                    if theraClass is None:
                        # Don't have a previously populated class labels for this medication ID, but just found it with this data.  Populate then.
                        theraClass = rowModel["thera_class"];
                        ingredientTheraClassByRxcui[rxcui] = (ingredient, theraClass);
                        theraClassNeedsPopulation = True;
                if theraClassNeedsPopulation:
                    rowDict = {"thera_class": rowModel["thera_class"], "pharm_class": rowModel["pharm_class"], "pharm_subclass": rowModel["pharm_subclass"],}
                    DBUtil.updateRow("stride_mapped_meds", rowDict, medId, idCol="medication_id", conn=conn);

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
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["code"]);
        if clinicalItemKey not in self.clinicalItemByCategoryIdCode:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel \
                (   {   "clinical_item_category_id": category["clinical_item_category_id"],
                        "external_id": sourceItem["medication_id"],
                        "name": sourceItem["code"],
                        "description": sourceItem["description"],
                    }
                );
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn);
            clinicalItem["clinical_item_id"] = clinicalItemId;
            self.clinicalItemByCategoryIdCode[clinicalItemKey] = clinicalItem;
        return self.clinicalItemByCategoryIdCode[clinicalItemKey];

    def patientItemFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id":  sourceItem["medication_id"],
                    "patient_id":  sourceItem["pat_anon_id"],
                    "encounter_id":  None,
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["contact_date"],
                }
            );
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys() );
        insertParams= patientItem.values();
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute( insertQuery, insertParams, conn=conn );
            patientItem["patient_item_id"] = DBUtil.execute( DBUtil.identityQuery("patient_item"), conn=conn )[0][0];
        except IntegrityError, err:
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
        parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time on or after this date.");
        parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time before this date.");
        parser.add_option("-n", "--normalizeMixtures", dest="normalizeMixtures", action="store_true",  help="If set, when find medication mixtures, will unravel / normalize into separate entries, one for each ingredient");
        parser.add_option("-m", "--maxMixtureCount", dest="maxMixtureCount", help="If not normalizing mixtures, then this is the maximum number of mixture components will itemize for a mixture.  If more than this, just use the summary label.");
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
        self.normalizeMixtures = False;
        self.maxMixtureCount = None;

    def extractParserOptions(self, options):
        if options.startDate is not None:
            # Parse out the start date parameter
            timeTuple = time.strptime(options.startDate, DATE_FORMAT);
            self.startDate = datetime(*timeTuple[0:3]);

        if options.endDate is not None:
            # Parse out the end date parameter
            timeTuple = time.strptime(options.endDate, DATE_FORMAT);
            self.endDate = datetime(*timeTuple[0:3]);

        if options.maxMixtureCount is not None:
            self.maxMixtureCount = int(options.maxMixtureCount);

if __name__ == "__main__":
    instance = STRIDEPreAdmitMedConversion();
    instance.main(sys.argv);
