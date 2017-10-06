#!/usr/bin/env python
"""
Test suite for respective module in application package.
"""

import datetime
import unittest

from Const import RUNNER_VERBOSITY
from cStringIO import StringIO
from FeatureMatrixTestData import FM_TEST_INPUT_TABLES, FM_TEST_OUTPUT
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.db.test.Util import DBTestCase

from Util import log

class TestFeatureMatrixFactory(DBTestCase):
    def setUp(self):
        """Prepare state for test cases."""
        DBTestCase.setUp(self);
        self._deleteTestRecords()
        self._insertTestRecords()

    def _insertTestRecords(self):
        """Populate database for with patient data."""
        # Populate clinical_item_category.
        testRecords = FM_TEST_INPUT_TABLES.get("clinical_item_category")
        DBUtil.insertFile(StringIO(testRecords), "clinical_item_category", \
                            delim="\t");

        # Populate clinical_item.
        testRecords = FM_TEST_INPUT_TABLES.get("clinical_item")
        DBUtil.insertFile(StringIO(testRecords), "clinical_item", delim="\t");

        # Populate patient_item.
        testRecords = FM_TEST_INPUT_TABLES.get("patient_item")
        DBUtil.insertFile(StringIO(testRecords), "patient_item", delim="\t", \
                            dateColFormats={"item_date": None});

        # Populate stride_order_proc.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_order_proc")
        DBUtil.insertFile(StringIO(testRecords), "stride_order_proc", \
                            delim="\t", \
                            dateColFormats={"item_date": None});

        # Populate stride_order_results.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_order_results")
        DBUtil.insertFile(StringIO(testRecords), "stride_order_results", \
                            delim="\t", dateColFormats={"result_time": None});

        # Populate stride_flowsheet.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_flowsheet")
        DBUtil.insertFile(StringIO(testRecords), "stride_flowsheet", \
                            delim="\t", \
                            dateColFormats={"shifted_record_dt_tm": None});

        # Populate stride_order_med.
        testRecords = FM_TEST_INPUT_TABLES.get("stride_order_med")
        DBUtil.insertFile(StringIO(testRecords), "stride_order_med", \
            delim="\t", dateColFormats = {"start_taking_time": None, \
                "end_taking_time": None});

    def _deleteTestRecords(self):
        """Delete test records from database."""
        DBUtil.execute("delete from stride_order_med where order_med_id < 0");
        DBUtil.execute("delete from stride_flowsheet where flo_meas_id < 0");
        DBUtil.execute("delete from stride_order_results where order_proc_id < 0");
        DBUtil.execute("delete from stride_order_proc where order_proc_id < 0");
        DBUtil.execute("delete from patient_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
        DBUtil.execute("delete from clinical_item_category where clinical_item_category_id < 0");

    def tearDown(self):
        """Restore state from any setUp or test steps."""
        self._deleteTestRecords();
        DBTestCase.tearDown(self);

    def test_dbCache(self):
        """Test database result caching."""
        factory = FeatureMatrixFactory(cacheDBResults=False)
        self.assertEqual(factory.dbCache, None)

        factory = FeatureMatrixFactory()
        self.assertEqual(type(factory.dbCache), type(dict()))

    def test_processPatientListInput(self):
        """Test processPatientListInput()."""
        # Initialize FeatureMatrixFactory.
        factory = FeatureMatrixFactory()

        # Verify FeatureMatrixFactory throws Error if patientListInput
        # has not been set.
        with self.assertRaises(ValueError):
            factory.processPatientListInput()

        # Initialize DB cursor.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Build SQL query for list of patients.
        patientListQuery = SQLQuery()
        patientListQuery.addSelect("CAST(pat_id AS bigint)")
        patientListQuery.addFrom("stride_order_proc")
        patientListQuery.addWhere("proc_code = 'LABMETB'")
        patientListQuery.addGroupBy("pat_id")
        patientListQuery.addOrderBy("1 ASC")
        cursor.execute(str(patientListQuery), patientListQuery.params)

        # Set and process patientListInput.
        factory.setPatientListInput(cursor, "pat_id")
        factory.processPatientListInput()
        resultPatientIterator = factory.getPatientListIterator()

        # Verify results.
        expectedPatientList = ["-789", "-456", "-123"]
        for expectedPatientId in expectedPatientList:
            resultPatientId = resultPatientIterator.next()['pat_id']
            self.assertEqual(resultPatientId, expectedPatientId)

        # Build TSV file for list of patients.
        patientList = \
            "patient_item_id\tpatient_id\tclinical_item_id\titem_date\n\
            -1000\t-123\t-100\t10/6/2113 10:20\n\
            -2000\t-123\t-200\t10/6/2113 11:20\n\
            -2500\t-123\t-100\t10/7/2113 11:20\n\
            -3000\t-456\t-100\t11/6/2113 10:20\n\
            -6000\t-789\t-200\t12/6/2113 11:20\n"
        patientListTsv = open("patient_list.tsv", "w")
        patientListTsv.write(patientList)
        patientListTsv.close()

        # Initialize new FeatureMatrixFactory.
        factory = FeatureMatrixFactory()

        # Set and process patientListInput.
        patientListTsv = open("patient_list.tsv", "r")
        factory.setPatientListInput(patientListTsv, "patient_id")
        factory.processPatientListInput()
        resultPatientIterator = factory.getPatientListIterator()

        # Verify results.
        expectedPatientList = ["-123", "-123", "-123", "-456", "-789"]
        for expectedPatientId in expectedPatientList:
            resultPatientId = resultPatientIterator.next()['patient_id']
            self.assertEqual(resultPatientId, expectedPatientId)

    def test_buildFeatureMatrix_multiClinicalItem(self):
        """Test _buildFeatureMatrix()."""
        # Initialize FeatureMatrixFactory.
        factory = FeatureMatrixFactory()

        # Verify FeatureMatrixFactory throws Error if patientEpisodeInput
        # has not been set.
        with self.assertRaises(ValueError):
            factory.processPatientEpisodeInput()

        # Initialize DB cursor.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Build SQL query for list of patient episodes.
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("CAST(pat_id AS bigint)")
        patientEpisodeQuery.addSelect("sop.order_proc_id AS order_proc_id")
        patientEpisodeQuery.addSelect("proc_code")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addSelect("COUNT(CASE result_in_range_yn WHEN 'Y' THEN 1 ELSE null END) AS normal_results")
        patientEpisodeQuery.addFrom("stride_order_proc AS sop")
        patientEpisodeQuery.addFrom("stride_order_results AS sor")
        patientEpisodeQuery.addWhere("sop.order_proc_id = sor.order_proc_id")
        patientEpisodeQuery.addWhereEqual("proc_code", "LABMETB")
        patientEpisodeQuery.addGroupBy("pat_id, sop.order_proc_id, proc_code, order_time")
        patientEpisodeQuery.addOrderBy("pat_id, sop.order_proc_id, proc_code, order_time")
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        # Set and process patientEpisodeInput.
        factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        factory.processPatientEpisodeInput()
        resultEpisodeIterator = factory.getPatientEpisodeIterator()
        resultPatientEpisodes = list()
        for episode in resultEpisodeIterator:
            episode["pat_id"] = int(episode["pat_id"])
            episode["order_time"] = DBUtil.parseDateValue(episode["order_time"])
            resultPatientEpisodes.append(episode)

        # Verify results (note sort order).
        expectedPatientEpisodes = FM_TEST_OUTPUT["test_processPatientEpisodeInput"]
        self.assertEqualList(resultPatientEpisodes, expectedPatientEpisodes)

        # Add TestItem100 and TestItem200 clinical item data.
        factory.addClinicalItemFeatures(["TestItem100"])
        factory.addClinicalItemFeatures(["TestItem200"])
        factory.buildFeatureMatrix()
        resultMatrix = factory.readFeatureMatrixFile()
        expectedMatrix = FM_TEST_OUTPUT["test_buildFeatureMatrix_multiClinicalItem"]

        self.assertEqualList(resultMatrix, expectedMatrix)

    def test_build_FeatureMatrix_multiLabTest(self):
        """
        Test buildFeatureMatrix() and addLabFeatures().
        """
        # Initialize FeatureMatrixFactory.
        factory = FeatureMatrixFactory()

        # Verify FeatureMatrixFactory throws Error if patientEpisodeInput
        # has not been set.
        with self.assertRaises(ValueError):
            factory.processPatientEpisodeInput()

        # Initialize DB cursor.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Build SQL query for list of patient episodes.
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("CAST(pat_id AS bigint)")
        patientEpisodeQuery.addSelect("sop.order_proc_id AS order_proc_id")
        patientEpisodeQuery.addSelect("proc_code")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addSelect("COUNT(CASE result_in_range_yn WHEN 'Y' THEN 1 ELSE null END) AS normal_results")
        patientEpisodeQuery.addFrom("stride_order_proc AS sop")
        patientEpisodeQuery.addFrom("stride_order_results AS sor")
        patientEpisodeQuery.addWhere("sop.order_proc_id = sor.order_proc_id")
        patientEpisodeQuery.addWhereEqual("proc_code", "LABMETB")
        patientEpisodeQuery.addGroupBy("pat_id, sop.order_proc_id, proc_code, order_time")
        patientEpisodeQuery.addOrderBy("pat_id, sop.order_proc_id, proc_code, order_time")
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        # Set and process patientEpisodeInput.
        factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        factory.processPatientEpisodeInput()
        resultEpisodeIterator = factory.getPatientEpisodeIterator()
        resultPatientEpisodes = list()
        for episode in resultEpisodeIterator:
            episode["pat_id"] = int(episode["pat_id"])
            episode["order_time"] = DBUtil.parseDateValue(episode["order_time"])
            resultPatientEpisodes.append(episode)

        # Verify results (note sort order).
        expectedPatientEpisodes = FM_TEST_OUTPUT["test_processPatientEpisodeInput"]
        self.assertEqualList(resultPatientEpisodes, expectedPatientEpisodes)

        # Add TNI and CR lab result data. LAC doesn't exist in data.
        labBaseNames = ["TNI", "CR", "LAC"]
        # Look for lab data 90 days before each episode, but never afterself.
        preTimeDelta = datetime.timedelta(-90)
        postTimeDelta = datetime.timedelta(0)
        factory.addLabResultFeatures(labBaseNames, preTimeDelta, postTimeDelta)
        factory.buildFeatureMatrix()
        resultMatrix = factory.readFeatureMatrixFile()

        # Verify results.
        expectedMatrix = FM_TEST_OUTPUT["test_buildFeatureMatrix_multiLabTest"]["expectedMatrix"]
        self.assertEqualList(resultMatrix, expectedMatrix)

    def test_buildFeatureMatrix_flowsheet(self):
        """
        Test buildFeatureMatrix and addFlowsheet.
        """

        # Initialize FeatureMatrixFactory.
        factory = FeatureMatrixFactory()

        # Verify FeatureMatrixFactory throws Error if patientEpisodeInput
        # has not been set.
        with self.assertRaises(ValueError):
            factory.processPatientEpisodeInput()

        # Initialize DB cursor.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Build SQL query for list of patient episodes.
        patientEpisodeQuery = SQLQuery()
        patientEpisodeQuery.addSelect("CAST(pat_id AS bigint)")
        patientEpisodeQuery.addSelect("sop.order_proc_id AS order_proc_id")
        patientEpisodeQuery.addSelect("proc_code")
        patientEpisodeQuery.addSelect("order_time")
        patientEpisodeQuery.addSelect("COUNT(CASE result_in_range_yn WHEN 'Y' THEN 1 ELSE null END) AS normal_results")
        patientEpisodeQuery.addFrom("stride_order_proc AS sop")
        patientEpisodeQuery.addFrom("stride_order_results AS sor")
        patientEpisodeQuery.addWhere("sop.order_proc_id = sor.order_proc_id")
        patientEpisodeQuery.addWhereEqual("proc_code", "LABMETB")
        patientEpisodeQuery.addGroupBy("pat_id, sop.order_proc_id, proc_code, order_time")
        patientEpisodeQuery.addOrderBy("pat_id, sop.order_proc_id, proc_code, order_time")
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        # Set and process patientEpisodeInput.
        factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        factory.processPatientEpisodeInput()
        resultEpisodeIterator = factory.getPatientEpisodeIterator()
        resultPatientEpisodes = list()
        for episode in resultEpisodeIterator:
            episode["pat_id"] = int(episode["pat_id"])
            episode["order_time"] = DBUtil.parseDateValue(episode["order_time"])
            resultPatientEpisodes.append(episode)

        # Verify results (note sort order).
        expectedPatientEpisodes = FM_TEST_OUTPUT["test_processPatientEpisodeInput"]
        self.assertEqualList(resultPatientEpisodes, expectedPatientEpisodes)

        # Add flowsheet features.
        flowsheetNames = ["Resp","FiO2","Glasgow Coma Scale Score"]
        # Look for lab data 90 days before each episode, but never afterself.
        preTimeDelta = datetime.timedelta(-90)
        postTimeDelta = datetime.timedelta(0)
        factory.addFlowsheetFeatures(flowsheetNames, preTimeDelta, postTimeDelta)
        factory.buildFeatureMatrix()
        resultMatrix = factory.readFeatureMatrixFile()

        # Verify results.
        expectedMatrix = FM_TEST_OUTPUT["test_buildFeatureMatrix_multiFlowsheet"]["expectedMatrix"]
        self.assertEqualList(resultMatrix, expectedMatrix)

def suite():
    """
    Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test".
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFeatureMatrixFactory))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
