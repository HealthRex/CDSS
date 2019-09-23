#!/usr/bin/env python
"""Test case for respective module in application package"""

'''
setup credentials: export GOOGLE_APPLICATION_CREDENTIALS='<path to json>'
'''

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
from medinfo.dataconversion.starr_conv.STARRDemographicsConversion import STARRDemographicsConversion
from expectedData import STARRExpectedData

from google.cloud import bigquery
from medinfo.db.bigquery import bigQueryUtil
import LocalEnv

TEST_SOURCE_TABLE = 'starr_datalake2018.demographic'
TEST_DEST_DATASET = 'test_dataset'
PATH_TO_GCP_TOKEN = LocalEnv.PATH_TO_GCP_TOKEN
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH_TO_GCP_TOKEN


class TestSTARRDemographicsConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self)
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()

        log.info("Sourcing from BigQuery DB")

        self.patientIds = ['JCd5ef6e', 'JCce317d', 'JCe83f82', 'JCe5fc81', 'JCdb8fe4', 'JCcdc6a0', 'JCd37637',
                           'JCdbb57e', 'JCcebdef', 'JCcc41b3', 'JCe160b3', 'JCe8415d', 'JCdb1735', 'JCeb8fe9',
                           'JCe362b1', 'JCcca36e', 'JCddddf4', 'JCe683c1', 'JCe74388', 'JCd30ac4', 'JCd1bb22',
                           'JCe3397c', 'JCccb16c', 'JCd5da6d', 'JCd6f915', 'JCe3e96d', 'JCd43db0', 'JCe5a52f',
                           'JCd9f7b5', 'JCd60bb3', 'JCe66004', 'JCe4a6c2', 'JCceb239', 'JCda9846', 'JCce3176',
                           'JCe098ca', 'JCd31af1', 'JCe796fd', 'JCcc9243', 'JCd05308', 'JCea3982', 'JCd99619',
                           'JCd99366', 'JCdb087f', 'JCd9f2b3', 'JCe8a2d4', 'JCd19201', 'JCcdc146', 'JCe05414',
                           'JCd98ef5']

        self.pat_id_csv = '/tmp/tmp_test_pat_id.csv'
        with open(self.pat_id_csv, 'wb') as f:
            for id in ['rit_uid'] + self.patientIds:
                f.write("%s\n" % id)

        self.bqConn = bigQueryUtil.connection()
        self.converter = STARRDemographicsConversion()  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        # os.remove(self.pat_id_csv)

        DBUtil.execute \
            ("""delete from patient_item 
                    where clinical_item_id in 
                    (   select clinical_item_id
                        from clinical_item as ci, clinical_item_category as cic
                        where ci.clinical_item_category_id = cic.clinical_item_category_id
                        and cic.source_table = '%s'
                    );
                    """ % TEST_SOURCE_TABLE
             )
        DBUtil.execute \
            ("""delete from clinical_item 
                    where clinical_item_category_id in 
                    (   select clinical_item_category_id 
                        from clinical_item_category 
                        where source_table = '%s'
                    );
                    """ % TEST_SOURCE_TABLE
             )
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % TEST_SOURCE_TABLE)

        bqCursor = self.bqConn.cursor()
        bqCursor.execute('DELETE FROM %s.patient_item WHERE true;' % TEST_DEST_DATASET)
        bqCursor.execute('DELETE FROM %s.clinical_item WHERE true;' % TEST_DEST_DATASET)
        bqCursor.execute('DELETE FROM %s.clinical_item_category WHERE true;' % TEST_DEST_DATASET)

        DBTestCase.tearDown(self)

    def test_batchDataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the batch conversion process, and upload to test dataset in BigQuery...")
        self.converter.convertItemsByBatch(self.pat_id_csv, 10, datasetId=TEST_DEST_DATASET, startBatch=4)

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
                pi.patient_id desc, ci.name
            """ % (TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_DEST_DATASET, TEST_SOURCE_TABLE)

        expectedData = STARRExpectedData().demographics_expected

        bqCursor = self.bqConn.cursor()
        bqCursor.execute(testQuery)
        actualData = [row.values() for row in bqCursor.fetchall()]
        #print('actual data %s' % actualData)
        self.assertEqualTable(expectedData, actualData)


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSTARRDemographicsConversion))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
