#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
from datetime import datetime;
import unittest
import sqlite3;

from .ParsingExample import ParsingExample;

class TestParsingExample(unittest.TestCase):
    def setUp(self):
        # Application instance to test on
        self.app = ParsingExample();

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        pass;


    def test_parseLogicStr(self):
        """Parsing of logic string into stack of items and operators"""
        testStr = "(SEX)&(AGE)&FI(1)&FI(2)";
        expectedLogicStack = \
            [   {"negate": False, "type": "SEX", "index": None },
                "&",
                {"negate": False, "type": "AGE", "index": None },
                "&",
                {"negate": False, "type": "FI", "index": 1 },
                "&",
                {"negate": False, "type": "FI", "index": 2 },
            ];
        logicStack = self.app.parseLogicStr( testStr );
        self.assertEqual(expectedLogicStack, logicStack);


        testStr = "(SEX)&(AGE)&FI(2)&'FI(3)";
        expectedLogicStack = \
            [   {"negate": False, "type": "SEX", "index": None },
                "&",
                {"negate": False, "type": "AGE", "index": None },
                "&",
                {"negate": False, "type": "FI", "index": 2 },
                "&",
                {"negate": True, "type": "FI", "index": 3 },
            ];
        logicStack = self.app.parseLogicStr( testStr );
        self.assertEqual(expectedLogicStack, logicStack);


        testStr = "FI(1)&FF(1)&(FI(5)!FI(6)!FI(7))&FF(2)";
        expectedLogicStack = \
            [   {"negate": False, "type": "FI", "index": 1 },
                "&",
                {"negate": False, "type": "FF", "index": 1 },
                "&",
                "(",
                    {"negate": False, "type": "FI", "index": 5 },
                    "!",
                    {"negate": False, "type": "FI", "index": 6 },
                    "!",
                    {"negate": False, "type": "FI", "index": 7 },
                ")",
                "&",
                {"negate": False, "type": "FF", "index": 2 },
            ];
        logicStack = self.app.parseLogicStr( testStr );
        self.assertEqual(expectedLogicStack, logicStack);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    suite.addTest(unittest.makeSuite(TestParsingExample));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
