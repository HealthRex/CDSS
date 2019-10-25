#!/usr/bin/env python
"""Test case for respective module in application package"""

import unittest
from cStringIO import StringIO

from Const import RUNNER_VERBOSITY
from Util import log
from medinfo.cpoe.cpoeSim.SimManager import SimManager
from medinfo.db import DBUtil
from medinfo.db.test.Util import DBTestCase


class TestSimManagerGrading(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        self.manager = SimManager()  # Instance to test on

        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()
        self.manager.buildCPOESimSchema()

        log.info("Populate the database with test data")

        # Basically import a bunch of rigged CSV or TSV files that have realistic simulating case and grading data
        # Get that data into the test database
        clinical_item_category_str = \
"""clinical_item_category_id;source_table
1;source_table
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(clinical_item_category_str), "clinical_item_category", delim=";")

        clinical_item_str = \
"""clinical_item_id;clinical_item_category_id;name
1;1;Clinical item 1
2;1;Clinical item 2
3;1;Clinical item 3
4;1;Clinical item 4
5;1;Clinical item 5
6;1;Clinical item 6
7;1;Clinical item 7
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(clinical_item_str), "clinical_item", delim=";")

        clinical_item_str = \
"""sim_user_id;name
0;Default user
1;Jonathan Chen
2;User 2
3;User 3
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(clinical_item_str), "sim_user", delim=";")

        sim_patient_str = \
"""sim_patient_id;name;age_years;gender
1;Patient One;40;Male
2;Patient Two;50;Female
3;Patient Three;60;Male
4;Patient Four;70;Female
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_patient_str), "sim_patient", delim=";")

        sim_state_str = \
"""sim_state_id;name
1;Sim state 1
2;Sim state 2
3;Sim state 3
4;Sim state 4
5;Sim state 5
6;Sim state 6
7;Sim state 7
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_state_str), "sim_state", delim=";")

        sim_patient_order_str = \
"""sim_patient_order_id;sim_user_id;sim_patient_id;clinical_item_id;relative_time_start;sim_state_id
1;0;1;1;1;1
2;1;1;2;2;2
3;1;1;3;3;3
4;1;1;4;4;4
5;1;1;5;5;5
6;1;1;6;6;6
7;1;1;7;7;7
8;2;2;1;1;1
9;3;2;2;2;1
10;3;2;3;3;2
11;2;3;1;1;1
12;3;3;2;2;2
13;3;3;3;3;3
14;1;4;1;1;2
15;1;4;2;2;3
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_patient_order_str), "sim_patient_order", delim=";")

        sim_grading_key_str = \
"""sim_grader_id;sim_state_id;clinical_item_id;score;group_name
Jonathan Chen;1;1;1;g1
Jonathan Chen;2;2;1;g2
Jonathan Chen;3;3;1;g3
Jonathan Chen;4;4;1;
Jonathan Chen;5;5;1;g5
Jonathan Chen;6;6;1;
Jonathan Chen;7;7;1;g7
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_grading_key_str), "sim_grading_key", delim=";")

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        DBTestCase.tearDown(self)

    def test_gradeCases(self):
        # Give the application ID of some simulated patient test cases and the name
        #   of a grading key and just verify that it produces the expected results
        sim_patient_ids = [1, 2, 3, 4, 5]
        sim_grading_key_id = "Jonathan Chen"
        expected_grades_by_patient_id = {
            1: {
                "total_score": 6,   # Default user (id = 0) is ignored and NULL group_names are counted separately
                "sim_patient_id": 1,
                "most_graded_user_id": 1,
                "most_active_user_id": 1
            },
            2: {
                "total_score": 1,   # Ungraded (clinical_item_id, sim_state_id) keys are omitted from summation
                "sim_patient_id": 2,
                "most_graded_user_id": 2,   # Most graded user is User 2 (even though most active is User 3)
                "most_active_user_id": 3
            },
            3: {
                "total_score": 3,
                "sim_patient_id": 3,
                "most_graded_user_id": 3,   # Most graded user is the most active one
                "most_active_user_id": 3
            },
            # 4: No grading available for the existing case
            # 5: Case doesn't exist
        }
        actual_grades_by_patient_id = self.manager.grade_cases(sim_patient_ids, sim_grading_key_id)
        self.assertEquals(expected_grades_by_patient_id, actual_grades_by_patient_id)


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
