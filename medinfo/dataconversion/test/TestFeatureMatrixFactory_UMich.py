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
from FeatureMatrixTestData import FM_TEST_INPUT_TABLES, FM_TEST_OUTPUT
from medinfo.dataconversion.DataExtractor import DataExtractor
from medinfo.dataconversion.FeatureMatrixFactory_UMich import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable
from medinfo.db.ResultsFormatter import TextResultsFormatter
from medinfo.db.test.Util import DBTestCase
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader;

from Util import log

class TestFeatureMatrixFactory(DBTestCase):
    def setUp(self):
        """Prepare state for test cases."""
        DBTestCase.setUp(self)
        # StrideLoader.build_stride_psql_schemata()
        # ClinicalItemDataLoader.build_clinical_item_psql_schemata();

        # self._deleteTestRecords()
        # self._insertTestRecords()

        self.factory = FeatureMatrixFactory()
        self.connection = DBUtil.connection();  # Setup a common connection for test cases to work with, can catch in finally tearDown method to close/cleanup

    def _insertTestRecords(self):
        """Populate database for with patient data."""
        # Populate clinical_item_category.
        testRecords = FM_TEST_INPUT_TABLES.get("clinical_item_category")
        DBUtil.insertFile(StringIO(testRecords), "clinical_item_category", \
                            delim="\t")

        # Populate clinical_item.
        testRecords = FM_TEST_INPUT_TABLES.get("clinical_item")
        DBUtil.insertFile(StringIO(testRecords), "clinical_item", delim="\t")

        # Populate patient_item.
        testRecords = FM_TEST_INPUT_TABLES.get("patient_item")
        DBUtil.insertFile(StringIO(testRecords), "patient_item", delim="\t", \
                            dateColFormats={"item_date": None})

        # Populate stride_order_proc.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_order_proc")
        DBUtil.insertFile(StringIO(testRecords), "stride_order_proc", \
                            delim="\t", \
                            dateColFormats={"item_date": None})

        # Populate stride_order_results.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_order_results")
        DBUtil.insertFile(StringIO(testRecords), "stride_order_results", \
                            delim="\t", dateColFormats={"result_time": None})

        # Populate stride_flowsheet.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_flowsheet")
        DBUtil.insertFile(StringIO(testRecords), "stride_flowsheet", \
                            delim="\t", \
                            dateColFormats={"shifted_record_dt_tm": None})

        # Populate stride_order_med.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_order_med")
        DBUtil.insertFile(StringIO(testRecords), "stride_order_med", \
            delim="\t", dateColFormats = {"start_taking_time": None, \
                "end_taking_time": None});

    def _deleteTestRecords(self):
        """Delete test records from database."""
        DBUtil.execute("delete from stride_order_med where order_med_id < 0")
        DBUtil.execute("delete from stride_flowsheet where flo_meas_id < 0")
        DBUtil.execute("delete from stride_order_results where order_proc_id < 0")
        DBUtil.execute("delete from stride_order_proc where order_proc_id < 0")
        DBUtil.execute("delete from patient_item where clinical_item_id < 0")
        # Must delete from clinical_item_assocatiation in order to make CDSS
        # test suite pass. Other suites may update this table.
        DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0")
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0")
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id < 0")


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

    def test1(self):
        # a = DBUtil.execute('select * from labs limit 10;')
        # print a
        pass

    def test_overall_for_single_patient(self):
        pat_id = 4662215939608726971

        cursor = self.connection.cursor()
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("pat_id")
        patientEpisodeQuery.addSelect("order_proc_id")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addFrom("labs")
        patientEpisodeQuery.addWhereEqual('pat_id', '4662215939608726971')
        patientEpisodeQuery.addWhereIn('proc_code', ['CBCP'])
        patientEpisodeQuery.addGroupBy("pat_id")
        patientEpisodeQuery.addGroupBy("order_proc_id")
        results = DBUtil.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        self.assertEqual(len(results), 19)

        # check previous orders of CBCP
        from operator import itemgetter
        results_sorted = sorted(results, key=lambda x:DBUtil.parseDateValue(x[2]))

        order_proc_ids = ['65F56626-06CB-E311-8235-F0921C021BF8',
        '54B48DB8-CFF4-E211-9A1C-00215A9B0094',
        '9CC18DB8-CFF4-E211-9A1C-00215A9B0094',
        '1613786F-65E8-E211-9FAA-00215A9B0094',
        'D9D3DB68-CAEB-E211-9FAA-00215A9B0094',
        '87ED5BEE-CDEB-E211-9FAA-00215A9B0094',
        '2BFD5610-E4EB-E211-9FAA-00215A9B0094',
        '6995554F-D0EB-E211-9FAA-00215A9B0094',
        '4DCF8FBA-CFF4-E211-9A1C-00215A9B0094',
        'C2D28FBA-CFF4-E211-9A1C-00215A9B0094',
        'A6D88FBA-CFF4-E211-9A1C-00215A9B0094',
        '6EDB8FBA-CFF4-E211-9A1C-00215A9B0094',
        '8DE08FBA-CFF4-E211-9A1C-00215A9B0094',
        'E613015B-0393-E311-85F1-6C3BE5AAA6F8',
        '4FD6E85E-DC73-E411-B478-F0921C021BF8',
        'C94440AD-5908-E511-846C-F0921C021BF8',
        'FCA378ED-943C-E611-967E-F0921C021BF8',
        '19167259-40C1-E611-80D2-0025B5000026',
        '99F5D5F9-EC28-E711-80D9-0025B5000026'
                          ]
        self.assertEqualList(order_proc_ids, [x[1] for x in results_sorted])

        num_pre_orders_true_in_730days = [0, 0, 0, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 6, 2, 2, 2, 2, 3]
        pre_day = 730
        num_pre_orders = [0] * 19
        for i in range(1,len(results_sorted)):
            curr_date = DBUtil.parseDateValue(results_sorted[i][2])
            for j in range(i-1,-1,-1):
                prev_date = DBUtil.parseDateValue(DBUtil.parseDateValue(results_sorted[j][2]))
                if (curr_date-prev_date).days < pre_day:
                    num_pre_orders[i] += 1
                else:
                    break
        self.assertEqualList(num_pre_orders, num_pre_orders_true_in_730days)

        date_interested = DBUtil.parseDateValue(results_sorted[7][2])

        # check previous orders of HCT
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("pat_id")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addSelect("ord_num_value")
        patientEpisodeQuery.addFrom("labs")
        patientEpisodeQuery.addWhereEqual('pat_id', '4662215939608726971')
        patientEpisodeQuery.addWhereIn('base_name', ['HCT'])
        patientEpisodeQuery.addGroupBy("pat_id")
        patientEpisodeQuery.addGroupBy("order_proc_id")
        results_HCT = DBUtil.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)
        results_HCT_sorted = sorted(results_HCT, key=lambda x:DBUtil.parseDateValue(x[1]))

        # collect
        all_measures = []
        for i in range(len(results_HCT_sorted)):
            this_date = DBUtil.parseDateValue(results_HCT_sorted[i][1])
            if (date_interested-this_date).days>0 and (date_interested-this_date).days<14: #TODO: might not be exact
                all_measures.append(results_HCT_sorted[i][2])
        print all_measures

    def test_queryMichiganItemsByCategory(self):
        cursor = self.connection.cursor()
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("*")
        patientEpisodeQuery.addFrom("labs")
        patientEpisodeQuery.addWhereEqual('pat_id', '4662215939608726971')
        patientEpisodeQuery.addWhereIn('proc_code', ['CBCP'])
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        self.factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()

        correct_list = [[4662215939608726971, u'2012-02-21 00:00:00'], [4662215939608726971, u'2012-02-13 00:00:00'], [4662215939608726971, u'2012-07-30 00:00:00'], [4662215939608726971, u'2012-05-29 00:00:00'], [4662215939608726971, u'2013-05-14 00:00:00'], [4662215939608726971, u'2012-10-30 00:00:00'], [4662215939608726971, u'2012-11-15 00:00:00'], [4662215939608726971, u'2012-11-02 00:00:00'], [4662215939608726971, u'2013-03-12 00:00:00'], [4662215939608726971, u'2012-05-07 00:00:00'], [4662215939608726971, u'2013-01-30 00:00:00'], [4662215939608726971, u'2013-11-01 00:00:00'], [4662215939608726971, u'2013-05-01 00:00:00'], [4662215939608726971, u'2014-05-06 00:00:00'], [4662215939608726971, u'2004-03-27 11:10:00'], [4662215939608726971, u'2008-02-04 09:30:00'], [4662215939608726971, u'2008-08-28 09:00:00'], [4662215939608726971, u'2012-02-23 09:30:00'], [4662215939608726971, u'2011-02-14 13:00:00'], [4662215939608726971, u'2006-04-03 08:33:00'], [4662215939608726971, u'2007-12-17 09:00:00'], [4662215939608726971, u'2007-12-03 09:00:00'], [4662215939608726971, u'2012-02-13 09:30:00'], [4662215939608726971, u'2012-04-10 10:45:00'], [4662215939608726971, u'2007-01-08 10:00:00'], [4662215939608726971, u'2009-01-29 10:01:00'], [4662215939608726971, u'2008-01-21 08:00:00'], [4662215939608726971, u'2008-05-27 08:00:00'], [4662215939608726971, u'2012-02-14 09:15:00'], [4662215939608726971, u'2012-10-16 09:45:00'], [4662215939608726971, u'2012-02-21 12:15:00'], [4662215939608726971, u'2012-01-31 09:06:00'], [4662215939608726971, u'2009-03-23 11:00:00'], [4662215939608726971, u'2009-09-09 18:51:00'], [4662215939608726971, u'2009-10-23 13:52:00'], [4662215939608726971, u'2011-11-04 15:06:00'], [4662215939608726971, u'2013-05-07 10:15:00'], [4662215939608726971, u'2010-03-26 08:23:00'], [4662215939608726971, u'2011-02-15 08:54:00'], [4662215939608726971, u'2012-01-05 10:16:00'], [4662215939608726971, u'2012-01-19 09:11:00'], [4662215939608726971, u'2013-05-14 11:15:00'], [4662215939608726971, u'2013-05-01 09:15:00'], [4662215939608726971, u'2012-10-30 11:00:00'], [4662215939608726971, u'2013-05-14 12:00:00'], [4662215939608726971, u'2012-10-16 13:45:00'], [4662215939608726971, u'2013-07-05 13:30:00'], [4662215939608726971, u'2013-08-28 14:30:00'], [4662215939608726971, u'2012-05-08 09:00:00'], [4662215939608726971, u'2012-05-07 09:00:00'], [4662215939608726971, u'2014-03-18 08:00:00'], [4662215939608726971, u'2014-05-06 11:45:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2006-07-20 00:00:00'], [4662215939608726971, u'2006-10-25 00:00:00'], [4662215939608726971, u'2007-03-05 00:00:00'], [4662215939608726971, u'2007-06-06 00:00:00'], [4662215939608726971, u'2007-11-27 00:00:00'], [4662215939608726971, u'2007-12-10 00:00:00'], [4662215939608726971, u'2008-04-30 00:00:00'], [4662215939608726971, u'2008-04-23 00:00:00'], [4662215939608726971, u'2008-02-12 00:00:00'], [4662215939608726971, u'2008-05-28 00:00:00'], [4662215939608726971, u'2008-04-16 00:00:00'], [4662215939608726971, u'2008-07-06 00:00:00'], [4662215939608726971, u'2008-11-26 00:00:00'], [4662215939608726971, u'2008-07-29 00:00:00'], [4662215939608726971, u'2009-04-23 00:00:00'], [4662215939608726971, u'2009-04-03 00:00:00'], [4662215939608726971, u'2009-09-10 00:00:00'], [4662215939608726971, u'2010-02-08 00:00:00'], [4662215939608726971, u'2010-11-22 00:00:00'], [4662215939608726971, u'2010-08-23 00:00:00'], [4662215939608726971, u'2010-01-28 00:00:00'], [4662215939608726971, u'2010-07-28 00:00:00'], [4662215939608726971, u'2010-02-04 00:00:00'], [4662215939608726971, u'2010-08-19 00:00:00'], [4662215939608726971, u'2010-09-16 00:00:00'], [4662215939608726971, u'2010-02-03 00:00:00'], [4662215939608726971, u'2011-11-07 00:00:00'], [4662215939608726971, u'2011-07-24 00:00:00'], [4662215939608726971, u'2011-09-07 00:00:00'], [4662215939608726971, u'2011-11-08 00:00:00'], [4662215939608726971, u'2011-03-21 00:00:00'], [4662215939608726971, u'2011-11-15 00:00:00'], [4662215939608726971, u'2011-12-16 00:00:00'], [4662215939608726971, u'2011-01-14 00:00:00'], [4662215939608726971, u'2011-11-18 00:00:00'], [4662215939608726971, u'2011-10-28 00:00:00'], [4662215939608726971, u'2011-12-22 00:00:00'], [4662215939608726971, u'2017-01-11 15:20:00'], [4662215939608726971, u'2017-01-11 15:10:00'], [4662215939608726971, u''], [4662215939608726971, u'2016-10-11 12:30:00'], [4662215939608726971, u'2016-10-11 12:40:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2016-10-12 13:00:00'], [4662215939608726971, u'2016-10-20 10:15:00'], [4662215939608726971, u'2016-10-11 13:20:00'], [4662215939608726971, u'2016-10-11 13:50:00'], [4662215939608726971, u''], [4662215939608726971, u'2016-10-12 07:55:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2016-10-14 14:45:00'], [4662215939608726971, u'2016-10-14 14:30:00'], [4662215939608726971, u'2016-10-13 15:35:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2016-12-29 09:00:00'], [4662215939608726971, u'2017-06-27 08:30:00'], [4662215939608726971, u'2017-06-05 08:00:00'], [4662215939608726971, u'2016-12-13 09:30:00'], [4662215939608726971, u''], [4662215939608726971, u'2017-04-05 15:40:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2017-04-05 16:30:00'], [4662215939608726971, u'2017-07-26 19:00:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2017-04-24 09:00:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2017-05-22 14:30:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2017-07-18 09:30:00'], [4662215939608726971, u'2017-07-25 09:30:00'], [4662215939608726971, u'2017-08-01 09:30:00'], [4662215939608726971, u'2017-07-11 09:30:00'], [4662215939608726971, u'2017-06-18 16:00:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2017-12-11 08:00:00'], [4662215939608726971, u'2018-06-11 08:00:00'], [4662215939608726971, u'2018-06-26 08:30:00'], [4662215939608726971, u'2018-01-29 07:30:00'], [4662215939608726971, u'2013-11-12 00:00:00'], [4662215939608726971, u'2014-02-10 10:30:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2014-02-17 11:00:00'], [4662215939608726971, u'2014-03-17 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2015-03-30 08:00:00'], [4662215939608726971, u'2014-03-24 11:15:00'], [4662215939608726971, u'2014-03-31 11:15:00'], [4662215939608726971, u'2014-04-07 11:15:00'], [4662215939608726971, u'2014-04-14 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2014-04-21 11:00:00'], [4662215939608726971, u'2014-05-05 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2014-11-11 14:15:00'], [4662215939608726971, u'2014-05-12 11:00:00'], [4662215939608726971, u'2014-05-06 12:15:00'], [4662215939608726971, u'2014-11-24 00:00:00'], [4662215939608726971, u'2014-11-24 07:20:00'], [4662215939608726971, u'2014-05-12 00:00:00'], [4662215939608726971, u'2014-05-12 08:10:00'], [4662215939608726971, u'2014-05-19 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2015-04-21 10:18:00'], [4662215939608726971, u'2015-09-01 08:30:00'], [4662215939608726971, u'2015-12-07 00:00:00'], [4662215939608726971, u'2015-06-01 08:00:00'], [4662215939608726971, u'2015-06-08 00:00:00'], [4662215939608726971, u'2015-06-04 00:00:00'], [4662215939608726971, u'2015-12-07 07:20:00'], [4662215939608726971, u'2015-06-01 07:29:00'], [4662215939608726971, u'2015-06-01 12:24:00'], [4662215939608726971, u'2012-10-31 09:14:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-02-23 09:24:29'], [4662215939608726971, u'2012-10-31 09:20:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-05-22 03:31:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-13 07:40:00'], [4662215939608726971, u'2012-01-13 00:00:00'], [4662215939608726971, u'2012-01-27 00:00:00'], [4662215939608726971, u'2012-07-28 11:47:00'], [4662215939608726971, u'2012-08-24 18:21:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-05-22 03:31:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-05-22 03:31:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-11-06 19:42:00'], [4662215939608726971, u'2012-08-09 01:12:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-10-09 16:52:00'], [4662215939608726971, u'2012-01-31 00:00:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-07-10 15:29:00'], [4662215939608726971, u'2015-05-21 08:30:00'], [4662215939608726971, u'2012-07-30 07:53:00'], [4662215939608726971, u'2011-12-30 00:00:00'], [4662215939608726971, u'2012-07-27 20:04:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-11-17 21:39:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2011-12-14 00:00:00'], [4662215939608726971, u'2011-12-14 00:00:00'], [4662215939608726971, u'2012-10-30 09:54:00'], [4662215939608726971, u'2012-08-04 18:28:00'], [4662215939608726971, u'2013-11-04 21:05:00'], [4662215939608726971, u'2013-05-14 11:19:00'], [4662215939608726971, u'2013-10-31 11:38:00'], [4662215939608726971, u'2013-09-04 09:16:00'], [4662215939608726971, u'2013-12-02 09:52:00'], [4662215939608726971, u'2013-11-01 08:30:00'], [4662215939608726971, u'2013-11-03 09:30:00'], [4662215939608726971, u'2013-02-06 10:46:00'], [4662215939608726971, u'2012-02-14 09:09:37'], [4662215939608726971, u'2013-05-15 11:52:00'], [4662215939608726971, u'2013-05-02 10:56:00'], [4662215939608726971, u'2013-12-09 13:05:00'], [4662215939608726971, u'2013-05-01 08:35:00'], [4662215939608726971, u'2013-11-11 10:03:00'], [4662215939608726971, u'2013-11-12 08:10:00'], [4662215939608726971, u'2013-09-03 13:33:00'], [4662215939608726971, u'2013-02-13 16:57:00'], [4662215939608726971, u'2013-11-14 15:27:00'], [4662215939608726971, u'2013-06-19 15:06:00'], [4662215939608726971, u'2013-11-08 11:16:00'], [4662215939608726971, u'2013-05-15 11:52:00'], [4662215939608726971, u'2013-11-27 16:53:00'], [4662215939608726971, u'2013-09-29 19:22:00'], [4662215939608726971, u'2013-11-03 09:29:00'], [4662215939608726971, u'2013-11-22 09:40:00'], [4662215939608726971, u'2013-11-13 12:52:00'], [4662215939608726971, u'2013-08-28 08:45:00'], [4662215939608726971, u'2013-01-30 08:01:00'], [4662215939608726971, u'2013-12-24 10:12:00'], [4662215939608726971, u'2013-03-12 10:22:00'], [4662215939608726971, u'2013-11-11 09:56:00'], [4662215939608726971, u'2013-09-05 08:59:00'], [4662215939608726971, u'2013-11-27 16:53:00'], [4662215939608726971, u'2014-05-12 16:56:00'], [4662215939608726971, u'2014-12-30 14:28:00'], [4662215939608726971, u'2014-05-08 08:15:00'], [4662215939608726971, u'2014-03-18 08:07:00'], [4662215939608726971, u'2014-11-20 14:27:00'], [4662215939608726971, u'2014-05-07 11:28:00'], [4662215939608726971, u'2014-03-17 15:38:00'], [4662215939608726971, u'2014-05-06 11:37:00'], [4662215939608726971, u'2014-05-13 15:36:00'], [4662215939608726971, u'2014-05-28 10:56:00'], [4662215939608726971, u'2014-01-03 07:47:00'], [4662215939608726971, u'2014-11-24 07:24:00'], [4662215939608726971, u'2014-03-17 17:24:00'], [4662215939608726971, u'2014-01-16 08:59:00'], [4662215939608726971, u'2014-01-16 15:44:00'], [4662215939608726971, u'2014-05-07 13:57:00'], [4662215939608726971, u'2014-11-25 14:47:00'], [4662215939608726971, u'2014-05-12 08:12:00'], [4662215939608726971, u'2014-05-07 13:51:00'], [4662215939608726971, u'2014-07-23 18:54:00'], [4662215939608726971, u'2014-03-17 15:51:00'], [4662215939608726971, u'2014-11-21 16:12:00'], [4662215939608726971, u'2014-01-14 11:56:00'], [4662215939608726971, u'2014-11-06 08:24:00'], [4662215939608726971, u'2014-12-05 13:32:00'], [4662215939608726971, u'2015-01-27 00:00:00'], [4662215939608726971, u'2015-01-31 09:51:00'], [4662215939608726971, u'2015-03-11 00:00:00'], [4662215939608726971, u'2015-01-28 07:47:00'], [4662215939608726971, u'2014-05-12 08:00:00'], [4662215939608726971, u'2014-11-25 12:40:00'], [4662215939608726971, u'2014-08-04 16:31:00'], [4662215939608726971, u'2016-01-16 14:55:00'], [4662215939608726971, u'2015-03-11 08:12:00'], [4662215939608726971, u'2015-03-16 08:12:00'], [4662215939608726971, u'2015-03-30 08:02:00'], [4662215939608726971, u'2015-07-15 00:00:00'], [4662215939608726971, u'2016-06-27 09:00:00'], [4662215939608726971, u'2016-06-30 11:00:00'], [4662215939608726971, u'2016-06-29 09:46:00'], [4662215939608726971, u'2016-06-27 08:15:00'], [4662215939608726971, u'2016-12-13 09:45:00'], [4662215939608726971, u'2014-02-24 11:00:00'], [4662215939608726971, u'2014-03-03 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2014-03-10 11:00:00'], [4662215939608726971, u'2015-12-07 08:30:00'], [4662215939608726971, u'2015-12-07 07:24:00'], [4662215939608726971, u'2015-12-11 00:00:00'], [4662215939608726971, u'2015-12-12 08:50:00'], [4662215939608726971, u'2015-12-08 15:41:00'], [4662215939608726971, u'2015-12-12 10:29:00'], [4662215939608726971, u'2016-07-01 08:00:00'], [4662215939608726971, u'2016-07-01 07:50:00'], [4662215939608726971, u'2016-04-26 00:00:00'], [4662215939608726971, u'2015-11-03 08:30:00'], [4662215939608726971, u'2015-11-17 10:30:00'], [4662215939608726971, u'2016-07-06 13:15:00'], [4662215939608726971, u'2016-07-13 15:12:00'], [4662215939608726971, u'2016-04-26 11:06:00'], [4662215939608726971, u'2015-06-10 15:31:00'], [4662215939608726971, u'2015-06-04 12:10:00'], [4662215939608726971, u'2015-06-08 10:00:00'], [4662215939608726971, u'2015-06-10 15:34:00'], [4662215939608726971, u'2015-07-21 00:00:00'], [4662215939608726971, u'2016-07-26 10:00:00'], [4662215939608726971, u'2014-11-20 14:15:00'], [4662215939608726971, u''], [4662215939608726971, u''], [4662215939608726971, u'2014-11-21 00:00:00'], [4662215939608726971, u'2015-01-28 00:00:00'], [4662215939608726971, u'2015-06-01 00:00:00'], [4662215939608726971, u'2014-11-24 08:15:00'], [4662215939608726971, u'2015-01-27 15:00:00'], [4662215939608726971, u'2015-06-01 07:20:00'], [4662215939608726971, u'2015-03-11 00:00:00'], [4662215939608726971, u'2014-12-23 00:00:00'], [4662215939608726971, u'2014-06-02 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2014-06-09 11:00:00'], [4662215939608726971, u''], [4662215939608726971, u'2014-06-24 11:00:00'], [4662215939608726971, u'2014-07-08 11:00:00'], [4662215939608726971, u'2014-07-22 11:00:00'], [4662215939608726971, u'2016-06-27 08:20:00'], [4662215939608726971, u'2016-06-27 08:10:00'], [4662215939608726971, u'2016-05-25 10:55:00'], [4662215939608726971, u'2015-12-29 10:03:00'], [4662215939608726971, u'2017-02-23 14:30:00'], [4662215939608726971, u'2017-02-27 08:00:00'], [4662215939608726971, u'2015-07-15 09:18:00'], [4662215939608726971, u'2015-07-21 15:42:00'], [4662215939608726971, u'2015-08-19 12:30:00']]


        cursor = self.connection.cursor()

        label = 'AdmitDxDate'
        tableName = 'encounters'
        componentItemEvents = self.factory._queryMichiganItemsByCategory(label, tableName)

        for componentItemEvent in componentItemEvents:
            pass
            # print 'componentItemEvent:', componentItemEvent
        self.assertEqualSet(correct_list, componentItemEvents)

    def test_querySexByName(self):
        cursor = self.connection.cursor()
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("*")
        patientEpisodeQuery.addFrom("demographics")
        # patientEpisodeQuery.addWhereEqual('pat_id', '4662215939608726971')
        # patientEpisodeQuery.addWhereIn('proc_code', ['CBCP'])
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        correct_list = [[7058194537092767591], [8765351125316159366], [974665342874392077], [4662215939608726971], [788761694652280543]]

        self.factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()
        clinicalItemNames = ['Male']
        clinicalItemType = 'GenderName'
        tableName = 'demographics'
        clinicalItemTime = None

        componentItemEvents = self.factory._queryMichiganItemsByName(clinicalItemNames, clinicalItemType, tableName,
                                                                     clinicalItemTime)
        male_list = [[x[0]] for x in componentItemEvents]
        self.assertEqualSet(correct_list, male_list)

    def test_queryComponentEventsByName(self):
        cursor = self.connection.cursor()
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("*")
        patientEpisodeQuery.addFrom("labs")
        patientEpisodeQuery.addWhereEqual('pat_id','4662215939608726971')
        patientEpisodeQuery.addWhereIn('proc_code',['CBCP'])
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        self.factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()
        # resultEpisodeIterator = self.factory.getPatientEpisodeIterator()
        #
        # patientIds = set()
        # for episode in resultEpisodeIterator:
        #     print episode
        #     patientIds.add(int(episode['pat_id']))
        # print 'patientIds:', patientIds

        correct_list = [[4662215939608726971, u'2002-01-03 19:30:00'], [4662215939608726971, u'2004-03-27 12:20:00'], [4662215939608726971, u'2008-02-12 10:07:00'], [4662215939608726971, u'2008-04-16 14:50:00'], [4662215939608726971, u'2011-07-24 21:40:00'], [4662215939608726971, u'2011-09-07 11:46:00'], [4662215939608726971, u'2011-10-28 09:33:00'], [4662215939608726971, u'2011-11-08 09:38:00'], [4662215939608726971, u'2012-02-13 10:08:00'], [4662215939608726971, u'2012-02-21 12:26:00'], [4662215939608726971, u'2012-05-29 10:29:00'], [4662215939608726971, u'2012-10-30 11:02:00'], [4662215939608726971, u'2013-05-14 11:57:00'], [4662215939608726971, u'2013-11-01 08:31:00'], [4662215939608726971, u'2014-11-24 08:08:00'], [4662215939608726971, u'2015-06-01 07:58:00'], [4662215939608726971, u'2016-06-27 09:00:00'], [4662215939608726971, u'2016-12-13 09:57:00'], [4662215939608726971, u'2017-04-24 09:13:00']]


        clinicalItemNames = ['CBCP']
        clinicalItemType = 'proc_code'
        tableName = 'labs'
        clinicalItemTime = 'order_time'
        componentItemEvents = self.factory._queryMichiganItemsByName(clinicalItemNames, clinicalItemType, tableName, clinicalItemTime)
        for componentItemEvent in componentItemEvents:
            print componentItemEvent
        self.assertEqualSet(correct_list, componentItemEvents)

    def test_queryAllRaces(self):
        print self.factory.queryAllRaces()

    def test_queryPatientEpisodes(self):
        cursor = self.connection.cursor()

        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("pat_id")
        patientEpisodeQuery.addSelect("order_proc_id")
        patientEpisodeQuery.addSelect("proc_code")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addFrom("labs")
        patientEpisodeQuery.addWhereEqual("proc_code", "CBCP")
        patientEpisodeQuery.addGroupBy("pat_id, order_proc_id, proc_code, order_time")
        patientEpisodeQuery.addOrderBy("pat_id, order_proc_id, proc_code, order_time")
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)
        print 'os.getcwd():', os.getcwd()

        self.factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()
        resultEpisodeIterator = self.factory.getPatientEpisodeIterator()
        # print 'os.getcwd():', os.getcwd()
        # quit()

        patientIds = set()
        for episode in resultEpisodeIterator:
            # print episode
            patientIds.add(int(episode['pat_id']))

        list_pre_queried = [-3384542270496665494,1262980084096039344,4662215939608726971,7058194537092767591,8765351125316159366]

        self.assertEqualSet(patientIds, set(list_pre_queried))

        print patientIds
        print sorted(patientIds)
        print list(patientIds)
        print list(set(list_pre_queried))


        print '4662215939608726971:', ('4662215939608726971' in patientIds)

        clinicalItemNames = ['WBC']
        clinicalItemType = 'base_name'
        tableName = 'labs'
        clinicalItemTime = None#['']
        # print 'self.factory.getPatientEpisodeIterator():', self.factory.getPatientEpisodeIterator()
        # print patientIds
        print self.factory._queryMichiganItemsByName(clinicalItemNames, clinicalItemType, tableName, clinicalItemTime)



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
