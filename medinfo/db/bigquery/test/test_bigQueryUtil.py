'''
need a delete list to remove from GCP after testing (do this in web GUI)
'''
import os
import unittest
import csv

from medinfo.dataconversion.test.Const import RUNNER_VERBOSITY
from medinfo.dataconversion.Util import log
from medinfo.db.bigquery import bigQueryUtil
from medinfo.common.test.Util import MedInfoTestCase
from medinfo.db.Model import RowItemModel

from google.cloud import bigquery

TEST_DEST_DATASET = 'test_dataset'
TEST_TABLE_ID = 'unittest_bigQueryUtil'
TMP_DIR = '/tmp'

class test_bigQueryUtil(MedInfoTestCase):

    def setUp(self):
        """Prepare state for test cases"""

        # create dummy CSV
        self.tmp_dummy_csv_path = TMP_DIR + '/unittest_bq_dummy.csv'
        self.dummy_table = lines = [['num', 'char']] + [[n, chr(ord('a')+n)] for n in range(26)]
        with open(self.tmp_dummy_csv_path, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerows(lines)

        self.tmp_csv_path = TMP_DIR + '/unittest_bq.csv'

        self.bqConn = bigQueryUtil.connection()
        self.bqClient = bigQueryUtil.BigQueryClient()

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        bqCursor = self.bqConn.cursor()
        bqCursor.execute('DELETE FROM %s.%s WHERE true;' % (TEST_DEST_DATASET, TEST_TABLE_ID))

        log.info("Removing tmp CSV files")
        if os.path.exists(self.tmp_csv_path):
            os.remove(self.tmp_csv_path)
        if os.path.exists(self.tmp_dummy_csv_path):
            os.remove(self.tmp_dummy_csv_path)

    def test_create_table_from_schema(self):
        schema = [bigquery.SchemaField(u'num',  u'INTEGER', u'REQUIRED', None, ()),
                   bigquery.SchemaField(u'char', u'STRING', u'NULLABLE', None, ())]

        self.bqClient.create_new_table_from_schema(TEST_DEST_DATASET, TEST_TABLE_ID, schema)

        table_ref = self.bqClient.client.dataset(TEST_DEST_DATASET).table(TEST_TABLE_ID)
        table = self.bqClient.client.get_table(table_ref)
        bq_schema = table.schema

        for ref_schema_field, cmp_schema_field in zip(schema, bq_schema):
            print(ref_schema_field.to_api_repr(), cmp_schema_field.to_api_repr())
            assert ref_schema_field.name == cmp_schema_field.name
            assert ref_schema_field.field_type == cmp_schema_field.field_type
            assert ref_schema_field.is_nullable == cmp_schema_field.is_nullable

    def _test_query_from_bq_table(self):
        '''skipping this for now, need to create a permanent test table to query from'''

        query = '''
                SELECT stride_treatment_team_id, pat_enc_csn_id, treatment_team
                FROM stride_2008_2017.stride_treatment_team
                WHERE stride_treatment_team_id IN UNNEST(@tt_ids);
                '''

        headers = ['stride_treatment_team_id', 'pat_enc_csn_id', 'treatment_team']
        treatment_team_ids = list(range(2141155, 2141205))
        query_params = [
            bigquery.ArrayQueryParameter('tt_ids', 'INT64', treatment_team_ids)
        ]

        query_job = self.bqClient.queryBQ(str(query), query_params=query_params, location='US', batch_mode=False,
                                          verbose=True)

        actual_data = []
        with open(self.tmp_csv_path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for row in query_job:
                writer.writerow(row.values())
                actual_data.append(row.values)

        # TODO fill expected data
        expected_data = []
        self.assertEqualTable(expected_data, actual_data)

    def test_load_csv_to_table(self):
        self.bqClient.load_csv_to_table(TEST_DEST_DATASET, TEST_TABLE_ID, self.tmp_dummy_csv_path, skip_rows=1,
                                        append_to_table=True)
        query = 'SELECT * FROM {}.{}'.format(TEST_DEST_DATASET, TEST_TABLE_ID)

        query_job = self.bqClient.queryBQ(str(query), location='US', batch_mode=False,
                                          verbose=True)

        actual_data = [['num', 'char']]
        for row in query_job:
            actual_data.append([row.num, row.char])
        self.assertEqualTable(self.dummy_table, actual_data)

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(test_bigQueryUtil))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())