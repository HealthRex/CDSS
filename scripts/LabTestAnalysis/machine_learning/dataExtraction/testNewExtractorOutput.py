import sys, os, gzip
from cStringIO import StringIO
from datetime import datetime, timedelta;
import unittest

from medinfo.dataconversion.test.Const import RUNNER_VERBOSITY;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil

class TestOutput(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

    def test_newExtractorOutput(self):
        firstFile = gzip.open("labFeatureMatrix.LABFER.2013-01-01.2013-01-02.tab.gz",'r').read(12000)
        secondFile = gzip.open("labFeatureMatrix.newDataExtractor.LABFER.2013-01-01.2013-01-02.tab.gz",'r').read(12000)
        self.assertEqualFile(StringIO(firstFile), StringIO(secondFile), whitespace=False)

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    suite.addTest(TestOutput("test_newExtractorOutput"))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
