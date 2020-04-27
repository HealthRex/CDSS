#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
from datetime import datetime;
import unittest
import sqlite3;

from .SQLQueryExample import SQLQueryExample;

# Sample SQL database contained in single sqlite file.
# More information and data schema: 
#   http://www.sqlitetutorial.net/sqlite-sample-database/
TEMP_DATABASE_FILENAME = "chinook.db"

class TestSQLQueryExample(unittest.TestCase):
    def setUp(self):
        """Prepare state for test cases"""
        # Create temp (SQLite) database file to work with
        self.conn = sqlite3.connect(TEMP_DATABASE_FILENAME);
        
        # Application instance to test on
        self.app = SQLQueryExample(self.conn);

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        # Close DB connection
        self.conn.close();

    def test_sqlQueries(self):
        """Dynamic SQL queries and expected results based on different parameters"""
        options = {"artistPrefix":"S", "invoiceDateStart":None, "invoiceDateEnd":None, "sortField":"artists.name"}
        expectedResults = \
            [
                (59,"Santana",3,27),
                (213,"Scholars Baroque Ensemble",1,1),
                (179,"Scorpions",1,12),
                (232,"Sergei Prokofiev & Yuri Temirkanov",1,1),
                (221,"Sir Georg Solti & Wiener Philharmoniker",1,1),
                (249,"Sir Georg Solti, Sumi Jo & Wiener Philharmoniker",1,1),
                (130,"Skank",2,23),
                (131,"Smashing Pumpkins",2,34),
                (132,"Soundgarden",1,17),
                (53,"Spyro Gyra",2,21),
                (133,"Stevie Ray Vaughan & Double Trouble",1,10),
                (134,"Stone Temple Pilots",1,12),
                (135,"System Of A Down",1,11),
            ];
        actualResults = self.app.queryTrackCounts(options);
        self.assertEqual(expectedResults, actualResults);

        options = {"artistPrefix":"The", "invoiceDateStart": datetime(2012,1,1), "invoiceDateEnd":datetime(2013,1,1), "sortField":"artists.name"}
        expectedResults = \
            [
                (137,"The Black Crowes",2,4),
                (138,"The Clash",1,2),
                (139,"The Cult",2,3),
                (140,"The Doors",1,1),
                (156,"The Office",3,13),
                (141,"The Police",1,2),
                (200,"The Posies",1,1),
                (142,"The Rolling Stones",3,5),
                (143,"The Tea Party",2,2),
                (144,"The Who",1,9),
            ];
        actualResults = self.app.queryTrackCounts(options);
        self.assertEqual(expectedResults, actualResults);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    suite.addTest(unittest.makeSuite(TestSQLQueryExample));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
