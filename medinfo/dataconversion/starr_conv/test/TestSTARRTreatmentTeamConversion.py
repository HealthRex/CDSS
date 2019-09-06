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

        expectedData = \
            [(2709560, 13914107, 131260688793, u'Treatment Team', None, u'RN', u'Registered Nurse',
              datetime(2018, 12, 30, 15, 26, tzinfo=pytz.UTC)), (
        2708067, 14717649, 131255744783, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 57, tzinfo=pytz.UTC)), (
        2701717, 13398957, 131259891113, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 33, tzinfo=pytz.UTC)), (
        2697065, 14677354, 131261130103, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 18, tzinfo=pytz.UTC)), (
        2655524, 14296268, 131260909852, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 30, tzinfo=pytz.UTC)), (
        2648197, 14045374, 131260898062, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 57, tzinfo=pytz.UTC)), (
        2638232, 15416902, 131260891850, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 2, tzinfo=pytz.UTC)), (
        2622278, 14210699, 131260810435, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 20, tzinfo=pytz.UTC)), (
        2582352, 13390259, 131261195711, u'Treatment Team', None, u'PR', u'Primary Resident',
        datetime(2018, 12, 30, 15, 7, tzinfo=pytz.UTC)), (
        2135397, 14945301, 131260435164, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 30, tzinfo=pytz.UTC)), (
        2127105, 15246271, 131261363409, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 52, tzinfo=pytz.UTC)), (
        2119040, 14313125, 131259375857, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 27, tzinfo=pytz.UTC)), (
        2107282, 13677667, 131260808224, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 4, tzinfo=pytz.UTC)), (
        2107282, 13869166, 131260810202, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 8, tzinfo=pytz.UTC)), (
        2107208, 13356701, 131260466149, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 17, tzinfo=pytz.UTC)), (
        2106448, 13842159, 131260466853, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 9, tzinfo=pytz.UTC)), (
        2106448, 14076737, 131261181450, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 9, tzinfo=pytz.UTC)), (
        2106448, 14777007, 131259626685, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 9, tzinfo=pytz.UTC)), (
        2103328, 14314915, 131260296016, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 6, tzinfo=pytz.UTC)), (
        2103300, 14299576, 131260524806, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 0, tzinfo=pytz.UTC)), (
        1667159, 14929896, 131259037994, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 54, tzinfo=pytz.UTC)), (
        1667159, 13398957, 131259891113, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 54, tzinfo=pytz.UTC)), (
        1667159, 14720679, 131260033006, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 54, tzinfo=pytz.UTC)), (
        1652569, 14856290, 131261100608, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 7, tzinfo=pytz.UTC)), (
        1639251, 14621193, 131255530644, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 9, tzinfo=pytz.UTC)), (
        1639251, 14210699, 131260810435, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 28, tzinfo=pytz.UTC)), (
        1599073, 14394017, 131258601774, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 59, tzinfo=pytz.UTC)), (
        497047, 14370277, 131260817905, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 48, tzinfo=pytz.UTC)), (
        417814, 14278493, 131259045304, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 3, tzinfo=pytz.UTC)), (
        398084, 13872813, 131258837268, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 34, tzinfo=pytz.UTC)), (
        333937, 14251162, 131261147644, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 51, tzinfo=pytz.UTC)), (
        287862, 15059389, 131260312121, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 15, tzinfo=pytz.UTC)), (
        287862, 14399592, 131259550746, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 15, tzinfo=pytz.UTC)), (
        287028, 13779004, 131260180787, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 15, 57, tzinfo=pytz.UTC)), (
        264215, 15484450, 131261127832, u'Treatment Team', None, u'CCA', u'Cross Cover Attending',
        datetime(2018, 12, 30, 15, 6, tzinfo=pytz.UTC)), (
        227605, 14601216, 131259919868, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 0, tzinfo=pytz.UTC)), (
        227605, 15232402, 131260565278, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 12, tzinfo=pytz.UTC)), (
        227605, 13665097, 131260385738, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 10, tzinfo=pytz.UTC)), (
        209156, 13744608, 131260688501, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 52, tzinfo=pytz.UTC)), (
        14184, 13388609, 131259880179, u'Treatment Team', None, u'RCP', u'Respiratory Care Practitioner',
        datetime(2018, 12, 30, 16, 0, tzinfo=pytz.UTC)), (
        12932, 14647360, 131259360262, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 3, tzinfo=pytz.UTC)), (
        12694, 15167216, 131261072213, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 21, tzinfo=pytz.UTC)), (
        10386, 14268873, 131260253920, u'Treatment Team', None, u'NA', u'Nursing Assistant',
        datetime(2018, 12, 30, 15, 5, tzinfo=pytz.UTC)), (
        9107, 14261525, 131260818663, u'Treatment Team', None, u'RN', u'Registered Nurse',
        datetime(2018, 12, 30, 15, 5, tzinfo=pytz.UTC)), (
        8293, 14125153, 131259837513, u'Treatment Team', None, u'LVN', u'Licensed Vocational Nurse',
        datetime(2018, 12, 30, 15, 21, tzinfo=pytz.UTC)), (
        8293, 13577716, 131261117326, u'Treatment Team', None, u'LVN', u'Licensed Vocational Nurse',
        datetime(2018, 12, 30, 15, 24, tzinfo=pytz.UTC))]

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
