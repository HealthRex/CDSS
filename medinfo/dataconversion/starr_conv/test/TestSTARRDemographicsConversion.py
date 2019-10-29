#!/usr/bin/env python
"""
Test case for respective module in application package
Setup credentials in LocalEnv.PATH_TO_GCP_TOKEN='<path to json>'
"""

import string

import os
import csv
import pytz
import random
import time
import logging

from datetime import datetime
import unittest

from medinfo.dataconversion.starr_conv import STARRDemographicsConversion
from medinfo.dataconversion.starr_conv.STARRUtil import StarrCommonUtils
from medinfo.dataconversion.test.Const import RUNNER_VERBOSITY
from medinfo.dataconversion.Util import log

from medinfo.db.test.Util import DBTestCase
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel

from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader

from medinfo.db.bigquery import bigQueryUtil
import LocalEnv


TEST_SOURCE_TABLE = 'test_dataset.starr_demographic'
TEST_DEST_DATASET = 'test_dataset'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = LocalEnv.PATH_TO_GCP_TOKEN

GENDER = ['Male', 'Female', 'Unknown']
RACE = ['Black', 'White', 'Asian', 'Other', 'Unknown', 'Pacific Islander', 'Native American']
ETHNICITY = ['Non-Hispanic', 'Hispanic/Latino', 'Unknown']
MARITAL_STATUS = [None, 'Separated', 'Single', 'Married', 'Unknown', 'Widowed', 'Divorced', 'Life Partner', 'Other',
                  'Legally Separated']
RELIGION = [None, 'Christian', 'Muslim', 'Buddhist', 'Other']   # only major religions - real table has much more values
LANGUAGE = [None, 'English', 'Chinese', 'French', 'Russian', 'Arabic', 'Spanish']   # UN official languages
PAT_STATUS = [None, 'Alive', 'Deceased']


