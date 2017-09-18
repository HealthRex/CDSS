import sys, os
from cStringIO import StringIO
from datetime import datetime
import unittest

from summary_stats import LabStats

class TestLabStats(unittest.TestCase):
    def setUp(self):
        """Prepare state for test cases"""
        # Create temp (SQLite) database file to work with
        # self.conn = sqlite3.connect(TEMP_DATABASE_FILENAME);

        # Application instance to test on
        self.maxDiff = None;
        self.app = LabStats();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        # Close DB connection
        # self.conn.close();

    def test_run(self):
        """Lab test descriptions, counts, prices, and volume charges"""
        # item_id: (name, description, count, order_code_description, min_price, max_price, mean_price, median_price, min_vc, max_vc, mean_vc, median_vc)
        expectedResults = \
            {
                68520: ('LAB11138R', 'HIV PHENO EXPR ANTIVIR RESIST', 1, 'HIV ANTIVIRAL SUSCEPTIBILITY', 43.0, 812.0, 427.5, 427.5, 43.0, 812.0, 427.5, 427.5),
                45953: ('LABHIVAB', 'HIV (TYPE 1 AND TYPE 2) ABY', 703, 'HIV (TYPE 1 AND TYPE 2) ABY', 38.0, 280.0, 159.0, 159.0, 26714.0, 196840.0, 111777.0, 111777.0),
                48624: ('LABPCEG7', 'ISTAT EG7, ARTERIAL', 12712, 'ISTAT EG7, ARTERIAL', 204.0, 815.0, 370.8, 219.0, 2593248.0, 10360280.0, 4713609.600000001, 2783928.0),
                45820: ('LABLPDPC', 'LIPID PLUS RISK PANEL WITH CALCULATED LDL', 82, 'LIPID PLUS RISK W/ CALC. LDL', 1198.0, 1198.0, 1198.0, 1198.0, 98236.0, 98236.0, 98236.0, 98236.0),
                49516: ('LABAFBC', 'AFB CULTURE, RESPIRATORY', 7402, 'AFB Culture/Conc.', 153.0, 337.0, 217.33333333333334, 162.0, 1132506.0, 2494474.0, 1608701.3333333335, 1199124.0),
                45753: ('LABPCG3', 'ISTAT G3+, ARTERIAL', 179184, 'ISTAT G3+, ARTERIAL', 815.0, 815.0, 815.0, 815.0, 146034960.0, 146034960.0, 146034960.0, 146034960.0),
                45908: ('LABTRFS', 'TRANSFERRIN SATURATION', 7398, 'TRANSFERRIN SATURATION', 165.0, 420.0, 292.5, 292.5, 1220670.0, 3107160.0, 2163915.0, 2163915.0)
            }
        item_ids = set([68520, 45953, 48624, 45820, 49516, 45753, 45908])
        actualResults = self.app.run()
        actualResults = {k: actualResults[k] for k in item_ids}
        self.assertEqual(expectedResults, actualResults);


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLabStats))
    return suite


if __name__=="__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
