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

from medinfo.dataconversion.DataExtractor import DataExtractor;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestDataExtractor(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        self.purgeTestRecords();
        log.info("Populate the database with test data")

        dataTextStr = \
"""clinical_item_category_id\tsource_table\tdescription
-100\tTestTable\tTestCategory
"""
        DBUtil.insertFile( StringIO(dataTextStr), "clinical_item_category", delim="\t" );

        dataTextStr = \
"""clinical_item_id\tname\tdescription\tclinical_item_category_id
-100\tTestItem100\tTest Item 100\t-100
-200\tTestItem200\tTest Item 200\t-100
"""
        DBUtil.insertFile( StringIO(dataTextStr), "clinical_item", delim="\t" );

        dataTextStr = \
"""patient_item_id\tpatient_id\tclinical_item_id\titem_date
-1000\t-123\t-100\t10/6/2113 10:20
-2000\t-123\t-200\t10/6/2113 11:20
-2500\t-123\t-100\t10/7/2113 11:20
-3000\t-456\t-100\t11/6/2113 10:20
-6000\t-789\t-200\t12/6/2113 11:20
"""
        DBUtil.insertFile( StringIO(dataTextStr), "patient_item", delim="\t", dateColFormats={"item_date": None} );

        dataTextStr = \
"""order_proc_id\tpat_id\torder_time\tproc_code
-100\t-123\t4/6/2009 6:00\tTNI
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
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_proc", delim="\t", dateColFormats={"item_date": None} );

        dataTextStr = \
"""order_proc_id\tline\tresult_time\tbase_name\tord_num_value\tresult_flag\tresult_in_range_yn
-100\t1\t4/6/2009 6:36\tTNI\t0.2\tHigh Panic\tN
-200\t1\t4/6/2009 16:34\tTNI\t0\tNone\tY
-300\t2\t4/6/2009 15:12\tCR\t2.1\tHigh\tN
-400\t1\t4/25/2009 6:36\tNA\t145\tNone\tY
-500\t1\t4/6/2009 16:34\tTNI\t9999999\tNone\tNone
-600\t2\t5/6/2009 15:12\tCR\t0.5\tNone\tY
-700\t2\t4/25/2009 12:00\tCR\t0.3\tNone\tY
-750\t2\t4/26/2009 6:00\tCR\t0.7\tNone\tY
-800\t1\t4/6/2009 16:34\tNA\t123\tLow\tN
-800\t2\t4/6/2009 12:00\tCR\t1.0\tNone\tNone
-900\t1\t5/6/2009 15:12\tNA\t151\tHigh\tN
"""
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_results", delim="\t", dateColFormats={"result_time": None} );

        dataTextStr = \
"""pat_anon_id\tflo_meas_id\tflowsheet_name\tflowsheet_value\tshifted_record_dt_tm
-123\t-1\tFiO2\t0.2\t4/6/2009 6:36
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
        DBUtil.insertFile( StringIO(dataTextStr), "stride_flowsheet", delim="\t", dateColFormats={"shifted_record_dt_tm": None} );

        dataTextStr = \
"""order_med_id\tpat_id\tmedication_id\tdescription\tstart_taking_time\tend_taking_time\tfreq_name\tmin_discrete_dose\tmin_rate
-123000\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP\t4/6/2009 12:30\t4/6/2009 15:00\tCONTINUOUS\t\t500
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
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_med", delim="\t", dateColFormats={"start_taking_time":None, "end_taking_time":None} );

        self.extractor = DataExtractor();  # Instance to test on

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

    def test_queryClinicalItems(self):
        patientById = \
            {   -123: {"patient_id": -123},
                -456: {"patient_id": -456},
                -789: {"patient_id": -789},
                -999: {"patient_id": -999},
            }

        # Direct name lookup
        clinicalItemNames = ["TestItem100","TestItem200"];
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
                {"patient_id": -789, "item_date": DBUtil.parseDateValue("12/6/2113 11:20") },
                {"patient_id": -456, "item_date": DBUtil.parseDateValue("11/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 11:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/7/2113 11:20") },
            ];
        self.assertEqualList( expectedData, actualData );


        # Use like regular expression
        clinicalItemNames = ["TestItem%"];  
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
                {"patient_id": -789, "item_date": DBUtil.parseDateValue("12/6/2113 11:20") },
                {"patient_id": -456, "item_date": DBUtil.parseDateValue("11/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 11:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/7/2113 11:20") },
            ];
        self.assertEqualList( expectedData, actualData );


        # Use like regular expression for one item and a fake item
        clinicalItemNames = ["TestItem1%","FakeItemName"];  
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
                {"patient_id": -456, "item_date": DBUtil.parseDateValue("11/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/7/2113 11:20") },
            ];
        self.assertEqualList( expectedData, actualData );

        # Expect no results
        clinicalItemNames = ["FakeItemName"];  
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
            ];
        self.assertEqualList( expectedData, actualData );




        log.info("Do series over again, but use regular expressions and descriptions instead of LIKE");

        # Direct name lookup
        clinicalItemNames = ["Test Item 100","Test Item 200"];
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile, col="description", operator="~*");

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
                {"patient_id": -789, "item_date": DBUtil.parseDateValue("12/6/2113 11:20") },
                {"patient_id": -456, "item_date": DBUtil.parseDateValue("11/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 11:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/7/2113 11:20") },
            ];
        self.assertEqualList( expectedData, actualData );


        # Use like regular expression
        clinicalItemNames = ["^test item"];  # Prefix search, not-case sensitive
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile, col="description", operator="~*");

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
                {"patient_id": -789, "item_date": DBUtil.parseDateValue("12/6/2113 11:20") },
                {"patient_id": -456, "item_date": DBUtil.parseDateValue("11/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 11:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/7/2113 11:20") },
            ];
        self.assertEqualList( expectedData, actualData );


        # Use like regular expression for one item and a fake item
        clinicalItemNames = ["Test Item 1","Fake Item Name"];  # Substring
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile, col="description", operator="~*");

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
                {"patient_id": -456, "item_date": DBUtil.parseDateValue("11/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/6/2113 10:20") },
                {"patient_id": -123, "item_date": DBUtil.parseDateValue("10/7/2113 11:20") },
            ];
        self.assertEqualList( expectedData, actualData );

        # Expect no results
        clinicalItemNames = ["FakeItemName"];  
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile, col="description", operator="~*");

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["patient_id"] = int(row["patient_id"]);
            row["item_date"] = DBUtil.parseDateValue(row["item_date"]);
        expectedData = \
            [   
            ];
        self.assertEqualList( expectedData, actualData );

    def test_generateDateRangeIndexTimes(self):
        log.debug("Setup clinical item feature data file first...");
        patientById = \
            {   -123: {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00")},
                -456: {"patient_id": -456, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20")},
                -789: {"patient_id": -789, "start_time":DBUtil.parseDateValue("1/5/2113 10:20"), "end_time":DBUtil.parseDateValue("1/2/2113 10:20")},
            }
        patientList = patientById.values();
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("start_time","end_time", patientList, colNames);

        expectedData = \
            {   -123: { DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 2.965277777},
                        DBUtil.parseDateValue("10/7/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/7/2113 10:50"), "days_until_end": 1.965277777},
                        DBUtil.parseDateValue("10/8/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/8/2113 10:50"), "days_until_end": 0.965277777},
                      },
                -456: {DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -456, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20"), "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0}},
                -789: {},   # Can't find a valid index time if start date is after end date
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
            self.assertEqual( len(expectedData[patientId]), len(patientEpisodeByIndexTime) )
        self.assertEqual( len(expectedData), len(actualData) );


        # Do over with different delta increment sizes (besides default 1 day)
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("start_time","end_time", patientList, colNames, timeInterval=timedelta(2));

        expectedData = \
            {   -123: { DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 2.965277777},
                        DBUtil.parseDateValue("10/8/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/8/2113 10:50"), "days_until_end": 0.965277777},
                      },
                -456: {DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -456, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20"), "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0}},
                -789: {},   # Can't find a valid index time if start date is after end date
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, patientId, indexTime, patient;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
            self.assertEqual( len(expectedData[patientId]), len(patientEpisodeByIndexTime) )
        self.assertEqual( len(expectedData), len(actualData) );

        # Do over with no delta increment (means only want single index=start time for each patient)
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("start_time","end_time", patientList, colNames, timeInterval=None);

        expectedData = \
            {   -123: { DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 2.965277777}},
                -456: {DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -456, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20"), "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0}},
                -789: {},   # Can't find a valid index time if start date is after end date
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, patientId, indexTime, patient;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
            self.assertEqual( len(expectedData[patientId]), len(patientEpisodeByIndexTime) )
        self.assertEqual( len(expectedData), len(actualData) );

    def test_generateDateRangeIndexTimes_repeatPatient(self):
        log.debug("Setup clinical item feature data file first...");
        patientList = \
            [   {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00")},
                {"patient_id": -123, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20")},
                {"patient_id": -123, "start_time":DBUtil.parseDateValue("1/5/2113 10:20"), "end_time":DBUtil.parseDateValue("1/2/2113 10:20")},
            ];
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("start_time","end_time", patientList, colNames);

        expectedData = \
            {   -123: { DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 2.965277777},
                        DBUtil.parseDateValue("10/7/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/7/2113 10:50"), "days_until_end": 1.965277777},
                        DBUtil.parseDateValue("10/8/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/8/2113 10:50"), "days_until_end": 0.965277777},
                        # Separate set of dates
                        DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20"), "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0},
                        # Last set has no valid dates to include
                      },
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, patientId, indexTime, patient;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
            self.assertEqual( len(expectedData[patientId]), len(patientEpisodeByIndexTime) )
        self.assertEqual( len(expectedData), len(actualData) );

        # Do over with no delta increment (means only want single index=start time for each patient)
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("start_time","end_time", patientList, colNames, timeInterval=None);

        expectedData = \
            {   -123: { DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("10/6/2113 10:50"), "end_time":DBUtil.parseDateValue("10/9/2113 10:00"), "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 2.965277777},
                        # Separate set of dates
                        DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -123, "start_time":DBUtil.parseDateValue("11/5/2113 10:20"), "end_time":DBUtil.parseDateValue("11/5/2113 10:20"), "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0},
                        # Last set has no valid dates to include
                      },
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, patientId, indexTime, patient;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
            self.assertEqual( len(expectedData[patientId]), len(patientEpisodeByIndexTime) )
        self.assertEqual( len(expectedData), len(actualData) );

    def test_addTimeCycleFeatures(self):
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("10/6/2113 00:00")},
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("7/5/2113 06:00")},
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("4/7/2113 12:00")},
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("1/6/2009 18:00")},
            }

        expectedDataByPatientId = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("10/6/2113 00:00"), "index_time.month":10, "index_time.month.sin":-1.0, "index_time.month.cos":0.0, "index_time.hour":0, "index_time.hour.sin":0.0, "index_time.hour.cos":1.0, },
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("7/5/2113 06:00"), "index_time.month":7, "index_time.month.sin":0.0, "index_time.month.cos":-1.0, "index_time.hour":6, "index_time.hour.sin":1.0, "index_time.hour.cos":0.0, },
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("4/7/2113 12:00"), "index_time.month":4, "index_time.month.sin":1.0, "index_time.month.cos":0.0, "index_time.hour":12, "index_time.hour.sin":0.0, "index_time.hour.cos":-1.0, },
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("1/6/2009 18:00"), "index_time.month":1, "index_time.month.sin":0.0, "index_time.month.cos":1.0, "index_time.hour":18, "index_time.hour.sin":-1.0, "index_time.hour.cos":0.0, },
            };
        expectedColNames = ["index_time.month","index_time.month.sin","index_time.month.cos", "index_time.hour","index_time.hour.sin","index_time.hour.cos"];

        colNames = None;
        for patientId, patientEpisode in patientById.iteritems():
            colNames = list();
            # Generate index time points copies for the patient
            colNames.extend(self.extractor.addTimeCycleFeatures_singleEpisode(patientEpisode, "index_time", "month"));
            colNames.extend(self.extractor.addTimeCycleFeatures_singleEpisode(patientEpisode, "index_time", "hour"));

            #print >> sys.stderr, patientEpisode;
            self.assertAlmostEqualsDict( expectedDataByPatientId[patientId], patientEpisode );
            self.assertEquals(expectedColNames, colNames);

    def test_addClinicalItemFeatures(self):
        log.debug("Setup clinical item feature data file first...");
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("10/6/2113 10:50")},
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("11/5/2113 10:20")},
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("12/7/2113 11:20")},
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 11:00")},
            }
        clinicalItemNames = ["TestItem100","TestItem200"];
        outFile = StringIO();
        self.extractor.queryClinicalItemsByName(clinicalItemNames, patientById, outFile);

        # Extract out item contents and link to patient data
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("index_time","index_time", patientById.values(), colNames);
        itemTimesByPatientId = self.extractor.parseClinicalItemFile(StringIO(outFile.getvalue()));
        self.extractor.addClinicalItemFeatures(itemTimesByPatientId, patientEpisodeByIndexTimeById, colNames, "TestItem");

        expectedData = \
            {   -123: {DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 0.0, "TestItem.preTimeDays":-0.0208333333, "TestItem.postTimeDays":0.0208333333, "TestItem.pre":1, "TestItem.pre.1d":1, "TestItem.pre.2d":1, "TestItem.pre.4d":1, "TestItem.pre.7d":1, "TestItem.pre.14d":1, "TestItem.pre.30d":1, "TestItem.pre.90d":1, "TestItem.pre.180d":1, "TestItem.pre.365d":1, "TestItem.pre.730d":1, "TestItem.pre.1460d":1, "TestItem.post":2, "TestItem.post.1d":1, "TestItem.post.2d":2, "TestItem.post.4d":2, "TestItem.post.7d":2, "TestItem.post.14d":2, "TestItem.post.30d":2, "TestItem.post.90d":2, "TestItem.post.180d":2, "TestItem.post.365d":2, "TestItem.post.730d":2, "TestItem.post.1460d":2, }},
                -456: {DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -456, "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0, "TestItem.preTimeDays":None, "TestItem.postTimeDays":1, "TestItem.pre":0, "TestItem.pre.1d":0, "TestItem.pre.2d":0, "TestItem.pre.4d":0, "TestItem.pre.7d":0, "TestItem.pre.14d":0, "TestItem.pre.30d":0, "TestItem.pre.90d":0, "TestItem.pre.180d":0, "TestItem.pre.365d":0, "TestItem.pre.730d":0, "TestItem.pre.1460d":0, "TestItem.post":1, "TestItem.post.1d":1, "TestItem.post.2d":1, "TestItem.post.4d":1, "TestItem.post.7d":1, "TestItem.post.14d":1, "TestItem.post.30d":1, "TestItem.post.90d":1, "TestItem.post.180d":1, "TestItem.post.365d":1, "TestItem.post.730d":1, "TestItem.post.1460d":1, }},
                -789: {DBUtil.parseDateValue("12/7/2113 11:20"): {"patient_id": -789, "index_time":DBUtil.parseDateValue("12/7/2113 11:20"), "days_until_end": 0.0, "TestItem.preTimeDays":-1, "TestItem.postTimeDays":None, "TestItem.pre":1, "TestItem.pre.1d":1, "TestItem.pre.2d":1, "TestItem.pre.4d":1, "TestItem.pre.7d":1, "TestItem.pre.14d":1, "TestItem.pre.30d":1, "TestItem.pre.90d":1, "TestItem.pre.180d":1, "TestItem.pre.365d":1, "TestItem.pre.730d":1, "TestItem.pre.1460d":1, "TestItem.post":0, "TestItem.post.1d":0, "TestItem.post.2d":0, "TestItem.post.4d":0, "TestItem.post.7d":0, "TestItem.post.14d":0, "TestItem.post.30d":0, "TestItem.post.90d":0, "TestItem.post.180d":0, "TestItem.post.365d":0, "TestItem.post.730d":0, "TestItem.post.1460d":0, }},
                -999: {DBUtil.parseDateValue("7/6/2009 11:00"):  {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 11:00"), "days_until_end": 0.0, "TestItem.preTimeDays":None, "TestItem.postTimeDays":None, "TestItem.pre":0, "TestItem.pre.1d":0, "TestItem.pre.2d":0, "TestItem.pre.4d":0, "TestItem.pre.7d":0, "TestItem.pre.14d":0, "TestItem.pre.30d":0, "TestItem.pre.90d":0, "TestItem.pre.180d":0, "TestItem.pre.365d":0, "TestItem.pre.730d":0, "TestItem.pre.1460d":0, "TestItem.post":0, "TestItem.post.1d":0, "TestItem.post.2d":0, "TestItem.post.4d":0, "TestItem.post.7d":0, "TestItem.post.14d":0, "TestItem.post.30d":0, "TestItem.post.90d":0, "TestItem.post.180d":0, "TestItem.post.365d":0, "TestItem.post.730d":0, "TestItem.post.1460d":0, }},
            };

        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, key, value;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
        self.assertEqual( len(expectedData), len(actualData) );

    def test_addClinicalItemFeatures_perPatient(self):
        log.debug("Setup clinical item feature data file first...");
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("10/6/2113 10:50")},
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("11/5/2113 10:20")},
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("12/7/2113 11:20")},
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 11:00")},
            }

        expectedDataByPatientId = \
            {   -123: {DBUtil.parseDateValue("10/6/2113 10:50"): {"patient_id": -123, "index_time":DBUtil.parseDateValue("10/6/2113 10:50"), "days_until_end": 0.0, "TestItem.preTimeDays":-0.0208333333, "TestItem.postTimeDays":0.0208333333, "TestItem.pre":1, "TestItem.pre.1d":1, "TestItem.pre.2d":1, "TestItem.pre.4d":1, "TestItem.pre.7d":1, "TestItem.pre.14d":1, "TestItem.pre.30d":1, "TestItem.pre.90d":1, "TestItem.pre.180d":1, "TestItem.pre.365d":1, "TestItem.pre.730d":1, "TestItem.pre.1460d":1, "TestItem.post":2, "TestItem.post.1d":1, "TestItem.post.2d":2, "TestItem.post.4d":2, "TestItem.post.7d":2, "TestItem.post.14d":2, "TestItem.post.30d":2, "TestItem.post.90d":2, "TestItem.post.180d":2, "TestItem.post.365d":2, "TestItem.post.730d":2, "TestItem.post.1460d":2, }},
                -456: {DBUtil.parseDateValue("11/5/2113 10:20"): {"patient_id": -456, "index_time":DBUtil.parseDateValue("11/5/2113 10:20"), "days_until_end": 0.0, "TestItem.preTimeDays":None, "TestItem.postTimeDays":1, "TestItem.pre":0, "TestItem.pre.1d":0, "TestItem.pre.2d":0, "TestItem.pre.4d":0, "TestItem.pre.7d":0, "TestItem.pre.14d":0, "TestItem.pre.30d":0, "TestItem.pre.90d":0, "TestItem.pre.180d":0, "TestItem.pre.365d":0, "TestItem.pre.730d":0, "TestItem.pre.1460d":0, "TestItem.post":1, "TestItem.post.1d":1, "TestItem.post.2d":1, "TestItem.post.4d":1, "TestItem.post.7d":1, "TestItem.post.14d":1, "TestItem.post.30d":1, "TestItem.post.90d":1, "TestItem.post.180d":1, "TestItem.post.365d":1, "TestItem.post.730d":1, "TestItem.post.1460d":1, }},
                -789: {DBUtil.parseDateValue("12/7/2113 11:20"): {"patient_id": -789, "index_time":DBUtil.parseDateValue("12/7/2113 11:20"), "days_until_end": 0.0, "TestItem.preTimeDays":-1, "TestItem.postTimeDays":None, "TestItem.pre":1, "TestItem.pre.1d":1, "TestItem.pre.2d":1, "TestItem.pre.4d":1, "TestItem.pre.7d":1, "TestItem.pre.14d":1, "TestItem.pre.30d":1, "TestItem.pre.90d":1, "TestItem.pre.180d":1, "TestItem.pre.365d":1, "TestItem.pre.730d":1, "TestItem.pre.1460d":1, "TestItem.post":0, "TestItem.post.1d":0, "TestItem.post.2d":0, "TestItem.post.4d":0, "TestItem.post.7d":0, "TestItem.post.14d":0, "TestItem.post.30d":0, "TestItem.post.90d":0, "TestItem.post.180d":0, "TestItem.post.365d":0, "TestItem.post.730d":0, "TestItem.post.1460d":0, }},
                -999: {DBUtil.parseDateValue("7/6/2009 11:00"):  {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 11:00"), "days_until_end": 0.0, "TestItem.preTimeDays":None, "TestItem.postTimeDays":None, "TestItem.pre":0, "TestItem.pre.1d":0, "TestItem.pre.2d":0, "TestItem.pre.4d":0, "TestItem.pre.7d":0, "TestItem.pre.14d":0, "TestItem.pre.30d":0, "TestItem.pre.90d":0, "TestItem.pre.180d":0, "TestItem.pre.365d":0, "TestItem.pre.730d":0, "TestItem.pre.1460d":0, "TestItem.post":0, "TestItem.post.1d":0, "TestItem.post.2d":0, "TestItem.post.4d":0, "TestItem.post.7d":0, "TestItem.post.14d":0, "TestItem.post.30d":0, "TestItem.post.90d":0, "TestItem.post.180d":0, "TestItem.post.365d":0, "TestItem.post.730d":0, "TestItem.post.1460d":0, }},
            };

        colNames = None;
        for patientId, basePatient in patientById.iteritems():
            colNames = list();
            # Generate index time points copies for the patient
            (patientEpisodeByIndexTime, newColNames) = self.extractor.generateDateRangeIndexTimes_singlePatient("index_time","index_time", basePatient);
            colNames.extend(newColNames);

            # Extract out item contents and link to patient data
            clinicalItemNames = ["TestItem100","TestItem200"];
            clinicalItemDataTable = self.extractor.queryClinicalItemsByName(clinicalItemNames, patientId);
            itemTimes = self.extractor.parseClinicalItemData_singlePatient(modelListFromTable(clinicalItemDataTable), patientId);
            newColNames = self.extractor.addClinicalItemFeatures_singlePatient(itemTimes, patientEpisodeByIndexTime, "TestItem");
            colNames.extend(newColNames);

            actualData = patientEpisodeByIndexTime;
            for indexTime, patient in actualData.iteritems():
                #print >> sys.stderr, patient;
                self.assertAlmostEqualsDict( expectedDataByPatientId[patientId][indexTime], patient );
            self.assertEqual( len(expectedDataByPatientId[patientId]), len(actualData) );

    def test_labResults(self):
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00")},
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("5/6/2009 12:00")},
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("6/6/2009 12:00")},
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 12:00")},
            }

        labBaseNames = ["TNI","CR","LAC"];
        outFile = StringIO();
        self.extractor.queryLabResults(labBaseNames, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:
            row["pat_id"] = int(row["pat_id"]);
            row["ord_num_value"] = float(row["ord_num_value"]);
            row["result_time"] = DBUtil.parseDateValue(row["result_time"]);
            row["result_flag"] = DBUtil.parseValue(row["result_flag"],"result_flag");
            row["result_in_range_yn"] = DBUtil.parseValue(row["result_in_range_yn"],"result_in_range_yn");

        expectedData = \
            [   
                #{"pat_id": -789, "base_name":"NA", "ord_num_value":123, "result_flag":"Low", "result_in_range_yn":"N", "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                {"pat_id": -789, "base_name":"CR", "ord_num_value":1.0, "result_flag": None, "result_in_range_yn":None, "result_time": DBUtil.parseDateValue("4/6/2009 12:00") },
                {"pat_id": -789, "base_name":"CR", "ord_num_value":0.3, "result_flag": None, "result_in_range_yn":"Y", "result_time": DBUtil.parseDateValue("4/25/2009 12:00") },
                {"pat_id": -789, "base_name":"CR", "ord_num_value":0.7, "result_flag": None, "result_in_range_yn":"Y", "result_time": DBUtil.parseDateValue("4/26/2009 6:00") },
                #{"pat_id": -789, "base_name":"NA", "ord_num_value":151, "result_flag": None, "result_in_range_yn":"Y", "result_time": DBUtil.parseDateValue("5/6/2009 15:12") },

                {"pat_id": -456, "base_name":"TNI", "ord_num_value":9999999, "result_flag": None, "result_in_range_yn": None, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                #{"pat_id": -456, "base_name":"NA", "ord_num_value":145, "result_flag": None, "result_in_range_yn":"Y", "result_time": DBUtil.parseDateValue("4/25/2009 6:36") },
                {"pat_id": -456, "base_name":"CR", "ord_num_value":0.5, "result_flag": None, "result_in_range_yn":"Y", "result_time": DBUtil.parseDateValue("5/6/2009 15:12") },

                {"pat_id": -123, "base_name":"TNI", "ord_num_value":0.2, "result_flag": "High Panic", "result_in_range_yn":"N", "result_time": DBUtil.parseDateValue("4/6/2009 6:36") },
                {"pat_id": -123, "base_name":"CR", "ord_num_value":2.1, "result_flag": "High", "result_in_range_yn":"N", "result_time": DBUtil.parseDateValue("4/6/2009 15:12") },
                {"pat_id": -123, "base_name":"TNI", "ord_num_value":0, "result_flag": None, "result_in_range_yn":"Y", "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
            ];
        self.assertEqualDictList( expectedData, actualData, expectedData[0].keys() );

        # Parse back the results and load into patient data
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("index_time","index_time", patientById.values(), colNames);

        preTimeDelta = timedelta(-90); # Any time in the past 90
        postTimeDelta = timedelta(0);   # Only look for past items
        labsByBaseNameByPatientId = self.extractor.parseLabResultsFile(StringIO(outFile.getvalue()));
        self.extractor.addLabFeatures(patientEpisodeByIndexTimeById, labsByBaseNameByPatientId, labBaseNames, preTimeDelta, postTimeDelta, colNames);

        expectedData = \
            {   -123: {DBUtil.parseDateValue("4/6/2009 12:00"): {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00"),"days_until_end": 0.0,  "TNI.-90_0.count":1, "TNI.-90_0.countInRange":0, "TNI.-90_0.min":0.2, "TNI.-90_0.max":0.2, "TNI.-90_0.median":0.2, "TNI.-90_0.mean":0.2, "TNI.-90_0.std":0, "TNI.-90_0.first":0.2, "TNI.-90_0.last":0.2, "TNI.-90_0.diff":0.0, "TNI.-90_0.slope":0.0, "TNI.-90_0.proximate":0.2, "TNI.-90_0.firstTimeDays":-0.225, "TNI.-90_0.lastTimeDays":-0.225, "TNI.-90_0.proximateTimeDays":-0.225, "CR.-90_0.count":0, "CR.-90_0.countInRange":0, "CR.-90_0.min":None, "CR.-90_0.max":None, "CR.-90_0.median":None, "CR.-90_0.mean":None, "CR.-90_0.std":None, "CR.-90_0.first":None, "CR.-90_0.last":None, "CR.-90_0.diff":None, "CR.-90_0.slope":None, "CR.-90_0.proximate":None, "CR.-90_0.firstTimeDays":None, "CR.-90_0.lastTimeDays":None, "CR.-90_0.proximateTimeDays":None, "LAC.-90_0.count":0, "LAC.-90_0.countInRange":0, "LAC.-90_0.min":None, "LAC.-90_0.max":None, "LAC.-90_0.median":None, "LAC.-90_0.mean":None, "LAC.-90_0.std":None, "LAC.-90_0.first":None, "LAC.-90_0.last":None, "LAC.-90_0.diff":None, "LAC.-90_0.slope":None, "LAC.-90_0.proximate":None, "LAC.-90_0.firstTimeDays":None, "LAC.-90_0.lastTimeDays":None, "LAC.-90_0.proximateTimeDays":None, }},
                -456: {DBUtil.parseDateValue("5/6/2009 12:00"): {"patient_id": -456, "index_time":DBUtil.parseDateValue("5/6/2009 12:00"),"days_until_end": 0.0,  "TNI.-90_0.count":0, "TNI.-90_0.countInRange":0, "TNI.-90_0.min":None, "TNI.-90_0.max":None, "TNI.-90_0.median":None, "TNI.-90_0.mean":None, "TNI.-90_0.std":None, "TNI.-90_0.first":None, "TNI.-90_0.last":None, "TNI.-90_0.diff":None, "TNI.-90_0.slope":None, "TNI.-90_0.proximate":None, "TNI.-90_0.firstTimeDays":None, "TNI.-90_0.lastTimeDays":None, "TNI.-90_0.proximateTimeDays":None, "CR.-90_0.count":0, "CR.-90_0.countInRange":0, "CR.-90_0.min":None, "CR.-90_0.max":None, "CR.-90_0.median":None, "CR.-90_0.mean":None, "CR.-90_0.std":None, "CR.-90_0.first":None, "CR.-90_0.last":None, "CR.-90_0.diff":None, "CR.-90_0.slope":None, "CR.-90_0.proximate":None, "CR.-90_0.firstTimeDays":None, "CR.-90_0.lastTimeDays":None, "CR.-90_0.proximateTimeDays":None, "LAC.-90_0.count":0, "LAC.-90_0.countInRange":0, "LAC.-90_0.min":None, "LAC.-90_0.max":None, "LAC.-90_0.median":None, "LAC.-90_0.mean":None, "LAC.-90_0.std":None, "LAC.-90_0.first":None, "LAC.-90_0.last":None, "LAC.-90_0.diff":None, "LAC.-90_0.slope":None, "LAC.-90_0.proximate":None, "LAC.-90_0.firstTimeDays":None, "LAC.-90_0.lastTimeDays":None, "LAC.-90_0.proximateTimeDays":None, }},
                -789: {DBUtil.parseDateValue("6/6/2009 12:00"): {"patient_id": -789, "index_time":DBUtil.parseDateValue("6/6/2009 12:00"),"days_until_end": 0.0,  "TNI.-90_0.count":0, "TNI.-90_0.countInRange":0, "TNI.-90_0.min":None, "TNI.-90_0.max":None, "TNI.-90_0.median":None, "TNI.-90_0.mean":None, "TNI.-90_0.std":None, "TNI.-90_0.first":None, "TNI.-90_0.last":None, "TNI.-90_0.diff":None, "TNI.-90_0.slope":None, "TNI.-90_0.proximate":None, "TNI.-90_0.firstTimeDays":None, "TNI.-90_0.lastTimeDays":None, "TNI.-90_0.proximateTimeDays":None, "CR.-90_0.count":3, "CR.-90_0.countInRange":2, "CR.-90_0.min":0.3, "CR.-90_0.max":1.0, "CR.-90_0.median":0.7, "CR.-90_0.mean":0.6666667, "CR.-90_0.std":0.2867442, "CR.-90_0.first":1.0, "CR.-90_0.last":0.7, "CR.-90_0.diff":-0.3, "CR.-90_0.slope":-0.01518987, "CR.-90_0.proximate":0.7, "CR.-90_0.firstTimeDays":-61, "CR.-90_0.lastTimeDays":-41.25, "CR.-90_0.proximateTimeDays":-41.25, "LAC.-90_0.count":0, "LAC.-90_0.countInRange":0, "LAC.-90_0.min":None, "LAC.-90_0.max":None, "LAC.-90_0.median":None, "LAC.-90_0.mean":None, "LAC.-90_0.std":None, "LAC.-90_0.first":None, "LAC.-90_0.last":None, "LAC.-90_0.diff":None, "LAC.-90_0.slope":None, "LAC.-90_0.proximate":None, "LAC.-90_0.firstTimeDays":None, "LAC.-90_0.lastTimeDays":None, "LAC.-90_0.proximateTimeDays":None, }},
                -999: {DBUtil.parseDateValue("7/6/2009 12:00"): {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 12:00"),"days_until_end": 0.0,  "TNI.-90_0.count":0, "TNI.-90_0.countInRange":0, "TNI.-90_0.min":None, "TNI.-90_0.max":None, "TNI.-90_0.median":None, "TNI.-90_0.mean":None, "TNI.-90_0.std":None, "TNI.-90_0.first":None, "TNI.-90_0.last":None, "TNI.-90_0.diff":None, "TNI.-90_0.slope":None, "TNI.-90_0.proximate":None, "TNI.-90_0.firstTimeDays":None, "TNI.-90_0.lastTimeDays":None, "TNI.-90_0.proximateTimeDays":None, "CR.-90_0.count":0, "CR.-90_0.countInRange":0, "CR.-90_0.min":None, "CR.-90_0.max":None, "CR.-90_0.median":None, "CR.-90_0.mean":None, "CR.-90_0.std":None, "CR.-90_0.first":None, "CR.-90_0.last":None, "CR.-90_0.diff":None, "CR.-90_0.slope":None, "CR.-90_0.proximate":None, "CR.-90_0.firstTimeDays":None, "CR.-90_0.lastTimeDays":None, "CR.-90_0.proximateTimeDays":None, "LAC.-90_0.count":0, "LAC.-90_0.countInRange":0, "LAC.-90_0.min":None, "LAC.-90_0.max":None, "LAC.-90_0.median":None, "LAC.-90_0.mean":None, "LAC.-90_0.std":None, "LAC.-90_0.first":None, "LAC.-90_0.last":None, "LAC.-90_0.diff":None, "LAC.-90_0.slope":None, "LAC.-90_0.proximate":None, "LAC.-90_0.firstTimeDays":None, "LAC.-90_0.lastTimeDays":None, "LAC.-90_0.proximateTimeDays":None, }},
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, patientId, patient;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
        self.assertEqual( len(expectedData), len(actualData) );

    def test_labResults_perPatient(self):
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00")},
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("5/6/2009 12:00")},
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("6/6/2009 12:00")},
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 12:00")},
            }

        expectedDataByPatientId = \
            {   -123:   [   {"pat_id": -123, "base_name":"TNI", "ord_num_value":0.2, "result_time": DBUtil.parseDateValue("4/6/2009 6:36") },
                            {"pat_id": -123, "base_name":"CR", "ord_num_value":2.1, "result_time": DBUtil.parseDateValue("4/6/2009 15:12") },
                            {"pat_id": -123, "base_name":"TNI", "ord_num_value":0, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                        ],
                -456:   [   {"pat_id": -456, "base_name":"TNI", "ord_num_value":9999999, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                            #{"pat_id": -456, "base_name":"NA", "ord_num_value":145, "result_time": DBUtil.parseDateValue("4/25/2009 6:36") },
                            {"pat_id": -456, "base_name":"CR", "ord_num_value":0.5, "result_time": DBUtil.parseDateValue("5/6/2009 15:12") },
                        ],
                -789:   [   #{"pat_id": -789, "base_name":"NA", "ord_num_value":123, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                            {"pat_id": -789, "base_name":"CR", "ord_num_value":1.0, "result_time": DBUtil.parseDateValue("4/6/2009 12:00") },
                            {"pat_id": -789, "base_name":"CR", "ord_num_value":0.3, "result_time": DBUtil.parseDateValue("4/25/2009 12:00") },
                            {"pat_id": -789, "base_name":"CR", "ord_num_value":0.7, "result_time": DBUtil.parseDateValue("4/26/2009 6:00") },
                            #{"pat_id": -789, "base_name":"NA", "ord_num_value":151, "result_time": DBUtil.parseDateValue("5/6/2009 15:12") },
                        ],
                -999:   [],
            };

        expectedpatientEpisodeByIndexTimeById = \
            {   -123: {DBUtil.parseDateValue("4/6/2009 12:00"): {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00"),"days_until_end": 0.0, "TNI.None_0.count":1, "TNI.None_0.countInRange":0, "TNI.None_0.min":0.2, "TNI.None_0.max":0.2, "TNI.None_0.median":0.2, "TNI.None_0.mean":0.2, "TNI.None_0.std":0, "TNI.None_0.first":0.2, "TNI.None_0.last":0.2, "TNI.None_0.diff":0.0, "TNI.None_0.slope":0.0, "TNI.None_0.proximate":0.2, "TNI.None_0.firstTimeDays":-0.225, "TNI.None_0.lastTimeDays":-0.225, "TNI.None_0.proximateTimeDays":-0.225, "CR.None_0.count":0, "CR.None_0.countInRange":0, "CR.None_0.min":None, "CR.None_0.max":None, "CR.None_0.median":None, "CR.None_0.mean":None, "CR.None_0.std":None, "CR.None_0.first":None, "CR.None_0.last":None, "CR.None_0.diff":None, "CR.None_0.slope":None, "CR.None_0.proximate":None, "CR.None_0.firstTimeDays":None, "CR.None_0.lastTimeDays":None, "CR.None_0.proximateTimeDays":None, "LAC.None_0.count":0, "LAC.None_0.countInRange":0, "LAC.None_0.min":None, "LAC.None_0.max":None, "LAC.None_0.median":None, "LAC.None_0.mean":None, "LAC.None_0.std":None, "LAC.None_0.first":None, "LAC.None_0.last":None, "LAC.None_0.diff":None, "LAC.None_0.slope":None, "LAC.None_0.proximate":None, "LAC.None_0.firstTimeDays":None, "LAC.None_0.lastTimeDays":None, "LAC.None_0.proximateTimeDays":None, }},
                -456: {DBUtil.parseDateValue("5/6/2009 12:00"): {"patient_id": -456, "index_time":DBUtil.parseDateValue("5/6/2009 12:00"),"days_until_end": 0.0, "TNI.None_0.count":0, "TNI.None_0.countInRange":0, "TNI.None_0.min":None, "TNI.None_0.max":None, "TNI.None_0.median":None, "TNI.None_0.mean":None, "TNI.None_0.std":None, "TNI.None_0.first":None, "TNI.None_0.last":None, "TNI.None_0.diff":None, "TNI.None_0.slope":None, "TNI.None_0.proximate":None, "TNI.None_0.firstTimeDays":None, "TNI.None_0.lastTimeDays":None, "TNI.None_0.proximateTimeDays":None, "CR.None_0.count":0, "CR.None_0.countInRange":0, "CR.None_0.min":None, "CR.None_0.max":None, "CR.None_0.median":None, "CR.None_0.mean":None, "CR.None_0.std":None, "CR.None_0.first":None, "CR.None_0.last":None, "CR.None_0.diff":None, "CR.None_0.slope":None, "CR.None_0.proximate":None, "CR.None_0.firstTimeDays":None, "CR.None_0.lastTimeDays":None, "CR.None_0.proximateTimeDays":None, "LAC.None_0.count":0, "LAC.None_0.countInRange":0, "LAC.None_0.min":None, "LAC.None_0.max":None, "LAC.None_0.median":None, "LAC.None_0.mean":None, "LAC.None_0.std":None, "LAC.None_0.first":None, "LAC.None_0.last":None, "LAC.None_0.diff":None, "LAC.None_0.slope":None, "LAC.None_0.proximate":None, "LAC.None_0.firstTimeDays":None, "LAC.None_0.lastTimeDays":None, "LAC.None_0.proximateTimeDays":None, }},
                -789: {DBUtil.parseDateValue("6/6/2009 12:00"): {"patient_id": -789, "index_time":DBUtil.parseDateValue("6/6/2009 12:00"),"days_until_end": 0.0, "TNI.None_0.count":0, "TNI.None_0.countInRange":0, "TNI.None_0.min":None, "TNI.None_0.max":None, "TNI.None_0.median":None, "TNI.None_0.mean":None, "TNI.None_0.std":None, "TNI.None_0.first":None, "TNI.None_0.last":None, "TNI.None_0.diff":None, "TNI.None_0.slope":None, "TNI.None_0.proximate":None, "TNI.None_0.firstTimeDays":None, "TNI.None_0.lastTimeDays":None, "TNI.None_0.proximateTimeDays":None, "CR.None_0.count":3, "CR.None_0.countInRange":2, "CR.None_0.min":0.3, "CR.None_0.max":1.0, "CR.None_0.median":0.7, "CR.None_0.mean":0.6666667, "CR.None_0.std":0.2867442, "CR.None_0.first":1.0, "CR.None_0.last":0.7, "CR.None_0.diff":-0.3, "CR.None_0.slope":-0.01518987, "CR.None_0.proximate":0.7, "CR.None_0.firstTimeDays":-61, "CR.None_0.lastTimeDays":-41.25, "CR.None_0.proximateTimeDays":-41.25, "LAC.None_0.count":0, "LAC.None_0.countInRange":0, "LAC.None_0.min":None, "LAC.None_0.max":None, "LAC.None_0.median":None, "LAC.None_0.mean":None, "LAC.None_0.std":None, "LAC.None_0.first":None, "LAC.None_0.last":None, "LAC.None_0.diff":None, "LAC.None_0.slope":None, "LAC.None_0.proximate":None, "LAC.None_0.firstTimeDays":None, "LAC.None_0.lastTimeDays":None, "LAC.None_0.proximateTimeDays":None, }},
                -999: {DBUtil.parseDateValue("7/6/2009 12:00"): {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 12:00"),"days_until_end": 0.0, "TNI.None_0.count":0, "TNI.None_0.countInRange":0, "TNI.None_0.min":None, "TNI.None_0.max":None, "TNI.None_0.median":None, "TNI.None_0.mean":None, "TNI.None_0.std":None, "TNI.None_0.first":None, "TNI.None_0.last":None, "TNI.None_0.diff":None, "TNI.None_0.slope":None, "TNI.None_0.proximate":None, "TNI.None_0.firstTimeDays":None, "TNI.None_0.lastTimeDays":None, "TNI.None_0.proximateTimeDays":None, "CR.None_0.count":0, "CR.None_0.countInRange":0, "CR.None_0.min":None, "CR.None_0.max":None, "CR.None_0.median":None, "CR.None_0.mean":None, "CR.None_0.std":None, "CR.None_0.first":None, "CR.None_0.last":None, "CR.None_0.diff":None, "CR.None_0.slope":None, "CR.None_0.proximate":None, "CR.None_0.firstTimeDays":None, "CR.None_0.lastTimeDays":None, "CR.None_0.proximateTimeDays":None, "LAC.None_0.count":0, "LAC.None_0.countInRange":0, "LAC.None_0.min":None, "LAC.None_0.max":None, "LAC.None_0.median":None, "LAC.None_0.mean":None, "LAC.None_0.std":None, "LAC.None_0.first":None, "LAC.None_0.last":None, "LAC.None_0.diff":None, "LAC.None_0.slope":None, "LAC.None_0.proximate":None, "LAC.None_0.firstTimeDays":None, "LAC.None_0.lastTimeDays":None, "LAC.None_0.proximateTimeDays":None, }},
            };

        colNames = None;
        for patientId, basePatient in patientById.iteritems():
            colNames = list();
            (patientEpisodeByIndexTime, newColNames) = self.extractor.generateDateRangeIndexTimes_singlePatient("index_time","index_time", basePatient);
            colNames.extend(newColNames);

            # Query out lab result data
            labBaseNames = ["TNI","CR","LAC"];
            labResultTable = self.extractor.queryLabResults(labBaseNames, patientId);
            actualData = modelListFromTable(labResultTable);
            expectedData = expectedDataByPatientId[patientId];
            expectedKeys = None;
            if len(expectedData) > 0:
                expectedKeys = expectedData[0].keys();
            self.assertEqualDictList( expectedData, actualData, expectedKeys );

            # Parse back the results and load into patient data
            preTimeDelta = None; # Any time in the past
            postTimeDelta = timedelta(0);   # Only look for past items
            labsByBaseName = self.extractor.parseLabResultsData_singlePatient(modelListFromTable(labResultTable), patientId);

            newColNames = self.extractor.addLabFeatures_singlePatient(patientEpisodeByIndexTime, labsByBaseName, labBaseNames, preTimeDelta, postTimeDelta);
            colNames.extend(newColNames);

            expectedpatientEpisodeByIndexTime = expectedpatientEpisodeByIndexTimeById[patientId];
            actualData = patientEpisodeByIndexTime;
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, patientId, patient["CR.None_0.count"], patient;
                self.assertAlmostEqualsDict( expectedpatientEpisodeByIndexTime[indexTime], patient );
            self.assertEqual( len(expectedpatientEpisodeByIndexTime), len(actualData) );

    def test_flowsheet(self):
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00")},
                -456: {"patient_id": -456, "index_time":DBUtil.parseDateValue("5/6/2009 12:00")},
                -789: {"patient_id": -789, "index_time":DBUtil.parseDateValue("6/6/2009 12:00")},
                -999: {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 12:00")},
            }

        flowsheetNames = ["Resp","FiO2","Glasgow Coma Scale Score"];
        outFile = StringIO();
        self.extractor.queryFlowsheet(flowsheetNames, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = list(TabDictReader(actualDataFile));
        for row in actualData:  # Note flowsheet uses different column labels
            row["pat_id"] = int(row["pat_anon_id"]);
            row["base_name"] = row["flowsheet_name"];
            row["num_value"] = None;
            if row["flowsheet_value"] is not None and row["flowsheet_value"] != NULL_STRING:
                row["num_value"] = float(row["flowsheet_value"]);
            row["result_time"] = DBUtil.parseDateValue(row["shifted_record_dt_tm"]);
            
            #print >> sys.stderr, "%(pat_id)s, %(base_name)s, %(num_value)s, %(result_time)s" % row;

        expectedData = \
            [   
                #{"pat_id": -789, "base_name":"BP_High_Systolic", "num_value":123, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                {"pat_id": -789, "base_name":"Glasgow Coma Scale Score", "num_value":1.0, "result_time": DBUtil.parseDateValue("4/6/2009 12:00") },
                {"pat_id": -789, "base_name":"Glasgow Coma Scale Score", "num_value":0.3, "result_time": DBUtil.parseDateValue("4/25/2009 12:00") },
                {"pat_id": -789, "base_name":"Glasgow Coma Scale Score", "num_value":0.7, "result_time": DBUtil.parseDateValue("4/26/2009 6:00") },
                #{"pat_id": -789, "base_name":"BP_High_Systolic", "num_value":151, "result_time": DBUtil.parseDateValue("5/6/2009 15:12") },

                {"pat_id": -456, "base_name":"FiO2", "num_value":None, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
                #{"pat_id": -456, "base_name":"BP_High_Systolic", "num_value":145, "result_time": DBUtil.parseDateValue("4/25/2009 6:36") },
                {"pat_id": -456, "base_name":"Glasgow Coma Scale Score", "num_value":0.5, "result_time": DBUtil.parseDateValue("5/6/2009 15:12") },

                {"pat_id": -123, "base_name":"FiO2", "num_value":0.2, "result_time": DBUtil.parseDateValue("4/6/2009 6:36") },
                {"pat_id": -123, "base_name":"Glasgow Coma Scale Score", "num_value":2.1, "result_time": DBUtil.parseDateValue("4/6/2009 15:12") },
                {"pat_id": -123, "base_name":"FiO2", "num_value":0, "result_time": DBUtil.parseDateValue("4/6/2009 16:34") },
            ];
        self.assertEqualDictList( expectedData, actualData, expectedData[0].keys() );

        # Parse back the results and load into patient data
        colNames = list();
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("index_time","index_time", patientById.values(), colNames);

        preTimeDelta = None; # Any time in the past
        postTimeDelta = timedelta(0);   # Only look for past items
        flowsheetByNameByPatientId = self.extractor.parseFlowsheetFile(StringIO(outFile.getvalue()));
        self.extractor.addFlowsheetFeatures(patientEpisodeByIndexTimeById, flowsheetByNameByPatientId, flowsheetNames, preTimeDelta, postTimeDelta, colNames);
        
        expectedData = \
            {   -123: {DBUtil.parseDateValue("4/6/2009 12:00"): {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00"), "days_until_end": 0.0, "FiO2.None_0.count":1, "FiO2.None_0.countInRange":0, "FiO2.None_0.min":0.2, "FiO2.None_0.max":0.2, "FiO2.None_0.median":0.2, "FiO2.None_0.mean":0.2, "FiO2.None_0.std":0, "FiO2.None_0.first":0.2, "FiO2.None_0.last":0.2, "FiO2.None_0.diff":0.0, "FiO2.None_0.slope":0.0, "FiO2.None_0.proximate":0.2, "FiO2.None_0.firstTimeDays":-0.225, "FiO2.None_0.lastTimeDays":-0.225, "FiO2.None_0.proximateTimeDays":-0.225, "Glasgow Coma Scale Score.None_0.count":0, "Glasgow Coma Scale Score.None_0.countInRange":0, "Glasgow Coma Scale Score.None_0.min":None, "Glasgow Coma Scale Score.None_0.max":None, "Glasgow Coma Scale Score.None_0.median":None, "Glasgow Coma Scale Score.None_0.mean":None, "Glasgow Coma Scale Score.None_0.std":None, "Glasgow Coma Scale Score.None_0.first":None, "Glasgow Coma Scale Score.None_0.last":None, "Glasgow Coma Scale Score.None_0.diff":None, "Glasgow Coma Scale Score.None_0.slope":None, "Glasgow Coma Scale Score.None_0.proximate":None, "Glasgow Coma Scale Score.None_0.firstTimeDays":None, "Glasgow Coma Scale Score.None_0.lastTimeDays":None, "Glasgow Coma Scale Score.None_0.proximateTimeDays":None, "Resp.None_0.count":0, "Resp.None_0.countInRange":0, "Resp.None_0.min":None, "Resp.None_0.max":None, "Resp.None_0.median":None, "Resp.None_0.mean":None, "Resp.None_0.std":None, "Resp.None_0.first":None, "Resp.None_0.last":None, "Resp.None_0.diff":None, "Resp.None_0.slope":None, "Resp.None_0.proximate":None, "Resp.None_0.firstTimeDays":None, "Resp.None_0.lastTimeDays":None, "Resp.None_0.proximateTimeDays":None, }},
                -456: {DBUtil.parseDateValue("5/6/2009 12:00"): {"patient_id": -456, "index_time":DBUtil.parseDateValue("5/6/2009 12:00"), "days_until_end": 0.0, "FiO2.None_0.count":0, "FiO2.None_0.countInRange":0, "FiO2.None_0.min":None, "FiO2.None_0.max":None, "FiO2.None_0.median":None, "FiO2.None_0.mean":None, "FiO2.None_0.std":None, "FiO2.None_0.first":None, "FiO2.None_0.last":None, "FiO2.None_0.diff":None, "FiO2.None_0.slope":None, "FiO2.None_0.proximate":None, "FiO2.None_0.firstTimeDays":None, "FiO2.None_0.lastTimeDays":None, "FiO2.None_0.proximateTimeDays":None, "Glasgow Coma Scale Score.None_0.count":0, "Glasgow Coma Scale Score.None_0.countInRange":0, "Glasgow Coma Scale Score.None_0.min":None, "Glasgow Coma Scale Score.None_0.max":None, "Glasgow Coma Scale Score.None_0.median":None, "Glasgow Coma Scale Score.None_0.mean":None, "Glasgow Coma Scale Score.None_0.std":None, "Glasgow Coma Scale Score.None_0.first":None, "Glasgow Coma Scale Score.None_0.last":None, "Glasgow Coma Scale Score.None_0.diff":None, "Glasgow Coma Scale Score.None_0.slope":None, "Glasgow Coma Scale Score.None_0.proximate":None, "Glasgow Coma Scale Score.None_0.firstTimeDays":None, "Glasgow Coma Scale Score.None_0.lastTimeDays":None, "Glasgow Coma Scale Score.None_0.proximateTimeDays":None, "Resp.None_0.count":0, "Resp.None_0.countInRange":0, "Resp.None_0.min":None, "Resp.None_0.max":None, "Resp.None_0.median":None, "Resp.None_0.mean":None, "Resp.None_0.std":None, "Resp.None_0.first":None, "Resp.None_0.last":None, "Resp.None_0.diff":None, "Resp.None_0.slope":None, "Resp.None_0.proximate":None, "Resp.None_0.firstTimeDays":None, "Resp.None_0.lastTimeDays":None, "Resp.None_0.proximateTimeDays":None, }},
                -789: {DBUtil.parseDateValue("6/6/2009 12:00"): {"patient_id": -789, "index_time":DBUtil.parseDateValue("6/6/2009 12:00"), "days_until_end": 0.0, "FiO2.None_0.count":0, "FiO2.None_0.countInRange":0, "FiO2.None_0.min":None, "FiO2.None_0.max":None, "FiO2.None_0.median":None, "FiO2.None_0.mean":None, "FiO2.None_0.std":None, "FiO2.None_0.first":None, "FiO2.None_0.last":None, "FiO2.None_0.diff":None, "FiO2.None_0.slope":None, "FiO2.None_0.proximate":None, "FiO2.None_0.firstTimeDays":None, "FiO2.None_0.lastTimeDays":None, "FiO2.None_0.proximateTimeDays":None, "Glasgow Coma Scale Score.None_0.count":3, "Glasgow Coma Scale Score.None_0.countInRange":0, "Glasgow Coma Scale Score.None_0.min":0.3, "Glasgow Coma Scale Score.None_0.max":1.0, "Glasgow Coma Scale Score.None_0.median":0.7, "Glasgow Coma Scale Score.None_0.mean":0.6666667, "Glasgow Coma Scale Score.None_0.std":0.2867442, "Glasgow Coma Scale Score.None_0.first":1.0, "Glasgow Coma Scale Score.None_0.last":0.7, "Glasgow Coma Scale Score.None_0.diff":-0.3, "Glasgow Coma Scale Score.None_0.slope":-0.01518987, "Glasgow Coma Scale Score.None_0.proximate":0.7, "Glasgow Coma Scale Score.None_0.firstTimeDays":-61, "Glasgow Coma Scale Score.None_0.lastTimeDays":-41.25, "Glasgow Coma Scale Score.None_0.proximateTimeDays":-41.25, "Resp.None_0.count":0, "Resp.None_0.countInRange":0, "Resp.None_0.min":None, "Resp.None_0.max":None, "Resp.None_0.median":None, "Resp.None_0.mean":None, "Resp.None_0.std":None, "Resp.None_0.first":None, "Resp.None_0.last":None, "Resp.None_0.diff":None, "Resp.None_0.slope":None, "Resp.None_0.proximate":None, "Resp.None_0.firstTimeDays":None, "Resp.None_0.lastTimeDays":None, "Resp.None_0.proximateTimeDays":None, }},
                -999: {DBUtil.parseDateValue("7/6/2009 12:00"): {"patient_id": -999, "index_time":DBUtil.parseDateValue("7/6/2009 12:00"), "days_until_end": 0.0, "FiO2.None_0.count":0, "FiO2.None_0.countInRange":0, "FiO2.None_0.min":None, "FiO2.None_0.max":None, "FiO2.None_0.median":None, "FiO2.None_0.mean":None, "FiO2.None_0.std":None, "FiO2.None_0.first":None, "FiO2.None_0.last":None, "FiO2.None_0.diff":None, "FiO2.None_0.slope":None, "FiO2.None_0.proximate":None, "FiO2.None_0.firstTimeDays":None, "FiO2.None_0.lastTimeDays":None, "FiO2.None_0.proximateTimeDays":None, "Glasgow Coma Scale Score.None_0.count":0, "Glasgow Coma Scale Score.None_0.countInRange":0, "Glasgow Coma Scale Score.None_0.min":None, "Glasgow Coma Scale Score.None_0.max":None, "Glasgow Coma Scale Score.None_0.median":None, "Glasgow Coma Scale Score.None_0.mean":None, "Glasgow Coma Scale Score.None_0.std":None, "Glasgow Coma Scale Score.None_0.first":None, "Glasgow Coma Scale Score.None_0.last":None, "Glasgow Coma Scale Score.None_0.diff":None, "Glasgow Coma Scale Score.None_0.slope":None, "Glasgow Coma Scale Score.None_0.proximate":None, "Glasgow Coma Scale Score.None_0.firstTimeDays":None, "Glasgow Coma Scale Score.None_0.lastTimeDays":None, "Glasgow Coma Scale Score.None_0.proximateTimeDays":None, "Resp.None_0.count":0, "Resp.None_0.countInRange":0, "Resp.None_0.min":None, "Resp.None_0.max":None, "Resp.None_0.median":None, "Resp.None_0.mean":None, "Resp.None_0.std":None, "Resp.None_0.first":None, "Resp.None_0.last":None, "Resp.None_0.diff":None, "Resp.None_0.slope":None, "Resp.None_0.proximate":None, "Resp.None_0.firstTimeDays":None, "Resp.None_0.lastTimeDays":None, "Resp.None_0.proximateTimeDays":None, }},
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #print >> sys.stderr, key, value;
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
        self.assertEqual( len(expectedData), len(actualData) );

    def test_loadMapData(self):
        reader = self.extractor.loadMapData("CharlsonComorbidity-ICD9CM");  # Depends on external data file
        charlsonByICD9 = dict();
        for row in reader:
            charlsonByICD9[row["icd9cm"]] = row["charlson"];

        self.assertEqual("Dementia", charlsonByICD9["294.1"]);
        self.assertEqual("Dementia", charlsonByICD9["331.2"]);
        self.assertEqual("COPD", charlsonByICD9["490"]);
        self.assertEqual("COPD", charlsonByICD9["416.8"]);
        self.assertEqual("Malignancy Metastatic", charlsonByICD9["199"]);
        self.assertEqual("AIDS/HIV", charlsonByICD9["042"]);

    def test_ivFluids(self):
        patientById = \
            {   -123: {"patient_id": -123, "index_time":DBUtil.parseDateValue("4/6/2009 12:00")},
            }

        # Look for specific IV fluid medication subset
        ivfMedIds = set();
        for row in self.extractor.loadMapData("Medication.IVFluids"):
            if row["group"] == "isotonic":
                ivfMedIds.add(row["medication_id"]);

        outFile = StringIO();
        self.extractor.queryIVFluids(ivfMedIds, patientById, outFile);

        actualDataFile = StringIO(outFile.getvalue());
        actualData = self.extractor.parseIVFluidFile(actualDataFile);

        expectedDataFile = \
StringIO("""pat_id\tmedication_id\tstart_taking_time\tend_taking_time\tfreq_name\tmin_discrete_dose\tmin_rate
-123\t540102\t4/6/2009 12:30\t4/6/2009 12:30\tONCE\t250\tNone
-123\t16426\t4/6/2009 12:30\t4/6/2009 15:00\tCONTINUOUS\tNone\t500
-123\t540115\t4/6/2009 14:00\t4/6/2009 14:00\tONCE\t500\tNone
-123\t540102\t4/6/2009 16:00\t4/10/2009 16:00\tDAILY\t250\tNone
-123\t27838\t4/6/2009 16:30\t4/6/2009 18:00\tCONTINUOUS\tNone\t500
-123\t4318\t4/6/2009 17:00\t4/6/2009 18:00\tCONTINUOUS\tNone\t1000
""");
        expectedData = self.extractor.parseIVFluidFile(expectedDataFile);
        self.assertEqualDictList( expectedData[-123], actualData[-123], expectedData[-123][0].keys() );


        # Parse back the results and load into patient data
        colNames = ["patient_id"];
        patientEpisodeByIndexTimeById = self.extractor.generateDateRangeIndexTimes("index_time","index_time", patientById.values(), colNames);

        thresholdVolumes = [500,1000,2000,3000,4000,5000];  # Volumes (mL) of fluid interested in time until encountering
        checkpointTimes = [0, 0.5*60*60, 1*60*60, 2*60*60, 3*60*60, 4*60*60, 4.5*60*60, 5*60*60, 6*60*60, 7*60*60];  # Time checkpoints (seconds) interested in accumulated fluid volume by that time
        ivFluidsByPatientId = self.extractor.parseIVFluidFile(StringIO(outFile.getvalue()));
        self.extractor.addIVFluidFeatures(patientEpisodeByIndexTimeById, ivFluidsByPatientId, thresholdVolumes, checkpointTimes, colNames);
        
        expectedData = \
            {   -123: 
                {   DBUtil.parseDateValue("4/6/2009 12:00"): 
                    {   "patient_id": -123, 
                        "index_time":DBUtil.parseDateValue("4/6/2009 12:00"),
                        "days_until_end": 0.0,
                        "ivf.secondsUntilCC.500": 3600,
                        "ivf.secondsUntilCC.1000": 7200,
                        "ivf.secondsUntilCC.2000": 10800,
                        "ivf.secondsUntilCC.3000": 19200,   # 5 hours, 20 minutes
                        "ivf.secondsUntilCC.4000": 21600,
                        "ivf.secondsUntilCC.5000": None,
                        "ivf.CCupToSec.0": 0,
                        "ivf.CCupToSec.1800": 250, # 30 minutes   # POST-bolus volume
                        "ivf.CCupToSec.3600": 500, # 1 hour
                        "ivf.CCupToSec.7200": 1500, # 2 hours
                        "ivf.CCupToSec.10800": 2000, # 3 hours
                        "ivf.CCupToSec.14400": 2250, # 4 hours
                        "ivf.CCupToSec.16200": 2250, # 4.5 hours
                        "ivf.CCupToSec.18000": 2500, # 5 hours
                        "ivf.CCupToSec.21600": 4000, # 6 hours
                        "ivf.CCupToSec.25200": 4000, # 7 hours
                    }
                 },
            };
        actualData = patientEpisodeByIndexTimeById;
        for patientId, patientEpisodeByIndexTime in actualData.iteritems():
            for indexTime, patient in patientEpisodeByIndexTime.iteritems():
                #keys = patient.keys();
                #keys.sort();
                #for key in keys:
                #    print >> sys.stderr, key, patient[key];
                self.assertAlmostEqualsDict( expectedData[patientId][indexTime], patient );
                self.assertEqual(set(expectedData[patientId][indexTime].keys()), set(colNames));
        self.assertEqual( len(expectedData), len(actualData) );

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestDataExtractor("test_addClinicalItemFeatures"));
    #suite.addTest(TestDataExtractor("test_generateDateRangeIndexTimes_repeatPatient"));
    #suite.addTest(TestDataExtractor('test_labResults_perPatient'));
    #suite.addTest(TestDataExtractor('test_labResults'));
    #suite.addTest(TestDataExtractor('test_addTimeCycleFeatures'));
    suite.addTest(unittest.makeSuite(TestDataExtractor));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
