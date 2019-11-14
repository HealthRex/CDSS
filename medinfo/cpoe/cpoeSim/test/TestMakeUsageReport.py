import unittest
import mock

from Const import RUNNER_VERBOSITY
from medinfo.db.test.Util import DBTestCase
from medinfo.cpoe.cpoeSim.analysis import make_usage_report
from Util import log, captured_output
from medinfo.db import DBUtil
from medinfo.cpoe.cpoeSim.SimManager import SimManager
from cStringIO import StringIO
import tempfile
import csv

header = ['user', 'patient', 'start_time', 'elapsed_time', 'total_num_clicks', 'num_note_clicks',
          'num_results_review_clicks', 'recommended_options', 'unique_recommended_options',
          'manual_search_options', 'total_orders', 'orders_from_recommender', 'orders_from_manual_search',
          'orders_from_recommender_missed']


def mock_aggregate_simulation_data(data_home, output_path):
    # create mock csv - we're not testing aggregate_simulation_data here
    content = [['1', '1']]

    with open(output_path, 'w') as outfile:
        outfile.write(str.join(',', header) + '\n')
        for row in content:
            outfile.write(str.join(',', row) + '\n')


@mock.patch('medinfo.cpoe.cpoeSim.analysis.make_usage_report.aggregate_simulation_data',
            side_effect=mock_aggregate_simulation_data)
class TestMakeUsageReport(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self)
        self.usage_reporter = SimManager()

        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader
        ClinicalItemDataLoader.build_clinical_item_psql_schemata()
        self.usage_reporter.buildCPOESimSchema()

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
            """
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(clinical_item_str), "clinical_item", delim=";")

        clinical_item_str = \
            """sim_user_id;name
            1;Jonathan Chen
            """
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(clinical_item_str), "sim_user", delim=";")

        sim_patient_str = \
            """sim_patient_id;name;age_years;gender
            1;Patient One;40;Male
            """
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_patient_str), "sim_patient", delim=";")

        sim_state_str = \
            """sim_state_id;name
            1;Sim state 1
            """
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_state_str), "sim_state", delim=";")

        sim_patient_order_str = \
            """sim_patient_order_id;sim_user_id;sim_patient_id;clinical_item_id;relative_time_start;sim_state_id
            1;1;1;1;1;1
            """
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_patient_order_str), "sim_patient_order", delim=";")

        sim_grading_key_str = \
            """sim_grader_id;sim_state_id;clinical_item_id;score;group_name;sim_case_name
            Jonathan Chen;1;1;1;g1;case_name
            Andre Kumar;1;1;2;g1;case_name
            """
        # Parse into DB insertion object
        DBUtil.insertFile(StringIO(sim_grading_key_str), "sim_grading_key", delim=";")

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        DBTestCase.tearDown(self)

    def test_not_enough_args(self, mock_aggregate_simulation_data):
        # setup
        argv = ['make_usage_report.py', '-g', tempfile.gettempdir() + '/tmp.csv']

        # test & verify
        self.verify_error_message_for_argv(argv, "Given parameters are not enough. Exiting.")

    def test_no_grader(self, mock_aggregate_simulation_data):
        # setup
        argv = ['make_usage_report.py', '../analysis/sim_data', tempfile.gettempdir() + '/tmp.csv']

        # test & verify
        self.verify_error_message_for_argv(argv, "No graders given. Cannot grade patient cases. Exiting.")

    def test_single_grader(self, mock_aggregate_simulation_data):
        # setup
        output_filename = tempfile.gettempdir() + '/tmp.csv'
        argv = ['make_usage_report.py', '../analysis/sim_data', '-g', 'Jonathan Chen', output_filename]

        # test
        make_usage_report.main(argv)

        # verify
        with open(output_filename) as output_file:
            output = csv.DictReader(output_file)
            self.assertTrue('grade ({})'.format(argv[3]) in output.fieldnames)
            # assert more columns than original + grade column
            self.assertGreater(len(output.fieldnames), len(header) + 1)

    def test_multiple_graders(self, mock_aggregate_simulation_data):
        # setup
        output_filename = tempfile.gettempdir() + '/tmp.csv'
        argv = ['make_usage_report.py', '../analysis/sim_data', '-g', 'Jonathan Chen,Andre Kumar', output_filename]

        # test
        make_usage_report.main(argv)

        # verify
        with open(output_filename) as output_file:
            output = csv.DictReader(output_file)
            self.assertTrue('grade ({})'.format(argv[3].split(',')[0]) in output.fieldnames)
            self.assertTrue('grade ({})'.format(argv[3].split(',')[1]) in output.fieldnames)
            # assert more columns than original + grade columns
            self.assertGreater(len(output.fieldnames), len(header) + 2)

    def verify_error_message_for_argv(self, argv, expected_error_message):
        with self.assertRaises(SystemExit) as cm:   # capture sys.exit() in the tested class
            with captured_output() as (out, err):
                make_usage_report.main(argv)

        actual_output = out.getvalue()
        self.assertEqual(expected_error_message, actual_output.split("\n", 1)[0])

        self.assertIsNone(cm.exception.code)    # we can verify exception code here


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestMakeUsageReport))

    return test_suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
