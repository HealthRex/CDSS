#!/usr/bin/env python

import sys, os
import time
from datetime import datetime
from medinfo.common.Util import ProgressDots
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.db.Model import RowItemModel

from scripts.GoogleCloud.BQ.BigQueryConnect_py2 import BigQueryConnect

from medinfo.dataconversion.Util import log

from google.cloud import bigquery

SOURCE_TABLE = "stride_patient"

UNSPECIFIED_RACE_ETHNICITY = ("Unknown","Other")
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
    """Data conversion module to take STRIDE provided patient demographics data
    into the structured data tables to facilitate subsequent analysis.

    Capturing death date for now as an event.
    """
    connFactory = None # Allow specification of alternative DB connection source

    categoryBySourceDescr = None   # Local cache to track the clinical item category table contents
    clinicalItemByCategoryIdExtId = None   # Local cache to track clinical item table contents

    def __init__(self):
        """Default constructor"""
        self.bqconn = BigQueryConnect()
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

        self.categoryBySourceDescr = dict()
        self.clinicalItemByCategoryIdExtId = dict()

    def convertSourceItems(self, patientIds=None):
        """Primary run function to process the contents of the stride_patient
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies to avoid repeating conversion.

        patientIds - If provided, only process items for patient IDs matching those provided
        """
        log.info("Conversion for patients: %s" % patientIds)
        progress = ProgressDots()

        with self.connFactory.connection() as conn:
            for sourceItem in self.querySourceItems(patientIds, progress=progress):
                self.convertSourceItem(sourceItem, conn=conn)

    def convertSourceItem(self, sourceItem, conn=None):
        """Given an individual sourceItem record, produce / convert it into an equivalent
        item record in the analysis database.
        """
        # Normalize sourceItem data into hierachical components (category -> clinical_item -> patient_item).
        #   Relatively small / finite number of categories and clinical_items, so these should only have to be instantiated
        #   in a first past, with subsequent calls just yielding back in memory cached copies
        categoryModel = self.categoryFromSourceItem(sourceItem, conn=conn)
        clinicalItemModel = self.clinicalItemFromSourceItem(sourceItem, categoryModel, conn=conn)
        patientItemModel = self.patientItemModelFromSourceItem(sourceItem, clinicalItemModel, conn=conn)

    def querySourceItems(self, patientIds=None, progress=None, debug=False):
        """Query the database for list of all patient demographics
        and yield the results one at a time.  If patientIds provided, only return items
        matching those IDs.
        """
        # Column headers to query for that map to respective fields in analysis table
        headers = ["rit_uid","birth_date_jittered","gender","death_date_jittered","canonical_race","canonical_ethnicity"]

        # TODO need to fix for BQ SQL
        '''
        query = SQLQuery()
        for header in headers:
            query.addSelect( header )
        query.addFrom("starr_datalake2018.demographic as dem")
        if patientIds is not None:
            query.addWhereIn("dem.rit_uid", patientIds)
        '''

        query = '''
                SELECT rit_uid,birth_date_jittered,gender,death_date_jittered,canonical_race,canonical_ethnicity
                FROM starr_datalake2018.demographic as dem
                WHERE dem.rit_uid IN UNNEST(@pat_ids)
                '''

        query_params = [
            bigquery.ArrayQueryParameter('pat_ids', 'STRING', patientIds),
        ]

        if debug:
            print(query)
            print(query_params)

        query_job = self.bqconn.queryBQ(str(query), query_params=query_params, location='US', batch_mode=False, verbose=True)

        if debug:
            for row in query_job:
                print(row)

        for row in query_job:  # API request - fetches results
            # Row values can be accessed by field name or index
            # assert row[0] == row.name == row["name"]
            rowModel = RowItemModel( row.values(), headers )

            if rowModel["birth_date_jittered"] is None:
                # Blank values, doesn't make sense.  Skip it
                log.warning(rowModel)
            else:
                # Record birth at resolution of year
                rowModel["itemDate"] = datetime(rowModel["birth_date_jittered"].year,1,1)
                rowModel["name"] = "Birth"
                rowModel["description"] = "Birth Year"
                yield rowModel

                # Record another at resolution of decade
                decade = (rowModel["birth_date_jittered"].year / 10) * 10
                rowModel["itemDate"] = datetime(rowModel["birth_date_jittered"].year,1,1)
                rowModel["name"] = "Birth%ds" % decade
                rowModel["description"] = "Birth Decade %ds" % decade
                yield rowModel

                # Summarize race and ethnicity information into single field of interest
                raceEthnicity = self.summarizeRaceEthnicity(rowModel)
                rowModel["itemDate"] = datetime(rowModel["birth_date_jittered"].year,1,1)
                rowModel["name"] = "Race"+(raceEthnicity.translate(None," ()-/"))   # Strip off punctuation
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

            progress.Update()


    def summarizeRaceEthnicity(self, rowModel):
        """Given row model with patient information, return a single string to summarize the patient's race and ethnicity information"""
        raceEthnicity = RACE_MAPPINGS[rowModel["canonical_race"]]
        if raceEthnicity in UNSPECIFIED_RACE_ETHNICITY and rowModel["canonical_ethnicity"] == HISPANIC_LATINO_ETHNICITY:
            raceEthnicity = RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY]   # Use Hispanic/Latino as basis if no other information
        if raceEthnicity.find("%s") >= 0:    # Found replacement string.  Look to ethnicity for more information
            if rowModel["canonical_ethnicity"] == HISPANIC_LATINO_ETHNICITY:
                raceEthnicity = raceEthnicity % RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY]
            else:
                raceEthnicity = raceEthnicity % ("Non-"+RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY])
        return raceEthnicity

    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        categoryKey = (SOURCE_TABLE, "Demographics")
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = \
                RowItemModel \
                    ({"source_table": SOURCE_TABLE,
                      "description": "Demographics",
                      }
                     )
            
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn)
            category["clinical_item_category_id"] = categoryId
            self.categoryBySourceDescr[categoryKey] = category
        return self.categoryBySourceDescr[categoryKey]

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["name"])
        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel \
                    ({"clinical_item_category_id": category["clinical_item_category_id"],
                      "external_id": None,
                      "name": sourceItem["name"],
                      "description": sourceItem["description"],
                      }
                     )
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn)
            clinicalItem["clinical_item_id"] = clinicalItemId
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey]

    def patientItemModelFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
                ({"external_id": None,
                  "patient_id": int(sourceItem["rit_uid"][2:], 16),
                  "encounter_id": None,
                  "clinical_item_id": clinicalItem["clinical_item_id"],
                  "item_date": sourceItem["itemDate"],
                  }
                 )
        insertQuery = DBUtil.buildInsertQuery("patient_item", patientItem.keys())
        insertParams = patientItem.values()
        try:
            # Optimistic insert of a new unique item
            DBUtil.execute(insertQuery, insertParams, conn=conn)
        except conn.IntegrityError, err:
            # If turns out to be a duplicate, okay, just note it and continue to insert whatever else is possible
            log.info(err);