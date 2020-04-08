#!/usr/bin/env python
"""Test case for respective module in application package.
Fill in test functions such that this can be run from command-line:

    python TestAssociationStatsExample.py

To verify whether the core counting functionality in the respective application code works appropriately.
"""

import sys, os
from io import StringIO
from datetime import datetime;
import unittest
import zipfile, gzip;

from .AssociationStatsExample import AssociationStatsExample;

INPUT_FILENAME_ZIP = "PartD_Prescriber_PUF_NPI_DRUG_15.zip";
INPUT_SAMPLE_FILENAME_ZIP = "PartD_Prescriber_PUF_NPI_DRUG_15.sample.zip";  # Consider using smaller sample file to avoid excessively long test
TOP_RESULTS = 10;   # How many of the top results to verify

class TestAssociationStatsExample(unittest.TestCase):
    def setUp(self):
        """Prepare state for test cases. """
        self.app = AssociationStatsExample();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        pass;

    def test_drugAssociationStats(self):
        """Verify association statistics counts from an example data table"""
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        pass;
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    suite.addTest(unittest.makeSuite(TestAssociationStatsExample));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
