#!/usr/bin/env python

import sys, os
import time
import csv

from itertools import islice
from datetime import datetime
from medinfo.common.Util import ProgressDots
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.db.Model import RowItemModel

from medinfo.dataconversion.Util import log
from medinfo.db.bigquery import bigQueryUtil

from google.cloud import bigquery

SOURCE_TABLE = 'starr_datalake2018.demographic'

UNSPECIFIED_RACE_ETHNICITY = ("Unknown", "Other")
HISPANIC_LATINO_ETHNICITY = "HISPANIC/LATINO"
RACE_MAPPINGS = \
    {
        None: "Unknown",
        "": "Unknown",
        "American Indian or Alaska Native": "Native American",
        "AMERICAN INDIAN OR ALASKA NATIVE": "Native American",
        "ASIAN - HISTORICAL CONV": "Asian",
        "Asian": "Asian",
        "ASIAN": "Asian",
        "ASIAN, HISPANIC": "Asian",
        "Asian, non-Hispanic": "Asian",
        "ASIAN, NON-HISPANIC": "Asian",
        "Black": "Black",
        "Black or African American": "Black",
        "BLACK OR AFRICAN AMERICAN": "Black",
        "Black, Hispanic": "Black",
        "BLACK, HISPANIC": "Black",
        "Black, non-Hispanic": "Black",
        "BLACK, NON-HISPANIC": "Black",
        "Native American": "Native American",
        "NATIVE AMERICAN, HISPANIC": "Native American",
        "Native American, non-Hispanic": "Native American",
        "NATIVE AMERICAN, NON-HISPANIC": "Native American",
        "Native Hawaiian or Other Pacific Islander": "Pacific Islander",
        "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER": "Pacific Islander",
        "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER ": "Pacific Islander",
        "Other": "Other",
        "OTHER": "Other",
        "Other, Hispanic": "Hispanic/Latino",
        "OTHER, HISPANIC": "Hispanic/Latino",
        "Other, non-Hispanic": "Other",
        "OTHER, NON-HISPANIC": "Other",
        "Pacific Islander": "Pacific Islander",
        "Pacific Islander, non-Hispanic": "Pacific Islander",
        "PACIFIC ISLANDER, NON-HISPANIC": "Pacific Islander",
        "Patient Refused": "Unknown",
        "PATIENT REFUSED": "Unknown",
        "Race and Ethnicity Unknown": "Unknown",
        "RACE AND ETHNICITY UNKNOWN": "Unknown",
        "Unknown": "Unknown",
        "UNKNOWN": "Unknown",
        "White": "White (%s)",
        "WHITE": "White (%s)",  # Subset by ethnicity Hispanic/Latino
        "White, Hispanic": "White (Hispanic/Latino)",
        "WHITE, HISPANIC": "White (Hispanic/Latino)",
        "White, non-Hispanic": "White (Non-Hispanic/Latino)",
        "WHITE, NON-HISPANIC": "White (Non-Hispanic/Latino)",
        HISPANIC_LATINO_ETHNICITY: "Hispanic/Latino"
    }


