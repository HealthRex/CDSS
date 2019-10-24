#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime
import unittest

from Const import RUNNER_VERBOSITY
from Util import log

from medinfo.db.test.Util import DBTestCase

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable

from medinfo.cpoe.cpoeSim.SimManager import SimManager


class TestSimManagerGrading(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        self.manager = SimManager()  # Instance to test on

        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()
        self.manager.buildCPOESimSchema()

        log.info("Populate the database with test data")

        #### Basically import a bunch of rigged CSV or TSV files that have realistic simulating case and grading data
        # Get that data into the test database

        dataTextStr = \
"""sim_result_id;name;description;group_string;priority
-10;Temp;Temperature (F);Flowsheet>Vitals;10
-20;Pulse;Pulse / Heart Rate (HR);Flowsheet>Vitals;20
-30;SBP;Blood Pressure, Systolic (SBP);Flowsheet>Vitals;30
-40;DBP;Blood Pressure, Diastolic (DBP);Flowsheet>Vitals;40
-50;Resp;Respirations (RR);Flowsheet>Vitals;50
-60;FiO2;Fraction Inspired Oxygen;Flowsheet>Vitals;60
-70;Urine;Urine Output (UOP);Flowsheet>Vitals;70
"""     # Parse into DB insertion object
        DBUtil.insertFile(StringIO(dataTextStr), "sim_result", delim=";")
        # Could change the is pandas insert_sql file...
        # Do same for sim_patient_order, sim_grading_key, sim_user, whatever else is just enough to get grading test to run
        # Do same for sim_patient_order, sim_grading_key, sim_user, whatever else is just enough to get grading test to run
        # Do same for sim_patient_order, sim_grading_key, sim_user, whatever else is just enough to get grading test to run
        # Do same for sim_patient_order, sim_grading_key, sim_user, whatever else is just enough to get grading test to run
        # Do same for sim_patient_order, sim_grading_key, sim_user, whatever else is just enough to get grading test to run

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        #self.purgeTestRecords();
        DBTestCase.tearDown(self)

    def test_gradeCases(self):
        # Give the application ID of some simulated patient test cases and the name
        #   of a grading key and just verify that it produces the expected results

        simPatientIds = [1, 2, 3, 4, 5]
        simGradingKeyId = "JonCVersion"
        verifyGradesByPatientId = {1: 23, 2: 65, 3: 65, 4: 32, 5: 32}
        sampleGradesByPatientId = self.manager.grade_cases(simPatientIds, simGradingKeyId)
        self.assertEquals(verifyGradesByPatientId, sampleGradesByPatientId)


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSimManagerGrading))

    return test_suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
