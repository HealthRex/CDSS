#!/usr/bin/env python
import sys, os
import hashlib
import time
from datetime import datetime
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList, RowItemFieldComparator

from medinfo.dataconversion.Util import log
from medinfo.dataconversion.Const import TEMPLATE_MEDICATION_ID, TEMPLATE_MEDICATION_PREFIX
from medinfo.dataconversion.Const import COLLECTION_TYPE_ORDERSET
from medinfo.dataconversion.Env import DATE_FORMAT

from medinfo.db.bigquery import bigQueryUtil
from medinfo.dataconversion.starr_conv import STARRUtil

from google.cloud import bigquery

SOURCE_TABLE = "starr_datalake2018.order_med"
ORDERSET_TABLE = "starr_datalake2018.med_orderset"

CATEGORY_TEMPLATE = "Med ({}) ({})"     # For this data source, item category will be a Medication subscripted by medication route
GENERIC_CODE_TEMPLATE = "MED{}"         # Template for generic medication code reference if detailed RXCUI values not available
RXCUI_CODE_TEMPLATE = "RXCUI{}"         # Template for medication code references when detailed RXCUI values available


class STARROrderMedConversion:
    """Data conversion module to take STARR provided computerized physician order entry data
    (medications specifically)
    into the structured data analysis tables to facilitate subsequent analysis.

    For combination medications (usually same medication but with "1.5x" dosing like
    Metoprolol 75mg ordered as combination of 50mg + 25mg tabs), just record as the
    first component in the mixture.

    Ignore PRN orders for now to simplify data set and focus on standing orders.
    """

    def __init__(self):
        """Default constructor"""
        self.bqConn = bigQueryUtil.connection()
        self.bqClient = bigQueryUtil.BigQueryClient()
        self.connFactory = DBUtil.ConnectionFactory()   # Default connection source, but Allow specification of alternative DB connection source

        self.categoryBySourceDescr = dict()     # Local cache to track the clinical item category table contents
        self.clinicalItemByCategoryIdCode = dict()  # Local cache to track clinical item table contents
        self.itemCollectionByKeyStr = dict()    # Local cache to track item collections
        self.itemCollectionItemByCollectionIdItemId = dict()    # Local cache to track item collection items

    def convertAndUpload(self, convOptions, tempDir='/tmp/', removeCsvs=True, target_dataset_id='starr_datalake2018'):
        """
        Wrapper around primary run function, does conversion locally and uploads to BQ
        No batching done for treatment team since converted table is small
        """
        starrUtil = STARRUtil.StarrCommonUtils(self.bqClient)
        self.convertSourceItems(convOptions)

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

    def convertSourceItems(self, convOptions):
        """Primary run function to process the contents of the order_med
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies after the fact to catch repeatEd conversions.

        startDate - If provided, only return items whose order_time_jittered is on or after that date.
        endDate - If provided, only return items whose order_time_jittered is before that date.
        """
        log.info("Conversion for items dated {} to {}".format(convOptions.startDate, convOptions.endDate))
        progress = ProgressDots()
        conn = self.connFactory.connection()
        try:
            # Load up the medication mapping table to facilitate subsequent conversions
            rxcuiDataByMedId = self.loadRXCUIData()

            # Next round for medications directly from order_med table not addressed in medmix
            for sourceItem in self.querySourceItems(rxcuiDataByMedId, convOptions, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn)
                progress.Update()

        finally:
            conn.close()
        progress.PrintStatus()

    def loadRXCUIData(self):
        """Load up the full contents of the stride_mapped_meds table into
        memory (only a few thousand records) to facilitate rapid lookup resolution
        of common medication ingredient data.
        """
        rxcuiDataByMedId = dict()

        query = \
            """select medication_id, rxcui, active_ingredient
            from starr_datalake2018.mapped_meds
            """

        query_job = self.bqClient.queryBQ(query, verbose=True)

        for row in query_job:  # API request - fetches results
            (medId, rxcui, ingredient) = row    # Unpack the data tuple
            if medId not in rxcuiDataByMedId:
                rxcuiDataByMedId[medId] = dict()
            rxcuiDataByMedId[medId][rxcui] = ingredient

        return rxcuiDataByMedId

    def querySourceItems(self, rxcuiDataByMedId, convOptions, progress=None, conn=None):
        """Query the database for list of all source clinical items (medications, etc.)
        and yield the results one at a time.  If startDate provided, only return items whose
        order_time_jittered is on or after that date.
        """
        # Column headers to query for that map to respective fields in analysis table
        queryHeaders = ["med.order_med_id_coded", "jc_uid", "med.pat_enc_csn_id_coded", "med.medication_id",
                        "med.med_description", "order_time_jittered", "med_route", "number_of_times", "protocol_id",
                        "protocol_name", "ss_section_id", "ss_section_name", "ss_sg_key", "ss_sg_name", "ordering_mode"]

        headers = ["order_med_id_coded", "jc_uid", "pat_enc_csn_id_coded", "medication_id",
                   "med_description", "order_time_jittered", "med_route", "number_of_times", "protocol_id",
                   "protocol_name", "ss_section_id", "ss_section_name", "ss_sg_key", "ss_sg_name", "ordering_mode"]

        # TODO original query - need to figure out how to pass date to query in BQ using SQLQuery object
        # query = SQLQuery()
        # for header in queryHeaders:
        #     query.addSelect(header)
        # query.addFrom("stride_order_med as med left outer join stride_orderset_order_med as os on med.order_med_id = os.order_med_id")  # Grab order set links if they exist
        # query.addWhere("med.medication_id <> %s" % TEMPLATE_MEDICATION_ID)
        # query.addWhere("freq_name not like '%%PRN'")    # Ignore PRN orders
        # if convOptions.startDate is not None:
        #     query.addWhereOp("ordering_date",">=", convOptions.startDate)
        # if convOptions.endDate is not None:
        #     query.addWhereOp("ordering_date","<", convOptions.endDate)

        query = "SELECT {} FROM {} as med left outer join {} as os on med.order_med_id_coded = os.order_med_id_coded".format(', '.join(queryHeaders), SOURCE_TABLE, ORDERSET_TABLE)

        # TODO only 20 records with medication_id = TEMPLATE_MEDICATION_ID (whereas stride has 67041 such rows)
        query += " where med.medication_id <> {}".format(TEMPLATE_MEDICATION_ID)
        query += " and (freq_name is NULL or freq_name not like '%PRN')"    # Ignore PRN orders
        if convOptions.startDate is not None:
            query += " and order_time_jittered >= @startDate"
        if convOptions.endDate is not None:
            query += " and order_time_jittered < @endDate"
        query += " order by med.order_med_id_coded, jc_uid, med.pat_enc_csn_id_coded, med.medication_id"
        query += ';'

        query_params = [
            bigquery.ScalarQueryParameter(
                'startDate',
                'DATETIME',
                convOptions.startDate,
            ),
            bigquery.ScalarQueryParameter(
                'endDate',
                'DATETIME',
                convOptions.endDate,
            )
        ]

        # TODO Query to get an estimate of how long the process will be
        # if progress is not None:
        #     progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0]

        query_job = self.bqClient.queryBQ(query, query_params=query_params, verbose=True)

        for row in query_job:  # API request - fetches results
            rowModel = RowItemModel(row.values(), headers)
            log.debug("rowModel: {}".format(rowModel))
            for normalizedModel in self.normalizeMedData(rxcuiDataByMedId, rowModel, convOptions):
                yield normalizedModel  # Yield one row worth of data at a time to avoid having to keep the whole result set in memory

    def normalizeMedData(self, rxcuiDataByMedId, rowModel, convOptions):
        """Normalize medication data by active ingredient mixtures and number of doses"""
        for rowModel in self.normalizeMedIngredients(rxcuiDataByMedId, rowModel, convOptions):
            if convOptions.doseCountLimit is not None and rowModel["number_of_times"] is not None:
                if rowModel["number_of_times"] < convOptions.doseCountLimit:
                    rowModel["code"] += " (<{})".format(convOptions.doseCountLimit)
                    rowModel["med_description"] += " (<{} doses)".format(convOptions.doseCountLimit)
            yield rowModel

    @staticmethod
    def normalizeMedIngredients(rxcuiDataByMedId, rowModel, convOptions):
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
            rowModel["code"] = GENERIC_CODE_TEMPLATE.format(rowModel["medication_id"])
            yield rowModel

        else:
            # Mapping entry found, yield a normalized model for each active ingredient found
            #   (will usually be a 1-to-1 relation, but sometimes multiple
            ingredientByRxcui = rxcuiDataByMedId[medId]
            if len(ingredientByRxcui) <= 1 or convOptions.normalizeMixtures:
                # Single ingredient or want component active ingredients to each have one record
                for (rxcui, ingredient) in ingredientByRxcui.iteritems():
                    # ~250/15000 RxCUI's don't have a defined active ingredient.
                    if ingredient is None:
                        # No mapping entry found, just use the available generic medication data then
                        rowModel["code"] = GENERIC_CODE_TEMPLATE.format(rowModel["medication_id"])
                        yield rowModel
                    else:
                        normalizedModel = RowItemModel(rowModel)
                        normalizedModel["medication_id"] = rxcui
                        normalizedModel["code"] = RXCUI_CODE_TEMPLATE.format(normalizedModel["medication_id"])
                        normalizedModel["med_description"] = ingredient.title()
                        if convOptions.includeRouteInDescription:
                            normalizedModel["med_description"] += " {}".format(normalizedModel["med_route"])

                        yield normalizedModel
            else:
                # Mixture of multiple ingredients and want to keep denormalized
                # Extract out the active ingredient names to make a composite based only on that unique combination
                ingredientRxcuiList = [(ingredient, rxcui) for (rxcui, ingredient) in ingredientByRxcui.iteritems()]
                ingredientRxcuiList.sort()    # Ensure consistent order

                rxcuiStrList = list()
                ingredientList = list()
                for (ingredient, rxcui) in ingredientRxcuiList:
                    # ~250/15000 RxCUI's don't have a defined active ingredient.
                    if ingredient is None:
                        continue
                    rxcuiStrList.append(str(rxcui))
                    ingredientList.append(ingredient.title())
                rxcuiComposite = str.join(",", rxcuiStrList)
                ingredientComposite = str.join("-", ingredientList)

                #rowModel["medication_id"] = hash(tuple(rxcuiList))    # Arbitrary integer, hash to try to be unique
                #rowModel["code"] = RXCUI_CODE_TEMPLATE.format(rxcuiComposite)
                # Nah, just stick to medication_id instead of creating a new hash number
                rowModel["code"] = GENERIC_CODE_TEMPLATE.format(rowModel["medication_id"])
                rowModel["med_description"] = ingredientComposite
                if convOptions.includeRouteInDescription:
                    rowModel["med_description"] += " {}".format(rowModel["med_route"])
                yield rowModel

    def convertSourceItem(self, sourceItem, conn=None):
        """Given an individual sourceItem record, produce / convert it into an equivalent
        item record in the analysis database.
        """
        extConn = conn is not None
        if not extConn:
            conn = self.connFactory.connection()
        try:
            # Normalize sourceItem data into hierarchical components (category -> clinical_item -> patient_item).
            #   Relatively small / finite number of categories and clinical_items, so these should only have to be instantiated
            #   in a first pass, with subsequent calls just yielding back in memory cached copies
            category = self.categoryFromSourceItem(sourceItem, conn=conn)
            clinicalItem = self.clinicalItemFromSourceItem(sourceItem, category, conn=conn)
            patientItem = self.patientItemFromSourceItem(sourceItem, clinicalItem, conn=conn)

            if sourceItem["protocol_id"] is not None:
                # Similarly build up item collection (order set) hierarchy and link
                itemCollection = self.itemCollectionFromSourceItem(sourceItem, conn=conn)
                itemCollectionItem = self.itemCollectionItemFromSourceItem(sourceItem, itemCollection, clinicalItem, conn=conn)
                patientItemCollectionLink = self.patientItemCollectionLinkFromSourceItem(sourceItem, itemCollectionItem, patientItem, conn=conn)

        finally:
            if not extConn:
                conn.close()

    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        #   In this case, always Medication
        categoryDescription = CATEGORY_TEMPLATE.format(sourceItem["med_route"], sourceItem["ordering_mode"])
        categoryKey = (SOURCE_TABLE, categoryDescription)
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = RowItemModel(
                {
                    "source_table":  SOURCE_TABLE,
                    "description":  categoryDescription,
                }
            )
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn)
            category["clinical_item_category_id"] = categoryId
            self.categoryBySourceDescr[categoryKey] = category
        return self.categoryBySourceDescr[categoryKey]

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["code"])
        if clinicalItemKey not in self.clinicalItemByCategoryIdCode:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = RowItemModel(
                {
                    "clinical_item_category_id": category["clinical_item_category_id"],
                    "external_id": sourceItem["medication_id"],
                    "name": sourceItem["code"],
                    "description": sourceItem["med_description"],
                }
            )
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn)
            clinicalItem["clinical_item_id"] = clinicalItemId
            self.clinicalItemByCategoryIdCode[clinicalItemKey] = clinicalItem
        else:
            # Clinical Item does exist, but check for redundancies and opportunities to
            #   simplify different descriptions for the same medication
            priorClinicalItem = self.clinicalItemByCategoryIdCode[clinicalItemKey]
            priorDescription = priorClinicalItem["description"]
            if len(sourceItem["med_description"]) < len(priorDescription) or priorDescription.startswith(TEMPLATE_MEDICATION_PREFIX):
                # Prior medication recorded description either a generic template,
                #   or a longer version than necessary, that can be replaced with the current one
                priorClinicalItem["description"] = sourceItem["med_description"]
                DBUtil.updateRow("clinical_item", priorClinicalItem, priorClinicalItem["clinical_item_id"], conn=conn)
        return self.clinicalItemByCategoryIdCode[clinicalItemKey]

    def patientItemFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = RowItemModel(
            {
                "external_id": sourceItem["order_med_id_coded"],
                "patient_id": int(sourceItem["jc_uid"][2:], 16),
                "encounter_id": sourceItem["pat_enc_csn_id_coded"],
                "clinical_item_id": clinicalItem["clinical_item_id"],
                "item_date": sourceItem["order_time_jittered"],
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
            log.info(err)    # Lookup just by the composite key components to avoid attempting duplicate insertion again
            searchPatientItem = {
                "patient_id":       patientItem["patient_id"],
                "clinical_item_id": patientItem["clinical_item_id"],
                "item_date":        patientItem["item_date"],
            }
            (patientItem["patient_item_id"], isNew) = DBUtil.findOrInsertItem("patient_item", searchPatientItem, conn=conn)
        return patientItem

    def itemCollectionFromSourceItem(self, sourceItem, conn):
        # Load or produce an item_collection record model for the given sourceItem
        if sourceItem["protocol_id"] is None:
            # No order set link to this item, so nothing to return
            return None

        key = {
            "protocol_id": sourceItem["protocol_id"],
            "ss_section_id": sourceItem["ss_section_id"],
            "ss_sg_key": sourceItem["ss_sg_key"].strip().upper() if sourceItem["ss_section_name"] is not None else None
        }

        collection_key = "%(protocol_id)d-%(ss_section_id)d-%(ss_sg_key)s" % key
        if collection_key not in self.itemCollectionByKeyStr:
            # Collection does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            collection = RowItemModel(
                {
                    "external_id": sourceItem["protocol_id"],
                    "name": sourceItem["protocol_name"],
                    "section": sourceItem["ss_section_name"],
                    "subgroup": sourceItem["ss_sg_name"],
                }
            )
            (collectionId, isNew) = DBUtil.findOrInsertItem("item_collection", collection, conn=conn)
            collection["item_collection_id"] = collectionId
            self.itemCollectionByKeyStr[collection_key] = collection
        return self.itemCollectionByKeyStr[collection_key]

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
                "item_collection_item_id": collectionItem["item_collection_item_id"],
            }
        )
        insertQuery = DBUtil.buildInsertQuery("patient_item_collection_link", patientItemCollectionLink.keys())
        insertParams = patientItemCollectionLink.values()
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute(insertQuery, insertParams, conn=conn)
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
            log.info(err)

    def main(self, argv):
        """Main method, callable from command line"""
        usage_str = "usage: %prog [options]\n"
        parser = OptionParser(usage=usage_str)
        parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time on or after this date.")
        parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time before this date.")
        parser.add_option("-n", "--normalizeMixtures", dest="normalizeMixtures", action="store_true",  help="If set, when find medication mixtures, will unravel / normalize into separate entries, one for each ingredient")
        parser.add_option("-m", "--maxMixtureCount", dest="maxMixtureCount", help="If not normalizing mixtures, then this is the maximum number of mixture components will itemize for a mixture.  If more than this, just use the summary label.")
        parser.add_option("-d", "--doseCountLimit", dest="doseCountLimit", help="Medication orders with a finite number of doses specified less than this limit will be labeled as different items than those without a number specified, or whose number is >= to this limit. Intended to distinguish things like IV single bolus / use vs. continuous infusions and standing medication orders")
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: " + str.join(" ", argv))
        timer = time.time()

        conv_options = ConversionOptions()
        conv_options.extract_parser_options(options)

        self.convertSourceItems(conv_options)

        timer = time.time() - timer
        log.info("%.3f seconds to complete", timer)


class ConversionOptions:
    """Simple struct to contain multiple program options"""
    def __init__(self):
        self.startDate = None
        self.endDate = None
        self.normalizeMixtures = False
        self.maxMixtureCount = None
        self.doseCountLimit = None
        self.includeRouteInDescription = True

    def extract_parser_options(self, options):
        if options.startDate is not None:
            # Parse out the start date parameter
            time_tuple = time.strptime(options.startDate, DATE_FORMAT)
            self.startDate = datetime(*time_tuple[0:3])

        if options.endDate is not None:
            # Parse out the end date parameter
            time_tuple = time.strptime(options.endDate, DATE_FORMAT)
            self.endDate = datetime(*time_tuple[0:3])

        if options.maxMixtureCount is not None:
            self.maxMixtureCount = int(options.maxMixtureCount)

        if options.doseCountLimit is not None:
            self.doseCountLimit = int(options.doseCountLimit)


if __name__ == "__main__":
    instance = STARROrderMedConversion()
    instance.main(sys.argv)