class STARRDemographicsConversion:
    """Data conversion module to take STARR provided patient demographics data
    into the structured data tables to facilitate subsequent analysis.

    Capturing death date for now as an event.
    """
    connFactory = None  # Allow specification of alternative DB connection source

    categoryBySourceDescr = None  # Local cache to track the clinical item category table contents
    clinicalItemByCategoryIdExtId = None  # Local cache to track clinical item table contents

    def __init__(self):
        """Default constructor"""
        self.bqConn = bigQueryUtil.connection()
        self.bqClient = bigQueryUtil.BigQueryClient()
        self.connFactory = DBUtil.ConnectionFactory()  # Default connection source

        self.categoryBySourceDescr = dict()
        self.clinicalItemByCategoryIdExtId = dict()

    def convertItemsByBatch(self, patientIdsFile, batchSize=10000, tempDir='/tmp/', removeCsvs=True,
                            datasetId='starr_datalake2018', skipFirstLine=True, startBatch=0):
        # split pat ids into blocks
        # for each split
        # convert to local postgres db
        # dump local postgres db to csv
        # upload csv to BQ clinical item
        # clean up

        log.info('Batch size is %s \n\n' % batchSize)

        def get_batch(input_file, num_lines):
            return [line.strip() for line in islice(input_file, num_lines)]

        with open(patientIdsFile, 'r') as f:
            if skipFirstLine:
                ignored_first_line = f.readline()

            batch_counter = 0

            # skip to required startBatch
            while batch_counter <= startBatch:
                ids_batch = get_batch(f, batchSize)
                batch_counter += 1

            while ids_batch:
                log.info('Processing batch %s' % batch_counter)
                log.info('Batch %s contains ids %s to %s' % (
                    batch_counter,
                    (batchSize * batch_counter + 1),
                    min(batchSize * (batch_counter + 1), batchSize * batch_counter + len(ids_batch))
                ))

                self.convertSourceItems(ids_batch)
                self.dumpPatientItemToCsv(tempDir, batch_counter)

                self.bqClient.reconnect_client() #refresh bq client connection
                self.uploadPatientItemCsvToBQ(tempDir, batch_counter, datasetId)

                if removeCsvs:
                    self.removePatientItemCsv(tempDir, batch_counter)

                self.removePatientItemAddedLines()

                log.info('Finished with batch %s \n\n' % batch_counter)
                ids_batch = get_batch(f, batchSize)
                batch_counter += 1

        # For now keep the clinical_* tables, upload them once all tables have been converted
        self.dumpClinicalTablesToCsv(tempDir)
        self.uploadClinicalTablesCsvToBQ(tempDir, datasetId)
        self.removeClinicalTablesCsv(tempDir)
        self.removeClinicalTablesAddedLines()

    def dumpPatientItemToCsv(self, tempDir, batchCounter):
        log.info('Dumping patient_item for batch %s to CSV' % batchCounter)

        DBUtil.execute(
            '''
            COPY patient_item TO '%s/%s_patient_item.csv' DELIMITER ',' CSV HEADER;
            ''' % (tempDir, batchCounter)
        )

    def dumpClinicalTablesToCsv(self, tempDir):
        log.info('Dumping clinical_item and clinical_item_category to CSV')

        DBUtil.execute(
            '''
            COPY clinical_item TO '%s/clinical_item.csv' DELIMITER ',' CSV HEADER;
            ''' % tempDir
        )

        DBUtil.execute(
            '''
            COPY clinical_item_category TO '%s/clinical_item_category.csv' DELIMITER ',' CSV HEADER;
            ''' % tempDir
        )

    def uploadPatientItemCsvToBQ(self, tempDir, batchCounter, datasetId):
        log.info('Uploading patient_item CSV to BQ dataset %s for batch %s' % (datasetId, batchCounter))

        patient_item_schema = self.bqClient.client.get_table(
                self.bqClient.client.dataset('clinical_item2018', 'mining-clinical-decisions').table('patient_item')
        ).schema

        csv_path = tempDir + '/' + str(batchCounter) + '_patient_item.csv'

        bigQueryUtil.headerChecker(csv_path, [sf.name for sf in patient_item_schema])

        self.bqClient.load_csv_to_table(datasetId, 'patient_item', csv_path, skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=patient_item_schema)

    def uploadClinicalTablesCsvToBQ(self, tempDir, datasetId):
        log.info('Uploading clinical_item_category CSV to BQ dataset %s' % datasetId)
        clinical_item_category_schema = self.bqClient.client.get_table(
                self.bqClient.client.dataset('clinical_item2018', 'mining-clinical-decisions')
                    .table('clinical_item_category')
        ).schema

        clinical_item_category_csv_path = tempDir + '/clinical_item_category.csv'

        bigQueryUtil.headerChecker(clinical_item_category_csv_path, [sf.name for sf in clinical_item_category_schema])

        self.bqClient.load_csv_to_table(datasetId, 'clinical_item_category', clinical_item_category_csv_path,
                                        skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=clinical_item_category_schema)

        log.info('Uploading clinical_item CSV to BQ dataset %s' % datasetId)
        clinical_item_schema = self.bqClient.client.get_table(
                self.bqClient.client.dataset('clinical_item2018', 'mining-clinical-decisions').table('clinical_item')
        ).schema

        clinical_item_csv_path = tempDir + '/clinical_item.csv'

        bigQueryUtil.headerChecker(clinical_item_csv_path, [sf.name for sf in clinical_item_schema])

        self.bqClient.load_csv_to_table(datasetId, 'clinical_item', clinical_item_csv_path,
                                        skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=clinical_item_schema)

    def removePatientItemCsv(self, tempDir, batchCounter):
        log.info('Removing patient_item CSV for batch %s' % batchCounter)
        if os.path.exists(tempDir + '/' + str(batchCounter) + '_patient_item.csv'):
            os.remove(tempDir + '/' + str(batchCounter) + '_patient_item.csv')
        else:
            print(tempDir + '/' + str(batchCounter) + '_patient_item.csv does not exist')

    def removeClinicalTablesCsv(self, tempDir):
        log.info('Removing clinical_item and clinical_item_category CSVs')
        if os.path.exists(tempDir + '/clinical_item.csv'):
            os.remove(tempDir + '/clinical_item.csv')
        else:
            print(tempDir + '/clinical_item.csv does not exist')

        if os.path.exists(tempDir + '/clinical_item_category.csv'):
            os.remove(tempDir + '/clinical_item_category.csv')
        else:
            print(tempDir + '/clinical_item_category.csv does not exist')

    def removePatientItemAddedLines(self):
        """delete added records"""
        log.info('Removing patient_item added lines in PSQL DB')

        DBUtil.execute(
            """delete from patient_item 
                where clinical_item_id in 
                (   select clinical_item_id
                    from clinical_item as ci, clinical_item_category as cic
                    where ci.clinical_item_category_id = cic.clinical_item_category_id
                    and cic.source_table = '%s'
                );
            """ % SOURCE_TABLE
        )

    def removeClinicalTablesAddedLines(self):
        """delete added records"""
        log.info('Removing clinical_item and clinical_item_category added lines in PSQL DB')

        DBUtil.execute(
            """delete from clinical_item 
                where clinical_item_category_id in 
                (   select clinical_item_category_id 
                    from clinical_item_category 
                    where source_table = '%s'
                );
                """ % SOURCE_TABLE
        )

        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % SOURCE_TABLE)

    def convertSourceItems(self, patientIds=None):
        """Primary run function to process the contents of the starr_datalake2018.demographic
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies to avoid repeating conversion.

        patientIds - If provided, only process items for patient IDs matching those provided
        """
        log.info("Conversion for patients starting with: %s, %s total" % (patientIds[:5], len(patientIds)))
        progress = ProgressDots()

        with self.connFactory.connection() as conn:
            category_model = self.categoryFromSourceItem(conn)   # only 1 category - no need to have it in the loop
            for sourceItem in self.querySourceItems(patientIds, progress):
                self.convertSourceItem(category_model, sourceItem, conn)

    def convertSourceItem(self, categoryModel, sourceItem, conn=None):
        """Given an individual sourceItem record, produce / convert it into an equivalent
        item record in the analysis database.
        """
        # Normalize sourceItem data into hierarchical components (category -> clinical_item -> patient_item).
        #   Relatively small / finite number of categories and clinical_items, so these should only have to be instantiated
        #   in a first past, with subsequent calls just yielding back in memory cached copies
        clinicalItemModel = self.clinicalItemFromSourceItem(sourceItem, categoryModel, conn)
        ignoredPatientItemModel = self.patientItemModelFromSourceItem(sourceItem, clinicalItemModel, conn)

    def querySourceItems(self, patientIds=None, progress=None, debug=False):
        """Query the database for list of all patient demographics
        and yield the results one at a time.  If patientIds provided, only return items
        matching those IDs.
        """
        # Column headers to query for that map to respective fields in analysis table
        headers = ["rit_uid", "birth_date_jittered", "gender", "death_date_jittered", "canonical_race",
                   "canonical_ethnicity"]

        '''
        query = SQLQuery()
        for header in headers:
            query.addSelect( header )
        query.addFrom(SOURCE_TABLE + " as dem")
        if patientIds is not None:
            query.addWhereIn("dem.rit_uid", patientIds)
        '''

        query = '''
                SELECT rit_uid,birth_date_jittered,gender,death_date_jittered,canonical_race,canonical_ethnicity
                FROM %s as dem
                WHERE dem.rit_uid IN UNNEST(@pat_ids)
                ORDER BY rit_uid;
                ''' % SOURCE_TABLE

        query_params = [
            bigquery.ArrayQueryParameter('pat_ids', 'STRING', patientIds)
        ]

        if debug:
            print(query)
            print(query_params)

        query_job = self.bqClient.queryBQ(str(query), query_params=query_params, location='US', batch_mode=False,
                                          verbose=True)

        previous_rit_uid = None
        rows_fetched = 0
        for row in query_job:  # API request - fetches results
            rows_fetched += 1
            # Row values can be accessed by field name or index
            # assert row[0] == row.name == row["name"]
            rowModel = RowItemModel(row.values(), headers)

            # skip this record if we already processed this rit_uid
            if rowModel["rit_uid"] == previous_rit_uid:
                continue

            if rowModel["birth_date_jittered"] is None:
                # Blank values, doesn't make sense.  Skip it
                log.warning(rowModel)
            else:
                # Record birth at resolution of year
                rowModel["itemDate"] = datetime(rowModel["birth_date_jittered"].year, 1, 1)
                rowModel["name"] = "Birth"
                rowModel["description"] = "Birth Year"
                yield rowModel

                # Record another at resolution of decade
                decade = (rowModel["birth_date_jittered"].year / 10) * 10
                rowModel["itemDate"] = datetime(rowModel["birth_date_jittered"].year, 1, 1)
                rowModel["name"] = "Birth%ds" % decade
                rowModel["description"] = "Birth Decade %ds" % decade
                yield rowModel

                # Summarize race and ethnicity information into single field of interest
                raceEthnicity = self.summarizeRaceEthnicity(rowModel["canonical_race"], rowModel["canonical_ethnicity"])
                rowModel["itemDate"] = datetime(rowModel["birth_date_jittered"].year, 1, 1)
                rowModel["name"] = "Race" + (raceEthnicity.translate(None, " ()-/"))  # Strip off punctuation
                rowModel["description"] = "Race/Ethnicity: %s" % raceEthnicity
                yield rowModel

                gender = rowModel["gender"].title()
                rowModel["name"] = gender
                rowModel["description"] = "%s Gender" % gender
                yield rowModel

                if rowModel["death_date_jittered"] is not None:
                    rowModel["name"] = "Death"
                    rowModel["description"] = "Death Date"
                    rowModel["itemDate"] = rowModel["death_date_jittered"]
                    yield rowModel

            previous_rit_uid = rowModel["rit_uid"]

            progress.Update()

        log.debug("fetched {} rows".format(rows_fetched))

    def summarizeRaceEthnicity(self, canonical_race, canonical_ethnicity):
        """Given row model with patient information, return a single string to summarize the patient's race and ethnicity information"""
        race_ethnicity = RACE_MAPPINGS[canonical_race]
        if race_ethnicity in UNSPECIFIED_RACE_ETHNICITY and canonical_ethnicity == HISPANIC_LATINO_ETHNICITY:
            race_ethnicity = RACE_MAPPINGS[
                HISPANIC_LATINO_ETHNICITY]  # Use Hispanic/Latino as basis if no other information
        if race_ethnicity.find("%s") >= 0:  # Found replacement string.  Look to ethnicity for more information
            if canonical_ethnicity == HISPANIC_LATINO_ETHNICITY:
                race_ethnicity = race_ethnicity % RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY]
            else:
                race_ethnicity = race_ethnicity % ("Non-" + RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY])
        return race_ethnicity

    def categoryFromSourceItem(self, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        category_key = (SOURCE_TABLE, "Demographics")
        if category_key not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = \
                RowItemModel({
                    "source_table": SOURCE_TABLE,
                    "description": "Demographics",
                })

            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn)
            category["clinical_item_category_id"] = categoryId
            self.categoryBySourceDescr[category_key] = category
        return self.categoryBySourceDescr[category_key]

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["name"])
        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel({
                    "clinical_item_category_id": category["clinical_item_category_id"],
                    "external_id": None,
                    "name": sourceItem["name"],
                    "description": sourceItem["description"],
                })
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn)
            clinicalItem["clinical_item_id"] = clinicalItemId
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey]

    def patientItemModelFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patient_item = \
            RowItemModel({
                "external_id": None,
                "patient_id": int(sourceItem["rit_uid"][2:], 16),
                "encounter_id": None,
                "clinical_item_id": clinicalItem["clinical_item_id"],
                "item_date": str(sourceItem["itemDate"])      # without str(), the time is being converted in postgres
            })
        insert_query = DBUtil.buildInsertQuery("patient_item", patient_item.keys())
        insert_params = patient_item.values()
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute(insert_query, insert_params, conn=conn)
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
            log.warn(err)