class TestSTARRDemographicsConversion(DBTestCase):
    TEST_DATA_SIZE = 50
    BATCH_SIZE = 10
    STARTING_BATCH = 4

    header = ['rit_uid', 'birth_date_jittered', 'death_date_jittered', 'gender', 'canonical_race',
              'canonical_ethnicity', 'marital_status', 'religion', 'language', 'intrptr_needed_yn',
              'insurance_payor_name', 'cur_pcp_prov_map_id', 'recent_conf_enc_jittered', 'recent_ht_in_cms',
              'recent_wt_in_kgs', 'bmi', 'charlson_score', 'n_hospitalizations', 'days_in_hospital',
              'pat_status']

    patientIds = []
    test_data = []
    expected_data = []

    test_data_csv = '/tmp/test_starr_demographic_dummy_data.csv'
    pat_id_csv = '/tmp/tmp_test_pat_id.csv'

    bqConn = bigQueryUtil.connection()
    converter = STARRDemographicsConversion.STARRDemographicsConversion()  # Instance to test on
    starrUtil = StarrCommonUtils(converter.bqClient)

    def setUp(self):
        """Prepare state for test cases"""
        log.setLevel(logging.INFO)  # without this no logs are printed

        DBTestCase.setUp(self)
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()

        # point the converter to dummy source table
        STARRDemographicsConversion.SOURCE_TABLE = TEST_SOURCE_TABLE

        log.info("Generating test source data")
        self.generate_test_and_expected_data(self.TEST_DATA_SIZE)
        self.starrUtil.dump_test_data_to_csv(self.header, self.test_data, self.test_data_csv)
        self.starrUtil.upload_csv_to_bigquery('starr_datalake2018', 'demographic',
                                              'test_dataset', 'starr_demographic', self.test_data_csv)
        self.dump_patient_ids_to_test_to_csv(self.pat_id_csv)

    def generate_test_and_expected_data(self, test_data_size):
        for curr_row in range(test_data_size):
            patient_id = 'JC' + format(curr_row, '06')
            self.patientIds.append(patient_id)
            test_data_row = self.generate_test_data_row(curr_row, StarrCommonUtils.random_period(), patient_id)
            self.test_data.append(test_data_row)

            # prepare expected data starting from requested batch
            if curr_row >= self.STARTING_BATCH * self.BATCH_SIZE:
                self.generate_expected_data_rows(test_data_row, self.expected_data)

        self.expected_data.sort(key=lambda tup: (-tup[1], tup[5]))  # patient_id desc, name asc

    def dump_patient_ids_to_test_to_csv(self, pat_id_csv):
        with open(pat_id_csv, 'wb') as f:
            for rit_uid in ['rit_uid'] + self.patientIds:
                f.write("%s\n" % rit_uid)

    @staticmethod
    def generate_test_data_row(curr_row, lifespan, patient_id):
        return (patient_id,
                lifespan[0],
                [None, lifespan[1]][random.randint(0, 1)],
                GENDER[random.randint(0, len(GENDER) - 1)],
                RACE[random.randint(0, len(RACE) - 1)],
                ETHNICITY[random.randint(0, len(ETHNICITY) - 1)],
                MARITAL_STATUS[random.randint(0, len(MARITAL_STATUS) - 1)],
                RELIGION[random.randint(0, len(RELIGION) - 1)],
                LANGUAGE[random.randint(0, len(LANGUAGE) - 1)],
                [None, 'N', 'Y'][random.randint(0, 2)],
                ''.join(random.choice(string.ascii_uppercase) for _ in range(10)),
                'SS' + format(curr_row, '07'),
                datetime.fromtimestamp(random.randint(1, int(time.time())), pytz.utc),
                random.randint(150, 210),
                random.randint(50, 150),
                random.randint(18, 24),
                random.randint(1, 27),
                random.randint(0, 300),
                random.randint(0, 1000),
                PAT_STATUS[random.randint(0, len(PAT_STATUS) - 1)])

    def generate_expected_data_rows(self, row, expected_data):
        birth_list = [
            None,
            StarrCommonUtils.convertPatIdToSTRIDE(row[0]),
            None,
            "Demographics",
            None,
            "Birth",
            "Birth Year",
            datetime(row[1].year, 1, 1, tzinfo=pytz.UTC)
        ]

        expected_data.append(tuple(birth_list))
        expected_data.append(self.birth_decade_tuple_from(birth_list, row))
        expected_data.append(self.race_tuple_from(birth_list, row))
        expected_data.append(self.gender_tuple_from(birth_list, row))

        if row[2]:
            expected_data.append(self.death_date_tuple_from(birth_list, row))

    @staticmethod
    def birth_decade_tuple_from(birth_list, row):
        birth_decade_list = list(birth_list)
        decade = (row[1].year / 10) * 10
        birth_decade_list[5] = "Birth%ds" % decade
        birth_decade_list[6] = "Birth Decade %ds" % decade
        return tuple(birth_decade_list)

    def race_tuple_from(self, birth_list, row):
        race_list = list(birth_list)
        race_ethnicity = self.converter.summarizeRaceEthnicity(row[4], row[5])
        race_list[5] = "Race%s" % race_ethnicity.translate(None, " ()-/")
        race_list[6] = "Race/Ethnicity: %s" % race_ethnicity
        return tuple(race_list)

    @staticmethod
    def gender_tuple_from(birth_list, row):
        gender_list = list(birth_list)
        gender_list[5] = row[3]
        gender_list[6] = "%s Gender" % row[3]
        return tuple(gender_list)

    @staticmethod
    def death_date_tuple_from(birth_list, row):
        death_list = list(birth_list)
        death_list[5] = "Death"
        death_list[6] = "Death Date"
        death_list[7] = row[2]
        return tuple(death_list)

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        os.remove(self.pat_id_csv)
        os.remove(self.test_data_csv)

        DBUtil.execute(
            """delete from patient_item 
                    where clinical_item_id in 
                    (   select clinical_item_id
                        from clinical_item as ci, clinical_item_category as cic
                        where ci.clinical_item_category_id = cic.clinical_item_category_id
                        and cic.source_table = '%s'
                    );
                    """ % TEST_SOURCE_TABLE
        )
        DBUtil.execute(
            """delete from clinical_item 
                    where clinical_item_category_id in 
                    (   select clinical_item_category_id 
                        from clinical_item_category 
                        where source_table = '%s'
                    );
                    """ % TEST_SOURCE_TABLE
        )
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % TEST_SOURCE_TABLE)

        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute('DELETE FROM %s.patient_item WHERE true;' % TEST_DEST_DATASET)
        bq_cursor.execute('DELETE FROM %s.clinical_item WHERE true;' % TEST_DEST_DATASET)
        bq_cursor.execute('DELETE FROM %s.clinical_item_category WHERE true;' % TEST_DEST_DATASET)

        bq_cursor.execute('DROP TABLE %s;' % TEST_SOURCE_TABLE)

        DBTestCase.tearDown(self)

    def test_batchDataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the batch conversion process, and upload to test dataset in BigQuery...")
        self.converter.convertItemsByBatch(self.pat_id_csv, self.BATCH_SIZE, datasetId=TEST_DEST_DATASET,
                                           startBatch=self.STARTING_BATCH)

        # Just query back for the same data, de-normalizing the data back to a general table
        test_query = \
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

        bq_cursor = self.bqConn.cursor()
        bq_cursor.execute(test_query)
        actual_data = [row.values() for row in bq_cursor.fetchall()]

        log.debug('actual data %s' % actual_data)
        log.debug('expected data %s' % self.expected_data)

        self.assertEqualTable(self.expected_data, actual_data)


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
