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

class TestPreliminaryQuery(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        self.patientIds = [-123,-456,-789,-999]

    def test_clinicalPreliminaryQueryByName(self):
        expectedOutput = \
        """
        SELECT pat.patient_id as patient_id, index_time, item_date
        FROM (
            SELECT patient_id, index_time
            FROM main_patient_table
            WHERE patient_id IN ('-123', '-456', '-789', '-999')
        ) AS pat
        LEFT JOIN (
            SELECT patient_id , item_date
            FROM patient_item
            WHERE clinical_item_id IN (-100,-200)
            AND patient_id IN (-123,-456,-789,-999)
            ORDER BY patient_id, item_date
        ) AS item
        ON pat.patient_id==item.patient_id
        ORDER BY pat.patient_id, pat.index_time, item_date
        """

        clinicalItemNames = ["TestItem100","TestItem200"];

        instance = ClinicalPreliminaryQueryByName(self.patientIds, clinicalItemNames)
        queryString = instance.writeQuery()
        self.assertEqualFile(StringIO(expectedOutput), StringIO(queryString), whitespace=False)

    def test_clinicalPreliminaryQueryByCategory(self):
        expectedOutput = \
        """
        SELECT pat.patient_id, index_time, item_date
        FROM (
            SELECT patient_id, index_time
            FROM main_patient_table
            WHERE patient_id IN ('-123', '-456', '-789', '-999')
        ) AS pat
        LEFT JOIN (
            SELECT patient_id , item_date
            FROM patient_item
            WHERE clinical_item_id IN (-100,-200)
            AND patient_id IN (-123,-456,-789,-999)
            ORDER BY patient_id, item_date
        ) AS item
        ON pat.patient_id==item.patient_id
        ORDER BY pat.patient_id, pat.index_time, item_name, item_date
        """

        clinicalItemCategoryIds = [-100];
        instance = ClinicalPreliminaryQueryByCategory(self.patientIds, clinicalItemCategoryIds)
        queryString = instance.writeQuery()
        self.assertEqualFile(StringIO(expectedOutput), StringIO(queryString), whitespace=False)

    def test_labPreliminaryQuery(self):
        expectedOutput = \
        """
        SELECT patient_id, index_time, item.base_name as item_name, item.ord_num_value as value, result_flag, result_in_range_yn, result_time as item_date
        FROM (
            SELECT patient_id, index_time
            FROM main_patient_table
            WHERE patient_id IN ('-123', '-456', '-789', '-999')
        ) AS pat
        LEFT JOIN (
            SELECT pat_id , base_name , ord_num_value , result_flag , result_in_range_yn , sor.result_time
            FROM stride_order_results as sor, stride_order_proc as sop
            WHERE sor.order_proc_id = sop.order_proc_id
            AND base_name IN ('TNI','CR','LAC')
            AND pat_id IN ('-123','-456','-789','-999')
            ORDER BY pat_id , base_name, sor.result_time
        ) AS item
        ON pat.patient_id==item.pat_id
        ORDER BY pat.patient_id, pat.index_time, item_name, item_date
        """

        baseNames = ["TNI", "CR", "LAC"]
        instance = LabPreliminaryQuery(self.patientIds, baseNames)
        queryString = instance.writeQuery()
        self.assertEqualFile(StringIO(expectedOutput), StringIO(queryString), whitespace=False)

    def test_flowsheetPreliminaryQuery(self):
        expectedOutput = \
        """
        SELECT patient_id, index_time, item.flowsheet_name as item_name, item.flowsheet_value as value, shifted_record_dt_tm as item_date
        FROM (
            SELECT patient_id, index_time
            FROM main_patient_table
            WHERE patient_id IN ('-123', '-456', '-789', '-999')
        ) AS pat
        LEFT JOIN (
            SELECT pat_anon_id , flo_meas_id , flowsheet_name , flowsheet_value , shifted_record_dt_tm
            FROM stride_flowsheet
            WHERE flowsheet_name IN ('Resp','FiO2','Glasgow Coma Scale Score')
            AND pat_anon_id IN ('-123','-456','-789','-999')
        ORDER BY pat_anon_id, flowsheet_name, shifted_record_dt_tm
        ) AS item
        ON pat.patient_id==item.pat_anon_id
        ORDER BY pat.patient_id, pat.index_time, item_name, item_date
        """

        flowsheetNames = ["Resp", "FiO2", "Glasgow Coma Scale Score"]
        instance = FlowsheetPreliminaryQuery(self.patientIds, flowsheetNames)
        queryString = instance.writeQuery()
        self.assertEqualFile(StringIO(expectedOutput), StringIO(queryString), whitespace=False)

    def test_ivFluidPreliminaryQuery(self):
        expectedOutput = \
        """
        SELECT pat.patient_id as patient_id, index_time, start_taking_time as item_date, end_taking_time as item_end_date, freq_name , min_discrete_dose , min_rate
        FROM (
            SELECT patient_id, index_time
            FROM main_patient_table
            WHERE patient_id IN ('-123')
        ) AS pat
        LEFT JOIN (
            SELECT pat_id , medication_id , start_taking_time , end_taking_time , freq_name , min_discrete_dose , min_rate
            FROM stride_order_med
            WHERE medication_id IN ('540102','4318','14858','590267','540115','16426','27838','15882')
            AND pat_id IN ('-123')
            AND freq_name not like '%PRN%' AND freq_name not like '%PACU%' AND freq_name not like '%ENDOSCOPY%'
            AND end_taking_time is not null
            ORDER BY pat_id , start_taking_time , end_taking_time
        ) AS item
        ON pat.patient_id==item.pat_id
        ORDER BY pat.patient_id, pat.index_time, item_date, item_end_date
        """

        medicationGroups = ["isotonic"]
        instance = IVFluidPreliminaryQuery([-123], medicationGroups)
        queryString = instance.writeQuery()
        self.assertEqualFile(StringIO(expectedOutput), StringIO(queryString), whitespace=False)

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestPreliminaryQuery("test_clinicalPreliminaryQueryByName"));
    #suite.addTest(TestPreliminaryQuery("test_clinicalPreliminaryQueryByCategory"))
    #suite.addTest(TestPreliminaryQuery("test_labPreliminaryQuery"))
    #suite.addTest(TestPreliminaryQuery("test_flowsheetPreliminaryQuery"))
    suite.addTest(TestPreliminaryQuery("test_ivFluidPreliminaryQuery"))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
