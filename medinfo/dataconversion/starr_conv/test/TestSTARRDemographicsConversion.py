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

    def _test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...")
        self.converter.convertSourceItems(self.patientIds)

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select 
                pi.external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description,
                ci.external_id,
                ci.name,
                ci.description,
                pi.item_date
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '%s'
            order by
                pi.patient_id desc, ci.name
            """ % TEST_SOURCE_TABLE

        expectedData = \
            [
                [None, 15437801L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1963, 1, 1, 0, 0)],
                [None, 15437801L, None, 'Demographics', None, 'Birth1960s', 'Birth Decade 1960s',
                 datetime(1963, 1, 1, 0, 0)],
                [None, 15437801L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1963, 1, 1, 0, 0)],
                [None, 15437801L, None, 'Demographics', None, 'RaceOther', 'Race/Ethnicity: Other',
                 datetime(1963, 1, 1, 0, 0)],
                [None, 15350146L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2007, 1, 1, 0, 0)],
                [None, 15350146L, None, 'Demographics', None, 'Birth2000s', 'Birth Decade 2000s',
                 datetime(2007, 1, 1, 0, 0)],
                [None, 15350146L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2007, 1, 1, 0, 0)],
                [None, 15350146L, None, 'Demographics', None, 'RaceAsian', 'Race/Ethnicity: Asian',
                 datetime(2007, 1, 1, 0, 0)],
                [None, 15246036L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2008, 1, 1, 0, 0)],
                [None, 15246036L, None, 'Demographics', None, 'Birth2000s', 'Birth Decade 2000s',
                 datetime(2008, 1, 1, 0, 0)],
                [None, 15246036L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(2008, 1, 1, 0, 0)],
                [None, 15246036L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(2008, 1, 1, 0, 0)],
                [None, 15221085L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1929, 1, 1, 0, 0)],
                [None, 15221085L, None, 'Demographics', None, 'Birth1920s', 'Birth Decade 1920s',
                 datetime(1929, 1, 1, 0, 0)],
                [None, 15221085L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1929, 1, 1, 0, 0)],
                [None, 15221085L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1929, 1, 1, 0, 0)],
                [None, 15220610L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1991, 1, 1, 0, 0)],
                [None, 15220610L, None, 'Demographics', None, 'Birth1990s', 'Birth Decade 1990s',
                 datetime(1991, 1, 1, 0, 0)],
                [None, 15220610L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1991, 1, 1, 0, 0)],
                [None, 15220610L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1991, 1, 1, 0, 0)],
                [None, 15177469L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1945, 1, 1, 0, 0)],
                [None, 15177469L, None, 'Demographics', None, 'Birth1940s', 'Birth Decade 1940s',
                 datetime(1945, 1, 1, 0, 0)],
                [None, 15177469L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1945, 1, 1, 0, 0)],
                [None, 15177469L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1945, 1, 1, 0, 0)],
                [None, 15156104L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1958, 1, 1, 0, 0)],
                [None, 15156104L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1958, 1, 1, 0, 0)],
                [None, 15156104L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1958, 1, 1, 0, 0)],
                [None, 15156104L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1958, 1, 1, 0, 0)],
                [None, 15107009L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1955, 1, 1, 0, 0)],
                [None, 15107009L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1955, 1, 1, 0, 0)],
                [None, 15107009L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1955, 1, 1, 0, 0)],
                [None, 15107009L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1955, 1, 1, 0, 0)],
                [None, 15097860L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1997, 1, 1, 0, 0)],
                [None, 15097860L, None, 'Demographics', None, 'Birth1990s', 'Birth Decade 1990s',
                 datetime(1997, 1, 1, 0, 0)],
                [None, 15097860L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1997, 1, 1, 0, 0)],
                [None, 15097860L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1997, 1, 1, 0, 0)],
                [None, 15072385L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2003, 1, 1, 0, 0)],
                [None, 15072385L, None, 'Demographics', None, 'Birth2000s', 'Birth Decade 2000s',
                 datetime(2003, 1, 1, 0, 0)],
                [None, 15072385L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2003, 1, 1, 0, 0)],
                [None, 15072385L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2003, 1, 1, 0, 0)],
                [None, 15050031L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1981, 1, 1, 0, 0)],
                [None, 15050031L, None, 'Demographics', None, 'Birth1980s', 'Birth Decade 1980s',
                 datetime(1981, 1, 1, 0, 0)],
                [None, 15050031L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1981, 1, 1, 0, 0)],
                [None, 15050031L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1981, 1, 1, 0, 0)],
                [None, 14984898L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1950, 1, 1, 0, 0)],
                [None, 14984898L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1950, 1, 1, 0, 0)],
                [None, 14984898L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1950, 1, 1, 0, 0)],
                [None, 14984898L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1950, 1, 1, 0, 0)],
                [None, 14936429L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1932, 1, 1, 0, 0)],
                [None, 14936429L, None, 'Demographics', None, 'Birth1930s', 'Birth Decade 1930s',
                 datetime(1932, 1, 1, 0, 0)],
                [None, 14936429L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1932, 1, 1, 0, 0)],
                [None, 14936429L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1932, 1, 1, 0, 0)],
                [None, 14901937L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1960, 1, 1, 0, 0)],
                [None, 14901937L, None, 'Demographics', None, 'Birth1960s', 'Birth Decade 1960s',
                 datetime(1960, 1, 1, 0, 0)],
                [None, 14901937L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1960, 1, 1, 0, 0)],
                [None, 14901937L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1960, 1, 1, 0, 0)],
                [None, 14891388L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2014, 1, 1, 0, 0)],
                [None, 14891388L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2014, 1, 1, 0, 0)],
                [None, 14891388L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(2014, 1, 1, 0, 0)],
                [None, 14891388L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2014, 1, 1, 0, 0)],
                [None, 14770355L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1950, 1, 1, 0, 0)],
                [None, 14770355L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1950, 1, 1, 0, 0)],
                [None, 14770355L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1950, 1, 1, 0, 0)],
                [None, 14770355L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1950, 1, 1, 0, 0)],
                [None, 14719178L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2011, 1, 1, 0, 0)],
                [None, 14719178L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2011, 1, 1, 0, 0)],
                [None, 14719178L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2011, 1, 1, 0, 0)],
                [None, 14719178L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2011, 1, 1, 0, 0)],
                [None, 14701588L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1949, 1, 1, 0, 0)],
                [None, 14701588L, None, 'Demographics', None, 'Birth1940s', 'Birth Decade 1940s',
                 datetime(1949, 1, 1, 0, 0)],
                [None, 14701588L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1949, 1, 1, 0, 0)],
                [None, 14701588L, None, 'Demographics', None, 'RaceOther', 'Race/Ethnicity: Other',
                 datetime(1949, 1, 1, 0, 0)],
                [None, 14540276L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2018, 1, 1, 0, 0)],
                [None, 14540276L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2018, 1, 1, 0, 0)],
                [None, 14540276L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2018, 1, 1, 0, 0)],
                [None, 14540276L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2018, 1, 1, 0, 0)],
                [None, 14398846L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1959, 1, 1, 0, 0)],
                [None, 14398846L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1959, 1, 1, 0, 0)],
                [None, 14398846L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1959, 1, 1, 0, 0)],
                [None, 14398846L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1959, 1, 1, 0, 0)],
                [None, 14389220L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1992, 1, 1, 0, 0)],
                [None, 14389220L, None, 'Demographics', None, 'Birth1990s', 'Birth Decade 1990s',
                 datetime(1992, 1, 1, 0, 0)],
                [None, 14389220L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1992, 1, 1, 0, 0)],
                [None, 14389220L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1992, 1, 1, 0, 0)],
                [None, 14358325L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1956, 1, 1, 0, 0)],
                [None, 14358325L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1956, 1, 1, 0, 0)],
                [None, 14358325L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1956, 1, 1, 0, 0)],
                [None, 14358325L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1956, 1, 1, 0, 0)],
                [None, 14354559L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1954, 1, 1, 0, 0)],
                [None, 14354559L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1954, 1, 1, 0, 0)],
                [None, 14354559L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1954, 1, 1, 0, 0)],
                [None, 14354559L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1954, 1, 1, 0, 0)],
                [None, 14325830L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1942, 1, 1, 0, 0)],
                [None, 14325830L, None, 'Demographics', None, 'Birth1940s', 'Birth Decade 1940s',
                 datetime(1942, 1, 1, 0, 0)],
                [None, 14325830L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1942, 1, 1, 0, 0)],
                [None, 14325830L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1942, 1, 1, 0, 0)],
                [None, 14284725L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2015, 1, 1, 0, 0)],
                [None, 14284725L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2015, 1, 1, 0, 0)],
                [None, 14284725L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(2015, 1, 1, 0, 0)],
                [None, 14284725L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2015, 1, 1, 0, 0)],
                [None, 14283443L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2007, 1, 1, 0, 0)],
                [None, 14283443L, None, 'Demographics', None, 'Birth2000s', 'Birth Decade 2000s',
                 datetime(2007, 1, 1, 0, 0)],
                [None, 14283443L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(2007, 1, 1, 0, 0)],
                [None, 14283443L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2007, 1, 1, 0, 0)],
                [None, 14259737L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1946, 1, 1, 0, 0)],
                [None, 14259737L, None, 'Demographics', None, 'Birth1940s', 'Birth Decade 1940s',
                 datetime(1946, 1, 1, 0, 0)],
                [None, 14259737L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1946, 1, 1, 0, 0)],
                [None, 14259737L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1946, 1, 1, 0, 0)],
                [None, 14259046L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1929, 1, 1, 0, 0)],
                [None, 14259046L, None, 'Demographics', None, 'Birth1920s', 'Birth Decade 1920s',
                 datetime(1929, 1, 1, 0, 0)],
                [None, 14259046L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1929, 1, 1, 0, 0)],
                [None, 14259046L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1929, 1, 1, 0, 0)],
                [None, 14257909L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2018, 1, 1, 0, 0)],
                [None, 14257909L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2018, 1, 1, 0, 0)],
                [None, 14257909L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2018, 1, 1, 0, 0)],
                [None, 14257909L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2018, 1, 1, 0, 0)],
                [None, 14088469L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1932, 1, 1, 0, 0)],
                [None, 14088469L, None, 'Demographics', None, 'Birth1930s', 'Birth Decade 1930s',
                 datetime(1932, 1, 1, 0, 0)],
                [None, 14088469L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1932, 1, 1, 0, 0)],
                [None, 14088469L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1932, 1, 1, 0, 0)],
                [None, 14027699L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2015, 1, 1, 0, 0)],
                [None, 14027699L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2015, 1, 1, 0, 0)],
                [None, 14027699L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2015, 1, 1, 0, 0)],
                [None, 14027699L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2015, 1, 1, 0, 0)],
                [None, 14020462L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1998, 1, 1, 0, 0)],
                [None, 14020462L, None, 'Demographics', None, 'Birth1990s', 'Birth Decade 1990s',
                 datetime(1998, 1, 1, 0, 0)],
                [None, 14020462L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1998, 1, 1, 0, 0)],
                [None, 14020462L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1998, 1, 1, 0, 0)],
                [None, 14015085L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1974, 1, 1, 0, 0)],
                [None, 14015085L, None, 'Demographics', None, 'Birth1970s', 'Birth Decade 1970s',
                 datetime(1974, 1, 1, 0, 0)],
                [None, 14015085L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1974, 1, 1, 0, 0)],
                [None, 14015085L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(1974, 1, 1, 0, 0)],
                [None, 13909424L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2011, 1, 1, 0, 0)],
                [None, 13909424L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2011, 1, 1, 0, 0)],
                [None, 13909424L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2011, 1, 1, 0, 0)],
                [None, 13909424L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(2011, 1, 1, 0, 0)],
                [None, 13858359L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1936, 1, 1, 0, 0)],
                [None, 13858359L, None, 'Demographics', None, 'Birth1930s', 'Birth Decade 1930s',
                 datetime(1936, 1, 1, 0, 0)],
                [None, 13858359L, None, 'Demographics', None, 'Death', 'Death Date', datetime(2013, 11, 4, 16, 0)],
                [None, 13858359L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1936, 1, 1, 0, 0)],
                [None, 13858359L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1936, 1, 1, 0, 0)],
                [None, 13834993L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1948, 1, 1, 0, 0)],
                [None, 13834993L, None, 'Demographics', None, 'Birth1940s', 'Birth Decade 1940s',
                 datetime(1948, 1, 1, 0, 0)],
                [None, 13834993L, None, 'Demographics', None, 'Death', 'Death Date', datetime(2016, 1, 19, 16, 0)],
                [None, 13834993L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1948, 1, 1, 0, 0)],
                [None, 13834993L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1948, 1, 1, 0, 0)],
                [None, 13830852L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2011, 1, 1, 0, 0)],
                [None, 13830852L, None, 'Demographics', None, 'Birth2010s', 'Birth Decade 2010s',
                 datetime(2011, 1, 1, 0, 0)],
                [None, 13830852L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(2011, 1, 1, 0, 0)],
                [None, 13830852L, None, 'Demographics', None, 'RaceUnknown', 'Race/Ethnicity: Unknown',
                 datetime(2011, 1, 1, 0, 0)],
                [None, 13744930L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1955, 1, 1, 0, 0)],
                [None, 13744930L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1955, 1, 1, 0, 0)],
                [None, 13744930L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1955, 1, 1, 0, 0)],
                [None, 13744930L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1955, 1, 1, 0, 0)],
                [None, 13734401L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1994, 1, 1, 0, 0)],
                [None, 13734401L, None, 'Demographics', None, 'Birth1990s', 'Birth Decade 1990s',
                 datetime(1994, 1, 1, 0, 0)],
                [None, 13734401L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1994, 1, 1, 0, 0)],
                [None, 13734401L, None, 'Demographics', None, 'RaceAsian', 'Race/Ethnicity: Asian',
                 datetime(1994, 1, 1, 0, 0)],
                [None, 13652744L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1979, 1, 1, 0, 0)],
                [None, 13652744L, None, 'Demographics', None, 'Birth1970s', 'Birth Decade 1970s',
                 datetime(1979, 1, 1, 0, 0)],
                [None, 13652744L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1979, 1, 1, 0, 0)],
                [None, 13652744L, None, 'Demographics', None, 'RacePacificIslander', 'Race/Ethnicity: Pacific Islander',
                 datetime(1979, 1, 1, 0, 0)],
                [None, 13549039L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1947, 1, 1, 0, 0)],
                [None, 13549039L, None, 'Demographics', None, 'Birth1940s', 'Birth Decade 1940s',
                 datetime(1947, 1, 1, 0, 0)],
                [None, 13549039L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1947, 1, 1, 0, 0)],
                [None, 13549039L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1947, 1, 1, 0, 0)],
                [None, 13546041L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1935, 1, 1, 0, 0)],
                [None, 13546041L, None, 'Demographics', None, 'Birth1930s', 'Birth Decade 1930s',
                 datetime(1935, 1, 1, 0, 0)],
                [None, 13546041L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1935, 1, 1, 0, 0)],
                [None, 13546041L, None, 'Demographics', None, 'RaceOther', 'Race/Ethnicity: Other',
                 datetime(1935, 1, 1, 0, 0)],
                [None, 13513085L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(2002, 1, 1, 0, 0)],
                [None, 13513085L, None, 'Demographics', None, 'Birth2000s', 'Birth Decade 2000s',
                 datetime(2002, 1, 1, 0, 0)],
                [None, 13513085L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(2002, 1, 1, 0, 0)],
                [None, 13513085L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(2002, 1, 1, 0, 0)],
                [None, 13513078L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1952, 1, 1, 0, 0)],
                [None, 13513078L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1952, 1, 1, 0, 0)],
                [None, 13513078L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1952, 1, 1, 0, 0)],
                [None, 13513078L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1952, 1, 1, 0, 0)],
                [None, 13485728L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1981, 1, 1, 0, 0)],
                [None, 13485728L, None, 'Demographics', None, 'Birth1980s', 'Birth Decade 1980s',
                 datetime(1981, 1, 1, 0, 0)],
                [None, 13485728L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1981, 1, 1, 0, 0)],
                [None, 13485728L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1981, 1, 1, 0, 0)],
                [None, 13484358L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1958, 1, 1, 0, 0)],
                [None, 13484358L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1958, 1, 1, 0, 0)],
                [None, 13484358L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1958, 1, 1, 0, 0)],
                [None, 13484358L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1958, 1, 1, 0, 0)],
                [None, 13414764L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1929, 1, 1, 0, 0)],
                [None, 13414764L, None, 'Demographics', None, 'Birth1920s', 'Birth Decade 1920s',
                 datetime(1929, 1, 1, 0, 0)],
                [None, 13414764L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1929, 1, 1, 0, 0)],
                [None, 13414764L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1929, 1, 1, 0, 0)],
                [None, 13411182L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1961, 1, 1, 0, 0)],
                [None, 13411182L, None, 'Demographics', None, 'Birth1960s', 'Birth Decade 1960s',
                 datetime(1961, 1, 1, 0, 0)],
                [None, 13411182L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1961, 1, 1, 0, 0)],
                [None, 13411182L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1961, 1, 1, 0, 0)],
                [None, 13406787L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1954, 1, 1, 0, 0)],
                [None, 13406787L, None, 'Demographics', None, 'Birth1950s', 'Birth Decade 1950s',
                 datetime(1954, 1, 1, 0, 0)],
                [None, 13406787L, None, 'Demographics', None, 'Female', 'Female Gender', datetime(1954, 1, 1, 0, 0)],
                [None, 13406787L, None, 'Demographics', None, 'RaceBlack', 'Race/Ethnicity: Black',
                 datetime(1954, 1, 1, 0, 0)],
                [None, 13386163L, None, 'Demographics', None, 'Birth', 'Birth Year', datetime(1983, 1, 1, 0, 0)],
                [None, 13386163L, None, 'Demographics', None, 'Birth1980s', 'Birth Decade 1980s',
                 datetime(1983, 1, 1, 0, 0)],
                [None, 13386163L, None, 'Demographics', None, 'Male', 'Male Gender', datetime(1983, 1, 1, 0, 0)],
                [None, 13386163L, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino',
                 'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1983, 1, 1, 0, 0)]

            ]

        actualData = DBUtil.execute(testQuery)
        self.assertEqualTable(expectedData, actualData)

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

        expectedData = \
            [(None, 15350146, None, u'Demographics', None, u'Birth', u'Birth Year',
              datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15350146, None, u'Demographics', None, u'Birth2000s', u'Birth Decade 2000s',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15350146, None, u'Demographics', None, u'Female', u'Female Gender',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15350146, None, u'Demographics', None, u'RaceAsian', u'Race/Ethnicity: Asian',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15246036, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(2008, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15246036, None, u'Demographics', None, u'Birth2000s', u'Birth Decade 2000s',
        datetime(2008, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15246036, None, u'Demographics', None, u'Male', u'Male Gender',
        datetime(2008, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 15246036, None, u'Demographics', None, u'RaceWhiteNonHispanicLatino',
        u'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(2008, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14701588, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(1949, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14701588, None, u'Demographics', None, u'Birth1940s', u'Birth Decade 1940s',
        datetime(1949, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14701588, None, u'Demographics', None, u'Female', u'Female Gender',
        datetime(1949, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14701588, None, u'Demographics', None, u'RaceOther', u'Race/Ethnicity: Other',
        datetime(1949, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14354559, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(1954, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14354559, None, u'Demographics', None, u'Birth1950s', u'Birth Decade 1950s',
        datetime(1954, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14354559, None, u'Demographics', None, u'Female', u'Female Gender',
        datetime(1954, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14354559, None, u'Demographics', None, u'RaceWhiteNonHispanicLatino',
        u'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1954, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14283443, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14283443, None, u'Demographics', None, u'Birth2000s', u'Birth Decade 2000s',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14283443, None, u'Demographics', None, u'Male', u'Male Gender',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14283443, None, u'Demographics', None, u'RaceUnknown', u'Race/Ethnicity: Unknown',
        datetime(2007, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259737, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(1946, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259737, None, u'Demographics', None, u'Birth1940s', u'Birth Decade 1940s',
        datetime(1946, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259737, None, u'Demographics', None, u'Male', u'Male Gender',
        datetime(1946, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259737, None, u'Demographics', None, u'RaceWhiteNonHispanicLatino',
        u'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1946, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259046, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(1929, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259046, None, u'Demographics', None, u'Birth1920s', u'Birth Decade 1920s',
        datetime(1929, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259046, None, u'Demographics', None, u'Female', u'Female Gender',
        datetime(1929, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14259046, None, u'Demographics', None, u'RaceWhiteNonHispanicLatino',
        u'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1929, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14257909, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(2018, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14257909, None, u'Demographics', None, u'Birth2010s', u'Birth Decade 2010s',
        datetime(2018, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14257909, None, u'Demographics', None, u'Female', u'Female Gender',
        datetime(2018, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 14257909, None, u'Demographics', None, u'RaceUnknown', u'Race/Ethnicity: Unknown',
        datetime(2018, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13734401, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(1994, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13734401, None, u'Demographics', None, u'Birth1990s', u'Birth Decade 1990s',
        datetime(1994, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13734401, None, u'Demographics', None, u'Male', u'Male Gender',
        datetime(1994, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13734401, None, u'Demographics', None, u'RaceAsian', u'Race/Ethnicity: Asian',
        datetime(1994, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13484358, None, u'Demographics', None, u'Birth', u'Birth Year',
        datetime(1958, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13484358, None, u'Demographics', None, u'Birth1950s', u'Birth Decade 1950s',
        datetime(1958, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13484358, None, u'Demographics', None, u'Female', u'Female Gender',
        datetime(1958, 1, 1, 0, 0, tzinfo=pytz.UTC)), (
        None, 13484358, None, u'Demographics', None, u'RaceWhiteNonHispanicLatino',
        u'Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1958, 1, 1, 0, 0, tzinfo=pytz.UTC))]

        bqCursor = self.bqConn.cursor()
        bqCursor.execute(testQuery)
        actualData = [row.values() for row in bqCursor.fetchall()]
        print('actual data %s' % actualData)
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
