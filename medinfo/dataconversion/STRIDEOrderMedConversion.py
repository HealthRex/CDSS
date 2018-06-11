#!/usr/bin/env python
import sys, os
import hashlib
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

SOURCE_TABLE = "stride_order_med";
CATEGORY_TEMPLATE = "Med (%s)";    # For this data source, item category will be a Medication subscripted by medication route
GENERIC_CODE_TEMPLATE = "MED%s";   # Template for generic medication code reference if detailed RXCUI values not available
RXCUI_CODE_TEMPLATE = "RXCUI%s";    # Template for medication code references when detailed RXCUI values available

class STRIDEOrderMedConversion:
    """Data conversion module to take STRIDE provided computerized physician order entry data
    (medications specifically)
    into the structured data analysis tables to facilitate subsequent analysis.

    For combination medications (usually same medication but with "1.5x" dosing like
    Metoprolol 75mg ordered as combination of 50mg + 25mg tabs), just record as the
    first component in the mixture.

    Ignore PRN orders for now to simplify data set and focus on standing orders.
    """

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source, but Allow specification of alternative DB connection source

        self.categoryBySourceDescr = dict();    # Local cache to track the clinical item category table contents
        self.clinicalItemByCategoryIdCode = dict(); # Local cache to track clinical item table contents
        self.itemCollectionByKeyStr = dict();   # Local cache to track item collections
        self.itemCollectionItemByCollectionIdItemId = dict();   # Local cache to track item collection items

    def convertSourceItems(self, convOptions):
        """Primary run function to process the contents of the stride_order_med
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies after the fact to catch repeatEd conversions.

        startDate - If provided, only return items whose ordering_date is on or after that date.
        endDate - If provided, only return items whose ordering_date is before that date.
        """
        log.info("Conversion for items dated %s to %s" % (convOptions.startDate, convOptions.endDate));
        progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            # Load up the medication mapping table to facilitate subsequent conversions
            rxcuiDataByMedId = self.loadRXCUIData(conn=conn);

            # Keep track of which order meds have already been converted based on mixture components (don't repeat for the aggregate order then)
            # Can be a lot to store in local memory for large conversions, so may need to batch smaller sub-processes
            convertedOrderMedIds = set();

            # First round for medication combinations that must be extracted from order_medmixinfo table
            for sourceItem in self.queryMixSourceItems(rxcuiDataByMedId, convOptions, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn);
                convertedOrderMedIds.add(sourceItem["order_med_id"]);
                progress.Update();

            # Next round for medications directly from order_med table not addressed in medmix
            for sourceItem in self.querySourceItems(rxcuiDataByMedId, convOptions, progress=progress, conn=conn):
                if sourceItem["order_med_id"] not in convertedOrderMedIds:  # Don't repeat conversion if mixture components already addressed
                    self.convertSourceItem(sourceItem, conn=conn);
                progress.Update();

        finally:
            conn.close();
        progress.PrintStatus();


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

            query = \
                """select medication_id, rxcui, active_ingredient
                from stride_mapped_meds
                """;

            cursor = conn.cursor();
            cursor.execute( query );

            row = cursor.fetchone();
            while row is not None:
                (medId, rxcui, ingredient) = row;   # Unpack the data tuple
                if medId not in rxcuiDataByMedId:
                    rxcuiDataByMedId[medId] = dict();
                rxcuiDataByMedId[medId][rxcui] = ingredient;

                row = cursor.fetchone();

            return rxcuiDataByMedId;

        finally:
            if not extConn:
                conn.close();

    def querySourceItems(self, rxcuiDataByMedId, convOptions, progress=None, conn=None):
        """Query the database for list of all source clinical items (medications, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose
        ordering_date is on or after that date.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        queryHeaders = ["med.order_med_id", "pat_id", "pat_enc_csn_id", "med.medication_id", "med.description", "ordering_date", "med_route","number_of_doses","protocol_id","protocol_name","section_name","smart_group"];
        headers = ["order_med_id", "pat_id", "pat_enc_csn_id", "medication_id", "description", "ordering_date", "med_route","number_of_doses","protocol_id","protocol_name","section_name","smart_group"];

        query = SQLQuery();
        for header in queryHeaders:
            query.addSelect( header );
        query.addFrom("stride_order_med as med left outer join stride_orderset_order_med as os on med.order_med_id = os.order_med_id"); # Grab order set links if they exist
        query.addWhere("med.medication_id <> %s" % TEMPLATE_MEDICATION_ID );
        query.addWhere("freq_name not like '%%PRN'");   # Ignore PRN orders
        if convOptions.startDate is not None:
            query.addWhereOp("ordering_date",">=", convOptions.startDate);
        if convOptions.endDate is not None:
            query.addWhereOp("ordering_date","<", convOptions.endDate);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            for normalizedModel in self.normalizeMedData(rxcuiDataByMedId, rowModel, convOptions):
                yield normalizedModel; # Yield one row worth of data at a time to avoid having to keep the whole result set in memory
            row = cursor.fetchone();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();

    def queryMixSourceItems(self, rxcuiDataByMedId, convOptions, progress=None, conn=None):
        """Query the database for list of source clinical items (medications from mixes, etc.)
        and yield the results one at a time.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        queryHeaders = ["med.order_med_id", "med.pat_id", "med.pat_enc_csn_id", "mix.medication_id", "mix.medication_name", "mix.ingredient_type", "med.ordering_date", "med.med_route", "med.number_of_doses","protocol_id","protocol_name","section_name","smart_group"];
        headers = ["order_med_id", "pat_id", "pat_enc_csn_id", "medication_id", "description", "ingredient_type", "ordering_date", "med_route", "number_of_doses","protocol_id","protocol_name","section_name","smart_group"];

        query = SQLQuery();
        for header in queryHeaders:
            query.addSelect( header );
        query.addFrom("stride_order_med as med left outer join stride_orderset_order_med as os on med.order_med_id = os.order_med_id"); # Grab order set links if they exist
        query.addFrom("stride_order_medmixinfo as mix");
        query.addWhere("med.order_med_id = mix.order_med_id");
        #query.addWhereEqual("med.medication_id", TEMPLATE_MEDICATION_ID );
        #query.addWhere("mix.line = 1"); # Just take the first item from a mix
        query.addWhere("freq_name not like '%%PRN'");   # Ignore PRN orders
        if convOptions.startDate is not None:
            query.addWhereOp("ordering_date",">=", convOptions.startDate);
        if convOptions.endDate is not None:
            query.addWhereOp("ordering_date","<", convOptions.endDate);
        query.addOrderBy("med.ordering_date, med.order_med_id, mix.line");

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        # Accumulate mixture components one item at a time
        mixByOrderMedId = dict();

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            orderMedId = rowModel["order_med_id"];
            if orderMedId not in mixByOrderMedId:  # New medication mix encountered.  Process any prior ones before moving on
                for normalizedModel in self.normalizeMixData(rxcuiDataByMedId, mixByOrderMedId, convOptions):
                    yield normalizedModel; # Yield one row worth of data at a time to avoid having to keep the whole result set in memory

                mixByOrderMedId.clear(); # Discard previously processed mixes so don't have a ton left in memory
                mixByOrderMedId[orderMedId] = list(); # Prep for next mix
            mixByOrderMedId[orderMedId].append(rowModel);
            row = cursor.fetchone();
        # One more pass for remaining items
        for normalizedModel in self.normalizeMixData(rxcuiDataByMedId, mixByOrderMedId, convOptions):
            yield normalizedModel; # Yield one row worth of data at a time to avoid having to keep the whole result set in memory

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();

    def normalizeMixData(self, rxcuiDataByMedId, mixByOrderMedId, convOptions):
        """Look through the mixture components to compile a consolidated set of medication data
        """
        for orderMedId, mixList in mixByOrderMedId.iteritems():
            mixSize = len(mixList);

            ingredientIds = set();
            ingredientList = list();
            for rowModel in mixList:
                #print >> sys.stderr, rowModel
                if mixSize == 2 and rowModel["ingredient_type"] == "Base":
                    # Mixture of two ingredients where one is just a base (usually NS or D5W), ignore the base ingredient
                    # Misses edge case where both ingredients are "bases" though that appears to only represent ~18 items out of ~421K med mixes
                    pass;
                else:
                    # Pull out fully normalized component ingredients first
                    subConvOptions = ConversionOptions();
                    subConvOptions.normalizeMixtures = True;
                    subConvOptions.includeRouteInDescription = False;
                    for ingredientModel in self.normalizeMedIngredients(rxcuiDataByMedId, rowModel, subConvOptions):
                        medId = ingredientModel["medication_id"];
                        if medId not in ingredientIds:
                            ingredientList.append(ingredientModel);
                            ingredientIds.add(medId);   # Avoid adding duplicates

            ingredientCount = len(ingredientList);
            if ingredientCount <= 1 or convOptions.normalizeMixtures:
                # Single ingredient or want component active ingredients to each have one record
                for ingredientModel in ingredientList:
                    ingredientModel["description"] += " (%s)" % (rowModel["med_route"]);
                    if convOptions.doseCountLimit is not None and ingredientModel["number_of_doses"] is not None:
                        if ingredientModel["number_of_doses"] < convOptions.doseCountLimit:
                            ingredientModel["code"] += " (<%d)" % convOptions.doseCountLimit;
                            ingredientModel["description"] += " (<%d doses)" % convOptions.doseCountLimit;
                    yield ingredientModel;
            elif convOptions.maxMixtureCount is None or ingredientCount <= convOptions.maxMixtureCount:
                # Composite into single denormalized item
                ingredientList.sort( RowItemFieldComparator("description") ); # Ensure stable sort order

                idStrList = list();
                descriptionList = list();
                for ingredientModel in ingredientList:
                    medId = ingredientModel["medication_id"];
                    idStrList.append(str(medId));
                    descriptionList.append(ingredientModel["description"]);
                idComposite = str.join(",", idStrList );
                descriptionComposite = str.join("-",descriptionList );

                # Build on last mix item's row model
                # Create arbitrary integer, hash to try to be unique
                # https://stackoverflow.com/questions/16008670/python-how-to-hash-a-string-into-8-digits
                number = int(hashlib.sha1(idComposite).hexdigest(), 16) % (10 ** 12)
                rowModel["medication_id"] = number
                rowModel["code"] = RXCUI_CODE_TEMPLATE % idComposite;
                # Hard to trace back to Order_Med.medication_id from here, since working with Order_Med_MixInfo records
                #rowModel["code"] = GENERIC_CODE_TEMPLATE % rowModel["medication_id"];
                rowModel["description"] = "%s (%s)" % (descriptionComposite, rowModel["med_route"]);

                if convOptions.doseCountLimit is not None and rowModel["number_of_doses"] is not None:
                    if rowModel["number_of_doses"] < convOptions.doseCountLimit:
                        rowModel["code"] += " (<%d)" % convOptions.doseCountLimit;
                        rowModel["description"] += " (<%d doses)" % convOptions.doseCountLimit;
                yield rowModel;
            else:   # ingredientCount > convOptions.maxMixtureCount.  Too many components, don't try to use mixture, defer to summary label
                pass;

    def normalizeMedData(self, rxcuiDataByMedId, rowModel, convOptions):
        """Normalize medication data by active ingredient mixtures and number of doses"""
        for rowModel in self.normalizeMedIngredients(rxcuiDataByMedId, rowModel, convOptions):
            if convOptions.doseCountLimit is not None and rowModel["number_of_doses"] is not None:
                if rowModel["number_of_doses"] < convOptions.doseCountLimit:
                    rowModel["code"] += " (<%d)" % convOptions.doseCountLimit;
                    rowModel["description"] += " (<%d doses)" % convOptions.doseCountLimit;
            yield rowModel;

    def normalizeMedIngredients(self, rxcuiDataByMedId, rowModel, convOptions):
        """Given a rowModel of medication data, normalize it further.
        Specifically, look for common active ingredients to simplify the data.
        If the medication is actually a compound of multiple active ingredients,
        then break out into active ingredients.

        If normalizeMixtures set, then will yield out multiple items to reflect each active ingredient.
        If normalizeMixtures not set, will yield a single item with name being a composite of the active ingredients.
        """
        medId = rowModel["medication_id"]

        if medId not in rxcuiDataByMedId:
            # No mapping entry found, just use the available generic medication data then
            rowModel["code"] = GENERIC_CODE_TEMPLATE % rowModel["medication_id"];
            yield rowModel;

        else:
            # Mapping entry found, yield a normalized model for each active ingredient found
            #   (will usually be a 1-to-1 relation, but sometimes multiple
            ingredientByRxcui = rxcuiDataByMedId[medId];
            if len(ingredientByRxcui) <= 1 or convOptions.normalizeMixtures:
                # Single ingredient or want component active ingredients to each have one record
                for (rxcui, ingredient) in ingredientByRxcui.iteritems():
                    # ~250/15000 RxCUI's don't have a defined active ingredient.
                    if ingredient is None:
                        continue

                    normalizedModel = RowItemModel(rowModel);
                    normalizedModel["medication_id"] = rxcui;
                    normalizedModel["code"] = RXCUI_CODE_TEMPLATE % normalizedModel["medication_id"];
                    normalizedModel["description"] = ingredient.title();
                    if convOptions.includeRouteInDescription:
                        normalizedModel["description"] += " (%s)" % (normalizedModel["med_route"]);

                    yield normalizedModel;
            else:
                # Mixture of multiple ingredients and want to keep denormalized
                # Extract out the active ingredient names to make a composite based only on that unique combination
                ingredientRxcuiList = [ (ingredient, rxcui) for (rxcui, ingredient) in ingredientByRxcui.iteritems()];
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

                #rowModel["medication_id"] = hash(tuple(rxcuiList));   # Arbitrary integer, hash to try to be unique
                #rowModel["code"] = RXCUI_CODE_TEMPLATE % rxcuiComposite;
                # Nah, just stick to medication_id instead of creating a new hash number
                rowModel["code"] = GENERIC_CODE_TEMPLATE % rowModel["medication_id"];
                rowModel["description"] = ingredientComposite;
                if convOptions.includeRouteInDescription:
                    rowModel["description"] += " (%s)" % (rowModel["med_route"]);
                yield rowModel;


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
        #   In this case, always Medication
        categoryDescription = CATEGORY_TEMPLATE % sourceItem["med_route"];
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
        else:
            # Clinical Item does exist, but check for redundancies and opportunities to
            #   simplify different descriptions for the same medication
            priorClinicalItem = self.clinicalItemByCategoryIdCode[clinicalItemKey];
            priorDescription = priorClinicalItem["description"];
            if sourceItem["description"] < priorDescription or priorDescription.startswith(TEMPLATE_MEDICATION_PREFIX):
                # Prior medication recorded description either a generic template,
                #   or a longer version than necessary, that can be replaced with the current one
                priorClinicalItem["description"] = sourceItem["description"];
                DBUtil.updateRow("clinical_item", priorClinicalItem, priorClinicalItem["clinical_item_id"], conn=conn);
        return self.clinicalItemByCategoryIdCode[clinicalItemKey];

    def patientItemFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id":  sourceItem["order_med_id"],
                    "patient_id":  sourceItem["pat_id"],
                    "encounter_id":  sourceItem["pat_enc_csn_id"],
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["ordering_date"],
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
        parser.add_option("-n", "--normalizeMixtures", dest="normalizeMixtures", action="store_true",  help="If set, when find medication mixtures, will unravel / normalize into separate entries, one for each ingredient");
        parser.add_option("-m", "--maxMixtureCount", dest="maxMixtureCount", help="If not normalizing mixtures, then this is the maximum number of mixture components will itemize for a mixture.  If more than this, just use the summary label.");
        parser.add_option("-d", "--doseCountLimit", dest="doseCountLimit", help="Medication orders with a finite number of doses specified less than this limit will be labeled as different items than those without a number specified, or whose number is >= to this limit.");
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
        self.doseCountLimit = None;
        self.includeRouteInDescription = True;

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

        if options.doseCountLimit is not None:
            self.doseCountLimit = int(options.doseCountLimit);

if __name__ == "__main__":
    instance = STRIDEOrderMedConversion();
    instance.main(sys.argv);
