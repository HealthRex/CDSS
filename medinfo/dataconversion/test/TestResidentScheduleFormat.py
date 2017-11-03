#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, generatePlaceholders;

from medinfo.dataconversion.ResidentScheduleFormat import ResidentScheduleFormat;

class TestResidentScheduleFormat(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

        self.BASE_YEAR = 2013;  # Expected base/start year that the test data represents

        self.R1_DATA = \
            """Split dates in '( )'\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13
\t6/25 - 7/19\t7/20 - 8/16\t8/17 - 9/13\t9/14 - 10/11\t10/12 - 11/8\t11/9 - 12/6\t12/7 - 1/3\t1/4 - 1/31\t2/1 - 2/28\t3/1 - 3/28\t3/29 - 4/25\t4/26 - 5/23\t5/24 - 6/24
\t(7/6)\t(8/3)\t(8/31)\t(9/28)\t(10/26)\t(11/23)\t(12/21)\t(1/18)\t(2/15)\t(3/15)\t(4/12)\t(5/10)\t(6/7)
"R1VA"\tStanford Wards\tOncology\tStanford Wards\tVA ICU\tVA Night Team | Vacation\tStanford ED\tStanford Wards\tGastroenterology Inpatient | Gastroenterology Outpatient\tGeneral Cardiology\tSCV Wards\tVA Wards\tGeriatrics | VA Night Team\tPulmonology SUH | Vacation
"R1KC"\tVA ICU\tGeneral Cardiology\tStanford Wards\tSCV Wards\tStanford Night Team | Vacation\tOncology\tVA Wards\tStanford Wards\tHematology\tStanford ED\tInfectious Disease VA | Pulmonology SUH\tStanford Wards\tVacation | Geriatrics
"R1AC"\tSCV Wards\tVA ICU\tVA Wards\tStanford Wards\tVA Night Team | Vacation\tStanford Wards\tVA Wards\tGeneral Cardiology\tGastroenterology Inpatient | Gastroenterology Outpatient\tPulmonology SUH | Vacation\tStanford Wards\tStanford Night Team | Geriatrics\tOncology
""";
        self.R2_DATA = \
            """Split dates in '( )'\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13
\t7/1 - 7/26\t7/27 - 8/23\t8/24 - 9/20\t9/21 - 10/18\t10/19 - 11/15\t11/16 - 12/27\t12/28 - 1/10\t1/11 - 2/7\t2/8 - 3/7\t3/8 - 4/4\t4/5 - 5/2\t5/3 - 5/30\t5/31 - 6/30
\t(7/13)\t(8/10)\t(9/7)\t(10/5)\t(11/2)\t(12/7)\t(1/5)\t(1/25)\t(2/22)\t(3/22)\t(4/19)\t(5/17)\t(6/14)
"R2AA"\tStanford ICU\tVA Night Team | Palliative Care VA\tStanford Night Team | Global Health Elective\tCCU Heart Failure\tVA Vacation | Willow Block\tGastroenterology Outpatient | Rheumatology\tHoliday 12/28-1/1\tOutpatient Oncology | Johnson & Johnson\tJohnson & Johnson\tOutpatient Neuro | Nephrology Outpatient\tVA Vacation | Endocrinology\tSCV Wards\tVA Wards
\t\t\t\t\t\t\tPulmonology SUH\t\t\t\t\t\t
"R2MB"\tCCU Heart Failure\tStanford ICU\tStanford Wards\tWomen's Health | VA Ambulatory\tVA Wards\tHoliday 12/23-12/27\t\t\t\tSIM Block 4/2-4/4\tOutpatient Neuro | Stanford Night Team\tStanford Night Team | Menlo Clinic\tNephrology Outpatient 6/23-6/30
\t\t\t\t\t\tOutpatient Oncology | Outpatient Hematology\t\t\t\t--\t\t\tWomen's Health | Vacation
"R2DL"\tCCU Heart Failure\tGastroenterology Inpatient | Gastroenterology Outpatient\tResearch\tVA Wards\tNephrology Outpatient | Nephrology Inpatient\tVacation 11/30-12/13\tOncology\tVA Wards\tStanford ICU\tVA Night Team | Vacation\tStanford ED\tPulmonology SUH | Rheumatology\tHIV | VA Night Team
\t\t\t\t\t\tHomeless 12/14-12/22\t\t\t\t\t\t\t
\t\t\t\t\t\tHoliday 12/23-12/27\t\t\t\t\t\t\t
\t\t\t\t\t\tNephrology Inpatient\t\t\t\t\t\t\t
"R2TS"\tOutpatient Hematology | Outpatient Oncology\t-\t\t- | VA Night Team\tCCU Heart Failure\tHoliday 12/23-12/27\tSCV Wards\tPalliative Care VA | VA Night Team\tVacation | Hepatology\tStanford ICU\tVA Wards\tEndocrinology | Stanford Night Team\tVacation | HIV
\t\t\t\t\t\tHomeless | Neurology\t\t\t\t\t\t\t
""";

        self.converter = ResidentScheduleFormat();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        DBTestCase.tearDown(self);

    def test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the formatting process for R1s");
        headers = ["resident","rotation","start","end"];
        expectedData = \
            [
                RowItemModel( ['R1VA', 'Stanford Wards', datetime(2013, 6, 25, 7, 0), datetime(2013, 7, 20, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Oncology', datetime(2013, 7, 20, 7, 0), datetime(2013, 8, 17, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Stanford Wards', datetime(2013, 8, 17, 7, 0), datetime(2013, 9, 14, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'VA ICU', datetime(2013, 9, 14, 7, 0), datetime(2013, 10, 12, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'VA Night Team', datetime(2013, 10, 12, 7, 0), datetime(2013, 10, 26, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Vacation', datetime(2013, 10, 26, 7, 0), datetime(2013, 11, 9, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Stanford ED', datetime(2013, 11, 9, 7, 0), datetime(2013, 12, 7, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Stanford Wards', datetime(2013, 12, 7, 7, 0), datetime(2014, 1, 4, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Gastroenterology Inpatient', datetime(2014, 1, 4, 7, 0), datetime(2014, 1, 18, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Gastroenterology Outpatient', datetime(2014, 1, 18, 7, 0), datetime(2014, 2, 1, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'General Cardiology', datetime(2014, 2, 1, 7, 0), datetime(2014, 3, 1, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'SCV Wards', datetime(2014, 3, 1, 7, 0), datetime(2014, 3, 29, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'VA Wards', datetime(2014, 3, 29, 7, 0), datetime(2014, 4, 26, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Geriatrics', datetime(2014, 4, 26, 7, 0), datetime(2014, 5, 10, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'VA Night Team', datetime(2014, 5, 10, 7, 0), datetime(2014, 5, 24, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Pulmonology SUH', datetime(2014, 5, 24, 7, 0), datetime(2014, 6, 7, 7, 0)], headers ),
                RowItemModel( ['R1VA', 'Vacation', datetime(2014, 6, 7, 7, 0), datetime(2014, 6, 25, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'VA ICU', datetime(2013, 6, 25, 7, 0), datetime(2013, 7, 20, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'General Cardiology', datetime(2013, 7, 20, 7, 0), datetime(2013, 8, 17, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Stanford Wards', datetime(2013, 8, 17, 7, 0), datetime(2013, 9, 14, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'SCV Wards', datetime(2013, 9, 14, 7, 0), datetime(2013, 10, 12, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Stanford Night Team', datetime(2013, 10, 12, 7, 0), datetime(2013, 10, 26, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Vacation', datetime(2013, 10, 26, 7, 0), datetime(2013, 11, 9, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Oncology', datetime(2013, 11, 9, 7, 0), datetime(2013, 12, 7, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'VA Wards', datetime(2013, 12, 7, 7, 0), datetime(2014, 1, 4, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Stanford Wards', datetime(2014, 1, 4, 7, 0), datetime(2014, 2, 1, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Hematology', datetime(2014, 2, 1, 7, 0), datetime(2014, 3, 1, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Stanford ED', datetime(2014, 3, 1, 7, 0), datetime(2014, 3, 29, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Infectious Disease VA', datetime(2014, 3, 29, 7, 0), datetime(2014, 4, 12, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Pulmonology SUH', datetime(2014, 4, 12, 7, 0), datetime(2014, 4, 26, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Stanford Wards', datetime(2014, 4, 26, 7, 0), datetime(2014, 5, 24, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Vacation', datetime(2014, 5, 24, 7, 0), datetime(2014, 6, 7, 7, 0)], headers ),
                RowItemModel( ['R1KC', 'Geriatrics', datetime(2014, 6, 7, 7, 0), datetime(2014, 6, 25, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'SCV Wards', datetime(2013, 6, 25, 7, 0), datetime(2013, 7, 20, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'VA ICU', datetime(2013, 7, 20, 7, 0), datetime(2013, 8, 17, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'VA Wards', datetime(2013, 8, 17, 7, 0), datetime(2013, 9, 14, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Stanford Wards', datetime(2013, 9, 14, 7, 0), datetime(2013, 10, 12, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'VA Night Team', datetime(2013, 10, 12, 7, 0), datetime(2013, 10, 26, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Vacation', datetime(2013, 10, 26, 7, 0), datetime(2013, 11, 9, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Stanford Wards', datetime(2013, 11, 9, 7, 0), datetime(2013, 12, 7, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'VA Wards', datetime(2013, 12, 7, 7, 0), datetime(2014, 1, 4, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'General Cardiology', datetime(2014, 1, 4, 7, 0), datetime(2014, 2, 1, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Gastroenterology Inpatient', datetime(2014, 2, 1, 7, 0), datetime(2014, 2, 15, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Gastroenterology Outpatient', datetime(2014, 2, 15, 7, 0), datetime(2014, 3, 1, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Pulmonology SUH', datetime(2014, 3, 1, 7, 0), datetime(2014, 3, 15, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Vacation', datetime(2014, 3, 15, 7, 0), datetime(2014, 3, 29, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Stanford Wards', datetime(2014, 3, 29, 7, 0), datetime(2014, 4, 26, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Stanford Night Team', datetime(2014, 4, 26, 7, 0), datetime(2014, 5, 10, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Geriatrics', datetime(2014, 5, 10, 7, 0), datetime(2014, 5, 24, 7, 0)], headers ),
                RowItemModel( ['R1AC', 'Oncology', datetime(2014, 5, 24, 7, 0), datetime(2014, 6, 25, 7, 0)], headers ),
            ];
        actualData = self.converter.parseScheduleItems( StringIO(self.R1_DATA), self.BASE_YEAR );
        self.assertEqualList( expectedData, actualData );

        log.debug("Run the formatting process for R2s");
        headers = ["resident","rotation","start","end"];
        expectedData = \
            [
                RowItemModel( ['R2AA','Stanford ICU',datetime(2013,7,1,7),datetime(2013,7,27,7)], headers),
                RowItemModel( ['R2AA','VA Night Team',datetime(2013,7,27,7),datetime(2013,8,10,7)], headers),
                RowItemModel( ['R2AA','Palliative Care VA',datetime(2013,8,10,7),datetime(2013,8,24,7)], headers),
                RowItemModel( ['R2AA','Stanford Night Team',datetime(2013,8,24,7),datetime(2013,9,7,7)], headers),
                RowItemModel( ['R2AA','Global Health Elective',datetime(2013,9,7,7),datetime(2013,9,21,7)], headers),
                RowItemModel( ['R2AA','CCU Heart Failure',datetime(2013,9,21,7),datetime(2013,10,19,7)], headers),
                RowItemModel( ['R2AA','VA Vacation',datetime(2013,10,19,7),datetime(2013,11,2,7)], headers),
                RowItemModel( ['R2AA','Willow Block',datetime(2013,11,2,7),datetime(2013,11,16,7)], headers),
                RowItemModel( ['R2AA','Gastroenterology Outpatient',datetime(2013,11,16,7),datetime(2013,12,7,7)], headers),
                RowItemModel( ['R2AA','Rheumatology',datetime(2013,12,7,7),datetime(2013,12,28,7)], headers),
                RowItemModel( ['R2AA','Holiday',datetime(2013,12,28,7),datetime(2014,1,2,7)], headers),
                RowItemModel( ['R2AA','Pulmonology SUH',datetime(2014,1,2,7),datetime(2014,1,11,7)], headers),
                RowItemModel( ['R2AA','Outpatient Oncology',datetime(2014,1,11,7),datetime(2014,1,25,7)], headers),
                RowItemModel( ['R2AA','Johnson & Johnson',datetime(2014,1,25,7),datetime(2014,2,8,7)], headers),
                RowItemModel( ['R2AA','Johnson & Johnson',datetime(2014,2,8,7),datetime(2014,3,8,7)], headers),
                RowItemModel( ['R2AA','Outpatient Neuro',datetime(2014,3,8,7),datetime(2014,3,22,7)], headers),
                RowItemModel( ['R2AA','Nephrology Outpatient',datetime(2014,3,22,7),datetime(2014,4,5,7)], headers),
                RowItemModel( ['R2AA','VA Vacation',datetime(2014,4,5,7),datetime(2014,4,19,7)], headers),
                RowItemModel( ['R2AA','Endocrinology',datetime(2014,4,19,7),datetime(2014,5,3,7)], headers),
                RowItemModel( ['R2AA','SCV Wards',datetime(2014,5,3,7),datetime(2014,5,31,7)], headers),
                RowItemModel( ['R2AA','VA Wards',datetime(2014,5,31,7),datetime(2014,7,1,7)], headers),
                RowItemModel( ['R2MB','CCU Heart Failure',datetime(2013,7,1,7),datetime(2013,7,27,7)], headers),
                RowItemModel( ['R2MB','Stanford ICU',datetime(2013,7,27,7),datetime(2013,8,24,7)], headers),
                RowItemModel( ['R2MB','Stanford Wards',datetime(2013,8,24,7),datetime(2013,9,21,7)], headers),
                RowItemModel( ['R2MB','Women\'s Health',datetime(2013,9,21,7),datetime(2013,10,5,7)], headers),
                RowItemModel( ['R2MB','VA Ambulatory',datetime(2013,10,5,7),datetime(2013,10,19,7)], headers),
                RowItemModel( ['R2MB','VA Wards',datetime(2013,10,19,7),datetime(2013,11,16,7)], headers),
                RowItemModel( ['R2MB','Outpatient Oncology',datetime(2013,11,16,7),datetime(2013,12,7,7)], headers),
                RowItemModel( ['R2MB','Outpatient Hematology',datetime(2013,12,7,7),datetime(2013,12,23,7)], headers),
                RowItemModel( ['R2MB','Holiday',datetime(2013,12,23,7),datetime(2013,12,28,7)], headers),
                RowItemModel( ['R2MB','SIM Block',datetime(2014,4,2,7),datetime(2014,4,5,7)], headers),
                RowItemModel( ['R2MB','Outpatient Neuro',datetime(2014,4,5,7),datetime(2014,4,19,7)], headers),
                RowItemModel( ['R2MB','Stanford Night Team',datetime(2014,4,19,7),datetime(2014,5,3,7)], headers),
                RowItemModel( ['R2MB','Stanford Night Team',datetime(2014,5,3,7),datetime(2014,5,17,7)], headers),
                RowItemModel( ['R2MB','Menlo Clinic',datetime(2014,5,17,7),datetime(2014,5,31,7)], headers),
                RowItemModel( ['R2MB','Women\'s Health',datetime(2014,5,31,7),datetime(2014,6,14,7)], headers),
                RowItemModel( ['R2MB','Vacation',datetime(2014,6,14,7),datetime(2014,6,23,7)], headers),
                RowItemModel( ['R2MB','Nephrology Outpatient',datetime(2014,6,23,7),datetime(2014,7,1,7)], headers),
                RowItemModel( ['R2DL','CCU Heart Failure',datetime(2013,7,1,7),datetime(2013,7,27,7)], headers),
                RowItemModel( ['R2DL','Gastroenterology Inpatient',datetime(2013,7,27,7),datetime(2013,8,10,7)], headers),
                RowItemModel( ['R2DL','Gastroenterology Outpatient',datetime(2013,8,10,7),datetime(2013,8,24,7)], headers),
                RowItemModel( ['R2DL','Research',datetime(2013,8,24,7),datetime(2013,9,21,7)], headers),
                RowItemModel( ['R2DL','VA Wards',datetime(2013,9,21,7),datetime(2013,10,19,7)], headers),
                RowItemModel( ['R2DL','Nephrology Outpatient',datetime(2013,10,19,7),datetime(2013,11,2,7)], headers),
                RowItemModel( ['R2DL','Nephrology Inpatient',datetime(2013,11,2,7),datetime(2013,11,16,7)], headers),
                RowItemModel( ['R2DL','Nephrology Inpatient',datetime(2013,11,16,7),datetime(2013,11,30,7)], headers),
                RowItemModel( ['R2DL','Vacation',datetime(2013,11,30,7),datetime(2013,12,14,7)], headers),
                RowItemModel( ['R2DL','Homeless',datetime(2013,12,14,7),datetime(2013,12,23,7)], headers),
                RowItemModel( ['R2DL','Holiday',datetime(2013,12,23,7),datetime(2013,12,28,7)], headers),
                RowItemModel( ['R2DL','Oncology',datetime(2013,12,28,7),datetime(2014,1,11,7)], headers),
                RowItemModel( ['R2DL','VA Wards',datetime(2014,1,11,7),datetime(2014,2,8,7)], headers),
                RowItemModel( ['R2DL','Stanford ICU',datetime(2014,2,8,7),datetime(2014,3,8,7)], headers),
                RowItemModel( ['R2DL','VA Night Team',datetime(2014,3,8,7),datetime(2014,3,22,7)], headers),
                RowItemModel( ['R2DL','Vacation',datetime(2014,3,22,7),datetime(2014,4,5,7)], headers),
                RowItemModel( ['R2DL','Stanford ED',datetime(2014,4,5,7),datetime(2014,5,3,7)], headers),
                RowItemModel( ['R2DL','Pulmonology SUH',datetime(2014,5,3,7),datetime(2014,5,17,7)], headers),
                RowItemModel( ['R2DL','Rheumatology',datetime(2014,5,17,7),datetime(2014,5,31,7)], headers),
                RowItemModel( ['R2DL','HIV',datetime(2014,5,31,7),datetime(2014,6,14,7)], headers),
                RowItemModel( ['R2DL','VA Night Team',datetime(2014,6,14,7),datetime(2014,7,1,7)], headers),
                RowItemModel( ['R2TS','Outpatient Hematology',datetime(2013,7,1,7),datetime(2013,7,13,7)], headers),
                RowItemModel( ['R2TS','Outpatient Oncology',datetime(2013,7,13,7),datetime(2013,7,27,7)], headers),
                RowItemModel( ['R2TS','VA Night Team',datetime(2013,10,5,7),datetime(2013,10,19,7)], headers),
                RowItemModel( ['R2TS','CCU Heart Failure',datetime(2013,10,19,7),datetime(2013,11,16,7)], headers),
                RowItemModel( ['R2TS','Homeless',datetime(2013,11,16,7),datetime(2013,12,7,7)], headers),
                RowItemModel( ['R2TS','Neurology',datetime(2013,12,7,7),datetime(2013,12,23,7)], headers),
                RowItemModel( ['R2TS','Holiday',datetime(2013,12,23,7),datetime(2013,12,28,7)], headers),
                RowItemModel( ['R2TS','SCV Wards',datetime(2013,12,28,7),datetime(2014,1,11,7)], headers),
                RowItemModel( ['R2TS','Palliative Care VA',datetime(2014,1,11,7),datetime(2014,1,25,7)], headers),
                RowItemModel( ['R2TS','VA Night Team',datetime(2014,1,25,7),datetime(2014,2,8,7)], headers),
                RowItemModel( ['R2TS','Vacation',datetime(2014,2,8,7),datetime(2014,2,22,7)], headers),
                RowItemModel( ['R2TS','Hepatology',datetime(2014,2,22,7),datetime(2014,3,8,7)], headers),
                RowItemModel( ['R2TS','Stanford ICU',datetime(2014,3,8,7),datetime(2014,4,5,7)], headers),
                RowItemModel( ['R2TS','VA Wards',datetime(2014,4,5,7),datetime(2014,5,3,7)], headers),
                RowItemModel( ['R2TS','Endocrinology',datetime(2014,5,3,7),datetime(2014,5,17,7)], headers),
                RowItemModel( ['R2TS','Stanford Night Team',datetime(2014,5,17,7),datetime(2014,5,31,7)], headers),
                RowItemModel( ['R2TS','Vacation',datetime(2014,5,31,7),datetime(2014,6,14,7)], headers),
                RowItemModel( ['R2TS','HIV',datetime(2014,6,14,7),datetime(2014,7,1,7)], headers),
            ];
        actualData = self.converter.parseScheduleItems( StringIO(self.R2_DATA), self.BASE_YEAR );
        self.assertEqualList( expectedData, actualData );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestResidentScheduleFormat("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestResidentScheduleFormat("test_insertFile_skipErrors"));
    #suite.addTest(TestResidentScheduleFormat('test_executeIterator'));
    #suite.addTest(TestResidentScheduleFormat('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestResidentScheduleFormat));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
