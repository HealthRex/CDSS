#!/usr/bin/env python
"""Test case for respective module in application package"""

import unittest
from io import BytesIO  # for Python 3 use StringIO
from io import StringIO

import json
import csv
from .Const import RUNNER_VERBOSITY
from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM
from .Util import log, captured_output
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
4;User 4
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(clinical_item_str), "sim_user", delim=";")

        sim_patient_str = \
"""sim_patient_id;name;age_years;gender
1;Patient One;40;Male
2;Patient Two;50;Female
3;Patient Three;60;Male
4;Patient Four;70;Female
5;Patient Five;80;Male
6;Patient Six;90;Female
7;Patient Seven;100;Male
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
16;2;5;1;1;3
17;2;5;2;2;4
18;3;6;4;1;1
19;3;6;4;2;2
20;3;6;4;3;3
21;4;7;5;1;1
22;4;7;5;2;2
23;4;7;5;3;3
24;4;7;5;4;4
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
Jonathan Chen;3;1;1;g8
Jonathan Chen;4;2;1;g8
Jonathan Chen;1;4;-1000;
Jonathan Chen;2;4;10;
Jonathan Chen;3;4;2000;
Jonathan Chen;1;5;-1000;g9
Jonathan Chen;2;5;-1;
Jonathan Chen;3;5;0;g10
Jonathan Chen;3;5;-500;
"""
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_grading_key_str), "sim_grading_key", delim=";")

        self.expected_grades_by_patient_id = [
            {
                "total_score": 6,   # Default user (id = 0) is ignored and NULL group_names are counted separately
                "sim_patient_id": 1,
                "most_graded_user_id": 1,
                "most_active_user_id": 1,
                "sim_grader_id": "Jonathan Chen"
            },
            {
                "total_score": 1,   # Ungraded (clinical_item_id, sim_state_id) keys are omitted from summation
                "sim_patient_id": 2,
                "most_graded_user_id": 2,   # Most graded user is User 2 (even though most active is User 3)
                "most_active_user_id": 3,
                "sim_grader_id": "Jonathan Chen"
            },
            {
                "total_score": 3,
                "sim_patient_id": 3,
                "most_graded_user_id": 3,   # Most graded user is the most active one
                "most_active_user_id": 3,
                "sim_grader_id": "Jonathan Chen"
            },
            # 4: No grading available for the existing case
            {
                "total_score": 1,   # Scores in the same group g8 are counted only once
                "sim_patient_id": 5,
                "most_graded_user_id": 2,
                "most_active_user_id": 2,
                "sim_grader_id": "Jonathan Chen"
            },
            {
                "total_score": 1010,    # Non-uniform scores (i.e., not all scores = 1)
                "sim_patient_id": 6,
                "most_graded_user_id": 3,
                "most_active_user_id": 3,
                "sim_grader_id": "Jonathan Chen"
            },
            {
                "total_score": -1501,   # All negative and one 0 score results in negative score
                "sim_patient_id": 7,
                "most_graded_user_id": 4,
                "most_active_user_id": 4,
                "sim_grader_id": "Jonathan Chen"
            }
            # 8: Case doesn't exist
        ]

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        DBTestCase.tearDown(self)

    def test_gradeCases(self):
        # Give the application ID of some simulated patient test cases and the name
        #   of a grading key and just verify that it produces the expected results
        sim_patient_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        sim_grading_key_id = "Jonathan Chen"
        actual_grades_by_patient_id = self.manager.grade_cases(sim_patient_ids, sim_grading_key_id)
        self.assertEqual(self.expected_grades_by_patient_id, actual_grades_by_patient_id)

    def test_commandLine(self):
        argv = ["SimManager.py", "-p", "1,2,3,4,5,6", "-g", "Jonathan Chen"]
        with captured_output() as (out, err):
            self.manager.main(argv)

        actual_output = out.getvalue()

        actual_comment_line, output_csv = actual_output.split("\n", 1)

        # verify comment line
        expected_comment_line = COMMENT_TAG + " " + json.dumps({"argv": argv})
        self.assertEqual(expected_comment_line, actual_comment_line)

        # verify csv
        actual_output_csv = StringIO(output_csv)
        reader = csv.DictReader(actual_output_csv)
        # verify header
        self.assertEqualList(sorted(self.expected_grades_by_patient_id[0].keys()), sorted(reader.fieldnames))

        # verify lines
        for line_num, actual_grade in enumerate(reader):
            expected_grade_str_values = {k: str(v) for k, v in self.expected_grades_by_patient_id[line_num].items()}
            self.assertEqual(expected_grade_str_values, actual_grade)

    def test_commandLine_no_patientIds(self):
        argv = ["SimManager.py", "-g", "Jonathan Chen"]
        self.verify_error_message_for_argv(argv, "No patient cases given. Nothing to grade. Exiting.")

    def test_commandLine_no_graderIds(self):
        argv = ["SimManager.py", "-p", "1"]
        self.verify_error_message_for_argv(argv, "No graders given. Cannot grade patient cases. Exiting.")

    def verify_error_message_for_argv(self, argv, expected_error_message):
        with self.assertRaises(SystemExit) as cm:   # capture sys.exit() in the tested class
            with captured_output() as (out, err):
                self.manager.main(argv)

        actual_output = out.getvalue()
        self.assertEqual(expected_error_message, actual_output.split("\n", 1)[0])

        self.assertIsNone(cm.exception.code)    # we can verify exception code here


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSimManagerGrading))

    return test_suite


# TODO testcase for different scores for same group in different state

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
