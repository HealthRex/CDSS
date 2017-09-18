#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.common.Const import NULL_STRING;
from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.dataconversion.DataExtractor import *;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestDataExtractor(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

        #self.purgeTestRecords();
        log.info("Populate the database with test data")

        # add main patient table
        columnDataString = "patient_id\tindex_time"
        dataTextStr = \
"""-123\t10/6/2113 00:00
-456\t7/5/2113 06:00
-789\t4/7/2113 12:00
-999\t1/6/2009 18:00
"""

        # For lab, flowsheet, or IV fluid testing
        """
        -123\t4/6/2009 12:00
        -456\t5/6/2009 12:00
        -789\t6/6/2009 12:00
        -999\t7/6/2009 12:00
        """

        # for clinical item testing
        """-123\t10/6/2113 10:50
        -456\t11/5/2113 10:20
        -789\t12/7/2113 11:20
        -999\t7/6/2009 11:00
        """

        # for time cycle testing
        """-123\t10/6/2113 00:00
        -456\t7/5/2113 06:00
        -789\t4/7/2113 12:00
        -999\t1/6/2009 18:00
        """

        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.execute("drop table if exists %s " % "main_patient_table");
        DBUtil.execute("create table %s %s" % ("main_patient_table", columnString));
        DBUtil.insertFile( StringIO(dataTextStr), "main_patient_table", delim="\t", columnNames=columns);


        columnDataString = "clinical_item_category_id\tsource_table\tdescription"
        dataTextStr = \
        """-100\tTestTable\tTestCategory
        """
        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "clinical_item_category", delim="\t", columnNames=columns);

        columnDataString = "clinical_item_id\tname\tdescription\tclinical_item_category_id"
        dataTextStr = \
"""-100\tTestItem100\tTest Item 100\t-100
-200\tTestItem200\tTest Item 200\t-100
"""
        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "clinical_item", delim="\t", columnNames=columns);

        columnDataString = "patient_item_id\tpatient_id\tclinical_item_id\titem_date"
        dataTextStr = \
"""-1000\t-123\t-100\t10/6/2113 10:20
-2000\t-123\t-200\t10/6/2113 11:20
-2500\t-123\t-100\t10/7/2113 11:20
-3000\t-456\t-100\t11/6/2113 10:20
-6000\t-789\t-200\t12/6/2113 11:20
"""
        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "patient_item", delim="\t", dateColFormats={"item_date": None}, columnNames=columns );

        columnDataString = "order_proc_id\tpat_id\torder_time\tproc_code"
        dataTextStr = \
"""-100\t-123\t4/6/2009 6:00\tTNI
-200\t-123\t4/6/2009 16:00\tTNI
-300\t-123\t4/6/2009 15:00\tLABMETB
-400\t-456\t4/25/2009 6:00\tLABMETB
-500\t-456\t4/6/2009 16:00\tTNI
-600\t-456\t5/6/2009 15:00\tLABMETB
-700\t-789\t4/25/2009 6:00\tLABMETB
-750\t-789\t4/26/2009 6:00\tLABMETB
-800\t-789\t4/6/2009 16:00\tLABMETB
-900\t-789\t5/6/2009 15:00\tLABMETB
"""
        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_proc", delim="\t", dateColFormats={"item_date": None}, columnNames=columns );

        columnDataString = "order_proc_id\tline\tresult_time\tbase_name\tord_num_value\tresult_flag\tresult_in_range_yn"
        dataTextStr = \
"""-100\t1\t4/6/2009 6:36\tTNI\t0.2\tHigh Panic\tN
-200\t1\t4/6/2009 16:34\tTNI\t0\tNone\tY
-300\t2\t4/6/2009 15:12\tCR\t2.1\tHigh\tN
-400\t1\t4/25/2009 6:36\tNA\t145\tNone\tY
-600\t2\t5/6/2009 15:12\tCR\t0.5\tNone\tY
-700\t2\t4/25/2009 12:00\tCR\t0.3\tNone\tY
-500\t1\t4/6/2009 16:34\tTNI\t9999999\tNone\tNone
-750\t2\t4/26/2009 6:00\tCR\t0.7\tNone\tY
-800\t1\t4/6/2009 16:34\tNA\t123\tLow\tN
-800\t2\t4/6/2009 12:00\tCR\t1.0\tNone\tNone
-900\t1\t5/6/2009 15:12\tNA\t151\tHigh\tN
"""

        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_results", delim="\t", dateColFormats={"result_time": None}, columnNames=columns );

        columnDataString = "pat_anon_id\tflo_meas_id\tflowsheet_name\tflowsheet_value\tshifted_record_dt_tm"
        dataTextStr = \
