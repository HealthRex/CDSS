#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
import csv
import pytz

from cStringIO import StringIO
from datetime import datetime
import unittest

from medinfo.dataconversion.test.Const import RUNNER_VERBOSITY
from medinfo.dataconversion.Util import log

from medinfo.db.test.Util import DBTestCase

from stride.core.StrideLoader import StrideLoader
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel

from medinfo.dataconversion.starr_conv.STARRTreatmentTeamConversion import STARRTreatmentTeamConversion, \
    ConversionOptions

from google.cloud import bigquery
from medinfo.db.bigquery import bigQueryUtil
from medinfo.dataconversion.starr_conv import STARRUtil
from expectedData import STARRExpectedData
import LocalEnv

TEST_SOURCE_TABLE = 'starr_datalake2018.treatment_team'
TEST_DEST_DATASET = 'test_dataset'
PATH_TO_GCP_TOKEN = LocalEnv.PATH_TO_GCP_TOKEN
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH_TO_GCP_TOKEN
# Date in far future to start checking for test records to avoid including existing data in database
TEST_START_DATE = datetime(2018, 12, 30, 23)

class TestSTARRTreatmentTeamConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        log.info("Sourcing from BigQuery DB")
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()

        self.converter = STARRTreatmentTeamConversion()  # Instance to test on
        self.bqConn = self.converter.bqConn
        self.starrUtil = STARRUtil.StarrCommonUtils(self.converter.bqClient)

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
            ("""delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = '%s'
            )
            """ % TEST_SOURCE_TABLE
             )
        DBUtil.execute \
            ("""delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = '%s'
            )
            """ % TEST_SOURCE_TABLE
             )
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % TEST_SOURCE_TABLE)

        bqCursor = self.bqConn.cursor()
        bqCursor.execute('DELETE FROM %s.patient_item WHERE true;' % TEST_DEST_DATASET)
        bqCursor.execute('DELETE FROM %s.clinical_item WHERE true;' % TEST_DEST_DATASET)
        bqCursor.execute('DELETE FROM %s.clinical_item_category WHERE true;' % TEST_DEST_DATASET)

        DBTestCase.tearDown(self)

    def test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...")
        convOptions = ConversionOptions()
        convOptions.startDate = TEST_START_DATE
        #self.converter.convertSourceItems(convOptions)
        tempDir = '/tmp'
        self.converter.convertAndUpload(convOptions, tempDir=tempDir, datasetId=TEST_DEST_DATASET)

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select
                pi.external_id as pi_external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description as cic_description,
                ci.external_id as ci_external_id,
                ci.name,
                ci.description as ci_description,
                pi.item_date
            from
                %s.patient_item as pi,
                %s.clinical_item as ci,
                %s.clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '%s'
            order by
                pi.external_id desc, ci.external_id desc
            """ % (TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_SOURCE_TABLE)

        self.starrUtil.dumpClinicalTablesToCsv(tempDir)
        self.starrUtil.uploadClinicalTablesCsvToBQ(tempDir, TEST_DEST_DATASET)
        self.starrUtil.removeClinicalTablesCsv(tempDir)
        self.starrUtil.removeClinicalTablesAddedLines(TEST_SOURCE_TABLE)

        expectedData = STARRExpectedData().treatmentteam_expected

        bqCursor = self.bqConn.cursor()
        bqCursor.execute(testQuery)
        actualData = [row.values() for row in bqCursor.fetchall()]
        #print('actual data %s' % actualData)
        self.assertEqualTable(expectedData, actualData)

    def _test_dataConversion_aggregate(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...")
        convOptions = ConversionOptions()
        convOptions.startDate = TEST_START_DATE
        convOptions.aggregate = True
        self.converter.convertSourceItems(convOptions)

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select 
                pi.external_id as pi_external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description as cic_description,
                ci.external_id as ci_external_id,
                ci.name,
                ci.description as ci_description,
                pi.item_date
            from
                %s.patient_item as pi,
                %s.clinical_item as ci,
                %s.clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '%s'
            order by
                pi.external_id desc, ci.external_id desc
            """ % (TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_SOURCE_TABLE)
        expectedData = \
            []
        actualData = DBUtil.execute(testQuery)
        self.assertEqualTable(expectedData, actualData)


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite()
    # suite.addTest(TestSTARRTreatmentTeamConversion("test_incColNamesAndTypeCodes"))
    # suite.addTest(TestSTARRTreatmentTeamConversion("test_insertFile_skipErrors"))
    # suite.addTest(TestSTARRTreatmentTeamConversion('test_executeIterator'))
    # suite.addTest(TestSTARRTreatmentTeamConversion('test_dataConversion_aggregate'))
    suite.addTest(unittest.makeSuite(TestSTARRTreatmentTeamConversion))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
