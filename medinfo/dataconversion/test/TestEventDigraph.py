#!/usr/bin/python
"""
Test suite for respective module in application package.
"""

import unittest

from Const import RUNNER_VERBOSITY
from cStringIO import StringIO
from EventDigraphTestData import ED_TEST_INPUT_TABLES, ED_TEST_OUTPUT_TABLES
from medinfo.dataconversion.EventDigraph import EventDigraph
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.db.test.Util import DBTestCase
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 

class TestEventDigraph(DBTestCase):
    def setUp(self):
        """Prepare state for test cases."""
        DBTestCase.setUp(self)
        StrideLoader.build_stride_psql_schemata()
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        self._deleteTestRecords()
        self._insertTestRecords()

    def _insertTestRecords(self):
        """Populate database for with patient data."""
        # clinical_item_category
        testRecords = ED_TEST_INPUT_TABLES.get("clinical_item_category")
        DBUtil.insertFile(StringIO(testRecords), "clinical_item_category", \
                            delim="\t")
        # clinical_item
        testRecords = ED_TEST_INPUT_TABLES.get("clinical_item")
        DBUtil.insertFile(StringIO(testRecords), "clinical_item", delim="\t")
        # patient_item
        testRecords = ED_TEST_INPUT_TABLES.get("patient_item")
        DBUtil.insertFile(StringIO(testRecords), "patient_item", delim="\t")

    def tearDown(self):
        """Restore state from any setUp or test steps."""
        self._deleteTestRecords()
        DBTestCase.tearDown(self)

    def _deleteTestRecords(self):
        """Delete test records from database."""
        DBUtil.execute("DELETE FROM patient_item WHERE clinical_item_id < 0")
        DBUtil.execute("DELETE FROM clinical_item WHERE clinical_item_id < 0")
        DBUtil.execute("DELETE FROM clinical_item_category WHERE clinical_item_category_id < 0")

    def test_init(self):
        # Query events by clinical_item_category.
        # SELECT
        #     pi.patient_id AS sequence_id,
        #     pi.item_date AS event_time,
        #     cic.description AS event_id
        # FROM
        #     patient_item AS pi
        # JOIN
        #     clinical_item AS ci
        # ON
        #     pi.clinical_item_id = ci.clinical_item_id
        # JOIN
        #     clinical_item_category AS cic
        # ON
        #     ci.clinical_item_category_id = cic.clinical_item_category_id
        # ORDER BY
        #     sequence_id,
        #     event_time,
        #     event_id
        query = SQLQuery()
        query.addSelect('pi.patient_id AS sequence_id')
        query.addSelect('pi.item_date AS event_time')
        query.addSelect('cic.description AS event_id')
        query.addFrom('patient_item AS pi')
        query.addJoin('clinical_item AS ci', 'pi.clinical_item_id = ci.clinical_item_id')
        query.addJoin('clinical_item_category AS cic', 'ci.clinical_item_category_id = cic.clinical_item_category_id')
        query.addOrderBy('sequence_id')
        query.addOrderBy('event_time')
        query.addOrderBy('event_id')
        events = DBUtil.execute(query)

        # Build graph based on clinical_item_category.
        categoryDigraph = EventDigraph(events)
        # Sort for easier comparison against test data.
        actualCategoryNodes = sorted(categoryDigraph.nodes())
        actualCategoryEdges = sorted(categoryDigraph.edges())

        # Validate results.
        expectedCategoryNodes = ED_TEST_OUTPUT_TABLES['test_init']['category_nodes']
        self.assertEqualList(actualCategoryNodes, expectedCategoryNodes)
        expectedCategoryEdges = ED_TEST_OUTPUT_TABLES['test_init']['category_edges']
        self.assertEqualList(actualCategoryEdges, expectedCategoryEdges)

        # Query events by clinical_item.
        # SELECT
        #     pi.patient_id AS sequence_id,
        #     pi.item_date AS event_time,
        #     ci.description AS event_id
        # FROM
        #     patient_item AS pi
        # JOIN
        #     clinical_item AS ci
        # ON
        #     pi.clinical_item_id = ci.clinical_item_id
        # ORDER BY
        #     sequence_id,
        #     event_time,
        #     event_id
        query = SQLQuery()
        query.addSelect('pi.patient_id AS sequence_id')
        query.addSelect('pi.item_date AS event_time')
        query.addSelect('ci.description AS event_id')
        query.addFrom('patient_item AS pi')
        query.addJoin('clinical_item AS ci', 'pi.clinical_item_id = ci.clinical_item_id')
        query.addJoin('clinical_item_category AS cic', 'ci.clinical_item_category_id = cic.clinical_item_category_id')
        query.addOrderBy('sequence_id')
        query.addOrderBy('event_time')
        query.addOrderBy('event_id')
        events = DBUtil.execute(query)

        # Build graph based on clinical_item.
        itemDigraph = EventDigraph(events)
        # Sort for easier comparison against test data.
        actualItemNodes = sorted(itemDigraph.nodes())
        actualItemEdges = sorted(itemDigraph.edges())

        # Validate results.
        expectedItemNodes = ED_TEST_OUTPUT_TABLES['test_init']['item_nodes']
        self.assertEqualList(actualItemNodes, expectedItemNodes)
        expectedItemEdges = ED_TEST_OUTPUT_TABLES['test_init']['item_edges']
        self.assertEqualList(actualItemEdges, expectedItemEdges)

    def test_draw(self):
        # Query events by clinical_item_category.
        # SELECT
        #     pi.patient_id AS sequence_id,
        #     pi.item_date AS event_time,
        #     cic.description AS event_id
        # FROM
        #     patient_item AS pi
        # JOIN
        #     clinical_item AS ci
        # ON
        #     pi.clinical_item_id = ci.clinical_item_id
        # JOIN
        #     clinical_item_category AS cic
        # ON
        #     ci.clinical_item_category_id = cic.clinical_item_category_id
        # ORDER BY
        #     sequence_id,
        #     event_time,
        #     event_id
        query = SQLQuery()
        query.addSelect('pi.patient_id AS sequence_id')
        query.addSelect('pi.item_date AS event_time')
        query.addSelect('cic.description AS event_id')
        query.addFrom('patient_item AS pi')
        query.addJoin('clinical_item AS ci', 'pi.clinical_item_id = ci.clinical_item_id')
        query.addJoin('clinical_item_category AS cic', 'ci.clinical_item_category_id = cic.clinical_item_category_id')
        query.addOrderBy('sequence_id')
        query.addOrderBy('event_time')
        query.addOrderBy('event_id')
        events = DBUtil.execute(query)

        # Build graph based on clinical_item_category.
        categoryDigraph = EventDigraph(events)
        categoryDigraphVizFileName = "test-category-digraph.png"
        categoryDigraph.draw(categoryDigraphVizFileName)

def suite():
    """
    Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test".
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEventDigraph))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