"""-123\t-1\tFiO2\t0.2\t4/6/2009 6:36
-123\t-1\tFiO2\t0\t4/6/2009 16:34
-123\t-2\tGlasgow Coma Scale Score\t2.1\t4/6/2009 15:12
-456\t-3\tBP_High_Systolic\t145\t4/25/2009 6:36
-456\t-1\tFiO2\tNone\t4/6/2009 16:34
-456\t-2\tGlasgow Coma Scale Score\t0.5\t5/6/2009 15:12
-789\t-2\tGlasgow Coma Scale Score\t0.3\t4/25/2009 12:00
-789\t-2\tGlasgow Coma Scale Score\t0.7\t4/26/2009 6:00
-789\t-3\tBP_High_Systolic\t123\t4/6/2009 16:34
-789\t-2\tGlasgow Coma Scale Score\t1\t4/6/2009 12:00
-789\t-3\tBP_High_Systolic\t151\t5/6/2009 15:12
"""
        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "stride_flowsheet", delim="\t", dateColFormats={"shifted_record_dt_tm": None}, columnNames=columns );

        columnDataString = "order_med_id\tpat_id\tmedication_id\tdescription\tstart_taking_time\tend_taking_time\tfreq_name\tmin_discrete_dose\tmin_rate"
        dataTextStr = \
