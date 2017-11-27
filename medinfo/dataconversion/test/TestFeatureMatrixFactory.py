#!/usr/bin/env python
"""
Test suite for respective module in application package.
"""

import datetime
import os
import time
import unittest

from Const import RUNNER_VERBOSITY
from cStringIO import StringIO
from FeatureMatrixTestData import FM_TEST_INPUT_TABLES, FM_TEST_OUTPUT
from medinfo.dataconversion.DataExtractor import DataExtractor
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable
from medinfo.db.ResultsFormatter import TextResultsFormatter
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

        # Clean up patient_list.
        try:
            os.remove("patient_list.tsv")
            os.remove("fmf.patient_list.tsv")
        except OSError:
            pass

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

        try:
            os.remove(factory.getMatrixFileName())
        except OSError:
            pass

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
        factory.addLabResultFeatures(labBaseNames, False, preTimeDelta, postTimeDelta)
        factory.buildFeatureMatrix()
        resultMatrix = factory.readFeatureMatrixFile()

        # Verify results.
        expectedMatrix = FM_TEST_OUTPUT["test_buildFeatureMatrix_multiLabTest"]["expectedMatrix"]
        self.assertEqualList(resultMatrix, expectedMatrix)

        try:
            os.remove(factory.getMatrixFileName())
        except OSError:
            pass

    def test_buildFeatureMatrix_multiFlowsheet(self):
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

        try:
            os.remove(factory.getMatrixFileName())
        except OSError:
            pass

    def test_addTimeCycleFeatures(self):
        """
        Test .addTimeCycleFeatures()
        """
        # Initialize DB cursor.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Initialize FeatureMatrixFactory.
        factory = FeatureMatrixFactory()

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

        # Add time cycle features.
        factory.addTimeCycleFeatures("order_time", "month")
        factory.addTimeCycleFeatures("order_time", "hour")

        # Verify output.
        factory.buildFeatureMatrix()
        resultMatrix = factory.readFeatureMatrixFile()
        expectedMatrix = FM_TEST_OUTPUT["test_addTimeCycleFeatures"]["expectedMatrix"]
        self.assertEqualList(resultMatrix, expectedMatrix)

        # Clean up feature matrix.
        try:
            os.remove(factory.getMatrixFileName())
        except OSError:
            pass

    def test_loadMapData(self):
        factory = FeatureMatrixFactory()

        # Depends on external data file
        reader = factory.loadMapData("CharlsonComorbidity-ICD9CM")
        charlsonByICD9 = dict()

        for row in reader:
            charlsonByICD9[row["icd9cm"]] = row["charlson"]

        self.assertEqual("Dementia", charlsonByICD9["294.1"])
        self.assertEqual("Dementia", charlsonByICD9["331.2"])
        self.assertEqual("COPD", charlsonByICD9["490"])
        self.assertEqual("COPD", charlsonByICD9["416.8"])
        self.assertEqual("Malignancy Metastatic", charlsonByICD9["199"])
        self.assertEqual("AIDS/HIV", charlsonByICD9["042"])

    def test_performance(self):
        """
        Test performance against DataExtractor.
        """
        # Initialize DB cursor.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Initialize FeatureMatrixFactory.
        factoryStart = time.time()
        factory = FeatureMatrixFactory()

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
        patientEpisodeQuery.addWhereIn("proc_code", ["Foo", "Bar", "Baz","Qux"])
        patientEpisodeQuery.addGroupBy("pat_id, sop.order_proc_id, proc_code, order_time")
        patientEpisodeQuery.addOrderBy("pat_id, sop.order_proc_id, proc_code, order_time")
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        # Set and process patientEpisodeInput.
        factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        factory.processPatientEpisodeInput()

        # Look for lab data 90 days before each episode, but never afterself.
        preTimeDelta = datetime.timedelta(-90)
        postTimeDelta = datetime.timedelta(0)

        # Add clinical item features.
        factory.addClinicalItemFeatures(["PerfItem300"])
        factory.addClinicalItemFeatures(["PerfItem400"])
        factory.addClinicalItemFeatures(["PerfItem500"])

        # Add lab result features.
        factory.addLabResultFeatures(["Foo"], preTimeDelta, postTimeDelta)
        factory.addLabResultFeatures(["Bar"], preTimeDelta, postTimeDelta)
        factory.addLabResultFeatures(["Baz"], preTimeDelta, postTimeDelta)
        factory.addLabResultFeatures(["Qux"], preTimeDelta, postTimeDelta)

        # Add flowsheet features.
        factory.addFlowsheetFeatures(["Perflow"], preTimeDelta, postTimeDelta)

        # Build matrix.
        factory.buildFeatureMatrix()

        # Stop timer.
        factoryStop = time.time()

        # Initialize DataExtractor.
        extractorStart = time.time()
        extractor = DataExtractor()
        extractor.dataCache = dict()

        # Initialize output file.
        outFile = open("extractor.feature_matrix.tab.gz","w")
        formatter = TextResultsFormatter(outFile)

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
        patientEpisodeQuery.addWhereIn("proc_code", ["Foo", "Bar", "Baz","Qux"])
        patientEpisodeQuery.addGroupBy("pat_id, sop.order_proc_id, proc_code, order_time")
        patientEpisodeQuery.addOrderBy("pat_id, sop.order_proc_id, proc_code, order_time")
        cursor.execute(str(patientEpisodeQuery), patientEpisodeQuery.params)

        # Process patient episodes.
        patientEpisodes = list()
        row = cursor.fetchone()

        while row is not None:
            (pat_id, order_proc_id, proc_code, order_time, normal_results) = row
            patientEpisode = \
                RowItemModel \
                (
                    {
                        "patient_id": pat_id,
                        "order_proc_id": order_proc_id,
                        "proc_code": proc_code,
                        "order_time": order_time,
                        "result_normal_count": normal_results
                    }
                )
            patientEpisodes.append(patientEpisode)
            row = cursor.fetchone()

        # Initialize patient data.
        lastPatientId = None
        colNames = None
        patientEpisodeByIndexTime = None

        # Look for lab data 90 days before each episode, but never afterself.
        preTimeDelta = datetime.timedelta(-90)
        postTimeDelta = datetime.timedelta(0)

        # Populate patient data.
        tempColNames = \
            ["patient_id", "order_proc_id", "proc_code", "order_time",
                "result_normal_count"]
        for patientEpisode in patientEpisodes:
            patientId = patientEpisode["patient_id"]

            if lastPatientId is not None and lastPatientId != patientId:
                # New patient ID so start querying for patient specific data and
                # populating patient episode data.

                # Clinical Item (PerfItem300)
                eventTimes = extractor.parseClinicalItemData_singlePatient(\
                    modelListFromTable(extractor.queryClinicalItemsByName(\
                        ("PerfItem300",), [patientId])))
                tempColNames.extend(\
                    extractor.addClinicalItemFeatures_singlePatient(\
                    eventTimes, patientEpisodeByIndexTime, "PerfItem300", \
                    daysBins=[]))

                # Clinical Item (PerfItem400)
                eventTimes = extractor.parseClinicalItemData_singlePatient(\
                    modelListFromTable(extractor.queryClinicalItemsByName(\
                        ("PerfItem400",), [patientId])))
                tempColNames.extend(\
                    extractor.addClinicalItemFeatures_singlePatient(\
                    eventTimes, patientEpisodeByIndexTime, "PerfItem300", \
                    daysBins=[]))

                # Clinical Item (PerfItem500)
                eventTimes = extractor.parseClinicalItemData_singlePatient(\
                    modelListFromTable(extractor.queryClinicalItemsByName(\
                        ("PerfItem500",), [patientId])))
                tempColNames.extend(\
                    extractor.addClinicalItemFeatures_singlePatient(\
                    eventTimes, patientEpisodeByIndexTime, "PerfItem300", \
                    daysBins=[]))

                # Lab Result (Foo)
                labResultTable = extractor.queryLabResults(["Foo"], [patientId])
                labsByBaseName = extractor.parseLabResultsData_singlePatient(\
                    modelListFromTable(labResultTable))
                tempColNames.extend(extractor.addLabFeatures_singlePatient(\
                    patientEpisodeByIndexTime, labsByBaseName, ["Foo"], \
                    preTimeDelta, postTimeDelta))

                # Lab Result (Bar)
                labResultTable = extractor.queryLabResults(["Bar"], [patientId])
                labsByBaseName = extractor.parseLabResultsData_singlePatient(\
                    modelListFromTable(labResultTable))
                tempColNames.extend(extractor.addLabFeatures_singlePatient(\
                    patientEpisodeByIndexTime, labsByBaseName, ["Bar"], \
                    preTimeDelta, postTimeDelta))

                # Lab Result (Baz)
                labResultTable = extractor.queryLabResults(["Baz"], [patientId])
                labsByBaseName = extractor.parseLabResultsData_singlePatient(\
                    modelListFromTable(labResultTable))
                tempColNames.extend(extractor.addLabFeatures_singlePatient(\
                    patientEpisodeByIndexTime, labsByBaseName, ["Baz"], \
                    preTimeDelta, postTimeDelta))

                # Lab Result (Qux)
                labResultTable = extractor.queryLabResults(["Qux"], [patientId])
                labsByBaseName = extractor.parseLabResultsData_singlePatient(\
                    modelListFromTable(labResultTable))
                tempColNames.extend(extractor.addLabFeatures_singlePatient(\
                    patientEpisodeByIndexTime, labsByBaseName, ["Qux"], \
                    preTimeDelta, postTimeDelta))

                # Flowsheet (Perflow)
                # tempFile = StringIO()
                # labResultTable = extractor.queryFlowsheet(["Perflow"], [patientId], tempFile)
                # flowsheetByNameByPatientId = extractor.parseFlowsheetFile(\
                #     StringIO(tempFile.getvalue()))
                # tempColNames.extend(extractor.addFlowsheetFeatures_singlePatient(\
                #     patientEpisodeByIndexTime, flowsheetByNameByPatientId[patientId], \
                #     ["Perflow"], preTimeDelta, postTimeDelta, tempColNames))

                if colNames is None:
                    # First row, print header row
                    colNames = tempColNames
                    formatter.formatTuple(colNames)

                # Print out patient (episode) data (one row per episode)
                formatter.formatResultDicts(patientEpisodeByIndexTime.values(), colNames)

            if lastPatientId is None or lastPatientId != patientId:
                # Prepare to aggregate patient episode record per patient
                patientEpisodeByIndexTime = dict()

            patientEpisodeByIndexTime[patientEpisode["order_time"]] = patientEpisode
            lastPatientId = patientId
            outFile.flush()

        # Last Iteration
        patientId = lastPatientId
        # Clinical Item (PerfItem300)
        eventTimes = extractor.parseClinicalItemData_singlePatient(\
            modelListFromTable(extractor.queryClinicalItemsByName(\
                ("PerfItem300",), [patientId])))
        tempColNames.extend(\
            extractor.addClinicalItemFeatures_singlePatient(\
            eventTimes, patientEpisodeByIndexTime, "PerfItem300", \
            daysBins=[]))

        # Clinical Item (PerfItem400)
        eventTimes = extractor.parseClinicalItemData_singlePatient(\
            modelListFromTable(extractor.queryClinicalItemsByName(\
                ("PerfItem400",), [patientId])))
        tempColNames.extend(\
            extractor.addClinicalItemFeatures_singlePatient(\
            eventTimes, patientEpisodeByIndexTime, "PerfItem300", \
            daysBins=[]))

        # Clinical Item (PerfItem500)
        eventTimes = extractor.parseClinicalItemData_singlePatient(\
            modelListFromTable(extractor.queryClinicalItemsByName(\
                ("PerfItem500",), [patientId])))
        tempColNames.extend(\
            extractor.addClinicalItemFeatures_singlePatient(\
            eventTimes, patientEpisodeByIndexTime, "PerfItem300", \
            daysBins=[]))

        # Lab Result (Foo)
        labResultTable = extractor.queryLabResults(["Foo"], [patientId])
        labsByBaseName = extractor.parseLabResultsData_singlePatient(\
            modelListFromTable(labResultTable))
        tempColNames.extend(extractor.addLabFeatures_singlePatient(\
            patientEpisodeByIndexTime, labsByBaseName, ["Foo"], \
            preTimeDelta, postTimeDelta))

        # Lab Result (Bar)
        labResultTable = extractor.queryLabResults(["Bar"], [patientId])
        labsByBaseName = extractor.parseLabResultsData_singlePatient(\
            modelListFromTable(labResultTable))
        tempColNames.extend(extractor.addLabFeatures_singlePatient(\
            patientEpisodeByIndexTime, labsByBaseName, ["Bar"], \
            preTimeDelta, postTimeDelta))

        # Lab Result (Baz)
        labResultTable = extractor.queryLabResults(["Baz"], [patientId])
        labsByBaseName = extractor.parseLabResultsData_singlePatient(\
            modelListFromTable(labResultTable))
        tempColNames.extend(extractor.addLabFeatures_singlePatient(\
            patientEpisodeByIndexTime, labsByBaseName, ["Baz"], \
            preTimeDelta, postTimeDelta))

        # Lab Result (Qux)
        labResultTable = extractor.queryLabResults(["Qux"], [patientId])
        labsByBaseName = extractor.parseLabResultsData_singlePatient(\
            modelListFromTable(labResultTable))
        tempColNames.extend(extractor.addLabFeatures_singlePatient(\
            patientEpisodeByIndexTime, labsByBaseName, ["Qux"], \
            preTimeDelta, postTimeDelta))

        formatter.formatResultDicts(patientEpisodeByIndexTime.values(), colNames)

        # Close file.
        outFile.close()

        # Stop timer.
        extractorStop = time.time()

        # Compare results.
        factoryTime = factoryStop - factoryStart
        extractorTime = extractorStop - extractorStart
        self.assertTrue(extractorTime > factoryTime)

        # Clean up feature matrix files.
        try:
            os.remove("extractor.feature_matrix.tab.gz")
        except OSError:
            pass
        try:
            os.remove(factory.getMatrixFileName())
        except OSError:
            pass

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
