#!/usr/bin/env python
"""
Test suite for respective module in application package.
"""
import LocalEnv
LocalEnv.LOCAL_TEST_DB_PARAM["DSN"] = 'UMich_test.db'
LocalEnv.LOCAL_TEST_DB_PARAM["DBPATH"] = LocalEnv.PATH_TO_CDSS + '/medinfo/dataconversion/test/'
import medinfo.db.Env # TODO: comment
medinfo.db.Env.SQL_PLACEHOLDER = "?"
medinfo.db.Env.DATABASE_CONNECTOR_NAME = "sqlite3"

import datetime
import sys, os
os.chdir(LocalEnv.PATH_TO_CDSS + '/' + 'medinfo/dataconversion/test/')

import time
import unittest
from Const import RUNNER_VERBOSITY
from cStringIO import StringIO
# from FeatureMatrixTestData_UMich import FM_TEST_INPUT_TABLES, FM_TEST_OUTPUT
from medinfo.dataconversion.DataExtractor import DataExtractor
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable
from medinfo.db.ResultsFormatter import TextResultsFormatter
from medinfo.db.test.Util import DBTestCase
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader;

from Util import log


import pandas as pd
pd.set_option('display.width', 300)
import sqlite3
import UMichFeatureMatrixTestData as FMTU

