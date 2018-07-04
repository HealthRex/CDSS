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

SOURCE_TABLE = "stride_patient";

UNSPECIFIED_RACE_ETHNICITY = ("Unknown","Other");
HISPANIC_LATINO_ETHNICITY = "HISPANIC/LATINO";
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

class STRIDEDemographicsConversion:
    """Data conversion module to take STRIDE provided patient demographics data
    into the structured data tables to facilitate subsequent analysis.

    Capturing death date for now as an event.  Should eventually incorporate
    patient age and gender into data, though less clear what item event date
    to assign to these to make them useful.
    """
    connFactory = None; # Allow specification of alternative DB connection source

    categoryBySourceDescr = None;   # Local cache to track the clinical item category table contents
    clinicalItemByCategoryIdExtId = None;   # Local cache to track clinical item table contents

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

        self.categoryBySourceDescr = dict();
        self.clinicalItemByCategoryIdExtId = dict();

    def convertSourceItems(self, patientIds=None):
        """Primary run function to process the contents of the stride_patient
        table and convert them into equivalent patient_item, clinical_item, and clinical_item_category entries.
        Should look for redundancies to avoid repeating conversion.

        patientIds - If provided, only process items for patient IDs matching those provided
        """
        log.info("Conversion for patients: %s" % patientIds);
        progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            for sourceItem in self.querySourceItems(patientIds, progress=progress, conn=conn):
                self.convertSourceItem(sourceItem, conn=conn);
        finally:
            conn.close();
        # progress.PrintStatus();


    def querySourceItems(self, patientIds=None, progress=None, conn=None):
        """Query the database for list of all patient demographics
        and yield the results one at a time.  If patientIds provided, only return items
        matching those IDs.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        headers = ["pat_id","birth_year","gender","death_date","race","ethnicity"];

        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom("stride_patient as sp");
        if patientIds is not None:
            query.addWhereIn("sp.pat_id", patientIds);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );

            if rowModel["birth_year"] is None:
                # Blank values, doesn't make sense.  Skip it
                log.warning(rowModel);
            else:
                # Record birth at resolution of year
                rowModel["itemDate"] = datetime(rowModel["birth_year"],1,1);
                rowModel["name"] = "Birth";
                rowModel["description"] = "Birth Year";
                yield rowModel;

                # Record another at resolution of decade
                decade = (rowModel["birth_year"] / 10) * 10;
                rowModel["itemDate"] = datetime(rowModel["birth_year"],1,1);
                rowModel["name"] = "Birth%ds" % decade;
                rowModel["description"] = "Birth Decade %ds" % decade;
                yield rowModel;

                # Summarize race and ethnicity information into single field of interest
                raceEthnicity = self.summarizeRaceEthnicity(rowModel);
                rowModel["itemDate"] = datetime(rowModel["birth_year"],1,1);
                rowModel["name"] = "Race"+(raceEthnicity.translate(None," ()-/"));   # Strip off punctuation
                rowModel["description"] = "Race/Ethnicity: %s" % raceEthnicity;
                yield rowModel;


                gender = rowModel["gender"].title();
                rowModel["name"] = gender;
                rowModel["description"] = "%s Gender" % gender;
                yield rowModel;

                if rowModel["death_date"] is not None:
                    rowModel["name"] = "Death";
                    rowModel["description"] = "Death Date";
                    rowModel["itemDate"] = rowModel["death_date"];
                    yield rowModel;

            row = cursor.fetchone();
            progress.Update();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();

    def summarizeRaceEthnicity(self, rowModel):
        """Given row model with patient information, return a single string to summarize the patient's race and ethnicity information"""
        raceEthnicity = RACE_MAPPINGS[rowModel["race"]];
        if raceEthnicity in UNSPECIFIED_RACE_ETHNICITY and rowModel["ethnicity"] == HISPANIC_LATINO_ETHNICITY:
            raceEthnicity = RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY];   # Use Hispanic/Latino as basis if no other information
        if raceEthnicity.find("%s") >= 0:    # Found replacement string.  Look to ethnicity for more information
            if rowModel["ethnicity"] == HISPANIC_LATINO_ETHNICITY:
                raceEthnicity = raceEthnicity % RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY];
            else:
                raceEthnicity = raceEthnicity % ("Non-"+RACE_MAPPINGS[HISPANIC_LATINO_ETHNICITY]);
        return raceEthnicity;


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
            clinicalItemModel = self.clinicalItemFromSourceItem(sourceItem, categoryModel, conn=conn);
            patientItemModel = self.patientItemModelFromSourceItem(sourceItem, clinicalItemModel, conn=conn);

        finally:
            if not extConn:
                conn.close();

    def categoryFromSourceItem(self, sourceItem, conn):
        # Load or produce a clinical_item_category record model for the given sourceItem
        categoryKey = (SOURCE_TABLE, "Demographics");
        if categoryKey not in self.categoryBySourceDescr:
            # Category does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            category = \
                RowItemModel \
                (   {   "source_table":  SOURCE_TABLE,
                        "description":  "Demographics",
                    }
                );
            (categoryId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", category, conn=conn);
            category["clinical_item_category_id"] = categoryId;
            self.categoryBySourceDescr[categoryKey] = category;
        return self.categoryBySourceDescr[categoryKey];

    def clinicalItemFromSourceItem(self, sourceItem, category, conn):
        # Load or produce a clinical_item record model for the given sourceItem
        clinicalItemKey = (category["clinical_item_category_id"], sourceItem["name"]);
        if clinicalItemKey not in self.clinicalItemByCategoryIdExtId:
            # Clinical Item does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            clinicalItem = \
                RowItemModel \
                (   {   "clinical_item_category_id": category["clinical_item_category_id"],
                        "external_id": None,
                        "name": sourceItem["name"],
                        "description": sourceItem["description"],
                    }
                );
            (clinicalItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", clinicalItem, conn=conn);
            clinicalItem["clinical_item_id"] = clinicalItemId;
            self.clinicalItemByCategoryIdExtId[clinicalItemKey] = clinicalItem;
        return self.clinicalItemByCategoryIdExtId[clinicalItemKey];

    def patientItemModelFromSourceItem(self, sourceItem, clinicalItem, conn):
        # Produce a patient_item record model for the given sourceItem
        patientItem = \
            RowItemModel \
            (   {   "external_id":  None,
                    "patient_id":  sourceItem["pat_id"],
                    "encounter_id":  None,
                    "clinical_item_id":  clinicalItem["clinical_item_id"],
                    "item_date":  sourceItem["itemDate"],
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



    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options]\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-p", "--patientIds", dest="patientIds", metavar="<patientIds>",  help="Comma separated list of patient IDs to convert demographics data for.  Leave blank to attempt conversion for all available");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        patientIds = None;
        if options.patientIds is not None:
            patientIds = options.patientIds.split(",");

        self.convertSourceItems(patientIds);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = STRIDEDemographicsConversion();
    instance.main(sys.argv);