"""-123000\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP\t4/6/2009 12:30\t4/6/2009 15:00\tCONTINUOUS\t\t500
-123010\t-123\t540102\tNS IV BOLUS\t4/6/2009 12:30\t4/6/2009 12:30\tONCE\t250\t
-123020\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP (missing end date, means cancelled. Ignore)\t4/6/2009 13:00\t\tCONTINUOUS\t\t50
-123030\t-123\t27838\tSODIUM CHLORIDE 0.9 % 0.9 % IV SOLP (ignore PACU)\t4/6/2009 10:00\t4/7/2009 10:00\tPACU ONLY\t\t125
-123040\t-123\t4318\tLACTATED RINGERS IV SOLP (ignore PRN)\t4/6/2009 10:00\t4/7/2009 10:00\tPRN\t\t250
-123050\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP (ignore endoscopy PRN)\t4/6/2009 13:00\t4/7/2009 10:00\tENDOSCOPY PRN\t\t75
-123060\t-123\t540115\tLACTATED RINGERS IV BOLUS\t4/6/2009 14:00\t4/6/2009 14:00\tONCE\t500\t
-123070\t-123\t540102\tNS IV BOLUS (register first daily admin, though may expand to capture multiple)\t4/6/2009 16:00\t4/10/2009 16:00\tDAILY\t250\t
-123080\t-123\t14863\tD5-1/2 NS & POTASSIUM CHLORIDE 20 MEQ/L IV SOLP (should ignore hypotonic IVF for now)\t4/6/2009 14:00\t4/7/2009 14:00\tCONTINUOUS\t\t75
-123090\t-123\t8982\tALBUMIN, HUMAN 5 % 5 % IV SOLP (should ignore albumin for now)\t4/6/2009 14:00\t4/7/2009 14:00\tONCE\t500\t
-123100\t-123\t27838\tSODIUM CHLORIDE 0.9 % 0.9 % IV SOLP\t4/6/2009 16:30\t4/6/2009 18:00\tCONTINUOUS\t\t500
-123110\t-123\t4318\tLACTATED RINGERS IV SOLP\t4/6/2009 17:00\t4/6/2009 18:00\tCONTINUOUS\t\t1000
"""
        columns = [col for col in columnDataString.split('\t')]
        columnString = "(%s varchar)" % str.join(" varchar, ", columns)
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_med", delim="\t", dateColFormats={"start_taking_time":None, "end_taking_time":None}, columnNames=columns );

        self.outputFileName = "medinfo/dataconversion/test/dataExtraction_test.out"
        self.extractor = DataExtractor(self.outputFileName);  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.purgeTestRecords();
        DBTestCase.tearDown(self);

    def purgeTestRecords(self):
        log.info("Purge test records from the database")
        DBUtil.execute("""delete from stride_order_med where order_med_id < 0""");
        DBUtil.execute("""delete from stride_flowsheet where flo_meas_id < 0""");
        DBUtil.execute("""delete from stride_order_results where order_proc_id < 0""");
        DBUtil.execute("""delete from stride_order_proc where order_proc_id < 0""");
        DBUtil.execute("""delete from patient_item where clinical_item_id < 0""");
        DBUtil.execute("""delete from clinical_item where clinical_item_id < 0""");
        DBUtil.execute("""delete from clinical_item_category where clinical_item_category_id < 0""");

    def test_addInitPatientData(self):
        targetTable = "patient_item"
        patientList = [-123, -456, -789, -999]
        expectedOutput = \
        """
        patient_id\t-123\t-456\t-789\t-999
        index_time\t10/6/2113 10:50\t11/5/2113 10:20\t12/7/2113 11:20\t7/6/2009 11:00
        """

        self.extractor.addInitPatientData(patientList)

        f = open(self.outputFileName, 'rb')
        data = f.read(os.path.getsize(self.outputFileName))
        self.assertEqualFile(StringIO(expectedOutput), StringIO(data), whitespace=False)

    def test_addClinicalItemFeatures(self):
        clinicalItemNames = ["TestItem100","TestItem200"]
        patientList = [-123, -456, -789, -999]
        prefix = "TestItem"
        expectedOutput = \
        """
patient_id\tindex_time\tdays_until_end\tTestItem.preTimeDays\tTestItem.postTimeDays\tTestItem.pre\tTestItem.pre.1d\tTestItem.pre.2d\tTestItem.pre.4d\tTestItem.pre.7d\tTestItem.pre.14d\tTestItem.pre.30d\tTestItem.pre.90d\tTestItem.pre.180d\tTestItem.pre.365d\tTestItem.pre.730d\tTestItem.pre.1460d\tTestItem.post\tTestItem.post.1d\tTestItem.post.2d\tTestItem.post.4d\tTestItem.post.7d\tTestItem.post.14d\tTestItem.post.30d\tTestItem.post.90d\tTestItem.post.180d\tTestItem.post.365d\tTestItem.post.730d\tTestItem.post.1460d
-123\t10/6/2113 10:50\t0\t-0.0208333333333\t0.0208333333333\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t2\t1\t2\t2\t2\t2\t2\t2\t2\t2\t2\t2
-456\t11/5/2113 10:20\t0\tNone\t1.0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1
-789\t12/7/2113 11:20\t0\t-1.0\tNone\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t1\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
-999\t7/6/2009 11:00\t0\tNone\tNone\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0
        """

        self.extractor.addClinicalItemFeaturesByName(patientList, clinicalItemNames, prefix)

        f = open(self.outputFileName, 'rb')
        data = f.read(os.path.getsize(self.outputFileName))
        self.assertEqualFile(StringIO(expectedOutput), StringIO(data), whitespace=False)

    def test_addLabFeatures(self):
        baseNames = ['TNI', 'LAC', 'CR']
        patientList = [-123, -456, -789, -999]
        lookbackTime = timedelta(-90)
        patIdCol = "pat_id"
        timeCol = "result_time"
        valCol = "ord_num_value"
        expectedOutput = """\
patient_id\tindex_time\tTNI.-90_0.count\tTNI.-90_0.countInRange\tTNI.-90_0.min\tTNI.-90_0.max\tTNI.-90_0.median\tTNI.-90_0.mean\tTNI.-90_0.std\tTNI.-90_0.first\tTNI.-90_0.last\tTNI.-90_0.diff\tTNI.-90_0.slope\tTNI.-90_0.proximate\tTNI.-90_0.firstTimeDays\tTNI.-90_0.lastTimeDays\tTNI.-90_0.proximateTimeDays\tLAC.-90_0.count\tLAC.-90_0.countInRange\tLAC.-90_0.min\tLAC.-90_0.max\tLAC.-90_0.median\tLAC.-90_0.mean\tLAC.-90_0.std\tLAC.-90_0.first\tLAC.-90_0.last\tLAC.-90_0.diff\tLAC.-90_0.slope\tLAC.-90_0.proximate\tLAC.-90_0.firstTimeDays\tLAC.-90_0.lastTimeDays\tLAC.-90_0.proximateTimeDays\tCR.-90_0.count\tCR.-90_0.countInRange\tCR.-90_0.min\tCR.-90_0.max\tCR.-90_0.median\tCR.-90_0.mean\tCR.-90_0.std\tCR.-90_0.first\tCR.-90_0.last\tCR.-90_0.diff\tCR.-90_0.slope\tCR.-90_0.proximate\tCR.-90_0.firstTimeDays\tCR.-90_0.lastTimeDays\tCR.-90_0.proximateTimeDays
-123\t4/6/2009 12:00\t1\t0\t0.2\t0.2\t0.2\t0.2\t0.0\t0.2\t0.2\t0.0\t0.0\t0.2\t-0.225\t-0.225\t-0.225\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone
-456\t5/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone
-789\t6/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t3\t2\t0.3\t1.0\t0.7\t0.666666666667\t0.286744175568\t1.0\t0.7\t-0.3\t-0.0151898734177\t0.7\t-61.0\t-41.25\t-41.25
-999\t7/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone
        """
        self.extractor.addLabFeatures(patientList, baseNames, patIdCol, timeCol, valCol, lookbackTime=lookbackTime, lookaheadTime=timedelta(0))
        #self.extractor.transposeMatrixFile()

        f = open(self.outputFileName, 'rb')
        data = f.read(os.path.getsize(self.outputFileName))
        self.assertEqualFile(StringIO(expectedOutput), StringIO(data), whitespace=False)

    def test_addFlowsheetFeatures(self):
        flowsheetNames = ["Resp", "FiO2", "Glasgow Coma Scale Score"]
        patientList = [-123, -456, -789, -999]
        #lookbackTime = timedelta(-90)
        patIdCol = "pat_anon_id"
        timeCol = "shifted_record_dt_tm"
        valCol = "flowsheet_value"
        expectedOutput = """\
patient_id\tindex_time\tResp.None_0.count\tResp.None_0.countInRange\tResp.None_0.min\tResp.None_0.max\tResp.None_0.median\tResp.None_0.mean\tResp.None_0.std\tResp.None_0.first\tResp.None_0.last\tResp.None_0.diff\tResp.None_0.slope\tResp.None_0.proximate\tResp.None_0.firstTimeDays\tResp.None_0.lastTimeDays\tResp.None_0.proximateTimeDays\tFiO2.None_0.count\tFiO2.None_0.countInRange\tFiO2.None_0.min\tFiO2.None_0.max\tFiO2.None_0.median\tFiO2.None_0.mean\tFiO2.None_0.std\tFiO2.None_0.first\tFiO2.None_0.last\tFiO2.None_0.diff\tFiO2.None_0.slope\tFiO2.None_0.proximate\tFiO2.None_0.firstTimeDays\tFiO2.None_0.lastTimeDays\tFiO2.None_0.proximateTimeDays\tGlasgow Coma Scale Score.None_0.count\tGlasgow Coma Scale Score.None_0.countInRange\tGlasgow Coma Scale Score.None_0.min\tGlasgow Coma Scale Score.None_0.max\tGlasgow Coma Scale Score.None_0.median\tGlasgow Coma Scale Score.None_0.mean\tGlasgow Coma Scale Score.None_0.std\tGlasgow Coma Scale Score.None_0.first\tGlasgow Coma Scale Score.None_0.last\tGlasgow Coma Scale Score.None_0.diff\tGlasgow Coma Scale Score.None_0.slope\tGlasgow Coma Scale Score.None_0.proximate\tGlasgow Coma Scale Score.None_0.firstTimeDays\tGlasgow Coma Scale Score.None_0.lastTimeDays\tGlasgow Coma Scale Score.None_0.proximateTimeDays
-123\t4/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t1\t0\t0.2\t0.2\t0.2\t0.2\t0.0\t0.2\t0.2\t0.0\t0.0\t0.2\t-0.225\t-0.225\t-0.225\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone
-456\t5/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone
-789\t6/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t3\t0\t0.3\t1.0\t0.7\t0.666666666667\t0.286744175568\t1.0\t0.7\t-0.3\t-0.0151898734177\t0.7\t-61.0\t-41.25\t-41.25
-999\t7/6/2009 12:00\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\t0\t0\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone\tNone
        """
        self.extractor.addFlowsheetFeatures(patientList, flowsheetNames,patIdCol, timeCol, valCol,lookaheadTime=timedelta(0))
        #self.extractor.transposeMatrixFile()

        f = open(self.outputFileName, 'rb')
        data = f.read(os.path.getsize(self.outputFileName))
        self.assertEqualFile(StringIO(expectedOutput), StringIO(data), whitespace=False)

    def test_addIVFluidFeatures(self):
        medicationGroups = ["isotonic"]
        patientList = [-123]
        thresholdVolumes = [500,1000,2000,3000,4000,5000];  # Volumes (mL) of fluid interested in time until encountering
        checkpointTimes = [0, 1800, 1*60*60, 2*60*60, 3*60*60, 4*60*60, 4.5*60*60, 5*60*60, 6*60*60, 7*60*60];  # Time checkpoints (seconds) interested in accumulated fluid volume by that time

        expectedOutput = """
patient_id\tindex_time\tivf.secondsUntilCC.500\tivf.secondsUntilCC.1000\tivf.secondsUntilCC.2000\tivf.secondsUntilCC.3000\tivf.secondsUntilCC.4000\tivf.secondsUntilCC.5000\tivf.CCupToSec.0\tivf.CCupToSec.1800\tivf.CCupToSec.3600\tivf.CCupToSec.7200\tivf.CCupToSec.10800\tivf.CCupToSec.14400\tivf.CCupToSec.16200\tivf.CCupToSec.18000\tivf.CCupToSec.21600\tivf.CCupToSec.25200
-123\t4/6/2009 12:00\t3600.0\t7200.0\t10800.0\t19200.0\t21600.0\tNone\t0.0\t250.0\t500.0\t1500.0\t2000.0\t2250.0\t2250.0\t2500.0\t4000.0\t4000.0
        """
        self.extractor.addIVFluidFeatures(patientList, medicationGroups, thresholdVolumes, checkpointTimes)

        f = open(self.outputFileName, 'rb')
        data = f.read(os.path.getsize(self.outputFileName))
        self.assertEqualFile(StringIO(expectedOutput), StringIO(data), whitespace=False)

    def test_addTimeCycleFeatures(self):
        timeAttributes = ["month","hour"]
        patientList = [-123, -456, -789, -999]

        expectedOutput = """
patient_id\tindex_time\tindex_time.month\tindex_time.month.sin\tindex_time.month.cos\tindex_time.hour\tindex_time.hour.sin\tindex_time.hour.cos
-123\t10/6/2113 00:00\t10\t-1.0\t-1.83697019872e-16\t0\t0.0\t1.0
-456\t7/5/2113 06:00\t7\t1.22464679915e-16\t-1.0\t6\t1.0\t6.12323399574e-17
-789\t4/7/2113 12:00\t4\t1.0\t6.12323399574e-17\t12\t1.22464679915e-16\t-1.0
-999\t1/6/2009 18:00\t1\t0.0\t1.0\t18\t-1.0\t-1.83697019872e-16
"""
        self.extractor.addTimeCycleFeatures(patientList,timeAttributes)

        f = open(self.outputFileName, 'rb')
        data = f.read(os.path.getsize(self.outputFileName))
        self.assertEqualFile(StringIO(expectedOutput), StringIO(data), whitespace=False)

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestDataExtractor("test_addInitPatientData"))
    #suite.addTest(TestDataExtractor("test_addClinicalItemFeatures"));
    #suite.addTest(TestDataExtractor("test_addLabFeatures"));
    #suite.addTest(TestDataExtractor('test_addFlowsheetFeatures'));
    #suite.addTest(TestDataExtractor('test_addIVFluidFeatures'));
    #suite.addTest(TestDataExtractor('test_addTimeCycleFeatures'));
    suite.addTest(unittest.makeSuite(TestDataExtractor));

    return suite;

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