class TestFeatureMatrixFactory(DBTestCase):
    def setUp(self):
        """Prepare state for test cases."""
        DBTestCase.setUp(self)

        # StrideLoader.build_stride_psql_schemata()
        # ClinicalItemDataLoader.build_clinical_item_psql_schemata();

        # self._deleteTestRecords()
        # self._insertTestRecords()
        self.factory = FeatureMatrixFactory()  # TODO: self.RACE_FEATURES = self.queryAllRaces(), OperationalError: no such table: demographics

        self.connection = DBUtil.connection();  # Setup a common connection for test cases to work with, can catch in finally tearDown method to close/cleanup
        self.cursor = self.connection.cursor()
        self._insertUMichTestRecords()

    def _insertUMichTestRecords(self):
        db_name = medinfo.db.Env.DB_PARAM['DSN']
        db_path = medinfo.db.Env.DB_PARAM['DATAPATH']
        conn = sqlite3.connect(db_path + '/' + db_name)

        table_names = ['labs', 'pt_info', 'demographics', 'encounters', 'diagnoses']

        for table_name in table_names:
            columns = FMTU.FM_TEST_INPUT_TABLES["%s_columns"%table_name]
            column_types = FMTU.FM_TEST_INPUT_TABLES["%s_column_types"%table_name]

            df = pd.DataFrame()
            for one_line in FMTU.FM_TEST_INPUT_TABLES['%s_data'%table_name]:
                df = df.append(dict(zip(columns, one_line)), ignore_index=True)

            df.to_sql(table_name, conn, if_exists="append", index=False)

        # First, write basic (pat_id, order_time) episode information to TempFile
        # Then, all [[pat_id, event_time]] operations are based on these episodes
        # i.e., pat_id are all from these pat_ids

        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("CAST(pat_id AS INTEGER) AS pat_id")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addFrom("labs")
        self.cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        self.factory.setPatientEpisodeInput(self.cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()
        resultEpisodeIterator = self.factory.getPatientEpisodeIterator()
        resultPatientEpisodes = list()
        for episode in resultEpisodeIterator:
            episode["pat_id"] = int(episode["pat_id"])
            episode["order_time"] = DBUtil.parseDateValue(episode["order_time"])
            resultPatientEpisodes.append(episode)

        # print 'len(resultPatientEpisodes):', len(resultPatientEpisodes)

    def tearDown(self):
        """Restore state from any setUp or test steps."""
        # self._deleteTestRecords()

        # Clean up files that might have lingered from failed tests.
        try:
            os.remove("patient_list.tsv")
        except:
            pass
        try:
            self.factory.cleanTempFiles()
        except:
            pass
        try:
            os.remove(self.factory.getMatrixFileName())
        except:
            pass
        try:
            os.remove("extractor.feature_matrix.tab.gz")
        except:
            pass

        self.connection.close();

        DBTestCase.tearDown(self)

    def test__queryMichiganItemsByName_UMich(self):
        ## Input parameters:
        # clinicalItemNames: (e.g. ['Male'], ['Caucasian'], ['Birth']),
        # clinicalItemType: (e.g. 'GenderName', 'RaceName', None),
        # tableName: (e.g. demographics, demographics, pt_info),
        # clinicalItemTime: (e.g. None, None, 'Birth', where the None values are imputed (1900,1,1) in FMF)

        ## Outputs:
        # clinicalItemEvents: [pat_id, event_time] pairs like
        # [
        # [-12411450059993L, datetime.datetime(2011, 8, 4, 23, 14)],
        # [-12411450059993L, datetime.datetime(2011, 8, 5, 0, 38)],
        # [-12392267210986L, datetime.datetime(2015, 11, 25, 22, 57)]
        # ...]

        # Test SEX feature
        MALE_events_expected = [[1, datetime.datetime(1900, 1, 1, 0, 0)]]
        MALE_events_queried = self.factory._queryMichiganItemsByName(clinicalItemNames=['Male'],
                                                     clinicalItemType='GenderName',
                                                     tableName='demographics',
                                                     clinicalItemTime=None)

        self.assertEqualSet(MALE_events_expected, MALE_events_queried)

        HCT_events_expected = [[1, u'2050-01-08 23:44:00']]

        HCT_events_queried = self.factory._queryMichiganItemsByName(clinicalItemNames=['HCT'],
                                                                     clinicalItemType='base_name',
                                                                     tableName='labs',
                                                                     clinicalItemTime='order_time')
        self.assertEqualSet(HCT_events_expected, HCT_events_queried)


    def lists_to_pd(self, alists):
        # The first list should be the column list
        columns = alists[0]
        df = pd.DataFrame()
        for i in range(1,len(alists)):
            df = df.append(dict(zip(columns, alists[i])), ignore_index=True)
        return df

    def test__BuildMatrix_UMich(self):
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['CBCP'],
                                                   clinicalItemType='proc_code',
                                                   tableName='labs',
                                                   clinicalItemTime='order_time')
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['WCB'],
                                                     clinicalItemType='base_name',
                                                     tableName='labs',
                                                     clinicalItemTime='order_time')
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['HCT'],
                                                     clinicalItemType='base_name',
                                                     tableName='labs',
                                                     clinicalItemTime='order_time')
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['Male'],
                                                     clinicalItemType='GenderName',
                                                     tableName='demographics',
                                                     clinicalItemTime=None)
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['Caucasian'],
                                                   clinicalItemType='RaceName',
                                                   tableName='demographics',
                                                   clinicalItemTime=None)
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['Hispanic'],
                                                   clinicalItemType='RaceName',
                                                   tableName='demographics',
                                                   clinicalItemTime=None)
        self.factory.addClinicalItemFeatures_UMich(clinicalItemNames=['Birth'],
                                                   clinicalItemType=None,
                                                   tableName='pt_info',
                                                   clinicalItemTime='Birth')
        self.factory.addCharlsonComorbidityFeatures(features='pre')
        self.factory.buildFeatureMatrix()

        resultMatrix = self.factory.readFeatureMatrixFile()
        # for resultrow in resultMatrix:
        #     print resultrow, ','
        # quit()
        df = self.lists_to_pd(resultMatrix[2:])
        df.to_csv('tmp.csv', index=False)
        pd.testing.assert_frame_equal(df, self.lists_to_pd(FMTU.FM_TEST_OUTPUT['OUTPUT_RAW_TABLE']))



def suite():
    """
    Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test".
    """
    suite = unittest.TestSuite()
    #suite.addTest(TestFeatureMatrixFactory("test_addTimeCycleFeatures"));
    #suite.addTest(TestFeatureMatrixFactory("test_buildFeatureMatrix_multiFlowsheet"));
    #suite.addTest(TestFeatureMatrixFactory("test_build_FeatureMatrix_multiLabTest"));
    #suite.addTest(TestFeatureMatrixFactory("test_processPatientListInput"));
    #suite.addTest(TestFeatureMatrixFactory("test_buildFeatureMatrix_multiClinicalItem"));

    # suite.addTest(TestFeatureMatrixFactory("test1"))
    # suite.addTest(TestFeatureMatrixFactory("test_querySexByName"))
    suite.addTest(unittest.makeSuite(TestFeatureMatrixFactory))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
